# -*- coding: utf-8 -*-
# 这是Django视图文件，用于处理用户请求并返回响应
# 视图函数是连接URL和模板的桥梁，就像餐厅的服务员，接收客人的点餐需求并提供相应的服务

from django.shortcuts import render  # 导入render函数，用于渲染模板
from django.http import HttpResponse, JsonResponse  # 导入HttpResponse和JsonResponse类，用于返回HTTP响应
from django.views.decorators.csrf import csrf_exempt  # 导入csrf_exempt装饰器，用于免除CSRF验证
from django.views.decorators.http import require_http_methods  # 导入require_http_methods装饰器，用于限制HTTP方法
from django.conf import settings  # 导入Django设置
import json  # 导入json模块，用于处理JSON数据
import os  # 导入os模块，用于文件操作
import configparser  # 导入configparser模块，用于处理配置文件
import logging  # 导入logging模块，用于记录日志
from datetime import datetime  # 导入datetime模块，用于处理时间
try:
    from pypinyin import lazy_pinyin, Style  # 导入pypinyin模块，用于中文转拼音
except ImportError:
    lazy_pinyin = None  # 如果没有安装pypinyin，设置为None

# 获取logger实例
logger = logging.getLogger('Mainsite')

@csrf_exempt
def load_first_sentence_prompt_list(request):
    """加载第一句话PROMPT文件列表"""
    try:
        first_sentence_dir = os.path.join(settings.BASE_DIR, 'common', 'first_sentence')
        
        # 确保目录存在
        if not os.path.exists(first_sentence_dir):
            os.makedirs(first_sentence_dir)
            return JsonResponse({'success': True, 'prompts': []})
        
        prompts = []
        for filename in os.listdir(first_sentence_dir):
            if filename.endswith('.txt'):
                name = filename[:-4]  # 去掉.txt后缀
                prompts.append({
                    'filename': filename,
                    'name': name
                })
        
        # 按文件名排序
        prompts.sort(key=lambda x: x['name'])
        
        return JsonResponse({'success': True, 'prompts': prompts})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def load_first_sentence_prompt_content(request):
    """加载指定第一句话PROMPT文件内容"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '请求方法错误'})
    
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '')
        
        if not filename:
            return JsonResponse({'success': False, 'error': '文件名不能为空'})
        
        first_sentence_dir = os.path.join(settings.BASE_DIR, 'common', 'first_sentence')
        file_path = os.path.join(first_sentence_dir, filename)
        
        if not os.path.exists(file_path):
            return JsonResponse({'success': False, 'error': '文件不存在'})
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return JsonResponse({'success': True, 'content': content})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def delete_first_sentence_prompt(request):
    """删除第一句话PROMPT文件"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '请求方法错误'})
    
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '')
        
        if not filename:
            return JsonResponse({'success': False, 'error': '文件名不能为空'})
        
        first_sentence_dir = os.path.join(settings.BASE_DIR, 'common', 'first_sentence')
        file_path = os.path.join(first_sentence_dir, filename)
        
        if not os.path.exists(file_path):
            return JsonResponse({'success': False, 'error': '文件不存在'})
        
        os.remove(file_path)
        
        return JsonResponse({'success': True, 'message': f'第一句话PROMPT "{filename}" 已删除'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["GET"])
def load_default_first_sentence_prompt(request):
    """
    加载默认第一句话PROMPT的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含默认第一句话PROMPT内容的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 默认第一句话PROMPT文件路径
        default_first_sentence_prompt_path = None
        
        # 尝试从配置文件读取第一句话PROMPT路径
        if os.path.exists(config_path):
            config = configparser.ConfigParser(interpolation=None)
            config.read(config_path, encoding='utf-8')
            
            # 检查是否有FIRST_SENTENCE_PROMPT_CONFIG节
            if config.has_section('FIRST_SENTENCE_PROMPT_CONFIG'):
                if config.has_option('FIRST_SENTENCE_PROMPT_CONFIG', 'active_first_sentence_prompt_file'):
                    active_first_sentence_prompt_file = config.get('FIRST_SENTENCE_PROMPT_CONFIG', 'active_first_sentence_prompt_file').strip()
                    if active_first_sentence_prompt_file:  # 如果active_first_sentence_prompt_file不为空
                        default_first_sentence_prompt_path = os.path.join(project_root, 'common', 'first_sentence', active_first_sentence_prompt_file)
        
        # 如果配置文件中没有指定，使用默认文件
        if not default_first_sentence_prompt_path:
            # 尝试找到第一个第一句话PROMPT文件
            first_sentence_prompt_dir = os.path.join(project_root, 'common', 'first_sentence')
            if os.path.exists(first_sentence_prompt_dir):
                first_sentence_prompt_files = [f for f in os.listdir(first_sentence_prompt_dir) if f.endswith('.txt')]
                if first_sentence_prompt_files:
                    default_first_sentence_prompt_path = os.path.join(first_sentence_prompt_dir, first_sentence_prompt_files[0])
        
        # 如果找到了默认文件，读取内容
        if default_first_sentence_prompt_path and os.path.exists(default_first_sentence_prompt_path):
            with open(default_first_sentence_prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取文件名（不包含路径）
            filename = os.path.basename(default_first_sentence_prompt_path)
            
            logger.info(f'已加载默认第一句话PROMPT: {default_first_sentence_prompt_path}')
            
            return JsonResponse({
                'success': True,
                'content': content,
                'filename': filename
            })
        else:
            return JsonResponse({
                'success': True,
                'content': ''
            })
        
    except Exception as e:
        logger.error(f'加载默认第一句话PROMPT时发生错误: {str(e)}')
        return JsonResponse({
             'success': False,
             'error': f'加载默认第一句话PROMPT时发生错误: {str(e)}'
         })

@csrf_exempt
@require_http_methods(["POST"])
def save_first_sentence_prompt_to_config(request):
    """
    保存第一句话PROMPT文件名到config.ini的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename参数
        
    返回:
        JsonResponse: 保存结果的JSON响应
    """
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '').strip()
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '文件名不能为空'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 读取或创建配置文件
        config = configparser.ConfigParser(interpolation=None)
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        # 确保FIRST_SENTENCE_PROMPT_CONFIG节存在
        if not config.has_section('FIRST_SENTENCE_PROMPT_CONFIG'):
            config.add_section('FIRST_SENTENCE_PROMPT_CONFIG')
        
        # 设置active_first_sentence_prompt_file
        config.set('FIRST_SENTENCE_PROMPT_CONFIG', 'active_first_sentence_prompt_file', filename)
        
        # 保存配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
        logger.info(f'已保存第一句话PROMPT文件名到config.ini: {filename}')
        
        return JsonResponse({
            'success': True,
            'message': f'已保存第一句话PROMPT配置: {filename}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f'保存第一句话PROMPT配置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存配置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_theme(request):
    try:
        data = json.loads(request.body)
        project_path = data.get('project_path')
        theme = data.get('theme')

        if not project_path or not theme:
            return JsonResponse({'success': False, 'error': '缺少项目路径或主题信息'})

        parameter_file_path = os.path.join(project_path, 'parameter.ini')
        config = configparser.ConfigParser(interpolation=None)

        if os.path.exists(parameter_file_path):
            config.read(parameter_file_path, encoding='utf-8')
        
        if not config.has_section('PAPER_INFO'):
            config.add_section('PAPER_INFO')
            
        config.set('PAPER_INFO', 'theme', theme)

        with open(parameter_file_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)

        return JsonResponse({'success': True, 'message': '主题已成功保存'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def index(request):
    """
    首页视图函数 - 显示项目介绍和概览
    
    参数:
        request: Django的HttpRequest对象，包含用户请求的所有信息
        
    返回:
        渲染后的index.html模板，包含README.md的内容
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        readme_path = os.path.join(project_root, 'README.md')
        
        # 读取README.md文件内容
        readme_content = ''
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        else:
            readme_content = '# README.md文件不存在\n\n请在项目根目录创建README.md文件。'
        
        # 传递README内容到模板
        context = {
            'readme_content': readme_content
        }
        
        return render(request, 'index.html', context)
        
    except Exception as e:
        logger.error(f'读取README.md文件时发生错误: {str(e)}')
        # 如果出错，返回错误信息
        context = {
            'readme_content': f'# 读取README.md时发生错误\n\n错误信息: {str(e)}'
        }
        return render(request, 'index.html', context)

def project_management(request):
    """
    项目管理页面视图函数 - 创建和管理视频项目
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        渲染后的project.html模板
    """
    return render(request, 'project.html')

def text_generation(request):
    """
    文案生成页面视图函数 - 使用DeepSeek生成视频文案
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        渲染后的text_gen.html模板
    """
    return render(request, 'text_gen.html')

def image_generation(request):
    """
    图像生成页面视图函数 - 使用ComfyUI+FLUX.1生成图像
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        渲染后的image_gen.html模板
    """
    return render(request, 'image_gen.html')

def audio_generation(request):
    """
    语音生成页面视图函数 - 使用ComfyUI+CosyVoice生成语音
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        渲染后的audio_gen.html模板
    """
    return render(request, 'audio_gen.html')



def video_maker(request):
    """
    视频拼接页面视图函数 - 使用MoviePy生成最终视频
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        渲染后的video_maker.html模板
    """
    try:
        # 获取当前项目信息
        current_project = load_current_project_from_config()
        
        # 初始化项目数据
        project_data = {
            'has_project': False,
            'project_name': '',
            'text_data': {
                'sentence_count': 0,
                'title': '暂无文案',
                'generated_time': '未生成'
            },
            'image_data': {
                'count': 0,
                'format': 'PNG'
            },
            'audio_data': {
                'count': 0,
                'format': 'WAV',
                'total_duration': 0
            }
        }
        
        if current_project and current_project.get('project_path'):
            project_path = current_project['project_path']
            project_data['has_project'] = True
            project_data['project_name'] = current_project.get('project_name', '')
            
            # 读取parameter.ini文件
            parameter_file_path = os.path.join(project_path, 'parameter.ini')
            if os.path.exists(parameter_file_path):
                config = configparser.ConfigParser(interpolation=None)
                config.read(parameter_file_path, encoding='utf-8')
                
                # 读取文案信息
                if config.has_section('PAPER_INFO'):
                    project_data['text_data']['sentence_count'] = config.getint('PAPER_INFO', 'sentence_count', fallback=0)
                    project_data['text_data']['title'] = config.get('PAPER_INFO', 'title', fallback='暂无标题')
                    project_data['text_data']['generated_time'] = config.get('PAPER_INFO', 'generated_time', fallback='未生成')
                
                # 计算音频总时长
                if config.has_section('AUDIO_INFO'):
                    total_duration = 0
                    for key, value in config.items('AUDIO_INFO'):
                        if key.endswith('_duration'):
                            try:
                                total_duration += float(value)
                            except ValueError:
                                pass
                    project_data['audio_data']['total_duration'] = round(total_duration, 1)
            
            # 统计图像文件
            images_path = os.path.join(project_path, 'images')
            if os.path.exists(images_path):
                png_files = [f for f in os.listdir(images_path) if f.endswith('.png')]
                project_data['image_data']['count'] = len(png_files)
            
            # 统计音频文件
            audios_path = os.path.join(project_path, 'audios')
            if os.path.exists(audios_path):
                # 支持多种音频格式
                audio_extensions = ('.flac', '.wav', '.mp3', '.m4a', '.aac', '.ogg')
                audio_files = [f for f in os.listdir(audios_path) if f.lower().endswith(audio_extensions)]
                project_data['audio_data']['count'] = len(audio_files)
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 读取可用字体文件
        fonts_path = os.path.join(project_root, 'common', 'Fonts')
        available_fonts = []
        if os.path.exists(fonts_path):
            for font_file in os.listdir(fonts_path):
                if font_file.endswith(('.ttf', '.otf')):
                    font_name = os.path.splitext(font_file)[0]
                    available_fonts.append({
                        'filename': font_file,
                        'name': font_name,
                        'path': os.path.join(fonts_path, font_file)
                    })
        
        # 读取可用背景音乐文件
        music_path = os.path.join(project_root, 'common', 'back_mus')
        available_music = []
        if os.path.exists(music_path):
            for music_file in os.listdir(music_path):
                if music_file.endswith(('.wav', '.mp3', '.m4a')):
                    music_name = os.path.splitext(music_file)[0]
                    available_music.append({
                        'filename': music_file,
                        'name': music_name,
                        'path': os.path.join(music_path, music_file)
                    })
        
        # 读取当前项目的视频设置（如果存在）
        video_settings = {
            'subtitle': {
                'font': 'SourceHanSansCN-Regular.otf',
                'size': 24,
                'color': '#ffffff',
                'position': 'bottom-quarter',
                'horizontal_align': 'center',
                'stroke_width': 2,
                'stroke_color': '#000000',
                'shadow': True
            },
            'background_music': {
                'file': '',
                'volume': 10,
                'fade_in': 2,
                'fade_out': 2,
                'loop_mode': 'loop',
                'auto_adjust': True
            }
        }
        
        # 如果有当前项目，读取其视频设置
        if current_project and current_project.get('project_path'):
            parameter_file_path = os.path.join(current_project['project_path'], 'parameter.ini')
            if os.path.exists(parameter_file_path):
                config = configparser.ConfigParser(interpolation=None)
                config.read(parameter_file_path, encoding='utf-8')
                
                # 读取字幕设置
                if config.has_section('VIDEO_SUBTITLE'):
                    video_settings['subtitle']['font'] = config.get('VIDEO_SUBTITLE', 'font', fallback=video_settings['subtitle']['font'])
                    video_settings['subtitle']['size'] = config.getint('VIDEO_SUBTITLE', 'size', fallback=video_settings['subtitle']['size'])
                    video_settings['subtitle']['color'] = config.get('VIDEO_SUBTITLE', 'color', fallback=video_settings['subtitle']['color'])
                    video_settings['subtitle']['position'] = config.get('VIDEO_SUBTITLE', 'position', fallback=video_settings['subtitle']['position'])
                    video_settings['subtitle']['horizontal_align'] = config.get('VIDEO_SUBTITLE', 'horizontal_align', fallback=video_settings['subtitle']['horizontal_align'])
                    video_settings['subtitle']['stroke_width'] = config.getint('VIDEO_SUBTITLE', 'stroke_width', fallback=video_settings['subtitle']['stroke_width'])
                    video_settings['subtitle']['stroke_color'] = config.get('VIDEO_SUBTITLE', 'stroke_color', fallback=video_settings['subtitle']['stroke_color'])
                    video_settings['subtitle']['shadow'] = config.getboolean('VIDEO_SUBTITLE', 'shadow', fallback=video_settings['subtitle']['shadow'])
                
                # 读取背景音乐设置
                if config.has_section('VIDEO_BACKGROUND_MUSIC'):
                    video_settings['background_music']['file'] = config.get('VIDEO_BACKGROUND_MUSIC', 'file', fallback=video_settings['background_music']['file'])
                    video_settings['background_music']['volume'] = config.getint('VIDEO_BACKGROUND_MUSIC', 'volume', fallback=video_settings['background_music']['volume'])
                    video_settings['background_music']['fade_in'] = config.getfloat('VIDEO_BACKGROUND_MUSIC', 'fade_in', fallback=video_settings['background_music']['fade_in'])
                    video_settings['background_music']['fade_out'] = config.getfloat('VIDEO_BACKGROUND_MUSIC', 'fade_out', fallback=video_settings['background_music']['fade_out'])
                    video_settings['background_music']['loop_mode'] = config.get('VIDEO_BACKGROUND_MUSIC', 'loop_mode', fallback=video_settings['background_music']['loop_mode'])
                    video_settings['background_music']['auto_adjust'] = config.getboolean('VIDEO_BACKGROUND_MUSIC', 'auto_adjust', fallback=video_settings['background_music']['auto_adjust'])
        
        context = {
            'project_data': project_data,
            'available_fonts': available_fonts,
            'available_music': available_music,
            'video_settings': video_settings
        }
        
        return render(request, 'video_maker.html', context)
        
    except Exception as e:
        logger.error(f'加载视频制作页面数据时发生错误: {str(e)}')
        # 如果出错，返回默认数据
        project_data = {
            'has_project': False,
            'project_name': '',
            'text_data': {'sentence_count': 0, 'title': '暂无文案', 'generated_time': '未生成'},
            'image_data': {'count': 0, 'format': 'PNG'},
            'audio_data': {'count': 0, 'format': 'WAV', 'total_duration': 0}
        }
        return render(request, 'video_maker.html', {'project_data': project_data})

@csrf_exempt
@require_http_methods(["POST"])
def save_video_settings(request):
    """
    保存视频设置到项目的parameter.ini文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含JSON格式的视频设置数据
        
    返回:
        JsonResponse: 包含操作结果的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        
        # 获取当前项目信息
        current_project = load_current_project_from_config()
        if not current_project or not current_project.get('project_path'):
            return JsonResponse({
                'success': False,
                'error': '没有当前打开的项目'
            })
        
        project_path = current_project['project_path']
        parameter_file_path = os.path.join(project_path, 'parameter.ini')
        
        # 创建或读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        
        # 如果文件存在，先读取现有配置
        if os.path.exists(parameter_file_path):
            config.read(parameter_file_path, encoding='utf-8')
        
        # 保存字幕设置
        subtitle_data = data.get('subtitle', {})
        if subtitle_data:
            if not config.has_section('VIDEO_SUBTITLE'):
                config.add_section('VIDEO_SUBTITLE')
            
            config.set('VIDEO_SUBTITLE', 'font', subtitle_data.get('font', 'SourceHanSansCN-Regular.otf'))
            config.set('VIDEO_SUBTITLE', 'size', str(subtitle_data.get('size', 24)))
            config.set('VIDEO_SUBTITLE', 'color', subtitle_data.get('color', '#ffffff'))
            config.set('VIDEO_SUBTITLE', 'position', subtitle_data.get('position', 'bottom-quarter'))
            config.set('VIDEO_SUBTITLE', 'horizontal_align', subtitle_data.get('horizontal_align', 'center'))
            config.set('VIDEO_SUBTITLE', 'stroke_width', str(subtitle_data.get('stroke_width', 2)))
            config.set('VIDEO_SUBTITLE', 'stroke_color', subtitle_data.get('stroke_color', '#000000'))
            config.set('VIDEO_SUBTITLE', 'shadow', str(subtitle_data.get('shadow', True)))
        
        # 保存背景音乐设置
        music_data = data.get('background_music', {})
        if music_data:
            if not config.has_section('VIDEO_BACKGROUND_MUSIC'):
                config.add_section('VIDEO_BACKGROUND_MUSIC')
            
            config.set('VIDEO_BACKGROUND_MUSIC', 'file', music_data.get('file', ''))
            config.set('VIDEO_BACKGROUND_MUSIC', 'volume', str(music_data.get('volume', 30)))
            config.set('VIDEO_BACKGROUND_MUSIC', 'fade_in', str(music_data.get('fade_in', 2)))
            config.set('VIDEO_BACKGROUND_MUSIC', 'fade_out', str(music_data.get('fade_out', 2)))
            config.set('VIDEO_BACKGROUND_MUSIC', 'loop_mode', music_data.get('loop_mode', 'loop'))
            config.set('VIDEO_BACKGROUND_MUSIC', 'auto_adjust', str(music_data.get('auto_adjust', True)))
        
        # 保存淡入淡出设置
        fade_data = data.get('fade', {})
        if fade_data:
            if not config.has_section('VIDEO_FADE'):
                config.add_section('VIDEO_FADE')
            
            config.set('VIDEO_FADE', 'fade_in_frames', str(fade_data.get('fade_in_frames', 4)))
            config.set('VIDEO_FADE', 'fade_out_frames', str(fade_data.get('fade_out_frames', 4)))
            config.set('VIDEO_FADE', 'video_fps', str(fade_data.get('video_fps', 25)))
        
        # 写入配置文件
        with open(parameter_file_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        # 记录日志
        logger.info(f'视频设置已保存到项目: {current_project.get("project_name", "未知项目")}')
        
        return JsonResponse({
            'success': True,
            'message': '视频设置已成功保存',
            'project_name': current_project.get('project_name', ''),
            'config_path': parameter_file_path
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'保存视频设置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存视频设置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def load_video_fade_settings(request):
    """
    从项目的parameter.ini文件加载淡入淡出设置的API端点
    
    参数:
        request: Django的HttpRequest对象，包含JSON格式的项目名称
        
    返回:
        JsonResponse: 包含淡入淡出设置的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        project_name = data.get('project_name')
        
        if not project_name:
            return JsonResponse({
                'success': False,
                'error': '缺少project_name参数'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        projects_dir = os.path.join(project_root, 'projects')
        project_path = os.path.join(projects_dir, project_name)
        
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建parameter.ini文件路径
        parameter_file_path = os.path.join(project_path, 'parameter.ini')
        
        # 从config.ini获取默认值
        config_path = os.path.join(project_root, 'config.ini')
        default_fade_in_frames = 4
        default_fade_out_frames = 4
        default_video_fps = 25
        
        if os.path.exists(config_path):
            config = configparser.ConfigParser(interpolation=None)
            config.read(config_path, encoding='utf-8')
            
            if config.has_section('VIDEO_FADE_CONFIG'):
                default_fade_in_frames = config.getint('VIDEO_FADE_CONFIG', 'default_fade_in_frames', fallback=4)
                default_fade_out_frames = config.getint('VIDEO_FADE_CONFIG', 'default_fade_out_frames', fallback=4)
                default_video_fps = config.getint('VIDEO_FADE_CONFIG', 'default_video_fps', fallback=25)
        
        # 读取项目的parameter.ini文件
        fade_in_frames = default_fade_in_frames
        fade_out_frames = default_fade_out_frames
        video_fps = default_video_fps
        
        if os.path.exists(parameter_file_path):
            parameter_config = configparser.ConfigParser(interpolation=None)
            parameter_config.read(parameter_file_path, encoding='utf-8')
            
            if parameter_config.has_section('VIDEO_FADE'):
                fade_in_frames = parameter_config.getint('VIDEO_FADE', 'fade_in_frames', fallback=default_fade_in_frames)
                fade_out_frames = parameter_config.getint('VIDEO_FADE', 'fade_out_frames', fallback=default_fade_out_frames)
                video_fps = parameter_config.getint('VIDEO_FADE', 'video_fps', fallback=default_video_fps)
        
        # 记录日志
        logger.info(f'加载淡入淡出设置: 淡入={fade_in_frames}帧, 淡出={fade_out_frames}帧, 帧率={video_fps}FPS')
        
        return JsonResponse({
            'success': True,
            'fade_in_frames': fade_in_frames,
            'fade_out_frames': fade_out_frames,
            'video_fps': video_fps
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'加载淡入淡出设置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载设置时发生错误: {str(e)}'
        })

def system_config(request):
    """
    系统设置页面视图函数 - 配置API密钥和系统参数
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        渲染后的system_config.html模板
    """
    return render(request, 'system_config.html')



@csrf_exempt
@require_http_methods(["POST"])
def save_model_config(request):
    """
    保存模型配置到config.ini文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含JSON格式的配置数据
        
    返回:
        JsonResponse: 包含操作结果的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        
        # 获取配置数据
        model = data.get('model', '')
        api_key = data.get('api_key', '')
        api_url = data.get('api_url', '')
        model_name = data.get('model_name', '')
        
        # 验证必要字段
        if not all([model, api_key, api_url]):
            return JsonResponse({
                'success': False,
                'error': '缺少必要的配置信息（模型、API密钥、API地址）'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 创建或读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        
        # 如果文件存在，先读取现有配置
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        # 确保存在MODEL_CONFIG节
        if not config.has_section('MODEL_CONFIG'):
            config.add_section('MODEL_CONFIG')
        
        # 设置配置值
        config.set('MODEL_CONFIG', 'selected_model', model)
        config.set('MODEL_CONFIG', 'api_key', api_key)
        config.set('MODEL_CONFIG', 'api_url', api_url)
        config.set('MODEL_CONFIG', 'model_name', model_name)
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        # 记录日志
        logger.info(f'模型配置已保存: 模型={model}, API地址={api_url}, 模型名称={model_name}')
        
        return JsonResponse({
            'success': True,
            'message': '模型配置已成功保存到config.ini文件',
            'config_path': config_path
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'保存模型配置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存配置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_parameter_config(request):
    """
    加载项目的parameter.ini文件内容的API端点
    
    参数:
        request: Django的HttpRequest对象，包含project_path参数
        
    返回:
        JsonResponse: 包含parameter.ini中sentence_count的JSON响应
    """
    try:
        project_path = request.GET.get('project_path', '').strip()
        
        if not project_path:
            # 如果没有提供项目路径，尝试从配置文件获取当前项目
            current_project = load_current_project_from_config()
            if current_project and current_project.get('path'):
                project_path = current_project['path']
            else:
                return JsonResponse({
                    'success': False,
                    'error': '未提供项目路径且没有当前打开的项目'
                })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建parameter.ini文件路径
        parameter_file_path = os.path.join(project_path, 'parameter.ini')
        
        if not os.path.exists(parameter_file_path):
            return JsonResponse({
                'success': False,
                'error': f'parameter.ini文件不存在: {parameter_file_path}'
            })
        
        # 读取parameter.ini文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(parameter_file_path, encoding='utf-8')
        
        sentence_count = 8  # 默认值
        # 按优先级检查不同的section
        if config.has_section('PAPER_INFO') and config.has_option('PAPER_INFO', 'sentence_count'):
            sentence_count = config.getint('PAPER_INFO', 'sentence_count')
        elif config.has_section('DEFAULT') and config.has_option('DEFAULT', 'sentence_count'):
            sentence_count = config.getint('DEFAULT', 'sentence_count')
        elif config.has_section('GENERATION') and config.has_option('GENERATION', 'sentence_count'):
            sentence_count = config.getint('GENERATION', 'sentence_count')
        
        # 读取文案内容
        paper_content = {}
        if config.has_section('PAPER_CONTENT'):
            for key, value in config.items('PAPER_CONTENT'):
                paper_content[key] = value
        
        return JsonResponse({
            'success': True,
            'sentence_count': sentence_count,
            'paper_content': paper_content
        })
        
    except Exception as e:
        logger.error(f'加载parameter.ini文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载parameter.ini文件时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_project_paper(request):
    """
    加载项目的paper.json文件内容的API端点
    
    参数:
        request: Django的HttpRequest对象，包含project_path参数
        
    返回:
        JsonResponse: 包含paper.json内容的JSON响应
    """
    try:
        project_path = request.GET.get('project_path', '').strip()
        
        if not project_path:
            # 如果没有提供项目路径，尝试从配置文件获取当前项目
            current_project = load_current_project_from_config()
            if current_project and current_project.get('path'):
                project_path = current_project['path']
            else:
                return JsonResponse({
                    'success': False,
                    'error': '未提供项目路径且没有当前打开的项目'
                })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建paper.json文件路径
        paper_file_path = os.path.join(project_path, 'paper.json')
        
        if not os.path.exists(paper_file_path):
            return JsonResponse({
                'success': False,
                'error': f'paper.json文件不存在: {paper_file_path}'
            })
        
        # 读取paper.json文件
        with open(paper_file_path, 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
        
        return JsonResponse({
            'success': True,
            'script': paper_data.get('script', []),
            'title': paper_data.get('title', ''),
            'character_profile': paper_data.get('character_profile', {}),
            'image_prompts': paper_data.get('image_prompts', {})
        })
        
    except json.JSONDecodeError as e:
        logger.error(f'解析paper.json文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'paper.json文件格式错误: {str(e)}'
        })
    except Exception as e:
        logger.error(f'加载paper.json文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载paper.json文件时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def generate_image(request):
    """
    生成单个图像的API端点
    
    参数:
        request: Django的HttpRequest对象，包含script_id、project_path和prompt等
        
    返回:
        JsonResponse: 包含生成结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        script_id = data.get('script_id')
        project_path = data.get('project_path', '').strip()
        prompt = data.get('prompt', 'masterpiece best quality')
        negative_prompt = data.get('negative_prompt', 'bad hands, blurry')
        width = data.get('width', 512)
        height = data.get('height', 512)
        steps = data.get('steps', 20)
        cfg = data.get('cfg', 8.0)
        seed = data.get('seed')
        
        if script_id is None:
            return JsonResponse({
                'success': False,
                'error': '缺少script_id参数'
            })
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        # 从系统配置中获取ComfyUI地址
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        comfyui_address = 'http://192.168.1.85:8188/'  # 默认地址
        if config.has_section('COMFYUI_CONFIG'):
            comfyui_address = config.get('COMFYUI_CONFIG', 'comfyui_address', fallback='http://192.168.1.85:8188/')
        
        # 移除协议前缀，因为ComfyUIClient需要的是host:port格式
        server_address = comfyui_address.replace('http://', '').replace('https://', '').rstrip('/')
        
        logger.info(f'开始生成图像: script_id={script_id}, project_path={project_path}, ComfyUI地址={server_address}')
        
        try:
            # 导入ComfyUI客户端
            import sys
            common_path = os.path.join(project_root, 'common')
            if common_path not in sys.path:
                sys.path.append(common_path)
            
            from comfyui_client import ComfyUIClient
            
            # 创建ComfyUI客户端
            client = ComfyUIClient(server_address)
            
            # 测试连接
            if not client.test_connection():
                return JsonResponse({
                    'success': False,
                    'error': f'无法连接到ComfyUI服务器: {comfyui_address}'
                })
            
            # 创建项目图像目录
            images_dir = os.path.join(project_path, 'images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            
            # 生成图像
            saved_files = client.generate_image(
                project_path=project_path,
                sentence_id=script_id,
                seed=seed
            )
            
            if saved_files:
                # ComfyUIClient已经直接保存到正确位置，无需复制
                final_filename = f'script_{script_id}.png'
                final_path = saved_files[0]  # 使用ComfyUIClient返回的路径
                
                # 生成媒体URL路径
                project_name = os.path.basename(project_path)
                image_url = f'/media/{project_name}/images/{final_filename}'
                
                logger.info(f'图像生成成功: script_id={script_id}, 文件路径={final_path}')
                
                return JsonResponse({
                    'success': True,
                    'image_url': image_url,
                    'message': f'图像生成成功 (script_id: {script_id})'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '图像生成失败，未返回任何图像文件'
                })
                
        except ImportError as e:
            logger.error(f'导入ComfyUI客户端失败: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': f'ComfyUI客户端模块导入失败: {str(e)}'
            })
        except Exception as e:
            logger.error(f'ComfyUI图像生成失败: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': f'图像生成失败: {str(e)}'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'生成图像时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'生成图像时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def generate_audio(request):
    """
    生成单个音频的API端点
    
    参数:
        request: Django的HttpRequest对象，包含script_id、project_path等
        
    返回:
        JsonResponse: 包含生成结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        script_id = data.get('script_id')
        project_path = data.get('project_path', '').strip()
        
        if script_id is None:
            return JsonResponse({
                'success': False,
                'error': '缺少script_id参数'
            })
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        # 从系统配置中获取ComfyUI地址
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        comfyui_address = 'http://192.168.1.85:8188/'  # 默认地址
        if config.has_section('COMFYUI_CONFIG'):
            comfyui_address = config.get('COMFYUI_CONFIG', 'comfyui_address', fallback='http://192.168.1.85:8188/')
        
        # 移除协议前缀，因为ComfyUIClient需要的是host:port格式
        server_address = comfyui_address.replace('http://', '').replace('https://', '').rstrip('/')
        
        logger.info(f'开始生成音频: script_id={script_id}, project_path={project_path}, ComfyUI地址={server_address}')
        
        try:
            # 导入ComfyUI客户端和音频处理器
            import sys
            common_path = os.path.join(project_root, 'common')
            if common_path not in sys.path:
                sys.path.append(common_path)
            
            from comfyui_client import ComfyUIClient
            from audio_processor import AudioProcessor
            
            # 创建ComfyUI客户端
            client = ComfyUIClient(server_address)
            
            # 测试连接
            if not client.test_connection():
                return JsonResponse({
                    'success': False,
                    'error': f'无法连接到ComfyUI服务器: {comfyui_address}'
                })
            
            # 创建项目音频目录
            audios_dir = os.path.join(project_path, 'audios')
            if not os.path.exists(audios_dir):
                os.makedirs(audios_dir)
            
            # 生成音频
            saved_files = client.generate_audio(
                project_path=project_path,
                sentence_id=script_id
            )
            
            if saved_files:
                # 找到音频文件（非工作流JSON文件）
                audio_files = [f for f in saved_files if not f.endswith('.json')]
                
                if audio_files:
                    audio_path = audio_files[0]
                    audio_filename = os.path.basename(audio_path)
                    
                    # 音频后处理：去除静音 + 更新parameter.ini
                    try:
                        audio_processor = AudioProcessor()
                        processed_path, duration = audio_processor.process_audio_after_generation(
                            audio_path, project_path, script_id
                        )
                        
                        logger.info(f'音频处理完成: script_id={script_id}, 原始文件={audio_path}, 处理后时长={duration:.2f}秒')
                        
                    except ImportError:
                        logger.warning('音频处理库未安装，跳过静音去除，仅计算时长')
                        # 如果音频处理库未安装，尝试使用基本方法计算时长
                        try:
                            import librosa
                            duration = librosa.get_duration(filename=audio_path)
                            
                            # 手动更新parameter.ini文件
                            parameter_file = os.path.join(project_path, 'parameter.ini')
                            if not os.path.exists(parameter_file):
                                with open(parameter_file, 'w', encoding='utf-8') as f:
                                    f.write("")
                            
                            param_config = configparser.ConfigParser(interpolation=None)
                            param_config.read(parameter_file, encoding='utf-8')
                            
                            if not param_config.has_section('AUDIO_INFO'):
                                param_config.add_section('AUDIO_INFO')
                            
                            param_config.set('AUDIO_INFO', f'script_{script_id}_duration', str(duration))
                            
                            with open(parameter_file, 'w', encoding='utf-8') as f:
                                param_config.write(f)
                            
                            logger.info(f'音频时长已写入parameter.ini: script_{script_id}_duration={duration:.2f}秒')
                            
                        except ImportError:
                            logger.warning('librosa库未安装，无法计算音频时长')
                            duration = 0.0
                        except Exception as e:
                            logger.error(f'计算音频时长失败: {e}')
                            duration = 0.0
                    
                    except Exception as e:
                        logger.error(f'音频后处理失败: {e}')
                        # 如果处理失败，至少尝试计算时长
                        try:
                            import librosa
                            duration = librosa.get_duration(filename=audio_path)
                        except:
                            duration = 0.0
                    
                    # 生成媒体URL路径
                    project_name = os.path.basename(project_path)
                    audio_url = f'/media/{project_name}/audios/{audio_filename}'
                    
                    logger.info(f'音频生成成功: script_id={script_id}, 文件路径={audio_path}')
                    
                    return JsonResponse({
                        'success': True,
                        'audio_url': audio_url,
                        'duration': duration,
                        'message': f'音频生成成功 (script_id: {script_id})'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '音频生成失败，未返回任何音频文件'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '音频生成失败，未返回任何文件'
                })
                
        except ImportError as e:
            logger.error(f'导入ComfyUI客户端失败: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': f'ComfyUI客户端模块导入失败: {str(e)}'
            })
        except Exception as e:
            logger.error(f'ComfyUI音频生成失败: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': f'音频生成失败: {str(e)}'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'生成音频时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'生成音频时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def clear_all_audios(request):
    """
    清除项目中所有音频文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含project_path
        
    返回:
        JsonResponse: 包含清除结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        project_path = data.get('project_path', '').strip()
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建音频目录路径
        audios_dir = os.path.join(project_path, 'audios')
        
        deleted_count = 0
        if os.path.exists(audios_dir):
            try:
                # 删除音频目录中的所有文件
                for filename in os.listdir(audios_dir):
                    file_path = os.path.join(audios_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f'已删除音频文件: {file_path}')
                
                logger.info(f'成功清除 {deleted_count} 个音频文件')
                
            except Exception as e:
                logger.error(f'删除音频文件时发生错误: {e}')
                return JsonResponse({
                    'success': False,
                    'error': f'删除音频文件失败: {str(e)}'
                })
        
        return JsonResponse({
            'success': True,
            'message': f'成功清除 {deleted_count} 个音频文件',
            'deleted_count': deleted_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'清除音频文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'清除音频文件时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def list_project_audios(request):
    """
    列出项目中所有音频文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含project_path参数
        
    返回:
        JsonResponse: 包含音频文件列表的JSON响应
    """
    try:
        project_path = request.GET.get('project_path', '').strip()
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建音频目录路径
        audios_dir = os.path.join(project_path, 'audios')
        
        if not os.path.exists(audios_dir):
            return JsonResponse({
                'success': True,
                'audios': [],
                'message': '音频目录不存在'
            })
        
        # 获取所有音频文件
        audio_extensions = ['.wav', '.mp3', '.m4a', '.aac', '.ogg', '.flac']
        audio_files = []
        
        try:
            for filename in os.listdir(audios_dir):
                file_path = os.path.join(audios_dir, filename)
                if os.path.isfile(file_path):
                    file_extension = os.path.splitext(filename)[1].lower()
                    if file_extension in audio_extensions:
                        # 获取文件信息
                        file_stat = os.stat(file_path)
                        audio_files.append({
                            'filename': filename,
                            'size': file_stat.st_size,
                            'modified_time': file_stat.st_mtime
                        })
            
            # 按修改时间排序（最新的在前）
            audio_files.sort(key=lambda x: x['modified_time'], reverse=True)
            
            logger.info(f'找到 {len(audio_files)} 个音频文件')
            
        except Exception as e:
            logger.error(f'读取音频目录时发生错误: {e}')
            return JsonResponse({
                'success': False,
                'error': f'读取音频目录失败: {str(e)}'
            })
        
        return JsonResponse({
            'success': True,
            'audios': audio_files,
            'count': len(audio_files)
        })
        
    except Exception as e:
        logger.error(f'列出音频文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'列出音频文件时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def delete_audio_file(request):
    """
    删除指定音频文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含project_path和filename参数
        
    返回:
        JsonResponse: 包含删除结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        project_path = data.get('project_path', '').strip()
        filename = data.get('filename', '').strip()
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '缺少filename参数'
            })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建音频文件路径
        audios_dir = os.path.join(project_path, 'audios')
        file_path = os.path.join(audios_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return JsonResponse({
                'success': False,
                'error': f'音频文件不存在: {filename}'
            })
        
        # 安全检查：确保文件在音频目录内
        if not os.path.abspath(file_path).startswith(os.path.abspath(audios_dir)):
            return JsonResponse({
                'success': False,
                'error': '无效的文件路径'
            })
        
        try:
            # 删除文件
            os.remove(file_path)
            logger.info(f'已删除音频文件: {file_path}')
            
        except Exception as e:
            logger.error(f'删除音频文件时发生错误: {e}')
            return JsonResponse({
                'success': False,
                'error': f'删除文件失败: {str(e)}'
            })
        
        return JsonResponse({
            'success': True,
            'message': f'成功删除音频文件: {filename}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'删除音频文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'删除音频文件时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def upload_image(request):
    """
    上传本地图像的API端点
    
    参数:
        request: Django的HttpRequest对象，包含图像文件、script_id和project_path
        
    返回:
        JsonResponse: 包含上传结果的JSON响应
    """
    try:
        script_id = request.POST.get('script_id')
        project_path = request.POST.get('project_path', '').strip()
        image_file = request.FILES.get('image')
        
        if script_id is None:
            return JsonResponse({
                'success': False,
                'error': '缺少script_id参数'
            })
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        if not image_file:
            return JsonResponse({
                'success': False,
                'error': '未提供图像文件'
            })
        
        # 检查文件类型
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        file_extension = os.path.splitext(image_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'不支持的文件类型: {file_extension}'
            })
        
        # 创建项目图像目录
        images_dir = os.path.join(project_path, 'images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        # 生成文件名
        filename = f'script_{script_id}{file_extension}'
        file_path = os.path.join(images_dir, filename)
        
        # 保存文件
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        logger.info(f'图像上传成功: script_id={script_id}, 文件路径={file_path}')
        
        # 生成媒体URL路径
        project_name = os.path.basename(project_path)
        image_url = f'/media/{project_name}/images/{filename}'
        
        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'message': f'图像上传成功 (script_id: {script_id})'
        })
        
    except Exception as e:
        logger.error(f'上传图像时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'上传图像时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def clear_all_images(request):
    """
    清除项目下所有图片的API端点
    
    参数:
        request: Django的HttpRequest对象，包含project_path
        
    返回:
        JsonResponse: 包含清除结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        project_path = data.get('project_path', '').strip()
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': '项目路径不存在'
            })
        
        # 构建images目录路径
        images_dir = os.path.join(project_path, 'images')
        
        if not os.path.exists(images_dir):
            return JsonResponse({
                'success': True,
                'message': 'images目录不存在，无需清除',
                'deleted_count': 0
            })
        
        # 获取所有图片文件和对应的JSON文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        deleted_files = []
        deleted_json_files = []
        
        try:
            for filename in os.listdir(images_dir):
                file_path = os.path.join(images_dir, filename)
                if os.path.isfile(file_path):
                    file_extension = os.path.splitext(filename)[1].lower()
                    if file_extension in image_extensions:
                        # 删除图片文件
                        os.remove(file_path)
                        deleted_files.append(filename)
                        logger.info(f'已删除图片文件: {file_path}')
                        
                        # 删除对应的JSON工作流文件
                        base_name = os.path.splitext(filename)[0]
                        json_filename = f'{base_name}.json'
                        json_file_path = os.path.join(images_dir, json_filename)
                        if os.path.exists(json_file_path):
                            os.remove(json_file_path)
                            deleted_json_files.append(json_filename)
                            logger.info(f'已删除工作流文件: {json_file_path}')
            
            logger.info(f'清除图片完成: 项目={project_path}, 删除图片文件数={len(deleted_files)}, 删除JSON文件数={len(deleted_json_files)}')
            
            return JsonResponse({
                'success': True,
                'message': f'成功清除 {len(deleted_files)} 个图片文件和 {len(deleted_json_files)} 个工作流文件',
                'deleted_count': len(deleted_files),
                'deleted_files': deleted_files,
                'deleted_json_count': len(deleted_json_files),
                'deleted_json_files': deleted_json_files
            })
            
        except PermissionError as e:
            logger.error(f'删除文件权限不足: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': f'删除文件权限不足: {str(e)}'
            })
        except Exception as e:
            logger.error(f'删除文件时发生错误: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': f'删除文件时发生错误: {str(e)}'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'清除图片时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'清除图片时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_system_config(request):
    """
    从config.ini文件加载系统配置的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含系统配置数据的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 检查配置文件是否存在
        if not os.path.exists(config_path):
            return JsonResponse({
                'success': False,
                'error': 'config.ini文件不存在'
            })
        
        # 读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 获取系统配置数据
        system_config = {}
        
        # 读取系统参数
        if config.has_section('SYSTEM_CONFIG'):
            system_config.update({
                'enable_logs': config.getboolean('SYSTEM_CONFIG', 'enable_logs', fallback=True),
                'content_generation_timeout': config.getint('SYSTEM_CONFIG', 'content_generation_timeout', fallback=300),
                'format_generation_timeout': config.getint('SYSTEM_CONFIG', 'format_generation_timeout', fallback=120)
            })
        else:
            system_config.update({
                'enable_logs': True,
                'content_generation_timeout': 300,
                'format_generation_timeout': 120
            })
        
        # 读取ComfyUI配置
        if config.has_section('COMFYUI_CONFIG'):
            system_config.update({
                'comfyui_address': config.get('COMFYUI_CONFIG', 'comfyui_address', fallback='http://192.168.1.85:8188/'),
                'image_workflow': config.get('COMFYUI_CONFIG', 'image_workflow', fallback=''),
                'audio_workflow': config.get('COMFYUI_CONFIG', 'audio_workflow', fallback='')
            })
        else:
            system_config.update({
                'comfyui_address': 'http://192.168.1.85:8188/',
                'image_workflow': '',
                'audio_workflow': ''
            })
        
        # 记录日志
        logger.info(f'已加载系统配置: 启用日志={system_config["enable_logs"]}')
        
        return JsonResponse({
            'success': True,
            'config': system_config
        })
        
    except Exception as e:
        logger.error(f'加载系统配置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载配置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_default_values(request):
    """
    从config.ini文件加载默认值的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含默认值数据的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 检查配置文件是否存在
        if not os.path.exists(config_path):
            return JsonResponse({
                'success': False,
                'error': 'config.ini文件不存在'
            })
        
        # 读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 获取默认值数据
        default_values = {
            'system_params': {
                'enable_logs': True,
                'content_generation_timeout': 300,
                'format_generation_timeout': 120
            },
            'comfyui_config': {
                'comfyui_address': 'http://192.168.1.85:8188/',
                'image_workflow': '',
                'audio_workflow': ''
            }
        }
        
        # 从SYSTEM_DEFAULTS节读取系统参数默认值
        if config.has_section('SYSTEM_DEFAULTS'):
            if config.has_option('SYSTEM_DEFAULTS', 'enable_logs'):
                default_values['system_params']['enable_logs'] = config.getboolean('SYSTEM_DEFAULTS', 'enable_logs')
            if config.has_option('SYSTEM_DEFAULTS', 'content_generation_timeout'):
                default_values['system_params']['content_generation_timeout'] = config.getint('SYSTEM_DEFAULTS', 'content_generation_timeout')
            if config.has_option('SYSTEM_DEFAULTS', 'format_generation_timeout'):
                default_values['system_params']['format_generation_timeout'] = config.getint('SYSTEM_DEFAULTS', 'format_generation_timeout')
        
        # 从COMFYUI_DEFAULTS节读取ComfyUI配置默认值
        if config.has_section('COMFYUI_DEFAULTS'):
            if config.has_option('COMFYUI_DEFAULTS', 'comfyui_address'):
                default_values['comfyui_config']['comfyui_address'] = config.get('COMFYUI_DEFAULTS', 'comfyui_address')
            if config.has_option('COMFYUI_DEFAULTS', 'image_workflow'):
                default_values['comfyui_config']['image_workflow'] = config.get('COMFYUI_DEFAULTS', 'image_workflow')
            if config.has_option('COMFYUI_DEFAULTS', 'audio_workflow'):
                default_values['comfyui_config']['audio_workflow'] = config.get('COMFYUI_DEFAULTS', 'audio_workflow')
        
        # 记录日志
        logger.info('已加载默认值配置')
        
        return JsonResponse(default_values)
        
    except Exception as e:
        logger.error(f'加载默认值时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载默认值时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_model_config(request):
    """
    从config.ini文件加载模型配置的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含配置数据的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 检查配置文件是否存在
        if not os.path.exists(config_path):
            return JsonResponse({
                'success': False,
                'error': 'config.ini文件不存在'
            })
        
        # 读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 检查MODEL_CONFIG节是否存在
        if not config.has_section('MODEL_CONFIG'):
            return JsonResponse({
                'success': False,
                'error': 'config.ini文件中没有找到MODEL_CONFIG配置节'
            })
        
        # 获取配置数据
        model_config = {
            'selected_model': config.get('MODEL_CONFIG', 'selected_model', fallback=''),
            'api_key': config.get('MODEL_CONFIG', 'api_key', fallback=''),
            'api_url': config.get('MODEL_CONFIG', 'api_url', fallback=''),
            'model_name': config.get('MODEL_CONFIG', 'model_name', fallback='')
        }
        
        # 记录日志
        logger.info(f'已加载模型配置: 模型={model_config["selected_model"]}, 模型名称={model_config["model_name"]}')
        
        return JsonResponse({
            'success': True,
            'config': model_config
        })
        
    except Exception as e:
        logger.error(f'加载模型配置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载配置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_workflow_list(request):
    """
    加载工作流文件列表的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含工作流文件列表的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        workflow_dir = os.path.join(project_root, 'common', 'Workflow')
        
        # 检查工作流目录是否存在
        if not os.path.exists(workflow_dir):
            return JsonResponse({
                'success': False,
                'error': 'Workflow目录不存在'
            })
        
        # 获取所有.json文件
        workflow_files = []
        for filename in os.listdir(workflow_dir):
            if filename.endswith('.json'):
                workflow_files.append(filename)
        
        # 记录日志
        logger.info(f'已加载工作流文件列表: {workflow_files}')
        
        return JsonResponse({
            'success': True,
            'workflows': workflow_files
        })
        
    except Exception as e:
        logger.error(f'加载工作流列表时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载工作流列表时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def validate_workflow(request):
    """
    验证工作流文件中是否包含指定的提示词插入标志
    
    参数:
        request: Django的HttpRequest对象，包含工作流文件名和必需标志
        
    返回:
        JsonResponse: 包含验证结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        workflow_file = data.get('workflow_file', '')
        required_flag = data.get('required_flag', '')
        
        if not workflow_file or not required_flag:
            return JsonResponse({
                'success': False,
                'error': '缺少工作流文件名或必需标志参数'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        workflow_path = os.path.join(project_root, 'common', 'Workflow', workflow_file)
        
        # 检查工作流文件是否存在
        if not os.path.exists(workflow_path):
            return JsonResponse({
                'success': False,
                'error': f'工作流文件不存在: {workflow_file}',
                'has_flag': False
            })
        
        # 读取工作流文件内容
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_content = f.read()
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'读取工作流文件失败: {str(e)}',
                'has_flag': False
            })
        
        # 检查是否包含必需的标志
        has_flag = required_flag in workflow_content
        
        logger.info(f'验证工作流文件 {workflow_file}，查找标志 {required_flag}，结果: {has_flag}')
        
        return JsonResponse({
            'success': True,
            'has_flag': has_flag,
            'workflow_file': workflow_file,
            'required_flag': required_flag
        })
        
    except json.JSONDecodeError:
        logger.error('验证工作流时JSON解析错误')
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式',
            'has_flag': False
        })
    except Exception as e:
        logger.error(f'验证工作流时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'验证工作流时发生错误: {str(e)}',
            'has_flag': False
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_system_config(request):
    """
    保存系统配置到config.ini文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含系统配置数据
        
    返回:
        JsonResponse: 包含保存结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        system_config = data
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 创建或读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        
        # 如果文件存在，先读取现有配置
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        # 确保存在SYSTEM_CONFIG节
        if not config.has_section('SYSTEM_CONFIG'):
            config.add_section('SYSTEM_CONFIG')
        
        # 确保存在COMFYUI_CONFIG节
        if not config.has_section('COMFYUI_CONFIG'):
            config.add_section('COMFYUI_CONFIG')
        
        # 设置系统参数
        if 'enable_logs' in system_config:
            config.set('SYSTEM_CONFIG', 'enable_logs', 'true' if system_config['enable_logs'] else 'false')
        if 'content_generation_timeout' in system_config:
            config.set('SYSTEM_CONFIG', 'content_generation_timeout', str(system_config['content_generation_timeout']))
        if 'format_generation_timeout' in system_config:
            config.set('SYSTEM_CONFIG', 'format_generation_timeout', str(system_config['format_generation_timeout']))
        
        # 设置ComfyUI配置
        if 'comfyui_address' in system_config:
            config.set('COMFYUI_CONFIG', 'comfyui_address', system_config['comfyui_address'])
        if 'image_workflow' in system_config:
            config.set('COMFYUI_CONFIG', 'image_workflow', system_config['image_workflow'])
        if 'audio_workflow' in system_config:
            config.set('COMFYUI_CONFIG', 'audio_workflow', system_config['audio_workflow'])
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        # 记录日志
        logger.info(f'系统配置已保存: 启用日志={system_config.get("enable_logs", False)}')
        # 确保日志输出的布尔值是正确的，而不是字符串
        
        return JsonResponse({
            'success': True,
            'message': '系统配置已成功保存到config.ini文件'
        })
        
    except json.JSONDecodeError:
        logger.error('保存系统配置时JSON解析错误')
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'保存系统配置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存配置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_api_list(request):
    """
    加载API列表的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含API列表的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        if not os.path.exists(config_path):
            return JsonResponse({'success': True, 'apis': []})
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        apis = []
        
        # 获取当前激活的API
        active_api = config.get('MAIN_MODEL', 'active_api', fallback='') if config.has_section('MAIN_MODEL') else ''
        
        # 查找所有API配置节
        for section_name in config.sections():
            if section_name.startswith('API_'):
                # 根据MAIN_MODEL中的active_api来确定状态
                status = 'active' if section_name == active_api else 'inactive'
                
                api_data = {
                    'id': section_name,
                    'name': config.get(section_name, 'name', fallback='未命名API'),
                    'api_url': config.get(section_name, 'api_url', fallback=''),
                    'api_key': config.get(section_name, 'api_key', fallback=''),
                    'selected_model': config.get(section_name, 'selected_model', fallback=''),
                    'status': status,
                    'created_time': config.get(section_name, 'created_time', fallback='')
                }
                apis.append(api_data)
        
        # 按创建时间排序
        apis.sort(key=lambda x: x['created_time'], reverse=True)
        
        logger.info(f'已加载API列表，共{len(apis)}个API')
        
        return JsonResponse({'success': True, 'apis': apis})
    except Exception as e:
        logger.error(f'加载API列表时发生错误: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def save_api_config(request):
    """
    保存API配置的API端点
    
    参数:
        request: Django的HttpRequest对象，包含API配置数据
        
    返回:
        JsonResponse: 包含保存结果的JSON响应
    """
    try:
        data = json.loads(request.body)
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        config = configparser.ConfigParser(interpolation=None)
        
        # 读取现有配置
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        # 确定API ID
        api_id = data.get('api_id')
        if not api_id:
            # 生成新的API ID
            import time
            api_id = f"API_{int(time.time())}"
        
        # 确保API节存在
        if not config.has_section(api_id):
            config.add_section(api_id)
        
        # 保存API配置
        config.set(api_id, 'name', data.get('name', ''))
        config.set(api_id, 'api_url', data.get('api_url', ''))
        config.set(api_id, 'api_key', data.get('api_key', ''))
        config.set(api_id, 'selected_model', data.get('selected_model', ''))
        
        # 如果是新API，设置创建时间
        if not config.has_option(api_id, 'created_time'):
            config.set(api_id, 'created_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        logger.info(f'API配置已保存: {api_id} - {data.get("name", "")}')
        
        return JsonResponse({'success': True, 'api_id': api_id})
    except json.JSONDecodeError:
        logger.error('保存API配置时JSON解析错误')
        return JsonResponse({'success': False, 'error': '无效的JSON数据格式'})
    except Exception as e:
        logger.error(f'保存API配置时发生错误: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def activate_api(request):
    """
    激活API的API端点
    
    参数:
        request: Django的HttpRequest对象，包含要激活的API ID
        
    返回:
        JsonResponse: 包含激活结果的JSON响应
    """
    try:
        data = json.loads(request.body)
        api_id = data.get('api_id')
        
        if not api_id:
            return JsonResponse({'success': False, 'error': 'API ID不能为空'})
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        if not os.path.exists(config_path):
            return JsonResponse({'success': False, 'error': '配置文件不存在'})
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        if not config.has_section(api_id):
            return JsonResponse({'success': False, 'error': 'API不存在'})
        
        # 确保MAIN_MODEL节存在
        if not config.has_section('MAIN_MODEL'):
            config.add_section('MAIN_MODEL')
        
        # 设置激活的API
        config.set('MAIN_MODEL', 'active_api', api_id)
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        logger.info(f'API已激活: {api_id}')
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        logger.error('激活API时JSON解析错误')
        return JsonResponse({'success': False, 'error': '无效的JSON数据格式'})
    except Exception as e:
        logger.error(f'激活API时发生错误: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def delete_api(request):
    """
    删除API配置的API端点
    
    参数:
        request: Django的HttpRequest对象，包含要删除的API ID
        
    返回:
        JsonResponse: 包含删除结果的JSON响应
    """
    try:
        data = json.loads(request.body)
        api_id = data.get('api_id')
        
        if not api_id:
            return JsonResponse({'success': False, 'error': 'API ID不能为空'})
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        if not os.path.exists(config_path):
            return JsonResponse({'success': False, 'error': '配置文件不存在'})
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        if not config.has_section(api_id):
            return JsonResponse({'success': False, 'error': 'API不存在'})
        
        # 检查是否是激活的API
        active_api = config.get('MAIN_MODEL', 'active_api', fallback='') if config.has_section('MAIN_MODEL') else ''
        was_active = (api_id == active_api)
        
        # 删除API节
        config.remove_section(api_id)
        
        # 如果删除的是激活的API，清空MAIN_MODEL中的active_api
        if was_active and config.has_section('MAIN_MODEL'):
            config.set('MAIN_MODEL', 'active_api', '')
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        logger.info(f'API已删除: {api_id}')
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        logger.error('删除API时JSON解析错误')
        return JsonResponse({'success': False, 'error': '无效的JSON数据格式'})
    except Exception as e:
        logger.error(f'删除API时发生错误: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)})

def get_active_api(request):
    """
    获取当前激活的API信息
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含当前激活API信息的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        if not os.path.exists(config_path):
            return JsonResponse({'success': True, 'active_api': None})
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 获取当前激活的API
        active_api_id = config.get('MAIN_MODEL', 'active_api', fallback='') if config.has_section('MAIN_MODEL') else ''
        
        if not active_api_id or not config.has_section(active_api_id):
            return JsonResponse({'success': True, 'active_api': None})
        
        # 获取激活API的详细信息
        active_api_info = {
            'id': active_api_id,
            'name': config.get(active_api_id, 'name', fallback=''),
            'api_url': config.get(active_api_id, 'api_url', fallback=''),
            'api_key': config.get(active_api_id, 'api_key', fallback=''),
            'selected_model': config.get(active_api_id, 'selected_model', fallback=''),
            'created_time': config.get(active_api_id, 'created_time', fallback='')
        }
        
        return JsonResponse({'success': True, 'active_api': active_api_info})
    except Exception as e:
        logger.error(f'获取激活API信息时发生错误: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def create_project(request):
    """
    创建新项目的API端点
    
    参数:
        request: Django的HttpRequest对象，包含项目名称和描述
        
    返回:
        JsonResponse: 包含创建结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        project_name = data.get('project_name', '').strip()
        project_desc = data.get('project_desc', '').strip()
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        projects_dir = os.path.join(project_root, 'projects')
        
        # 确保projects目录存在
        os.makedirs(projects_dir, exist_ok=True)
        
        # 确定文件夹名称
        if project_name:
            # 如果有项目名称，检查是否包含中文
            folder_name = convert_chinese_to_pinyin(project_name)
        else:
            # 如果没有项目名称，使用当前时间
            folder_name = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建项目文件夹路径
        project_folder = os.path.join(projects_dir, folder_name)
        
        # 检查文件夹是否已存在
        if os.path.exists(project_folder):
            return JsonResponse({
                'success': False,
                'error': f'项目文件夹 "{folder_name}" 已存在，请使用不同的项目名称'
            })
        
        # 创建项目文件夹
        os.makedirs(project_folder)
        
        # 如果有项目描述，创建描述文件
        if project_desc:
            desc_file = os.path.join(project_folder, 'project_description.txt')
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(project_desc)
        
        # 创建子目录
        images_dir = os.path.join(project_folder, 'images')
        audios_dir = os.path.join(project_folder, 'audios')
        videos_dir = os.path.join(project_folder, 'videos')
        temp_dir = os.path.join(project_folder, 'temp')
        
        os.makedirs(images_dir)
        os.makedirs(audios_dir)
        os.makedirs(videos_dir)
        os.makedirs(temp_dir)
        
        # 创建项目的parameter.ini文件
        try:
            from common.audio_processor import AudioProcessor
            audio_processor = AudioProcessor()
            audio_processor.create_project_parameter_ini(project_folder)
            logger.info(f'项目parameter.ini文件创建成功: {project_folder}')
        except Exception as param_error:
            logger.warning(f'创建项目parameter.ini文件时发生错误: {str(param_error)}')
        
        # 保存当前项目到config.ini
        try:
            save_current_project_to_config(project_folder, folder_name)
        except Exception as config_error:
            logger.warning(f'保存当前项目到配置文件时发生错误: {str(config_error)}')
        
        # 记录日志
        logger.info(f'项目创建成功: 文件夹名称={folder_name}, 原始名称={project_name}, 路径={project_folder}')
        
        return JsonResponse({
            'success': True,
            'message': f'项目 "{project_name or folder_name}" 创建成功',
            'folder_name': folder_name,
            'project_path': project_folder
        })
        
    except json.JSONDecodeError:
        logger.error('创建项目时JSON解析错误')
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'创建项目时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'创建项目时发生错误: {str(e)}'
        })

def convert_chinese_to_pinyin(text):
    """
    将中文转换为拼音，如果没有安装pypinyin则返回原文本
    
    参数:
        text: 要转换的文本
        
    返回:
        转换后的拼音文本或原文本
    """
    if lazy_pinyin is None:
        # 如果没有安装pypinyin，简单处理：移除特殊字符，保留字母数字和中文
        import re
        # 将中文和特殊字符替换为下划线，保留字母数字
        result = re.sub(r'[^\w\s]', '_', text)
        result = re.sub(r'\s+', '_', result)
        return result
    else:
        # 使用pypinyin转换中文为拼音
        pinyin_list = lazy_pinyin(text, style=Style.NORMAL)
        # 将拼音列表连接成字符串，用下划线分隔
        result = '_'.join(pinyin_list)
        # 移除特殊字符，只保留字母数字和下划线
        import re
        result = re.sub(r'[^\w]', '_', result)
        # 移除多余的下划线
        result = re.sub(r'_+', '_', result).strip('_')
        return result

def save_current_project_to_config(project_path, project_name):
    """
    将当前项目信息保存到config.ini文件
    
    参数:
        project_path: 项目的完整路径
        project_name: 项目名称
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 创建或读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        
        # 如果文件存在，先读取现有配置
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        # 确保存在PROJECT_CONFIG节
        if not config.has_section('PROJECT_CONFIG'):
            config.add_section('PROJECT_CONFIG')
        
        # 设置当前项目信息
        config.set('PROJECT_CONFIG', 'current_project_path', project_path)
        config.set('PROJECT_CONFIG', 'current_project_name', project_name)
        config.set('PROJECT_CONFIG', 'last_opened_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        logger.info(f'当前项目已保存到配置文件: {project_name} -> {project_path}')
        
    except Exception as e:
        logger.error(f'保存当前项目到配置文件时发生错误: {str(e)}')
        raise

def load_current_project_from_config():
    """
    从config.ini文件加载当前项目信息
    
    返回:
        dict: 包含项目信息的字典，如果没有找到则返回None
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 检查配置文件是否存在
        if not os.path.exists(config_path):
            return None
        
        # 读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 检查PROJECT_CONFIG节是否存在
        if not config.has_section('PROJECT_CONFIG'):
            return None
        
        # 获取项目信息
        current_project_path = config.get('PROJECT_CONFIG', 'current_project_path', fallback='')
        current_project_name = config.get('PROJECT_CONFIG', 'current_project_name', fallback='')
        last_opened_time = config.get('PROJECT_CONFIG', 'last_opened_time', fallback='')
        
        # 检查项目路径是否仍然存在
        if current_project_path and os.path.exists(current_project_path):
            return {
                'project_path': current_project_path,
                'project_name': current_project_name,
                'last_opened_time': last_opened_time
            }
        else:
            # 如果项目路径不存在，清除配置
            if current_project_path:
                logger.warning(f'配置中的项目路径不存在，已清除: {current_project_path}')
                clear_current_project_from_config()
            return None
            
    except Exception as e:
        logger.error(f'加载当前项目配置时发生错误: {str(e)}')
        return None

def clear_current_project_from_config():
    """
    清除config.ini文件中的当前项目信息
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 如果文件不存在，直接返回
        if not os.path.exists(config_path):
            return
        
        # 读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 如果PROJECT_CONFIG节存在，移除当前项目相关的配置
        if config.has_section('PROJECT_CONFIG'):
            if config.has_option('PROJECT_CONFIG', 'current_project_path'):
                config.remove_option('PROJECT_CONFIG', 'current_project_path')
            if config.has_option('PROJECT_CONFIG', 'current_project_name'):
                config.remove_option('PROJECT_CONFIG', 'current_project_name')
            if config.has_option('PROJECT_CONFIG', 'last_opened_time'):
                config.remove_option('PROJECT_CONFIG', 'last_opened_time')
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        logger.info('已清除当前项目配置')
        
    except Exception as e:
        logger.error(f'清除当前项目配置时发生错误: {str(e)}')

@csrf_exempt
@require_http_methods(["GET"])
def get_current_project(request):
    """
    获取当前项目信息的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含当前项目信息的JSON响应
    """
    try:
        current_project = load_current_project_from_config()
        
        if current_project:
            return JsonResponse({
                'success': True,
                'project': current_project
            })
        else:
            return JsonResponse({
                'success': True,
                'project': None,
                'message': '没有找到当前项目'
            })
            
    except Exception as e:
        logger.error(f'获取当前项目信息时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'获取当前项目信息时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def clear_current_project(request):
    """
    清除当前项目的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含清除结果的JSON响应
    """
    try:
        clear_current_project_from_config()
        
        return JsonResponse({
            'success': True,
            'message': '当前项目已清除'
        })
        
    except Exception as e:
        logger.error(f'清除当前项目时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'清除当前项目时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_project_list(request):
    """
    获取projects目录下所有项目的列表
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含项目列表的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        projects_dir = os.path.join(project_root, 'projects')
        
        # 检查projects目录是否存在
        if not os.path.exists(projects_dir):
            return JsonResponse({
                'success': True,
                'projects': [],
                'message': 'projects目录不存在'
            })
        
        projects = []
        
        # 遍历projects目录下的所有文件夹
        for item in os.listdir(projects_dir):
            item_path = os.path.join(projects_dir, item)
            
            # 只处理文件夹
            if os.path.isdir(item_path):
                project_info = {
                    'name': item,
                    'path': item_path,
                    'created_time': '',
                    'description': ''
                }
                
                # 获取文件夹创建时间
                try:
                    created_timestamp = os.path.getctime(item_path)
                    project_info['created_time'] = datetime.fromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    project_info['created_time'] = '未知'
                
                # 检查是否有项目描述文件
                desc_file = os.path.join(item_path, 'project_description.txt')
                if os.path.exists(desc_file):
                    try:
                        with open(desc_file, 'r', encoding='utf-8') as f:
                            description = f.read().strip()
                            project_info['description'] = description[:100] + '...' if len(description) > 100 else description
                    except:
                        project_info['description'] = '无法读取描述'
                
                # 检查项目是否完成（是否包含MP4文件）
                has_mp4 = False
                try:
                    for file in os.listdir(item_path):
                        if file.lower().endswith('.mp4'):
                            has_mp4 = True
                            break
                except:
                    pass
                project_info['completed'] = has_mp4
                
                projects.append(project_info)
        
        # 按创建时间倒序排列（最新的在前面）
        projects.sort(key=lambda x: x['created_time'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'projects': projects
        })
        
    except Exception as e:
        logger.error(f'获取项目列表时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'获取项目列表时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def open_project(request):
    """
    打开指定项目的API端点
    
    参数:
        request: Django的HttpRequest对象，包含项目路径
        
    返回:
        JsonResponse: 包含打开结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        project_path = data.get('project_path', '').strip()
        project_name = data.get('project_name', '').strip()
        
        if not project_path or not project_name:
            return JsonResponse({
                'success': False,
                'error': '项目路径和名称不能为空'
            })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 保存当前项目到config.ini
        try:
            save_current_project_to_config(project_path, project_name)
        except Exception as config_error:
            logger.warning(f'保存当前项目到配置文件时发生错误: {str(config_error)}')
            return JsonResponse({
                'success': False,
                'error': f'保存项目配置时发生错误: {str(config_error)}'
            })
        
        # 记录日志
        logger.info(f'项目打开成功: 项目名称={project_name}, 路径={project_path}')
        
        return JsonResponse({
            'success': True,
            'message': f'项目 "{project_name}" 打开成功',
            'project_name': project_name,
            'project_path': project_path
        })
        
    except json.JSONDecodeError:
        logger.error('打开项目时JSON解析错误')
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'打开项目时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'打开项目时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_project_statistics(request):
    """
    获取项目统计信息的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含项目统计信息的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        projects_dir = os.path.join(project_root, 'projects')
        
        # 检查projects目录是否存在
        if not os.path.exists(projects_dir):
            return JsonResponse({
                'success': True,
                'total_projects': 0,
                'completed_projects': 0,
                'ongoing_projects': 0
            })
        
        total_projects = 0
        completed_projects = 0
        ongoing_projects = 0
        
        # 遍历projects目录下的所有文件夹
        for item in os.listdir(projects_dir):
            item_path = os.path.join(projects_dir, item)
            
            # 只处理文件夹
            if os.path.isdir(item_path):
                total_projects += 1
                
                # 检查项目目录中是否有MP4文件
                has_mp4 = False
                try:
                    for file in os.listdir(item_path):
                        if file.lower().endswith('.mp4'):
                            has_mp4 = True
                            break
                    
                    # 如果没有在根目录找到，检查子目录
                    if not has_mp4:
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                if file.lower().endswith('.mp4'):
                                    has_mp4 = True
                                    break
                            if has_mp4:
                                break
                    
                    if has_mp4:
                        completed_projects += 1
                    else:
                        ongoing_projects += 1
                        
                except Exception as e:
                    logger.warning(f'检查项目 {item} 的MP4文件时发生错误: {str(e)}')
                    # 如果检查失败，默认为进行中
                    ongoing_projects += 1
        
        return JsonResponse({
            'success': True,
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'ongoing_projects': ongoing_projects
        })
        
    except Exception as e:
        logger.error(f'获取项目统计信息时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'获取项目统计信息时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_paper_content(request):
    """
    加载当前项目的paper.json文件内容
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含paper.json文件内容的JSON响应
    """
    try:
        # 获取当前项目路径
        current_project_path = get_current_project_path()
        if not current_project_path:
            return JsonResponse({
                'success': False,
                'error': '未找到当前项目路径，请先打开一个项目'
            })
        
        # 构建paper.json文件路径
        paper_file_path = os.path.join(current_project_path, 'paper.json')
        
        # 检查文件是否存在
        if not os.path.exists(paper_file_path):
            # 兼容旧的paper.ini文件
            old_paper_file_path = os.path.join(current_project_path, 'paper.ini')
            if os.path.exists(old_paper_file_path):
                # 读取旧文件内容并迁移到新文件
                with open(old_paper_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 保存到新的paper.json文件
                with open(paper_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                # 删除旧文件
                os.remove(old_paper_file_path)
                return JsonResponse({
                    'success': True,
                    'content': content
                })
            else:
                return JsonResponse({
                    'success': True,
                    'content': ''
                })
        
        # 读取文件内容
        with open(paper_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        logger.error(f'加载paper.json文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载文案内容时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def generate_first_sentence(request):
    """
    使用当前激活的API生成文案的第一句话
    
    参数:
        request: Django的HttpRequest对象，包含prompt
        
    返回:
        JsonResponse: 包含生成结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': '第一句话生成PROMPT不能为空'
            })
        
        # 获取当前项目路径
        current_project_path = get_current_project_path()
        if not current_project_path:
            return JsonResponse({
                'success': False,
                'error': '未找到当前项目路径，请先打开一个项目'
            })
        
        # 获取当前激活的API配置
        active_api = get_active_api_config()
        if not active_api:
            return JsonResponse({
                'success': False,
                'error': '未找到激活的API配置，请先在系统设置中激活一个API'
            })
        
        # 记录生成开始日志
        import logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        first_sentence_logger = logging.getLogger(__name__)
        first_sentence_logger.info(f"开始生成第一句话 - 项目路径: {current_project_path}")
        first_sentence_logger.info(f"使用API: {active_api['api_url']}, 模型: {active_api['selected_model']}")
        first_sentence_logger.info(f"第一句话提示词长度: {len(prompt)} 字符")
        
        # 检查parameter.ini文件中的theme值
        try:
            import configparser
            parameter_file_path = os.path.join(current_project_path, 'parameter.ini')
            theme_suffix = ""
            
            if os.path.exists(parameter_file_path):
                config = configparser.ConfigParser(interpolation=None)
                config.read(parameter_file_path, encoding='utf-8')
                
                if config.has_section('PAPER_INFO') and config.has_option('PAPER_INFO', 'theme'):
                    theme_value = config.get('PAPER_INFO', 'theme').strip()
                    if theme_value:  # 如果theme有值
                        theme_suffix = f"\n\n# 主题：用户指定的主题是\"{theme_value}\"，请围绕这个主题生成第一句话"
                        first_sentence_logger.info(f"检测到主题设置: {theme_value}")
                    else:
                        # 如果没有主题，添加治愈系默认提示
                        theme_suffix = "\n\n# 请生成治愈系文案的第一句话"
                        first_sentence_logger.info("未检测到主题，使用治愈系默认设置")
                else:
                    # 如果没有主题，添加治愈系默认提示
                    theme_suffix = "\n\n# 请生成治愈系文案的第一句话"
                    first_sentence_logger.info("未检测到主题配置，使用治愈系默认设置")
            else:
                # 如果没有配置文件，添加治愈系默认提示
                theme_suffix = "\n\n# 请生成治愈系文案的第一句话"
                first_sentence_logger.info("未找到配置文件，使用治愈系默认设置")
            
            # 将主题信息添加到prompt后面
            final_prompt = prompt + theme_suffix
            
        except Exception as theme_error:
            first_sentence_logger.warning(f"读取主题配置时发生错误: {str(theme_error)}，使用原始prompt")
            final_prompt = prompt + "\n\n# 请生成治愈系文案的第一句话"
        
        # 设置最大重试次数
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                first_sentence_logger.info(f"第 {attempt + 1} 次第一句话生成尝试")
                
                # 调用AI API生成第一句话
                import requests
                
                # 构建API请求
                api_url = active_api['api_url']
                if not api_url.endswith('/'):
                    api_url += '/'
                api_url += 'chat/completions'
                
                headers = {
                    'Authorization': f'Bearer {active_api["api_key"]}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': active_api.get('selected_model', 'gpt-3.5-turbo'),
                    'messages': [
                        {
                            'role': 'user',
                            'content': final_prompt
                        }
                    ],
                    'temperature': 0.8  # 稍微提高创造性
                }
                
                # 发送请求
                response = requests.post(api_url, headers=headers, json=payload, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    generated_content = result['choices'][0]['message']['content'].strip()
                    
                    first_sentence_logger.info(f"API调用成功，生成内容长度: {len(generated_content)} 字符")
                    
                    # 过滤掉<think>标签包裹的思考过程部分
                    import re
                    think_pattern = r'<think>.*?</think>'
                    filtered_content = re.sub(think_pattern, '', generated_content, flags=re.DOTALL).strip()
                    
                    if filtered_content != generated_content:
                        first_sentence_logger.info(f"已过滤思考过程，过滤后内容长度: {len(filtered_content)} 字符")
                        generated_content = filtered_content
                    
                    # 提取第一句话（取第一行非空内容）
                    lines = [line.strip() for line in generated_content.split('\n') if line.strip()]
                    if lines:
                        first_sentence = lines[0]
                        # 如果第一行太短，尝试合并前几行
                        if len(first_sentence) < 10 and len(lines) > 1:
                            first_sentence = ''.join(lines[:2])
                    else:
                        first_sentence = generated_content
                    
                    # 进行符号审核（免费的）
                    try:
                        first_sentence_logger.info(f"开始符号审核，检查第一句话是否包含不允许的符号")
                        
                        # 记录生成的第一句话内容
                        first_sentence_logger.info(f"生成的第一句话: {first_sentence}")
                        
                        # 定义允许的符号：半角和全角的逗号、句号、问号、感叹号
                        allowed_punctuation = '，。？！,.?!'
                        
                        # 检查第一句话中是否包含不允许的符号
                        invalid_symbols = []
                        for char in first_sentence:
                            # 如果是标点符号但不在允许列表中
                            if not char.isalnum() and not char.isspace() and char not in allowed_punctuation:
                                if char not in invalid_symbols:
                                    invalid_symbols.append(char)
                        
                        if invalid_symbols:
                            invalid_symbols_str = ''.join(invalid_symbols)
                            first_sentence_logger.warning(f"第 {attempt + 1} 次生成的第一句话包含不允许的符号: {invalid_symbols_str}")
                            first_sentence_logger.warning(f"完整第一句话内容: {first_sentence}")
                            if attempt == max_retries - 1:
                                return JsonResponse({
                                    'success': False,
                                    'error': f'经过{max_retries}次尝试，生成的第一句话仍包含不允许的符号: {invalid_symbols_str}'
                                })
                            continue  # 符号审核不通过，直接重新生成
                        
                        first_sentence_logger.info(f"符号审核通过，未发现不允许的符号")
                        
                    except Exception as symbol_exception:
                        first_sentence_logger.error(f"符号审核过程中发生错误: {str(symbol_exception)}")
                        # 符号审核出错时继续
                        first_sentence_logger.warning("符号审核失败，但继续返回结果")
                    
                    # 保存第一句话到配置文件
                    try:
                        parameter_file_path = os.path.join(current_project_path, 'parameter.ini')
                        config = configparser.ConfigParser(interpolation=None)
                        
                        # 如果文件存在，先读取现有配置
                        if os.path.exists(parameter_file_path):
                            config.read(parameter_file_path, encoding='utf-8')
                        
                        # 确保PAPER_INFO节存在
                        if not config.has_section('PAPER_INFO'):
                            config.add_section('PAPER_INFO')
                        
                        # 保存第一句话到title字段
                        config.set('PAPER_INFO', 'title', first_sentence)
                        config.set('PAPER_INFO', 'first_sentence_generated_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        
                        # 保存配置文件
                        with open(parameter_file_path, 'w', encoding='utf-8') as config_file:
                            config.write(config_file)
                        
                        first_sentence_logger.info(f"第一句话已成功保存到: {parameter_file_path}")
                        
                    except Exception as save_error:
                        first_sentence_logger.error(f"保存第一句话到配置文件时发生错误: {str(save_error)}")
                        # 即使保存失败，也返回生成的内容
                    
                    return JsonResponse({
                        'success': True,
                        'first_sentence': first_sentence,
                        'message': f'第一句话生成成功 (第{attempt + 1}次尝试)'
                    })
                else:
                    error_msg = f'API请求失败，状态码: {response.status_code}'
                    
                    # 记录完整的响应信息用于调试
                    first_sentence_logger.error(f"API请求失败详情:")
                    first_sentence_logger.error(f"  - 状态码: {response.status_code}")
                    first_sentence_logger.error(f"  - 响应头: {dict(response.headers)}")
                    
                    if response.text:
                        first_sentence_logger.error(f"  - 完整响应内容: {response.text}")
                        try:
                            error_data = response.json()
                            first_sentence_logger.error(f"  - 解析后的JSON: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                            error_msg += f', 错误信息: {error_data.get("error", {}).get("message", response.text)}'
                        except json.JSONDecodeError as json_err:
                            first_sentence_logger.error(f"  - JSON解析失败: {str(json_err)}")
                            error_msg += f', 响应内容: {response.text[:200]}'
                    else:
                        first_sentence_logger.error("  - 响应内容为空")
                    
                    first_sentence_logger.error(f"第一句话API调用失败: {error_msg}")
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    })
                    
            except requests.exceptions.Timeout as timeout_err:
                first_sentence_logger.error(f"第 {attempt + 1} 次第一句话生成尝试超时详情:")
                first_sentence_logger.error(f"  - 超时类型: {type(timeout_err).__name__}")
                first_sentence_logger.error(f"  - 超时信息: {str(timeout_err)}")
                first_sentence_logger.error(f"  - API地址: {api_url}")
                
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'第一句话生成请求超时（已重试{max_retries}次），请检查网络连接或稍后重试。详情: {str(timeout_err)}'
                    })
                    
            except Exception as request_error:
                first_sentence_logger.error(f"第 {attempt + 1} 次第一句话生成尝试发生错误: {str(request_error)}")
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'第一句话生成时发生错误（已重试{max_retries}次）: {str(request_error)}'
                    })
        
        # 如果所有重试都失败了
        return JsonResponse({
            'success': False,
            'error': f'经过{max_retries}次尝试，第一句话生成仍然失败'
        })
        
    except json.JSONDecodeError:
        logger.error('第一句话生成时JSON解析错误')
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'第一句话生成时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'第一句话生成时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_first_sentence_prompt(request):
    """
    保存第一句话生成的PROMPT到文件
    
    参数:
        request: Django的HttpRequest对象，包含content和filename
        
    返回:
        JsonResponse: 包含保存结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        filename = data.get('filename', '').strip()
        
        if not content:
            return JsonResponse({
                'success': False,
                'error': '第一句话PROMPT内容不能为空'
            })
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '文件名不能为空'
            })
        
        # 确保文件名安全（移除危险字符）
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        if not safe_filename.endswith('.txt'):
            safe_filename += '.txt'
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        first_sentence_dir = os.path.join(project_root, 'common', 'first_sentence')
        
        # 确保目录存在
        os.makedirs(first_sentence_dir, exist_ok=True)
        
        # 构建文件路径
        file_path = os.path.join(first_sentence_dir, safe_filename)
        
        # 保存PROMPT到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f'第一句话PROMPT已保存到: {file_path}')
        
        return JsonResponse({
            'success': True,
            'message': f'第一句话PROMPT已成功保存为 {safe_filename}',
            'filename': safe_filename
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'保存第一句话PROMPT时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存第一句话PROMPT时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def generate_text(request):
    """
    使用当前激活的API生成文案并保存到paper.json文件
    
    参数:
        request: Django的HttpRequest对象，包含prompt
        
    返回:
        JsonResponse: 包含生成结果的JSON响应
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'PROMPT不能为空'
            })
        
        # 获取当前项目路径
        current_project_path = get_current_project_path()
        if not current_project_path:
            return JsonResponse({
                'success': False,
                'error': '未找到当前项目路径，请先打开一个项目'
            })
        
        # 获取当前激活的API配置
        active_api = get_active_api_config()
        if not active_api:
            return JsonResponse({
                'success': False,
                'error': '未找到激活的API配置，请先在系统设置中激活一个API'
            })
        
        # 记录生成开始日志
        import logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        text_logger = logging.getLogger(__name__)
        text_logger.info(f"开始生成文案 - 项目路径: {current_project_path}")
        text_logger.info(f"使用API: {active_api['api_url']}, 模型: {active_api['selected_model']}")
        text_logger.info(f"提示词长度: {len(prompt)} 字符")
        
        # 检查parameter.ini文件中的theme值
        try:
            import configparser
            parameter_file_path = os.path.join(current_project_path, 'parameter.ini')
            theme_suffix = ""
            
            if os.path.exists(parameter_file_path):
                config = configparser.ConfigParser(interpolation=None)
                config.read(parameter_file_path, encoding='utf-8')
                
                if config.has_section('PAPER_INFO') and config.has_option('PAPER_INFO', 'theme'):
                    theme_value = config.get('PAPER_INFO', 'theme').strip()
                    if theme_value:  # 如果theme有值
                        theme_suffix = f"\n\n# 主题：用户指定的主题是\"{theme_value}\""
                        text_logger.info(f"检测到主题设置: {theme_value}")
            
            # 将主题信息添加到prompt后面
            final_prompt = prompt + theme_suffix
            
        except Exception as theme_error:
            text_logger.warning(f"读取主题配置时发生错误: {str(theme_error)}，使用原始prompt")
            final_prompt = prompt
        
        # 设置最大重试次数
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                text_logger.info(f"第 {attempt + 1} 次生成尝试")
                
                # 调用AI API生成文案
                import requests
                
                # 构建API请求
                api_url = active_api['api_url']
                if not api_url.endswith('/'):
                    api_url += '/'
                api_url += 'chat/completions'
                
                headers = {
                    'Authorization': f'Bearer {active_api["api_key"]}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': active_api.get('selected_model', 'gpt-3.5-turbo'),
                    'messages': [
                        {
                            'role': 'user',
                            'content': final_prompt
                        }
                    ],
                    'temperature': 0.7
                }
                
                # 发送请求
                response = requests.post(api_url, headers=headers, json=payload, timeout=300)
                
                if response.status_code == 200:
                    result = response.json()
                    generated_content = result['choices'][0]['message']['content'].strip()
                    
                    text_logger.info(f"API调用成功，生成内容长度: {len(generated_content)} 字符")
                    
                    # 过滤掉<think>标签包裹的思考过程部分
                    import re
                    think_pattern = r'<think>.*?</think>'
                    filtered_content = re.sub(think_pattern, '', generated_content, flags=re.DOTALL).strip()
                    
                    if filtered_content != generated_content:
                        text_logger.info(f"已过滤思考过程，过滤后内容长度: {len(filtered_content)} 字符")
                        generated_content = filtered_content
                    
                    # 先进行符号审核（免费的）
                    try:
                        text_logger.info(f"开始符号审核，检查是否包含不允许的符号")
                        
                        # 记录生成的具体内容（截取前200字符用于日志）
                        content_preview = generated_content[:200] + "..." if len(generated_content) > 200 else generated_content
                        text_logger.info(f"生成的内容预览: {content_preview}")
                        
                        # 定义允许的符号：半角和全角的逗号、句号、问号、感叹号
                        allowed_punctuation = '，。？！,.?!'
                        
                        # 检查文案中是否包含不允许的符号
                        invalid_symbols = []
                        for char in generated_content:
                            # 如果是标点符号但不在允许列表中
                            if not char.isalnum() and not char.isspace() and char not in allowed_punctuation:
                                if char not in invalid_symbols:
                                    invalid_symbols.append(char)
                        
                        if invalid_symbols:
                            invalid_symbols_str = ''.join(invalid_symbols)
                            text_logger.warning(f"第 {attempt + 1} 次生成的内容包含不允许的符号: {invalid_symbols_str}")
                            text_logger.warning(f"完整生成内容: {generated_content}")
                            if attempt == max_retries - 1:
                                return JsonResponse({
                                    'success': False,
                                    'error': f'经过{max_retries}次尝试，生成的内容仍包含不允许的符号: {invalid_symbols_str}'
                                })
                            continue  # 符号审核不通过，直接重新生成，不进行百度云审核
                        
                        text_logger.info(f"符号审核通过，未发现不允许的符号")
                        
                    except Exception as symbol_exception:
                        text_logger.error(f"符号审核过程中发生错误: {str(symbol_exception)}")
                        # 符号审核出错时继续进行百度云审核
                        text_logger.warning("符号审核失败，但继续进行百度云审核")
                    
                    # 符号审核通过后，再进行百度云内容审核（收费的）
                    try:
                        text_logger.info(f"开始百度云内容审核，文本长度: {len(generated_content)} 字符")
                        
                        # 调用百度云内容审核
                        is_pass, conclusion_type, conclusion, censor_error = baidu_text_censor(generated_content)
                        
                        if not is_pass:
                            text_logger.warning(f"第 {attempt + 1} 次生成的内容未通过百度云审核: {censor_error or conclusion}")
                            if attempt == max_retries - 1:
                                return JsonResponse({
                                    'success': False,
                                    'error': f'经过{max_retries}次尝试，生成的内容仍未通过百度云审核: {censor_error or conclusion}'
                                })
                            continue
                        
                        text_logger.info(f"百度云内容审核通过: {conclusion}")
                        
                    except Exception as censor_exception:
                        text_logger.error(f"百度云内容审核过程中发生错误: {str(censor_exception)}")
                        # 如果审核过程出错，可以选择继续保存（根据业务需求决定）
                        # 这里选择记录错误但继续保存
                        text_logger.warning("百度云内容审核失败，但继续保存文案")
                    
                    # 将生成的文案按行保存到parameter.ini文件
                    try:
                        # 按行分割文案内容并过滤无效行
                        import re
                        raw_lines = [line.strip() for line in generated_content.split('\n') if line.strip()]
                        
                        # 过滤掉只有符号、只有一个字或一个字加符号的行
                        filtered_lines = []
                        for line in raw_lines:
                            # 移除所有标点符号和空白字符，只保留中文字符和英文字母
                            text_only = re.sub(r'[^\u4e00-\u9fffa-zA-Z]', '', line)
                            
                            # 如果去除符号后有2个或以上的字符，则保留这行
                            if len(text_only) >= 2:
                                filtered_lines.append(line)
                            else:
                                text_logger.info(f"过滤掉无效行: {line}")
                        
                        lines = filtered_lines
                        sentence_count = len(lines)
                        
                        # 读取或创建parameter.ini文件
                        import configparser
                        config = configparser.ConfigParser(interpolation=None)
                        parameter_file_path = os.path.join(current_project_path, 'parameter.ini')
                        
                        # 如果文件存在，先读取现有配置
                        if os.path.exists(parameter_file_path):
                            config.read(parameter_file_path, encoding='utf-8')
                        
                        # 确保PAPER_INFO节存在
                        if not config.has_section('PAPER_INFO'):
                            config.add_section('PAPER_INFO')
                        
                        # 确保VIDEO_SUBTITLE节存在（如果不存在则添加默认配置）
                        if not config.has_section('VIDEO_SUBTITLE'):
                            add_default_video_subtitle_config(config)
                        
                        # 更新基本信息
                        config.set('PAPER_INFO', 'sentence_count', str(sentence_count))
                        config.set('PAPER_INFO', 'generated_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        config.set('PAPER_INFO', 'file_format', 'text')
                        
                        # 提取标题（第一行作为标题）
                        if lines:
                            config.set('PAPER_INFO', 'title', lines[0])
                        
                        # 添加文案内容节
                        if config.has_section('PAPER_CONTENT'):
                            config.remove_section('PAPER_CONTENT')
                        config.add_section('PAPER_CONTENT')
                        
                        # 将每行文案保存为单独的配置项
                        for i, line in enumerate(lines, 1):
                            config.set('PAPER_CONTENT', f'line_{i}', line)
                        
                        # 保存parameter.ini文件
                        with open(parameter_file_path, 'w', encoding='utf-8') as config_file:
                            config.write(config_file)
                        
                        text_logger.info(f"文案已成功保存到: {parameter_file_path}，共{sentence_count}行")
                        
                    except Exception as save_error:
                        text_logger.error(f"保存parameter.ini文件时发生错误: {str(save_error)}")
                        return JsonResponse({
                            'success': False,
                            'error': f'保存文案时发生错误: {str(save_error)}'
                        })
                    
                    return JsonResponse({
                        'success': True,
                        'content': generated_content,
                        'message': f'文案生成成功并已保存到parameter.ini文件 (第{attempt + 1}次尝试，共{sentence_count}行)'
                    })
                else:
                    error_msg = f'API请求失败，状态码: {response.status_code}'
                    
                    # 记录完整的响应信息用于调试
                    text_logger.error(f"API请求失败详情:")
                    text_logger.error(f"  - 状态码: {response.status_code}")
                    text_logger.error(f"  - 响应头: {dict(response.headers)}")
                    
                    if response.text:
                        text_logger.error(f"  - 完整响应内容: {response.text}")
                        try:
                            error_data = response.json()
                            text_logger.error(f"  - 解析后的JSON: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
                            error_msg += f', 错误信息: {error_data.get("error", {}).get("message", response.text)}'
                        except json.JSONDecodeError as json_err:
                            text_logger.error(f"  - JSON解析失败: {str(json_err)}")
                            error_msg += f', 响应内容: {response.text[:200]}'
                    else:
                        text_logger.error("  - 响应内容为空")
                    
                    text_logger.error(f"API调用失败: {error_msg}")
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    })
                    
            except requests.exceptions.Timeout as timeout_err:
                text_logger.error(f"第 {attempt + 1} 次尝试超时详情:")
                text_logger.error(f"  - 超时类型: {type(timeout_err).__name__}")
                text_logger.error(f"  - 超时信息: {str(timeout_err)}")
                text_logger.error(f"  - API地址: {api_url}")
                text_logger.error(f"  - 请求头: {headers}")
                text_logger.error(f"  - 请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'API请求超时（已重试{max_retries}次），请检查网络连接或稍后重试。详情: {str(timeout_err)}'
                    })
                continue
            except requests.exceptions.RequestException as req_err:
                text_logger.error(f"第 {attempt + 1} 次尝试请求异常详情:")
                text_logger.error(f"  - 异常类型: {type(req_err).__name__}")
                text_logger.error(f"  - 异常信息: {str(req_err)}")
                text_logger.error(f"  - API地址: {api_url}")
                text_logger.error(f"  - 请求头: {headers}")
                text_logger.error(f"  - 请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                
                # 如果有响应对象，记录响应信息
                if hasattr(req_err, 'response') and req_err.response is not None:
                    response = req_err.response
                    text_logger.error(f"  - 响应状态码: {response.status_code}")
                    text_logger.error(f"  - 响应头: {dict(response.headers)}")
                    if response.text:
                        text_logger.error(f"  - 响应内容: {response.text}")
                
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'API请求失败（已重试{max_retries}次）: {str(req_err)}'
                    })
                continue
            except Exception as e:
                text_logger.error(f"第 {attempt + 1} 次生成尝试失败: {str(e)}")
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'生成文案时发生错误: {str(e)}'
                    })
                continue
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'生成文案时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'生成文案时发生错误: {str(e)}'
        })

