# AutoMovie 项目技术地图 (MAP.MD)

> 这是AutoMovie项目的技术蓝图，专为AI和开发者设计，追求完整性和技术精确性。

## 全局依赖 (Global Dependencies)

基于 `requirements.txt` 的核心依赖：

```
Django>=4.2.0          # Web框架，提供MVC架构和ORM
pypinyin>=0.47.0       # 中文拼音转换库，用于文本处理
librosa>=0.10.0        # 音频分析库，用于音频处理和特征提取
soundfile>=0.12.0      # 音频文件读写库，支持多种音频格式
numpy>=1.21.0          # 数值计算库，为音频处理提供数学运算支持
# moviepy>=1.0.3       # 视频处理库，已弃用，已使用FFMPEG替代
```

**外部系统依赖：**
```
FFMPEG                 # 视频处理核心引擎，用于视频拼接、编码、字幕添加
ComfyUI                # AI图像和音频生成服务（外部服务）
```

## 项目结构与组件地图 (Project Structure & Component Map)

```
AutoMovie/
├── Mainsite/                     # Django核心业务应用
│   ├── __init__.py
│   ├── asgi.py                  # ASGI部署配置
│   ├── migrations/              # 数据库迁移文件
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── settings.py              # Django配置文件
│   ├── urls.py                  # URL路由配置
│   ├── views.py                 # 视图控制器 (6800+行)
│   └── wsgi.py                  # WSGI部署配置
├── templates/                    # Django模板文件
│   ├── audio_gen.html           # 音频生成页面
│   ├── auto_video.html          # 自动视频生成页面
│   ├── base.html                # 基础模板
│   ├── image_gen.html           # 图像生成页面
│   ├── index.html               # 首页
│   ├── project.html             # 项目管理页面
│   ├── system_config.html       # 系统配置页面
│   ├── text_gen.html            # 文案生成页面
│   └── video_maker.html         # 视频制作页面
├── static/                       # 静态资源文件
│   ├── css/                     # 样式表文件
│   │   ├── audio_gen.css        # 音频生成页面样式
│   │   ├── base.css             # 基础样式
│   │   ├── components.css       # 组件样式
│   │   ├── image_gen.css        # 图像生成页面样式
│   │   └── responsive.css       # 响应式样式
│   ├── js/                      # JavaScript文件
│   │   ├── common.js            # 通用脚本
│   │   ├── modules/             # 模块化脚本
│   │   └── pages/               # 页面专用脚本
│   └── README.md                # 静态资源说明
├── common/                       # 通用工具模块
│   ├── Fonts/                   # 字体文件目录
│   │   ├── Lxgw975HazyGoSC-600W.ttf     # 霞鹜文楷字体
│   │   ├── SourceHanSansCN-Heavy.otf    # 思源黑体粗体
│   │   └── SourceHanSansCN-Regular.otf  # 思源黑体常规
│   ├── Workflow/                # ComfyUI工作流文件
│   │   ├── CosyVoice.json       # CosyVoice音频工作流
│   │   ├── Cosyyu.json          # Cosyyu工作流
│   │   ├── Healinganimals.json  # 治愈动物工作流
│   │   ├── 治愈动物FLUX.json     # 治愈动物FLUX工作流
│   │   └── 治愈系动漫图.json      # 治愈系动漫图工作流
│   ├── back_mus/                # 背景音乐文件
│   │   ├── Miss You Back.wav
│   │   └── Too Many Times.wav
│   ├── comf_sun/                # ComfyUI音频示例
│   │   ├── ComfyUI_00005_.wav
│   │   ├── SoundTemplate.txt
│   │   ├── SoundTemplate.wav
│   │   ├── Soundr.wav
│   │   └── demosun.wav
│   ├── first_sentence/          # 第一句话提示词模板
│   │   ├── 第一句07.txt
│   │   ├── 第一句08.txt
│   │   └── 第一句09.txt
│   ├── text_fmt/                # 文本格式模板
│   │   ├── 人物格式03.txt
│   │   ├── 人物格式04.txt
│   │   └── 人物格式05.txt
│   ├── text_gen/                # 文本生成模板
│   │   ├── 人物15.txt
│   │   ├── 全人物02.txt
│   │   └── 全人物03.txt
│   ├── audio_processor.py       # 音频处理模块
│   ├── comfyui_client.py        # ComfyUI客户端
│   └── video_processor.py       # 视频处理模块
├── frames_fixed/                # 固定帧文件目录
├── projects/                     # 用户项目存储目录（运行时创建）
│   └── [project_name]/          # 具体项目目录
│       ├── audios/              # 音频文件
│       ├── images/              # 图像文件
│       ├── videos/              # 视频文件
│       ├── temp/                # 临时文件目录
│       ├── paper.json           # 项目文案数据
│       └── parameter.ini        # 项目参数配置（创建时自动从config.ini读取默认值）
├── .gitignore                   # Git忽略文件配置
├── LICENSE                      # 开源许可证
├── config.ini.example           # 配置文件示例
├── favicon.ico                  # 网站图标
├── logo.svg                     # 项目Logo
├── manage.py                    # Django管理脚本
├── requirements.txt             # Python依赖列表
├── runserver.bat                # Windows启动脚本
├── README.md                    # 用户文档
└── MAP.MD                       # 技术文档 (本文件)
```

