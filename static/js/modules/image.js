/**
 * AutoMovie 图片处理模块
 * 处理图片生成、预览、管理等功能
 */

(function() {
    'use strict';
    
    // 图片生成器
    const ImageGenerator = {
        // 生成图片
        generate: function(prompt, options = {}) {
            const formData = new FormData();
            formData.append('prompt', prompt);
            
            if (options.width) {
                formData.append('width', options.width);
            }
            
            if (options.height) {
                formData.append('height', options.height);
            }
            
            if (options.steps) {
                formData.append('steps', options.steps);
            }
            
            if (options.cfg_scale) {
                formData.append('cfg_scale', options.cfg_scale);
            }
            
            if (options.seed) {
                formData.append('seed', options.seed);
            }
            
            if (options.negative_prompt) {
                formData.append('negative_prompt', options.negative_prompt);
            }
            
            return fetch('/image_gen/', {
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
        
        // 批量生成图片
        generateBatch: function(prompts, options = {}) {
            const promises = prompts.map(prompt => 
                this.generate(prompt, options)
            );
            
            return Promise.all(promises);
        },
        
        // 获取生成进度
        getProgress: function(taskId) {
            return fetch(`/image_gen/progress/${taskId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': AutoMovie.getCookie('csrftoken')
                }
            })
            .then(response => response.json());
        }
    };
    
    // 图片预览器
    const ImagePreview = {
        // 创建预览容器
        createPreview: function(containerId, images) {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error('预览容器未找到:', containerId);
                return;
            }
            
            container.innerHTML = '';
            container.className = 'image-preview-container';
            
            images.forEach((imageSrc, index) => {
                const imageItem = this.createImageItem(imageSrc, index);
                container.appendChild(imageItem);
            });
        },
        
        // 创建单个图片项
        createImageItem: function(imageSrc, index) {
            const item = document.createElement('div');
            item.className = 'image-preview-item';
            item.innerHTML = `
                <div class="image-wrapper">
                    <img src="${imageSrc}" alt="生成的图片 ${index + 1}" loading="lazy">
                    <div class="image-overlay">
                        <button class="btn-preview" data-action="preview" data-src="${imageSrc}">预览</button>
                        <button class="btn-download" data-action="download" data-src="${imageSrc}">下载</button>
                        <button class="btn-delete" data-action="delete" data-index="${index}">删除</button>
                    </div>
                </div>
                <div class="image-info">
                    <span class="image-index">#${index + 1}</span>
                </div>
            `;
            
            // 绑定事件
            this.bindImageEvents(item);
            
            return item;
        },
        
        // 绑定图片事件
        bindImageEvents: function(item) {
            const previewBtn = item.querySelector('[data-action="preview"]');
            const downloadBtn = item.querySelector('[data-action="download"]');
            const deleteBtn = item.querySelector('[data-action="delete"]');
            
            // 预览事件
            previewBtn.addEventListener('click', (e) => {
                const src = e.target.dataset.src;
                this.showLightbox(src);
            });
            
            // 下载事件
            downloadBtn.addEventListener('click', (e) => {
                const src = e.target.dataset.src;
                this.downloadImage(src);
            });
            
            // 删除事件
            deleteBtn.addEventListener('click', (e) => {
                const index = e.target.dataset.index;
                if (confirm('确定要删除这张图片吗？')) {
                    item.remove();
                }
            });
        },
        
        // 显示灯箱预览
        showLightbox: function(imageSrc) {
            // 创建灯箱
            const lightbox = document.createElement('div');
            lightbox.className = 'image-lightbox';
            lightbox.innerHTML = `
                <div class="lightbox-overlay">
                    <div class="lightbox-content">
                        <img src="${imageSrc}" alt="预览图片">
                        <button class="lightbox-close">&times;</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(lightbox);
            
            // 绑定关闭事件
            const closeBtn = lightbox.querySelector('.lightbox-close');
            const overlay = lightbox.querySelector('.lightbox-overlay');
            
            const closeLightbox = () => {
                document.body.removeChild(lightbox);
            };
            
            closeBtn.addEventListener('click', closeLightbox);
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    closeLightbox();
                }
            });
            
            // ESC键关闭
            const handleKeydown = (e) => {
                if (e.key === 'Escape') {
                    closeLightbox();
                    document.removeEventListener('keydown', handleKeydown);
                }
            };
            document.addEventListener('keydown', handleKeydown);
        },
        
        // 下载图片
        downloadImage: function(imageSrc) {
            const link = document.createElement('a');
            link.href = imageSrc;
            link.download = `generated_image_${Date.now()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };
    
    // 图片上传器
    const ImageUploader = {
        // 创建上传区域
        createUploader: function(containerId, options = {}) {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error('上传容器未找到:', containerId);
                return;
            }
            
            const uploaderHTML = `
                <div class="image-uploader">
                    <div class="upload-area" data-action="upload">
                        <div class="upload-icon">📁</div>
                        <div class="upload-text">
                            <p>点击选择图片或拖拽图片到此处</p>
                            <p class="upload-hint">支持 JPG、PNG、GIF 格式，最大 ${options.maxSize || '10MB'}</p>
                        </div>
                        <input type="file" class="upload-input" accept="image/*" ${options.multiple ? 'multiple' : ''}>
                    </div>
                    <div class="upload-preview"></div>
                </div>
            `;
            
            container.innerHTML = uploaderHTML;
            
            // 绑定事件
            this.bindUploadEvents(container, options);
        },
        
        // 绑定上传事件
        bindUploadEvents: function(container, options) {
            const uploadArea = container.querySelector('.upload-area');
            const uploadInput = container.querySelector('.upload-input');
            const uploadPreview = container.querySelector('.upload-preview');
            
            // 点击上传
            uploadArea.addEventListener('click', () => {
                uploadInput.click();
            });
            
            // 文件选择
            uploadInput.addEventListener('change', (e) => {
                this.handleFiles(e.target.files, uploadPreview, options);
            });
            
            // 拖拽上传
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                this.handleFiles(e.dataTransfer.files, uploadPreview, options);
            });
        },
        
        // 处理文件
        handleFiles: function(files, previewContainer, options) {
            Array.from(files).forEach(file => {
                if (this.validateFile(file, options)) {
                    this.previewFile(file, previewContainer);
                    if (options.onFileSelect) {
                        options.onFileSelect(file);
                    }
                }
            });
        },
        
        // 验证文件
        validateFile: function(file, options) {
            const maxSize = options.maxSize || 10 * 1024 * 1024; // 默认10MB
            const allowedTypes = options.allowedTypes || ['image/jpeg', 'image/png', 'image/gif'];
            
            if (!allowedTypes.includes(file.type)) {
                AutoMovie.showStatus('不支持的文件格式', 'error');
                return false;
            }
            
            if (file.size > maxSize) {
                AutoMovie.showStatus('文件大小超出限制', 'error');
                return false;
            }
            
            return true;
        },
        
        // 预览文件
        previewFile: function(file, container) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const previewItem = document.createElement('div');
                previewItem.className = 'upload-preview-item';
                previewItem.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}">
                    <div class="preview-info">
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">${AutoMovie.formatFileSize(file.size)}</span>
                    </div>
                    <button class="preview-remove" data-action="remove">&times;</button>
                `;
                
                // 绑定删除事件
                const removeBtn = previewItem.querySelector('[data-action="remove"]');
                removeBtn.addEventListener('click', () => {
                    container.removeChild(previewItem);
                });
                
                container.appendChild(previewItem);
            };
            reader.readAsDataURL(file);
        }
    };
    
    // 导出到全局
    window.AutoMovie = window.AutoMovie || {};
    window.AutoMovie.Image = {
        Generator: ImageGenerator,
        Preview: ImagePreview,
        Uploader: ImageUploader
    };
    
})();