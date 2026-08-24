from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=[('lecturer', 'Lecturer'), ('student_leader', 'Student Leader')], default='student_leader')
    leadership_role = serializers.ChoiceField(choices=User.LEADERSHIP_ROLE_CHOICES, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('full_name', 'student_number', 'email', 'phone_number', 'role', 'leadership_role', 'password', 'password_confirm')
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        role = attrs.get('role', 'student_leader')
        if role not in ('lecturer', 'student_leader'):
            raise serializers.ValidationError({'role': 'Only Lecturer or Student Leader can self-register.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(
            full_name=validated_data['full_name'],
            student_number=validated_data.get('student_number') or None,
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'student_leader'),
            leadership_role=validated_data.get('leadership_role', ''),
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs


class UserResponseSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    leadership_role_display = serializers.CharField(source='get_leadership_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'full_name', 'student_number', 'email', 'phone_number', 'role', 'role_display', 'leadership_role', 'leadership_role_display', 'created_at')
        read_only_fields = fields


class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default='bearer')
    expires_in_minutes = serializers.IntegerField()
    user = UserResponseSerializer()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserResponseSerializer(self.user).data
        return data

