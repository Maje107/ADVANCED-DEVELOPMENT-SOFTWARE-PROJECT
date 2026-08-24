from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('lecturer', 'Lecturer'),
        ('student_leader', 'Student Leader'),
    )
    LEADERSHIP_ROLE_CHOICES = (
        ('peer_mentor', 'Peer Mentor'),
        ('tutor', 'Tutor'),
        ('house_committee', 'House Committee'),
        ('sub_warden', 'Sub Warden'),
        ('wellness_warrior', 'Wellness Warrior'),
        ('society_leader', 'Society Leader'),
        ('src', 'SRC Representative'),
    )

    full_name = models.CharField(max_length=100)
    student_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student_leader')
    leadership_role = models.CharField(max_length=30, choices=LEADERSHIP_ROLE_CHOICES, blank=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} ({self.email}) - {self.get_role_display()}'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_lecturer(self):
        return self.role == 'lecturer'

    @property
    def is_student_leader(self):
        return self.role == 'student_leader'
