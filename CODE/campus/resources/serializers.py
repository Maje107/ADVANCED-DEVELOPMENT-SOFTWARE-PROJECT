from rest_framework import serializers
from .models import Resource, Building, Booking
from users.serializers import UserResponseSerializer
from datetime import datetime, time


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ('id', 'campus_id', 'name')


class ResourceResponseSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True, default='')
    location = serializers.CharField(read_only=True)
    type = serializers.CharField(source='venue_type', read_only=True)

    class Meta:
        model = Resource
        fields = (
            'id',
            'name',
            'building',
            'building_name',
            'room_number',
            'venue_type',
            'type',
            'capacity',
            'description',
            'opening_time',
            'closing_time',
            'location',
            'manager_id',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'building_name', 'location', 'type')


class ResourceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = (
            'name',
            'building',
            'room_number',
            'venue_type',
            'capacity',
            'description',
            'opening_time',
            'closing_time',
            'manager_id',
        )

    def validate_capacity(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError('Capacity must be at least 1.')
        return value


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('resource', 'booking_date', 'start_time', 'end_time', 'purpose', 'phone_number')

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})

        resource = attrs.get('resource')
        booking_date = attrs.get('booking_date')

        if resource and booking_date and start_time and end_time:
            # Check operating hours
            if start_time < resource.opening_time or end_time > resource.closing_time:
                raise serializers.ValidationError({
                    'start_time': f"Venue operating hours are {resource.opening_time.strftime('%H:%M')} to {resource.closing_time.strftime('%H:%M')}."
                })

            # Check if conflicting approved booking exists
            if Booking.check_conflict(resource.id, booking_date, start_time, end_time):
                raise serializers.ValidationError({
                    'detail': 'The requested venue is already booked and approved during this time slot.'
                })
        return attrs


class BookingResponseSerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    building_name = serializers.CharField(source='resource.building.name', read_only=True, default='')
    room_number = serializers.CharField(source='resource.room_number', read_only=True, default='')
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    requested_by_email = serializers.CharField(source='requested_by.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id',
            'resource',
            'resource_name',
            'building_name',
            'room_number',
            'requested_by',
            'requested_by_name',
            'requested_by_email',
            'booking_date',
            'start_time',
            'end_time',
            'purpose',
            'phone_number',
            'status',
            'status_display',
            'created_at',
        )
        read_only_fields = ('id', 'requested_by', 'status', 'created_at')


class TimeSlotSerializer(serializers.Serializer):
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    status = serializers.CharField()
    purpose = serializers.CharField(required=False, allow_blank=True)


class AvailabilityResponseSerializer(serializers.Serializer):
    resource_id = serializers.IntegerField()
    resource_name = serializers.CharField()
    building_name = serializers.CharField()
    date = serializers.CharField()
    operating_hours = serializers.CharField()
    is_fully_available = serializers.BooleanField()
    existing_bookings = TimeSlotSerializer(many=True)
    available_slots = TimeSlotSerializer(many=True)

