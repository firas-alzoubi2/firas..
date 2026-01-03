# from django.contrib import admin
# from .models import User, Account, Driver, Vehicle, Trip, AdminLog

# # Register your models here.
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'role', 'is_staff')
#     list_filter = ('role', 'is_staff', 'is_active')
#     search_fields = ('username', 'email')

# @admin.register(Account)
# class AccountAdmin(admin.ModelAdmin):
#     list_display = ('user', 'balance')
#     search_fields = ('user__username',)

# @admin.register(Driver)
# class DriverAdmin(admin.ModelAdmin):
#     list_display = ('user', 'license_number', 'status', 'vehicle')
#     list_filter = ('status', 'license_type')
#     search_fields = ('user__username', 'license_number')

# @admin.register(Vehicle)
# class VehicleAdmin(admin.ModelAdmin):
#     list_display = ('plate_number', 'model', 'capacity', 'status')
#     list_filter = ('status', 'type')
#     search_fields = ('plate_number', 'model')

# @admin.register(Trip)
# class TripAdmin(admin.ModelAdmin):
#     list_display = ('trip_id', 'driver', 'start_location', 'end_location', 'status', 'departure_time')
#     list_filter = ('status', 'trip_type')
#     search_fields = ('trip_id', 'start_location', 'end_location')

# @admin.register(AdminLog)
# class AdminLogAdmin(admin.ModelAdmin):
#     list_display = ('admin', 'action', 'target_model', 'timestamp')
#     list_filter = ('action', 'target_model')
#     search_fields = ('details',)
