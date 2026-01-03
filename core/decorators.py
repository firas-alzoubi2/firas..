"""
Smart Transport Trip Management System - Decorators
Custom decorators for role-based access control
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def admin_required(view_func):
    """Decorator to restrict access to administrators only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('login')
        
        if not request.user.is_admin:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def driver_required(view_func):
    """Decorator to restrict access to drivers only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('login')
        
        if not request.user.is_driver:
            messages.error(request, 'This page is only accessible to drivers.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def passenger_required(view_func):
    """Decorator to restrict access to passengers only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('login')
        
        if not request.user.is_passenger:
            messages.error(request, 'This page is only accessible to passengers.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """Generic decorator to restrict access to specific roles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to access this page.')
                return redirect('login')
            
            if request.user.user_type not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
