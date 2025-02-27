from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
class SysUser(AbstractUser):

    class Meta:
        db_table = 'sys_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        ordering = ['id']