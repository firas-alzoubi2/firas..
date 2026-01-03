"""
Smart Transport Trip Management System - Views
Implements controllers following clean architecture and SOLID principles
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Q, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from datetime import timedelta

from .models import User, Account, Driver, Vehicle, Trip, TripBooking, Rating, AdminLog
from .forms import (
    UserRegistrationForm, LoginForm, UserProfileForm, CustomPasswordChangeForm,
    AdminUserForm, VehicleForm, DriverForm, CreateDriverForm, TripForm,
    TripSearchForm, BookingForm, RatingForm, CancelTripForm, AccountStatusForm
)
from .decorators import admin_required, driver_required, passenger_required


# =============================================================================
# Authentication Views
# =============================================================================

class CustomLoginView(LoginView):
    """Custom login view with form styling"""
    form_class = LoginForm
    template_name = 'core/auth/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        # Check if account is active
        if hasattr(user, 'account') and user.account.status != Account.Status.ACTIVE:
            messages.error(self.request, 'Your account has been disabled. Please contact support.')
            return self.form_invalid(form)
        
        # Update last login
        if hasattr(user, 'account'):
            user.account.last_login = timezone.now()
            user.account.save()
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return '/dashboard/'


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Smart Transport.')
            return redirect('core:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/auth/register.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:login')


# =============================================================================
# Dashboard Views
# =============================================================================

@login_required
def dashboard_view(request):
    """Main dashboard - routes based on user type"""
    user = request.user
    
    if user.is_admin:
        return admin_dashboard(request)
    elif user.is_driver:
        return driver_dashboard(request)
    else:
        return passenger_dashboard(request)


def admin_dashboard(request):
    """Administrator dashboard"""
    context = {
        'total_users': User.objects.count(),
        'total_drivers': Driver.objects.count(),
        'total_vehicles': Vehicle.objects.count(),
        'total_trips': Trip.objects.count(),
        'active_trips': Trip.objects.filter(status=Trip.Status.ONGOING).count(),
        'upcoming_trips': Trip.objects.filter(status=Trip.Status.UPCOMING).count(),
        'recent_bookings': TripBooking.objects.select_related('trip', 'user')[:5],
        'recent_users': User.objects.order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard/admin.html', context)


def driver_dashboard(request):
    """Driver dashboard"""
    try:
        driver = request.user.driver_profile
        context = {
            'driver': driver,
            'upcoming_trips': Trip.objects.filter(
                driver=driver,
                status=Trip.Status.UPCOMING
            ).order_by('departure_time')[:5],
            'ongoing_trip': Trip.objects.filter(
                driver=driver,
                status=Trip.Status.ONGOING
            ).first(),
            'completed_trips': Trip.objects.filter(
                driver=driver,
                status=Trip.Status.COMPLETED
            ).count(),
            'total_trips': driver.total_trips,
            'average_rating': driver.average_rating,
        }
    except Driver.DoesNotExist:
        context = {'driver': None}
    
    return render(request, 'core/dashboard/driver.html', context)


def passenger_dashboard(request):
    """Passenger dashboard"""
    user = request.user
    context = {
        'upcoming_bookings': TripBooking.objects.filter(
            user=user,
            status=TripBooking.Status.CONFIRMED,
            trip__status__in=[Trip.Status.UPCOMING, Trip.Status.ONGOING]
        ).select_related('trip')[:5],
        'completed_bookings': TripBooking.objects.filter(
            user=user,
            status=TripBooking.Status.COMPLETED
        ).count(),
        'available_trips': Trip.objects.filter(
            status=Trip.Status.UPCOMING,
            departure_time__gt=timezone.now()
        ).order_by('departure_time')[:5],
    }
    return render(request, 'core/dashboard/passenger.html', context)


# =============================================================================
# Profile Views
# =============================================================================

@login_required
def profile_view(request):
    """View and edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/profile/view.html', {'form': form})