### 详细组件说明

### `Mainsite/`
- **职责**: Django项目的核心业务应用，包含所有视图、URL路由和业务逻辑。

### `Mainsite/settings.py`
- **职责**: Django项目的全局配置文件，定义数据库、静态文件、应用列表等核心设置。
- **导入的外部库**: `from pathlib import Path`, `import os`
- **关键配置**: DEBUG模式、ALLOWED_HOSTS、INSTALLED_APPS、数据库配置、静态文件路径

### `Mainsite/urls.py`
- **职责**: 应用级URL路由配置，定义所有页面和API端点的路由规则。
- **导入的内部模块**: `from . import views`
- **导入的外部库**: `from django.urls import path`

### `Mainsite/asgi.py`
- **职责**: ASGI（异步服务器网关接口）部署配置文件，用于异步Web服务器部署。
- **导入的外部库**: `import os`, `from django.core.asgi import get_asgi_application`

### `Mainsite/wsgi.py`
- **职责**: WSGI（Web服务器网关接口）部署配置文件，用于传统Web服务器部署。
- **导入的外部库**: `import os`, `from django.core.wsgi import get_wsgi_application`

### `Mainsite/views.py`
- **职责**: 实现所有业务逻辑的视图控制器，包含项目管理、内容生成、系统配置等功能（6800+行代码）。
- **导入的内部模块**: 
  - `from common.comfyui_client import ComfyUIClient`
  - `from common.video_processor import VideoProcessor`
  - `from common.audio_processor import AudioProcessor`
- **导入的外部库**: 
  - `from django.shortcuts import render`
  - `from django.http import JsonResponse, HttpResponse`
  - `from django.views.decorators.csrf import csrf_exempt`
  - `from django.views.decorators.http import require_http_methods`
  - `from django.conf import settings`
  - `import json, os, configparser, logging`
  - `from datetime import datetime`
  - `from pypinyin import lazy_pinyin, Style`
- **定义的函数**:
  - `index(request) -> HttpResponse`: 首页视图，显示README内容
  - `project_management(request) -> HttpResponse`: 项目管理页面
  - `text_generation(request) -> HttpResponse`: 文案生成页面
  - `image_generation(request) -> HttpResponse`: 图像生成页面
  - `audio_generation(request) -> HttpResponse`: 音频生成页面
  - `video_maker(request) -> HttpResponse`: 视频制作页面
  - `load_first_sentence_prompt_list(request) -> JsonResponse`: 加载第一句话提示词列表
  - `load_first_sentence_prompt_content(request) -> JsonResponse`: 加载提示词内容
  - `delete_first_sentence_prompt(request) -> JsonResponse`: 删除提示词文件
  - `load_default_first_sentence_prompt(request) -> JsonResponse`: 加载默认提示词
  - `save_first_sentence_prompt_to_config(request) -> JsonResponse`: 保存提示词配置
  - `save_theme(request) -> JsonResponse`: 保存项目主题

