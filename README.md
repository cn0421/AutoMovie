# AutoMovie - 智能短视频自动生成工具

## 一句话简介
AutoMovie 是一个让你"傻瓜式"自动生成治愈系短视频的小帮手，零基础也能玩转！支持AI文案生成、图像生成、语音合成和视频拼接的完整工作流。

## 🌟 主要特性 (它能帮你做什么？)

- **🤖 AI智能文案生成**: 根据主题自动生成吸引人的短视频文案，支持治愈系风格
- **🎨 AI图片生成**: 通过ComfyUI工作流自动生成与文案匹配的精美图片，支持多种风格
- **🎵 AI语音合成**: 将文案转换为自然流畅的语音旁白，自动去除静音部分
- **🎬 自动视频组装**: 智能组合图片、语音和字幕，生成完整视频，支持批量字幕和FFMPEG高性能处理
- **📊 项目管理**: 完整的项目创建、编辑和管理功能，支持多项目并行，新项目自动从全局配置继承默认设置
- **⚙️ 灵活配置**: 支持多种AI服务配置和工作流自定义，实时连接测试
- **🎵 背景音乐**: 支持自动添加背景音乐，音量控制和淡入淡出效果
- **⏱️ 音频优化**: 自动去除静音，支持前后停顿时长精确控制

## "五步法"让它跑起来（安装与运行）

### 第1步：获取项目
```bash
git clone https://github.com/你的仓库地址/AutoMovie.git
cd AutoMovie
```
这就像从网上把整个项目文件夹复制到你的电脑里。

### 第2步：创建专属工具箱（虚拟环境）
```bash
python -m venv venv
# Windows系统激活虚拟环境：
venv\Scripts\activate
# Mac/Linux系统激活虚拟环境：
source venv/bin/activate
```
为了不把你电脑的通用工具弄乱，我们先给这个项目创建一个独立的、干净的"工具箱"，它需要的所有专用工具都放在里面。

### 第3步：安装所有依赖工具
```bash
pip install -r requirements.txt
```
这会把下面这些"现成工具包"，一次性装到这个专属工具箱里：
- **Django**：用来搭建整个网站的"骨架"
- **pypinyin**：把汉字转换成拼音的工具
- **librosa**、**soundfile**、**numpy**：用来处理音频和数据
- **FFMPEG**：用来处理视频拼接、剪辑和字幕的专业工具（已替代MoviePy）

### 第4步：进行必要设置（配置）
1. **复制配置文件**：
   ```bash
   copy config.ini.example config.ini
   ```
   
2. **填写API密钥**（重要！）：
   打开 `config.ini` 文件，填写你的AI服务密钥：
   ```ini
   [API_DeepSeek]
   api_key = sk-your-deepseek-key-here  # 在这里填写你的DeepSeek API密钥
   ```
   
3. **配置ComfyUI地址**（如果使用AI图像/语音生成）：
   ```ini
   [COMFYUI_CONFIG]
   comfyui_address = http://127.0.0.1:8188/  # ComfyUI服务地址
   ```

### 第5步：启动！
```bash
python manage.py runserver
```
启动后，终端会显示"服务已在 http://127.0.0.1:8000 启动"，用浏览器打开这个网址即可。你会看到一个漂亮的网页界面，就可以开始制作视频了！

## 项目地图与文件职责（项目结构）

