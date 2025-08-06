// 音频生成页面JavaScript
class AudioGenerator {
    constructor() {
        this.scriptData = [];
        this.projectPath = '';
        this.sentenceCount = 8; // 默认8个格子
        this.paperContent = {}; // 从parameter.ini加载的文案内容
        this.init();
    }

    async init() {
        await this.loadProjectData();
        this.renderAudioGrid();
        await this.loadExistingAudios();
        await this.loadAudioPauseSettings();
        this.bindEvents();
    }

    // 加载项目数据
    async loadProjectData() {
        try {
            // 获取当前项目路径
            const configResponse = await fetch('/get_current_project/');
            const configData = await configResponse.json();
            
            if (configData.success && configData.project) {
                this.projectPath = configData.project.project_path;
                console.log('Got project path:', this.projectPath);
                
                // 加载parameter.ini文件获取sentence_count
                await this.loadParameterConfig();
                
                // 加载paper.json文件
                const paperResponse = await fetch(`/load_project_paper/?project_path=${encodeURIComponent(this.projectPath)}`);
                const paperData = await paperResponse.json();
                
                if (paperData.success) {
                    this.scriptData = paperData.script || [];
                } else {
                    console.log('No paper.json found, will show empty tiles');
                    this.scriptData = [];
                }
            } else {
                console.error('Failed to get project path:', configData.message);
                this.showError('无法获取项目路径');
            }
        } catch (error) {
            console.error('Error loading project data:', error);
            this.showError('加载项目数据时出错');
        }
    }

    // 加载parameter.ini配置
    async loadParameterConfig() {
        try {
            const parameterPath = this.projectPath + '/parameter.ini';
            console.log('Loading parameter config from:', this.projectPath);
            const response = await fetch(`/load_parameter_config/?project_path=${encodeURIComponent(this.projectPath)}`);
            const data = await response.json();
            console.log('API response:', data);
            
            if (data.success && data.sentence_count !== undefined) {
                this.sentenceCount = parseInt(data.sentence_count);
                console.log('Loaded sentence_count from parameter.ini:', this.sentenceCount);
                
                // 加载文案内容
                if (data.paper_content) {
                    this.paperContent = data.paper_content;
                    console.log('Loaded paper content from parameter.ini:', this.paperContent);
                } else {
                    this.paperContent = {};
                }
            } else {
                console.log('Failed to load sentence_count, using default:', this.sentenceCount);
                console.log('API response details:', data);
                this.paperContent = {};
            }
        } catch (error) {
            console.log('Error loading parameter config:', error);
            console.log('Using default count:', this.sentenceCount);
            this.paperContent = {};
        }
    }

    // 加载音频停顿设置
    async loadAudioPauseSettings() {
        try {
            const response = await fetch(`/load_audio_pause_settings/?project_path=${encodeURIComponent(this.projectPath)}`);
            const data = await response.json();
            
            if (data.success) {
                // 更新UI中的停顿设置值
                const prePauseInput = document.getElementById('pre-pause');
                const postPauseInput = document.getElementById('post-pause');
                
                if (prePauseInput && data.pre_pause !== undefined) {
                    prePauseInput.value = data.pre_pause;
                }
                
                if (postPauseInput && data.post_pause !== undefined) {
                    postPauseInput.value = data.post_pause;
                }
                
                console.log(`已加载音频停顿设置: 前停顿=${data.pre_pause}秒, 后停顿=${data.post_pause}秒`);
            } else {
                console.log('Failed to load audio pause settings, using default values');
            }
        } catch (error) {
            console.log('Error loading audio pause settings:', error);
        }
    }

    // 渲染音频网格
    renderAudioGrid() {
        const gridContainer = document.getElementById('audio-grid');
        if (!gridContainer) return;

        gridContainer.innerHTML = '';

        // 根据sentenceCount显示对应数量的格子
        for (let i = 1; i <= this.sentenceCount; i++) {
            // 优先从paperContent获取文案，其次从scriptData，最后使用默认文案
            let text = '暂无文案内容';
            const lineKey = `line_${i}`;
            
            if (this.paperContent && this.paperContent[lineKey]) {
                text = this.paperContent[lineKey];
            } else {
                const scriptItem = this.scriptData.find(s => s.id === i);
                if (scriptItem && scriptItem.text) {
                    text = scriptItem.text;
                }
            }
            
            const script = {
                id: i,
                text: text
            };
            
            const cardElement = this.createAudioCard(script);
            gridContainer.appendChild(cardElement);
            
            // 检查是否已有生成的音频
            this.checkExistingAudio(i);
        }
        
        console.log(`渲染了 ${this.sentenceCount} 个音频卡片`);
    }

