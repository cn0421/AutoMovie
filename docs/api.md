# AutoMovie API 文档

## 概述

本文档详细介绍 AutoMovie 项目中所有的 API 接口，包括前端页面调用的后端接口、第三方 API 集成以及内部模块间的数据交互。每个 API 就像是系统的神经网络，连接着各个功能模块。

## API 架构说明

### API 分层结构

**1. 前端 API 层**
- 处理用户界面的请求
- 数据格式转换和验证
- 用户权限检查

**2. 业务逻辑层**
- 核心业务处理
- 数据处理和转换
- 工作流控制

**3. 第三方集成层**
- AI 服务 API 调用
- 外部工具集成
- 数据同步处理

**4. 数据存储层**
- 文件系统操作
- 配置文件管理
- 项目数据管理

## 前端 API 接口

### 1. 项目管理 API

#### 1.1 获取项目列表

**接口地址**：`/api/projects/list/`  
**请求方法**：GET  
**功能描述**：获取所有项目的列表信息

**请求参数**：无

**响应格式**：
```json
{
  "status": "success",
  "data": [
    {
      "name": "我的第一个视频",
      "created_time": "2024-01-15 10:30:00",
      "status": "进行中",
      "file_count": {
        "text": 1,
        "image": 5,
        "audio": 3,
        "video": 1
      }
    }
  ]
}
```

**使用场景**：项目管理页面加载时调用，显示所有可用项目

#### 1.2 创建新项目

**接口地址**：`/api/projects/create/`  
**请求方法**：POST  
**功能描述**：创建一个新的视频项目

**请求参数**：
```json
{
  "project_name": "项目名称"
}
```

**响应格式**：
```json
{
  "status": "success",
  "message": "项目创建成功",
  "project_name": "我的新项目"
}
```

**错误处理**：
- 项目名称为空：返回错误信息
- 项目名称重复：提示用户修改名称
- 磁盘空间不足：提示清理空间

#### 1.3 打开项目

**接口地址**：`/api/projects/open/`  
**请求方法**：POST  
**功能描述**：切换到指定的项目

**请求参数**：
```json
{
  "project_name": "要打开的项目名称"
}
```

**响应格式**：
```json
{
  "status": "success",
  "message": "项目已打开",
  "current_project": "我的项目"
}
```

#### 1.4 删除项目

**接口地址**：`/api/projects/delete/`  
**请求方法**：POST  
**功能描述**：删除指定的项目及其所有文件

**请求参数**：
```json
{
  "project_name": "要删除的项目名称"
}
```

**响应格式**：
```json
{
  "status": "success",
  "message": "项目已删除"
}
```

### 2. 文案生成 API

#### 2.1 获取第一句话 Prompt 列表

**接口地址**：`/api/first_sentence_prompt/list/`  
**请求方法**：GET  
**功能描述**：获取所有可用的第一句话生成模板

**响应格式**：
```json
{
  "status": "success",
  "data": [
    {
      "filename": "formal_style.txt",
      "display_name": "正式风格",
      "description": "适合商务和教育类视频"
    },
    {
      "filename": "casual_style.txt",
      "display_name": "轻松风格",
      "description": "适合娱乐和生活类视频"
    }
  ]
}
```

#### 2.2 获取 Prompt 内容

**接口地址**：`/api/first_sentence_prompt/content/`  
**请求方法**：POST  
**功能描述**：获取指定 Prompt 文件的具体内容

**请求参数**：
```json
{
  "filename": "formal_style.txt"
}
```

**响应格式**：
```json
{
  "status": "success",
  "content": "你是一个专业的文案写手，请根据给定主题生成一个吸引人的开头句..."
}
```

#### 2.3 删除 Prompt

**接口地址**：`/api/first_sentence_prompt/delete/`  
**请求方法**：POST  
**功能描述**：删除指定的 Prompt 文件

**请求参数**：
```json
{
  "filename": "要删除的文件名"
}
```

#### 2.4 生成第一句话

**接口地址**：`/api/text/generate_first_sentence/`  
**请求方法**：POST  
**功能描述**：基于主题和 Prompt 生成吸引人的开头句

