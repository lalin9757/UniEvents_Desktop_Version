from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from .forms import StudentRegistrationForm, UserProfileForm


def register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type  = 'student'      # always student on self-register
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name  = form.cleaned_data.get('last_name', '')
            user.email      = form.cleaned_data.get('email', '')
            user.student_id = form.cleaned_data.get('student_id', '')
            user.intake     = form.cleaned_data.get('intake', '')
            user.department = form.cleaned_data.get('department', '')
            user.phone      = form.cleaned_data.get('phone', '')
            user.save()
            login(request, user)
            messages.success(request, f'Welcome to UniEvents, {user.username}! 🎉')
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


def home_view(request):
    from clubs.models import Club
    from events.models import Event
    from django.utils import timezone

    now = timezone.now()
    total_clubs   = Club.objects.filter(status='active').count()
    total_events  = Event.objects.count()
    total_students = CustomUser.objects.filter(user_type='student').count()

    ongoing_events = Event.objects.filter(
        status='published', start_date__lte=now, end_date__gte=now
    ).select_related('club').order_by('end_date')[:4]

    upcoming_events = Event.objects.filter(
        status='published', start_date__gt=now
    ).select_related('club').order_by('start_date')[:4]

    past_events = Event.objects.filter(
        status='published', end_date__lt=now
    ).select_related('club').order_by('-end_date')[:3]

    featured_clubs = Club.objects.filter(status='active').order_by('?')[:8]

    return render(request, 'home.html', {
        'total_clubs':    total_clubs,
        'total_events':   total_events,
        'total_students': total_students,
        'ongoing_events':  ongoing_events,
        'upcoming_events': upcoming_events,
        'past_events':     past_events,
        'featured_clubs':  featured_clubs,
    })
