from django.contrib.auth import login
from django.urls import reverse

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from social_core.exceptions import AuthException
from social_django.utils import load_backend, load_strategy

from .models import User


class HelloWorld(APIView):
    def get(self, request):
        return Response({"message": "Hello, World!"})


class WeChatAuthorizationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        strategy = load_strategy(request)
        redirect_uri = request.build_absolute_uri(reverse('api:wechat-callback'))
        backend = load_backend(strategy=strategy, name='wechat', redirect_uri=redirect_uri)
        authorization_url = backend.auth_url()
        return Response({"authorization_url": authorization_url})


class WeChatAuthorizationCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        strategy = load_strategy(request)
        redirect_uri = request.build_absolute_uri(reverse('api:wechat-callback'))
        backend = load_backend(strategy=strategy, name='wechat', redirect_uri=redirect_uri)
        try:
            user = backend.complete(user=request.user if request.user.is_authenticated else None)
        except AuthException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(user, User):
            login(request, user)
            payload = {
                "id": user.id,
                "phone_number": user.phone_number,
                "name": user.name,
                "email": user.email,
                "gender": user.gender,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            }
            return Response(payload, status=status.HTTP_200_OK)

        return Response({"detail": "Unable to authenticate with WeChat."}, status=status.HTTP_400_BAD_REQUEST)
