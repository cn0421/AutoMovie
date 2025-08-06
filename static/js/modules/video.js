/**
 * AutoMovie 视频处理模块
 * 处理视频生成、预览、编辑等功能
 */

(function() {
    'use strict';
    
    // 视频生成器
    const VideoGenerator = {
        // 生成视频
        generate: function(options = {}) {
            const formData = new FormData();
            
            if (options.script) {
                formData.append('script', JSON.stringify(options.script));
            }
            
            if (options.images) {
                options.images.forEach((image, index) => {
                    formData.append(`image_${index}`, image);
                });
            }
            
            if (options.audio) {
                formData.append('audio', options.audio);
            }
            
            if (options.duration) {
                formData.append('duration', options.duration);
            }
            
            if (options.fps) {
                formData.append('fps', options.fps);
            }
            
            if (options.resolution) {
                formData.append('resolution', options.resolution);
            }
            
            if (options.transition) {
                formData.append('transition', options.transition);
            }
            
            return fetch('/video_maker/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': AutoMovie.getCookie('csrftoken')
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            });
        },
        
        // 获取生成进度
        getProgress: function(taskId) {
            return fetch(`/video_maker/progress/${taskId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': AutoMovie.getCookie('csrftoken')
                }
            })
            .then(response => response.json());
        },
        
        // 取消生成任务
        cancelTask: function(taskId) {
            return fetch(`/video_maker/cancel/${taskId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': AutoMovie.getCookie('csrftoken')
                }
            })
            .then(response => response.json());
        }
    };
    
    // 视频播放器
    const VideoPlayer = {
        // 创建播放器
        createPlayer: function(containerId, videoSrc, options = {}) {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error('播放器容器未找到:', containerId);
                return;
            }
            
            const playerHTML = `
                <div class="video-player">
                    <div class="video-container">
                        <video class="video-element" ${options.autoplay ? 'autoplay' : ''} ${options.loop ? 'loop' : ''} ${options.muted ? 'muted' : ''}>
                            <source src="${videoSrc}" type="video/mp4">
                            您的浏览器不支持视频播放。
                        </video>
                        <div class="video-overlay">
                            <button class="play-pause-btn">▶</button>
                        </div>
                    </div>
                    <div class="video-controls">
                        <button class="control-btn play-pause">▶</button>
                        <div class="progress-container">
                            <div class="progress-bar">
                                <div class="progress-buffer"></div>
                                <div class="progress-fill"></div>
                                <div class="progress-handle"></div>
                            </div>
                        </div>
                        <span class="time-display">00:00 / 00:00</span>
                        <div class="volume-container">
                            <button class="volume-btn">🔊</button>
                            <div class="volume-slider-container">
                                <input type="range" class="volume-slider" min="0" max="100" value="50">
                            </div>
                        </div>
                        <button class="fullscreen-btn">⛶</button>
                    </div>
                </div>
            `;
            
            container.innerHTML = playerHTML;
            
            // 绑定事件
            this.bindPlayerEvents(container);
            
            return container.querySelector('.video-element');
        },
        
        // 绑定播放器事件
        bindPlayerEvents: function(container) {
            const video = container.querySelector('.video-element');
            const playPauseBtn = container.querySelector('.play-pause');
            const overlayBtn = container.querySelector('.play-pause-btn');
            const progressBar = container.querySelector('.progress-bar');
            const progressFill = container.querySelector('.progress-fill');
            const progressHandle = container.querySelector('.progress-handle');
            const timeDisplay = container.querySelector('.time-display');
            const volumeBtn = container.querySelector('.volume-btn');
            const volumeSlider = container.querySelector('.volume-slider');
            const fullscreenBtn = container.querySelector('.fullscreen-btn');
            const videoContainer = container.querySelector('.video-container');
            
            let isDragging = false;
            
            // 播放/暂停
            const togglePlayPause = () => {
                if (video.paused) {
                    video.play();
                    playPauseBtn.textContent = '⏸';
                    overlayBtn.textContent = '⏸';
                } else {
                    video.pause();
                    playPauseBtn.textContent = '▶';
                    overlayBtn.textContent = '▶';
                }
            };
            
            playPauseBtn.addEventListener('click', togglePlayPause);
            overlayBtn.addEventListener('click', togglePlayPause);
            video.addEventListener('click', togglePlayPause);
            
            // 时间更新
            video.addEventListener('timeupdate', () => {
                if (!isDragging) {
                    const percent = (video.currentTime / video.duration) * 100;
                    progressFill.style.width = percent + '%';
                    progressHandle.style.left = percent + '%';
                }
                
                const currentTime = AutoMovie.formatDuration(video.currentTime);
                const duration = AutoMovie.formatDuration(video.duration || 0);
                timeDisplay.textContent = `${currentTime} / ${duration}`;
            });
            
            // 进度条拖拽
            const updateProgress = (e) => {
                const rect = progressBar.getBoundingClientRect();
                const percent = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
                video.currentTime = (percent / 100) * video.duration;
            };
            
            progressBar.addEventListener('mousedown', (e) => {
                isDragging = true;
                updateProgress(e);
            });
            
            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    updateProgress(e);
                }
            });
            
            document.addEventListener('mouseup', () => {
                isDragging = false;
            });
            
            // 音量控制
            volumeSlider.addEventListener('input', (e) => {
                const volume = e.target.value / 100;
                video.volume = volume;
                
                if (volume === 0) {
                    volumeBtn.textContent = '🔇';
                } else if (volume < 0.5) {
                    volumeBtn.textContent = '🔉';
                } else {
                    volumeBtn.textContent = '🔊';
                }
            });
            
            // 静音切换
            volumeBtn.addEventListener('click', () => {
                video.muted = !video.muted;
                if (video.muted) {
                    volumeBtn.textContent = '🔇';
                } else {
                    volumeBtn.textContent = '🔊';
                }
            });
            
            // 全屏
            fullscreenBtn.addEventListener('click', () => {
                if (document.fullscreenElement) {
                    document.exitFullscreen();
                } else {
                    videoContainer.requestFullscreen();
                }
            });
            
            // 键盘快捷键
            document.addEventListener('keydown', (e) => {
                if (e.target.tagName.toLowerCase() === 'input') return;
                
                switch (e.code) {
                    case 'Space':
                        e.preventDefault();
                        togglePlayPause();
                        break;
                    case 'ArrowLeft':
                        video.currentTime = Math.max(0, video.currentTime - 10);
                        break;
                    case 'ArrowRight':
                        video.currentTime = Math.min(video.duration, video.currentTime + 10);
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        video.volume = Math.min(1, video.volume + 0.1);
                        volumeSlider.value = video.volume * 100;
                        break;
                    case 'ArrowDown':
                        e.preventDefault();
                        video.volume = Math.max(0, video.volume - 0.1);
                        volumeSlider.value = video.volume * 100;
                        break;
                    case 'KeyF':
                        fullscreenBtn.click();
                        break;
                    case 'KeyM':
                        volumeBtn.click();
                        break;
                }
            });
        }
    };
    
    // 视频编辑器
    const VideoEditor = {
        // 创建时间轴
        createTimeline: function(containerId, clips = []) {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error('时间轴容器未找到:', containerId);
                return;
            }
            
            const timelineHTML = `
                <div class="video-timeline">
                    <div class="timeline-header">
                        <div class="timeline-controls">
                            <button class="btn-add-clip">添加片段</button>
                            <button class="btn-play-timeline">播放</button>
                            <button class="btn-export">导出</button>
                        </div>
                        <div class="timeline-info">
                            <span class="total-duration">总时长: 00:00</span>
                        </div>
                    </div>
                    <div class="timeline-tracks">
                        <div class="track video-track" data-track="video">
                            <div class="track-label">视频</div>
                            <div class="track-content"></div>
                        </div>
                        <div class="track audio-track" data-track="audio">
                            <div class="track-label">音频</div>
                            <div class="track-content"></div>
                        </div>
                    </div>
                    <div class="timeline-ruler"></div>
                </div>
            `;
            
            container.innerHTML = timelineHTML;
            
            // 添加片段
            clips.forEach(clip => this.addClip(container, clip));
            
            // 绑定事件
            this.bindTimelineEvents(container);
        },
        
        // 添加片段
        addClip: function(container, clip) {
            const trackContent = container.querySelector(`[data-track="${clip.type}"] .track-content`);
            if (!trackContent) return;
            
            const clipElement = document.createElement('div');
            clipElement.className = 'timeline-clip';
            clipElement.dataset.clipId = clip.id;
            clipElement.style.width = (clip.duration * 100) + 'px'; // 假设1秒=100px
            clipElement.innerHTML = `
                <div class="clip-content">
                    <span class="clip-name">${clip.name}</span>
                    <span class="clip-duration">${AutoMovie.formatDuration(clip.duration)}</span>
                </div>
                <div class="clip-handles">
                    <div class="handle handle-left"></div>
                    <div class="handle handle-right"></div>
                </div>
            `;
            
            trackContent.appendChild(clipElement);
            
            // 绑定片段事件
            this.bindClipEvents(clipElement);
        },
        
        // 绑定时间轴事件
        bindTimelineEvents: function(container) {
            const addClipBtn = container.querySelector('.btn-add-clip');
            const playBtn = container.querySelector('.btn-play-timeline');
            const exportBtn = container.querySelector('.btn-export');
            
            addClipBtn.addEventListener('click', () => {
                // 打开文件选择对话框或显示素材库
                this.showMediaLibrary();
            });
            
            playBtn.addEventListener('click', () => {
                // 播放时间轴
                this.playTimeline(container);
            });
            
            exportBtn.addEventListener('click', () => {
                // 导出视频
                this.exportVideo(container);
            });
        },
        
        // 绑定片段事件
        bindClipEvents: function(clipElement) {
            let isDragging = false;
            let isResizing = false;
            let startX = 0;
            let startWidth = 0;
            
            // 拖拽移动
            clipElement.addEventListener('mousedown', (e) => {
                if (e.target.classList.contains('handle')) return;
                
                isDragging = true;
                startX = e.clientX - clipElement.offsetLeft;
                clipElement.classList.add('dragging');
            });
            
            // 调整大小
            const handles = clipElement.querySelectorAll('.handle');
            handles.forEach(handle => {
                handle.addEventListener('mousedown', (e) => {
                    e.stopPropagation();
                    isResizing = true;
                    startX = e.clientX;
                    startWidth = clipElement.offsetWidth;
                    clipElement.classList.add('resizing');
                });
            });
            
            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    const newLeft = e.clientX - startX;
                    clipElement.style.left = Math.max(0, newLeft) + 'px';
                } else if (isResizing) {
                    const deltaX = e.clientX - startX;
                    const newWidth = Math.max(50, startWidth + deltaX);
                    clipElement.style.width = newWidth + 'px';
                }
            });
            
            document.addEventListener('mouseup', () => {
                if (isDragging || isResizing) {
                    clipElement.classList.remove('dragging', 'resizing');
                    isDragging = false;
                    isResizing = false;
                }
            });
        },
        
        // 显示素材库
        showMediaLibrary: function() {
            // 这里可以实现素材库的显示逻辑
            console.log('显示素材库');
        },
        
        // 播放时间轴
        playTimeline: function(container) {
            // 这里可以实现时间轴播放逻辑
            console.log('播放时间轴');
        },
        
        // 导出视频
        exportVideo: function(container) {
            // 收集时间轴数据并发送到后端进行视频合成
            const clips = this.getTimelineData(container);
            
            AutoMovie.showStatus('开始导出视频...', 'info');
            
            VideoGenerator.generate({
                clips: clips,
                resolution: '1920x1080',
                fps: 30
            })
            .then(response => {
                if (response.success) {
                    AutoMovie.showStatus('视频导出成功！', 'success');
                    // 可以提供下载链接
                } else {
                    AutoMovie.showStatus('视频导出失败: ' + response.error, 'error');
                }
            })
            .catch(error => {
                AutoMovie.showStatus('视频导出失败: ' + error.message, 'error');
            });
        },
        
        // 获取时间轴数据
        getTimelineData: function(container) {
            const clips = [];
            const clipElements = container.querySelectorAll('.timeline-clip');
            
            clipElements.forEach(clipElement => {
                clips.push({
                    id: clipElement.dataset.clipId,
                    startTime: parseFloat(clipElement.style.left) / 100, // 转换为秒
                    duration: parseFloat(clipElement.style.width) / 100, // 转换为秒
                    type: clipElement.closest('.track').dataset.track
                });
            });
            
            return clips;
        }
    };
    
    // 导出到全局
    window.AutoMovie = window.AutoMovie || {};
    window.AutoMovie.Video = {
        Generator: VideoGenerator,
        Player: VideoPlayer,
        Editor: VideoEditor
    };
    
})();