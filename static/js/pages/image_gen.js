// 图像生成页面JavaScript
class ImageGenerator {
    constructor() {
        this.scriptData = [];
        this.projectPath = '';
        this.sentenceCount = 8; // 默认8个格子
        this.paperContent = {}; // 从parameter.ini加载的文案内容
        this.currentModalIndex = 0; // 当前预览的图片索引
        this.availableImages = []; // 可用的图片列表
        this.init();
    }

    async init() {
        await this.loadProjectData();
        this.renderImageGrid();
        this.bindEvents();
        this.initImageModal();
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

    // 渲染图像网格
    renderImageGrid() {
        const gridContainer = document.getElementById('image-grid');
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
            
            const cardElement = this.createImageCard(script);
            gridContainer.appendChild(cardElement);
            
            // 检查是否已有生成的图像
            this.checkExistingImage(i);
        }
        
        console.log(`渲染了 ${this.sentenceCount} 个图像卡片`);
    }

    // 检查已存在的图像
    async checkExistingImage(scriptId) {
        try {
            // 构建媒体文件URL路径
            const projectName = this.projectPath.split(/[\/]/).pop(); // 获取项目名称
            const timestamp = new Date().getTime(); // 添加时间戳防止缓存
            const imageUrl = `/media/${projectName}/images/script_${scriptId}.png?t=${timestamp}`;
            
            // 尝试加载图像
            const img = new Image();
            img.onload = () => {
                const card = document.querySelector(`[data-script-id="${scriptId}"]`);
                if (card) {
                    this.displayImage(card, imageUrl);
                    const statusIndicator = card.querySelector('.status-indicator');
                    if (statusIndicator) {
                        statusIndicator.className = 'status-indicator completed';
                    }
                }
            };
            img.onerror = () => {
                // 图像不存在，保持默认状态
            };
            img.src = imageUrl;
        } catch (error) {
            console.log(`No existing image for script ${scriptId}`);
        }
    }

