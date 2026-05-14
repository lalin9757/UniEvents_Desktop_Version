from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import json

from clubs.models import Club, ClubMember, ClubCategory
from events.models import Event, EventRegistration, EventRequest, EventAnnouncement
from accounts.models import CustomUser


# ─────────────────────────────────────────────
# Helper decorators
# ─────────────────────────────────────────────

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.user_type == 'admin')

def is_president(user):
    return user.is_authenticated and Club.objects.filter(president=user, status='active').exists()

def admin_required(view_func):
    return login_required(user_passes_test(is_admin, login_url='/accounts/login/')(view_func))


# ─────────────────────────────────────────────
# MAIN DASHBOARD (role-based redirect)
# ─────────────────────────────────────────────

@login_required
def dashboard_home(request):
    user = request.user

    if is_admin(user):
        return redirect('admin_dashboard')

    if Club.objects.filter(president=user, status='active').exists():
        return redirect('president_dashboard')

    return redirect('student_dashboard')


# ─────────────────────────────────────────────
# ADMIN VIEWS
# ─────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    total_clubs = Club.objects.count()
    total_users = CustomUser.objects.count()
    total_events = Event.objects.count()
    pending_clubs = Club.objects.filter(status='pending').count()
    pending_event_requests = EventRequest.objects.filter(status='pending').count()
    total_students = CustomUser.objects.filter(user_type='student').count()
    total_presidents = Club.objects.filter(status='active').values('president').distinct().count()

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_events = Event.objects.filter(
        start_date__date__range=[week_start, week_end],
        status='published'
    ).count()

    recent_registrations = EventRegistration.objects.select_related(
        'event', 'user'
    ).order_by('-registration_date')[:10]

    pending_requests = EventRequest.objects.filter(
        status='pending'
    ).select_related('event', 'event__club', 'requested_by').order_by('-requested_at')[:5]

    context = {
        'total_clubs': total_clubs,
        'total_users': total_users,
        'total_events': total_events,
        'pending_clubs': pending_clubs,
        'pending_event_requests': pending_event_requests,
        'total_students': total_students,
        'total_presidents': total_presidents,
        'weekly_events': weekly_events,
        'recent_registrations': recent_registrations,
        'pending_requests': pending_requests,
    }
    return render(request, 'dashboard/admin/dashboard.html', context)