def get_current_project_path():
    """
    从config.ini文件获取当前项目路径
    
    返回:
        str: 当前项目路径，如果未找到则返回None
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        if not os.path.exists(config_path):
            return None
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        if config.has_section('PROJECT_CONFIG') and config.has_option('PROJECT_CONFIG', 'current_project_path'):
            return config.get('PROJECT_CONFIG', 'current_project_path')
        
        return None
        
    except Exception as e:
        logger.error(f'获取当前项目路径时发生错误: {str(e)}')
        return None

def add_default_video_subtitle_config(config):
    """
    添加默认的VIDEO_SUBTITLE配置到ConfigParser对象
    
    参数:
        config: ConfigParser对象
    """
    try:
        # 尝试从主配置文件读取默认值
        default_values = load_default_subtitle_config()
        
        # 添加VIDEO_SUBTITLE节
        config.add_section('VIDEO_SUBTITLE')
        
        # 设置默认值
        for key, value in default_values.items():
            config.set('VIDEO_SUBTITLE', key, value)
        
        logger.info("已添加默认VIDEO_SUBTITLE配置")
        
    except Exception as e:
        logger.error(f'添加默认VIDEO_SUBTITLE配置失败: {e}')

def load_default_subtitle_config():
    """
    从主配置文件加载默认的字幕配置
    
    返回:
        dict: 默认字幕配置字典
    """
    default_config = {
        'font': 'Arial',
        'size': '24',
        'color': 'white',
        'position': 'bottom-quarter',
        'horizontal_align': 'center',
        'stroke_color': 'black',
        'stroke_width': '2'
    }
    
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        if os.path.exists(config_path):
            main_config = configparser.ConfigParser(interpolation=None)
            main_config.read(config_path, encoding='utf-8')
            
            # 如果主配置文件中有VIDEO_SUBTITLE节，使用其中的值
            if main_config.has_section('VIDEO_SUBTITLE'):
                for key in default_config.keys():
                    if main_config.has_option('VIDEO_SUBTITLE', key):
                        default_config[key] = main_config.get('VIDEO_SUBTITLE', key)
                
                logger.info("已从主配置文件加载默认字幕配置")
            else:
                logger.info("主配置文件中未找到VIDEO_SUBTITLE节，使用内置默认值")
        else:
            logger.warning("主配置文件不存在，使用内置默认值")
            
    except Exception as e:
        logger.error(f'加载默认字幕配置失败，使用内置默认值: {e}')
    
    return default_config

def validate_json_completeness(content):
    """
    验证生成的内容是否为完整的JSON格式
    
    参数:
        content: 要验证的内容字符串
        
    返回:
        tuple: (is_valid, error_message, extracted_json)
    """
    import logging
    text_logger = logging.getLogger('text_generation')
    
    try:
        # 记录原始内容到日志
        text_logger.info(f"开始验证JSON内容，原始内容长度: {len(content)} 字符")
        text_logger.debug(f"原始内容: {content}")
        
        # 去除首尾空白字符
        content = content.strip()
        
        # 尝试从内容中提取JSON
        json_content = None
        extraction_method = ""
        
        # 方法1: 直接尝试解析整个内容
        try:
            json_content = content
            parsed_json = json.loads(json_content)
            extraction_method = "直接解析"
            text_logger.info(f"JSON提取成功 - 方法: {extraction_method}")
        except json.JSONDecodeError as e:
            text_logger.warning(f"直接解析失败: {str(e)}")
            
            # 方法2: 查找第一个{到最后一个}之间的内容
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_content = content[start_idx:end_idx + 1]
                try:
                    parsed_json = json.loads(json_content)
                    extraction_method = "大括号提取"
                    text_logger.info(f"JSON提取成功 - 方法: {extraction_method}，提取位置: {start_idx}-{end_idx}")
                except json.JSONDecodeError as e:
                    text_logger.warning(f"大括号提取失败: {str(e)}")
                    
                    # 方法3: 尝试查找```json代码块
                    import re
                    json_pattern = r'```json\s*([\s\S]*?)\s*```'
                    match = re.search(json_pattern, content, re.IGNORECASE)
                    if match:
                        json_content = match.group(1).strip()
                        try:
                            parsed_json = json.loads(json_content)
                            extraction_method = "代码块提取"
                            text_logger.info(f"JSON提取成功 - 方法: {extraction_method}")
                        except json.JSONDecodeError as e:
                            error_msg = f"代码块JSON解析失败: {str(e)}"
                            text_logger.error(error_msg)
                            text_logger.error(f"废弃的JSON内容: {json_content}")
                            return False, error_msg, None
                    else:
                        error_msg = "未找到有效的JSON格式内容"
                        text_logger.error(error_msg)
                        text_logger.error(f"废弃的原始内容: {content}")
                        return False, error_msg, None
            else:
                error_msg = "未找到JSON大括号"
                text_logger.error(error_msg)
                text_logger.error(f"废弃的原始内容: {content}")
                return False, error_msg, None
        
        # 检查必需的字段
        if not isinstance(parsed_json, dict):
            error_msg = "JSON根对象不是字典类型"
            text_logger.error(error_msg)
            text_logger.error(f"废弃的JSON内容: {json_content}")
            return False, error_msg, None
        
        if 'title' not in parsed_json:
            error_msg = "缺少必需字段：title"
            text_logger.error(error_msg)
            text_logger.error(f"废弃的JSON内容: {json_content}")
            text_logger.error(f"实际包含的字段: {list(parsed_json.keys())}")
            return False, error_msg, None
        
        if 'script' not in parsed_json:
            error_msg = "缺少必需字段：script"
            text_logger.error(error_msg)
            text_logger.error(f"废弃的JSON内容: {json_content}")
            text_logger.error(f"实际包含的字段: {list(parsed_json.keys())}")
            return False, error_msg, None
        
        if not isinstance(parsed_json['script'], list):
            error_msg = "script字段不是数组类型"
            text_logger.error(error_msg)
            text_logger.error(f"废弃的JSON内容: {json_content}")
            text_logger.error(f"script字段类型: {type(parsed_json['script'])}")
            return False, error_msg, None
        
        # 检查script数组中的每个元素
        for i, item in enumerate(parsed_json['script']):
            if not isinstance(item, dict):
                error_msg = f"script数组第{i+1}个元素不是对象类型"
                text_logger.error(error_msg)
                text_logger.error(f"废弃的JSON内容: {json_content}")
                text_logger.error(f"第{i+1}个元素类型: {type(item)}，内容: {item}")
                return False, error_msg, None
            
            if 'id' not in item:
                error_msg = f"script数组第{i+1}个元素缺少id字段"
                text_logger.error(error_msg)
                text_logger.error(f"废弃的JSON内容: {json_content}")
                text_logger.error(f"第{i+1}个元素包含的字段: {list(item.keys())}")
                return False, error_msg, None
            
            if 'text' not in item:
                error_msg = f"script数组第{i+1}个元素缺少text字段"
                text_logger.error(error_msg)
                text_logger.error(f"废弃的JSON内容: {json_content}")
                text_logger.error(f"第{i+1}个元素包含的字段: {list(item.keys())}")
                return False, error_msg, None
            
            if not isinstance(item['id'], (int, float)):
                error_msg = f"script数组第{i+1}个元素的id不是数字类型"
                text_logger.error(error_msg)
                text_logger.error(f"废弃的JSON内容: {json_content}")
                text_logger.error(f"第{i+1}个元素id类型: {type(item['id'])}，值: {item['id']}")
                return False, error_msg, None
            
            if not isinstance(item['text'], str):
                error_msg = f"script数组第{i+1}个元素的text不是字符串类型"
                text_logger.error(error_msg)
                text_logger.error(f"废弃的JSON内容: {json_content}")
                text_logger.error(f"第{i+1}个元素text类型: {type(item['text'])}，值: {item['text']}")
                return False, error_msg, None
        
        text_logger.info(f"JSON格式验证通过 - 提取方法: {extraction_method}，包含{len(parsed_json['script'])}个脚本段落")
        return True, "JSON格式验证通过", json_content
        
    except json.JSONDecodeError as e:
        error_msg = f"JSON解析错误: {str(e)}"
        text_logger.error(error_msg)
        text_logger.error(f"废弃的内容: {content}")
        # 尝试定位错误位置
        if hasattr(e, 'lineno') and hasattr(e, 'colno'):
            text_logger.error(f"错误位置: 第{e.lineno}行，第{e.colno}列")
            # 显示错误行的内容
            lines = content.split('\n')
            if e.lineno <= len(lines):
                error_line = lines[e.lineno - 1]
                text_logger.error(f"错误行内容: {error_line}")
                if e.colno <= len(error_line):
                    text_logger.error(f"错误字符: '{error_line[e.colno-1] if e.colno > 0 else ''}' (位置{e.colno})")
        return False, error_msg, None
    except Exception as e:
        error_msg = f"验证过程中发生错误: {str(e)}"
        text_logger.error(error_msg)
        text_logger.error(f"废弃的内容: {content}")
        return False, error_msg, None

def get_baidu_censor_config():
    """
    从config.ini获取百度云内容审核配置
    
    返回:
        dict: 百度云内容审核配置信息，如果没有找到则返回None
    """
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        if not os.path.exists(config_path):
            return None
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 获取百度云内容审核配置
        if not config.has_section('BAIDU_CONTENT_CENSOR'):
            return None
        
        censor_config = dict(config['BAIDU_CONTENT_CENSOR'])
        return censor_config
        
    except Exception as e:
        logger.error(f"获取百度云内容审核配置时发生错误: {str(e)}")
        return None

def get_baidu_access_token(api_key, secret_key):
    """
    获取百度云API的access_token
    
    参数:
        api_key: 百度云API Key
        secret_key: 百度云Secret Key
        
    返回:
        tuple: (access_token, expires_in) 或 (None, None)
    """
    import requests
    
    try:
        url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': api_key,
            'client_secret': secret_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'access_token' in result:
                return result['access_token'], result.get('expires_in', 2592000)  # 默认30天
            else:
                logger.error(f"获取access_token失败: {result}")
                return None, None
        else:
            logger.error(f"请求access_token失败，状态码: {response.status_code}")
            return None, None
            
    except Exception as e:
        logger.error(f"获取百度云access_token时发生错误: {str(e)}")
        return None, None

def update_baidu_access_token_in_config(access_token, expires_in):
    """
    更新config.ini中的百度云access_token和过期时间
    
    参数:
        access_token: 新的access_token
        expires_in: 有效期（秒）
    """
    try:
        from datetime import datetime, timedelta
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        config = configparser.ConfigParser(interpolation=None)
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        if not config.has_section('BAIDU_CONTENT_CENSOR'):
            config.add_section('BAIDU_CONTENT_CENSOR')
        
        # 计算过期时间
        expire_time = datetime.now() + timedelta(seconds=expires_in)
        expire_time_str = expire_time.strftime('%Y-%m-%d %H:%M:%S')
        
        config['BAIDU_CONTENT_CENSOR']['access_token'] = access_token
        config['BAIDU_CONTENT_CENSOR']['access_token_expires'] = expire_time_str
        
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
            
    except Exception as e:
        logger.error(f"更新百度云access_token配置时发生错误: {str(e)}")

def check_baidu_access_token_validity(censor_config):
    """
    检查百度云access_token是否有效
    
    参数:
        censor_config: 百度云内容审核配置
        
    返回:
        bool: True表示有效，False表示无效或即将过期
    """
    try:
        from datetime import datetime
        
        if not censor_config or 'access_token_expires' not in censor_config:
            return False
        
        expire_time_str = censor_config['access_token_expires']
        expire_time = datetime.strptime(expire_time_str, '%Y-%m-%d %H:%M:%S')
        
        # 如果距离过期时间少于1小时，认为需要刷新
        current_time = datetime.now()
        time_diff = expire_time - current_time
        
        return time_diff.total_seconds() > 3600  # 大于1小时才认为有效
        
    except Exception as e:
        logger.error(f"检查百度云access_token有效性时发生错误: {str(e)}")
        return False

def get_valid_baidu_access_token():
    """
    获取有效的百度云access_token，如果过期则自动刷新
    
    返回:
        str: 有效的access_token，如果获取失败则返回None
    """
    censor_config = get_baidu_censor_config()
    
    if not censor_config:
        logger.warning("未找到百度云内容审核配置")
        return None
    
    # 检查当前token是否有效
    if check_baidu_access_token_validity(censor_config) and 'access_token' in censor_config:
        return censor_config['access_token']
    
    # token无效或不存在，重新获取
    api_key = censor_config.get('api_key')
    secret_key = censor_config.get('secret_key')
    
    if not api_key or not secret_key:
        logger.warning("百度云API Key或Secret Key未配置")
        return None
    
    access_token, expires_in = get_baidu_access_token(api_key, secret_key)
    
    if access_token:
        # 更新配置文件
        update_baidu_access_token_in_config(access_token, expires_in)
        return access_token
    
    return None

def baidu_text_censor(text):
    """
    使用百度云API进行文本内容审核
    
    参数:
        text: 要审核的文本内容
        
    返回:
        tuple: (is_pass, conclusion_type, conclusion, error_message)
               is_pass: 是否通过审核
               conclusion_type: 审核结果类型 (1:合规, 2:不合规, 3:疑似, 4:审核失败)
               conclusion: 审核结论
               error_message: 错误信息（如果有）
    """
    import requests
    from urllib.parse import urlencode
    import logging
    
    text_logger = logging.getLogger('text_generation')
    
    try:
        # 获取配置
        censor_config = get_baidu_censor_config()
        if not censor_config:
            return False, 4, "审核失败", "未找到百度云内容审核配置"
        
        # 检查是否启用内容审核
        if censor_config.get('enable_content_censor', 'true').lower() != 'true':
            text_logger.info("内容审核功能已禁用，跳过审核")
            return True, 1, "合规", None
        
        # 获取有效的access_token
        access_token = get_valid_baidu_access_token()
        if not access_token:
            return False, 4, "审核失败", "无法获取有效的access_token"
        
        # 构建请求URL
        url = f"https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined?access_token={access_token}"
        
        # 构建请求参数
        params = {'text': text}
        
        # 添加策略ID（如果配置了）
        strategy_id = censor_config.get('strategy_id')
        if strategy_id and strategy_id.strip():
            params['strategyId'] = strategy_id.strip()
        
        # 发送请求
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = urlencode(params)
        
        text_logger.info(f"开始百度云文本内容审核，文本长度: {len(text)} 字符")
        
        response = requests.post(url, data=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            text_logger.debug(f"百度云审核API响应: {result}")
            
            conclusion_type = result.get('conclusionType', 4)
            conclusion = result.get('conclusion', '审核失败')
            
            # 1:合规, 2:不合规, 3:疑似, 4:审核失败
            is_pass = conclusion_type == 1
            
            if conclusion_type == 2:
                # 不合规，记录详细信息
                data_info = result.get('data', [])
                violation_details = []
                for item in data_info:
                    if 'msg' in item:
                        violation_details.append(item['msg'])
                
                error_msg = f"内容审核不通过: {', '.join(violation_details) if violation_details else conclusion}"
                text_logger.warning(f"百度云审核不通过: {error_msg}")
                return False, conclusion_type, conclusion, error_msg
            
            elif conclusion_type == 3:
                # 疑似违规
                text_logger.warning(f"百度云审核疑似违规: {conclusion}")
                return False, conclusion_type, conclusion, f"内容疑似违规: {conclusion}"
            
            elif conclusion_type == 1:
                # 合规
                text_logger.info(f"百度云审核通过: {conclusion}")
                return True, conclusion_type, conclusion, None
            
            else:
                # 审核失败
                text_logger.error(f"百度云审核失败: {conclusion}")
                return False, conclusion_type, conclusion, f"审核失败: {conclusion}"
        
        else:
            error_msg = f"百度云API请求失败，状态码: {response.status_code}, 响应: {response.text}"
            text_logger.error(error_msg)
            return False, 4, "审核失败", error_msg
            
    except Exception as e:
        error_msg = f"百度云文本审核时发生错误: {str(e)}"
        text_logger.error(error_msg)
        return False, 4, "审核失败", error_msg

def get_active_api_config():
    """
    从config.ini文件获取当前激活的API配置
    
    返回:
        dict: 激活的API配置，如果未找到则返回None
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        if not os.path.exists(config_path):
            return None
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 获取激活的API ID
        if not (config.has_section('MAIN_MODEL') and config.has_option('MAIN_MODEL', 'active_api')):
            return None
        
        active_api_id = config.get('MAIN_MODEL', 'active_api')
        
        # 获取对应的API配置
        if not config.has_section(active_api_id):
            return None
        
        api_config = {
            'api_id': active_api_id,
            'name': config.get(active_api_id, 'name', fallback=''),
            'api_url': config.get(active_api_id, 'api_url', fallback=''),
            'api_key': config.get(active_api_id, 'api_key', fallback=''),
            'selected_model': config.get(active_api_id, 'selected_model', fallback='gpt-3.5-turbo')
        }
        
        return api_config
        
    except Exception as e:
        logger.error(f'获取激活API配置时发生错误: {str(e)}')
        return None

