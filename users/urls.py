from django.urls import path
from .views import RegisterView, LoginAPIView, UserAPIView, VerifyEmailView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", UserAPIView.as_view(), name="user-profile"),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify-email"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/<str:token>/", ResetPasswordView.as_view(), name="reset-password"),
]