@login_required
def admin_club_list(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    clubs = Club.objects.all().select_related('president', 'category').annotate(
        member_count=Count('members', filter=Q(members__status='active'))
    ).order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        clubs = clubs.filter(status=status_filter)

    search = request.GET.get('search')
    if search:
        clubs = clubs.filter(Q(name__icontains=search) | Q(description__icontains=search))

    context = {
        'clubs': clubs,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'dashboard/admin/club_list.html', context)


@login_required
def admin_club_create(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        short_description = request.POST.get('short_description', '').strip()
        category_id = request.POST.get('category')
        president_id = request.POST.get('president')
        status = request.POST.get('status', 'active')

        if not name or not description or not president_id:
            messages.error(request, 'Name, description, and president are required.')
        else:
            try:
                president = CustomUser.objects.get(id=president_id, user_type='president')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Selected user is not a president account.')
                president = None

            if president:
                from django.utils.text import slugify
                slug = slugify(name)
                base_slug = slug
                counter = 1
                while Club.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                category = None
                if category_id:
                    try:
                        category = ClubCategory.objects.get(id=category_id)
                    except ClubCategory.DoesNotExist:
                        pass

                club = Club.objects.create(
                    name=name,
                    slug=slug,
                    description=description,
                    short_description=short_description,
                    category=category,
                    president=president,
                    status=status,
                )

                ClubMember.objects.get_or_create(
                    club=club,
                    user=president,
                    defaults={'role': 'president', 'status': 'active'}
                )

                messages.success(request, f'Club "{name}" created successfully.')
                return redirect('admin_club_list')

    presidents = CustomUser.objects.filter(user_type='president')
    categories = ClubCategory.objects.all()
    context = {'presidents': presidents, 'categories': categories}
    return render(request, 'dashboard/admin/club_form.html', context)


@login_required
def admin_club_edit(request, club_id):
    if not is_admin(request.user):
        return redirect('dashboard')

    club = get_object_or_404(Club, id=club_id)

    if request.method == 'POST':
        club.name = request.POST.get('name', club.name).strip()
        club.description = request.POST.get('description', club.description).strip()
        club.short_description = request.POST.get('short_description', '').strip()
        club.status = request.POST.get('status', club.status)
        club.email = request.POST.get('email', '').strip()

        president_id = request.POST.get('president')
        if president_id:
            try:
                new_president = CustomUser.objects.get(id=president_id, user_type='president')
                club.president = new_president
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid president selected.')

        category_id = request.POST.get('category')
        if category_id:
            try:
                club.category = ClubCategory.objects.get(id=category_id)
            except ClubCategory.DoesNotExist:
                pass

        club.save()
        messages.success(request, f'Club "{club.name}" updated successfully.')
        return redirect('admin_club_list')

    presidents = CustomUser.objects.filter(user_type='president')
    categories = ClubCategory.objects.all()
    context = {'club': club, 'presidents': presidents, 'categories': categories}
    return render(request, 'dashboard/admin/club_form.html', context)


@login_required
def admin_club_delete(request, club_id):
    if not is_admin(request.user):
        return redirect('dashboard')

    club = get_object_or_404(Club, id=club_id)

    if request.method == 'POST':
        name = club.name
        club.delete()
        messages.success(request, f'Club "{name}" deleted.')
        return redirect('admin_club_list')

    return render(request, 'dashboard/admin/club_confirm_delete.html', {'club': club})


@login_required
def admin_president_list(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    presidents = CustomUser.objects.filter(user_type='president').prefetch_related('president_of')
    context = {'presidents': presidents}
    return render(request, 'dashboard/admin/president_list.html', context)


@login_required
def admin_president_create(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        department = request.POST.get('department', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not username or not email or not password:
            messages.error(request, 'Username, email, and password are required.')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use.')
        else:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='president',
                department=department,
                phone=phone,
                is_verified=True,
            )

            # Club assign (optional)
            assign_club_id = request.POST.get('assign_club')
            if assign_club_id:
                try:
                    club = Club.objects.get(id=assign_club_id)
                    club.president = user
                    club.save()
                    ClubMember.objects.update_or_create(
                        club=club, user=user,
                        defaults={'role': 'president', 'status': 'active'}
                    )
                    messages.success(request, f'President account "{username}" created and assigned to "{club.name}".')
                except Club.DoesNotExist:
                    messages.success(request, f'President account "{username}" created.')
            else:
                messages.success(request, f'President account "{username}" created.')

            return redirect('admin_president_list')

    clubs = Club.objects.filter(status='active').select_related('president').order_by('name')
    return render(request, 'dashboard/admin/president_form.html', {'clubs': clubs})


@login_required
def admin_president_delete(request, user_id):
    if not is_admin(request.user):
        return redirect('dashboard')

    user = get_object_or_404(CustomUser, id=user_id, user_type='president')

    # Superadmin cannot be deleted
    if user.username == 'superadmin':
        messages.error(request, 'The superadmin account cannot be deleted.')
        return redirect('admin_president_list')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'President account "{username}" deleted.')
        return redirect('admin_president_list')

    return render(request, 'dashboard/admin/president_confirm_delete.html', {'president': user})


@login_required
def admin_event_requests(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    status_filter = request.GET.get('status', 'pending')
    requests_qs = EventRequest.objects.select_related(
        'event', 'event__club', 'requested_by'
    ).order_by('-requested_at')

    if status_filter and status_filter != 'all':
        requests_qs = requests_qs.filter(status=status_filter)

    context = {
        'event_requests': requests_qs,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/admin/event_requests.html', context)


@login_required
def admin_event_request_action(request, request_id):
    if not is_admin(request.user):
        return redirect('dashboard')

    event_request = get_object_or_404(EventRequest, id=request_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '').strip()

        if event_request.request_type == 'delete':
            if action == 'approve':
                event_title = event_request.event.title
                event_request.event.delete()
                messages.success(request, f'Event "{event_title}" permanently deleted.')
                event_request.admin_note = admin_note
                event_request.reviewed_at = timezone.now()
                event_request.reviewed_by = request.user
                # request is already deleted with event (CASCADE), so skip save
                return redirect('admin_event_requests')
            elif action == 'reject':
                event_request.status = 'rejected'
                messages.warning(request, f'Delete request for "{event_request.event.title}" rejected.')
        else:
            if action == 'approve':
                event_request.status = 'approved'
                event_request.event.status = 'published'
                event_request.event.save()
                messages.success(request, f'Event "{event_request.event.title}" approved and published.')
            elif action == 'reject':
                event_request.status = 'rejected'
                event_request.event.status = 'draft'
                event_request.event.save()
                messages.warning(request, f'Event "{event_request.event.title}" rejected.')

        event_request.admin_note = admin_note
        event_request.reviewed_at = timezone.now()
        event_request.reviewed_by = request.user
        event_request.save()

    return redirect('admin_event_requests')


@login_required
def admin_statistics(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    total_users = CustomUser.objects.count()
    total_students = CustomUser.objects.filter(user_type='student').count()
    total_presidents = CustomUser.objects.filter(user_type='president').count()
    total_clubs = Club.objects.count()
    active_clubs = Club.objects.filter(status='active').count()
    total_events = Event.objects.count()
    published_events = Event.objects.filter(status='published').count()
    total_registrations = EventRegistration.objects.count()
    pending_event_requests = EventRequest.objects.filter(status='pending').count()
    approved_requests = EventRequest.objects.filter(status='approved').count()
    rejected_requests = EventRequest.objects.filter(status='rejected').count()

    top_clubs = Club.objects.filter(status='active').annotate(
        member_count=Count('members', filter=Q(members__status='active'))
    ).order_by('-member_count')[:5]

    top_events = Event.objects.filter(status='published').annotate(
        reg_count=Count('registrations', filter=Q(registrations__status='registered'))
    ).order_by('-reg_count')[:5]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_presidents': total_presidents,
        'total_clubs': total_clubs,
        'active_clubs': active_clubs,
        'total_events': total_events,
        'published_events': published_events,
        'total_registrations': total_registrations,
        'pending_event_requests': pending_event_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'top_clubs': top_clubs,
        'top_events': top_events,
    }
    return render(request, 'dashboard/admin/statistics.html', context)


# ─────────────────────────────────────────────
# PRESIDENT VIEWS
# ─────────────────────────────────────────────

@login_required
def president_dashboard(request):
    user = request.user
    club = Club.objects.filter(president=user, status='active').first()

    if not club:
        messages.error(request, 'You are not a president of any active club.')
        return redirect('student_dashboard')

    club_members_count = ClubMember.objects.filter(club=club, status='active').count()
    club_events_count = Event.objects.filter(club=club).count()
    pending_join_requests = ClubMember.objects.filter(club=club, status='pending').count()
    pending_event_requests = EventRequest.objects.filter(
        event__club=club, status='pending'
    ).count()

    upcoming_events = Event.objects.filter(
        club=club,
        status='published',
        start_date__gte=timezone.now()
    ).order_by('start_date')[:5]

    recent_members = ClubMember.objects.filter(
        club=club, status='active'
    ).select_related('user').order_by('-joined_date')[:5]

    context = {
        'club': club,
        'club_members_count': club_members_count,
        'club_events_count': club_events_count,
        'pending_join_requests': pending_join_requests,
        'pending_event_requests': pending_event_requests,
        'upcoming_events': upcoming_events,
        'recent_members': recent_members,
    }
    return render(request, 'dashboard/president/dashboard.html', context)


@login_required
def president_event_create(request):
    user = request.user
    club = Club.objects.filter(president=user, status='active').first()

    if not club:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        short_description = request.POST.get('short_description', '').strip()
        venue = request.POST.get('venue', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        event_type = request.POST.get('event_type', 'workshop')
        max_participants = request.POST.get('max_participants') or None
        is_free = request.POST.get('is_free') == 'on'
        fee = request.POST.get('fee', '0.00')

        if not all([title, description, venue, start_date, end_date]):
            messages.error(request, 'All required fields must be filled.')
        else:
            from django.utils.text import slugify
            slug = slugify(title)
            base_slug = slug
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            event = Event.objects.create(
                title=title,
                slug=slug,
                description=description,
                short_description=short_description,
                venue=venue,
                start_date=start_date,
                end_date=end_date,
                event_type=event_type,
                max_participants=max_participants,
                is_free=is_free,
                fee=fee if not is_free else 0,
                club=club,
                created_by=user,
                status='draft',  # Admin approve করলে published হবে
            )

            # Auto-create event request
            EventRequest.objects.create(
                event=event,
                requested_by=user,
                status='pending',
            )

            messages.success(request, f'Event "{title}" submitted for admin approval.')
            return redirect('president_event_list')

    event_types = Event.EVENT_TYPE_CHOICES
    context = {'club': club, 'event_types': event_types}
    return render(request, 'dashboard/president/event_form.html', context)


@login_required
def president_event_list(request):
    user = request.user
    club = Club.objects.filter(president=user, status='active').first()

    if not club:
        return redirect('dashboard')

    events = Event.objects.filter(club=club).select_related('request').order_by('-created_at')
    context = {'club': club, 'events': events}
    return render(request, 'dashboard/president/event_list.html', context)


@login_required
def president_announcement_create(request, event_id):
    user = request.user
    club = Club.objects.filter(president=user, status='active').first()

    if not club:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    event = get_object_or_404(Event, id=event_id, club=club)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        announcement_type = request.POST.get('announcement_type', 'general')

        if not title or not message:
            messages.error(request, 'Title and message are required.')
        else:
            EventAnnouncement.objects.create(
                event=event,
                posted_by=user,
                title=title,
                message=message,
                announcement_type=announcement_type,
            )

            # If cancellation, update event status
            if announcement_type == 'cancellation':
                event.status = 'cancelled'
                event.save()
                messages.warning(request, 'Event marked as cancelled.')
            else:
                messages.success(request, 'Announcement posted successfully.')

            return redirect('president_event_list')

    announcement_types = EventAnnouncement.TYPE_CHOICES
    context = {'event': event, 'club': club, 'announcement_types': announcement_types}
    return render(request, 'dashboard/president/announcement_form.html', context)


@login_required
def president_join_requests(request):
    user = request.user
    club = Club.objects.filter(president=user, status='active').first()

    if not club:
        return redirect('dashboard')

    pending = ClubMember.objects.filter(
        club=club, status='pending'
    ).select_related('user').order_by('-joined_date')

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        action = request.POST.get('action')

        try:
            member = ClubMember.objects.get(id=member_id, club=club)
            if action == 'approve':
                member.status = 'active'
                member.approved_by = user
                member.approved_at = timezone.now()
                member.save()
                messages.success(request, f'{member.user.get_full_name() or member.user.username} approved.')
            elif action == 'reject':
                member.status = 'inactive'
                member.save()
                messages.warning(request, f'{member.user.get_full_name() or member.user.username} rejected.')
        except ClubMember.DoesNotExist:
            messages.error(request, 'Member not found.')

        return redirect('president_join_requests')

    context = {'club': club, 'pending_members': pending}
    return render(request, 'dashboard/president/join_requests.html', context)


@login_required
def president_member_list(request):
    user = request.user
    club = Club.objects.filter(president=user, status='active').first()

    if not club:
        return redirect('dashboard')

    members = ClubMember.objects.filter(
        club=club, status='active'
    ).select_related('user').order_by('role', 'joined_date')

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        action = request.POST.get('action')

        try:
            member = ClubMember.objects.get(id=member_id, club=club)

            if action == 'change_role':
                new_role = request.POST.get('new_role')
                if new_role == 'president':
                    messages.error(request, 'Cannot assign president role from here. Contact admin.')
                elif new_role in dict(ClubMember.ROLE_CHOICES):
                    member.role = new_role
                    member.save()
                    messages.success(request, f'Role updated for {member.user.username}.')
                else:
                    messages.error(request, 'Invalid role.')

            elif action == 'remove':
                name = member.user.username
                member.delete()
                messages.success(request, f'{name} removed from club.')

        except ClubMember.DoesNotExist:
            messages.error(request, 'Member not found.')

        return redirect('president_member_list')

    context = {
        'club': club,
        'members': members,
        'role_choices': ClubMember.ROLE_CHOICES,
    }
    return render(request, 'dashboard/president/member_list.html', context)


@login_required
def president_registered_students(request, event_id):
    user = request.user
    club = Club.objects.filter(president=user, status='active').first()

    if not club:
        return redirect('dashboard')

    event = get_object_or_404(Event, id=event_id, club=club)

    registrations = EventRegistration.objects.filter(
        event=event,
        status__in=['registered', 'attended']
    ).select_related('user').order_by('-registration_date')

    context = {
        'event': event,
        'club': club,
        'registrations': registrations,
        'total': registrations.count(),
    }
    return render(request, 'dashboard/president/registered_students.html', context)

@login_required
def president_event_delete_request(request, event_id):
    user = request.user
    club = Club.objects.filter(president=user, status='active').first()
    if not club:
        return redirect('dashboard')

    event = get_object_or_404(Event, id=event_id, club=club)

    # Already has a pending delete request?
    from events.models import EventRequest
    existing = EventRequest.objects.filter(event=event, request_type='delete', status='pending').first()
    if existing:
        messages.warning(request, 'ইতিমধ্যে একটি delete request pending আছে।')
        return redirect('president_event_list')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Delete request এর কারণ লিখতে হবে।')
        else:
            # Update or create request
            req, created = EventRequest.objects.get_or_create(
                event=event,
                defaults={'requested_by': user, 'request_type': 'delete', 'status': 'pending', 'delete_reason': reason}
            )
            if not created:
                req.request_type = 'delete'
                req.status = 'pending'
                req.delete_reason = reason
                req.save()
            messages.success(request, f'Event "{event.title}" এর delete request admin এর কাছে পাঠানো হয়েছে।')
            return redirect('president_event_list')

    context = {'event': event, 'club': club}
    return render(request, 'dashboard/president/event_delete_request.html', context)


# ─────────────────────────────────────────────
# STUDENT VIEWS
# ─────────────────────────────────────────────

@login_required
def student_dashboard(request):
    user = request.user

    my_clubs = ClubMember.objects.filter(
        user=user, status='active'
    ).select_related('club').order_by('-joined_date')

    pending_clubs = ClubMember.objects.filter(
        user=user, status='pending'
    ).select_related('club')

    my_registrations = EventRegistration.objects.filter(
        user=user,
        status__in=['registered', 'attended']
    ).select_related('event', 'event__club').order_by('event__start_date')

    upcoming_registrations = my_registrations.filter(
        event__start_date__gte=timezone.now()
    )

    # Announcements for events the student is registered for
    registered_event_ids = my_registrations.values_list('event_id', flat=True)
    announcements = EventAnnouncement.objects.filter(
        event__id__in=registered_event_ids
    ).select_related('event').order_by('-created_at')[:10]

    # Browse: upcoming published events not yet registered
    available_events = Event.objects.filter(
        status='published',
        start_date__gte=timezone.now()
    ).exclude(
        id__in=registered_event_ids
    ).order_by('start_date')[:6]

    context = {
        'my_clubs': my_clubs,
        'pending_clubs': pending_clubs,
        'my_registrations': my_registrations,
        'upcoming_registrations': upcoming_registrations,
        'announcements': announcements,
        'available_events': available_events,
    }
    return render(request, 'dashboard/student/dashboard.html', context)


# ─────────────────────────────────────────────
# LEGACY VIEWS (kept for backward compatibility)
# ─────────────────────────────────────────────

@login_required
def calendar_view(request):
    from events.models import Event
    import json

    events = Event.objects.filter(
        Q(status='published') | Q(created_by=request.user)
    )

    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'club': event.club.name,
            'color': event.category.color if event.category else '#007bff',
            'url': f'/events/{event.slug}/',
        })

    return render(request, 'dashboard/calendar.html', {
        'events_json': json.dumps(event_list)
    })


@login_required
def my_clubs(request):
    memberships = ClubMember.objects.filter(
        user=request.user, status='active'
    ).select_related('club')

    pending_memberships = ClubMember.objects.filter(
        user=request.user, status='pending'
    ).select_related('club')

    context = {
        'active_memberships': memberships,
        'pending_memberships': pending_memberships,
    }
    return render(request, 'dashboard/my_clubs.html', context)


@login_required
def my_events(request):
    registered_events = EventRegistration.objects.filter(
        user=request.user
    ).select_related('event').order_by('-registration_date')

    created_events = Event.objects.filter(
        created_by=request.user
    ).order_by('-created_at')

    context = {
        'registered_events': registered_events,
        'created_events': created_events,
    }
    return render(request, 'dashboard/my_events.html', context)


@login_required
def attendance_view(request):
    registrations = EventRegistration.objects.filter(
        user=request.user,
        event__status='published'
    ).select_related('event').order_by('-registration_date')

    attended = [r for r in registrations if r.attended]
    upcoming = [r for r in registrations if not r.attended and r.event.start_date > timezone.now()]

    context = {
        'attended_events': attended,
        'upcoming_registrations': upcoming,
    }
    return render(request, 'dashboard/attendance.html', context)