@login_required
def change_password_view(request):
    """Change user password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            # Update password changed timestamp
            if hasattr(user, 'account'):
                user.account.password_changed_at = timezone.now()
                user.account.save()
            
            messages.success(request, 'Password changed successfully!')
            return redirect('core:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'core/profile/change_password.html', {'form': form})


# =============================================================================
# Admin User Management Views
# =============================================================================

@login_required
@admin_required
def user_list_view(request):
    """List all users for admin"""
    query = request.GET.get('q', '')
    user_type = request.GET.get('type', '')
    
    users = User.objects.all()
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    
    if user_type:
        users = users.filter(user_type=user_type)
    
    paginator = Paginator(users, 10)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'core/admin/user_list.html', {
        'users': users,
        'query': query,
        'user_type': user_type,
    })


@login_required
@admin_required
def user_create_view(request):
    """Create new user by admin"""
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                user.set_password('defaultpassword123')
            user.save()
            Account.objects.create(user=user)
            
            log_admin_action(request.user, 'CREATE', 'User', user.id, f'Created user: {user.username}')
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('core:user_list')
    else:
        form = AdminUserForm()
    
    return render(request, 'core/admin/user_form.html', {'form': form, 'action': 'Create'})


@login_required
@admin_required
def user_edit_view(request, user_id):
    """Edit user by admin"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
            log_admin_action(request.user, 'UPDATE', 'User', user.id, f'Updated user: {user.username}')
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('core:user_list')
    else:
        form = AdminUserForm(instance=user)
    
    return render(request, 'core/admin/user_form.html', {
        'form': form,
        'action': 'Edit',
        'target_user': user
    })


@login_required
@admin_required
def user_status_view(request, user_id):
    """Change user account status"""
    user = get_object_or_404(User, id=user_id)
    account, _ = Account.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = AccountStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            account.status = new_status
            account.save()
            
            # Also update user's is_active based on status
            user.is_active = (new_status == Account.Status.ACTIVE)
            user.save()
            
            log_admin_action(
                request.user, 'STATUS_CHANGE', 'Account', account.id,
                f'Changed status for {user.username} to {new_status}'
            )
            messages.success(request, f'Account status updated to {new_status}')
            return redirect('core:user_list')
    else:
        form = AccountStatusForm(initial={'status': account.status})
    
    return render(request, 'core/admin/user_status.html', {
        'form': form,
        'target_user': user,
        'account': account
    })


@login_required
@admin_required
def user_delete_view(request, user_id):
    """Delete user account"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user_id_log = user.id
        user.delete()
        
        log_admin_action(request.user, 'DELETE', 'User', user_id_log, f'Deleted user: {username}')
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('core:user_list')
    
    return render(request, 'core/admin/user_delete.html', {'target_user': user})


# =============================================================================
# Vehicle Management Views
# =============================================================================

@login_required
@admin_required
def vehicle_list_view(request):
    """List all vehicles"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    
    vehicles = Vehicle.objects.all()
    
    if query:
        vehicles = vehicles.filter(
            Q(plate_number__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query)
        )
    
    if status:
        vehicles = vehicles.filter(status=status)
    
    paginator = Paginator(vehicles, 10)
    page = request.GET.get('page')
    vehicles = paginator.get_page(page)
    
    return render(request, 'core/admin/vehicle_list.html', {
        'vehicles': vehicles,
        'query': query,
        'status_filter': status,
    })


@login_required
@admin_required
def vehicle_create_view(request):
    """Create new vehicle"""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            log_admin_action(request.user, 'CREATE', 'Vehicle', vehicle.id, f'Created vehicle: {vehicle.plate_number}')
            messages.success(request, f'Vehicle {vehicle.plate_number} added successfully!')
            return redirect('core:vehicle_list')
    else:
        form = VehicleForm()
    
    return render(request, 'core/admin/vehicle_form.html', {'form': form, 'action': 'Add'})


@login_required
@admin_required
def vehicle_edit_view(request, vehicle_id):
    """Edit vehicle"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            log_admin_action(request.user, 'UPDATE', 'Vehicle', vehicle.id, f'Updated vehicle: {vehicle.plate_number}')
            messages.success(request, f'Vehicle {vehicle.plate_number} updated successfully!')
            return redirect('core:vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    
    return render(request, 'core/admin/vehicle_form.html', {
        'form': form,
        'action': 'Edit',
        'vehicle': vehicle
    })


@login_required
@admin_required
def vehicle_delete_view(request, vehicle_id):
    """Delete vehicle"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        plate_number = vehicle.plate_number
        vehicle_id_log = vehicle.id
        vehicle.delete()
        
        log_admin_action(request.user, 'DELETE', 'Vehicle', vehicle_id_log, f'Deleted vehicle: {plate_number}')
        messages.success(request, f'Vehicle {plate_number} deleted successfully!')
        return redirect('core:vehicle_list')
    
    return render(request, 'core/admin/vehicle_delete.html', {'vehicle': vehicle})


