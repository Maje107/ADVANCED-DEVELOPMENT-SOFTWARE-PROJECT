from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('health', views.HealthCheck.as_view(), name='health'),
    path('buildings', views.BuildingListView.as_view(), name='buildings_list'),
    path('venues', views.ResourceListView.as_view(), name='venues_list'),
    path('venues/create', views.ResourceCreateView.as_view(), name='venues_create'),
    path('venues/<int:resource_id>', views.ResourceDetailView.as_view(), name='venues_detail'),
    path('venues/<int:resource_id>/update', views.ResourceDetailView.as_view(), name='venues_update'),
    path('venues/<int:resource_id>/availability', views.AvailabilityView.as_view(), name='venues_availability'),
    path('bookings', views.BookingListCreateView.as_view(), name='bookings_list_create'),
    path('bookings/<int:booking_id>', views.BookingDetailView.as_view(), name='bookings_detail'),
    path('bookings/<int:booking_id>/cancel', views.BookingCancelView.as_view(), name='bookings_cancel'),
    path('bookings/<int:booking_id>/status', views.BookingStatusUpdateView.as_view(), name='bookings_status'),
    # Legacy alias routes for backward compatibility
    path('', views.ResourceListView.as_view(), name='list'),
    path('create', views.ResourceCreateView.as_view(), name='create'),
    path('<int:resource_id>', views.ResourceDetailView.as_view(), name='detail'),
    path('<int:resource_id>/update', views.ResourceDetailView.as_view(), name='update'),
    path('<int:resource_id>/availability', views.AvailabilityView.as_view(), name='availability'),
]

