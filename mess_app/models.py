from django.contrib.auth.models import AbstractUser
from django.db import models 
import calendar
from datetime import date
from decimal import Decimal 
from django.db.models import F, Sum, ExpressionWrapper, fields 

# --- 1. User Management Model---

class User(AbstractUser):
    # Custom choices for user roles
    STUDENT = 1
    ADMIN = 2

    ROLE_CHOICES = (
        (STUDENT, 'Student'),
        (ADMIN, 'Admin'),
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=STUDENT)
    
    # Student specific details for profile display
    department = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username

# --- 2. Food Menu Module ---

WEEKDAYS = [
    (str(i), day_name) for i, day_name in enumerate(calendar.day_name)
]

class FoodMenu(models.Model):
    MEAL_CHOICES = (
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
    )
    
    day_of_week = models.CharField(max_length=10, choices=WEEKDAYS) 
    meal_type = models.CharField(max_length=1, choices=MEAL_CHOICES)
    menu_details = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('day_of_week', 'meal_type') 
        verbose_name_plural = "Food Menus"
        ordering = ['day_of_week', 'meal_type'] 

    def __str__(self):
        return f"Day {self.day_of_week} - {self.get_meal_type_display()}"


# --- 3. Leave Request Module ---

class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField() 
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    requested_on = models.DateTimeField(auto_now_add=True)

    @property
    def total_leave_days(self):
        """Calculates total days requested."""
        if self.from_date and self.to_date:
            return (self.to_date - self.from_date).days + 1
        return 0

# --- 4. Bill Details Module ---
class Bill(models.Model):
    STATUS_CHOICES = (
        ('D', 'Due'),
        ('P', 'Paid'),
    )
    student = models.ForeignKey('User', on_delete=models.CASCADE)
    month = models.DateField()
    
    # Financial Inputs
    base_rate_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_days_in_month = models.IntegerField(default=30)
    leave_days_approved = models.IntegerField(default=0)
    
    # Calculated Fields
    base_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    adjustment_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    last_date_of_payment = models.DateField()

    # --- Verification & Automation Field ---
    notification_sent = models.BooleanField(default=False)

    def get_approved_leave_days(self):
        """Calculates total approved leave days for the specific month."""
        month_start = self.month.replace(day=1)
        _, last_day = calendar.monthrange(self.month.year, self.month.month)
        month_end = self.month.replace(day=last_day)

        # Pulling LeaveRequest locally to avoid circular imports if necessary
        from .models import LeaveRequest
        approved_leaves = LeaveRequest.objects.filter(
            student=self.student,
            status='A', 
            from_date__lte=month_end,
            to_date__gte=month_start,
        )

        total_days = 0
        for req in approved_leaves:
            overlap_start = max(req.from_date, month_start)
            overlap_end = min(req.to_date, month_end)
            if overlap_start <= overlap_end:
                total_days += (overlap_end - overlap_start).days + 1
        return total_days

    def calculate_amounts(self):
        """Calculates financial totals."""
        base_rate = Decimal(self.base_rate_per_day)
        total_days = Decimal(self.total_days_in_month)
        leave_days = Decimal(self.leave_days_approved) 

        self.base_amount = base_rate * total_days
        self.adjustment_amount = base_rate * leave_days
        self.total_amount = max(self.base_amount - self.adjustment_amount, Decimal('0.00'))

    def save(self, *args, **kwargs):
        """
        Triggers every time a Bill is created or updated.
        Calculates values and sends automatic WhatsApp if status is Due.
        """
        # 1. Update calculations
        self.leave_days_approved = self.get_approved_leave_days()
        self.calculate_amounts()
        
        # 2. Save record to Database first
        super().save(*args, **kwargs)
        
        # 3. AUTOMATIC TRIGGER LOGIC
        # Conditions: Status is 'Due' AND message hasn't been sent yet
        if self.status == 'D' and not self.notification_sent:
            if self.student.mobile_number:
                from .utils import send_whatsapp_notification
                
                # Try sending the message
                success = send_whatsapp_notification(self.student.mobile_number, self.whatsapp_message_body)
                
                if success:
                    # Update the database flag so the cross turns into a checkmark
                    # Using .update() prevents the save() method from looping
                    self.__class__.objects.filter(pk=self.pk).update(notification_sent=True)
            else:
                # Log to terminal if number is missing
                print(f"⚠️ Notification skipped for {self.student.username}: No mobile number found.")

    @property
    def whatsapp_message_body(self):
        """The exact message format requested."""
        month_name = self.month.strftime('%B %Y')
        due_date = self.last_date_of_payment.strftime('%d %b, %Y')
        
        return (
            f"🔔 MESS BILL ALERT - {month_name}\n\n"
            f"Amount Due: ₹{self.total_amount}\n"
            f"Status: {self.get_status_display()}\n"
            f"Payment Due Date: {due_date}\n\n"
            f"Leave Adjustment: -₹{self.adjustment_amount} ({self.leave_days_approved} days)\n"
            "Please pay on time to avoid fines. Check the portal for details."
        )

    def __str__(self):
        return f"Bill for {self.student.username} - {self.month.strftime('%B %Y')}"
    
# --- 5. Feedback Module ---

class Feedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    comment = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        verbose_name_plural = "Feedback"

# --- 6. Lost & Found Module ---

class LostAndFound(models.Model):
    TYPE_CHOICES = (
        ('L', 'Lost'),
        ('F', 'Found'),
    )
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    item_name = models.CharField(max_length=255)
    date_event = models.DateField() 
    place_event = models.CharField(max_length=255)
    description = models.TextField()
    is_approved = models.BooleanField(default=False) 
    posted_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Lost and Found"

# --- 7. Admin Notification Module ---

class AdminNotification(models.Model):
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Admin Notifications"
        ordering = ['-created_at'] 

    def __str__(self):
        return f"Notification: {self.message[:50]}..."
        
# --- 8. Meal Rating Module---

class MealRating(models.Model):
    MEAL_CHOICES = (
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
    )
    
    # Simple rating: 1 (Bad) to 5 (Excellent)
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=1, choices=MEAL_CHOICES)
    rating_date = models.DateField(default=date.today) 
    rating_score = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True) 
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a student can only rate a specific meal once per day
        unique_together = ('student', 'meal_type', 'rating_date') 
        verbose_name_plural = "Meal Ratings"
        ordering = ['-rating_date', 'meal_type']

    def __str__(self):
        return f"{self.student.username}'s {self.get_meal_type_display()} Rating ({self.rating_date})"