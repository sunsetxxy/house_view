"""
Jazzmin 配置文件
包含 Django Admin 界面的美化设置
"""

# Jazzmin 设置
JAZZMIN_SETTINGS = {
    # 标题
    "site_title": "房价查看系统",
    "site_header": "房价查看系统管理",
    "site_brand": "房价查看系统",
    "site_logo": None,  # 如果有 logo，可以在这里设置路径
    "login_logo": None,
    
    # 顶部导航栏颜色
    "navbar_color": "navbar-dark",
    "navbar_theme": "bg-primary",
    
    # 侧边栏设置
    "sidebar_fixed": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    
    # 控制面板设置
    "show_ui_builder": True,
    
    # 相关模型在下拉菜单中显示
    "related_modal_active": True,
    

    
    # 图标
    "icons": {
        "user.SysUser": "fas fa-user",
        "house.city": "fas fa-building",
        "house.city_id": "fas fa-city",
        "house.Area": "fas fa-map-marker",
        "house.Location": "fas fa-map-pin",
    },
    
    # 默认图标（当没有为模型指定图标时使用）
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",
}

# UI 主题设置
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}