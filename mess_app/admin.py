from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin 
from django.contrib import messages 
from django.db import models 
from django import forms
from .models import (
    User, FoodMenu, LeaveRequest, Bill, Feedback, LostAndFound, AdminNotification, MealRating
)
from .utils import send_whatsapp_notification


def get_student_full_name(obj):
    user = getattr(obj, 'student', getattr(obj, 'reporter', None))
    if user:
        return f"{user.first_name} {user.last_name} ({user.username})"
    return "N/A"

get_student_full_name.short_description = 'Student Name'
get_student_full_name.admin_order_field = 'student__first_name' 

# --- 1. Custom User Admin for Role Management ---

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'department', 'mobile_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'department', 'mobile_number')}),
    )
    list_display = ('username', 'email', 'first_name', 'department', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')

admin.site.register(User, CustomUserAdmin)

# --- 2. Food Menu Admin ---

@admin.register(FoodMenu)
class FoodMenuAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'meal_type', 'menu_details', 'updated_at')
    list_filter = ('day_of_week', 'meal_type')
    search_fields = ('menu_details',)
    list_editable = ('menu_details',) 
    
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 40})},
    }
    
    def save_model(self, request, obj, form, change):
        """
        Custom save logic to trigger WhatsApp notification on menu update.
        """
        is_new = not obj.pk
        super().save_model(request, obj, form, change)

        # Only send notification if a change was made (or it's a new entry)
        if change or is_new:
            try:
                # Find all students with a mobile number to notify
                students_to_notify = User.objects.filter(
                    role=User.STUDENT, 
                    mobile_number__isnull=False
                ).exclude(mobile_number='')
                
                # Notification message
                day_name = obj.get_day_of_week_display()
                meal_name = obj.get_meal_type_display()
                
                message_body = (
                    f"🍽️ MESS MENU UPDATE - {day_name} {meal_name}\n\n"
                    f"New Menu: {obj.menu_details}\n\n"
                    "Check the Portal for the full weekly menu."
                )

                # Send notification to all students
                for student in students_to_notify:
                    # recipient = f"whatsapp:{student.mobile_number}" 
                    send_whatsapp_notification(student.mobile_number, message_body)

                self.message_user(request, "Menu updated and WhatsApp notifications have been sent to students.", level=messages.SUCCESS)

            except Exception as e:
                self.message_user(request, f"Menu saved, but failed to send some WhatsApp notifications: {e}", level=messages.WARNING)

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (get_student_full_name, 'from_date', 'to_date', 'total_leave_days', 'status', 'requested_on')
    list_filter = ('status', 'from_date')
    readonly_fields = ('requested_on',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (get_student_full_name, 'comment', 'submitted_at')
    list_filter = ()
    search_fields = ('comment', 'student__username', 'student__first_name', 'student__last_name')
    readonly_fields = ('student', 'comment', 'submitted_at')


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    # Display the notification status (Check/Cross) in the list view
    list_display = ('student_full_name', 'month', 'total_amount', 'status', 'last_date_of_payment', 'notification_sent')
    
    # Filters to help find unsent or due bills
    list_filter = ('status', 'month', 'notification_sent')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    
    # Add the manual resend action to the dropdown menu
    actions = ['resend_bill_notifications']
    
    # Protect calculated fields from manual editing
    readonly_fields = ('base_amount', 'adjustment_amount', 'total_amount', 'leave_days_approved', 'notification_sent', 'current_student_display')
    
    fields = (
        ('student', 'current_student_display'), 
        'month', 'base_rate_per_day', 'total_days_in_month',
        'leave_days_approved', 'last_date_of_payment', 'status',
        'base_amount', 'adjustment_amount', 'total_amount', 'notification_sent'
    )

    def student_full_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name} ({obj.student.username})"
    
    def current_student_display(self, obj):
        if obj.pk:
            return f"<strong>{obj.student.first_name} {obj.student.last_name}</strong>"
        return "Select a student above."
    current_student_display.short_description = "Selected Student Name"
    current_student_display.allow_tags = True 

    def resend_bill_notifications(self, request, queryset):
        """
        Action to manually resend notifications.
        Resets the flag and saves the model to trigger the automatic logic in models.py.
        """
        sent_count = 0
        for bill in queryset:
            # Setting this to False allows the models.py save() logic to fire again
            bill.notification_sent = False
            bill.save() 
            sent_count += 1
        
        self.message_user(request, f"Successfully resending notification for {sent_count} bill(s).", messages.SUCCESS)
    
    resend_bill_notifications.short_description = "Resend WhatsApp Notifications to selected bills"


@admin.register(LostAndFound)
class LostAndFoundAdmin(admin.ModelAdmin):
    list_display = ('item_name', get_student_full_name, 'type', 'is_approved', 'date_event', 'posted_on')
    list_filter = ('is_approved', 'type')
    actions = ['approve_selected_items']
    
    get_student_full_name.admin_order_field = 'reporter__first_name' 
    get_student_full_name.short_description = 'Reporter'

    def approve_selected_items(self, request, queryset):
        unapproved_items = queryset.filter(is_approved=False)
        unapproved_items.update(is_approved=True)
        self.message_user(request, f"{unapproved_items.count()} items have been approved.")
    approve_selected_items.short_description = "Approve selected Lost & Found items"


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('message',)

# --- 7. Meal Rating Admin ---

@admin.register(MealRating)
class MealRatingAdmin(admin.ModelAdmin):
    list_display = (get_student_full_name, 'rating_date', 'meal_type', 'rating_score', 'submitted_at')
    list_filter = ('rating_date', 'meal_type', 'rating_score')
    search_fields = ('student__username', 'comment', 'student__first_name', 'student__last_name')
    readonly_fields = ('student', 'rating_date', 'meal_type', 'rating_score', 'comment', 'submitted_at')
    
    get_student_full_name.admin_order_field = 'student__first_name' 
    get_student_full_name.short_description = 'Student Name'