@csrf_exempt
@require_http_methods(["GET"])
def load_prompt_list(request):
    """
    加载PROMPT文件列表的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含PROMPT文件列表的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_dir = os.path.join(project_root, 'common', 'text_gen')
        
        # 检查prompt目录是否存在
        if not os.path.exists(prompt_dir):
            return JsonResponse({
                'success': False,
                'error': 'prompt目录不存在'
            })
        
        # 获取所有.txt文件
        prompt_files = []
        for filename in os.listdir(prompt_dir):
            if filename.endswith('.txt'):
                name = filename[:-4]  # 去掉.txt后缀
                prompt_files.append({
                    'name': name,
                    'filename': filename
                })
        
        # 按文件名排序
        prompt_files.sort(key=lambda x: x['name'])
        
        logger.info(f'已加载{len(prompt_files)}个PROMPT文件')
        
        return JsonResponse({
            'success': True,
            'prompts': prompt_files
        })
        
    except Exception as e:
        logger.error(f'加载PROMPT列表时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载PROMPT列表时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def load_prompt_content(request):
    """
    加载指定PROMPT文件内容的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename参数
        
    返回:
        JsonResponse: 包含PROMPT文件内容的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        filename = data.get('filename', '')
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '缺少文件名参数'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 确保文件名有.txt扩展名
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
            
        prompt_path = os.path.join(project_root, 'common', 'text_gen', filename)
        
        # 检查文件是否存在
        if not os.path.exists(prompt_path):
            return JsonResponse({
                'success': False,
                'error': f'PROMPT文件不存在: {filename}'
            })
        
        # 读取文件内容
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新config.ini中的active_prompt_file
        config_path = os.path.join(project_root, 'config.ini')
        if os.path.exists(config_path):
            config = configparser.ConfigParser(interpolation=None)
            config.read(config_path, encoding='utf-8')
            
            # 确保PROMPT_CONFIG部分存在
            if not config.has_section('PROMPT_CONFIG'):
                config.add_section('PROMPT_CONFIG')
            
            # 更新active_prompt_file字段
            config.set('PROMPT_CONFIG', 'active_prompt_file', filename)
            
            # 提取文件名（不含扩展名）作为active_prompt_name
            prompt_name = os.path.splitext(filename)[0]
            config.set('PROMPT_CONFIG', 'active_prompt_name', prompt_name)
            
            # 保存配置文件
            with open(config_path, 'w', encoding='utf-8') as config_file:
                config.write(config_file)
            
            logger.info(f'已更新配置文件中的active_prompt_file: {filename}')
        
        logger.info(f'已加载PROMPT文件: {filename}')
        
        return JsonResponse({
            'success': True,
            'content': content,
            'filename': filename
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'加载PROMPT内容时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载PROMPT内容时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_prompt(request):
    """
    保存PROMPT到文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename和content参数
        
    返回:
        JsonResponse: 包含保存结果的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        filename = data.get('filename', '').strip()
        content = data.get('content', '')
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '文件名不能为空'
            })
        
        if not content:
            return JsonResponse({
                'success': False,
                'error': 'PROMPT内容不能为空'
            })
        
        # 确保文件名安全（移除危险字符）
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        if not safe_filename.endswith('.txt'):
            safe_filename += '.txt'
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_dir = os.path.join(project_root, 'common', 'text_gen')
        
        # 确保prompt目录存在
        os.makedirs(prompt_dir, exist_ok=True)
        
        prompt_path = os.path.join(prompt_dir, safe_filename)
        
        # 写入文件
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f'已保存PROMPT文件: {safe_filename}')
        
        return JsonResponse({
            'success': True,
            'message': f'PROMPT已成功保存为: {safe_filename}',
            'filename': safe_filename
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'保存PROMPT时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存PROMPT时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_format_prompt_list(request):
    """
    加载格式化PROMPT文件列表的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含格式化PROMPT文件列表的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        format_prompt_dir = os.path.join(project_root, 'common', 'text_fmt')
        
        # 检查text_fmt目录是否存在
        if not os.path.exists(format_prompt_dir):
            return JsonResponse({
                'success': False,
                'error': 'text_fmt目录不存在'
            })
        
        # 获取所有.txt文件
        prompt_files = []
        for filename in os.listdir(format_prompt_dir):
            if filename.endswith('.txt'):
                name = filename[:-4]  # 去掉.txt后缀
                prompt_files.append({
                    'name': name,
                    'filename': filename
                })
        
        # 按文件名排序
        prompt_files.sort(key=lambda x: x['name'])
        
        logger.info(f'已加载{len(prompt_files)}个格式化PROMPT文件')
        
        return JsonResponse({
            'success': True,
            'prompts': prompt_files
        })
        
    except Exception as e:
        logger.error(f'加载格式化PROMPT列表时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载格式化PROMPT列表时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def load_format_prompt_content(request):
    """
    加载指定格式化PROMPT文件内容的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename参数
        
    返回:
        JsonResponse: 包含格式化PROMPT文件内容的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        filename = data.get('filename', '')
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '缺少文件名参数'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 确保文件名有.txt扩展名
        if not filename.endswith('.txt'):
            filename = filename + '.txt'
            
        format_prompt_path = os.path.join(project_root, 'common', 'text_fmt', filename)
        
        # 检查文件是否存在
        if not os.path.exists(format_prompt_path):
            return JsonResponse({
                'success': False,
                'error': f'格式化PROMPT文件不存在: {filename}'
            })
        
        # 读取文件内容
        with open(format_prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f'已加载格式化PROMPT文件: {filename}')
        
        return JsonResponse({
            'success': True,
            'content': content,
            'filename': filename
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'加载格式化PROMPT内容时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载格式化PROMPT内容时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_format_prompt(request):
    """
    保存格式化PROMPT到文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename和content参数
        
    返回:
        JsonResponse: 包含保存结果的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        filename = data.get('filename', '').strip()
        content = data.get('content', '')
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '文件名不能为空'
            })
        
        if not content:
            return JsonResponse({
                'success': False,
                'error': '格式化PROMPT内容不能为空'
            })
        
        # 确保文件名安全（移除危险字符）
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        if not safe_filename.endswith('.txt'):
            safe_filename += '.txt'
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        format_prompt_dir = os.path.join(project_root, 'common', 'text_fmt')
        
        # 确保text_fmt目录存在
        os.makedirs(format_prompt_dir, exist_ok=True)
        
        format_prompt_path = os.path.join(format_prompt_dir, safe_filename)
        
        # 写入文件
        with open(format_prompt_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f'已保存格式化PROMPT文件: {safe_filename}')
        
        return JsonResponse({
            'success': True,
            'message': f'格式化PROMPT已成功保存为: {safe_filename}',
            'filename': safe_filename
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'保存格式化PROMPT时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存格式化PROMPT时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def delete_format_prompt(request):
    """
    删除格式化PROMPT文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename参数
        
    返回:
        JsonResponse: 包含删除结果的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        filename = data.get('filename', '')
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '缺少文件名参数'
            })
        
        # 确保文件名有.txt扩展名
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        format_prompt_path = os.path.join(project_root, 'common', 'text_fmt', filename)
        
        # 检查文件是否存在
        if not os.path.exists(format_prompt_path):
            return JsonResponse({
                'success': False,
                'error': f'格式化PROMPT文件不存在: {filename}'
            })
        
        # 删除文件
        os.remove(format_prompt_path)
        
        logger.info(f'已删除格式化PROMPT文件: {filename}')
        
        return JsonResponse({
            'success': True,
            'message': f'格式化PROMPT文件已删除: {filename}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'删除格式化PROMPT时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'删除格式化PROMPT时发生错误: {str(e)}'
        })

@csrf_exempt
def format_text(request):
    if request.method == 'POST':
        try:
            import requests  # 导入requests模块
            import logging  # 导入logging模块
            
            data = json.loads(request.body)
            format_prompt = data.get('prompt', '').strip()
            
            if not format_prompt:
                return JsonResponse({'success': False, 'error': '格式化提示词不能为空'})
            
            # 获取当前项目路径
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            current_project_path = config.get('PROJECT_CONFIG', 'current_project_path', fallback='')
            
            if not current_project_path:
                return JsonResponse({'success': False, 'error': '未找到当前项目路径'})
            
            # 读取当前项目的 parameter.ini 文件中的 PAPER_CONTENT
            parameter_ini_path = os.path.join(current_project_path, 'parameter.ini')
            if not os.path.exists(parameter_ini_path):
                return JsonResponse({'success': False, 'error': f'未找到项目配置文件: {parameter_ini_path}'})
            
            project_config = configparser.ConfigParser()
            project_config.read(parameter_ini_path, encoding='utf-8')
            
            # 读取 PAPER_CONTENT 部分
            paper_content_lines = []
            if project_config.has_section('PAPER_CONTENT'):
                for key in project_config.options('PAPER_CONTENT'):
                    if key.startswith('line_'):
                        paper_content_lines.append(project_config.get('PAPER_CONTENT', key))
            
            if not paper_content_lines:
                return JsonResponse({'success': False, 'error': '项目中未找到文案内容'})
            
            # 组合完整的内容
            paper_content = '\n'.join(paper_content_lines)
            
            # 构建完整的 PROMPT（格式化提示词 + 文案内容）
            full_prompt = f"{format_prompt}\n\n文案内容：\n{paper_content}"
            
            # 记录调试信息
            format_logger = logging.getLogger('format_text')
            format_logger.info(f"开始格式化文案")
            format_logger.info(f"格式化提示词长度: {len(format_prompt)} 字符")
            format_logger.info(f"文案内容长度: {len(paper_content)} 字符")
            format_logger.info(f"完整PROMPT长度: {len(full_prompt)} 字符")
            format_logger.info(f"完整PROMPT内容: {full_prompt}")
            
            # 获取活跃的API配置
            active_api_config = get_active_api_config()
            if not active_api_config:
                return JsonResponse({'success': False, 'error': '未找到活跃的API配置'})
            
            api_url = active_api_config['api_url']
            api_key = active_api_config['api_key']
            model = active_api_config['selected_model']
            
            # 构建API请求
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': [
                    {
                        'role': 'user',
                        'content': full_prompt
                    }
                ],
                'temperature': 0.7
            }
            
            # 发送API请求
            response = requests.post(f"{api_url}/chat/completions", headers=headers, json=payload, timeout=500)
            
            if response.status_code == 200:
                result = response.json()
                raw_content = result['choices'][0]['message']['content'].strip()
                
                # 添加返回内容的调试日志
                format_logger.info(f"AI返回原始内容长度: {len(raw_content)} 字符")
                format_logger.info(f"AI返回原始内容: {raw_content}")
                
                # 尝试提取JSON内容
                extracted_json = None
                extraction_method = ""
                
                # 方法1: 直接尝试解析整个内容
                try:
                    json.loads(raw_content)
                    extracted_json = raw_content
                    extraction_method = "直接解析"
                    format_logger.info(f"JSON提取成功 - 方法: {extraction_method}")
                except json.JSONDecodeError:
                    format_logger.info("直接解析失败，尝试其他方法")
                    
                    # 方法2: 查找第一个{到最后一个}之间的内容
                    start_idx = raw_content.find('{')
                    end_idx = raw_content.rfind('}')
                    
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        bracket_content = raw_content[start_idx:end_idx + 1]
                        try:
                            json.loads(bracket_content)
                            extracted_json = bracket_content
                            extraction_method = "大括号提取"
                            format_logger.info(f"JSON提取成功 - 方法: {extraction_method}，提取位置: {start_idx}-{end_idx}")
                        except json.JSONDecodeError:
                            format_logger.info("大括号提取失败，尝试代码块提取")
                            
                            # 方法3: 尝试查找```json代码块
                            import re
                            json_pattern = r'```json\s*([\s\S]*?)\s*```'
                            match = re.search(json_pattern, raw_content, re.IGNORECASE)
                            if match:
                                code_block_content = match.group(1).strip()
                                try:
                                    json.loads(code_block_content)
                                    extracted_json = code_block_content
                                    extraction_method = "代码块提取"
                                    format_logger.info(f"JSON提取成功 - 方法: {extraction_method}")
                                except json.JSONDecodeError:
                                    format_logger.warning("代码块JSON解析失败")
                            else:
                                format_logger.warning("未找到```json代码块")
                
                # 使用提取的JSON或原始内容
                if extracted_json:
                    formatted_content = extracted_json
                    format_logger.info(f"使用提取的JSON内容，长度: {len(formatted_content)} 字符")
                    
                    # 将JSON内容保存到当前项目的 paper.json 文件
                    paper_json_path = os.path.join(current_project_path, 'paper.json')
                    try:
                        # 验证JSON格式
                        json_data = json.loads(formatted_content)
                        
                        # 保存到文件
                        with open(paper_json_path, 'w', encoding='utf-8') as f:
                            json.dump(json_data, f, ensure_ascii=False, indent=2)
                        
                        format_logger.info(f"JSON内容已保存到: {paper_json_path}")
                        logger.info('文案格式化成功，已保存到 paper.json')
                        
                        return JsonResponse({
                            'success': True,
                            'message': '文案格式化成功，已保存到 paper.json'
                        })
                        
                    except json.JSONDecodeError as e:
                        format_logger.error(f"JSON格式验证失败: {e}")
                        return JsonResponse({'success': False, 'error': f'返回的内容不是有效的JSON格式: {e}'})
                    except Exception as e:
                        format_logger.error(f"保存JSON文件失败: {e}")
                        return JsonResponse({'success': False, 'error': f'保存文件失败: {e}'})
                else:
                    format_logger.warning("未能提取有效JSON，格式化失败")
                    return JsonResponse({'success': False, 'error': '未能从AI返回内容中提取有效的JSON格式'})
            else:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                format_logger.error(error_msg)
                return JsonResponse({'success': False, 'error': error_msg})
                
        except Exception as e:
            error_msg = f"格式化文案时发生错误: {str(e)}"
            format_logger = logging.getLogger('format_text')
            format_logger.error(error_msg)
            logger.error(error_msg)
            return JsonResponse({'success': False, 'error': error_msg})
    
    return JsonResponse({'success': False, 'error': '仅支持POST请求'})

@csrf_exempt
@require_http_methods(["GET"])
def load_paper_json(request):
    """
    加载当前项目的paper.json文件内容
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含paper.json内容的JSON响应
    """
    try:
        # 获取当前项目路径
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        current_project_path = config.get('PROJECT_CONFIG', 'current_project_path', fallback='')
        
        if not current_project_path:
            return JsonResponse({
                'success': False,
                'error': '未找到当前项目路径'
            })
        
        # 构建paper.json文件路径
        paper_json_path = os.path.join(current_project_path, 'paper.json')
        
        # 检查文件是否存在
        if not os.path.exists(paper_json_path):
            return JsonResponse({
                'success': True,
                'content': ''
            })
        
        # 读取paper.json文件
        with open(paper_json_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        logger.error(f'加载paper.json时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载paper.json时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_formatted_content(request):
    """
    加载当前项目的paper.json文件中的formatted_content字段
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含formatted_content的JSON响应
    """
    try:
        # 获取当前项目路径
        current_project_path = get_current_project_path()
        if not current_project_path:
            return JsonResponse({
                'success': False,
                'error': '未找到当前项目路径，请先打开一个项目'
            })
        
        # 构建paper.json文件路径
        paper_file_path = os.path.join(current_project_path, 'paper.json')
        
        # 检查文件是否存在
        if not os.path.exists(paper_file_path):
            return JsonResponse({
                'success': True,
                'content': ''
            })
        
        # 读取paper.json文件
        with open(paper_file_path, 'r', encoding='utf-8') as f:
            paper_data = json.load(f)
        
        # 获取formatted_content字段
        formatted_content = paper_data.get('formatted_content', '')
        
        return JsonResponse({
            'success': True,
            'content': formatted_content
        })
        
    except json.JSONDecodeError as e:
        logger.error(f'解析paper.json文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'paper.json文件格式错误: {str(e)}'
        })
    except Exception as e:
        logger.error(f'加载formatted_content时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载格式化文案时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_paper_content_from_ini(request):
    """
    从parameter.ini文件读取[PAPER_CONTENT]内容的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含文案内容的JSON响应
    """
    try:
        # 获取当前项目路径
        project_path = request.GET.get('project_path')  # 优先使用请求参数中的项目路径
        if not project_path:
            project_path = get_current_project_path()  # 如果没有传递项目路径，使用当前项目路径
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '无法获取当前项目路径'
            })
        
        # parameter.ini文件路径
        parameter_ini_path = os.path.join(project_path, 'parameter.ini')
        
        # 检查parameter.ini文件是否存在
        if not os.path.exists(parameter_ini_path):
            return JsonResponse({
                'success': True,
                'content': ''
            })
        
        # 读取parameter.ini文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(parameter_ini_path, encoding='utf-8')
        
        # 检查[PAPER_CONTENT]节是否存在
        if not config.has_section('PAPER_CONTENT'):
            return JsonResponse({
                'success': True,
                'content': ''
            })
        
        # 获取[PAPER_CONTENT]中的所有内容
        paper_content_items = config.items('PAPER_CONTENT')
        
        if not paper_content_items:
            return JsonResponse({
                'success': True,
                'content': ''
            })
        
        # 提取文案内容（去掉line_1 = 等前缀）
        content_lines = []
        for key, value in paper_content_items:
            if key.startswith('line_') and value.strip():
                content_lines.append(value.strip())
        
        # 将文案内容合并为一个字符串
        content = '\n'.join(content_lines)
        
        logger.info(f'已从parameter.ini加载文案内容，共{len(content_lines)}行')
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        logger.error(f'从parameter.ini加载文案内容时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载文案内容时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_default_format_prompt(request):
    """
    加载默认格式化PROMPT的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含默认格式化PROMPT内容的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 默认格式化PROMPT文件路径
        default_format_prompt_path = None
        
        # 尝试从配置文件读取格式化PROMPT路径
        if os.path.exists(config_path):
            config = configparser.ConfigParser(interpolation=None)
            config.read(config_path, encoding='utf-8')
            
            # 检查是否有FORMAT_PROMPT_CONFIG节
            if config.has_section('FORMAT_PROMPT_CONFIG'):
                if config.has_option('FORMAT_PROMPT_CONFIG', 'active_format_prompt_file'):
                    active_format_prompt_file = config.get('FORMAT_PROMPT_CONFIG', 'active_format_prompt_file').strip()
                    if active_format_prompt_file:  # 如果active_format_prompt_file不为空
                        default_format_prompt_path = os.path.join(project_root, 'common', 'text_fmt', active_format_prompt_file)
        
        # 如果配置文件中没有指定，使用默认文件
        if not default_format_prompt_path:
            # 尝试找到第一个格式化PROMPT文件
            format_prompt_dir = os.path.join(project_root, 'common', 'text_fmt')
            if os.path.exists(format_prompt_dir):
                format_prompt_files = [f for f in os.listdir(format_prompt_dir) if f.endswith('.txt')]
                if format_prompt_files:
                    default_format_prompt_path = os.path.join(format_prompt_dir, format_prompt_files[0])
        
        # 如果找到了默认文件，读取内容
        if default_format_prompt_path and os.path.exists(default_format_prompt_path):
            with open(default_format_prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取文件名（不包含路径）
            filename = os.path.basename(default_format_prompt_path)
            
            logger.info(f'已加载默认格式化PROMPT: {default_format_prompt_path}')
            
            return JsonResponse({
                'success': True,
                'content': content,
                'filename': filename
            })
        else:
            return JsonResponse({
                'success': True,
                'content': ''
            })
        
    except Exception as e:
        logger.error(f'加载默认格式化PROMPT时发生错误: {str(e)}')
        return JsonResponse({
             'success': False,
             'error': f'加载默认格式化PROMPT时发生错误: {str(e)}'
         })

@csrf_exempt
@require_http_methods(["POST"])
def save_format_prompt_to_config(request):
    """
    保存格式化PROMPT文件名到config.ini的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename参数
        
    返回:
        JsonResponse: 保存结果的JSON响应
    """
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '').strip()
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '文件名不能为空'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 读取或创建配置文件
        config = configparser.ConfigParser(interpolation=None)
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        # 确保FORMAT_PROMPT_CONFIG节存在
        if not config.has_section('FORMAT_PROMPT_CONFIG'):
            config.add_section('FORMAT_PROMPT_CONFIG')
        
        # 设置active_format_prompt_file
        config.set('FORMAT_PROMPT_CONFIG', 'active_format_prompt_file', filename)
        
        # 保存配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
        logger.info(f'已保存格式化PROMPT文件名到config.ini: {filename}')
        
        return JsonResponse({
            'success': True,
            'message': f'已保存格式化PROMPT配置: {filename}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f'保存格式化PROMPT配置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存配置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_default_prompt(request):
    """
    加载默认PROMPT的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含默认PROMPT内容的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 默认PROMPT文件路径
        default_prompt_path = None
        
        # 尝试从配置文件读取PROMPT路径
        if os.path.exists(config_path):
            config = configparser.ConfigParser(interpolation=None)
            config.read(config_path, encoding='utf-8')
            
            # 优先使用active_prompt_file，如果没有则使用default_prompt_file
            if config.has_section('PROMPT_CONFIG'):
                if config.has_option('PROMPT_CONFIG', 'active_prompt_file'):
                    active_prompt_file = config.get('PROMPT_CONFIG', 'active_prompt_file').strip()
                    if active_prompt_file:  # 如果active_prompt_file不为空
                        default_prompt_path = os.path.join(project_root, 'common', 'text_gen', active_prompt_file)
                elif config.has_option('PROMPT_CONFIG', 'default_prompt_file'):
                    default_prompt_path = config.get('PROMPT_CONFIG', 'default_prompt_file')
        
        # 如果配置文件中没有指定，使用默认文件
        if not default_prompt_path:
            default_prompt_path = os.path.join(project_root, 'common', 'text_gen', '默认AI短视频策略师.txt')
        
        # 检查文件是否存在
        if not os.path.exists(default_prompt_path):
            return JsonResponse({
                'success': False,
                'error': '默认PROMPT文件不存在'
            })
        
        # 读取文件内容
        with open(default_prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f'已加载默认PROMPT: {default_prompt_path}')
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        logger.error(f'加载默认PROMPT时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载默认PROMPT时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def delete_prompt(request):
    """
    删除PROMPT文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename参数
        
    返回:
        JsonResponse: 包含删除结果的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        filename = data.get('filename', '').strip()
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '缺少文件名参数'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(project_root, 'common', 'text_gen', filename)
        
        # 检查文件是否存在
        if not os.path.exists(prompt_path):
            return JsonResponse({
                'success': False,
                'error': f'PROMPT文件不存在: {filename}'
            })
        
        # 安全检查：确保文件在prompt目录内
        prompt_dir = os.path.join(project_root, 'common', 'text_gen')
        if not os.path.commonpath([prompt_path, prompt_dir]) == prompt_dir:
            return JsonResponse({
                'success': False,
                'error': '无效的文件路径'
            })
        
        # 删除文件
        os.remove(prompt_path)
        
        logger.info(f'已删除PROMPT文件: {filename}')
        
        return JsonResponse({
            'success': True,
            'message': f'PROMPT文件已删除: {filename}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'删除PROMPT时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'删除PROMPT时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_prompt_to_config(request):
    """
    保存PROMPT文件名到config.ini的API端点
    
    参数:
        request: Django的HttpRequest对象，包含filename参数
        
    返回:
        JsonResponse: 保存结果的JSON响应
    """
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '').strip()
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '文件名不能为空'
            })
        
        # 确保文件名有.txt扩展名
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 读取或创建配置文件
        config = configparser.ConfigParser(interpolation=None)
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        # 确保PROMPT_CONFIG节存在
        if not config.has_section('PROMPT_CONFIG'):
            config.add_section('PROMPT_CONFIG')
        
        # 设置active_prompt_file
        config.set('PROMPT_CONFIG', 'active_prompt_file', filename)
        
        # 保存配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
        logger.info(f'已保存PROMPT文件名到config.ini: {filename}')
        
        return JsonResponse({
            'success': True,
            'message': f'已保存PROMPT配置: {filename}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f'保存PROMPT配置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存配置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def convert_ini_to_paper_json(request):
    """
    将parameter.ini文件的[PAPER_CONTENT]内容转换为paper.json的sentences格式
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含转换结果的JSON响应
    """
    try:
        # 获取当前项目路径
        project_path = get_current_project_path()
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '无法获取当前项目路径'
            })
        
        # parameter.ini文件路径
        parameter_ini_path = os.path.join(project_path, 'parameter.ini')
        
        # 检查parameter.ini文件是否存在
        if not os.path.exists(parameter_ini_path):
            return JsonResponse({
                'success': False,
                'error': 'parameter.ini文件不存在，请先生成文案'
            })
        
        # 读取parameter.ini文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(parameter_ini_path, encoding='utf-8')
        
        # 检查[PAPER_CONTENT]节是否存在
        if not config.has_section('PAPER_CONTENT'):
            return JsonResponse({
                'success': False,
                'error': '请先生成文案'
            })
        
        # 获取[PAPER_CONTENT]中的所有内容
        paper_content_items = config.items('PAPER_CONTENT')
        
        if not paper_content_items:
            return JsonResponse({
                'success': False,
                'error': '请先生成文案'
            })
        
        # 提取文案内容并创建sentences数组
        sentences = []
        for key, value in paper_content_items:
            if key.startswith('line_') and value.strip():
                # 提取行号作为ID
                line_num = key.replace('line_', '')
                try:
                    sentence_id = int(line_num)
                except ValueError:
                    sentence_id = len(sentences) + 1
                
                sentences.append({
                    'id': sentence_id,
                    'text': value.strip()
                })
        
        if not sentences:
            return JsonResponse({
                'success': False,
                'error': '请先生成文案'
            })
        
        # 创建paper.json数据结构
        paper_data = {
            'sentences': sentences,
            'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_sentences': len(sentences),
            'source': 'parameter.ini'
        }
        
        # 保存到paper.json文件
        paper_json_path = os.path.join(project_path, 'paper.json')
        
        try:
            with open(paper_json_path, 'w', encoding='utf-8') as f:
                json.dump(paper_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已将parameter.ini内容转换为paper.json格式，共{len(sentences)}个句子")
            
            return JsonResponse({
                'success': True,
                'message': f'成功转换{len(sentences)}个句子到paper.json格式',
                'sentences_count': len(sentences)
            })
            
        except Exception as save_error:
            logger.error(f"保存paper.json文件时发生错误: {str(save_error)}")
            return JsonResponse({
                'success': False,
                'error': f'保存文件时发生错误: {str(save_error)}'
            })
        
    except Exception as e:
        logger.error(f'转换parameter.ini到paper.json时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'转换失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def format_text_from_ini(request):
    """
    从parameter.ini文件读取[PAPER_CONTENT]内容进行格式化的API端点
    
    参数:
        request: Django的HttpRequest对象，包含prompt参数
        
    返回:
        JsonResponse: 包含格式化结果的JSON响应
    """
    import requests
    text_logger = logging.getLogger('text_generation')
    
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': '缺少格式化PROMPT参数'
            })
        
        # 获取当前项目路径
        project_path = get_current_project_path()
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '无法获取当前项目路径'
            })
        
        # parameter.ini文件路径
        parameter_ini_path = os.path.join(project_path, 'parameter.ini')
        
        # 检查parameter.ini文件是否存在
        if not os.path.exists(parameter_ini_path):
            return JsonResponse({
                'success': False,
                'error': 'parameter.ini文件不存在，请先生成文案'
            })
        
        # 读取parameter.ini文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(parameter_ini_path, encoding='utf-8')
        
        # 检查[PAPER_CONTENT]节是否存在
        if not config.has_section('PAPER_CONTENT'):
            return JsonResponse({
                'success': False,
                'error': '请先生成文案'
            })
        
        # 获取[PAPER_CONTENT]中的所有内容
        paper_content_items = config.items('PAPER_CONTENT')
        
        if not paper_content_items:
            return JsonResponse({
                'success': False,
                'error': '请先生成文案'
            })
        
        # 提取文案内容（去掉line_1 = 等前缀）
        content_lines = []
        for key, value in paper_content_items:
            if key.startswith('line_') and value.strip():
                content_lines.append(value.strip())
        
        if not content_lines:
            return JsonResponse({
                'success': False,
                'error': '请先生成文案'
            })
        
        # 将文案内容合并为一个字符串
        original_content = '\n'.join(content_lines)
        
        # 构建完整的格式化PROMPT
        final_prompt = f"{prompt}\n\n{original_content}"
        
        # 获取激活的API配置
        api_config = get_active_api_config()
        if not api_config:
            return JsonResponse({
                'success': False,
                'error': '无法获取API配置，请检查config.ini文件'
            })
        
        # 记录日志
        text_logger.info(f"开始格式化文案，使用API: {api_config.get('name', 'Unknown')}")
        text_logger.info(f"格式化PROMPT长度: {len(final_prompt)}")
        
        # 构建请求payload
        payload = {
            "model": api_config['selected_model'],
            "messages": [
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            "temperature": float(api_config.get('temperature', 0.7)),
            "max_tokens": int(api_config.get('max_tokens', 4000))
        }
        
        # 构建API请求URL
        api_url = api_config['api_url']
        if not api_url.endswith('/'):
            api_url += '/'
        api_url += 'chat/completions'
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {api_config['api_key']}"
        }
        
        # 设置最大重试次数
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                text_logger.info(f"第 {attempt + 1} 次格式化尝试")
                
                # 发送API请求
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=300  # 5分钟超时
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        formatted_content = response_data['choices'][0]['message']['content']
                        
                        # 过滤掉<think>标签内容
                        import re
                        filtered_content = re.sub(r'<think>.*?</think>', '', formatted_content, flags=re.DOTALL)
                        filtered_content = filtered_content.strip()
                        
                        text_logger.info(f"格式化成功，生成内容长度: {len(filtered_content)}")
                        
                        # 保存到paper.json文件
                        paper_json_path = os.path.join(project_path, 'paper.json')
                        
                        try:
                            with open(paper_json_path, 'w', encoding='utf-8') as f:
                                json.dump({
                                    "formatted_content": filtered_content,
                                    "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    "original_lines_count": len(content_lines)
                                }, f, ensure_ascii=False, indent=2)
                            
                            text_logger.info(f"格式化后的文案已保存到: {paper_json_path}")
                            
                            return JsonResponse({
                                'success': True,
                                'content': filtered_content,
                                'message': f'文案格式化成功（第{attempt + 1}次尝试）'
                            })
                            
                        except Exception as save_error:
                            text_logger.error(f"保存paper.json文件时发生错误: {str(save_error)}")
                            return JsonResponse({
                                'success': False,
                                'error': f'保存文件时发生错误: {str(save_error)}'
                            })
                    else:
                        text_logger.error("API响应中没有choices字段或choices为空")
                        if attempt == max_retries - 1:
                            return JsonResponse({
                                'success': False,
                                'error': f'经过{max_retries}次尝试，API响应格式仍然错误'
                            })
                        continue
                else:
                    text_logger.error(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
                    if attempt == max_retries - 1:
                        return JsonResponse({
                            'success': False,
                            'error': f'经过{max_retries}次尝试，API请求仍然失败: {response.status_code}'
                        })
                    continue
                    
            except requests.exceptions.Timeout:
                text_logger.error(f"第 {attempt + 1} 次格式化请求超时")
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'格式化请求超时（已重试{max_retries}次），请检查网络连接或稍后重试'
                    })
                continue
            except requests.exceptions.RequestException as e:
                text_logger.error(f"第 {attempt + 1} 次格式化请求异常: {str(e)}")
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'格式化请求失败（已重试{max_retries}次）: {str(e)}'
                    })
                continue
            except Exception as e:
                text_logger.error(f"第 {attempt + 1} 次格式化尝试失败: {str(e)}")
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'格式化失败（已重试{max_retries}次）: {str(e)}'
                    })
                continue
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        text_logger.error(f'格式化文案时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'格式化文案时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def generate_video(request):
    """
    生成视频的API端点 - 按片段生成视频
    
    参数:
        request: Django的HttpRequest对象，包含分辨率、质量和文件名设置
        
    返回:
        JsonResponse: 包含生成结果的JSON响应
    """
    try:
        # 解析请求参数
        data = json.loads(request.body) if request.body else {}
        
        # 获取输出设置
        resolution = data.get('resolution', {'width': 1080, 'height': 1920})  # 默认手机分辨率
        quality = data.get('quality', {'preset': 'medium'})  # 默认中等质量
        filename = data.get('filename', '').strip()  # 文件名
        
        # 导入VideoProcessor
        import sys
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common'))
        from video_processor import VideoProcessor
        
        # 获取当前项目路径
        project_path = get_current_project_path()
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '无法获取当前项目路径'
            })
        
        logger.info(f"开始按片段生成视频，项目路径: {project_path}")
        logger.info(f"输出设置 - 分辨率: {resolution['width']}x{resolution['height']}, 质量: {quality}, 文件名: {filename}")
        
        # 读取项目配置
        parameter_file = os.path.join(project_path, 'parameter.ini')
        if not os.path.exists(parameter_file):
            return JsonResponse({
                'success': False,
                'error': 'parameter.ini文件不存在'
            })
        
        config = configparser.ConfigParser(interpolation=None)
        config.read(parameter_file, encoding='utf-8')
        
        # 获取片段数量
        sentence_count = config.getint('PAPER_INFO', 'sentence_count', fallback=0)
        if sentence_count == 0:
            return JsonResponse({
                'success': False,
                'error': '项目中没有找到有效的片段数量'
            })
        
        logger.info(f"需要生成 {sentence_count} 个视频片段")
        
        # 创建视频处理器
        processor = VideoProcessor()
        
        # 生成每个视频片段
        generated_segments = []
        for segment_index in range(1, sentence_count + 1):
            try:
                # 获取音频时长
                audio_duration_key = f'script_{segment_index}_duration'
                if not config.has_section('AUDIO_INFO') or not config.has_option('AUDIO_INFO', audio_duration_key):
                    logger.warning(f"未找到片段{segment_index}的音频时长信息")
                    continue
                
                audio_duration = config.getfloat('AUDIO_INFO', audio_duration_key)
                
                # 查找对应的图片文件
                images_dir = os.path.join(project_path, 'images')
                image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))] if os.path.exists(images_dir) else []
                
                # 按数字顺序排序
                import re
                def extract_number(filename):
                    match = re.search(r'script_(\d+)', filename)
                    return int(match.group(1)) if match else 0
                
                image_files.sort(key=extract_number)
                
                if segment_index - 1 >= len(image_files):
                    logger.warning(f"未找到片段{segment_index}对应的图片文件")
                    continue
                
                image_path = os.path.join(images_dir, image_files[segment_index - 1])
                
                logger.info(f"生成片段{segment_index}: 音频时长={audio_duration}秒, 图片={image_files[segment_index - 1]}")
                
                # 生成视频片段
                success = processor.generate_video_segment(
                    project_path, segment_index, audio_duration, image_path
                )
                
                if success:
                    generated_segments.append(segment_index)
                    logger.info(f"片段{segment_index}生成成功")
                else:
                    logger.error(f"片段{segment_index}生成失败")
                    
            except Exception as e:
                logger.error(f"生成片段{segment_index}时发生错误: {e}")
                continue
        
        if not generated_segments:
            return JsonResponse({
                'success': False,
                'error': '没有成功生成任何视频片段'
            })
        
        logger.info(f"成功生成 {len(generated_segments)} 个视频片段: {generated_segments}")
        
        # 合并所有视频片段
        videos_dir = os.path.join(project_path, 'videos')
        segment_files = []
        for segment_index in generated_segments:
            segment_file = os.path.join(videos_dir, f'segment_{segment_index:03d}.mp4')
            if os.path.exists(segment_file):
                segment_files.append(segment_file)
            else:
                logger.warning(f"视频片段文件不存在: {segment_file}")
        
        if not segment_files:
            return JsonResponse({
                'success': False,
                'error': '没有找到生成的视频片段文件'
            })
        
        # 生成最终文件名
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'video_{timestamp}.mp4'
        
        if not filename.endswith('.mp4'):
            filename += '.mp4'
        
        # 输出到项目根目录（不是videos目录）
        final_video_path = os.path.join(project_path, filename)
        
        # 使用FFMPEG合并视频片段
        success = processor.concatenate_videos(
            segment_files, final_video_path, project_path
        )
        
        if success:
            logger.info(f"最终视频生成完成: {final_video_path}")
            return JsonResponse({
                'success': True,
                'message': '视频生成成功',
                'video_path': final_video_path,
                'segments_generated': len(generated_segments),
                'total_segments': sentence_count
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '合并视频片段失败'
            })
        
        return JsonResponse({
            'success': True,
            'message': '视频生成成功',
            'output_path': output_path,
            'filename': output_filename
        })
        
    except Exception as e:
        logger.error(f'生成视频时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'生成视频时发生错误: {str(e)}'
        })

