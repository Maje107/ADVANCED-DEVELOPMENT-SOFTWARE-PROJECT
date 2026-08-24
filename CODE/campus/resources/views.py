from datetime import datetime, time
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Resource, Building, Booking
from .serializers import (
    BuildingSerializer,
    ResourceResponseSerializer,
    ResourceCreateUpdateSerializer,
    BookingCreateSerializer,
    BookingResponseSerializer,
    AvailabilityResponseSerializer,
)
from users.permissions import IsAdmin, IsBooker


class HealthCheck(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'service': 'spu-venue-booking-service',
            'status': 'ok',
            'university': 'Sol Plaatje University',
            'buildings_count': Building.objects.count(),
            'venues_count': Resource.objects.count(),
        })


class BuildingListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


class ResourceListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResourceResponseSerializer

    def get_queryset(self):
        queryset = Resource.objects.select_related('building').all()
        building_id = self.request.query_params.get('building') or self.request.query_params.get('building_id')
        venue_type = self.request.query_params.get('type') or self.request.query_params.get('venue_type')
        min_capacity = self.request.query_params.get('min_capacity')
        search = self.request.query_params.get('search')

        if building_id:
            queryset = queryset.filter(building_id=building_id)
        if venue_type:
            queryset = queryset.filter(venue_type__iexact=venue_type)
        if min_capacity:
            try:
                queryset = queryset.filter(capacity__gte=int(min_capacity))
            except ValueError:
                pass
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(room_number__icontains=search) |
                Q(building__name__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset


class ResourceCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = ResourceCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            resource = serializer.save()
            return Response(
                ResourceResponseSerializer(resource).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ResourceDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, resource_id):
        try:
            resource = Resource.objects.select_related('building').get(id=resource_id)
        except Resource.DoesNotExist:
            return Response({'detail': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ResourceResponseSerializer(resource).data)

    def put(self, request, resource_id):
        if not (request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)):
            return Response({'detail': 'Administrator access required to update venues.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            resource = Resource.objects.get(id=resource_id)
        except Resource.DoesNotExist:
            return Response({'detail': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResourceCreateUpdateSerializer(resource, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ResourceResponseSerializer(resource).data)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, resource_id):
        if not (request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)):
            return Response({'detail': 'Administrator access required to delete venues.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            resource = Resource.objects.get(id=resource_id)
        except Resource.DoesNotExist:
            return Response({'detail': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingListCreateView(APIView):
    permission_classes = [IsBooker]

    def get(self, request):
        if request.user.role == 'admin' or request.user.is_superuser:
            bookings = Booking.objects.select_related('resource', 'resource__building', 'requested_by').all()
        else:
            bookings = Booking.objects.select_related('resource', 'resource__building', 'requested_by').filter(requested_by=request.user)

        resource_id = request.query_params.get('resource_id')
        date_str = request.query_params.get('date')
        booking_status = request.query_params.get('status')

        if resource_id:
            bookings = bookings.filter(resource_id=resource_id)
        if date_str:
            bookings = bookings.filter(booking_date=date_str)
        if booking_status:
            bookings = bookings.filter(status=booking_status)

        serializer = BookingResponseSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(requested_by=request.user)
            return Response(
                BookingResponseSerializer(booking).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class BookingDetailView(APIView):
    permission_classes = [IsBooker]

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.select_related('resource', 'resource__building', 'requested_by').get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not (request.user.role == 'admin' or request.user.is_superuser or booking.requested_by == request.user):
            return Response({'detail': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(BookingResponseSerializer(booking).data)


class BookingCancelView(APIView):
    permission_classes = [IsBooker]

    def put(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not (request.user.role == 'admin' or request.user.is_superuser or booking.requested_by == request.user):
            return Response({'detail': 'You can only cancel your own bookings.'}, status=status.HTTP_403_FORBIDDEN)

        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
        return Response({
            'message': 'Booking cancelled successfully.',
            'booking': BookingResponseSerializer(booking).data,
        }, status=status.HTTP_200_OK)


class BookingStatusUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, booking_id):
        return self._update_status(request, booking_id)

    def patch(self, request, booking_id):
        return self._update_status(request, booking_id)

    def _update_status(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ('approved', 'declined', 'cancelled', 'pending'):
            return Response({'detail': 'Invalid status. Must be approved, declined, cancelled, or pending.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if new_status == 'approved':
            # Verify no conflicts exist
            if Booking.check_conflict(booking.resource_id, booking.booking_date, booking.start_time, booking.end_time, exclude_booking_id=booking.id):
                return Response({'detail': 'Cannot approve booking: A conflicting approved booking already exists for this slot.'}, status=status.HTTP_409_CONFLICT)

        booking.status = new_status
        booking.save(update_fields=['status'])
        return Response({
            'message': f'Booking status updated to {new_status}.',
            'booking': BookingResponseSerializer(booking).data,
        }, status=status.HTTP_200_OK)


class AvailabilityView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, resource_id):
        try:
            resource = Resource.objects.select_related('building').get(id=resource_id)
        except Resource.DoesNotExist:
            return Response({'detail': 'Venue not found.'}, status=status.HTTP_404_NOT_FOUND)

        date_str = request.query_params.get('date', '')
        if not date_str:
            return Response({'detail': 'date query parameter is required (YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve approved bookings for this venue and date
        approved_bookings = Booking.objects.filter(
            resource=resource,
            booking_date=check_date,
            status='approved',
        ).order_by('start_time')

        existing_bookings_data = [
            {
                'start_time': b.start_time.strftime('%H:%M'),
                'end_time': b.end_time.strftime('%H:%M'),
                'status': 'booked',
                'purpose': b.purpose,
            }
            for b in approved_bookings
        ]

        # Compute free slots between opening_time and closing_time
        available_slots = []
        cur_start = resource.opening_time

        for b in approved_bookings:
            if b.start_time > cur_start:
                available_slots.append({
                    'start_time': cur_start.strftime('%H:%M'),
                    'end_time': b.start_time.strftime('%H:%M'),
                    'status': 'available',
                    'purpose': 'Available for booking',
                })
            if b.end_time > cur_start:
                cur_start = b.end_time

        if cur_start < resource.closing_time:
            available_slots.append({
                'start_time': cur_start.strftime('%H:%M'),
                'end_time': resource.closing_time.strftime('%H:%M'),
                'status': 'available',
                'purpose': 'Available for booking',
            })

        data = {
            'resource_id': resource.id,
            'resource_name': resource.name,
            'building_name': resource.building.name if resource.building else 'Campus',
            'date': date_str,
            'operating_hours': f"{resource.opening_time.strftime('%H:%M')} - {resource.closing_time.strftime('%H:%M')}",
            'is_fully_available': len(approved_bookings) == 0,
            'existing_bookings': existing_bookings_data,
            'available_slots': available_slots,
        }
        return Response(AvailabilityResponseSerializer(data).data)

