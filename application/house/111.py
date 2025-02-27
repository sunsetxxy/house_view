import logging
from django_filters.rest_framework import FilterSet, filters
from django_filters import CharFilter, BooleanFilter, TypedChoiceFilter
from rest_framework import filters, generics, mixins, views, status
from rest_framework.decorators import action
from utils.rest_framework.viewsets import ModelViewSet
from utils.rest_framework.response import Response, BadResponse
from utils.pagination import PageNumberPagination
from project.models import Task, Project
from project.serializers.task import TaskSerializer
from user.models import User
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from srcfile.models import OssFile
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from project.models.project import ProjectLog
import json
from utils.wechat.minipush.push_by_api import WeChatMiniService
from datetime import timedelta, datetime
from project.models.stage import Stage
from django.db.models import Q
logger = logging.getLogger('django')


class TaskFilter(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='contains')
    owner_id = CharFilter(field_name='owner_id')
    STATUS_CHOICES = (
        (0, '未完成'),
        (1, '已完成'),
    )
    is_finished = TypedChoiceFilter(
        choices=STATUS_CHOICES,
        coerce=lambda x: bool(int(x)),  # 将 0 和 1 转为布尔值
        method='filter_status',
        label='完成状态'
    )

    def filter_status(self, queryset, name, value):
        """
        自定义过滤器，根据完成状态过滤
        value: True 表示已完成 (status='finish')，False 表示未完成 (status != 'finish')
        """
        if value:  # True: 过滤已完成任务
            return queryset.filter(status='finish')
        else:  # False: 过滤未完成任务
            return queryset.exclude(status='finish')