@csrf_exempt
def get_project_title(request):
    """
    获取指定项目的parameter.ini文件中[PAPER_INFO]部分的title内容
    
    参数:
        request: HTTP请求对象，包含project_path
        
    返回:
        JsonResponse: 包含title内容的JSON响应
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': '仅支持POST请求'
        })
    
    try:
        data = json.loads(request.body)
        project_path = data.get('project_path')
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建parameter.ini文件路径
        parameter_file_path = os.path.join(project_path, 'parameter.ini')
        
        if not os.path.exists(parameter_file_path):
            return JsonResponse({
                'success': False,
                'error': f'parameter.ini文件不存在: {parameter_file_path}'
            })
        
        # 读取parameter.ini文件
        config = configparser.ConfigParser(interpolation=None)
        config.read(parameter_file_path, encoding='utf-8')
        
        # 获取[PAPER_INFO]部分的title
        if config.has_section('PAPER_INFO') and config.has_option('PAPER_INFO', 'title'):
            title = config.get('PAPER_INFO', 'title')
            
            if title.strip():  # 确保title不为空
                return JsonResponse({
                    'success': True,
                    'title': title,
                    'message': '成功获取第一句话内容'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'title字段为空，请先生成第一句话'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': '未找到[PAPER_INFO]部分的title字段，请先生成第一句话'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'获取项目title时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'获取项目title时发生错误: {str(e)}'
        })

def auto_video(request):
    """
    自动生成视频页面视图函数 - 整合所有流程的核心页面
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        渲染后的auto_video.html模板
    """
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    context = {
        'current_time': current_time
    }
    
    return render(request, 'auto_video.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def save_continuous_generation_settings(request):
    """
    保存连续生成设置到config.ini文件的API端点
    
    参数:
        request: Django的HttpRequest对象，包含JSON格式的设置数据
        
    返回:
        JsonResponse: 包含操作结果的JSON响应
    """
    try:
        # 解析请求中的JSON数据
        data = json.loads(request.body)
        
        # 获取设置数据
        continuous_generation_enabled = data.get('continuous_generation_enabled', False)
        continuous_generation_count = data.get('continuous_generation_count', 2)
        
        # 验证数据
        if not isinstance(continuous_generation_enabled, bool):
            return JsonResponse({
                'success': False,
                'error': 'continuous_generation_enabled必须是布尔值'
            })
        
        if not isinstance(continuous_generation_count, int) or continuous_generation_count < 1 or continuous_generation_count > 100:
            return JsonResponse({
                'success': False,
                'error': 'continuous_generation_count必须是1-100之间的整数'
            })
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 创建或读取配置文件
        config = configparser.ConfigParser(interpolation=None)
        
        # 如果文件存在，先读取现有配置
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        # 确保存在AUTO_VIDEO_CONFIG节
        if not config.has_section('AUTO_VIDEO_CONFIG'):
            config.add_section('AUTO_VIDEO_CONFIG')
        
        # 设置配置值
        config.set('AUTO_VIDEO_CONFIG', 'continuous_generation_enabled', str(continuous_generation_enabled).lower())
        config.set('AUTO_VIDEO_CONFIG', 'continuous_generation_count', str(continuous_generation_count))
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        # 记录日志
        logger.info(f'连续生成设置已保存: 启用={continuous_generation_enabled}, 次数={continuous_generation_count}')
        
        return JsonResponse({
            'success': True,
            'message': '连续生成设置已成功保存到config.ini文件',
            'continuous_generation_enabled': continuous_generation_enabled,
            'continuous_generation_count': continuous_generation_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'保存连续生成设置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存设置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_continuous_generation_settings(request):
    """
    从config.ini文件加载连续生成设置的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含连续生成设置的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 默认值
        continuous_generation_enabled = False
        continuous_generation_count = 2
        
        # 如果配置文件存在，读取设置
        if os.path.exists(config_path):
            config = configparser.ConfigParser(interpolation=None)
            config.read(config_path, encoding='utf-8')
            
            if config.has_section('AUTO_VIDEO_CONFIG'):
                if config.has_option('AUTO_VIDEO_CONFIG', 'continuous_generation_enabled'):
                    continuous_generation_enabled = config.getboolean('AUTO_VIDEO_CONFIG', 'continuous_generation_enabled')
                
                if config.has_option('AUTO_VIDEO_CONFIG', 'continuous_generation_count'):
                    continuous_generation_count = config.getint('AUTO_VIDEO_CONFIG', 'continuous_generation_count')
        
        return JsonResponse({
            'success': True,
            'continuous_generation_enabled': continuous_generation_enabled,
            'continuous_generation_count': continuous_generation_count,
            'message': '连续生成设置加载成功'
        })
        
    except Exception as e:
        logger.error(f'加载连续生成设置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载设置时发生错误: {str(e)}',
            'continuous_generation_enabled': False,
            'continuous_generation_count': 2
        })

