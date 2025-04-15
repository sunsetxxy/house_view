from django.shortcuts import render
from user.serializer import AuthSerializer, RegisterSerializer, UserSerializer, ChangePasswordSerializer,AdminUserUpdateSerializer
from user.models import SysUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.serializers import RefreshToken  # 引入Simple JWT的Token生成器
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi  # 添加这一行
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
# Create your views here.


class LoginView(GenericAPIView):

    serializer_class = AuthSerializer
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_description="登录")
    def post(self, request):
        username = request.data.get('username') 
        password = request.data.get('password')
        # 使用Django的authenticate验证用户密码（支持哈希验证）
        user = authenticate(username=username, password=password)
        if not username or not password:
            return Response({
            'code': '400',
            'info': '用户名和密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        if user is not None:
            # 生成双Token（Access + Refresh）
            refresh = RefreshToken.for_user(user)
            return Response({
                'code': '200',
                'info': '登录成功',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'is_staff': user.is_staff,
            }, status=status.HTTP_200_OK)
        else:
            return Response({'code': '401','info': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        

        
class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )

    @swagger_auto_schema(operation_description="注册")
    def post(self, request):
        # 使用序列化器验证输入数据
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': '400',
                'info': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查用户是否已存在
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        
        if SysUser.objects.filter(username=username).exists():
            return Response({
                'code': '409',
                'info': '用户名已被注册'
            }, status=status.HTTP_409_CONFLICT)

        if SysUser.objects.filter(email=email).exists():
            return Response({
                'code': '409',
                'info': '邮箱已被注册'
            }, status=status.HTTP_409_CONFLICT)

        # 创建用户（使用序列化器的save方法，自动处理is_staff字段）
        serializer.context['request'] = request  # 添加request到上下文，用于权限验证
        user = serializer.save()

        # 可选：生成并返回Token实现自动登录
        # refresh = RefreshToken.for_user(user)
        return Response({
            'code': '201',
            'info': '注册成功',
            # 'access': str(refresh.access_token),
            # 'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)


class UserList(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )

    @swagger_auto_schema(
        operation_description="获取用户列表或根据用户名查找用户",
        manual_parameters=[
            openapi.Parameter(
                'username', 
                openapi.IN_QUERY, 
                description="要查找的用户名(可选)", 
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def get(self, request):
        username = request.query_params.get('username')
        
        if username:
            # 如果提供了用户名参数，查找特定用户
            try:
                user = SysUser.objects.get(username=username)
                serializer = UserSerializer(user)
                return Response({
                    'code': 200,
                    'info': '查找成功',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            except SysUser.DoesNotExist:
                return Response({
                    'code': 404,
                    'info': '用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 获取所有用户数据
            users = SysUser.objects.all()
            count = users.count()  # 获取用户总数
            valueList = list(users.values())
            return JsonResponse({
                'code': '200',
                'info': '获取用户列表成功',
                'count': count,  # 添加用户总数
                'data': valueList
            }, status=status.HTTP_200_OK)
    
class UserInfo(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )

    def get(self, request):
        # 序列化当前用户数据
        serializer = UserSerializer(request.user)
        return Response({
            'code': 200,
            'info': '获取成功',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="修改密码",
        request_body=ChangePasswordSerializer
    )
    def put(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'info': '密码修改成功'
            })
        return Response({
            'code': 400,
            'info': '修改失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="修改个人信息",
        request_body=UserSerializer
    )
    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'info': '个人信息修改成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'info': '修改失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



        
# from rest_framework.permissions import IsAdminUser

class AdminUserUpdate(APIView):
    authentication_classes = (
        SessionAuthentication,
        JWTAuthentication
    )
    # permission_classes = [IsAdminUser]  # 只允许管理员访问

    @swagger_auto_schema(
        operation_description="管理员修改用户信息",
        request_body=AdminUserUpdateSerializer,
        responses={
            200: openapi.Response('用户信息修改成功'),
            400: openapi.Response('参数错误'),
            401: openapi.Response('未认证'),
            403: openapi.Response('权限不足'),
            404: openapi.Response('用户不存在'),
            500: openapi.Response('服务器内部错误'),
        }
    )
    def put(self, request, user_id):
        try:
            # 检查当前用户是否有管理员权限
            if not request.user.is_staff:
                return Response({
                    'code': 403,
                    'info': '权限不足，需要管理员权限'
                }, status=status.HTTP_403_FORBIDDEN)
                
            # 查找要修改的用户
            try:
                user = SysUser.objects.get(id=user_id)
            except SysUser.DoesNotExist:
                return Response({
                    'code': 404,
                    'info': '用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)

            # 验证并保存数据
            serializer = AdminUserUpdateSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}  # 添加请求上下文
            )
            
            if serializer.is_valid():
                # 保存修改
                updated_user = serializer.save()
                
                # 返回成功响应
                return Response({
                    'code': 200,
                    'info': '用户信息修改成功',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                # 返回验证错误
                return Response({
                    'code': 400,
                    'info': '修改失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            # 处理意外异常
            return Response({
                'code': 500,
                'info': f'服务器内部错误: {str(e)}',
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 