import secrets
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from datetime import datetime, time
from users.models import User
from resources.models import Resource, Building, Booking


def choose_role(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        role = request.POST.get('role', 'student_leader')
        if role in ('admin', 'lecturer', 'student_leader'):
            request.session['selected_role'] = role
            return redirect('dashboard:login')
        else:
            messages.error(request, 'Please choose a valid portal role.')
    return render(request, 'dashboard/choose_role.html')


def student_leadership(request):
    if request.method == 'POST':
        leadership_role = request.POST.get('leadership_role')
        if leadership_role in dict(User.LEADERSHIP_ROLE_CHOICES):
            request.session['leadership_role'] = leadership_role
            request.session['selected_role'] = 'student_leader'
            return redirect('dashboard:login')
        messages.error(request, 'Please select a student leadership designation.')
    return render(request, 'dashboard/student_leadership.html', {
        'leadership_choices': User.LEADERSHIP_ROLE_CHOICES,
    })


def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # If the user visits /dashboard/login directly without picking a role, default or redirect to choose_role
    selected_role = request.session.get('selected_role')
    if not selected_role:
        return redirect('dashboard:choose_role')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', selected_role)
        
        user = authenticate(request, email=email, password=password)
        if user:
            # Enforce strict role validation on credentials submission ONLY
            if user.role != role:
                messages.error(
                    request,
                    f'Access Denied: Your account is registered as "{user.get_role_display()}", '
                    f'which does not match the selected "{dict(User.ROLE_CHOICES).get(role, role)}" portal role.'
                )
            elif not user.is_active:
                messages.error(request, 'This account is deactivated. Please contact SPU Administration.')
            else:
                login(request, user)
                request.session['selected_role'] = user.role
                messages.success(request, f'Welcome back, {user.full_name}!')
                next_url = request.GET.get('next') or 'dashboard:home'
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid email address or password. Please check your credentials.')

    return render(request, 'dashboard/login.html', {
        'selected_role': selected_role,
        'role_choices': User.ROLE_CHOICES,
    })



def dashboard_signup(request):
    selected_role = request.session.get('selected_role', 'student_leader')
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = request.POST.get('role', selected_role)
        student_number = request.POST.get('student_number', '').strip() or None
        phone_number = request.POST.get('phone_number', '').strip()
        leadership_role = request.POST.get('leadership_role', '')

        if not all([full_name, email, password, password_confirm]):
            messages.error(request, 'All required fields must be completed.')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match. Please re-enter.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif role == 'admin':
            messages.error(request, 'Administrator registration is not permitted. Please contact IT Support.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email address is already registered.')
        elif student_number and User.objects.filter(student_number=student_number).exists():
            messages.error(request, 'An account with this student number is already registered.')
        else:
            try:
                user = User.objects.create_user(
                    full_name=full_name,
                    email=email,
                    password=password,
                    role=role,
                    student_number=student_number,
                    phone_number=phone_number,
                    leadership_role=leadership_role if role == 'student_leader' else '',
                )
                login(request, user)
                messages.success(request, f'Welcome to Sol Plaatje University Venue Management, {user.full_name}!')
                return redirect('dashboard:home')
            except Exception as error:
                messages.error(request, f'Registration error: {error}')
    return render(request, 'dashboard/signup.html', {
        'selected_role': selected_role,
        'leadership_choices': User.LEADERSHIP_ROLE_CHOICES,
    })


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
            # Generate a 6-digit numeric security OTP verification code
            otp_code = f"{random.randint(100000, 999999)}"
            user.reset_token = otp_code
            user.save(update_fields=['reset_token'])
            
            # Since email/SMS sending is limited (per specification 5.2),
            # provide immediate verification code directly in user-facing message & session
            request.session['reset_email'] = email
            request.session['reset_token'] = otp_code
            messages.success(
                request,
                f'Password Reset Authorization Code for {email}: [{otp_code}]. '
                'Please enter this code below along with your new password.'
            )
            return redirect('dashboard:reset_password')
        except User.DoesNotExist:
            messages.error(request, 'No registered SPU account found with that email address.')
    return render(request, 'dashboard/forgot_password.html')


def reset_password_view(request):
    initial_email = request.session.get('reset_email', '')
    initial_token = request.session.get('reset_token', '')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        token = request.POST.get('reset_token', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not all([email, token, new_password, confirm_password]):
            messages.error(request, 'All fields are required.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match. Please re-enter.')
        elif len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters long.')
        else:
            try:
                user = User.objects.get(email=email, reset_token=token)
                # Set brand new password directly without old password verification
                user.set_password(new_password)
                user.reset_token = None
                user.save()
                
                # Clear reset session data
                request.session.pop('reset_email', None)
                request.session.pop('reset_token', None)
                
                messages.success(request, 'Your password has been successfully updated! You can now sign in.')
                return redirect('dashboard:login')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email address or reset authorization code. Please request a new code.')

    return render(request, 'dashboard/reset_password.html', {
        'email': initial_email,
        'reset_token': initial_token,
    })


def dashboard_logout(request):
    logout(request)
    request.session.pop('selected_role', None)
    return redirect('dashboard:choose_role')


@login_required
def dashboard_home(request):
    if request.user.role != 'admin':
        return render(request, 'dashboard/home.html', {
            'total_resources': Resource.objects.count(),
            'buildings': Building.objects.all(),
            'my_bookings': Booking.objects.filter(requested_by=request.user).order_by('-created_at')[:5],
        })

    total_users = User.objects.count()
    total_students = User.objects.filter(role='student_leader').count()
    total_lecturers = User.objects.filter(role='lecturer').count()
    total_admins = User.objects.filter(role='admin').count()
    total_resources = Resource.objects.count()

    resources_by_type = Resource.objects.values('venue_type').annotate(
        count=Count('id')
    ).order_by('venue_type')

    resources_by_type_labels = [r['venue_type'] for r in resources_by_type]
    resources_by_type_data = [r['count'] for r in resources_by_type]

    recent_users = User.objects.order_by('-created_at')[:5]
    recent_resources = Resource.objects.order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_admins': total_admins,
        'total_resources': total_resources,
        'resources_by_type_labels': resources_by_type_labels,
        'resources_by_type_data': resources_by_type_data,
        'recent_users': recent_users,
        'recent_resources': recent_resources,
        'pending_booking_count': Booking.objects.filter(status='pending').count(),
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_users(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden('Admin access required.')
    users = User.objects.all().order_by('-created_at')
    role_filter = request.GET.get('role', '')
    search = request.GET.get('search', '')

    if role_filter:
        users = users.filter(role=role_filter)
    if search:
        users = users.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(student_number__icontains=search)
        )

    context = {
        'users': users,
        'role_groups': (
            ('Student Leaders', users.filter(role='student_leader')),
            ('Lecturers', users.filter(role='lecturer')),
            ('Administrators', users.filter(role='admin')),
        ),
        'role_filter': role_filter,
        'search': search,
    }
    return render(request, 'dashboard/users.html', context)


@login_required
def dashboard_users_edit(request, user_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Admin access required')
        return redirect('dashboard:users')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name', user.full_name)
        user.student_number = request.POST.get('student_number') or None
        user.role = request.POST.get('role', user.role)
        new_password = request.POST.get('password')

        if new_password:
            user.set_password(new_password)

        try:
            user.save()
            messages.success(request, 'User account updated successfully.')
            return redirect('dashboard:users')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')

    return render(request, 'dashboard/user_form.html', {'mode': 'edit', 'user': user})


@login_required
def dashboard_users_delete(request, user_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Admin access required')
        return redirect('dashboard:users')

    target_user = get_object_or_404(User, id=user_id)

    # Strictly prohibit admin self-deletion
    if request.user.id == target_user.id:
        messages.error(request, 'Security Policy: You are prohibited from deleting your own Administrator account.')
        return redirect('dashboard:users')

    # Also prohibit non-superusers from deleting other admins
    if target_user.role == 'admin' and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete an Administrator account.')
        return redirect('dashboard:users')

    if request.method == 'POST':
        target_user.delete()
        messages.success(request, f'User account ({target_user.email}) has been permanently deleted.')
        return redirect('dashboard:users')

    return render(request, 'dashboard/user_delete.html', {'user': target_user})


@login_required
def dashboard_resources(request):
    resources = Resource.objects.select_related('building').all().order_by('building', 'name')
    building_filter = request.GET.get('building', '')
    type_filter = request.GET.get('type', '')
    search = request.GET.get('search', '')

    if building_filter:
        resources = resources.filter(building_id=building_filter)
    if type_filter:
        resources = resources.filter(venue_type=type_filter)
    if search:
        resources = resources.filter(
            Q(name__icontains=search) |
            Q(room_number__icontains=search) |
            Q(building__name__icontains=search) |
            Q(description__icontains=search)
        )

    context = {
        'resources': resources,
        'buildings': Building.objects.all(),
        'selected_building': building_filter,
        'type_filter': type_filter,
        'search': search,
        'type_choices': Resource.TYPE_CHOICES,
    }
    return render(request, 'dashboard/resources.html', context)


@login_required
def dashboard_resources_create(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Only administrators can add SPU venues.')
        return redirect('dashboard:resources')

    if request.method == 'POST':
        name = request.POST.get('name')
        building_id = request.POST.get('building')
        room_number = request.POST.get('room_number', '')
        venue_type = request.POST.get('venue_type', 'Classroom')
        capacity = request.POST.get('capacity') or None
        description = request.POST.get('description', '')
        opening_time = request.POST.get('opening_time') or '06:00'
        closing_time = request.POST.get('closing_time') or '23:00'

        if not all([name, building_id]):
            messages.error(request, 'Venue name and building selection are required.')
        else:
            try:
                building = Building.objects.get(id=building_id)
                Resource.objects.create(
                    name=name,
                    building=building,
                    room_number=room_number,
                    venue_type=venue_type,
                    capacity=capacity if capacity else None,
                    description=description,
                    opening_time=opening_time,
                    closing_time=closing_time,
                )
                messages.success(request, 'SPU Venue created successfully.')
                return redirect('dashboard:resources')
            except Exception as e:
                messages.error(request, f'Error creating venue: {str(e)}')

    return render(request, 'dashboard/resource_form.html', {
        'mode': 'create',
        'buildings': Building.objects.all(),
        'type_choices': Resource.TYPE_CHOICES,
    })


@login_required
def dashboard_resources_edit(request, resource_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Only administrators can edit SPU venues.')
        return redirect('dashboard:resources')

    resource = get_object_or_404(Resource, id=resource_id)

    if request.method == 'POST':
        resource.name = request.POST.get('name', resource.name)
        building_id = request.POST.get('building')
        if building_id:
            resource.building = Building.objects.get(id=building_id)
        resource.room_number = request.POST.get('room_number', resource.room_number)
        resource.venue_type = request.POST.get('venue_type', resource.venue_type)
        capacity = request.POST.get('capacity')
        resource.capacity = capacity if capacity else None
        resource.description = request.POST.get('description', resource.description)
        resource.opening_time = request.POST.get('opening_time', resource.opening_time)
        resource.closing_time = request.POST.get('closing_time', resource.closing_time)

        try:
            resource.save()
            messages.success(request, 'SPU Venue updated successfully.')
            return redirect('dashboard:resources')
        except Exception as e:
            messages.error(request, f'Error updating venue: {str(e)}')

    return render(request, 'dashboard/resource_form.html', {
        'mode': 'edit',
        'resource': resource,
        'buildings': Building.objects.all(),
        'type_choices': Resource.TYPE_CHOICES,
    })


@login_required
def dashboard_resources_delete(request, resource_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Only administrators can delete SPU venues.')
        return redirect('dashboard:resources')

    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'SPU Venue deleted successfully.')
        return redirect('dashboard:resources')

    return render(request, 'dashboard/resource_delete.html', {'resource': resource})


@login_required
def venue_availability_api(request, resource_id):
    """
    Real-time JSON endpoint returning booked intervals and availability for a given venue and date.
    """
    resource = get_object_or_404(Resource, id=resource_id)
    date_str = request.GET.get('date', '')
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)
    
    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format (YYYY-MM-DD)'}, status=400)

    # Live availability panel: only show APPROVED (confirmed) bookings as occupied slots
    approved_bookings = Booking.objects.filter(
        resource=resource,
        booking_date=query_date,
        status='approved'
    ).order_by('start_time')

    booked_slots = [
        {
            'id': b.id,
            'start_time': b.start_time.strftime('%H:%M'),
            'end_time': b.end_time.strftime('%H:%M'),
            'status': b.status,
            'purpose': b.purpose,
            'requested_by': b.requested_by.full_name if (request.user.role == 'admin' or b.requested_by == request.user) else 'Reserved',
        }
        for b in approved_bookings
    ]


    return JsonResponse({
        'resource_id': resource.id,
        'resource_name': resource.name,
        'building': resource.building.name if resource.building else 'Campus',
        'date': date_str,
        'booked_slots': booked_slots,
        'total_booked': len(booked_slots),
    })


@login_required
def booking_create(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    if request.method == 'POST':
        booking_date = request.POST.get('booking_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        purpose = request.POST.get('purpose', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        if not all([booking_date, start_time, end_time, purpose, phone_number]):
            messages.error(request, 'All fields are required.')
        elif start_time >= end_time:
            messages.error(request, 'Invalid time range: The end time must be after the start time.')
        elif Booking.check_conflict(resource.id, booking_date, start_time, end_time):
            messages.error(request, 'Conflict detected: A confirmed reservation already exists for this venue and time slot.')
        else:
            booking = Booking.objects.create(
                resource=resource,
                requested_by=request.user,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                purpose=purpose,
                phone_number=phone_number,
                status='pending',
            )
            messages.success(
                request,
                f'Booking request #{booking.id} for {resource.name} submitted successfully! '
                'It is now in the review queue. Please check your booking list periodically for status updates.'
            )
            return redirect('dashboard:booking_reports')
    return render(request, 'dashboard/booking_form.html', {'resource': resource})


@login_required
def booking_detail(request, booking_id):
    """
    Search and retrieve specific details of a single booking by ID or reference.
    """
    booking = get_object_or_404(
        Booking.objects.select_related('resource', 'resource__building', 'requested_by'),
        id=booking_id
    )

    # Permission check: Admin can view any booking; normal users can only view their own
    if not (request.user.role == 'admin' or request.user.is_superuser or booking.requested_by == request.user):
        messages.error(request, 'Access Denied: You are not authorized to view this booking record.')
        return redirect('dashboard:booking_reports')

    return render(request, 'dashboard/booking_detail.html', {'booking': booking})


@login_required
def booking_requests(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden('Admin access required.')
    
    bookings = Booking.objects.select_related('resource', 'resource__building', 'requested_by').all().order_by('-created_at')
    
    # Specific search retrieval by Booking ID or search term
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')

    if search_query:
        if search_query.isdigit():
            bookings = bookings.filter(id=int(search_query))
        else:
            bookings = bookings.filter(
                Q(resource__name__icontains=search_query) |
                Q(requested_by__full_name__icontains=search_query) |
                Q(purpose__icontains=search_query)
            )

    if status_filter:
        bookings = bookings.filter(status=status_filter)

    return render(request, 'dashboard/booking_requests.html', {
        'bookings': bookings,
        'search_query': search_query,
        'status_filter': status_filter,
    })


@login_required
def booking_update_status(request, booking_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden('Admin access required.')
    if request.method != 'POST':
        return redirect('dashboard:booking_requests')
    booking = get_object_or_404(Booking, id=booking_id)
    status = request.POST.get('status')
    if status not in ('approved', 'declined', 'cancelled'):
        messages.error(request, 'Select a valid booking status decision.')
    else:
        if status == 'approved' and Booking.check_conflict(booking.resource_id, booking.booking_date, booking.start_time, booking.end_time, exclude_booking_id=booking.id):
            messages.error(request, 'Cannot approve: A conflicting booking is already approved for this time slot.')
        else:
            booking.status = status
            booking.save(update_fields=['status'])
            messages.success(request, f'Booking request #{booking.id} status updated to {booking.get_status_display()}.')
    return redirect('dashboard:booking_requests')


@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not (request.user.role == 'admin' or request.user.is_superuser or booking.requested_by == request.user):
        return HttpResponseForbidden('You can only cancel your own bookings.')

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
        messages.success(request, f'Reservation #{booking.id} for {booking.resource.name} cancelled.')
    return redirect('dashboard:booking_reports')


@login_required
def booking_reports(request):
    bookings = Booking.objects.filter(requested_by=request.user).select_related('resource', 'resource__building').order_by('-created_at')
    
    # Specific search retrieval by Booking ID or venue keyword
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')

    if search_query:
        if search_query.isdigit():
            bookings = bookings.filter(id=int(search_query))
        else:
            bookings = bookings.filter(
                Q(resource__name__icontains=search_query) |
                Q(purpose__icontains=search_query)
            )

    if status_filter:
        bookings = bookings.filter(status=status_filter)

    return render(request, 'dashboard/booking_reports.html', {
        'bookings': bookings,
        'search_query': search_query,
        'status_filter': status_filter,
    })

