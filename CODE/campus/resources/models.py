from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import datetime, time


class Building(models.Model):
    campus_id = models.IntegerField(default=1)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'buildings'
        ordering = ['id']

    def __str__(self):
        return self.name


class Resource(models.Model):
    TYPE_CHOICES = (
        ('Laboratory', 'Laboratory'),
        ('Classroom', 'Classroom'),
        ('Lecture Hall', 'Lecture Hall'),
        ('Auditorium', 'Auditorium'),
        ('Tutorial Room', 'Tutorial Room'),
        ('Event Venue', 'Event Venue'),
        ('Computer Lab', 'Computer Lab'),
    )

    name = models.CharField(max_length=150)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='venues', null=True, blank=True)
    room_number = models.CharField(max_length=50, blank=True, default='')
    venue_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Classroom', db_index=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    opening_time = models.TimeField(default=time(8, 0))
    closing_time = models.TimeField(default=time(17, 0))
    manager_id = models.CharField(max_length=100, default='22222222-2222-2222-2222-222222222222')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'venues'
        ordering = ['building', 'name']

    def __str__(self):
        return f"{self.name} ({self.room_number or self.venue_type})"

    @property
    def type(self):
        return self.venue_type

    @property
    def location(self):
        return f"{self.building.name if self.building else 'Campus'}, Room {self.room_number}" if self.room_number else (self.building.name if self.building else 'Main Campus')


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    )

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.TextField()
    phone_number = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.resource.name} - {self.booking_date} ({self.status})'

    @classmethod
    def check_conflict(cls, resource_id, booking_date, start_time, end_time, exclude_booking_id=None):
        """
        Returns True if an approved booking already overlaps with the requested interval.
        """
        qs = cls.objects.filter(
            resource_id=resource_id,
            booking_date=booking_date,
            status='approved',
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if exclude_booking_id:
            qs = qs.exclude(id=exclude_booking_id)
        return qs.exists()

