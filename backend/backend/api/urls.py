from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('hello/', views.HelloWorld.as_view(), name='hello'),
    path('auth/wechat/login/', views.WeChatAuthorizationView.as_view(), name='wechat-login'),
    path('auth/wechat/callback/', views.WeChatAuthorizationCallbackView.as_view(), name='wechat-callback'),
]
