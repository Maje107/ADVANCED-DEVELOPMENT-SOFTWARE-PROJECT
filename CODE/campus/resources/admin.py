from django.contrib import admin
from .models import Booking, Resource, Building


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'campus_id')
    search_fields = ('name',)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'building', 'room_number', 'venue_type', 'capacity', 'opening_time', 'closing_time', 'created_at')
    list_filter = ('venue_type', 'building')
    search_fields = ('name', 'room_number', 'description')
    ordering = ('building', 'name')
    readonly_fields = ('created_at',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('resource', 'requested_by', 'booking_date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('resource__name', 'requested_by__full_name', 'phone_number')