    // 创建单个图像卡片
    createImageCard(script) {
        const card = document.createElement('div');
        card.className = 'image-card';
        card.dataset.scriptId = script.id;

        card.innerHTML = `
            <div class="image-preview">
                <div class="image-placeholder">
                    <span class="icon">🖼️</span>
                    <span class="text">等待生成</span>
                </div>
                <div class="status-indicator pending"></div>
            </div>
            <div class="script-info">
                <div class="script-id">第${script.id}段</div>
                <p class="script-text">${script.text}</p>
            </div>
            <div class="card-actions">
                <button class="action-btn generate-btn" data-action="generate" data-script-id="${script.id}">
                    🎨 生成
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

        newGenerateBtn.addEventListener('click', () => this.generateImage(script.id));
        newRegenerateBtn.addEventListener('click', () => this.regenerateImage(script.id));
        newUploadBtn.addEventListener('click', () => this.uploadImage(script.id));

        return card;
    }

    // 绑定事件
    bindEvents() {
        // 批量生成按钮
        const batchBtn = document.getElementById('batch-generate-btn');
        if (batchBtn) {
            batchBtn.addEventListener('click', () => this.batchGenerateImages());
        }
        
        // 清除所有图片按钮
        const clearBtn = document.getElementById('clear-all-images-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAllImages());
        }
    }

    // 初始化图片预览模态框
    initImageModal() {
        const modal = document.getElementById('image-modal');
        const modalClose = document.getElementById('modal-close');
        const modalPrev = document.getElementById('modal-prev');
        const modalNext = document.getElementById('modal-next');
        
        // 关闭模态框
        modalClose.addEventListener('click', () => {
            this.closeImageModal();
        });
        
        // 点击背景关闭模态框
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeImageModal();
            }
        });
        
        // 上一张图片
        modalPrev.addEventListener('click', () => {
            this.showPrevImage();
        });
        
        // 下一张图片
        modalNext.addEventListener('click', () => {
            this.showNextImage();
        });
        
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (modal.classList.contains('show')) {
                switch(e.key) {
                    case 'Escape':
                        this.closeImageModal();
                        break;
                    case 'ArrowLeft':
                        this.showPrevImage();
                        break;
                    case 'ArrowRight':
                        this.showNextImage();
                        break;
                }
            }
        });
    }

    // 批量生成所有图像
    async batchGenerateImages() {
        const batchBtn = document.getElementById('batch-generate-btn');
        if (batchBtn) {
            batchBtn.disabled = true;
            batchBtn.textContent = '🔄 生成中...';
        }

        try {
            // 根据sentenceCount生成所有图像，而不是依赖scriptData
            for (let i = 1; i <= this.sentenceCount; i++) {
                console.log(`开始生成第${i}段图像`);
                
                try {
                    await this.generateImage(i);
                } catch (error) {
                    // 如果是第一个图片生成失败，检查是否是paper.json相关错误
                    if (i === 1) {
                        const errorMessage = error.message || '';
                        if (errorMessage.includes('paper.json') || 
                            errorMessage.includes('无法加载paper.json数据') ||
                            errorMessage.includes('项目文案未格式化')) {
                            
                            // 弹窗提示用户项目文案未格式化
                            const userConfirm = confirm(
                                '⚠️ 项目文案未格式化\n\n' +
                                '检测到当前项目的文案还没有进行格式化处理，无法生成图像。\n\n' +
                                '请先到"文案生成"页面完成以下步骤：\n' +
                                '1. 生成或输入项目文案\n' +
                                '2. 点击"格式化文案"按钮\n' +
                                '3. 确保生成了paper.json文件\n\n' +
                                '是否现在跳转到文案生成页面？'
                            );
                            
                            if (userConfirm) {
                                // 跳转到文案生成页面
                                window.location.href = '/text_generation/';
                            }
                            
                            // 停止批量生成
                            console.log('由于文案未格式化，停止批量生成');
                            return;
                        }
                    }
                    
                    // 其他错误继续处理但不中断批量生成
                    console.error(`第${i}段图像生成失败:`, error);
                }
                
                // 添加延迟避免请求过快
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            console.log('批量生成完成');
        } catch (error) {
            console.error('Batch generation error:', error);
            this.showError('批量生成过程中出现错误: ' + error.message);
        } finally {
            if (batchBtn) {
                batchBtn.disabled = false;
                batchBtn.textContent = '🎨 批量生成所有图像';
            }
        }
    }

    // 生成单个图像
    async generateImage(scriptId) {
        console.log(`generateImage called with scriptId: ${scriptId}`);
        
        const card = document.querySelector(`[data-script-id="${scriptId}"]`);
        console.log(`Found card:`, card);
        
        if (!card) {
            console.warn(`Card not found for script ID: ${scriptId}`);
            return;
        }

        const statusIndicator = card.querySelector('.status-indicator');
        let placeholder = card.querySelector('.image-placeholder');
        
        // 如果没有找到placeholder，说明图像已存在，需要重新创建placeholder
        if (!placeholder) {
            const imagePreview = card.querySelector('.image-preview');
            if (imagePreview) {
                imagePreview.innerHTML = `
                    <div class="image-placeholder">
                        <span class="icon">🖼️</span>
                        <span class="text">等待生成</span>
                    </div>
                    <div class="status-indicator pending"></div>
                `;
                placeholder = card.querySelector('.image-placeholder');
            }
        }
        
        if (!statusIndicator && !placeholder) {
            console.error(`Required elements not found in card for script ID: ${scriptId}`);
            return;
        }
        
        // 获取当前的状态指示器（可能是新创建的）
        const currentStatusIndicator = card.querySelector('.status-indicator');
        
        // 更新状态为生成中
        currentStatusIndicator.className = 'status-indicator generating';
        placeholder.innerHTML = '<span class="icon">⏳</span><span class="text">生成中...</span>';

        try {
            const response = await fetch('/generate_image/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    script_id: scriptId,
                    project_path: this.projectPath
                })
            });

            const result = await response.json();

            if (result.success) {
                // 生成成功，显示图像（添加时间戳防止缓存）
                const timestamp = new Date().getTime();
                const imageUrlWithTimestamp = `${result.image_url}?t=${timestamp}`;
                this.displayImage(card, imageUrlWithTimestamp);
                const finalStatusIndicator = card.querySelector('.status-indicator');
                if (finalStatusIndicator) {
                    finalStatusIndicator.className = 'status-indicator completed';
                }
            } else {
                // 生成失败
                currentStatusIndicator.className = 'status-indicator failed';
                placeholder.innerHTML = '<span class="icon">❌</span><span class="text">生成失败</span>';
                console.error('Image generation failed:', result.message);
                
                // 检查是否是paper.json相关错误，如果是则抛出异常
                const errorMessage = result.error || result.message || '';
                if (errorMessage.includes('paper.json') || 
                    errorMessage.includes('无法加载paper.json数据') ||
                    errorMessage.includes('项目文案未格式化')) {
                    throw new Error(errorMessage);
                }
            }
        } catch (error) {
            console.error('Error generating image:', error);
            currentStatusIndicator.className = 'status-indicator failed';
            placeholder.innerHTML = '<span class="icon">❌</span><span class="text">网络错误</span>';
            
            // 如果是paper.json相关错误，重新抛出异常
            const errorMessage = error.message || '';
            if (errorMessage.includes('paper.json') || 
                errorMessage.includes('无法加载paper.json数据') ||
                errorMessage.includes('项目文案未格式化')) {
                throw error;
            }
        }
    }

    // 重新生成图像
    async regenerateImage(scriptId) {
        console.log(`regenerateImage called with scriptId: ${scriptId}`);
        await this.generateImage(scriptId);
    }

    // 上传本地图像
    uploadImage(scriptId) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleImageUpload(scriptId, file);
            }
        };
        input.click();
    }

    // 处理图像上传
    async handleImageUpload(scriptId, file) {
        const card = document.querySelector(`[data-script-id="${scriptId}"]`);
        if (!card) return;

        const statusIndicator = card.querySelector('.status-indicator');
        const placeholder = card.querySelector('.image-placeholder');
        
        statusIndicator.className = 'status-indicator generating';
        placeholder.innerHTML = '<span class="icon">📤</span><span class="text">上传中...</span>';

        try {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('script_id', scriptId);
            formData.append('project_path', this.projectPath);

            const response = await fetch('/upload_image/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // 上传成功，显示图像（添加时间戳防止缓存）
                const timestamp = new Date().getTime();
                const imageUrlWithTimestamp = `${result.image_url}?t=${timestamp}`;
                this.displayImage(card, imageUrlWithTimestamp);
                statusIndicator.className = 'status-indicator completed';
            } else {
                statusIndicator.className = 'status-indicator failed';
                placeholder.innerHTML = '<span class="icon">❌</span><span class="text">上传失败</span>';
                console.error('Image upload failed:', result.message);
            }
        } catch (error) {
            console.error('Error uploading image:', error);
            statusIndicator.className = 'status-indicator failed';
            placeholder.innerHTML = '<span class="icon">❌</span><span class="text">上传错误</span>';
        }
    }

    // 清除所有图片
    async clearAllImages() {
        const clearBtn = document.getElementById('clear-all-images-btn');
        
        // 显示确认对话框
        if (!confirm('确定要删除当前项目下所有图片吗？此操作不可撤销！')) {
            return;
        }
        
        if (clearBtn) {
            clearBtn.disabled = true;
            clearBtn.textContent = '🗑️ 删除中...';
        }

        try {
            const response = await fetch('/clear_all_images/', {
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
                // 清除成功，重置所有卡片状态并强制刷新
                this.resetAllCards();
                // 强制刷新页面缓存
                setTimeout(() => {
                    window.location.reload(true);
                }, 500);
                console.log('所有图片已清除');
            } else {
                console.error('清除图片失败:', result.message);
                alert('清除图片失败: ' + result.message);
            }
        } catch (error) {
            console.error('Error clearing images:', error);
            alert('清除图片时出现网络错误');
        } finally {
            if (clearBtn) {
                clearBtn.disabled = false;
                clearBtn.textContent = '🗑️ 清除所有图片';
            }
        }
    }

    // 重置所有卡片状态
    resetAllCards() {
        const cards = document.querySelectorAll('.image-card');
        cards.forEach(card => {
            const preview = card.querySelector('.image-preview');
            if (preview) {
                preview.innerHTML = `
                    <div class="image-placeholder">
                        <span class="icon">🖼️</span>
                        <span class="text">等待生成</span>
                    </div>
                    <div class="status-indicator pending"></div>
                `;
            }
        });
    }

    // 显示图像
    displayImage(card, imageUrl) {
        const preview = card.querySelector('.image-preview');
        // 如果URL中没有时间戳，添加时间戳防止缓存
        const finalImageUrl = imageUrl.includes('?t=') ? imageUrl : `${imageUrl}?t=${new Date().getTime()}`;
        preview.innerHTML = `
            <img src="${finalImageUrl}" alt="Generated Image" />
            <div class="status-indicator completed"></div>
        `;
        
        // 添加点击事件打开预览
        const imgElement = preview.querySelector('img');
        if (imgElement) {
            imgElement.addEventListener('click', () => {
                const scriptId = card.dataset.scriptId;
                this.openImageModal(parseInt(scriptId));
            });
        }
    }

    // 显示错误信息
    showError(message) {
        const gridContainer = document.getElementById('image-grid');
        if (gridContainer) {
            gridContainer.innerHTML = `<div class="loading">❌ ${message}</div>`;
        }
    }

    // 获取CSRF Token
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

    // 打开图片预览模态框
    openImageModal(scriptId) {
        this.updateAvailableImages();
        const imageIndex = this.availableImages.findIndex(img => img.scriptId === scriptId);
        if (imageIndex !== -1) {
            this.currentModalIndex = imageIndex;
            this.showImageInModal();
            const modal = document.getElementById('image-modal');
            modal.classList.add('show');
        }
    }

    // 关闭图片预览模态框
    closeImageModal() {
        const modal = document.getElementById('image-modal');
        modal.classList.remove('show');
    }

    // 显示上一张图片
    showPrevImage() {
        if (this.availableImages.length === 0) return;
        this.currentModalIndex = (this.currentModalIndex - 1 + this.availableImages.length) % this.availableImages.length;
        this.showImageInModal();
    }

    // 显示下一张图片
    showNextImage() {
        if (this.availableImages.length === 0) return;
        this.currentModalIndex = (this.currentModalIndex + 1) % this.availableImages.length;
        this.showImageInModal();
    }

    // 在模态框中显示图片
    showImageInModal() {
        if (this.availableImages.length === 0) return;
        
        const currentImage = this.availableImages[this.currentModalIndex];
        const modalImage = document.getElementById('modal-image');
        const modalInfo = document.getElementById('modal-info');
        
        if (modalImage) {
            modalImage.src = currentImage.imageUrl;
        }
        
        if (modalInfo) {
            modalInfo.innerHTML = `
                <div>第${currentImage.scriptId}段 (${this.currentModalIndex + 1} / ${this.availableImages.length})</div>
                <div style="margin-top: 4px; font-size: 12px; opacity: 0.8;">${currentImage.text}</div>
            `;
        }
        
        // 更新导航按钮状态
        const prevBtn = document.getElementById('modal-prev');
        const nextBtn = document.getElementById('modal-next');
        if (prevBtn && nextBtn) {
            prevBtn.style.display = this.availableImages.length > 1 ? 'block' : 'none';
            nextBtn.style.display = this.availableImages.length > 1 ? 'block' : 'none';
        }
    }

    // 更新可用图片列表
    updateAvailableImages() {
        this.availableImages = [];
        
        for (let i = 1; i <= this.sentenceCount; i++) {
            const card = document.querySelector(`[data-script-id="${i}"]`);
            if (card) {
                const img = card.querySelector('.image-preview img');
                if (img && img.src) {
                    // 获取文案内容
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
                    
                    this.availableImages.push({
                        scriptId: i,
                        imageUrl: img.src,
                        text: text
                    });
                }
            }
        }
    }
}

// 全局实例
let imageGen;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    imageGen = new ImageGenerator();
});