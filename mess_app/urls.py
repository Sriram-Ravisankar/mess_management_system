from django.urls import path 
from django.contrib.auth.views import LogoutView 
from . import views
from .views import MessLoginView

urlpatterns = [
    # Auth
    path('login/', MessLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('', views.student_dashboard, name='home'), 
    
    path('data-endpoint/', views.data_endpoint, name='data_endpoint'), 
]