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
        required=True
    )
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, help_text='名字')
    last_name = serializers.CharField(required=False, help_text='姓氏')
    is_staff = serializers.BooleanField(required=False, default=False, help_text='是否为管理员')
    is_active = serializers.BooleanField(required=False, default=True, help_text='是否激活账号')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'is_staff', 'is_active')

    def validate(self, attrs):
        password = attrs.get('password')
        
        # 检查两次密码是否一致
        if password != attrs.get('password2'):
            raise serializers.ValidationError({"password2": ["两次密码不一致"]})
        
        # 自定义密码验证逻辑：密码长度至少为6位
        if len(password) < 6:
            raise serializers.ValidationError({
                "password": ["密码长度不能少于6个字符。"]
            })
            
        # 移除了对is_staff的权限检查，允许任何用户设置管理员权限
            
        return attrs

    def create(self, validated_data):
        # 移除重复密码字段
        validated_data.pop('password2')
        # 创建用户并设置管理员权限
        user = User.objects.create_user(**validated_data)
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login']
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
    is_active = serializers.BooleanField(required=False, help_text='是否激活账号')
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'is_staff', 'is_active']
        
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        if 'is_staff' in validated_data:
            instance.is_staff = validated_data.pop('is_staff')
        if 'is_active' in validated_data:
            instance.is_active = validated_data.pop('is_active')
        return super().update(instance, validated_data)
        