/**
 * AutoMovie 公共JavaScript函数库
 * 包含项目中常用的工具函数和通用功能
 */

// 获取CSRF Token的函数
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 显示状态消息的通用函数
function showStatus(message, type = 'info', duration = 3000) {
    const statusElement = document.getElementById('status-message');
    if (!statusElement) {
        console.warn('状态消息元素未找到');
        return;
    }
    
    // 清除之前的样式
    statusElement.className = '';
    
    // 根据类型设置样式
    let bgColor, textColor, borderColor;
    switch (type) {
        case 'success':
            bgColor = '#d4edda';
            textColor = '#155724';
            borderColor = '#c3e6cb';
            break;
        case 'error':
            bgColor = '#f8d7da';
            textColor = '#721c24';
            borderColor = '#f5c6cb';
            break;
        case 'warning':
            bgColor = '#fff3cd';
            textColor = '#856404';
            borderColor = '#ffeaa7';
            break;
        default: // info
            bgColor = '#d1ecf1';
            textColor = '#0c5460';
            borderColor = '#bee5eb';
    }
    
    statusElement.style.backgroundColor = bgColor;
    statusElement.style.color = textColor;
    statusElement.style.border = `1px solid ${borderColor}`;
    statusElement.textContent = message;
    statusElement.style.display = 'block';
    
    // 自动隐藏
    if (duration > 0) {
        setTimeout(() => {
            statusElement.style.display = 'none';
        }, duration);
    }
}

// 格式化文件大小的函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化时间的函数
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

// 防抖函数
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 验证表单字段的函数
function validateField(field, rules) {
    const value = field.value.trim();
    const errors = [];
    
    if (rules.required && !value) {
        errors.push('此字段为必填项');
    }
    
    if (rules.minLength && value.length < rules.minLength) {
        errors.push(`最少需要${rules.minLength}个字符`);
    }
    
    if (rules.maxLength && value.length > rules.maxLength) {
        errors.push(`最多允许${rules.maxLength}个字符`);
    }
    
    if (rules.pattern && !rules.pattern.test(value)) {
        errors.push(rules.patternMessage || '格式不正确');
    }
    
    return errors;
}

// 显示加载状态的函数
function showLoading(element, text = '加载中...') {
    if (element) {
        element.disabled = true;
        element.dataset.originalText = element.textContent;
        element.textContent = text;
    }
}

// 隐藏加载状态的函数
function hideLoading(element) {
    if (element && element.dataset.originalText) {
        element.disabled = false;
        element.textContent = element.dataset.originalText;
        delete element.dataset.originalText;
    }
}

// 通用的AJAX请求函数
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    // 如果是POST请求，自动添加CSRF token
    if (options.method === 'POST' || options.method === 'PUT' || options.method === 'DELETE') {
        defaultOptions.headers['X-CSRFToken'] = getCookie('csrftoken');
    }
    
    const finalOptions = { ...defaultOptions, ...options };
    
    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('请求失败:', error);
            throw error;
        });
}

function getCurrentProjectPath() {
    // 这个函数需要根据你的应用逻辑来实现，例如从URL、localStorage或全局变量中获取
    // 这里我们先用一个假数据
    const projectData = JSON.parse(localStorage.getItem('currentProject'));
    return projectData ? projectData.path : null;
}

function saveThemeToConfig(projectPath, theme) {
    fetch('/api/save_theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 
            project_path: projectPath,
            theme: theme
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('主题已成功锁定！', 'success');
        } else {
            showStatus('锁定主题失败: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error saving theme:', error);
        showStatus('锁定主题时发生错误。', 'error');
    });
}

// 页面加载完成后的初始化函数
document.addEventListener('DOMContentLoaded', function() {
    // 为所有带有data-confirm属性的元素添加确认对话框
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.dataset.confirm;
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // 为所有表单添加基础验证
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                } else {
                    field.style.borderColor = '#ddd';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showStatus('请填写所有必填字段', 'error');
            }
        });
    });

    // 锁定主题按钮事件
    const lockThemeBtn = document.getElementById('lock-theme-btn');
    if (lockThemeBtn) {
        lockThemeBtn.addEventListener('click', function() {
            const themeInput = document.getElementById('theme-input');
            const theme = themeInput.value.trim();
            if (theme) {
                const projectPath = getCurrentProjectPath(); 
                if (projectPath) {
                    saveThemeToConfig(projectPath, theme);
                } else {
                    showStatus('无法获取当前项目路径，无法锁定主题。', 'error');
                }
            } else {
                showStatus('请输入主题名称。', 'warning');
            }
        });
    }
});

// 导出函数供其他模块使用
window.AutoMovie = {
    getCookie,
    showStatus,
    formatFileSize,
    formatDuration,
    debounce,
    throttle,
    validateField,
    showLoading,
    hideLoading,
    makeRequest
};