### `common/comfyui_client.py`
- **职责**: 实现ComfyUI WebSocket API客户端，处理图像和音频生成任务。
- **导入的外部库**: 
  - `import websocket, uuid, json, urllib.request, urllib.parse`
  - `from PIL import Image`
  - `import io, os, logging, configparser, requests`
  - `from urllib.parse import urlparse`
  - `from typing import Dict, List, Optional, Tuple`
- **定义的类**:
  - `ComfyUIClient`: ComfyUI客户端主类
- **定义的函数**:
  - `_load_comfyui_address()`: 从配置文件加载ComfyUI地址
  - `_load_workflow_from_config()`: 从配置文件加载工作流
  - `_get_default_workflow()`: 获取默认工作流配置
  - `_update_workflow_parameters()`: 动态更新工作流参数
  - `queue_prompt()`: 提交prompt到ComfyUI队列

### `common/audio_processor.py`
- **职责**: 实现音频处理功能，包括静音去除、停顿添加、时长计算和项目配置管理。
- **导入的外部库**: 
  - `import librosa, soundfile, numpy, os, logging, configparser`
  - `from typing import Tuple`
- **定义的类**:
  - `AudioProcessor`: 音频处理主类
- **定义的函数**:
  - `trim_silence()`: 去除音频前后静音并添加停顿
  - `get_audio_duration()`: 获取音频文件时长
  - `create_project_parameter_ini()`: 为新项目创建parameter.ini文件（从config.ini读取默认配置）
  - `update_parameter_ini()`: 更新parameter.ini中的音频时长信息
  - `_create_default_parameter_ini()`: 创建带有默认配置的parameter.ini文件
  - `_add_default_video_subtitle_config()`: 添加默认字幕配置
  - `_add_default_audio_pause_config()`: 添加默认音频停顿配置
  - `_add_default_background_music_config()`: 添加默认背景音乐配置
  - `_add_default_video_fade_config()`: 添加默认视频淡入淡出配置
  - `process_audio_after_generation()`: 音频生成后的完整处理流程

### `common/video_processor.py`
- **职责**: 实现视频处理功能，包括拼接、剪辑、字幕添加等操作（已使用FFMPEG完全实现）。
- **导入的外部库**: 
  - `import os, logging, subprocess, configparser, math`
  - `from typing import List, Optional, Tuple, Dict, Any`
- **定义的类**:
  - `VideoProcessor`: 视频处理主类（基于FFMPEG实现）
- **定义的函数**:
  - `generate_video_segment()`: 生成单个视频片段（FFMPEG实现）
  - `concatenate_videos()`: 拼接多个视频文件（FFMPEG实现，已修复视频片段文件名匹配问题（segment_XXX.mp4格式），输出文件位于项目根目录，支持背景音乐混合）
  - `_generate_frames_with_fade()`: 生成带淡入淡出效果的帧图片
  - `_create_video_from_frames()`: 从帧图片创建视频
  - `_add_audio_to_video()`: 为视频添加对应的音频文件（音频文件格式固定为script_N_1.wav，找不到文件时抛出FileNotFoundError异常）
  - `_add_subtitles_to_video()`: 为视频添加字幕
  - `_merge_video_segments_with_background_music()`: 合并视频片段并添加背景音乐
  - `_add_background_music_to_video()`: 为视频添加背景音乐
- `cleanup()`: 清理临时文件

