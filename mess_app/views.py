from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.decorators import login_required, user_passes_test # type: ignore
from django.contrib.auth.views import LoginView # type: ignore
from django.urls import reverse # type: ignore
from django.db.models import Avg, Max # type: ignore
from django.contrib import messages # type: ignore
from django.http import JsonResponse, HttpResponse # <--- FIX: Ensure HttpResponse is available (though render uses it)
from django.views.decorators.cache import never_cache
from datetime import date, datetime
import calendar

from .models import (
    User, FoodMenu, LeaveRequest, Bill, Feedback, LostAndFound, AdminNotification, MealRating,
    WEEKDAYS # <--- FIX: Import WEEKDAYS from models module
)
from .forms import LeaveRequestForm, FeedbackForm, LostAndFoundForm, MealRatingForm
from .utils import send_whatsapp_notification

# --- RBAC Helpers ---

def is_student(user):
    return user.role == User.STUDENT

# --- Login View with Role Redirection ---

class MessLoginView(LoginView):
    template_name = 'mess_app/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == User.ADMIN or user.is_superuser:
                return reverse('admin:index') 
            elif user.role == User.STUDENT:
                return reverse('student_dashboard')
        return super().get_success_url()

# --- Student Dashboard and Module Views (Consolidated SPA Logic) ---

@login_required
@user_passes_test(is_student)
@never_cache
def student_dashboard(request):
    user = request.user
    
    # --- 1. Form Initialization and Processing ---
    
    if request.method == 'POST':
        form_action = request.POST.get('form_action')
        
        # BIND POST DATA FOR EACH FORM
        leave_form = LeaveRequestForm(request.POST)
        feedback_form = FeedbackForm(request.POST)
        lost_found_form = LostAndFoundForm(request.POST)
        meal_rating_form = MealRatingForm(request.POST) 
        
        initial_module = request.GET.get('module') or 'dashboard' 

        if form_action == 'leave':
            if leave_form.is_valid():
                leave = leave_form.save(commit=False)
                leave.student = user
                leave.save()
                messages.success(request, "Leave request submitted successfully and is awaiting admin approval.")
                return redirect(reverse('student_dashboard') + '?module=leave')
            else:
                initial_module = 'leave'
                messages.error(request, "Error submitting leave request. Please check the dates and provide a reason.")
        
        elif form_action == 'feedback':
            if feedback_form.is_valid():
                feedback = feedback_form.save(commit=False)
                feedback.student = user 
                feedback.save()
                messages.success(request, "Feedback submitted successfully! Thank you for your input.")
                return redirect(reverse('student_dashboard') + '?module=feedback')
            else:
                initial_module = 'feedback'
                messages.error(request, "Error submitting feedback. Please ensure your comments are valid.")

        elif form_action == 'lost_found':
            if lost_found_form.is_valid():
                item = lost_found_form.save(commit=False)
                item.reporter = user
                item.save()
                messages.success(request, "Lost & Found report submitted. It will be visible after admin approval.")
                return redirect(reverse('student_dashboard') + '?module=lost-found')
            else:
                initial_module = 'lost-found'
                messages.error(request, "Error submitting Lost & Found report. Please check all mandatory fields.")
        
        elif form_action == 'meal_rating': 
            if meal_rating_form.is_valid():
                rating = meal_rating_form.save(commit=False)
                rating.student = user
                rating.rating_date = date.today() # Enforce today's date
                rating.save()
                messages.success(request, f"{rating.get_meal_type_display()} rating submitted successfully!")
                return redirect(reverse('student_dashboard') + '?module=feedback') 
            else:
                initial_module = 'feedback' 
                messages.error(request, "Error submitting meal rating. Please ensure you have selected a score.")
    else:
        # For GET request (Initial load) - Initialize forms here for GET only
        leave_form = LeaveRequestForm()
        feedback_form = FeedbackForm()
        lost_found_form = LostAndFoundForm()
        meal_rating_form = MealRatingForm()
        initial_module = request.GET.get('module') or 'dashboard' 


    # --- 2. Data Fetching for All Modules ---
    
    # A. Menu Data & Update Status
    today_day_num = str(date.today().weekday())
    today_day_name = calendar.day_name[int(today_day_num)]
    
    menu_today = FoodMenu.objects.filter(day_of_week=today_day_num).order_by('meal_type')
    latest_menu_update = FoodMenu.objects.aggregate(Max('updated_at'))['updated_at__max']

    menu_all = FoodMenu.objects.all().order_by('day_of_week', 'meal_type') 
    
    # Structured data for the Menu tab (eliminates the need for get_item filter)
    menu_by_day_meal = {}
    for menu_item in menu_all:
        day_key = menu_item.day_of_week 
        meal_key = menu_item.meal_type 
        if day_key not in menu_by_day_meal:
            menu_by_day_meal[day_key] = {}
        menu_by_day_meal[day_key][meal_key] = menu_item.menu_details

    # Use the imported WEEKDAYS list
    WEEKDAY_CHOICES = WEEKDAYS 
    weekly_menu_table = []
    
    for day_num, day_name in WEEKDAY_CHOICES:
        day_menu = menu_by_day_meal.get(day_num, {})
        weekly_menu_table.append({
            'day_num': day_num,
            'day_name': day_name,
            'is_today': day_num == today_day_num,
            'B': day_menu.get('B', 'N/A'),
            'L': day_menu.get('L', 'N/A'),
            'D': day_menu.get('D', 'N/A'),
        })

    # B. Leave Status
    leave_history = LeaveRequest.objects.filter(student=user).order_by('-requested_on')
    pending_leaves_count = leave_history.filter(status='P').count()
    latest_leave = leave_history.first()
    
    # C. Bill Status
    bill_history = Bill.objects.filter(student=user).order_by('-month')
    latest_bill = bill_history.first()
    
    # D. Feedback & Lost & Found
    overall_rating = 'N/A' 
    lost_found_items = LostAndFound.objects.filter(is_approved=True).order_by('-posted_on')
    
    # E. Latest Admin Notifications
    admin_notifications = AdminNotification.objects.filter(is_active=True).order_by('-created_at')[:5]

    # F. Meal Rating Data 
    rated_meals_today = MealRating.objects.filter(
        student=user,
        rating_date=date.today()
    ).values_list('meal_type', flat=True)
    today_average_rating = MealRating.objects.filter(rating_date=date.today()).aggregate(Avg('rating_score'))['rating_score__avg']


    # --- 3. Context Preparation ---

    context = {
        'profile': user,
        'initial_module': initial_module, 
        
        # Dashboard Stats
        'latest_bill': latest_bill,
        'pending_leaves_count': pending_leaves_count,
        'latest_menu_update': latest_menu_update,
        'admin_notifications': admin_notifications, 
        
        # Module Data
        'menu_today': menu_today, 
        'weekly_menu_table': weekly_menu_table, 
        'today_day_name': today_day_name,
        'today_day_num': today_day_num,
        'bill_history': bill_history,
        'leave_history': leave_history,
        'latest_leave': latest_leave,
        'overall_rating': overall_rating, 
        'lost_found_items': lost_found_items,
        
        # Meal Rating Context
        'rated_meals_today': list(rated_meals_today),
        'meal_choices': FoodMenu.MEAL_CHOICES,
        'today_average_rating': round(today_average_rating, 2) if today_average_rating else 'N/A',
        
        # Forms
        'leave_form': leave_form,
        'feedback_form': feedback_form,
        'lost_found_form': lost_found_form,
        'meal_rating_form': meal_rating_form,
    }
    
    response = render(request, 'mess_app/student_dashboard.html', context)
    
    # --- FIX: Add explicit no-cache headers for definitive cache prevention ---
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response # <--- Return the modified response object


