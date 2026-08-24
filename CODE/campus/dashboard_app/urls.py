from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('choose-role/', views.choose_role, name='choose_role'),
    path('student-leadership/', views.student_leadership, name='student_leadership'),
    path('login/', views.dashboard_login, name='login'),
    path('signup/', views.dashboard_signup, name='signup'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),

    path('users/', views.dashboard_users, name='users'),
    path('users/<int:user_id>/edit/', views.dashboard_users_edit, name='users_edit'),
    path('users/<int:user_id>/delete/', views.dashboard_users_delete, name='users_delete'),

    path('resources/', views.dashboard_resources, name='resources'),
    path('resources/create/', views.dashboard_resources_create, name='resources_create'),
    path('resources/<int:resource_id>/edit/', views.dashboard_resources_edit, name='resources_edit'),
    path('resources/<int:resource_id>/delete/', views.dashboard_resources_delete, name='resources_delete'),
    path('resources/<int:resource_id>/availability-api/', views.venue_availability_api, name='venue_availability_api'),

    path('resources/<int:resource_id>/book/', views.booking_create, name='booking_create'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/requests/', views.booking_requests, name='booking_requests'),
    path('bookings/<int:booking_id>/status/', views.booking_update_status, name='booking_update_status'),
    path('bookings/<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('bookings/reports/', views.booking_reports, name='booking_reports'),
]