### `common/audio_processor.py`
- **职责**: 实现音频处理功能，包括静音检测与去除、音频时长计算、前后停顿控制、配置文件更新等功能。使用librosa和soundfile库实现。
- **导入的外部库**: 
  - `import librosa, soundfile as sf, numpy as np`
  - `import os, logging, configparser`
  - `from typing import Tuple, Optional`
- **定义的类**:
  - `AudioProcessor`: 音频处理主类
- **定义的函数**:
  - `trim_silence()`: 去除音频文件前后的无声部分，支持前后停顿控制
  - `get_audio_duration()`: 获取音频文件时长
  - `update_parameter_ini()`: 更新配置文件中的音频时长信息
  - `_create_default_parameter_ini()`: 创建默认配置文件
  - `_add_default_video_subtitle_config()`: 添加默认字幕配置
  - `_add_default_audio_pause_config()`: 添加默认音频停顿配置

### `static/js/system_config.js`
- **职责**: 系统配置页面的前端交互逻辑，包括API管理、标签切换、表单处理等。
- **核心功能**: API列表管理、配置表单处理、连接测试、状态更新
- **异步请求**: 使用fetch API与后端交互，处理JSON响应
- **事件处理**: 点击、双击事件处理，CSRF令牌管理

## 核心函数与类详解 (技术版)

### Class `ComfyUIClient`
- **继承自**: `object`
- **功能概述**: ComfyUI WebSocket API客户端，负责与ComfyUI服务器通信，处理图像和音频生成任务。支持工作流加载、参数更新、WebSocket通信和文件下载。
- **主要属性**:
  - `server_address (str)`: ComfyUI服务器地址
  - `client_id (str)`: 客户端唯一标识符
  - `logger (logging.Logger)`: 日志记录器
  - `image_workflow (dict)`: 图像生成工作流配置
  - `audio_workflow (dict)`: 音频生成工作流配置
- **核心方法**:
  - `__init__(self, server_address: str = None)`: 初始化客户端，加载配置和工作流
  - `_load_comfyui_address(self) -> str`: 从config.ini加载ComfyUI地址
  - `_load_workflow_from_config(self, workflow_type: str = 'image') -> dict`: 从配置文件加载工作流
  - `_get_default_workflow(self) -> dict`: 获取默认工作流配置
  - `_update_workflow_parameters(self, workflow: dict, params: dict, workflow_type: str = 'image')`: 动态更新工作流参数
  - `queue_prompt(self, prompt: dict) -> dict`: 提交prompt到ComfyUI队列

#### `__init__()`
- **功能**: 初始化ComfyUI客户端，从配置文件加载服务器地址，生成客户端ID。
- **输入 (参数)**:
  - `server_address (str, optional)`: ComfyUI服务器地址，如果为None则从配置文件读取
- **输出 (返回值)**: 无
- **可能抛出的异常**:
  - `Exception`: 配置文件读取失败时记录错误日志

#### `_load_workflow_from_config()`
- **功能**: 从config.ini和JSON文件加载指定类型的工作流配置，支持图像和音频两种类型。
- **输入 (参数)**:
  - `workflow_type (str)`: 工作流类型，'image'或'audio'，默认为'image'
- **输出 (返回值)**:
  - `dict`: 工作流配置字典
- **可能抛出的异常**:
  - `Exception`: 工作流文件加载失败时返回默认工作流

#### `_update_workflow_parameters()`
- **功能**: 动态更新工作流参数，支持CLIP提示词占位符替换、CLIPTextEncodeFlux节点处理和KSampler种子设置。
- **输入 (参数)**:
  - `workflow (dict)`: 原始工作流配置
  - `params (dict)`: 要更新的参数字典
  - `workflow_type (str)`: 工作流类型，默认为'image'
- **输出 (返回值)**: 无（直接修改workflow对象）
- **可能抛出的异常**:
  - `ValueError`: 工作流中未找到占位符时抛出
  - `Exception`: 参数更新失败时抛出

