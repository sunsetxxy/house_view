from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import SysUser

@admin.register(SysUser)
class SysUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    list_per_page = 20
    actions = ['activate_users', 'deactivate_users', 'set_as_staff', 'remove_staff_status']
    
    fieldsets = (
        ('基本信息', {'fields': ('username', 'email', 'password')}),
        ('权限设置', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'已成功激活 {queryset.count()} 个用户')
    activate_users.short_description = '激活选中用户'
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'已成功禁用 {queryset.count()} 个用户')
    deactivate_users.short_description = '禁用选中用户'
    
    def set_as_staff(self, request, queryset):
        queryset.update(is_staff=True)
        self.message_user(request, f'已将 {queryset.count()} 个用户设为管理员')
    set_as_staff.short_description = '设为管理员'
    
    def remove_staff_status(self, request, queryset):
        queryset.update(is_staff=False)
        self.message_user(request, f'已移除 {queryset.count()} 个用户的管理员权限')
    remove_staff_status.short_description = '移除管理员权限'
    
    def get_readonly_fields(self, request, obj=None):
        # 如果是编辑现有用户，将日期字段设为只读
        if obj:
            return ['date_joined', 'last_login']
        return []
