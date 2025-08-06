# AutoMovie 函数文档

## 概述

本文档详细介绍 AutoMovie 项目中所有重要函数的功能、参数和使用方法。函数就像工厂里的各种机器，每个都有特定的作用，接收特定的原料（参数），产出特定的产品（返回值）。

## Mainsite/views.py - 主要业务逻辑函数

### 页面渲染函数

#### `index(request)`
- **作用**：显示首页，加载项目介绍内容
- **参数**：
  - `request` - Django 请求对象，包含用户访问信息
- **返回值**：渲染后的首页 HTML 页面
- **用途**：当用户访问网站首页时调用

#### `project_management(request)`
- **作用**：显示项目管理页面
- **参数**：
  - `request` - Django 请求对象
- **返回值**：项目管理页面的 HTML
- **用途**：让用户创建、打开、管理项目

#### `text_generation(request)`
- **作用**：显示文案生成页面
- **参数**：
  - `request` - Django 请求对象
- **返回值**：文案生成页面的 HTML
- **用途**：让用户输入主题，生成视频文案

#### `image_generation(request)`
- **作用**：显示图片生成页面
- **参数**：
  - `request` - Django 请求对象
- **返回值**：图片生成页面的 HTML
- **用途**：根据文案内容生成配套图片

#### `audio_generation(request)`
- **作用**：显示语音生成页面
- **参数**：
  - `request` - Django 请求对象
- **返回值**：语音生成页面的 HTML
- **用途**：将文字转换为语音旁白

#### `video_maker(request)`
- **作用**：显示视频制作页面
- **参数**：
  - `request` - Django 请求对象
- **返回值**：视频制作页面的 HTML
- **用途**：将图片、音频、字幕合成为完整视频

#### `auto_video(request)`
- **作用**：显示自动视频生成页面
- **参数**：
  - `request` - Django 请求对象
- **返回值**：自动视频生成页面的 HTML
- **用途**：一键生成完整视频的高级功能

#### `system_config(request)`
- **作用**：显示系统配置页面
- **参数**：
  - `request` - Django 请求对象
- **返回值**：系统配置页面的 HTML
- **用途**：设置 API 密钥、服务器地址等系统参数

### 项目管理函数

#### `create_project(request)`
- **作用**：创建新项目
- **参数**：
  - `request` - 包含项目名称的 POST 请求
- **返回值**：JSON 格式的创建结果
  - `success`: 是否成功（true/false）
  - `message`: 结果消息
  - `project_path`: 项目路径（成功时）
- **用途**：用户输入项目名称后，系统创建项目文件夹和配置文件

#### `get_current_project(request)`
- **作用**：获取当前打开的项目信息
- **参数**：
  - `request` - GET 请求
- **返回值**：JSON 格式的项目信息
  - `success`: 是否成功
  - `project_name`: 项目名称
  - `project_path`: 项目路径
- **用途**：页面加载时显示当前项目状态

#### `open_project(request)`
- **作用**：打开指定项目
- **参数**：
  - `request` - 包含项目名称的 POST 请求
- **返回值**：JSON 格式的打开结果
- **用途**：用户选择项目后切换到该项目

#### `get_project_list(request)`
- **作用**：获取所有项目列表
- **参数**：
  - `request` - GET 请求
- **返回值**：JSON 格式的项目列表
  - `success`: 是否成功
  - `projects`: 项目数组，每个包含名称、路径、创建时间等
- **用途**：在项目管理页面显示所有可用项目

### 文案生成函数

#### `generate_first_sentence(request)`
- **作用**：生成视频的第一句话
- **参数**：
  - `request` - 包含主题和 prompt 的 POST 请求
- **返回值**：JSON 格式的生成结果
  - `success`: 是否成功
  - `first_sentence`: 生成的第一句话
- **用途**：根据用户输入的主题，AI 生成吸引人的开头句

#### `generate_text(request)`
- **作用**：生成完整的视频文案
- **参数**：
  - `request` - 包含第一句话和生成参数的 POST 请求
- **返回值**：JSON 格式的文案内容
  - `success`: 是否成功
  - `content`: 生成的完整文案
- **用途**：基于第一句话，AI 扩展生成完整的视频脚本

#### `format_text(request)`
- **作用**：格式化文案内容
- **参数**：
  - `request` - 包含原始文案的 POST 请求
- **返回值**：JSON 格式的格式化结果
  - `success`: 是否成功
  - `formatted_content`: 格式化后的文案
- **用途**：将生成的文案按照视频制作需求进行结构化处理

### 图片生成函数

#### `generate_image(request)`
- **作用**：根据文案生成图片
- **参数**：
  - `request` - 包含句子 ID 和生成参数的 POST 请求
