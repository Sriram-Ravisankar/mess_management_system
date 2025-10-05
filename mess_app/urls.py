from django.urls import path # type: ignore
from django.contrib.auth.views import LogoutView # type: ignore
from . import views
from .views import MessLoginView

urlpatterns = [
    # Auth
    path('login/', MessLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Dashboard/Home (Handles all student-side GET requests and form submissions)
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('', views.student_dashboard, name='home'), 
    
    # NEW: JSON Endpoint for real-time polling updates
    path('data-endpoint/', views.data_endpoint, name='data_endpoint'), 
]