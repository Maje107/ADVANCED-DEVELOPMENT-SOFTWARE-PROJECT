import secrets
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserResponseSerializer,
    TokenResponseSerializer,
)


class HealthCheck(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'service': 'spu-auth-service',
            'status': 'ok',
            'university': 'Sol Plaatje University',
        })


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(
                    {
                        'message': 'Registration successful.',
                        'user': UserResponseSerializer(user).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                if 'unique' in str(e).lower() or 'Duplicate' in str(e):
                    return Response(
                        {'detail': 'Email or student number already registered.'},
                        status=status.HTTP_409_CONFLICT,
                    )
                return Response({'detail': f'Registration failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            data = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'token_type': 'bearer',
                'expires_in_minutes': int(access_token_lifetime.total_seconds() // 60),
                'user': UserResponseSerializer(user).data,
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserResponseSerializer(request.user).data)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = secrets.token_hex(16)
                user.reset_token = token
                user.save(update_fields=['reset_token'])
                return Response({
                    'message': 'Password reset token generated.',
                    'reset_token': token,
                    'note': 'In production, this token is sent via email or SMS. Use this token on the reset endpoint.',
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                # Return generic response for security
                return Response({
                    'message': 'If the email exists, a reset token has been issued.',
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            token = serializer.validated_data['reset_token']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(email=email, reset_token=token)
                user.set_password(new_password)
                user.reset_token = None
                user.save()
                return Response({'message': 'Password has been successfully updated.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'detail': 'Invalid email or reset token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