# Django日志管理系统
import threading
import queue
import time
from datetime import datetime

# 全局日志队列
django_log_queue = queue.Queue(maxsize=1000)

class DjangoLogHandler(logging.Handler):
    """自定义Django日志处理器，将日志发送到队列"""
    
    def emit(self, record):
        try:
            # 格式化日志记录
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).strftime('%H:%M:%S'),
                'level': record.levelname,
                'message': self.format(record),
                'module': record.module if hasattr(record, 'module') else 'django',
                'created': record.created
            }
            
            # 添加到队列，如果队列满了就丢弃最旧的日志
            if django_log_queue.full():
                try:
                    django_log_queue.get_nowait()
                except queue.Empty:
                    pass
            
            django_log_queue.put_nowait(log_entry)
            
        except Exception:
            # 避免日志处理器本身出错
            pass

# 初始化日志处理器
def setup_django_log_handler():
    """设置Django日志处理器"""
    try:
        # 获取Django的根日志器
        django_logger = logging.getLogger('django')
        
        # 创建自定义处理器
        handler = DjangoLogHandler()
        handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # 添加处理器到Django日志器
        django_logger.addHandler(handler)
        
        # 也添加到应用日志器
        app_logger = logging.getLogger('Mainsite')
        app_logger.addHandler(handler)
        
        return True
    except Exception as e:
        print(f"设置Django日志处理器失败: {e}")
        return False