#### `queue_prompt()`
- **功能**: 将prompt提交到ComfyUI队列，返回包含prompt_id的响应字典。
- **输入 (参数)**:
  - `prompt (dict)`: 要提交的prompt配置
- **输出 (返回值)**:
  - `dict`: 包含prompt_id等信息的响应字典
- **可能抛出的异常**:
  - `Exception`: 网络请求失败或响应格式错误时抛出



### Class `VideoProcessor`
- **继承自**: `object`
- **功能概述**: 视频处理工具类，提供视频拼接、剪辑、调整尺寸、添加字幕等功能。使用FFMPEG实现，支持多种视频格式和高性能处理。
- **主要属性**:
  - `logger (logging.Logger)`: 日志记录器
  - `temp_files (list)`: 临时文件列表，用于清理
  - `ffmpeg_path (str)`: FFMPEG可执行文件路径
- **核心方法**:
  - `__init__(self)`: 初始化处理器
  - `generate_video_segment(self, project_path: str, segment_index: int, audio_duration: float, image_path: str) -> bool`: 生成单个视频片段
  - `concatenate_videos(self, video_paths: list, output_path: str) -> bool`: 拼接多个视频（FFMPEG实现）
  - `_generate_frames_with_fade(self, image_path: str, temp_dir: str, segment_index: int, total_frames: int, fade_in_frames: int, fade_out_frames: int) -> bool`: 生成带淡入淡出效果的帧图片
  - `_create_video_from_frames(self, temp_dir: str, segment_index: int, total_frames: int, video_fps: int, audio_duration: float) -> str`: 从帧图片创建视频
  - `_add_audio_to_video(self, video_path: str, project_path: str, segment_index: int) -> str`: 为视频添加对应的音频文件
  - `_add_subtitles_to_video(self, video_path: str, project_path: str, segment_index: int) -> str`: 为视频添加字幕
  - `_merge_video_segments_with_background_music(self, segment_files: list, output_path: str, project_path: str) -> bool`: 合并视频片段并添加背景音乐
  - `_add_background_music_to_video(self, video_path: str, output_path: str, project_path: str, bgm_filename: str) -> bool`: 为视频添加背景音乐
  - `cleanup(self)`: 清理临时文件

#### `generate_video_segment()`
- **功能**: 生成单个视频片段，包括帧图片生成、视频合成、音频添加、字幕添加等完整流程，支持淡入淡出效果。
- **输入 (参数)**:
  - `project_path (str)`: 项目路径
  - `segment_index (int)`: 片段索引（从1开始）
  - `audio_duration (float)`: 音频时长（秒）
  - `image_path (str)`: 图片路径
- **输出 (返回值)**:
  - `bool`: 生成是否成功
- **可能抛出的异常**:
  - `Exception`: 视频生成过程出错
- **重要修复**: 修复了视频片段没有声音的问题，确保音频正确添加到视频中

#### `_add_audio_to_video()`
- **功能**: 为视频添加对应的音频文件，从项目audios目录中查找匹配的音频文件并合成到视频中
- **输入 (参数)**:
  - `video_path (str)`: 输入视频文件路径
  - `project_path (str)`: 项目路径
  - `segment_index (int)`: 片段索引（从1开始）
- **输出 (返回值)**:
  - `Optional[str]`: 添加音频后的视频路径或None
- **可能抛出的异常**:
  - `Exception`: FFMPEG执行失败、音频文件不存在
- **音频文件格式**: 使用ComfyUI固定生成的命名格式（script_N_1.wav）
- **错误处理**: 如果音频文件不存在会抛出FileNotFoundError异常，确保音频完整性
- **重要修复**: 解决了视频片段没有声音的核心问题

