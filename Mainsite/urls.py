"""
URL configuration for Mainsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# -*- coding: utf-8 -*-
# 这是URL配置文件，用于定义网站的网址路由
# 就像一个地址簿，告诉Django当用户访问不同网址时应该调用哪个视图函数

from django.urls import path  # 导入path函数，用于定义URL路径
from django.conf import settings
from django.conf.urls.static import static
from . import views  # 从当前目录导入views模块，包含所有视图函数

# URL模式列表，定义了网址和对应视图函数的映射关系
urlpatterns = [
    # 主要功能页面路由
    path('', views.index, name='index'),  # 首页 - 显示项目介绍
    path('project/', views.project_management, name='project_management'),  # 项目管理页面
    path('text-gen/', views.text_generation, name='text_generation'),  # 文案生成页面
    path('image-gen/', views.image_generation, name='image_generation'),  # 图像生成页面
    path('audio-gen/', views.audio_generation, name='audio_generation'),  # 语音生成页面

    path('video-maker/', views.video_maker, name='video_maker'),  # 视频拼接页面
    path('auto-video/', views.auto_video, name='auto_video'),  # 自动生成视频页面
    path('system-config/', views.system_config, name='system_config'),  # 系统设置页面
    
    # API端点路由
    path('save_model_config/', views.save_model_config, name='save_model_config'),  # 保存模型配置API
    path('load_model_config/', views.load_model_config, name='load_model_config'),  # 加载模型配置API
    path('save_system_config/', views.save_system_config, name='save_system_config'),  # 保存系统配置API
    path('load_system_config/', views.load_system_config, name='load_system_config'),  # 加载系统配置API
    path('load_default_values/', views.load_default_values, name='load_default_values'),  # 加载默认值API
    path('load_workflow_list/', views.load_workflow_list, name='load_workflow_list'),  # 加载工作流列表API
    path('validate_workflow/', views.validate_workflow, name='validate_workflow'),  # 验证工作流文件API
    
    # 新增API管理相关路由
    path('load_api_list/', views.load_api_list, name='load_api_list'),  # 加载API列表API
    path('save_api_config/', views.save_api_config, name='save_api_config'),  # 保存API配置API
    path('activate_api/', views.activate_api, name='activate_api'),  # 激活API
    path('delete_api/', views.delete_api, name='delete_api'),  # 删除API配置API
    path('get_active_api/', views.get_active_api, name='get_active_api'),  # 获取当前激活的API
    path('create_project/', views.create_project, name='create_project'),
    path('get_current_project/', views.get_current_project, name='get_current_project'),
    path('get_project_title/', views.get_project_title, name='get_project_title'),
    path('clear_current_project/', views.clear_current_project, name='clear_current_project'),
    path('get_project_list/', views.get_project_list, name='get_project_list'),
    path('open_project/', views.open_project, name='open_project'),
    path('get_project_statistics/', views.get_project_statistics, name='get_project_statistics'),
    
    # 文案生成相关API路由
    path('load_paper_content/', views.load_paper_content, name='load_paper_content'),  # 加载paper.ini文件内容API
    path('generate_text/', views.generate_text, name='generate_text'),  # 第一句话生成相关API
    path('generate_first_sentence/', views.generate_first_sentence, name='generate_first_sentence'),
    path('save_first_sentence_prompt/', views.save_first_sentence_prompt, name='save_first_sentence_prompt'),
    path('load_first_sentence_prompt_list/', views.load_first_sentence_prompt_list, name='load_first_sentence_prompt_list'),
    path('load_first_sentence_prompt_content/', views.load_first_sentence_prompt_content, name='load_first_sentence_prompt_content'),
    path('delete_first_sentence_prompt/', views.delete_first_sentence_prompt, name='delete_first_sentence_prompt'),  # 保存第一句话PROMPT API
    path('load_default_first_sentence_prompt/', views.load_default_first_sentence_prompt, name='load_default_first_sentence_prompt'),  # 加载默认第一句话PROMPT API
    path('save_first_sentence_prompt_to_config/', views.save_first_sentence_prompt_to_config, name='save_first_sentence_prompt_to_config'),  # 保存第一句话PROMPT配置API
    
    # PROMPT管理相关API路由
    path('load_prompt_list/', views.load_prompt_list, name='load_prompt_list'),  # 加载PROMPT文件列表API
    path('load_prompt_content/', views.load_prompt_content, name='load_prompt_content'),  # 加载PROMPT文件内容API
    path('save_prompt/', views.save_prompt, name='save_prompt'),  # 保存PROMPT文件API
    path('delete_prompt/', views.delete_prompt, name='delete_prompt'),  # 删除PROMPT文件API
    path('save_prompt_to_config/', views.save_prompt_to_config, name='save_prompt_to_config'),  # 保存PROMPT配置API
    path('load_default_prompt/', views.load_default_prompt, name='load_default_prompt'),  # 加载默认PROMPT API
    
    # 格式化PROMPT管理相关API路由
    path('load_format_prompt_list/', views.load_format_prompt_list, name='load_format_prompt_list'),  # 加载格式化PROMPT文件列表API
    path('load_format_prompt_content/', views.load_format_prompt_content, name='load_format_prompt_content'),  # 加载格式化PROMPT文件内容API
    path('load_active_format_prompt_content/', views.load_active_format_prompt_content, name='load_active_format_prompt_content'),  # 从config.ini加载活动格式化PROMPT内容API
    path('save_format_prompt/', views.save_format_prompt, name='save_format_prompt'),  # 保存格式化PROMPT文件API
    path('delete_format_prompt/', views.delete_format_prompt, name='delete_format_prompt'),  # 删除格式化PROMPT文件API
    path('format_text/', views.format_text, name='format_text'),  # 格式化文案API
    path('format_text_from_ini/', views.format_text_from_ini, name='format_text_from_ini'),
    path('load_paper_json/', views.load_paper_json, name='load_paper_json'),  # 加载paper.json文件内容API
    path('load_paper_content_from_ini/', views.load_paper_content_from_ini, name='load_paper_content_from_ini'),
    path('load_formatted_content/', views.load_formatted_content, name='load_formatted_content'),  # 加载格式化文案内容API
    path('load_default_format_prompt/', views.load_default_format_prompt, name='load_default_format_prompt'),
    path('save_format_prompt_to_config/', views.save_format_prompt_to_config, name='save_format_prompt_to_config'),
    
    # 图像生成相关API路由
    path('load_project_paper/', views.load_project_paper, name='load_project_paper'),  # 加载项目paper.json文件API
    path('load_parameter_config/', views.load_parameter_config, name='load_parameter_config'),  # 加载项目parameter.ini文件API
    path('generate_image/', views.generate_image, name='generate_image'),  # 生成图像API
    path('api/save_theme/', views.save_theme, name='save_theme'),  # 保存主题API
    path('upload_image/', views.upload_image, name='upload_image'),  # 上传图像API
    path('clear_all_images/', views.clear_all_images, name='clear_all_images'),  # 清除所有图片API
    
    # 音频生成相关API路由
    path('generate_audio/', views.generate_audio, name='generate_audio'),  # 生成音频API
    path('clear_all_audios/', views.clear_all_audios, name='clear_all_audios'),  # 清除所有音频API
    path('list_project_audios/', views.list_project_audios, name='list_project_audios'),  # 列出项目音频文件API
    path('delete_audio_file/', views.delete_audio_file, name='delete_audio_file'),  # 删除音频文件API
    path('convert_ini_to_paper_json/', views.convert_ini_to_paper_json, name='convert_ini_to_paper_json'),  # 转换parameter.ini到paper.json API
    path('load_audio_pause_settings/', views.load_audio_pause_settings, name='load_audio_pause_settings'),  # 加载音频停顿设置API
    path('save_audio_pause_settings/', views.save_audio_pause_settings, name='save_audio_pause_settings'),  # 保存音频停顿设置API
    
    # 视频设置相关API路由
    path('save_video_settings/', views.save_video_settings, name='save_video_settings'),  # 保存视频设置API
    path('load_video_fade_settings/', views.load_video_fade_settings, name='load_video_fade_settings'),  # 加载淡入淡出设置API
    path('generate_video/', views.generate_video, name='generate_video'),  # 生成视频API
    
    # 自动生成视频相关API路由
    path('save_continuous_generation_settings/', views.save_continuous_generation_settings, name='save_continuous_generation_settings'),  # 保存连续生成设置API
    path('load_continuous_generation_settings/', views.load_continuous_generation_settings, name='load_continuous_generation_settings'),  # 加载连续生成设置API
    
    # Django日志相关API路由
    path('get_django_logs/', views.get_django_logs, name='get_django_logs'),  # 获取Django实时日志API
    path('add_custom_log/', views.add_custom_log, name='add_custom_log'),  # 添加自定义日志API
    
    # 视频历史相关API路由
    path('get_video_history/', views.get_video_history, name='get_video_history'),  # 获取视频生成历史API
    path('delete_video/', views.delete_video, name='delete_video'),  # 删除视频文件API
    path('clear_video_history/', views.clear_video_history, name='clear_video_history'),  # 清空视频历史API
    
    # 测试媒体文件路由
    path('test-media/<path:file_path>', views.test_media_file, name='test_media_file'),  # 测试媒体文件服务

]

# 在开发环境中提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
