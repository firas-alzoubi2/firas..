"""
Smart Transport Trip Management System - Models
Following the DB schema with clean architecture principles
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from decimal import Decimal


class UserManager(BaseUserManager):
    """Custom user manager for User model"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', User.UserType.ADMINISTRATOR)
        
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model corresponding to USERS table
    Implements Single Responsibility Principle - handles user identity only
    """
    
    class UserType(models.TextChoices):
        ADMINISTRATOR = 'Administrator', 'Administrator'
        DRIVER = 'Driver', 'Driver'
        PASSENGER = 'Passenger', 'Passenger'
    
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.PASSENGER
    )
    
    # Django auth fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    def get_full_name(self):
        return self.username
    
    def get_short_name(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.user_type == self.UserType.ADMINISTRATOR
    
    @property
    def is_driver(self):
        return self.user_type == self.UserType.DRIVER
    
    @property
    def is_passenger(self):
        return self.user_type == self.UserType.PASSENGER


class Account(models.Model):
    """
    Account model corresponding to ACCOUNTS table
    Handles account status and authentication metadata
    """
    
    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        DISABLED = 'Disabled', 'Disabled'
        DELETED = 'Deleted', 'Deleted'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='account'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    last_login = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
    
    def __str__(self):
        return f"Account for {self.user.username} - {self.status}"
    
    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE


class Vehicle(models.Model):
    """
    Vehicle model corresponding to VEHICLES table
    Follows Single Responsibility - handles vehicle data only
    """
    
    class VehicleType(models.TextChoices):
        BUS = 'Bus', 'Bus'
        MINIBUS = 'Minibus', 'Minibus'
        VAN = 'Van', 'Van'
        CAR = 'Car', 'Car'
    
    class Status(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        IN_USE = 'In Use', 'In Use'
        MAINTENANCE = 'Maintenance', 'Maintenance'
        RETIRED = 'Retired', 'Retired'
    
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.BUS
    )
    model = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    year = models.IntegerField()
    capacity = models.IntegerField()
    color = models.CharField(max_length=20)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicles'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"


class Driver(models.Model):
    """
    Driver model corresponding to DRIVERS table
    Links user to driver-specific information
    """
    
    class Status(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        ON_TRIP = 'On Trip', 'On Trip'
        OFF_DUTY = 'Off Duty', 'Off Duty'
        SUSPENDED = 'Suspended', 'Suspended'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_drivers'
    )
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=20)
    license_expiry = models.DateField()
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_trips = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drivers'
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
    
    def __str__(self):
        return f"Driver: {self.user.username} - {self.license_number}"


class Trip(models.Model):
    """
    Trip model corresponding to TRIPS table
    Core entity for trip management
    """
    
    class Status(models.TextChoices):
        UPCOMING = 'Upcoming', 'Upcoming'
        ONGOING = 'Ongoing', 'Ongoing'
        COMPLETED = 'Completed', 'Completed'
        CANCELLED = 'Cancelled', 'Cancelled'
    
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trips'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trips'
    )
    trip_name = models.CharField(max_length=100)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPCOMING
    )
    cancelled_by = models.CharField(max_length=20, blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trips'
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'
        ordering = ['-departure_time']
    
    def __str__(self):
        return f"{self.trip_name}: {self.start_location} → {self.end_location}"
    
    @property
    def is_bookable(self):
        return (
            self.status == self.Status.UPCOMING and 
            self.available_seats > 0 and
            self.departure_time > timezone.now()
        )


class TripBooking(models.Model):
    """
    TripBooking model corresponding to TRIP_BOOKINGS table
    Handles passenger bookings for trips
    """
    
    class Status(models.TextChoices):
        CONFIRMED = 'Confirmed', 'Confirmed'
        CANCELLED = 'Cancelled', 'Cancelled'
        COMPLETED = 'Completed', 'Completed'
    
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    seats_booked = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trip_bookings'
        verbose_name = 'Trip Booking'
        verbose_name_plural = 'Trip Bookings'
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"Booking #{self.pk} - {self.user.username} for {self.trip.trip_name}"


class Rating(models.Model):
    """
    Rating model corresponding to RATINGS table
    Handles ratings for trips, drivers, and vehicles
    """
    
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings_given'
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name='ratings_received',
        null=True,
        blank=True
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='ratings_received',
        null=True,
        blank=True
    )
    driver_rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        null=True,
        blank=True
    )
    vehicle_rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        null=True,
        blank=True
    )
    driver_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ratings'
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ['trip', 'user']
    
    def __str__(self):
        return f"Rating by {self.user.username} for {self.trip.trip_name}"


class AdminLog(models.Model):
    """
    AdminLog model corresponding to ADMIN_LOGS table
    Audit trail for administrator actions
    """
    
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='admin_logs'
    )
    action_type = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_logs'
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin.username}: {self.action_type} on {self.entity_type}"