#### `concatenate_videos()`
- **功能**: 将多个视频文件按顺序拼接成一个完整视频，使用FFMPEG实现高性能处理，支持背景音乐混合。
- **输入 (参数)**:
  - `video_paths (List[str])`: 要拼接的视频文件路径列表
  - `output_path (str)`: 输出视频文件路径（输出到项目根目录）
  - `project_path (str)`: 项目路径
  - `fps (int)`: 输出视频帧率，默认24
  - `codec (str)`: 视频编码器，默认'libx264'
- **输出 (返回值)**:
  - `bool`: 拼接是否成功
- **可能抛出的异常**:
  - `Exception`: 视频文件加载失败或拼接过程出错
- **注意**: 使用FFMPEG实现，支持背景音乐混合，输出文件位于项目根目录
- **修复**: 已修复视频片段文件名匹配问题（segment_XXX.mp4格式）

#### `create_color_clip()`
- **功能**: 创建纯色背景视频片段，用于视频拼接或作为背景。
- **输入 (参数)**:
  - `color (Tuple[int, int, int])`: RGB颜色值
  - `duration (float)`: 时长（秒）
  - `size (Tuple[int, int])`: 视频尺寸，默认(1920, 1080)
  - `fps (int)`: 帧率，默认24
- **输出 (返回值)**:
  - `Optional[ColorClip]`: ColorClip对象或None
- **可能抛出的异常**:
  - `Exception`: 创建颜色片段失败

#### `trim_video()`
- **功能**: 剪辑视频片段，提取指定时间范围的内容。
- **输入 (参数)**:
  - `input_path (str)`: 输入视频路径
  - `output_path (str)`: 输出视频路径
  - `start_time (float)`: 开始时间（秒）
  - `end_time (float)`: 结束时间（秒）
- **输出 (返回值)**:
  - `bool`: 剪辑是否成功
- **可能抛出的异常**:
  - `Exception`: 视频剪辑过程出错

#### `get_video_info()`
- **功能**: 获取视频文件的详细信息，包括时长、帧率、尺寸等。
- **输入 (参数)**:
  - `video_path (str)`: 视频文件路径
- **输出 (返回值)**:
  - `Optional[dict]`: 包含视频信息的字典或None
- **可能抛出的异常**:
  - `Exception`: 获取视频信息失败

### Class `AudioProcessor`
- **继承自**: `object`
- **功能概述**: 音频处理工具类，提供静音检测与去除、音频时长计算、配置文件更新等功能。使用librosa和soundfile库实现。
- **主要属性**:
  - `logger (logging.Logger)`: 日志记录器
  - `librosa_available (bool)`: librosa库是否可用
  - `soundfile_available (bool)`: soundfile库是否可用
- **核心方法**:
  - `__init__(self)`: 初始化处理器，检查依赖库
  - `trim_silence(self, audio_path: str, output_path: str, threshold_db: float, min_duration: float) -> tuple`: 去除静音
  - `get_audio_duration(self, audio_path: str) -> float`: 获取音频时长
  - `update_parameter_ini(self, project_path: str, audio_duration: float) -> bool`: 更新配置文件
  - `process_audio_after_generation(self, audio_path: str, project_path: str, **kwargs) -> bool`: 完整音频处理流程

#### `trim_silence()`
- **功能**: 使用librosa检测并去除音频文件前后的静音部分，支持添加指定的前后停顿时长，提高音频质量。
- **输入 (参数)**:
  - `audio_path (str)`: 输入音频文件路径
  - `output_path (str)`: 输出音频文件路径，如果为None则覆盖原文件
  - `silence_threshold (float)`: 静音阈值（0-1之间），默认0.01
  - `frame_length (int)`: 帧长度，默认2048
  - `hop_length (int)`: 跳跃长度，默认512
  - `pre_pause (float)`: 前停顿时长（秒），默认0.0
  - `post_pause (float)`: 后停顿时长（秒），默认0.0
- **输出 (返回值)**:
  - `Tuple[str, float]`: (处理后的文件路径, 音频时长)