# =============================================================================
# Driver Management Views
# =============================================================================

@login_required
@admin_required
def driver_list_view(request):
    """List all drivers"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    
    drivers = Driver.objects.select_related('user', 'vehicle')
    
    if query:
        drivers = drivers.filter(
            Q(user__username__icontains=query) |
            Q(license_number__icontains=query)
        )
    
    if status:
        drivers = drivers.filter(status=status)
    
    paginator = Paginator(drivers, 10)
    page = request.GET.get('page')
    drivers = paginator.get_page(page)
    
    return render(request, 'core/admin/driver_list.html', {
        'drivers': drivers,
        'query': query,
        'status_filter': status,
    })


@login_required
@admin_required
def driver_create_view(request):
    """Create new driver with user account"""
    if request.method == 'POST':
        form = CreateDriverForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                phone=form.cleaned_data.get('phone'),
                user_type=User.UserType.DRIVER
            )
            Account.objects.create(user=user)
            
            # Create driver profile
            driver = Driver.objects.create(
                user=user,
                license_number=form.cleaned_data['license_number'],
                license_type=form.cleaned_data['license_type'],
                license_expiry=form.cleaned_data['license_expiry'],
                vehicle=form.cleaned_data.get('vehicle')
            )
            
            log_admin_action(request.user, 'CREATE', 'Driver', driver.id, f'Created driver: {user.username}')
            messages.success(request, f'Driver {user.username} created successfully!')
            return redirect('core:driver_list')
    else:
        form = CreateDriverForm()
    
    return render(request, 'core/admin/driver_form.html', {'form': form, 'action': 'Create'})


@login_required
@admin_required
def driver_edit_view(request, driver_id):
    """Edit driver profile"""
    driver = get_object_or_404(Driver, id=driver_id)
    
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            log_admin_action(request.user, 'UPDATE', 'Driver', driver.id, f'Updated driver: {driver.user.username}')
            messages.success(request, f'Driver {driver.user.username} updated successfully!')
            return redirect('core:driver_list')
    else:
        form = DriverForm(instance=driver)
    
    return render(request, 'core/admin/driver_edit.html', {
        'form': form,
        'driver': driver
    })


@login_required
@admin_required
def driver_assign_vehicle_view(request, driver_id):
    """Assign vehicle to driver"""
    driver = get_object_or_404(Driver, id=driver_id)
    
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        if vehicle_id:
            vehicle = get_object_or_404(Vehicle, id=vehicle_id)
            driver.vehicle = vehicle
            driver.save()
            
            log_admin_action(
                request.user, 'ASSIGN', 'Driver-Vehicle',
                driver.id, f'Assigned {vehicle.plate_number} to {driver.user.username}'
            )
            messages.success(request, f'Vehicle {vehicle.plate_number} assigned to {driver.user.username}')
        else:
            driver.vehicle = None
            driver.save()
            messages.info(request, f'Vehicle unassigned from {driver.user.username}')
        
        return redirect('core:driver_list')
    
    available_vehicles = Vehicle.objects.filter(status=Vehicle.Status.AVAILABLE)
    return render(request, 'core/admin/driver_assign_vehicle.html', {
        'driver': driver,
        'vehicles': available_vehicles
    })


# =============================================================================
# Trip Management Views
# =============================================================================

@login_required
@admin_required
def trip_list_admin_view(request):
    """List all trips for admin"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    
    trips = Trip.objects.select_related('driver__user', 'vehicle')
    
    if query:
        trips = trips.filter(
            Q(trip_name__icontains=query) |
            Q(start_location__icontains=query) |
            Q(end_location__icontains=query)
        )
    
    if status:
        trips = trips.filter(status=status)
    
    paginator = Paginator(trips, 10)
    page = request.GET.get('page')
    trips = paginator.get_page(page)
    
    return render(request, 'core/admin/trip_list.html', {
        'trips': trips,
        'query': query,
        'status_filter': status,
    })


