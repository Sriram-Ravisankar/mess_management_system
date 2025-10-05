from django.contrib.auth.models import AbstractUser # type: ignore
from django.db import models # type: ignore
import calendar
from datetime import date
from decimal import Decimal

# --- 1. User Management Model for RBAC ---

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

# --- 2. Food Menu Module (FIXED: Using Calendar for Day Order) ---

# Map 0-6 to Day Names (Monday is 0). This is a module-level constant.
WEEKDAYS = [
    (str(i), day_name) for i, day_name in enumerate(calendar.day_name)
]

class FoodMenu(models.Model):
    MEAL_CHOICES = (
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
    )
    
    # Use WEEKDAYS for correct sorting in the Admin dropdown
    day_of_week = models.CharField(max_length=10, choices=WEEKDAYS) 
    meal_type = models.CharField(max_length=1, choices=MEAL_CHOICES)
    menu_details = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensures only one entry per meal per day
        unique_together = ('day_of_week', 'meal_type') 
        verbose_name_plural = "Food Menus"
        ordering = ['day_of_week', 'meal_type'] # Ensure correct order for weekly view

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
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField() # e.g., date(2025, 9, 1) to track the billing month
    
    # Core Financial Fields
    base_rate_per_day = models.DecimalField(max_digits=6, decimal_places=2, default=0.00) 
    total_days_in_month = models.IntegerField(default=30)
    leave_days_approved = models.IntegerField(default=0) # Days to be deducted
    
    # Calculated Fields
    base_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    adjustment_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00) # Deduction due to leave
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    last_date_of_payment = models.DateField()
    
    def calculate_amounts(self):
        """Calculates base_amount, adjustment_amount, and total_amount."""
        # Ensure Decimal type for calculations
        base_rate = Decimal(self.base_rate_per_day) # type: ignore
        total_days = Decimal(self.total_days_in_month) # type: ignore
        leave_days = Decimal(self.leave_days_approved) # type: ignore

        # 1. Base Amount (Assuming fixed cost for the full month)
        self.base_amount = base_rate * total_days

        # 2. Adjustment Amount (Reduction)
        # Assuming adjustment is the per-day rate multiplied by approved leave days.
        self.adjustment_amount = base_rate * leave_days

        # 3. Total Amount Due
        self.total_amount = self.base_amount - self.adjustment_amount
        if self.total_amount < 0:
            self.total_amount = Decimal('0.00') # type: ignore

    def save(self, *args, **kwargs):
        # Automatically run calculation before saving (on creation/update)
        self.calculate_amounts()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Bill for {self.student.username} - {self.month.strftime('%B %Y')}"

# --- 5. Feedback Module ---

class Feedback(models.Model):
    # TEMPORARY FIX: Add null=True so Django can proceed with migration
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    # RATING FIELD IS ALREADY REMOVED
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
    date_event = models.DateField() # Date of loss or date item was found
    place_event = models.CharField(max_length=255)
    description = models.TextField()
    is_approved = models.BooleanField(default=False) # Admin approval before visibility
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
        ordering = ['-created_at'] # Show latest notifications first

    def __str__(self):
        return f"Notification: {self.message[:50]}..."
        
# --- 8. Meal Rating Module (NEW) ---

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
    rating_date = models.DateField(default=date.today) # Date of the meal
    rating_score = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True) # Optional comment
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a student can only rate a specific meal once per day
        unique_together = ('student', 'meal_type', 'rating_date') 
        verbose_name_plural = "Meal Ratings"
        ordering = ['-rating_date', 'meal_type']

    def __str__(self):
        return f"{self.student.username}'s {self.get_meal_type_display()} Rating ({self.rating_date})"