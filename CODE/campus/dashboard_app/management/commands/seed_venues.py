from django.core.management.base import BaseCommand
from resources.models import Building, Resource, Booking
from users.models import User
from datetime import time

class Command(BaseCommand):
    help = 'Seed Sol Plaatje University (SPU) buildings and venues data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding SPU buildings and venues...'))

        buildings_data = [
            (1, 1, 'WP Building'),
            (2, 1, 'BA Building'),
            (3, 1, 'C Block'),
            (4, 1, 'T Block'),
            (5, 1, 'N Block (Sciences)'),
            (6, 1, 'Humanities Building'),
            (7, 1, 'Main Auditorium Complex'),
        ]

        building_objs = {}
        for b_id, campus_id, name in buildings_data:
            building, _ = Building.objects.update_or_create(
                id=b_id,
                defaults={'campus_id': campus_id, 'name': name}
            )
            building_objs[b_id] = building

        Booking.objects.all().delete()
        Resource.objects.all().delete()

        venues_data = [
            ('WP5 (Geo Lab)', 1, 'WP5', 'Laboratory', 30, 'Geography teaching laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('WP11', 1, 'WP11', 'Classroom', 30, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('WP12 (Consumer Lab)', 1, 'WP12', 'Laboratory', 24, 'Consumer science teaching lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('WP17', 1, 'WP17', 'Classroom', 48, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('WP20 (Bio/Bot/Zoo Lab)', 1, 'WP20', 'Laboratory', 30, 'Biology / Botany / Zoology lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('WP26 (Physical Science Lab)', 1, 'WP26', 'Laboratory', 30, 'Physical science teaching lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('WP30 (Technology Lab)', 1, 'WP30', 'Laboratory', 26, 'Technology practical lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),

            ('BA103', 2, 'BA103', 'Lecture Hall', 102, 'Lecture venue.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('BA111', 2, 'BA111', 'Classroom', 42, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('BA112', 2, 'BA112', 'Classroom', 42, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),

            ('Old Library (C230)', 3, 'C230', 'Lecture Hall', 120, 'Repurposed lecture venue.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('C012', 3, 'C012', 'Classroom', 56, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('C013', 3, 'C013', 'Classroom', 60, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('C014', 3, 'C014', 'Classroom', 40, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('C015 (Auditorium 111)', 3, 'C015', 'Auditorium', 144, 'Tiered auditorium venue.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('C016 (Auditorium 213)', 3, 'C016', 'Auditorium', 221, 'Tiered auditorium venue.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('C112 (Auditorium 111)', 3, 'C112', 'Auditorium', 95, 'Tiered auditorium venue.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('C113 (Auditorium 213)', 3, 'C113', 'Auditorium', 221, 'Tiered auditorium venue.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('C118', 3, 'C118', 'Classroom', 60, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),

            ('T004 (Auditorium A)', 4, 'T004', 'Auditorium', 70, 'Tiered auditorium venue.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T005 (Auditorium B)', 4, 'T005', 'Auditorium', 80, 'Tiered auditorium venue.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T022', 4, 'T022', 'Classroom', 95, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T023', 4, 'T023', 'Classroom', 75, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T125', 4, 'T125', 'Classroom', 102, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T126', 4, 'T126', 'Classroom', 68, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T204 (Teaching Lab)', 4, 'T204', 'Laboratory', 50, 'Micro-teaching practice lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T225 (Teaching Lab)', 4, 'T225', 'Laboratory', 50, 'Micro-teaching practice lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T226 (Teaching Lab)', 4, 'T226', 'Laboratory', 50, 'Micro-teaching practice lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T232', 4, 'T232', 'Classroom', 38, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T233 (Lab)', 4, 'T233', 'Laboratory', 48, 'Teaching laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T215 (Micro-Teach Lab)', 4, 'T215', 'Laboratory', 36, 'Micro-teaching practice lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T216', 4, 'T216', 'Classroom', 35, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T305 (Natural Sciences Lab)', 4, 'T305', 'Laboratory', 42, 'Natural sciences teaching lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('T310 (Maths Lab)', 4, 'T310', 'Laboratory', 55, 'Mathematics teaching lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Exam Hall', 4, 'EXAM', 'Event Venue', 300, 'Large venue used for exams and big lectures.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),

            ('N001 (Chemistry Lab)', 5, 'N001', 'Laboratory', 48, 'Chemistry practical laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N004 (Chemistry Lab)', 5, 'N004', 'Laboratory', 80, 'Chemistry practical laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N009 (Archaeology Dry Lab)', 5, 'N009', 'Laboratory', 64, 'Archaeology dry laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N101 (Museum Science Wet Lab)', 5, 'N101', 'Laboratory', 70, 'Museum science wet laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N104 (Physics Lab)', 5, 'N104', 'Laboratory', 77, 'Physics practical laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N106 (Physics Lab)', 5, 'N106', 'Laboratory', 48, 'Physics practical laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N118', 5, 'N118', 'Classroom', 84, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N201 (Geo GIS Lab)', 5, 'N201', 'Laboratory', 58, 'Geography GIS laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N204 (Bio/Bot/Zoo Lab)', 5, 'N204', 'Laboratory', 73, 'Biology / Botany / Zoology lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N205 (Bio/Bot/Zoo Lab)', 5, 'N205', 'Laboratory', 48, 'Biology / Botany / Zoology lab.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('N217', 5, 'N217', 'Classroom', 84, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),

            ('Auditorium 1 (Humanities)', 6, 'HUM-A1', 'Auditorium', 144, 'Tiered auditorium.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Auditorium 2 (Humanities)', 6, 'HUM-A2', 'Auditorium', 146, 'Tiered auditorium.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Auditorium 3 (Humanities)', 6, 'HUM-A3', 'Auditorium', 252, 'Tiered auditorium.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 1 (Humanities)', 6, 'HUM-C1', 'Classroom', 80, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 2 (Humanities)', 6, 'HUM-C2', 'Classroom', 40, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 3 (Humanities)', 6, 'HUM-C3', 'Classroom', 71, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 4 (Humanities)', 6, 'HUM-C4', 'Classroom', 66, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Tutorial Room 1 (Humanities)', 6, 'HUM-T1', 'Tutorial Room', 45, 'Small group tutorial room.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Tutorial Room 2 (Humanities)', 6, 'HUM-T2', 'Tutorial Room', 45, 'Small group tutorial room.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Tutorial Room 3 (Humanities)', 6, 'HUM-T3', 'Tutorial Room', 40, 'Small group tutorial room.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Museum Science Lab (Humanities)', 6, 'HUM-MSL', 'Laboratory', 30, 'Museum science laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),

            ('Auditorium 1 (001)', 7, '001', 'Auditorium', 320, 'Main campus large auditorium.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Auditorium 2 (006)', 7, '006', 'Auditorium', 320, 'Main campus large auditorium.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Auditorium 3 (C005)', 7, 'C005', 'Auditorium', 183, 'Main campus auditorium.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Lecture Hall 1 (003)', 7, '003', 'Lecture Hall', 160, 'Large lecture hall.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Lecture Hall 2 (004)', 7, '004', 'Lecture Hall', 160, 'Large lecture hall.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 1 (102)', 7, '102', 'Classroom', 80, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 2 (103)', 7, '103', 'Classroom', 80, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 3 (104)', 7, '104', 'Classroom', 80, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 4 (105)', 7, '105', 'Classroom', 80, 'General-purpose classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 1 (313)', 7, '313', 'Classroom', 30, 'Small classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Classroom 2 (314)', 7, '314', 'Classroom', 30, 'Small classroom.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Computer Lab 1', 7, 'CL1', 'Computer Lab', 60, 'General computer laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Computer Lab 2', 7, 'CL2', 'Computer Lab', 60, 'General computer laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Undergraduate GIS Lab (C011)', 7, 'C011-A', 'Computer Lab', 40, 'GIS computer laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Physical Geography Lab (C011)', 7, 'C011-B', 'Laboratory', 40, 'Physical geography laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Cartography Lab (C011)', 7, 'C011-C', 'Laboratory', 40, 'Cartography laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Soil Science Lab 1', 7, 'SSL1', 'Laboratory', 30, 'Soil science laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
            ('Soil Science Lab 2', 7, 'SSL2', 'Laboratory', 30, 'Soil science laboratory.', time(8, 0), time(17, 0), '22222222-2222-2222-2222-222222222222'),
        ]

        for name, b_id, room_num, v_type, cap, desc, op_time, cl_time, mgr_id in venues_data:
            Resource.objects.create(
                name=name,
                building=building_objs.get(b_id),
                room_number=room_num,
                venue_type=v_type,
                capacity=cap,
                description=desc,
                opening_time=op_time,
                closing_time=cl_time,
                manager_id=mgr_id
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(venues_data)} SPU venues.'))

        admin_user, _ = User.objects.get_or_create(
            email='admin@spu.ac.za',
            defaults={
                'full_name': 'SPU Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('AdminPass123!')
        admin_user.role = 'admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        lecturer_user, _ = User.objects.get_or_create(
            email='lecturer@spu.ac.za',
            defaults={
                'full_name': 'Dr. Thabo Khumalo',
                'role': 'lecturer',
                'phone_number': '+27821234567',
            }
        )
        lecturer_user.set_password('Lecturer123!')
        lecturer_user.role = 'lecturer'
        lecturer_user.save()

        leader_user, _ = User.objects.get_or_create(
            email='leader@spu.ac.za',
            defaults={
                'full_name': 'Kagiso Molefe',
                'student_number': '20230001',
                'role': 'student_leader',
                'leadership_role': 'peer_mentor',
                'phone_number': '+27839876543',
            }
        )
        leader_user.set_password('Student123!')
        leader_user.role = 'student_leader'
        leader_user.leadership_role = 'peer_mentor'
        leader_user.save()

        self.stdout.write(self.style.SUCCESS('Default accounts initialized.'))