# 在模块加载时初始化日志处理器
setup_django_log_handler()

@csrf_exempt
@require_http_methods(["GET"])
def get_django_logs(request):
    """
    获取Django实时日志的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含日志条目的JSON响应
    """
    try:
        # 获取查询参数
        max_logs = int(request.GET.get('max_logs', 50))  # 最多返回50条日志
        since_timestamp = request.GET.get('since', None)  # 获取指定时间戳之后的日志
        
        logs = []
        temp_logs = []
        
        # 从队列中获取所有日志
        while not django_log_queue.empty() and len(temp_logs) < max_logs * 2:
            try:
                log_entry = django_log_queue.get_nowait()
                temp_logs.append(log_entry)
            except queue.Empty:
                break
        
        # 如果指定了时间戳，只返回该时间戳之后的日志
        if since_timestamp:
            try:
                since_time = float(since_timestamp)
                temp_logs = [log for log in temp_logs if log['created'] > since_time]
            except (ValueError, TypeError):
                pass
        
        # 按时间排序并限制数量
        temp_logs.sort(key=lambda x: x['created'])
        logs = temp_logs[-max_logs:] if len(temp_logs) > max_logs else temp_logs
        
        # 将处理过的日志重新放回队列（保持队列中的日志）
        for log in temp_logs:
            if not django_log_queue.full():
                try:
                    django_log_queue.put_nowait(log)
                except queue.Full:
                    break
        
        return JsonResponse({
            'success': True,
            'logs': logs,
            'count': len(logs),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f'获取Django日志时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'获取日志时发生错误: {str(e)}',
            'logs': [],
            'count': 0
        })