**请求参数**：
```json
{
  "topic": "人工智能的发展",
  "prompt_file": "formal_style.txt",
  "style": "专业"
}
```

**响应格式**：
```json
{
  "status": "success",
  "first_sentence": "在这个科技飞速发展的时代，人工智能正在悄然改变着我们的生活方式。"
}
```

#### 2.5 生成完整文案

**接口地址**：`/api/text/generate_full_script/`  
**请求方法**：POST  
**功能描述**：基于第一句话扩展生成完整的视频文案

**请求参数**：
```json
{
  "first_sentence": "在这个科技飞速发展的时代...",
  "target_length": "medium",
  "style": "专业",
  "audience": "普通观众"
}
```

**响应格式**：
```json
{
  "status": "success",
  "full_script": "在这个科技飞速发展的时代，人工智能正在悄然改变着我们的生活方式。从智能手机到自动驾驶汽车...",
  "sentence_count": 8,
  "estimated_duration": "45秒"
}
```

#### 2.6 保存文案

**接口地址**：`/api/text/save/`  
**请求方法**：POST  
**功能描述**：将生成或编辑的文案保存到项目中

**请求参数**：
```json
{
  "content": "完整的文案内容",
  "project_name": "我的项目"
}
```

### 3. 图片生成 API

#### 3.1 获取文案句子列表

**接口地址**：`/api/images/get_sentences/`  
**请求方法**：GET  
**功能描述**：获取当前项目文案中的所有句子

**响应格式**：
```json
{
  "status": "success",
  "sentences": [
    {
      "index": 0,
      "content": "在这个科技飞速发展的时代，人工智能正在悄然改变着我们的生活方式。",
      "has_image": true,
      "image_count": 2
    }
  ]
}
```

#### 3.2 生成图片

**接口地址**：`/api/images/generate/`  
**请求方法**：POST  
**功能描述**：为指定句子生成配套图片

**请求参数**：
```json
{
  "sentence_index": 0,
  "sentence_content": "句子内容",
  "style": "realistic",
  "size": "16:9",
  "quality": "standard",
  "count": 2
}
```

**响应格式**：
```json
{
  "status": "success",
  "task_id": "img_task_12345",
  "message": "图片生成任务已提交"
}
```

#### 3.3 检查生成状态

**接口地址**：`/api/images/status/`  
**请求方法**：POST  
**功能描述**：检查图片生成任务的状态

**请求参数**：
```json
{
  "task_id": "img_task_12345"
}
```

**响应格式**：
```json
{
  "status": "success",
  "task_status": "completed",
  "progress": 100,
  "images": [
    {
      "filename": "sentence_0_image_1.png",
      "url": "/media/projects/my_project/images/sentence_0_image_1.png"
    }
  ]
}
```

#### 3.4 获取项目图片

**接口地址**：`/api/images/list/`  
**请求方法**：GET  
**功能描述**：获取当前项目中所有的图片文件

**响应格式**：
```json
{
  "status": "success",
  "images": [
    {
      "sentence_index": 0,
      "filename": "sentence_0_image_1.png",
      "url": "/media/projects/my_project/images/sentence_0_image_1.png",
      "size": "1920x1080",
      "file_size": "2.5MB"
    }
  ]
}
```

#### 3.5 删除图片

**接口地址**：`/api/images/delete/`  
**请求方法**：POST  
**功能描述**：删除指定的图片文件

**请求参数**：
```json
{
  "filename": "sentence_0_image_1.png"
}
```

### 4. 音频生成 API

#### 4.1 生成语音

**接口地址**：`/api/audio/generate/`  
**请求方法**：POST  
**功能描述**：将文字转换为语音

**请求参数**：
```json
{
  "text": "要转换的文字内容",
  "voice": "female_standard",
  "speed": "normal",
  "pitch": "standard",
  "emotion": "neutral"
}
```

**响应格式**：
```json
{
  "status": "success",
  "task_id": "audio_task_12345",
  "estimated_duration": "5秒"
}
```

#### 4.2 检查音频生成状态

**接口地址**：`/api/audio/status/`  
**请求方法**：POST  
**功能描述**：检查语音生成任务的状态

**请求参数**：
```json
{
  "task_id": "audio_task_12345"
}
```