    // 加载项目中所有现有的音频文件
    async loadExistingAudios() {
        try {
            const response = await fetch(`/list_project_audios/?project_path=${encodeURIComponent(this.projectPath)}`);
            const data = await response.json();
            
            if (data.success && data.audios && data.audios.length > 0) {
                console.log('Found existing audios:', data.audios);
                
                // 为每个现有音频文件创建试听卡片（如果还没有对应的脚本卡片）
                const gridContainer = document.getElementById('audio-grid');
                if (!gridContainer) return;
                
                data.audios.forEach(audioFile => {
                    // 尝试从文件名中提取脚本ID
                    const scriptIdMatch = audioFile.filename.match(/(?:script_|audio_)?(\d+)\./i);
                    let scriptId = null;
                    
                    if (scriptIdMatch) {
                        scriptId = parseInt(scriptIdMatch[1]);
                        // 如果已经有对应的脚本卡片，跳过
                        if (scriptId <= this.sentenceCount) {
                            return;
                        }
                    }
                    
                    // 创建额外的音频试听卡片
                    const audioCard = this.createAudioPreviewCard(audioFile);
                    gridContainer.appendChild(audioCard);
                });
            }
        } catch (error) {
            console.log('Error loading existing audios:', error);
        }
    }
    
    // 创建音频预览卡片（用于现有音频文件）
    createAudioPreviewCard(audioFile) {
        const card = document.createElement('div');
        card.className = 'audio-card preview-card';
        card.dataset.filename = audioFile.filename;
        
        const projectName = this.projectPath.split(/[\/]/).pop();
        const audioUrl = `/media/${projectName}/audios/${audioFile.filename}`;
        
        card.innerHTML = `
            <div class="audio-player">
                <div class="audio-controls show">
                    <audio controls preload="none">
                        您的浏览器不支持音频播放。
                    </audio>
                    <div class="audio-info">
                        <span>文件: ${audioFile.filename}</span>
                        <span>大小: ${this.formatFileSize(audioFile.size)}</span>
                    </div>
                </div>
                <div class="status-indicator completed"></div>
            </div>
            <div class="script-info">
                <div class="script-id">现有音频</div>
                <p class="script-text">${audioFile.filename}</p>
            </div>
            <div class="card-actions">
                <button class="action-btn delete-btn" data-action="delete" data-filename="${audioFile.filename}">
                    🗑️ 删除
                </button>
                <button class="action-btn download-btn" data-action="download" data-filename="${audioFile.filename}">
                    💾 下载
                </button>
            </div>
        `;
        
        // 设置音频源
        const audioElement = card.querySelector('audio');
        if (audioElement) {
            audioElement.src = audioUrl;
        }
        
        // 绑定删除和下载事件
        const deleteBtn = card.querySelector('.delete-btn');
        const downloadBtn = card.querySelector('.download-btn');
        
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => this.deleteAudioFile(audioFile.filename));
        }
        
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadAudioFile(audioFile.filename));
        }
        
        return card;
    }
    
    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 删除音频文件
    async deleteAudioFile(filename) {
        if (!confirm(`确定要删除音频文件 "${filename}" 吗？此操作不可撤销。`)) {
            return;
        }
        
        try {
            const response = await fetch('/delete_audio_file/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    project_path: this.projectPath,
                    filename: filename
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 移除卡片
                const card = document.querySelector(`[data-filename="${filename}"]`);
                if (card) {
                    card.remove();
                }
                console.log(`音频文件 ${filename} 已删除`);
            } else {
                console.error('Delete audio failed:', result.message);
                alert(`删除失败: ${result.message}`);
            }
        } catch (error) {
            console.error('Error deleting audio:', error);
            alert(`删除失败: ${error.message}`);
        }
    }
    
    // 下载音频文件
    downloadAudioFile(filename) {
        const projectName = this.projectPath.split(/[\/]/).pop();
        const audioUrl = `/media/${projectName}/audios/${filename}`;
        
        const link = document.createElement('a');
        link.href = audioUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // 检查已存在的音频
    async checkExistingAudio(scriptId) {
        try {
            // 使用API获取项目中的所有音频文件
            const response = await fetch(`/list_project_audios/?project_path=${encodeURIComponent(this.projectPath)}`);
            const data = await response.json();
            
            if (data.success && data.audios && data.audios.length > 0) {
                // 构建媒体文件URL路径
                const projectName = this.projectPath.split(/[\/]/).pop(); // 获取项目名称
                const timestamp = new Date().getTime(); // 添加时间戳防止缓存
                
                // 尝试多种可能的音频文件名格式
                const possibleFilenames = [
                    `script_${scriptId}.wav`,
                    `audio_${scriptId}.wav`,
                    `${scriptId}.wav`,
                    `script_${scriptId}.mp3`,
                    `audio_${scriptId}.mp3`,
                    `${scriptId}.mp3`
                ];
                
                // 同时检查带有额外数字后缀的文件名（如script_1_1.wav）
                const audioFilesForScript = data.audios.filter(audio => {
                    const filename = audio.filename;
                    // 匹配 script_X_Y.ext 或 audio_X_Y.ext 或 X_Y.ext 格式
                    const patterns = [
                        new RegExp(`^script_${scriptId}_\\d+\\.(wav|mp3|m4a|aac|ogg|flac)$`, 'i'),
                        new RegExp(`^audio_${scriptId}_\\d+\\.(wav|mp3|m4a|aac|ogg|flac)$`, 'i'),
                        new RegExp(`^${scriptId}_\\d+\\.(wav|mp3|m4a|aac|ogg|flac)$`, 'i')
                    ];
                    return patterns.some(pattern => pattern.test(filename)) || possibleFilenames.includes(filename);
                });
                
                if (audioFilesForScript.length > 0) {
                    // 优先使用最新的文件（按修改时间排序）
                    const latestAudio = audioFilesForScript.sort((a, b) => b.modified_time - a.modified_time)[0];
                    const audioUrl = `/media/${projectName}/audios/${latestAudio.filename}?t=${timestamp}`;
                    const card = document.querySelector(`[data-script-id="${scriptId}"]`);
                    if (card) {
                        this.displayAudio(card, audioUrl);
                        const statusIndicator = card.querySelector('.status-indicator');
                        if (statusIndicator) {
                            statusIndicator.className = 'status-indicator completed';
                        }
                    }
                    console.log(`Found existing audio: ${latestAudio.filename} for script ${scriptId}`);
                    return; // 找到音频文件后退出
                }
                

            }
            
            console.log(`No existing audio found for script ${scriptId}`);
        } catch (error) {
            console.log(`Error checking existing audio for script ${scriptId}:`, error);
        }
    }

    // 创建单个音频卡片
    createAudioCard(script) {
        const card = document.createElement('div');
        card.className = 'audio-card';
        card.dataset.scriptId = script.id;

        card.innerHTML = `
            <div class="audio-player">
                <div class="audio-placeholder">
                    <span class="icon">🎵</span>
                    <span class="text">等待生成</span>
                </div>
                <div class="audio-controls">
                    <audio controls preload="none">
                        您的浏览器不支持音频播放。
                    </audio>
                    <div class="audio-info">
                        <span>格式: WAV</span>
                        <span>质量: 高</span>
                    </div>
                </div>
                <div class="status-indicator pending"></div>
            </div>
            <div class="script-info">
                <div class="script-id">第${script.id}段</div>
                <p class="script-text">${script.text}</p>
            </div>
            <div class="card-actions">
                <button class="action-btn generate-btn" data-action="generate" data-script-id="${script.id}">
                    🎤 生成
                </button>
                <button class="action-btn regenerate-btn" data-action="regenerate" data-script-id="${script.id}">
                    🔄 重生成
                </button>
                <button class="action-btn upload-btn" data-action="upload" data-script-id="${script.id}">
                    📁 上传
                </button>
            </div>
        `;

        // 绑定事件监听器
        const generateBtn = card.querySelector('.generate-btn');
        const regenerateBtn = card.querySelector('.regenerate-btn');
        const uploadBtn = card.querySelector('.upload-btn');

        // 移除可能存在的旧事件监听器
        generateBtn.replaceWith(generateBtn.cloneNode(true));
        regenerateBtn.replaceWith(regenerateBtn.cloneNode(true));
        uploadBtn.replaceWith(uploadBtn.cloneNode(true));
        
        // 重新获取元素引用
        const newGenerateBtn = card.querySelector('.generate-btn');
        const newRegenerateBtn = card.querySelector('.regenerate-btn');
        const newUploadBtn = card.querySelector('.upload-btn');

        newGenerateBtn.addEventListener('click', () => this.generateAudio(script.id));
        newRegenerateBtn.addEventListener('click', () => this.regenerateAudio(script.id));
        newUploadBtn.addEventListener('click', () => this.uploadAudio(script.id));

        return card;
    }

    // 绑定事件
    bindEvents() {
        // 批量生成按钮
        const batchBtn = document.getElementById('batch-generate-btn');
        if (batchBtn) {
            batchBtn.addEventListener('click', () => this.batchGenerateAudios());
        }
        
        // 清除所有音频按钮
        const clearBtn = document.getElementById('clear-all-audios-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAllAudios());
        }
        
        // 保存音频停顿设置按钮
        const savePauseBtn = document.getElementById('save-pause-settings-btn');
        if (savePauseBtn) {
            savePauseBtn.addEventListener('click', () => this.saveAudioPauseSettings());
        }
    }

    // 批量生成所有音频
    async batchGenerateAudios() {
        // 确认批量生成
        if (!confirm(`确定要批量生成 ${this.sentenceCount} 个音频吗？这可能需要较长时间。`)) {
            return;
        }

        const batchBtn = document.getElementById('batch-generate-btn');
        if (batchBtn) {
            batchBtn.disabled = true;
            batchBtn.textContent = '🔄 生成中...';
        }

        let successCount = 0;
        let failCount = 0;

        try {
            // 根据sentenceCount生成所有音频
            for (let i = 1; i <= this.sentenceCount; i++) {
                try {
                    console.log(`开始生成第${i}段音频`);
                    await this.generateAudio(i);
                    successCount++;
                    console.log(`音频 ${i} 生成成功`);
                } catch (error) {
                    failCount++;
                    console.error(`音频 ${i} 生成失败:`, error);
                }
                
                // 添加延迟避免请求过快
                if (i < this.sentenceCount) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
            
            // 显示批量生成结果
            console.log(`批量生成完成！成功: ${successCount} 个，失败: ${failCount} 个`);
            console.log('批量生成完成');
        } catch (error) {
            console.error('Batch generation error:', error);
            this.showError('批量生成过程中出现错误: ' + error.message);
        } finally {
            if (batchBtn) {
                batchBtn.disabled = false;
                batchBtn.textContent = '🎵 批量生成所有音频';
            }
        }
    }

    // 生成单个音频
    async generateAudio(scriptId) {
        console.log(`generateAudio called with scriptId: ${scriptId}`);
        
        const card = document.querySelector(`[data-script-id="${scriptId}"]`);
        console.log(`Found card:`, card);
        
        if (!card) {
            console.warn(`Card not found for script ID: ${scriptId}`);
            return;
        }

        const statusIndicator = card.querySelector('.status-indicator');
        let placeholder = card.querySelector('.audio-placeholder');
        const audioControls = card.querySelector('.audio-controls');
        
        // 隐藏音频控制器，显示占位符
        if (audioControls) {
            audioControls.classList.remove('show');
        }
        if (placeholder) {
            placeholder.style.display = 'flex';
        }
        
        // 更新状态为生成中
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator generating';
        }
        if (placeholder) {
            placeholder.innerHTML = '<span class="icon">⏳</span><span class="text">生成中...</span>';
        }

        try {
            const response = await fetch('/generate_audio/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    script_id: scriptId,
                    project_path: this.projectPath,
                    seed: Math.floor(Math.random() * 1000000)
                })
            });

            const result = await response.json();

            if (result.success) {
                // 生成成功，显示音频（添加时间戳防止缓存）
                const timestamp = new Date().getTime();
                const audioUrlWithTimestamp = `${result.audio_url}?t=${timestamp}`;
                this.displayAudio(card, audioUrlWithTimestamp);
                if (statusIndicator) {
                    statusIndicator.className = 'status-indicator completed';
                }
                console.log('音频生成成功:', result.message);
            } else {
                // 生成失败
                if (statusIndicator) {
                    statusIndicator.className = 'status-indicator failed';
                }
                if (placeholder) {
                    placeholder.innerHTML = '<span class="icon">❌</span><span class="text">生成失败</span>';
                }
                console.error('Audio generation failed:', result.message);
                alert(`音频生成失败: ${result.error || result.message}`);
            }
        } catch (error) {
            console.error('Error generating audio:', error);
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator failed';
            }
            if (placeholder) {
                placeholder.innerHTML = '<span class="icon">❌</span><span class="text">网络错误</span>';
            }
            alert(`音频生成失败: ${error.message}`);
        }
    }

    // 重新生成音频
    async regenerateAudio(scriptId) {
        console.log(`regenerateAudio called with scriptId: ${scriptId}`);
        await this.generateAudio(scriptId);
    }

    // 上传本地音频
    uploadAudio(scriptId) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'audio/*';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleAudioUpload(scriptId, file);
            }
        };
        input.click();
    }

    // 处理音频上传
    async handleAudioUpload(scriptId, file) {
        const card = document.querySelector(`[data-script-id="${scriptId}"]`);
        if (!card) return;

        const statusIndicator = card.querySelector('.status-indicator');
        const placeholder = card.querySelector('.audio-placeholder');

        // 更新状态为上传中
        if (statusIndicator) {
            statusIndicator.className = 'status-indicator generating';
        }
        if (placeholder) {
            placeholder.innerHTML = '<span class="icon">⏳</span><span class="text">上传中...</span>';
        }

        try {
            const formData = new FormData();
            formData.append('audio_file', file);
            formData.append('script_id', scriptId);
            formData.append('project_path', this.projectPath);

            const response = await fetch('/upload_audio/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // 上传成功
                const timestamp = new Date().getTime();
                const audioUrlWithTimestamp = `${result.audio_url}?t=${timestamp}`;
                this.displayAudio(card, audioUrlWithTimestamp);
                if (statusIndicator) {
                    statusIndicator.className = 'status-indicator completed';
                }
            } else {
                // 上传失败
                if (statusIndicator) {
                    statusIndicator.className = 'status-indicator failed';
                }
                if (placeholder) {
                    placeholder.innerHTML = '<span class="icon">❌</span><span class="text">上传失败</span>';
                }
                console.error('Audio upload failed:', result.message);
            }
        } catch (error) {
            console.error('Error uploading audio:', error);
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator failed';
            }
            if (placeholder) {
                placeholder.innerHTML = '<span class="icon">❌</span><span class="text">上传错误</span>';
            }
        }
    }

    // 显示音频
    displayAudio(card, audioUrl) {
        const placeholder = card.querySelector('.audio-placeholder');
        const audioControls = card.querySelector('.audio-controls');
        const audioElement = card.querySelector('audio');

        if (placeholder) {
            placeholder.style.display = 'none';
        }
        
        if (audioControls && audioElement) {
            audioElement.src = audioUrl;
            audioControls.classList.add('show');
        }
    }

    // 清除所有音频
    async clearAllAudios() {
        if (!confirm('确定要清除所有音频吗？此操作不可撤销。')) {
            return;
        }

        const clearBtn = document.getElementById('clear-all-audios-btn');
        if (clearBtn) {
            clearBtn.disabled = true;
            clearBtn.textContent = '清除中...';
        }

        try {
            const response = await fetch('/clear_all_audios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    project_path: this.projectPath
                })
            });

            const result = await response.json();

            if (result.success) {
                // 重新渲染网格
                this.renderAudioGrid();
                console.log('所有音频已清除');
                alert('所有音频已清除');
            } else {
                console.error('Clear audios failed:', result.message);
                this.showError('清除音频失败: ' + result.message);
            }
        } catch (error) {
            console.error('Error clearing audios:', error);
            this.showError('清除音频时出错: ' + error.message);
        } finally {
            if (clearBtn) {
                clearBtn.disabled = false;
                clearBtn.textContent = '🗑️ 清除所有音频';
            }
        }
    }

    // 获取CSRF令牌
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    // 保存音频停顿设置
    async saveAudioPauseSettings() {
        const prePauseInput = document.getElementById('pre-pause');
        const postPauseInput = document.getElementById('post-pause');
        const saveBtn = document.getElementById('save-pause-settings-btn');
        
        if (!prePauseInput || !postPauseInput) {
            alert('无法获取停顿设置输入框');
            return;
        }
        
        const prePause = parseFloat(prePauseInput.value);
        const postPause = parseFloat(postPauseInput.value);
        
        // 验证输入值
        if (isNaN(prePause) || prePause < 0 || prePause > 5) {
            alert('前停顿时长必须在0-5秒之间');
            return;
        }
        
        if (isNaN(postPause) || postPause < 0 || postPause > 5) {
            alert('后停顿时长必须在0-5秒之间');
            return;
        }
        
        // 禁用保存按钮
        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.textContent = '💾 保存中...';
        }
        
        try {
            const response = await fetch('/save_audio_pause_settings/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    project_path: this.projectPath,
                    pre_pause: prePause,
                    post_pause: postPause
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log(`音频停顿设置已保存: 前停顿=${prePause}秒, 后停顿=${postPause}秒`);
                alert('音频停顿设置已保存');
            } else {
                console.error('Save audio pause settings failed:', result.message);
                alert(`保存失败: ${result.error || result.message}`);
            }
        } catch (error) {
            console.error('Error saving audio pause settings:', error);
            alert(`保存失败: ${error.message}`);
        } finally {
            // 恢复保存按钮
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.textContent = '💾 保存设置';
            }
        }
    }

    // 显示错误信息
    showError(message) {
        alert(message);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new AudioGenerator();
});