# AutoMovie 静态文件目录结构

本目录包含了 AutoMovie 项目的所有静态文件，按照 Django 最佳实践进行组织。

## 目录结构

```
static/
├── css/
│   ├── base.css           # 基础样式（全局样式、布局、通用组件）
│   ├── components.css      # UI组件样式（播放器、预览器、上传器等）
│   └── responsive.css      # 响应式样式（移动端适配、媒体查询）
├── js/
│   ├── common.js          # 通用工具函数（CSRF、状态消息、工具函数等）
│   ├── modules/
│   │   ├── audio.js       # 音频相关模块（播放器、生成器、管理器）
│   │   ├── image.js       # 图片相关模块（生成器、预览器、上传器）
│   │   └── video.js       # 视频相关模块（播放器、编辑器、生成器）
│   └── pages/
│       └── text-generation.js  # 文案生成页面专用脚本
└── README.md              # 本说明文件
```

## 文件说明

### CSS 文件

#### `css/base.css`
- 全局样式重置和基础样式
- 页面布局（侧边栏、内容区域）
- 通用按钮、表单、提示框样式
- 基础响应式断点

#### `css/components.css`
- 音频播放器组件样式
- 图片预览和灯箱样式
- 图片上传器样式
- 视频播放器和时间轴样式
- 状态消息、加载动画、进度条样式
- 模态框样式

#### `css/responsive.css`
- 针对不同屏幕尺寸的响应式样式
- 移动端优化
- 打印样式
- 无障碍访问支持（高对比度、减少动画）
- 暗色主题支持

### JavaScript 文件

#### `js/common.js`
包含全局通用功能：
- CSRF Token 获取
- 状态消息显示
- 文件大小和时间格式化
- 防抖和节流函数
- 表单验证
- 加载状态管理
- 通用 AJAX 请求封装

#### `js/modules/audio.js`
音频相关功能模块：
- `AudioManager`: 音频播放、暂停、音量控制
- `AudioGenerator`: 通过 API 生成音频
- `AudioPlayer`: 音频播放器 UI 组件

#### `js/modules/image.js`
图片相关功能模块：
- `ImageGenerator`: 图片生成功能
- `ImagePreview`: 图片预览组件
- `ImageUploader`: 图片上传组件

#### `js/modules/video.js`
视频相关功能模块：
- `VideoGenerator`: 视频生成和进度查询
- `VideoPlayer`: 视频播放器组件
- `VideoEditor`: 视频编辑器和时间轴

#### `js/pages/text-generation.js`
文案生成页面专用脚本：
- PROMPT 文件管理
- 文案生成功能
- 页面特定的交互逻辑

## 使用方法

### 在 Django 模板中引用

```html
{% load static %}

<!-- 引用 CSS -->
<link rel="stylesheet" href="{% static 'css/base.css' %}">
<link rel="stylesheet" href="{% static 'css/components.css' %}">
<link rel="stylesheet" href="{% static 'css/responsive.css' %}">

<!-- 引用 JavaScript -->
<script src="{% static 'js/common.js' %}"></script>
<script src="{% static 'js/modules/audio.js' %}"></script>
<script src="{% static 'js/modules/image.js' %}"></script>
<script src="{% static 'js/modules/video.js' %}"></script>

<!-- 页面特定脚本 -->
<script src="{% static 'js/pages/text-generation.js' %}"></script>
```

### 模块化使用

所有 JavaScript 模块都通过 `window.AutoMovie` 命名空间暴露：

```javascript
// 使用音频管理器
const audioManager = new AutoMovie.AudioManager();
audioManager.play('audio-url');

// 使用图片生成器
const imageGen = new AutoMovie.ImageGenerator();
imageGen.generate(prompt, options);

// 显示状态消息
AutoMovie.showStatus('操作成功', 'success');

// 格式化文件大小
const size = AutoMovie.formatFileSize(1024000); // "1.02 MB"
```

## 开发指南

### 添加新的 CSS 样式

1. **全局样式**: 添加到 `css/base.css`
2. **组件样式**: 添加到 `css/components.css`
3. **响应式样式**: 添加到 `css/responsive.css`

### 添加新的 JavaScript 功能

1. **通用工具函数**: 添加到 `js/common.js`
2. **功能模块**: 在 `js/modules/` 下创建新文件
3. **页面特定脚本**: 在 `js/pages/` 下创建新文件

### 命名规范

- CSS 类名使用 kebab-case: `.audio-player`, `.image-preview`
- JavaScript 函数使用 camelCase: `showStatus()`, `formatFileSize()`
- JavaScript 类使用 PascalCase: `AudioManager`, `ImageGenerator`
- 文件名使用 kebab-case: `text-generation.js`, `components.css`

### 代码组织原则

1. **单一职责**: 每个文件只负责特定功能
2. **模块化**: 使用 IIFE 避免全局污染
3. **命名空间**: 所有功能通过 `AutoMovie` 命名空间暴露
4. **依赖管理**: 明确标注文件间的依赖关系
5. **向后兼容**: 保持 API 稳定性

## 迁移指南

从内联样式和脚本迁移到静态文件：

1. 将 `<style>` 标签中的 CSS 移动到对应的 CSS 文件
2. 将 `<script>` 标签中的 JavaScript 移动到对应的 JS 文件
3. 更新模板文件，使用 `{% static %}` 标签引用文件
4. 测试功能确保迁移正确

## 性能优化

- CSS 文件按加载优先级排序（base → components → responsive）
- JavaScript 文件按依赖关系排序（common → modules → pages）
- 生产环境建议压缩和合并文件
- 使用 CDN 加速静态文件加载