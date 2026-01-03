"""
Smart Transport Trip Management System - URL Configuration
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication URLs
    path('', views.CustomLoginView.as_view(), name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    
    # Admin User Management URLs
    path('admin/users/', views.user_list_view, name='user_list'),
    path('admin/users/create/', views.user_create_view, name='user_create'),
    path('admin/users/<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    path('admin/users/<int:user_id>/status/', views.user_status_view, name='user_status'),
    path('admin/users/<int:user_id>/delete/', views.user_delete_view, name='user_delete'),
    
    # Admin Vehicle Management URLs
    path('admin/vehicles/', views.vehicle_list_view, name='vehicle_list'),
    path('admin/vehicles/create/', views.vehicle_create_view, name='vehicle_create'),
    path('admin/vehicles/<int:vehicle_id>/edit/', views.vehicle_edit_view, name='vehicle_edit'),
    path('admin/vehicles/<int:vehicle_id>/delete/', views.vehicle_delete_view, name='vehicle_delete'),
    
    # Admin Driver Management URLs
    path('admin/drivers/', views.driver_list_view, name='driver_list'),
    path('admin/drivers/create/', views.driver_create_view, name='driver_create'),
    path('admin/drivers/<int:driver_id>/edit/', views.driver_edit_view, name='driver_edit'),
    path('admin/drivers/<int:driver_id>/assign-vehicle/', views.driver_assign_vehicle_view, name='driver_assign_vehicle'),
    
    # Admin Trip Management URLs
    path('admin/trips/', views.trip_list_admin_view, name='trip_list_admin'),
    path('admin/trips/create/', views.trip_create_view, name='trip_create'),
    path('admin/trips/<int:trip_id>/edit/', views.trip_edit_view, name='trip_edit'),
    path('admin/trips/<int:trip_id>/cancel/', views.trip_cancel_view, name='trip_cancel'),
    
    # Admin Logs
    path('admin/logs/', views.admin_logs_view, name='admin_logs'),
    
    # Trip Search and Booking (Passenger)
    path('trips/', views.trip_search_view, name='trip_search'),
    path('trips/<int:trip_id>/', views.trip_detail_view, name='trip_detail'),
    path('trips/<int:trip_id>/book/', views.trip_book_view, name='trip_book'),
    path('trips/schedule/', views.trip_schedule_view, name='trip_schedule'),
    
    # My Bookings (Passenger)
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('my-bookings/<int:booking_id>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    path('my-bookings/<int:booking_id>/rate/', views.rate_trip_view, name='rate_trip'),
    
    # Driver Trip URLs
    path('driver/trips/', views.driver_trips_view, name='driver_trips'),
    path('driver/trips/<int:trip_id>/', views.driver_trip_detail_view, name='driver_trip_detail'),
    path('driver/trips/<int:trip_id>/start/', views.driver_start_trip_view, name='driver_start_trip'),
    path('driver/trips/<int:trip_id>/complete/', views.driver_complete_trip_view, name='driver_complete_trip'),
]