- **返回值**：JSON 格式的生成结果
  - `success`: 是否成功
  - `image_paths`: 生成的图片路径列表
- **用途**：为文案中的每句话生成对应的配图

#### `upload_image(request)`
- **作用**：上传自定义图片
- **参数**：
  - `request` - 包含图片文件的 POST 请求
- **返回值**：JSON 格式的上传结果
- **用途**：用户可以上传自己的图片替换 AI 生成的图片

#### `clear_all_images(request)`
- **作用**：清除项目中的所有图片
- **参数**：
  - `request` - POST 请求
- **返回值**：JSON 格式的清除结果
- **用途**：重新生成图片前清理旧文件

### 音频生成函数

#### `generate_audio(request)`
- **作用**：将文字转换为语音
- **参数**：
  - `request` - 包含句子 ID 和语音参数的 POST 请求
- **返回值**：JSON 格式的生成结果
  - `success`: 是否成功
  - `audio_paths`: 生成的音频文件路径
- **用途**：为文案中的每句话生成语音旁白

#### `list_project_audios(request)`
- **作用**：列出项目中的所有音频文件
- **参数**：
  - `request` - GET 请求
- **返回值**：JSON 格式的音频列表
- **用途**：在音频管理页面显示所有可用音频

#### `delete_audio_file(request)`
- **作用**：删除指定音频文件
- **参数**：
  - `request` - 包含文件名的 POST 请求
- **返回值**：JSON 格式的删除结果
- **用途**：清理不需要的音频文件

### 视频生成函数

#### `generate_video(request)`
- **作用**：生成完整视频
- **参数**：
  - `request` - 包含视频参数的 POST 请求
- **返回值**：JSON 格式的生成结果
  - `success`: 是否成功
  - `video_path`: 生成的视频文件路径
- **用途**：将图片、音频、字幕合成为最终视频

#### `get_video_history(request)`
- **作用**：获取视频生成历史
- **参数**：
  - `request` - GET 请求
- **返回值**：JSON 格式的历史记录
- **用途**：显示之前生成的所有视频

#### `delete_video(request)`
- **作用**：删除指定视频文件
- **参数**：
  - `request` - 包含视频路径的 POST 请求
- **返回值**：JSON 格式的删除结果
- **用途**：清理不需要的视频文件

### 配置管理函数

#### `save_model_config(request)`
- **作用**：保存 AI 模型配置
- **参数**：
  - `request` - 包含模型参数的 POST 请求
- **返回值**：JSON 格式的保存结果
- **用途**：设置文案生成、图片生成等 AI 模型的参数

#### `load_model_config(request)`
- **作用**：加载 AI 模型配置
- **参数**：
  - `request` - GET 请求
- **返回值**：JSON 格式的配置数据
- **用途**：页面加载时显示当前的模型设置

#### `save_system_config(request)`
- **作用**：保存系统配置
- **参数**：
  - `request` - 包含系统参数的 POST 请求
- **返回值**：JSON 格式的保存结果
- **用途**：设置 API 密钥、服务器地址等系统级参数

#### `load_system_config(request)`
- **作用**：加载系统配置
- **参数**：
  - `request` - GET 请求
- **返回值**：JSON 格式的配置数据
- **用途**：页面加载时显示当前的系统设置

## common/video_processor.py - 视频处理函数

### VideoProcessor 类的主要方法

#### `generate_video_segment(project_path, segment_index, audio_duration, image_path)`
- **作用**：生成单个视频片段
- **参数**：
  - `project_path` - 项目路径
  - `segment_index` - 片段索引（从1开始）
  - `audio_duration` - 音频时长（秒）
  - `image_path` - 图片路径
- **返回值**：布尔值，表示是否成功
- **用途**：将一张图片和对应音频合成为一个视频片段

#### `concatenate_videos(video_paths, output_path, project_path, fps=24, codec='libx264')`
- **作用**：拼接多个视频片段
- **参数**：
  - `video_paths` - 视频文件路径列表
  - `output_path` - 输出文件路径
  - `project_path` - 项目路径
  - `fps` - 帧率（默认24）
  - `codec` - 视频编码器（默认libx264）
- **返回值**：布尔值，表示是否成功
- **用途**：将多个视频片段合并为完整视频

#### `add_subtitle(video_path, output_path, subtitle_text, start_time, duration, ...)`
- **作用**：为视频添加字幕
- **参数**：
  - `video_path` - 输入视频路径
  - `output_path` - 输出视频路径
  - `subtitle_text` - 字幕文字
  - `start_time` - 开始时间
  - `duration` - 持续时间
  - 其他字幕样式参数
- **返回值**：布尔值，表示是否成功
- **用途**：在视频上叠加文字字幕

