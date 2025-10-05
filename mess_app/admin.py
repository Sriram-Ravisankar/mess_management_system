from django.contrib import admin # type: ignore
from django.contrib.auth.admin import UserAdmin # type: ignore
from django.contrib import messages # type: ignore
from .models import (
    User, FoodMenu, LeaveRequest, Bill, Feedback, LostAndFound, AdminNotification, MealRating
)
from .utils import send_whatsapp_notification

# --- 1. Custom User Admin for Role Management ---

class CustomUserAdmin(UserAdmin):
    # Add 'role', 'department', and 'mobile_number' to the user creation form and change form
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'department', 'mobile_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'department', 'mobile_number')}),
    )
    list_display = ('username', 'email', 'first_name', 'department', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')

admin.site.register(User, CustomUserAdmin)

# --- 2. Food Menu Admin (NEW REGISTRATION/UPDATE) ---

@admin.register(FoodMenu)
class FoodMenuAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'meal_type', 'menu_details', 'updated_at')
    list_filter = ('day_of_week', 'meal_type')
    search_fields = ('menu_details',)
    list_editable = ('menu_details',) # Allow quick editing of menu details
    
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
                    "Check the Student Portal for the full weekly menu."
                )

                # Send notification to all students
                for student in students_to_notify:
                    # NOTE: Ensure student.mobile_number is pre-pended with 'whatsapp:' 
                    # and formatted correctly (E.164) for Twilio in settings/utils.
                    recipient = f"whatsapp:{student.mobile_number}" 
                    send_whatsapp_notification(recipient, message_body)

                self.message_user(request, "Menu updated and WhatsApp notifications have been sent to students.", level=messages.SUCCESS)

            except Exception as e:
                # Log error but don't prevent saving
                self.message_user(request, f"Menu saved, but failed to send some WhatsApp notifications: {e}", level=messages.WARNING)

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'from_date', 'to_date', 'total_leave_days', 'status', 'requested_on')
    list_filter = ('status', 'from_date')
    readonly_fields = ('requested_on',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'comment', 'submitted_at')
    list_filter = ()
    search_fields = ('comment', 'student__username')
    # CRITICAL: Define fields that the Admin can ONLY view, not edit.
    readonly_fields = ('student', 'comment', 'submitted_at')

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('student', 'month', 'total_amount', 'status', 'last_date_of_payment')
    list_filter = ('status', 'month')
    search_fields = ('student__username',)
    # The calculated fields are read-only
    readonly_fields = ('base_amount', 'adjustment_amount', 'total_amount')
    # Make 'leave_days_approved' editable by admin
    fields = ('student', 'month', 'base_rate_per_day', 'total_days_in_month', 
              'leave_days_approved', 'last_date_of_payment', 'status', 
              'base_amount', 'adjustment_amount', 'total_amount')


@admin.register(LostAndFound)
class LostAndFoundAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'reporter', 'type', 'is_approved', 'date_event', 'posted_on')
    list_filter = ('is_approved', 'type')
    actions = ['approve_selected_items']
    
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

# --- 7. Meal Rating Admin (NEW REGISTRATION) ---

@admin.register(MealRating)
class MealRatingAdmin(admin.ModelAdmin):
    list_display = ('student', 'rating_date', 'meal_type', 'rating_score', 'submitted_at')
    list_filter = ('rating_date', 'meal_type', 'rating_score')
    search_fields = ('student__username', 'comment')
    # MODIFIED: Added all feedback fields to read-only
    readonly_fields = ('student', 'rating_date', 'meal_type', 'rating_score', 'comment', 'submitted_at')