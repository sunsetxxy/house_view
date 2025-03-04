ps -aux | grep python|xargs kill -9    # 注意如果有多个虚拟环境中运行着多个django服务需要使用端口
nohup python manage.py runserver 0.0.0.0:8000 >nohup.out 2>&1 &