@csrf_exempt
@require_http_methods(["POST"])
def add_custom_log(request):
    """
    添加自定义日志条目的API端点
    
    参数:
        request: Django的HttpRequest对象，包含日志数据
        
    返回:
        JsonResponse: 操作结果
    """
    try:
        data = json.loads(request.body)
        
        level = data.get('level', 'INFO').upper()
        message = data.get('message', '')
        module = data.get('module', 'AutoVideo')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': '日志消息不能为空'
            })
        
        # 创建日志条目
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'message': message,
            'module': module,
            'created': time.time()
        }
        
        # 添加到队列
        if django_log_queue.full():
            try:
                django_log_queue.get_nowait()
            except queue.Empty:
                pass
        
        django_log_queue.put_nowait(log_entry)
        
        # 同时记录到Django日志系统
        app_logger = logging.getLogger('Mainsite.AutoVideo')
        if level == 'ERROR':
            app_logger.error(message)
        elif level == 'WARNING':
            app_logger.warning(message)
        elif level == 'SUCCESS':
            app_logger.info(f"✅ {message}")
        else:
            app_logger.info(message)
        
        return JsonResponse({
            'success': True,
            'message': '日志已添加'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'添加自定义日志时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'添加日志时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def load_active_format_prompt_content(request):
    """
    从config.ini读取活动格式化提示词文件内容的API端点
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含格式化提示词内容的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config.ini')
        
        # 读取config.ini配置
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path, encoding='utf-8')
        
        # 获取活动格式化提示词文件名
        if not config.has_section('FORMAT_PROMPT_CONFIG'):
            return JsonResponse({
                'success': False,
                'error': 'config.ini中缺少FORMAT_PROMPT_CONFIG配置节'
            })
        
        if not config.has_option('FORMAT_PROMPT_CONFIG', 'active_format_prompt_file'):
            return JsonResponse({
                'success': False,
                'error': 'config.ini中缺少active_format_prompt_file配置项'
            })
        
        filename = config.get('FORMAT_PROMPT_CONFIG', 'active_format_prompt_file')
        
        if not filename:
            return JsonResponse({
                'success': False,
                'error': '活动格式化提示词文件名为空'
            })
        
        # 构建文件路径
        format_prompt_path = os.path.join(project_root, 'common', 'text_fmt', filename)
        
        # 检查文件是否存在
        if not os.path.exists(format_prompt_path):
            return JsonResponse({
                'success': False,
                'error': f'格式化提示词文件不存在: {filename}'
            })
        
        # 读取文件内容
        with open(format_prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f'已从config.ini加载活动格式化提示词文件: {filename}')
        
        return JsonResponse({
            'success': True,
            'content': content,
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f'加载活动格式化提示词内容时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载活动格式化提示词内容时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_video_history(request):
    """
    获取projects目录下所有MP4文件的历史记录
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 包含MP4文件列表的JSON响应
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        projects_dir = os.path.join(project_root, 'projects')
        
        videos = []
        
        # 检查projects目录是否存在
        if not os.path.exists(projects_dir):
            return JsonResponse({
                'success': True,
                'videos': [],
                'count': 0
            })
        
        # 遍历projects目录下的所有子目录
        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            
            # 跳过非目录文件
            if not os.path.isdir(project_path):
                continue
            
            # 查找该项目目录下的所有MP4文件
            for file_name in os.listdir(project_path):
                if file_name.lower().endswith('.mp4'):
                    file_path = os.path.join(project_path, file_name)
                    
                    # 获取文件信息
                    try:
                        stat_info = os.stat(file_path)
                        file_size = stat_info.st_size
                        modified_time = stat_info.st_mtime
                        
                        # 格式化文件大小
                        if file_size < 1024:
                            size_str = f"{file_size} B"
                        elif file_size < 1024 * 1024:
                            size_str = f"{file_size / 1024:.1f} KB"
                        elif file_size < 1024 * 1024 * 1024:
                            size_str = f"{file_size / (1024 * 1024):.1f} MB"
                        else:
                            size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
                        
                        # 格式化修改时间
                        from datetime import datetime
                        modified_datetime = datetime.fromtimestamp(modified_time)
                        time_str = modified_datetime.strftime('%Y-%m-%d %H:%M:%S')
                        
                        videos.append({
                            'filename': file_name,
                            'project_name': project_name,
                            'file_path': file_path,
                            'relative_path': f'{project_name}/{file_name}',
                            'size': file_size,
                            'formatted_size': size_str,
                            'modified_time': modified_time,
                            'formatted_time': time_str
                        })
                        
                    except OSError as e:
                        logger.warning(f'无法获取文件信息: {file_path}, 错误: {str(e)}')
                        continue
        
        # 按修改时间降序排序（最新的在前面）
        videos.sort(key=lambda x: x['modified_time'], reverse=True)
        
        logger.info(f'找到 {len(videos)} 个视频文件')
        
        return JsonResponse({
            'success': True,
            'videos': videos,
            'count': len(videos)
        })
        
    except Exception as e:
        logger.error(f'获取视频历史记录时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'获取视频历史记录时发生错误: {str(e)}',
            'videos': [],
            'count': 0
        })

@csrf_exempt
@require_http_methods(["POST"])
def delete_video(request):
    """
    删除指定的视频文件
    
    参数:
        request: Django的HttpRequest对象，包含要删除的文件路径
        
    返回:
        JsonResponse: 删除操作的结果
    """
    try:
        data = json.loads(request.body)
        file_path = data.get('file_path')
        
        if not file_path:
            return JsonResponse({
                'success': False,
                'error': '未提供文件路径'
            })
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return JsonResponse({
                'success': False,
                'error': '文件不存在'
            })
        
        # 检查文件是否在projects目录下（安全检查）
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        projects_dir = os.path.join(project_root, 'projects')
        
        # 获取文件的绝对路径
        abs_file_path = os.path.abspath(file_path)
        abs_projects_dir = os.path.abspath(projects_dir)
        
        # 检查文件是否在projects目录下
        if not abs_file_path.startswith(abs_projects_dir):
            return JsonResponse({
                'success': False,
                'error': '只能删除projects目录下的文件'
            })
        
        # 检查文件是否为MP4格式
        if not file_path.lower().endswith('.mp4'):
            return JsonResponse({
                'success': False,
                'error': '只能删除MP4文件'
            })
        
        # 删除文件
        os.remove(file_path)
        
        logger.info(f'成功删除视频文件: {file_path}')
        
        return JsonResponse({
            'success': True,
            'message': '视频文件删除成功'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except OSError as e:
        logger.error(f'删除视频文件时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'删除文件时发生错误: {str(e)}'
        })
    except Exception as e:
        logger.error(f'删除视频时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'删除视频时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def clear_video_history(request):
    """
    清空所有视频历史记录（删除projects目录下的所有MP4文件）
    
    参数:
        request: Django的HttpRequest对象
        
    返回:
        JsonResponse: 清空操作的结果
    """
    try:
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        projects_dir = os.path.join(project_root, 'projects')
        
        deleted_count = 0
        
        # 检查projects目录是否存在
        if not os.path.exists(projects_dir):
            return JsonResponse({
                'success': True,
                'deleted_count': 0,
                'message': 'projects目录不存在，无需清空'
            })
        
        # 遍历projects目录下的所有子目录
        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            
            # 跳过非目录文件
            if not os.path.isdir(project_path):
                continue
            
            # 查找该项目目录下的所有MP4文件并删除
            for file_name in os.listdir(project_path):
                if file_name.lower().endswith('.mp4'):
                    file_path = os.path.join(project_path, file_name)
                    
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f'删除视频文件: {file_path}')
                    except OSError as e:
                        logger.warning(f'删除文件失败: {file_path}, 错误: {str(e)}')
                        continue
        
        logger.info(f'清空视频历史完成，共删除 {deleted_count} 个文件')
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'成功清空历史记录，删除了 {deleted_count} 个视频文件'
        })
        
    except Exception as e:
        logger.error(f'清空视频历史时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'清空视频历史时发生错误: {str(e)}',
            'deleted_count': 0
        })

