from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, UserSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = authenticate(
            username=ser.validated_data["username"],
            password=ser.validated_data["password"],
        )
        if not user or not user.is_active:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        lifetime_hours = 24 if user.portal == "client" else 8
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
                "token_lifetime_hours": lifetime_hours,
            }
        )


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