@login_required
@admin_required
def trip_create_view(request):
    """Create new trip"""
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save()
            log_admin_action(request.user, 'CREATE', 'Trip', trip.id, f'Created trip: {trip.trip_name}')
            messages.success(request, f'Trip "{trip.trip_name}" created successfully!')
            return redirect('core:trip_list_admin')
    else:
        form = TripForm()
    
    return render(request, 'core/admin/trip_form.html', {'form': form, 'action': 'Create'})


@login_required
@admin_required
def trip_edit_view(request, trip_id):
    """Edit trip"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            log_admin_action(request.user, 'UPDATE', 'Trip', trip.id, f'Updated trip: {trip.trip_name}')
            messages.success(request, f'Trip "{trip.trip_name}" updated successfully!')
            return redirect('core:trip_list_admin')
    else:
        form = TripForm(instance=trip)
    
    return render(request, 'core/admin/trip_form.html', {
        'form': form,
        'action': 'Edit',
        'trip': trip
    })


@login_required
@admin_required
def trip_cancel_view(request, trip_id):
    """Cancel trip by admin"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    if trip.status == Trip.Status.CANCELLED:
        messages.warning(request, 'This trip is already cancelled.')
        return redirect('core:trip_list_admin')
    
    if request.method == 'POST':
        form = CancelTripForm(request.POST)
        if form.is_valid():
            trip.status = Trip.Status.CANCELLED
            trip.cancelled_by = 'Administrator'
            trip.cancellation_reason = form.cleaned_data['cancellation_reason']
            trip.save()
            
            # Cancel all bookings for this trip
            TripBooking.objects.filter(trip=trip).update(status=TripBooking.Status.CANCELLED)
            
            log_admin_action(request.user, 'CANCEL', 'Trip', trip.id, f'Cancelled trip: {trip.trip_name}')
            messages.success(request, f'Trip "{trip.trip_name}" cancelled successfully!')
            return redirect('core:trip_list_admin')
    else:
        form = CancelTripForm()
    
    return render(request, 'core/admin/trip_cancel.html', {'form': form, 'trip': trip})


# =============================================================================
# Trip Search and Booking Views (Passenger)
# =============================================================================

@login_required
def trip_search_view(request):
    """Search available trips"""
    form = TripSearchForm(request.GET or None)
    trips = Trip.objects.filter(
        status=Trip.Status.UPCOMING,
        departure_time__gt=timezone.now(),
        available_seats__gt=0
    ).select_related('driver__user', 'vehicle')
    
    if form.is_valid():
        start = form.cleaned_data.get('start_location')
        end = form.cleaned_data.get('end_location')
        date = form.cleaned_data.get('date')
        
        if start:
            trips = trips.filter(start_location__icontains=start)
        if end:
            trips = trips.filter(end_location__icontains=end)
        if date:
            trips = trips.filter(departure_time__date=date)
    
    trips = trips.order_by('departure_time')
    
    paginator = Paginator(trips, 10)
    page = request.GET.get('page')
    trips = paginator.get_page(page)
    
    return render(request, 'core/trips/search.html', {'form': form, 'trips': trips})


@login_required
def trip_detail_view(request, trip_id):
    """View trip details"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    # Check if user already booked this trip
    existing_booking = None
    if request.user.is_passenger:
        existing_booking = TripBooking.objects.filter(
            trip=trip,
            user=request.user,
            status=TripBooking.Status.CONFIRMED
        ).first()
    
    return render(request, 'core/trips/detail.html', {
        'trip': trip,
        'existing_booking': existing_booking
    })


@login_required
@passenger_required
def trip_book_view(request, trip_id):
    """Book a trip"""
    trip = get_object_or_404(Trip, id=trip_id)
    
    if not trip.is_bookable:
        messages.error(request, 'This trip is no longer available for booking.')
        return redirect('core:trip_detail', trip_id=trip_id)
    
    # Check for existing booking
    existing = TripBooking.objects.filter(
        trip=trip,
        user=request.user,
        status=TripBooking.Status.CONFIRMED
    ).exists()
    
    if existing:
        messages.warning(request, 'You have already booked this trip.')
        return redirect('core:trip_detail', trip_id=trip_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, trip=trip)
        if form.is_valid():
            seats = form.cleaned_data['seats']
            
            if seats > trip.available_seats:
                messages.error(request, f'Only {trip.available_seats} seats available.')
                return redirect('core:trip_book', trip_id=trip_id)
            
            # Create booking
            total_price = trip.price * seats
            booking = TripBooking.objects.create(
                trip=trip,
                user=request.user,
                seats_booked=seats,
                total_price=total_price
            )
            
            # Update available seats
            trip.available_seats -= seats
            trip.save()
            
            messages.success(request, f'Successfully booked {seats} seat(s) for {trip.trip_name}!')
            return redirect('core:my_bookings')
    else:
        form = BookingForm(trip=trip)
    
    return render(request, 'core/trips/book.html', {'form': form, 'trip': trip})


@login_required
@passenger_required
def my_bookings_view(request):
    """View user's bookings"""
    status = request.GET.get('status')
    bookings = TripBooking.objects.filter(user=request.user).select_related('trip', 'trip__vehicle', 'trip__driver__user').order_by('-created_at')
    
    if status:
        if status == 'Confirmed':
            bookings = bookings.filter(status=TripBooking.Status.CONFIRMED)
        elif status == 'Completed':
            bookings = bookings.filter(
                Q(status=TripBooking.Status.COMPLETED) |
                Q(trip__status=Trip.Status.COMPLETED)
            )
        elif status == 'Cancelled':
            bookings = bookings.filter(status=TripBooking.Status.CANCELLED)
    
    return render(request, 'core/trips/my_bookings.html', {
        'bookings': bookings,
        'status': status
    })