### 项目"家庭树"
```
AutoMovie/
├── manage.py                    # Django项目启动文件
├── AutoMovie/                   # Django主配置目录
│   ├── __init__.py
│   ├── settings.py              # Django设置文件
│   ├── urls.py                  # 主URL路由配置
│   └── wsgi.py                  # WSGI部署配置
├── Mainsite/                    # 主应用目录
│   ├── __init__.py
│   ├── admin.py                 # Django管理后台配置
│   ├── apps.py                  # 应用配置
│   ├── models.py                # 数据模型（暂未使用）
│   ├── tests.py                 # 测试文件
│   ├── urls.py                  # 应用URL路由
│   └── views.py                 # 视图函数（核心业务逻辑）
├── common/                      # 公共工具模块
│   ├── __init__.py
│   ├── comfyui_client.py        # ComfyUI客户端（WebSocket通信）
│   ├── video_processor.py       # 视频处理器（MoviePy封装）
│   ├── audio_processor.py       # 音频处理器（librosa封装）
│   ├── Fonts/                   # 字体文件目录
│   │   └── SourceHanSansCN-Regular.otf  # 思源黑体字体
│   └── Workflow/                # ComfyUI工作流文件夹
│       ├── Workflow.json        # 默认图像生成工作流
│       └── audio_workflow.json  # 音频生成工作流
├── static/                      # 静态资源目录
│   ├── css/                     # 样式文件
│   │   ├── style.css            # 主样式文件
│   │   └── system-config.css    # 系统配置页面样式
│   ├── js/                      # JavaScript文件
│   │   ├── main.js              # 主要前端逻辑
│   │   ├── system-config.js     # 系统配置页面脚本
│   │   └── auto-video.js        # 自动视频生成脚本
│   └── images/                  # 图片资源
├── templates/                   # HTML模板目录
│   └── Mainsite/                # 主应用模板
│       ├── index.html           # 首页模板
│       ├── project_management.html  # 项目管理页面
│       ├── text_generation.html     # 文案生成页面
│       ├── image_generation.html    # 图片生成页面
│       ├── audio_generation.html    # 音频生成页面
│       ├── video_generation.html    # 视频生成页面
│       ├── auto_video.html          # 自动视频生成页面
│       └── system_config.html       # 系统配置页面
├── first_sentence_prompts/      # 首句提示词模板目录
├── projects/                    # 项目存储目录（运行时创建）
├── config.ini                   # 系统配置文件
├── requirements.txt             # Python依赖列表
├── README.md                    # 项目说明文档（用户版）
└── MAP.MD                       # 项目技术文档（开发者版）
```

### 文件职责说明