#### `get_video_info(video_path)`
- **作用**：获取视频文件信息
- **参数**：
  - `video_path` - 视频文件路径
- **返回值**：包含视频信息的字典（时长、分辨率、帧率等）
- **用途**：分析视频文件的基本属性

## common/audio_processor.py - 音频处理函数

### AudioProcessor 类的主要方法

#### `trim_silence(audio_path, output_path=None, silence_threshold=0.01, ...)`
- **作用**：去除音频前后的无声部分
- **参数**：
  - `audio_path` - 输入音频路径
  - `output_path` - 输出音频路径（可选）
  - `silence_threshold` - 静音阈值（0-1之间）
  - `pre_pause` - 前停顿时长（秒）
  - `post_pause` - 后停顿时长（秒）
- **返回值**：元组 (处理后的文件路径, 音频时长)
- **用途**：清理音频文件，去除多余的静音部分

#### `get_audio_duration(audio_path)`
- **作用**：获取音频文件时长
- **参数**：
  - `audio_path` - 音频文件路径
- **返回值**：音频时长（秒）
- **用途**：计算音频播放时间，用于视频同步

#### `process_audio_after_generation(audio_path, project_path, script_id)`
- **作用**：音频生成后的后处理
- **参数**：
  - `audio_path` - 原始音频路径
  - `project_path` - 项目路径
  - `script_id` - 脚本ID
- **返回值**：元组 (处理后的文件路径, 音频时长)
- **用途**：对新生成的音频进行标准化处理

#### `update_parameter_ini(project_path, script_id, duration)`
- **作用**：更新项目参数文件中的音频时长
- **参数**：
  - `project_path` - 项目路径
  - `script_id` - 脚本ID
  - `duration` - 音频时长
- **返回值**：布尔值，表示是否成功
- **用途**：记录每个音频片段的时长信息

## common/comfyui_client.py - AI图像生成函数

### ComfyUIClient 类的主要方法

#### `__init__(server_address=None)`
- **作用**：初始化 ComfyUI 客户端
- **参数**：
  - `server_address` - ComfyUI 服务器地址（可选）
- **返回值**：无
- **用途**：创建与 ComfyUI 服务的连接

#### `generate_image(project_path, sentence_id=1, seed=None)`
- **作用**：生成图片
- **参数**：
  - `project_path` - 项目路径
  - `sentence_id` - 句子ID（默认1）
  - `seed` - 随机种子（可选）
- **返回值**：生成的图片文件路径列表
- **用途**：根据文案内容生成对应的图片

#### `test_connection()`
- **作用**：测试与 ComfyUI 服务器的连接
- **参数**：无
- **返回值**：布尔值，表示连接是否正常
- **用途**：检查 AI 图像生成服务是否可用

#### `queue_prompt(prompt)`
- **作用**：向 ComfyUI 发送生成请求
- **参数**：
  - `prompt` - 包含生成参数的字典
- **返回值**：包含任务ID的响应字典
- **用途**：提交图像生成任务到队列

#### `get_images_from_websocket(prompt)`
- **作用**：通过 WebSocket 获取生成的图片
- **参数**：
  - `prompt` - 生成参数字典
- **返回值**：图片URL列表
- **用途**：实时接收 AI 生成的图片结果

## 函数调用关系

### 典型的视频制作流程中的函数调用链

1. **项目创建流程**：
   ```
   create_project() → 创建文件夹 → AudioProcessor.create_project_parameter_ini()
   ```

2. **文案生成流程**：
   ```
   generate_first_sentence() → AI API调用 → generate_text() → format_text()
   ```

3. **图片生成流程**：
   ```
   generate_image() → ComfyUIClient.generate_image() → queue_prompt() → get_images_from_websocket()
   ```

4. **音频生成流程**：
   ```
   generate_audio() → AI API调用 → AudioProcessor.process_audio_after_generation() → trim_silence()
   ```

5. **视频合成流程**：
   ```
   generate_video() → VideoProcessor.generate_video_segment() → concatenate_videos() → add_subtitle()
   ```

### 配置管理流程

```
load_system_config() → 读取config.ini → save_system_config() → 写入config.ini
```

### 项目管理流程

```
get_project_list() → 扫描projects目录 → open_project() → 设置当前项目
```

## 错误处理机制

大部分函数都包含 try-catch 错误处理：

1. **捕获异常**：使用 try-except 块捕获可能的错误
2. **记录日志**：使用 logger 记录详细错误信息
3. **返回结果**：统一返回 JSON 格式的成功/失败状态
4. **用户提示**：向前端返回用户友好的错误消息

这种设计确保了系统的稳定性和用户体验的友好性。