
from django.urls import path

from user.views import LoginView,RegisterView,UserList,UserInfo,AdminUserUpdate

from rest_framework import routers



urlpatterns= [
    path('login',LoginView.as_view(),name='login'), 
    path('register',RegisterView.as_view(),name='register'), 
    path('userlist',UserList.as_view(),name='userlist'), 
    path('userinfo',UserInfo.as_view(),name='userinfo'), 
    path('admininfo',AdminUserUpdate.as_view(),name='admininfo'), 
]