- **可能抛出的异常**:
  - `ImportError`: 音频处理库未安装
  - `Exception`: 音频处理失败

#### `update_parameter_ini()`
- **功能**: 将音频时长信息写入项目的parameter.ini文件的AUDIO_INFO节，用于后续视频生成。
- **输入 (参数)**:
  - `project_path (str)`: 项目目录路径
  - `script_id (int)`: 脚本ID
  - `duration (float)`: 音频时长（秒）
- **输出 (返回值)**:
  - `bool`: 更新是否成功
- **可能抛出的异常**:
  - `Exception`: 配置文件操作失败

#### `get_audio_duration()`
- **功能**: 获取音频文件的时长信息。
- **输入 (参数)**:
  - `audio_path (str)`: 音频文件路径
- **输出 (返回值)**:
  - `float`: 音频时长（秒）
- **可能抛出的异常**:
  - `ImportError`: 音频处理库未安装
  - `Exception`: 获取时长失败

### 核心视图函数详解

#### `index()`
- **功能**: 首页视图函数，读取并显示README.md文件内容，作为项目介绍和概览页面。
- **输入 (参数)**:
  - `request (HttpRequest)`: Django请求对象
- **输出 (返回值)**:
  - `HttpResponse`: 渲染后的index.html模板，包含README内容
- **可能抛出的异常**:
  - `Exception`: 读取README文件失败时记录错误并显示错误信息

#### `load_first_sentence_prompt_list()`
- **功能**: 加载第一句话提示词文件列表，扫描common/first_sentence目录下的所有.txt文件。
- **输入 (参数)**:
  - `request (HttpRequest)`: Django请求对象
- **输出 (返回值)**:
  - `JsonResponse`: 包含提示词文件列表的JSON响应
- **可能抛出的异常**:
  - `Exception`: 目录扫描失败时返回错误信息

#### `save_theme()`
- **功能**: 保存项目主题信息到parameter.ini文件的PAPER_INFO节。
- **输入 (参数)**:
  - `request (HttpRequest)`: Django请求对象，包含项目路径和主题信息
- **输出 (返回值)**:
  - `JsonResponse`: 包含保存结果的JSON响应
- **可能抛出的异常**:
  - `Exception`: 配置文件操作失败时返回错误信息

## 配置文件结构

### `config.ini`
全局系统配置文件，包含以下节：
- `[MAIN_MODEL]`: 主模型配置，指定当前激活的API
- `[API_*]`: 多API配置节，支持OpenRouter、DeepSeek、OpenAI等
- `[COMFYUI_CONFIG]`: ComfyUI服务配置
- `[SYSTEM_CONFIG]`: 系统级配置（向后兼容）
- `[PROJECT_CONFIG]`: 当前项目配置
- `[BAIDU_CONTENT_CENSOR]`: 百度内容审核配置
- `[PROMPT_CONFIG]`: 默认PROMPT文件配置
- `[AUDIO_PAUSE_CONFIG]`: 音频停顿默认配置
- `[VIDEO_FADE_CONFIG]`: 视频淡入淡出默认配置
- `[FIRST_SENTENCE_PROMPT_CONFIG]`: 第一句话生成配置

### `parameter.ini` (项目级)
项目特定配置文件，包含以下节：
- `[PAPER_INFO]`: 文案信息（title、theme等）
- `[PAPER_CONTENT]`: 文案内容（line_1、line_2等）
- `[AUDIO_INFO]`: 音频元数据（script_*_duration等）
- `[AUDIO_PAUSE]`: 音频停顿配置（pre_pause、post_pause）
- `[VIDEO_SUBTITLE]`: 视频字幕配置（size、color、position等）
- `[VIDEO_FADE]`: 视频淡入淡出配置（fade_in_frames、fade_out_frames、video_fps）
- `[VIDEO_BACKGROUND_MUSIC]`: 背景音乐配置（file、volume、fade_in、fade_out、loop_mode）