@login_required
@passenger_required
def cancel_booking_view(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(TripBooking, id=booking_id, user=request.user)
    
    if booking.status != TripBooking.Status.CONFIRMED:
        messages.warning(request, 'This booking cannot be cancelled.')
        return redirect('core:my_bookings')
    
    if booking.trip.status != Trip.Status.UPCOMING:
        messages.warning(request, 'Cannot cancel booking for trips that have started or completed.')
        return redirect('core:my_bookings')
    
    if request.method == 'POST':
        booking.status = TripBooking.Status.CANCELLED
        booking.save()
        
        # Restore available seats
        booking.trip.available_seats += booking.seats_booked
        booking.trip.save()
        
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('core:my_bookings')
    
    return render(request, 'core/trips/cancel_booking.html', {'booking': booking})


# =============================================================================
# Rating Views
# =============================================================================

@login_required
@passenger_required
def rate_trip_view(request, booking_id):
    """Rate a completed trip"""
    booking = get_object_or_404(TripBooking, id=booking_id, user=request.user)
    trip = booking.trip
    
    # Check if trip is completed
    if trip.status != Trip.Status.COMPLETED:
        messages.warning(request, 'You can only rate completed trips.')
        return redirect('core:my_bookings')
    
    # Check if already rated
    existing_rating = Rating.objects.filter(trip=trip, user=request.user).exists()
    if existing_rating:
        messages.info(request, 'You have already rated this trip.')
        return redirect('core:my_bookings')
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.trip = trip
            rating.user = request.user
            rating.driver = trip.driver
            rating.vehicle = trip.vehicle
            rating.save()
            
            # Update driver average rating
            if trip.driver:
                avg = Rating.objects.filter(driver=trip.driver).aggregate(
                    avg=Avg('driver_rating')
                )['avg']
                if avg:
                    trip.driver.average_rating = avg
                    trip.driver.save()
            
            # Update vehicle average rating
            if trip.vehicle:
                avg = Rating.objects.filter(vehicle=trip.vehicle).aggregate(
                    avg=Avg('vehicle_rating')
                )['avg']
                if avg:
                    trip.vehicle.average_rating = avg
                    trip.vehicle.save()
            
            messages.success(request, 'Thank you for your rating!')
            return redirect('core:my_bookings')
    else:
        form = RatingForm()
    
    return render(request, 'core/trips/rate.html', {
        'form': form,
        'trip': trip,
        'booking': booking
    })


# =============================================================================
# Trip Schedule View
# =============================================================================

@login_required
def trip_schedule_view(request):
    """View trip schedule"""
    # Get current week start (Monday)
    today = timezone.now().date()
    week_str = request.GET.get('week')
    
    if week_str:
        try:
            current_date = timezone.datetime.strptime(week_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = today
    else:
        current_date = today
        
    # Calculate start of week (Monday)
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Generate days for the week
    week_days = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # Get trips for this week
    trips = Trip.objects.filter(
        departure_time__date__range=[start_of_week, end_of_week],
        status__in=[Trip.Status.UPCOMING, Trip.Status.ONGOING]
    ).select_related('vehicle')
    
    # Generate hours for the grid (e.g., 6 AM to 10 PM)
    hours = [f"{h:02d}" for h in range(6, 23)]
    
    context = {
        'week_days': week_days,
        'week_start': start_of_week,
        'week_end': end_of_week,
        'prev_week': start_of_week - timedelta(days=7),
        'next_week': start_of_week + timedelta(days=7),
        'today': today,
        'trips': trips,
        'hours': hours,
    }
    
    return render(request, 'core/trips/schedule.html', context)


# =============================================================================
# Driver Trip Views
# =============================================================================

@login_required
@driver_required
def driver_trips_view(request):
    """View driver's assigned trips"""
    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        messages.error(request, 'Driver profile not found.')
        return redirect('core:dashboard')
    
    status_filter = request.GET.get('status', '')
    
    trips = Trip.objects.filter(driver=driver)
    
    if status_filter:
        trips = trips.filter(status=status_filter)
    
    trips = trips.order_by('-departure_time')
    
    paginator = Paginator(trips, 10)
    page = request.GET.get('page')
    trips = paginator.get_page(page)
    
    return render(request, 'core/driver/trips.html', {
        'trips': trips,
        'status_filter': status_filter
    })


@login_required
@driver_required
def driver_trip_detail_view(request, trip_id):
    """Driver view trip details with passengers"""
    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        messages.error(request, 'Driver profile not found.')
        return redirect('core:dashboard')
    
    trip = get_object_or_404(Trip, id=trip_id, driver=driver)
    bookings = TripBooking.objects.filter(
        trip=trip,
        status=TripBooking.Status.CONFIRMED
    ).select_related('user')
    
    return render(request, 'core/driver/trip_detail.html', {
        'trip': trip,
        'bookings': bookings
    })


@login_required
@driver_required
def driver_start_trip_view(request, trip_id):
    """Driver starts a trip"""
    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        messages.error(request, 'Driver profile not found.')
        return redirect('core:dashboard')
    
    trip = get_object_or_404(Trip, id=trip_id, driver=driver)
    
    if trip.status != Trip.Status.UPCOMING:
        messages.warning(request, 'This trip cannot be started.')
        return redirect('core:driver_trips')
    
    if request.method == 'POST':
        trip.status = Trip.Status.ONGOING
        trip.save()
        
        driver.status = Driver.Status.ON_TRIP
        driver.save()
        
        messages.success(request, f'Trip "{trip.trip_name}" started!')
        return redirect('core:driver_trips')
    
    return render(request, 'core/driver/start_trip.html', {'trip': trip})


@login_required
@driver_required
def driver_complete_trip_view(request, trip_id):
    """Driver completes a trip"""
    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        messages.error(request, 'Driver profile not found.')
        return redirect('core:dashboard')
    
    trip = get_object_or_404(Trip, id=trip_id, driver=driver)
    
    if trip.status != Trip.Status.ONGOING:
        messages.warning(request, 'This trip cannot be completed.')
        return redirect('core:driver_trips')
    
    if request.method == 'POST':
        trip.status = Trip.Status.COMPLETED
        trip.save()
        
        # Update bookings to completed
        TripBooking.objects.filter(
            trip=trip,
            status=TripBooking.Status.CONFIRMED
        ).update(status=TripBooking.Status.COMPLETED)
        
        # Update driver stats
        driver.status = Driver.Status.AVAILABLE
        driver.total_trips += 1
        driver.save()
        
        messages.success(request, f'Trip "{trip.trip_name}" completed!')
        return redirect('core:driver_trips')
    
    return render(request, 'core/driver/complete_trip.html', {'trip': trip})


# =============================================================================
# Admin Logs View
# =============================================================================

@login_required
@admin_required
def admin_logs_view(request):
    """View admin action logs"""
    logs = AdminLog.objects.select_related('admin').order_by('-created_at')
    
    paginator = Paginator(logs, 20)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    return render(request, 'core/admin/logs.html', {'logs': logs})


# =============================================================================
# Helper Functions
# =============================================================================

def log_admin_action(admin_user, action_type, entity_type, entity_id, description):
    """Log an admin action"""
    AdminLog.objects.create(
        admin=admin_user,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description
    )