# --- JSON ENDPOINT FOR REAL-TIME POLLING ---

@login_required
@user_passes_test(is_student)
def data_endpoint(request):
    user = request.user

    # Fetch latest bill data
    latest_bill = Bill.objects.filter(student=user).order_by('-month').first()
    
    # Fetch pending leave count
    pending_leaves_count = LeaveRequest.objects.filter(student=user, status='P').count()

    # Get latest leave status (for the polling JS logic)
    latest_leave = LeaveRequest.objects.filter(student=user).order_by('-requested_on').first()
    latest_leave_status_code = latest_leave.status if latest_leave else 'N'

    # Fetch latest notifications
    notifications = AdminNotification.objects.filter(is_active=True).order_by('-created_at')[:3]

    # Prepare JSON response data (Handle empty data safely)
    bill_data = {}
    if latest_bill:
        bill_data = {
            'amount': str(latest_bill.total_amount),
            'due_date': latest_bill.last_date_of_payment.strftime('%b %d, %Y') if latest_bill.last_date_of_payment else 'N/A',
            'status': latest_bill.get_status_display(),
            'status_code': latest_bill.status,
        }

    notifications_data = []
    for notif in notifications:
        notifications_data.append({
            'message': notif.message,
            'date': notif.created_at.strftime('%d %b'),
        })

    return JsonResponse({
        'status': 'success',
        'dashboard': {
            'bill': bill_data,
            'pending_leaves': pending_leaves_count,
            'latest_leave_status': latest_leave_status_code, 
            'notifications': notifications_data,
        }
    })