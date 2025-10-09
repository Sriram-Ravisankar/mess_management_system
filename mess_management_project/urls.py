from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore

urlpatterns = [
    path('admin/', admin.site.urls), # Django Admin Panel for the Admin Role
    path('', include('mess_app.urls')), # Includes all URLs defined in mess_app
]