class TaskViewSet(ModelViewSet):
    """任务"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = PageNumberPagination
    filter_class = TaskFilter
    ordering_fields = ['id']

    def list(self, request, *args, **kwargs):
        # 获取请求用户
        user = request.user

        # 过滤出 owner 是当前用户的任务
        queryset = self.filter_queryset(self.get_queryset().filter(owner=user))

        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 返回数据
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        status = request.data.get('status')
        # 如果 'status' 不在合法选项中，设置为默认值 'init'
        if status not in dict(Task.STATUS_CHOICES):
            request.data['status'] = 'init'  # 设置默认值
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        owner_id = request.data.get('owner')
        if owner_id is None:
            return BadResponse({'负责人不能为空'})
        # 确保指定的 owner 存在
        if owner_id and not User.objects.filter(id=owner_id).exists():
            return BadResponse({'指定的负责人不存在'})

        serializer.validated_data['status'] = status
        serializer.validated_data['owner'] = User.objects.get(id=owner_id)
        attachment_ids = request.data.get('attachment_ids')
        if attachment_ids is not None:  # 如果附件数据存在，进行处理
            try:
                db_attachment_ids = OssFile.objects.filter(id__in=attachment_ids).values_list('id',
                                                                                              flat=True).distinct()
                if len(db_attachment_ids) != len(attachment_ids):  # 如果数据库中不包含这些附件，抛出异常
                    raise Exception(f'{attachment_ids}文件不存在')
                serializer.attachment_ids = attachment_ids  # 更新附件字段
            except Exception as e:
                return BadResponse("凭证附件不存在")

        content_attachment_ids = request.data.get('content_attachment_ids')
        if content_attachment_ids is not None:  # 如果附件数据存在，进行处理
            try:
                db_attachment_ids = OssFile.objects.filter(id__in=content_attachment_ids).values_list('id',
                                                                                                      flat=True).distinct()
                if len(db_attachment_ids) != len(content_attachment_ids):  # 如果数据库中不包含这些附件，抛出异常
                    raise Exception(f'{content_attachment_ids}文件不存在')
                serializer.content_attachment_ids = content_attachment_ids  # 更新附件字段
            except Exception as e:
                return BadResponse("任务附件不存在")
        # 保存任务
        task = serializer.save()
        # 遇到没保存上的问题 再保存一遍发现解决
        if content_attachment_ids:
            task.content_attachment_ids = content_attachment_ids
            task.save()
        return Response(self.get_serializer(task).data)

    def update(self, request, *args, **kwargs):
        task = self.get_object()  # 获取待更新的任务对象
        # 使用序列化器进行部分更新
        serializer = self.get_serializer(task, data=request.data, partial=True)
        # 验证数据
        serializer.is_valid(raise_exception=True)
        # 进行保存
        stage = task.stage
        # 只有当任务的类型是 stage 且状态为已完成时，才检查并更新阶段状态
        owner = request.data.get('owner')
        if owner:
            try:
                # 查找对应的 User 实例并更新到 task 的 owner 字段
                task.owner = User.objects.get(id=owner)
            except User.DoesNotExist:
                return Response("新更新的用户未找到")

            # 更新其他字段并保存
        status = request.data.get('status')
        need_update_status = False
        if status and status == 'finish' and task.status != 'finish':
            need_update_status = True
        self.perform_update(serializer)

        attachment_ids = request.data.get('attachment_ids')
        if attachment_ids is not None:  # 如果附件数据存在，进行处理
            try:
                db_attachment_ids = OssFile.objects.filter(id__in=attachment_ids).values_list('id',
                                                                                              flat=True).distinct()
                if len(db_attachment_ids) != len(attachment_ids):  # 如果数据库中不包含这些附件，抛出异常
                    raise Exception(f'{attachment_ids}文件不存在')
                task.attachment_ids = attachment_ids  # 更新附件字段
                task = serializer.save()
            except Exception as e:
                return BadResponse("凭证附件不存在")

        if need_update_status:
            ProjectLog.objects.create(
                user=request.user,
                project=task.project,
                log=request.user.name + " 完成了" + task.title
            )
            if task.project.landlord and task.project.landlord.wechat_openid:
                WeChatMiniService.push_task_finish(task.project.name, task.title, task.project.landlord.wechat_openid)

        content_attachment_ids = request.data.get('content_attachment_ids')
        if content_attachment_ids is not None:  # 如果附件数据存在，进行处理
            try:
                db_attachment_ids = OssFile.objects.filter(id__in=content_attachment_ids).values_list('id',
                                                                                                      flat=True).distinct()
                if len(db_attachment_ids) != len(content_attachment_ids):  # 如果数据库中不包含这些附件，抛出异常
                    raise Exception(f'{content_attachment_ids}文件不存在')
                task.content_attachment_ids = content_attachment_ids  # 更新附件字段
                task = serializer.save()
            except Exception as e:
                return BadResponse("任务附件不存在")

        if task.ttype == 'stage' and need_update_status and stage:
            # 检查该阶段是否还有其他未完成的任务
            remaining_tasks = Task.objects.filter(stage=stage, ttype='stage', status__in=['init', 'doing'])
            if not remaining_tasks.exists():
                # 如果该阶段没有其他未完成的任务，更新该阶段的状态为完成
                stage.status = 'finish'
                stage.actual_end_date = request.data.get('end_time')
                stage.save()
                # 增加延期逻辑
                # 如果延期
                actual_end_date = datetime.strptime(stage.actual_end_date, '%Y-%m-%d').date()
                if stage.actual_end_date and actual_end_date > stage.end_time:
                    # 延期天数
                    delay_days = (actual_end_date - stage.end_time).days
                    # 查询同一项目下 order 大于当前阶段的所有阶段

                    subsequent_stages = Stage.objects.filter(
                        project=stage.project
                    ).filter(
                        (Q(order__gt=stage.order) | Q(order=0)) & ~Q(id=stage.id)
                    )

                    # 顺延所有相关阶段的开始和结束时间
                    for subsequent_stage in subsequent_stages:
                        if subsequent_stage.begin_time:
                            subsequent_stage.begin_time += timedelta(days=delay_days)
                        if subsequent_stage.end_time:
                            subsequent_stage.end_time += timedelta(days=delay_days)
                        subsequent_stage.save()

            stages = task.project.stage_set.filter(status__in=['init', 'doing']).order_by('begin_time')
            if not stages:
                print(f"项目完工:{task}")
                task.project.status = 'finish'
                task.project.save()
                task.project.contract_bill.project_status = 'finish'
                task.project.contract_bill.save()

        # 返回更新后的数据
        return Response(serializer.data)



    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法
        """
        task = self.get_object()
        stages = task.project.stage_set.filter(status__in=['init', 'doing']).order_by('begin_time')
        if not stages:
            print(f"项目完工:{task}")
            task.project.status = 'finish'
            task.project.save()
            task.project.contract_bill.project_status = 'finish'
            task.project.contract_bill.save()

        task.is_deleted = True
        task.save()
        # 自定义返回响应
        return Response({"detail": "删除成功"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='tasks-by-stage')
    def list_by_stage(self, request):
        stage = request.query_params.get('stage')
        project_id = request.query_params.get('project_id')
        title_filter = request.query_params.get('title')  # 获取标题搜索关键字
        status_filter = request.query_params.get('status')
        owner_filter = request.query_params.get('owner')
        if not stage:
            return BadResponse({'缺少阶段参数'})
        tasks_stage = Task.objects.filter(stage=stage, project_id=project_id, ttype='stage')
        # tasks_other = Task.objects.filter(ttype='other', project_id=project_id)
        tasks_other = Task.objects.filter(ttype='other', project_id=project_id).exclude(stage=stage, status='completed')
        if title_filter:
            tasks_stage = tasks_stage.filter(title__icontains=title_filter)
            tasks_other = tasks_other.filter(title__icontains=title_filter)
        if status_filter:
            if status_filter == 'finish':  # 已完成
                tasks_stage = tasks_stage.filter(status='finish')
                tasks_other = tasks_other.filter(status='finish')
            elif status_filter == 'pending':  # 未完成
                tasks_stage = tasks_stage.exclude(status='finish')
                tasks_other = tasks_other.exclude(status='finish')
        if owner_filter:
            owner_user = User.objects.filter(
                mobile=Project.objects.filter(id=project_id).first().landlord_phone).first()
            if owner_filter == 'landlord':  # 已完成
                tasks_stage = tasks_stage.filter(owner=owner_user)
                tasks_other = tasks_other.filter(owner=owner_user)
            elif owner_filter == 'project':
                tasks_stage = tasks_stage.exclude(owner=owner_user)
                tasks_other = tasks_other.exclude(owner=owner_user)
        user_tasks = Task.objects.filter(owner=request.user)
        if project_id:
            user_tasks = user_tasks.filter(project_id=project_id)
        if stage:
            user_tasks = user_tasks.filter(stage=stage)

        response_data = {
            'tasks': self.get_serializer(tasks_stage, many=True).data,
            'tasks_other': self.get_serializer(tasks_other, many=True).data,
            'user_tasks': self.get_serializer(user_tasks, many=True).data,
        }

        return Response(response_data)

    @action(detail=False, methods=['get'])
    def by_project(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'message': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        stages = self.queryset.filter(project_id=project_id)
        serializer = self.get_serializer(stages, many=True)
        return Response(serializer.data)
