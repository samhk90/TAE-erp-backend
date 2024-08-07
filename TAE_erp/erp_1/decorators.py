from django.shortcuts import redirect
from functools import wraps

def supabase_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'teacher_email' in request.session:
            # User is authenticated, proceed to the view
            return view_func(request, *args, **kwargs)
        # User is not authenticated, redirect to login page
        return redirect('login')  # Replace 'login' with your login URL name if different
    return _wrapped_view
