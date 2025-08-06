/**
 * AutoMovie 音频处理模块
 * 处理音频生成、播放、管理等功能
 */

(function() {
    'use strict';
    
    // 音频管理器
    const AudioManager = {
        currentAudio: null,
        audioQueue: [],
        
        // 播放音频
        play: function(audioSrc, options = {}) {
            if (this.currentAudio) {
                this.stop();
            }
            
            this.currentAudio = new Audio(audioSrc);
            
            // 设置音频属性
            if (options.volume !== undefined) {
                this.currentAudio.volume = options.volume;
            }
            
            if (options.loop) {
                this.currentAudio.loop = true;
            }
            
            // 添加事件监听器
            this.currentAudio.addEventListener('loadstart', () => {
                if (options.onLoadStart) options.onLoadStart();
            });
            
            this.currentAudio.addEventListener('canplay', () => {
                if (options.onCanPlay) options.onCanPlay();
            });
            
            this.currentAudio.addEventListener('ended', () => {
                if (options.onEnded) options.onEnded();
                this.currentAudio = null;
            });
            
            this.currentAudio.addEventListener('error', (e) => {
                if (options.onError) options.onError(e);
                console.error('音频播放错误:', e);
            });
            
            return this.currentAudio.play();
        },
        
        // 停止播放
        stop: function() {
            if (this.currentAudio) {
                this.currentAudio.pause();
                this.currentAudio.currentTime = 0;
                this.currentAudio = null;
            }
        },
        
        // 暂停播放
        pause: function() {
            if (this.currentAudio) {
                this.currentAudio.pause();
            }
        },
        
        // 恢复播放
        resume: function() {
            if (this.currentAudio) {
                return this.currentAudio.play();
            }
        },
        
        // 设置音量
        setVolume: function(volume) {
            if (this.currentAudio) {
                this.currentAudio.volume = Math.max(0, Math.min(1, volume));
            }
        },
        
        // 获取播放状态
        isPlaying: function() {
            return this.currentAudio && !this.currentAudio.paused;
        }
    };
    
    // 音频生成相关函数
    const AudioGenerator = {
        // 生成音频
        generate: function(text, options = {}) {
            const formData = new FormData();
            formData.append('text', text);
            
            if (options.voice) {
                formData.append('voice', options.voice);
            }
            
            if (options.speed) {
                formData.append('speed', options.speed);
            }
            
            if (options.pitch) {
                formData.append('pitch', options.pitch);
            }
            
            return fetch('/audio_gen/', {
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
        
        // 批量生成音频
        generateBatch: function(textList, options = {}) {
            const promises = textList.map(text => 
                this.generate(text, options)
            );
            
            return Promise.all(promises);
        }
    };
    
    // 音频播放器UI组件
    const AudioPlayer = {
        // 创建播放器HTML
        createPlayer: function(containerId, audioSrc) {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error('播放器容器未找到:', containerId);
                return;
            }
            
            const playerHTML = `
                <div class="audio-player">
                    <button class="play-btn" data-action="play">▶</button>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <span class="time-display">00:00 / 00:00</span>
                    </div>
                    <div class="volume-container">
                        <span class="volume-icon">🔊</span>
                        <input type="range" class="volume-slider" min="0" max="100" value="50">
                    </div>
                </div>
            `;
            
            container.innerHTML = playerHTML;
            
            // 绑定事件
            this.bindEvents(container, audioSrc);
        },
        
        // 绑定播放器事件
        bindEvents: function(container, audioSrc) {
            const playBtn = container.querySelector('.play-btn');
            const progressBar = container.querySelector('.progress-bar');
            const progressFill = container.querySelector('.progress-fill');
            const timeDisplay = container.querySelector('.time-display');
            const volumeSlider = container.querySelector('.volume-slider');
            
            let isPlaying = false;
            
            // 播放/暂停按钮
            playBtn.addEventListener('click', () => {
                if (!isPlaying) {
                    AudioManager.play(audioSrc, {
                        onCanPlay: () => {
                            playBtn.textContent = '⏸';
                            isPlaying = true;
                        },
                        onEnded: () => {
                            playBtn.textContent = '▶';
                            isPlaying = false;
                            progressFill.style.width = '0%';
                        },
                        onError: (e) => {
                            AutoMovie.showStatus('音频播放失败', 'error');
                            playBtn.textContent = '▶';
                            isPlaying = false;
                        }
                    });
                } else {
                    AudioManager.pause();
                    playBtn.textContent = '▶';
                    isPlaying = false;
                }
            });
            
            // 音量控制
            volumeSlider.addEventListener('input', (e) => {
                const volume = e.target.value / 100;
                AudioManager.setVolume(volume);
            });
            
            // 进度条点击跳转
            progressBar.addEventListener('click', (e) => {
                if (AudioManager.currentAudio) {
                    const rect = progressBar.getBoundingClientRect();
                    const percent = (e.clientX - rect.left) / rect.width;
                    AudioManager.currentAudio.currentTime = 
                        percent * AudioManager.currentAudio.duration;
                }
            });
            
            // 更新进度条和时间显示
            setInterval(() => {
                if (AudioManager.currentAudio && isPlaying) {
                    const current = AudioManager.currentAudio.currentTime;
                    const duration = AudioManager.currentAudio.duration;
                    
                    if (duration) {
                        const percent = (current / duration) * 100;
                        progressFill.style.width = percent + '%';
                        
                        const currentTime = AutoMovie.formatDuration(current);
                        const totalTime = AutoMovie.formatDuration(duration);
                        timeDisplay.textContent = `${currentTime} / ${totalTime}`;
                    }
                }
            }, 100);
        }
    };
    
    // 导出到全局
    window.AutoMovie = window.AutoMovie || {};
    window.AutoMovie.Audio = {
        Manager: AudioManager,
        Generator: AudioGenerator,
        Player: AudioPlayer
    };
    
})();