**响应格式**：
```json
{
  "status": "success",
  "task_status": "completed",
  "audio_file": "sentence_0_audio.wav",
  "duration": "4.2秒",
  "file_size": "1.2MB"
}
```

#### 4.3 获取项目音频

**接口地址**：`/api/audio/list/`  
**请求方法**：GET  
**功能描述**：获取当前项目中所有的音频文件

**响应格式**：
```json
{
  "status": "success",
  "audio_files": [
    {
      "sentence_index": 0,
      "filename": "sentence_0_audio.wav",
      "url": "/media/projects/my_project/audio/sentence_0_audio.wav",
      "duration": "4.2秒",
      "file_size": "1.2MB"
    }
  ]
}
```

#### 4.4 音频处理

**接口地址**：`/api/audio/process/`  
**请求方法**：POST  
**功能描述**：对音频进行后处理（去静音、标准化等）

**请求参数**：
```json
{
  "filename": "sentence_0_audio.wav",
  "operations": [
    "trim_silence",
    "normalize_volume"
  ]
}
```

### 5. 视频制作 API

#### 5.1 获取项目素材

**接口地址**：`/api/video/get_materials/`  
**请求方法**：GET  
**功能描述**：获取当前项目中所有可用的素材

**响应格式**：
```json
{
  "status": "success",
  "materials": {
    "text": "完整的文案内容",
    "sentences": ["句子1", "句子2"],
    "images": [
      {
        "sentence_index": 0,
        "filename": "image1.png",
        "url": "/media/path/image1.png"
      }
    ],
    "audio": [
      {
        "sentence_index": 0,
        "filename": "audio1.wav",
        "duration": 4.2
      }
    ]
  }
}
```

#### 5.2 生成视频

**接口地址**：`/api/video/generate/`  
**请求方法**：POST  
**功能描述**：将素材合成为完整视频

**请求参数**：
```json
{
  "resolution": "1920x1080",
  "fps": 30,
  "quality": "high",
  "subtitle_style": {
    "font": "Arial",
    "size": 24,
    "color": "white",
    "position": "bottom"
  },
  "transition_effect": "fade",
  "background_music": {
    "enabled": true,
    "volume": 0.3
  }
}
```

**响应格式**：
```json
{
  "status": "success",
  "task_id": "video_task_12345",
  "estimated_time": "2分钟"
}
```

#### 5.3 检查视频生成状态

**接口地址**：`/api/video/status/`  
**请求方法**：POST  
**功能描述**：检查视频生成任务的状态

**请求参数**：
```json
{
  "task_id": "video_task_12345"
}
```

**响应格式**：
```json
{
  "status": "success",
  "task_status": "processing",
  "progress": 65,
  "current_step": "添加字幕中...",
  "estimated_remaining": "45秒"
}
```

### 6. 自动视频生成 API

#### 6.1 一键生成视频

**接口地址**：`/api/auto_video/generate/`  
**请求方法**：POST  
**功能描述**：从主题到完整视频的一键生成

**请求参数**：
```json
{
  "topic": "人工智能的发展",
  "style": "professional",
  "duration": "medium",
  "project_name": "AI发展视频"
}
```

**响应格式**：
```json
{
  "status": "success",
  "task_id": "auto_video_12345",
  "estimated_time": "5分钟",
  "steps": [
    "文案生成",
    "图片生成",
    "语音生成",
    "视频合成"
  ]
}
```

#### 6.2 检查自动生成状态

**接口地址**：`/api/auto_video/status/`  
**请求方法**：POST  
**功能描述**：检查自动视频生成的整体进度

**请求参数**：
```json
{
  "task_id": "auto_video_12345"
}
```

**响应格式**：
```json
{
  "status": "success",
  "overall_progress": 75,
  "current_step": "语音生成",
  "step_progress": 50,
  "steps_completed": [
    {
      "step": "文案生成",
      "status": "completed",
      "result": "文案已生成"
    },
    {
      "step": "图片生成",
      "status": "completed",
      "result": "5张图片已生成"
    }
  ],
  "estimated_remaining": "1分30秒"
}
```

### 7. 系统配置 API

#### 7.1 获取配置

