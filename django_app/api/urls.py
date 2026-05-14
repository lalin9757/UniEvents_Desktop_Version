from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clubs', views.ClubViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'registrations', views.EventRegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
    path('user/events/', views.UserEventsAPIView.as_view(), name='user-events'),
    path('scan-qr/', views.scan_qr_code, name='scan-qr'),
    path('calendar/', views.CalendarAPIView.as_view(), name='calendar-api'),
]