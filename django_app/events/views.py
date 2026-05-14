from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from .models import Event, EventRegistration, EventCategory
from .forms import EventForm, EventRegistrationForm, EventFilterForm
from clubs.models import ClubMember

def event_list(request):
    from clubs.models import Club
    events = Event.objects.filter(status='published').select_related('club', 'category')

    search = request.GET.get('search', '').strip()
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(venue__icontains=search)
        )

    club_slug = request.GET.get('club', '').strip()
    if club_slug:
        events = events.filter(club__slug=club_slug)

    event_type = request.GET.get('event_type', '').strip()
    if event_type:
        events = events.filter(event_type=event_type)

    now = timezone.now()
    ongoing_events = events.filter(start_date__lte=now, end_date__gte=now).order_by('start_date')
    upcoming_events = events.filter(start_date__gt=now).order_by('start_date')
    past_events = events.filter(end_date__lt=now).order_by('-start_date')

    ongoing_paginator = Paginator(ongoing_events, 9)
    ongoing_page = request.GET.get('ongoing_page')
    ongoing_events_page = ongoing_paginator.get_page(ongoing_page)

    upcoming_paginator = Paginator(upcoming_events, 9)
    upcoming_page = request.GET.get('upcoming_page')
    upcoming_events_page = upcoming_paginator.get_page(upcoming_page)

    past_paginator = Paginator(past_events, 9)
    past_page = request.GET.get('past_page')
    past_events_page = past_paginator.get_page(past_page)

    clubs = Club.objects.filter(status='active').order_by('name')

    context = {
        'ongoing_events': ongoing_events_page,
        'upcoming_events': upcoming_events_page,
        'past_events': past_events_page,
        'clubs': clubs,
        'event_types': Event.EVENT_TYPE_CHOICES,
        'search': search,
        'selected_club': club_slug,
        'selected_type': event_type,
        'now': now,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    
    is_registered = False
    registration = None
    if request.user.is_authenticated:
        registration = EventRegistration.objects.filter(
            event=event,
            user=request.user,
            status__in=['registered', 'attended']
        ).first()
        is_registered = registration is not None
    
    similar_events = Event.objects.filter(
        category=event.category,
        status='published',
        start_date__gte=timezone.now()
    ).exclude(id=event.id)[:4]
    
    registration_count = event.registration_count
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'registration': registration,
        'similar_events': similar_events,
        'registration_count': registration_count,
        'is_full': event.max_participants and registration_count >= event.max_participants,
        'now': timezone.now(),
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def event_register(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')

    # Block admin and president from registering
    if request.user.user_type in ('admin', 'president') or request.user.is_staff:
        messages.error(request, 'Admins and Presidents cannot register for events.')
        return redirect('event_detail', slug=slug)

    # Block registration for past events or if deadline passed
    from django.utils import timezone
    now = timezone.now()
    if event.end_date and event.end_date < now:
        messages.error(request, 'Registration is closed. This event has already ended.')
        return redirect('event_detail', slug=slug)
    if event.registration_close and event.registration_close < now:
        messages.error(request, 'Registration deadline has passed for this event.')
        return redirect('event_detail', slug=slug)
    if event.start_date and event.start_date < now and not event.end_date:
        messages.error(request, 'Registration is closed. This event has already started.')
        return redirect('event_detail', slug=slug)
    
    if request.method == 'POST':
        # Require confirmation flag from popup
        if not request.POST.get('confirmed'):
            messages.error(request, 'Please confirm your registration.')
            return redirect('event_detail', slug=slug)

        existing = EventRegistration.objects.filter(event=event, user=request.user).first()
        
        if existing:
            messages.warning(request, 'You are already registered for this event.')
            return redirect('event_detail', slug=slug)
        
        if not event.is_registration_open:
            messages.error(request, 'Registration is not open for this event.')
            return redirect('event_detail', slug=slug)
        
        if event.max_participants and event.registration_count >= event.max_participants:
            messages.error(request, 'Event is full.')
            return redirect('event_detail', slug=slug)
        
        registration = EventRegistration.objects.create(
            event=event,
            user=request.user,
            status='registered'
        )
        
        messages.success(request, 'Successfully registered for the event!')
        return redirect('event_detail', slug=slug)
    
    return redirect('event_detail', slug=slug)

@login_required
def event_create(request, club_slug=None):
    club = None
    if club_slug:
        club = get_object_or_404('clubs.Club', slug=club_slug)
        
        membership = ClubMember.objects.filter(
            club=club,
            user=request.user,
            status='active',
            role__in=['president', 'vice_president', 'secretary', 'executive']
        ).exists()
        
        if not membership and not request.user.is_staff:
            messages.error(request, 'You do not have permission to create events for this club.')
            return redirect('club_detail', slug=club_slug)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            if club:
                event.club = club
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', slug=event.slug)
    else:
        form = EventForm()
    
    context = {'form': form, 'club': club}
    return render(request, 'events/event_create.html', context)

