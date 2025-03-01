from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserLoginSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from .utils import send_verification_email, send_reset_password_email
import uuid





class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Генерация JWT-токенов
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )






class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи

    def get(self, request):
        """Получить данные текущего пользователя"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Редактирование данных пользователя"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Удаление аккаунта"""
        request.user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)




class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_verified = False
            user.verification_token = str(uuid.uuid4())  # Генерируем токен
            user.save()
            send_verification_email(user.email, user.verification_token)  # Отправляем email
            return Response({"message": "На вашу почту отправлено письмо для подтверждения."})
        return Response(serializer.errors, status=400)



class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            user.is_verified = True
            user.verification_token = None
            user.save()
            return Response({"message": "Email подтвержден!"})
        except User.DoesNotExist:
            return Response({"error": "Неверный токен"}, status=400)



class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            user.reset_token = str(uuid.uuid4())
            user.save()
            send_reset_password_email(user.email, user.reset_token)
            return Response({"message": "На почту отправлено письмо с инструкцией по сбросу пароля."})
        except User.DoesNotExist:
            return Response({"error": "Пользователь с таким email не найден."}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6)


class ResetPasswordView(APIView):
    def post(self, request, token):
        try:
            user = User.objects.get(reset_token=token)
        except User.DoesNotExist:
            return Response({"error": "Неверный или устаревший токен."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.reset_token = None
            user.save()
            return Response({"message": "Пароль успешно изменен."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)