**接口地址**：`/api/config/get/`  
**请求方法**：GET  
**功能描述**：获取当前系统配置

**响应格式**：
```json
{
  "status": "success",
  "config": {
    "comfyui_address": "http://localhost:8188",
    "text_api_key": "sk-***",
    "audio_api_key": "***",
    "default_resolution": "1920x1080",
    "max_concurrent_tasks": 3
  }
}
```

#### 7.2 更新配置

**接口地址**：`/api/config/update/`  
**请求方法**：POST  
**功能描述**：更新系统配置参数

**请求参数**：
```json
{
  "comfyui_address": "http://localhost:8188",
  "text_api_key": "新的API密钥",
  "default_resolution": "1920x1080"
}
```

#### 7.3 测试连接

**接口地址**：`/api/config/test_connection/`  
**请求方法**：POST  
**功能描述**：测试各种 API 服务的连接状态

**请求参数**：
```json
{
  "service": "comfyui"
}
```

**响应格式**：
```json
{
  "status": "success",
  "connection_status": "connected",
  "response_time": "150ms",
  "service_info": {
    "version": "1.0.0",
    "available_models": ["model1", "model2"]
  }
}
```

## 第三方 API 集成

### 1. ComfyUI API 集成

#### 连接管理

**WebSocket 连接**
- 地址：`ws://localhost:8188/ws`
- 用途：实时获取生成进度和结果
- 心跳机制：每30秒发送ping保持连接

**HTTP API**
- 基础地址：`http://localhost:8188`
- 主要端点：
  - `/prompt`：提交生成任务
  - `/queue`：查看任务队列
  - `/history`：获取历史记录

#### 工作流管理

**工作流加载**
```python
def load_workflow(workflow_path):
    """加载 ComfyUI 工作流文件"""
    with open(workflow_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

**参数更新**
```python
def update_workflow_params(workflow, params):
    """更新工作流中的参数"""
    for node_id, node_params in params.items():
        if node_id in workflow:
            workflow[node_id]['inputs'].update(node_params)
    return workflow
```

#### 任务提交和监控

**提交任务**
```python
def submit_task(workflow):
    """提交生成任务到 ComfyUI"""
    response = requests.post(
        f"{self.base_url}/prompt",
        json={"prompt": workflow}
    )
    return response.json()['prompt_id']
```

**监控进度**
```python
def monitor_progress(prompt_id):
    """通过 WebSocket 监控任务进度"""
    # WebSocket 消息处理逻辑
    # 实时更新进度状态
```

### 2. 文案生成 API 集成

#### OpenAI API

**配置管理**
```python
class TextGenerationAPI:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(api_key=api_key, base_url=base_url)
```

**文案生成**
```python
def generate_text(self, prompt, max_tokens=500):
    """调用 API 生成文案"""
    response = self.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个专业的文案写手"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content
```

### 3. 语音合成 API 集成

#### TTS 服务集成

**音频生成**
```python
def text_to_speech(self, text, voice_params):
    """文字转语音"""
    response = requests.post(
        f"{self.tts_api_url}/synthesize",
        json={
            "text": text,
            "voice": voice_params['voice'],
            "speed": voice_params['speed'],
            "pitch": voice_params['pitch']
        }
    )
    return response.content  # 音频数据
```

**音频处理**
```python
def process_audio(self, audio_data, operations):
    """音频后处理"""
    if 'trim_silence' in operations:
        audio_data = self.trim_silence(audio_data)
    if 'normalize_volume' in operations:
        audio_data = self.normalize_volume(audio_data)
    return audio_data
```

## 内部模块 API

### 1. 文件管理 API

#### 项目文件操作

**创建项目目录**
```python
def create_project_structure(project_name):
    """创建项目目录结构"""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    os.makedirs(os.path.join(project_path, 'text'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'images'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'audio'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'video'), exist_ok=True)
    return project_path
