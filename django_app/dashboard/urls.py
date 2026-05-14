from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard (role-based redirect)
    path('', views.dashboard_home, name='dashboard'),

    # ── Admin ──────────────────────────────────────────
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/statistics/', views.admin_statistics, name='admin_statistics'),

    # Club management
    path('admin/clubs/', views.admin_club_list, name='admin_club_list'),
    path('admin/clubs/create/', views.admin_club_create, name='admin_club_create'),
    path('admin/clubs/<int:club_id>/edit/', views.admin_club_edit, name='admin_club_edit'),
    path('admin/clubs/<int:club_id>/delete/', views.admin_club_delete, name='admin_club_delete'),

    # President account management
    path('admin/presidents/', views.admin_president_list, name='admin_president_list'),
    path('admin/presidents/create/', views.admin_president_create, name='admin_president_create'),
    path('admin/presidents/<int:user_id>/delete/', views.admin_president_delete, name='admin_president_delete'),

    # Event request approve/reject
    path('admin/event-requests/', views.admin_event_requests, name='admin_event_requests'),
    path('admin/event-requests/<int:request_id>/action/', views.admin_event_request_action, name='admin_event_request_action'),

    # ── President ──────────────────────────────────────
    path('president/', views.president_dashboard, name='president_dashboard'),
    path('president/events/', views.president_event_list, name='president_event_list'),
    path('president/events/create/', views.president_event_create, name='president_event_create'),
    path('president/events/<int:event_id>/announcement/', views.president_announcement_create, name='president_announcement_create'),
    path('president/events/<int:event_id>/students/', views.president_registered_students, name='president_registered_students'),
    path('president/join-requests/', views.president_join_requests, name='president_join_requests'),
    path('president/members/', views.president_member_list, name='president_member_list'),
    path('president/events/<int:event_id>/delete-request/', views.president_event_delete_request, name='president_event_delete_request'),

    # ── Student ───────────────────────────────────────
    path('student/', views.student_dashboard, name='student_dashboard'),

    # ── Legacy routes (backward compatibility) ─────────
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('my-clubs/', views.my_clubs, name='my_clubs'),
    path('my-events/', views.my_events, name='my_events'),
    path('attendance/', views.attendance_view, name='attendance'),
]
