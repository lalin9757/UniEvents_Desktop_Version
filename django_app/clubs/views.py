from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Club, ClubMember, ClubCategory
from .forms import ClubForm, ClubMemberForm, JoinClubForm
from events.models import Event

def club_list(request):
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    clubs = Club.objects.filter(status='active')
    
    if category:
        clubs = clubs.filter(category__id=category)
    
    if search:
        clubs = clubs.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(short_description__icontains=search)
        )
    
    clubs = clubs.annotate(member_count=Count('members', filter=Q(members__status='active')))
    
    paginator = Paginator(clubs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ClubCategory.objects.all()
    
    context = {
        'clubs': page_obj,
        'categories': categories,
        'selected_category': category,
        'search_query': search,
    }
    return render(request, 'clubs/club_list.html', context)

def club_detail(request, slug):
    club = get_object_or_404(Club, slug=slug, status='active')
    
    is_member = False
    has_pending_request = False
    user_membership = None
    if request.user.is_authenticated:
        user_membership = ClubMember.objects.filter(
            club=club, 
            user=request.user, 
            status='active'
        ).first()
        is_member = user_membership is not None
        if not is_member:
            has_pending_request = ClubMember.objects.filter(
                club=club, user=request.user, status='pending'
            ).exists()
    
    upcoming_events = Event.objects.filter(
        club=club,
        status='published',
        start_date__gte=timezone.now()
    ).order_by('start_date')[:5]
    
    members = club.members.filter(status='active').select_related('user')
    
    context = {
        'club': club,
        'is_member': is_member,
        'has_pending_request': has_pending_request,
        'user_membership': user_membership,
        'upcoming_events': upcoming_events,
        'members': members,
    }
    return render(request, 'clubs/club_detail.html', context)

@login_required
def create_club(request):
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES)
        if form.is_valid():
            club = form.save(commit=False)
            club.president = request.user
            club.save()
            
            ClubMember.objects.create(
                club=club,
                user=request.user,
                role='president',
                status='active'
            )
            
            messages.success(request, 'Club created successfully! Waiting for admin approval.')
            return redirect('club_detail', slug=club.slug)
    else:
        form = ClubForm()
    
    return render(request, 'clubs/club_create.html', {'form': form})

@login_required
def join_club(request, slug):
    club = get_object_or_404(Club, slug=slug, status='active')

    # Block admin and superadmin from joining clubs
    if request.user.user_type in ('admin', 'president') or request.user.is_staff:
        messages.error(request, 'Admins and Presidents cannot join clubs as members.')
        return redirect('club_detail', slug=club.slug)
    
    existing_membership = ClubMember.objects.filter(
        club=club, 
        user=request.user
    ).first()
    
    if existing_membership:
        if existing_membership.status == 'active':
            messages.warning(request, 'You are already a member of this club.')
        else:
            messages.warning(request, 'You have already submitted a join request for this club.')
        return redirect('club_detail', slug=club.slug)
    
    if request.method == 'POST':
        form = JoinClubForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data.get('reason', '').strip()
            if not reason:
                messages.error(request, 'Please provide a reason for joining.')
            else:
                ClubMember.objects.create(
                    club=club,
                    user=request.user,
                    role='member',
                    status='pending',
                    additional_info=reason
                )
                messages.success(request, 'Join request submitted! The president will review your application.')
                return redirect('club_detail', slug=club.slug)
    else:
        form = JoinClubForm()
    
    context = {
        'club': club,
        'form': form
    }
    return render(request, 'clubs/club_join.html', context)

@login_required
def manage_club_members(request, slug):
    club = get_object_or_404(Club, slug=slug)
    
    if not (request.user == club.president or request.user.is_staff):
        messages.error(request, 'You do not have permission to manage this club.')
        return redirect('club_detail', slug=club.slug)
    
    pending_members = club.members.filter(status='pending')
    active_members = club.members.filter(status='active')
    
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        action = request.POST.get('action')
        
        try:
            member = ClubMember.objects.get(id=member_id, club=club)
            
            if action == 'approve':
                member.status = 'active'
                member.approved_by = request.user
                member.approved_at = timezone.now()
                member.save()
                messages.success(request, f'Approved {member.user.username}')
            
            elif action == 'reject':
                member.status = 'inactive'
                member.save()
                messages.success(request, f'Rejected {member.user.username}')
            
            elif action == 'remove':
                member.delete()
                messages.success(request, f'Removed {member.user.username}')
            
            elif action == 'change_role':
                new_role = request.POST.get('new_role')
                if new_role in dict(ClubMember.ROLE_CHOICES):
                    member.role = new_role
                    member.save()
                    messages.success(request, f'Updated role for {member.user.username}')
        
        except ClubMember.DoesNotExist:
            messages.error(request, 'Member not found.')
    
    context = {
        'club': club,
        'pending_members': pending_members,
        'active_members': active_members,
        'role_choices': ClubMember.ROLE_CHOICES,
    }
    return render(request, 'clubs/manage_members.html', context)