```

**文件保存**
```python
def save_file(project_name, file_type, filename, content):
    """保存文件到项目目录"""
    file_path = os.path.join(
        PROJECTS_DIR, project_name, file_type, filename
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path
```

### 2. 配置管理 API

#### 配置文件操作

**读取配置**
```python
def load_config():
    """加载系统配置"""
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config
```

**更新配置**
```python
def update_config(section, key, value):
    """更新配置项"""
    config = load_config()
    if section not in config:
        config.add_section(section)
    config.set(section, key, value)
    
    with open('config.ini', 'w', encoding='utf-8') as f:
        config.write(f)
```

### 3. 任务队列 API

#### 异步任务管理

**任务提交**
```python
class TaskQueue:
    def __init__(self):
        self.tasks = {}
        self.task_counter = 0
    
    def submit_task(self, task_type, params):
        """提交异步任务"""
        task_id = f"{task_type}_{self.task_counter}"
        self.task_counter += 1
        
        task = {
            'id': task_id,
            'type': task_type,
            'params': params,
            'status': 'pending',
            'progress': 0,
            'result': None
        }
        
        self.tasks[task_id] = task
        self._execute_task(task)
        return task_id
```

**任务状态查询**
```python
def get_task_status(self, task_id):
    """获取任务状态"""
    if task_id in self.tasks:
        return self.tasks[task_id]
    return None
```

## API 错误处理

### 错误码定义

**通用错误码**
- `1000`：请求参数错误
- `1001`：项目不存在
- `1002`：文件不存在
- `1003`：权限不足
- `1004`：磁盘空间不足

**业务错误码**
- `2000`：文案生成失败
- `2001`：图片生成失败
- `2002`：音频生成失败
- `2003`：视频合成失败
- `2004`：API 服务不可用

### 错误响应格式

```json
{
  "status": "error",
  "error_code": 2000,
  "message": "文案生成失败：API 密钥无效",
  "details": {
    "api_response": "Invalid API key",
    "suggestion": "请检查 API 密钥配置"
  }
}
```

### 重试机制

**自动重试**
```python
def api_call_with_retry(func, max_retries=3, delay=1):
    """带重试的 API 调用"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))  # 指数退避
```

## API 性能优化

### 1. 缓存策略

**结果缓存**
```python
class APICache:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 3600  # 1小时
    
    def get_cached_result(self, cache_key):
        """获取缓存结果"""
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item['timestamp'] < self.cache_timeout:
                return cached_item['data']
        return None
```

### 2. 并发控制

**请求限流**
```python
class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def allow_request(self):
        """检查是否允许请求"""
        now = time.time()
        # 清理过期请求
        self.requests = [req for req in self.requests 
                        if now - req < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
```

### 3. 异步处理

**异步任务执行**
```python
import asyncio

async def async_api_call(url, data):
    """异步 API 调用"""
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

async def batch_process(tasks):
    """批量异步处理"""
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## API 安全措施

### 1. 身份验证

**API 密钥验证**
```python
def verify_api_key(request):
    """验证 API 密钥"""
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != VALID_API_KEY:
        raise PermissionError("Invalid API key")
```

### 2. 输入验证

**参数验证**
```python
def validate_request_params(params, schema):
    """验证请求参数"""
    for field, rules in schema.items():
        if field not in params and rules.get('required', False):
            raise ValueError(f"Missing required field: {field}")
        
        if field in params:
            value = params[field]
            if 'type' in rules and not isinstance(value, rules['type']):
                raise ValueError(f"Invalid type for field: {field}")
```

### 3. 数据加密

**敏感数据加密**
```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        """加密数据"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """解密数据"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

## API 监控和日志

### 1. 请求日志

**日志记录**
```python
import logging

def log_api_request(request, response, duration):
    """记录 API 请求日志"""
    logger.info({
        'method': request.method,
        'url': request.url,
        'status_code': response.status_code,
        'duration': duration,
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr
    })
```

### 2. 性能监控

**响应时间监控**
```python
def monitor_api_performance(func):
    """API 性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            log_performance(func.__name__, duration, 'success')
            return result
        except Exception as e:
            duration = time.time() - start_time
            log_performance(func.__name__, duration, 'error')
            raise e
    return wrapper
```

这套完整的 API 体系确保了 AutoMovie 项目各个模块之间的高效协作，为用户提供了流畅的视频制作体验。通过合理的架构设计、错误处理、性能优化和安全措施，系统能够稳定可靠地运行。