- **manage.py**: 项目的总开关和启动入口，就像电脑的开机按钮。
- **AutoMovie/**: Django主配置目录，存放项目的核心设置。
  - **settings.py**: 项目的"设置面板"，配置数据库、安全等选项。
  - **urls.py**: 主URL路由配置，网站的"总导航图"。
- **Mainsite/**: 存放项目的核心功能代码，就像汽车的发动机舱。
  - **views.py**: 处理用户请求的"大脑"，包含所有业务逻辑（3000+行代码）。
  - **urls.py**: 应用级路由表，告诉系统用户访问哪个网址时该做什么。
- **templates/**: 存放网页模板文件，就像网页的"外观设计图"。
  - **index.html**: 首页模板，项目的"门面"。
  - **project_management.html**: 项目管理页面，管理所有视频项目。
  - **text_generation.html**: 文案生成页面，AI写文案的地方。
  - **image_generation.html**: 图片生成页面，AI画图的地方。
  - **audio_generation.html**: 音频生成页面，AI配音的地方。
  - **video_generation.html**: 视频生成页面，最终成片的地方。
  - **auto_video.html**: 自动视频生成页面，一键生成完整视频。
  - **system_config.html**: 系统配置页面，设置AI服务的地方。
- **static/**: 存放CSS样式、JavaScript脚本和图片等静态资源。
  - **css/**: 样式文件，让网页变漂亮的"化妆师"。
  - **js/**: JavaScript脚本，让网页变聪明的"程序员"。
- **common/**: 存放所有通用小工具的文件夹。
  - **comfyui_client.py**: 与ComfyUI服务通信的"翻译官"，支持图像和音频生成。
  - **video_processor.py**: 视频处理的"剪辑师"，负责拼接、剪切、添加字幕（已使用FFMPEG实现）。
  - **audio_processor.py**: 音频处理的"调音师"，负责去除静音、计算时长、前后停顿控制。
  - **Fonts/**: 字体文件目录，存放思源黑体、霞鹜文楷等多种字体。
  - **Workflow/**: ComfyUI工作流配置文件，AI生成的"配方"，支持多种风格。
  - **back_mus/**: 背景音乐文件目录，存放预设的背景音乐。
- **first_sentence_prompts/**: 首句提示词模板目录，存放文案生成的"灵感库"。
- **projects/**: 项目存储目录，每个视频项目都有独立文件夹。
  - **audios/**: 存放生成的音频文件
  - **images/**: 存放生成的图像文件
  - **videos/**: 存放生成的视频文件
  - **temp/**: 存放临时处理文件
- **requirements.txt**: 项目需要的所有"工具包"清单。
- **config.ini**: 系统配置文件，存储API密钥、服务地址等重要设置。
- **README.md**: 项目说明文档（你正在看的这个），给人类看的"使用手册"。
- **MAP.MD**: 项目技术文档，给AI和开发者看的"技术蓝图"。

## 核心功能逻辑详解（人类版）

#### `generate_first_sentence()`
- **它能做什么**: 根据你输入的主题，自动生成视频文案的第一句话，支持治愈系风格，会自动过滤不合适的符号。
- **什么时候会用到它**: 当你创建新项目时，系统会调用这个功能来生成吸引人的开头，并自动保存到项目配置中。

#### `generate_image()`
- **它能做什么**: 根据文案内容和项目配置，通过ComfyUI自动生成配套的图片，支持治愈动物、治愈动漫等多种艺术风格。
- **什么时候会用到它**: 在文案生成完成后，你点击"生成图片"按钮时会调用这个功能，会自动保存工作流配置。

#### `generate_audio()`
- **它能做什么**: 把文案转换成自然流畅的语音，并自动去除前后的无声部分，支持前后停顿时长精确控制。
- **什么时候会用到它**: 在图片生成完成后，你点击"生成语音"按钮时会调用这个功能，会自动更新项目参数。

#### `create_video()`
- **它能做什么**: 把图片、语音和字幕智能组合成完整的视频文件，支持批量字幕、背景音乐和FFMPEG高性能处理。**已修复视频片段无声音问题，现在会自动将audios文件夹中的音频文件（固定格式script_N_1.wav）添加到对应视频片段，如果音频文件不存在会报错提醒。最终合并的视频输出到项目根目录，支持背景音乐混合（音量默认10%）。**
- **什么时候会用到它**: 当所有素材准备完毕，你点击"生成视频"按钮时会调用这个功能。

#### `ComfyUIClient`类
- **它能做什么**: 负责与ComfyUI服务器通信，支持WebSocket实时监听，自动处理图像和音频生成任务。
- **什么时候会用到它**: 每当需要生成图片或音频时，系统都会通过这个"翻译官"与AI服务对话，支持连接测试。

#### `VideoProcessor`类
- **它能做什么**: 专门处理视频相关的操作，包括FFMPEG拼接、剪切、调整尺寸、添加单个或批量字幕、背景音乐混合等。
- **什么时候会用到它**: 在最终生成视频阶段，需要把各种素材组合成完整视频时，支持多种字体和描边效果，以及淡入淡出特效。

#### `AudioProcessor`类
- **它能做什么**: 专门处理音频相关的操作，包括去除静音、计算时长、前后停顿控制、自动更新项目配置等。
- **什么时候会用到它**: 在音频生成完成后，需要优化音频质量和获取准确时长信息时，会自动保存到parameter.ini文件，支持精确的停顿时长设置。

#### 项目管理功能
- **它能做什么**: 提供完整的项目生命周期管理，包括创建、删除、重命名项目，以及清理各种生成文件。
- **什么时候会用到它**: 在项目管理页面进行项目操作时，支持批量操作和安全验证。

#### 系统配置功能
- **它能做什么**: 管理AI服务配置，包括API密钥、ComfyUI地址、工作流文件等，支持实时测试连接。
- **什么时候会用到它**: 在系统配置页面设置各种AI服务参数时，确保服务正常可用。