@csrf_exempt
def test_media_file(request, file_path):
    """测试媒体文件服务"""
    try:
        from django.http import FileResponse, Http404
        import mimetypes
        
        # 构建完整的文件路径
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            return HttpResponse(f"文件不存在: {full_path}", status=404)
        
        # 获取文件的MIME类型
        content_type, _ = mimetypes.guess_type(full_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # 返回文件响应
        response = FileResponse(open(full_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(full_path)}"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f"服务器错误: {str(e)}", status=500)

@csrf_exempt
@require_http_methods(["GET"])
def load_audio_pause_settings(request):
    """
    加载项目的音频停顿设置
    
    参数:
        request: Django的HttpRequest对象，包含project_path参数
        
    返回:
        JsonResponse: 包含音频停顿设置的JSON响应
    """
    try:
        project_path = request.GET.get('project_path', '').strip()
        
        if not project_path:
            # 如果没有提供项目路径，尝试从配置文件获取当前项目
            current_project = load_current_project_from_config()
            if current_project and current_project.get('path'):
                project_path = current_project['path']
            else:
                return JsonResponse({
                    'success': False,
                    'error': '未提供项目路径且没有当前打开的项目'
                })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建parameter.ini文件路径
        parameter_file_path = os.path.join(project_path, 'parameter.ini')
        
        # 默认值
        pre_pause = 0.25
        post_pause = 0.25
        
        if os.path.exists(parameter_file_path):
            # 读取parameter.ini文件
            config = configparser.ConfigParser(interpolation=None)
            config.read(parameter_file_path, encoding='utf-8')
            
            # 读取音频停顿设置
            if config.has_section('AUDIO_PAUSE'):
                pre_pause = config.getfloat('AUDIO_PAUSE', 'pre_pause', fallback=0.25)
                post_pause = config.getfloat('AUDIO_PAUSE', 'post_pause', fallback=0.25)
        
        return JsonResponse({
            'success': True,
            'pre_pause': pre_pause,
            'post_pause': post_pause
        })
        
    except Exception as e:
        logger.error(f'加载音频停顿设置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'加载音频停顿设置时发生错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def save_audio_pause_settings(request):
    """
    保存项目的音频停顿设置
    
    参数:
        request: Django的HttpRequest对象，包含project_path、pre_pause、post_pause参数
        
    返回:
        JsonResponse: 保存结果的JSON响应
    """
    try:
        data = json.loads(request.body)
        project_path = data.get('project_path', '').strip()
        pre_pause = data.get('pre_pause')
        post_pause = data.get('post_pause')
        
        if not project_path:
            return JsonResponse({
                'success': False,
                'error': '缺少project_path参数'
            })
        
        if pre_pause is None or post_pause is None:
            return JsonResponse({
                'success': False,
                'error': '缺少pre_pause或post_pause参数'
            })
        
        # 验证参数值
        try:
            pre_pause = float(pre_pause)
            post_pause = float(post_pause)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': '停顿时长必须是数字'
            })
        
        if pre_pause < 0 or pre_pause > 5 or post_pause < 0 or post_pause > 5:
            return JsonResponse({
                'success': False,
                'error': '停顿时长必须在0-5秒之间'
            })
        
        # 检查项目路径是否存在
        if not os.path.exists(project_path):
            return JsonResponse({
                'success': False,
                'error': f'项目路径不存在: {project_path}'
            })
        
        # 构建parameter.ini文件路径
        parameter_file_path = os.path.join(project_path, 'parameter.ini')
        
        # 读取或创建配置文件
        config = configparser.ConfigParser(interpolation=None)
        if os.path.exists(parameter_file_path):
            config.read(parameter_file_path, encoding='utf-8')
        
        # 确保存在AUDIO_PAUSE节
        if not config.has_section('AUDIO_PAUSE'):
            config.add_section('AUDIO_PAUSE')
        
        # 设置音频停顿值
        config.set('AUDIO_PAUSE', 'pre_pause', str(pre_pause))
        config.set('AUDIO_PAUSE', 'post_pause', str(post_pause))
        
        # 写入配置文件
        with open(parameter_file_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
        logger.info(f'音频停顿设置已保存: 前停顿={pre_pause}秒, 后停顿={post_pause}秒')
        
        return JsonResponse({
            'success': True,
            'message': f'音频停顿设置已保存: 前停顿={pre_pause}秒, 后停顿={post_pause}秒'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据格式'
        })
    except Exception as e:
        logger.error(f'保存音频停顿设置时发生错误: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'保存音频停顿设置时发生错误: {str(e)}'
        })