### `paper.json` (项目级)
项目文案数据文件，支持多种结构：
- 场景结构：`{"scenes": [{"image_prompt": "", "text": ""}]}`
- 故事结构：`{"story": [{"image_prompts": [""], "sentences": [""]}]}`
- 句子结构：`{"sentences": [""]}`

## 技术架构特点

1. **模块化设计**: 核心功能分离到common目录，便于维护和测试
2. **异步处理**: 使用WebSocket实现实时进度监听
3. **配置驱动**: 支持多层级配置文件，灵活适应不同需求
4. **错误处理**: 完善的异常处理和日志记录机制
5. **资源管理**: 自动清理临时文件，防止磁盘空间浪费
6. **向后兼容**: 支持多种配置格式和数据结构
7. **前后端分离**: 使用Ajax/Fetch实现异步交互
8. **多媒体支持**: 集成音频、视频、图像处理能力
9. **高性能视频处理**: 使用FFMPEG替代MoviePy，提供更好的性能和稳定性
10. **多API支持**: 支持多种AI服务提供商，灵活切换
11. **精确音频控制**: 支持前后停顿时长精确控制，提升音频质量
12. **视觉效果增强**: 支持淡入淡出、背景音乐等视觉和听觉效果

## 技术架构依赖关系

### 核心模块依赖图
```
Mainsite/views.py (6661行)
├── common/comfyui_client.py (ComfyUI WebSocket客户端)
├── common/video_processor.py (FFMPEG视频处理)
├── common/audio_processor.py (librosa音频处理)
├── Django框架 (Web服务)
├── configparser (配置文件管理)
└── logging (日志记录)

common/comfyui_client.py
├── websocket (WebSocket通信)
├── PIL (图像处理)
├── requests (HTTP请求)
└── configparser (配置读取)

common/video_processor.py
├── FFMPEG (视频处理核心引擎)
├── subprocess (系统调用)
├── configparser (配置管理)
└── logging (日志记录)

common/audio_processor.py
├── librosa (音频分析)
├── soundfile (音频文件IO)
├── numpy (数值计算)
└── configparser (配置管理)
```

### 数据流向图
```
用户请求 → Django Views → 业务逻辑处理
                    ↓
            ComfyUI客户端 ← → ComfyUI服务器 (图像/音频生成)
                    ↓
            音频处理器 → librosa处理 → 去除静音/停顿控制
                    ↓
            视频处理器 → FFMPEG处理 → 帧生成/拼接/字幕/背景音乐
                    ↓
            配置文件更新 → parameter.ini (时长/设置)
                    ↓
            文件系统存储 → projects/[项目名]/
                    ↓
            JSON响应 → 前端页面 (进度/结果)
```

## 开发指南

### 代码规范
1. **Python代码**: 遵循PEP 8规范，使用中文注释
2. **Django视图**: 使用装饰器进行权限控制和HTTP方法限制
3. **错误处理**: 统一使用try-except结构，记录详细日志
4. **配置管理**: 所有配置项统一存放在config.ini文件中
5. **文件路径**: 统一使用os.path.join构建跨平台路径

### 扩展开发
1. **新增工作流**: 在common/Workflow目录添加JSON文件
2. **新增处理器**: 在common目录创建新的处理模块
3. **新增页面**: 在templates目录添加HTML模板，在static目录添加对应样式
4. **新增API**: 在Mainsite/views.py添加视图函数，在urls.py配置路由

### 部署说明
1. **开发环境**: 使用`python manage.py runserver`启动
2. **生产环境**: 配置WSGI/ASGI服务器，设置DEBUG=False
3. **依赖服务**: 确保ComfyUI服务正常运行
4. **文件权限**: 确保projects目录具有读写权限

---

*本文档版本: v2.0*  
*最后更新: 基于当前代码状态完全同步*  
*维护者: AutoMovie开发团队*