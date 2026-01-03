"""
Smart Transport Trip Management System - Forms
Implements form validation and user input handling
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User, Account, Driver, Vehicle, Trip, TripBooking, Rating


class UserRegistrationForm(UserCreationForm):
    """Form for passenger registration"""
    
    USER_TYPE_CHOICES = [
        (User.UserType.PASSENGER, 'Passenger'),
        (User.UserType.DRIVER, 'Driver'),
    ]
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (optional)'
        })
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial=User.UserType.PASSENGER
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )
    
    # Driver specific fields
    license_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control driver-field',
            'placeholder': 'License Number'
        })
    )
    license_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control driver-field',
            'placeholder': 'License Type'
        })
    )
    license_expiry = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control driver-field',
            'type': 'date'
        })
    )
    
    class Meta:
        model = User
        fields = ['email', 'username', 'phone', 'user_type', 'password1', 'password2', 'license_number', 'license_type', 'license_expiry']
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == User.UserType.DRIVER:
            if not cleaned_data.get('license_number'):
                self.add_error('license_number', 'License number is required for drivers.')
            if not cleaned_data.get('license_type'):
                self.add_error('license_type', 'License type is required for drivers.')
            if not cleaned_data.get('license_expiry'):
                self.add_error('license_expiry', 'License expiry date is required for drivers.')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
            # Create associated account
            Account.objects.create(user=user)
            
            # Create driver profile if user is a driver
            if user.user_type == User.UserType.DRIVER:
                Driver.objects.create(
                    user=user,
                    license_number=self.cleaned_data['license_number'],
                    license_type=self.cleaned_data['license_type'],
                    license_expiry=self.cleaned_data['license_expiry']
                )
        return user


class LoginForm(AuthenticationForm):
    """Custom login form"""
    
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with Bootstrap styling"""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )


class AdminUserForm(forms.ModelForm):
    """Form for admin to create/edit users"""
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to keep current password'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'user_type', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VehicleForm(forms.ModelForm):
    """Form for vehicle management"""
    
    class Meta:
        model = Vehicle
        fields = [
            'plate_number', 'vehicle_type', 'brand', 'model',
            'year', 'capacity', 'color', 'status'
        ]
        widgets = {
            'plate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class DriverForm(forms.ModelForm):
    """Form for driver profile management"""
    
    class Meta:
        model = Driver
        fields = ['license_number', 'license_type', 'license_expiry', 'vehicle', 'status']
        widgets = {
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_type': forms.TextInput(attrs={'class': 'form-control'}),
            'license_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CreateDriverForm(forms.Form):
    """Form for creating a new driver with user account"""
    
    # User fields
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    # Driver fields
    license_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    license_type = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    license_expiry = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.filter(status=Vehicle.Status.AVAILABLE),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class TripForm(forms.ModelForm):
    """Form for creating and editing trips"""
    
    class Meta:
        model = Trip
        fields = [
            'trip_name', 'driver', 'vehicle', 'start_location', 'end_location',
            'departure_time', 'arrival_time', 'price', 'available_seats', 'status'
        ]
        widgets = {
            'trip_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'start_location': forms.TextInput(attrs={'class': 'form-control'}),
            'end_location': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'arrival_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get('departure_time')
        arrival = cleaned_data.get('arrival_time')
        
        if departure and arrival and arrival <= departure:
            raise ValidationError('Arrival time must be after departure time')
        
        return cleaned_data


class TripSearchForm(forms.Form):
    """Form for searching trips"""
    
    start_location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'From (Start Location)'
        })
    )
    end_location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'To (End Location)'
        })
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class BookingForm(forms.Form):
    """Form for booking a trip"""
    
    seats = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, trip=None, **kwargs):
        super().__init__(*args, **kwargs)
        if trip:
            self.fields['seats'].max_value = trip.available_seats
            self.fields['seats'].widget.attrs['max'] = trip.available_seats


class RatingForm(forms.ModelForm):
    """Form for rating a trip"""
    
    driver_rating = forms.ChoiceField(
        choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    vehicle_rating = forms.ChoiceField(
        choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Rating
        fields = ['driver_rating', 'vehicle_rating', 'driver_comment']
        widgets = {
            'driver_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience (optional)'
            }),
        }


class CancelTripForm(forms.Form):
    """Form for cancelling a trip"""
    
    cancellation_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for cancellation'
        })
    )


class AccountStatusForm(forms.Form):
    """Form for changing account status"""
    
    status = forms.ChoiceField(
        choices=Account.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
