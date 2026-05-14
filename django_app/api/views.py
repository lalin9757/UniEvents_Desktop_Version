from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from clubs.models import Club, ClubMember
from events.models import Event, EventRegistration
from .serializers import (
    UserSerializer, ClubSerializer, EventSerializer,
    EventRegistrationSerializer, EventRegistrationCreateSerializer
)

class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Club.objects.filter(status='active')
    serializer_class = ClubSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category__name=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.filter(status='published')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        club_id = self.request.query_params.get('club')
        if club_id:
            queryset = queryset.filter(club_id=club_id)
        
        event_type = self.request.query_params.get('type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        time_filter = self.request.query_params.get('time')
        if time_filter == 'upcoming':
            queryset = queryset.filter(start_date__gte=timezone.now())
        elif time_filter == 'past':
            queryset = queryset.filter(start_date__lt=timezone.now())
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()
        user = request.user
        
        existing = EventRegistration.objects.filter(event=event, user=user).first()
        
        if existing:
            return Response({'detail': 'Already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not event.is_registration_open:
            return Response({'detail': 'Registration closed'}, status=status.HTTP_400_BAD_REQUEST)
        
        if event.max_participants and event.registration_count >= event.max_participants:
            return Response({'detail': 'Event full'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = EventRegistrationCreateSerializer(data=request.data)
        if serializer.is_valid():
            registration = serializer.save(event=event, user=user, status='registered')
            return Response(EventRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EventRegistration.objects.filter(user=self.request.user)

class UserEventsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        registered = EventRegistration.objects.filter(user=request.user).select_related('event')
        created = Event.objects.filter(created_by=request.user)
        
        data = {
            'registered_events': EventRegistrationSerializer(registered, many=True).data,
            'created_events': EventSerializer(created, many=True).data,
        }
        
        return Response(data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def scan_qr_code(request):
    qr_data = request.data.get('qr_data')
    parts = qr_data.split('|')
    
    if len(parts) != 3:
        return Response({'error': 'Invalid QR code'}, status=status.HTTP_400_BAD_REQUEST)
    
    registration_id = parts[0]
    
    try:
        registration = EventRegistration.objects.get(
            registration_id=registration_id,
            attended=False
        )
        
        registration.attended = True
        registration.attended_at = timezone.now()
        registration.status = 'attended'
        registration.save()
        
        return Response({
            'success': True,
            'message': f'Attendance marked for {registration.user.username}',
            'event': registration.event.title
        })
        
    except EventRegistration.DoesNotExist:
        return Response({'error': 'Invalid ticket'}, status=status.HTTP_400_BAD_REQUEST)

class CalendarAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        events = Event.objects.filter(
            Q(status='published') |
            Q(created_by=request.user)
        )
        
        if start and end:
            events = events.filter(start_date__gte=start, end_date__lte=end)
        
        data = []
        for event in events:
            data.append({
                'id': event.id,
                'title': event.title,
                'start': event.start_date.isoformat(),
                'end': event.end_date.isoformat(),
                'club': event.club.name,
                'color': event.category.color if event.category else '#007bff',
                'url': f'/events/{event.slug}/',
            })
        
        return Response(data)