from requests import Response
from rest_framework.serializers import BaseSerializer, ModelSerializer, Serializer
from rest_framework import serializers
from rest_framework import fields
from user.models import SysUser
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class AuthSerializer(Serializer):

    username = fields.CharField(help_text='账号',required=True)
    password = fields.CharField(help_text='密码',required=True)

    class Meta:
        model=SysUser
        fields = ['username', 'password']



class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("两次密码不一致")
        return attrs

    def create(self, validated_data):
        # 移除重复密码字段
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']  # 设置只读字段
        # 排除敏感字段如 password, is_superuser 等

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='旧密码'
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='新密码',
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(
        write_only=True,
        required=True,
        help_text='确认新密码'
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError("新密码两次输入不一致")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

        
class AdminUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True)
    is_staff = serializers.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff']
        
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        if 'is_staff' in validated_data:
            instance.is_staff = validated_data.pop('is_staff')
        return super().update(instance, validated_data)
        