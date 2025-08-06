// 文案生成页面的JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    initTextGeneration();
});

function initTextGeneration() {
    // 加载PROMPT列表
    loadPromptList();
    
    // 加载格式化PROMPT列表
    loadFormatPromptList();
    
    // 加载默认PROMPT
    loadDefaultPrompt();
    
    // 加载默认格式化PROMPT
    loadDefaultFormatPrompt();
    
    // 加载当前项目的文案内容
    loadCurrentProjectContent();
    
    // 加载当前项目的 paper.json 内容
    loadPaperJsonContent();
    
    // 绑定事件监听器
    bindEventListeners();
}

function bindEventListeners() {
    // 主题锁定功能
    const lockThemeBtn = document.getElementById('lock-theme-btn');
    if (lockThemeBtn) {
        lockThemeBtn.addEventListener('click', lockTheme);
    }
    
    // 文案生成按钮
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateText);
    }
    
    // 保存PROMPT按钮
    const savePromptBtn = document.getElementById('save-prompt-btn');
    if (savePromptBtn) {
        savePromptBtn.addEventListener('click', savePrompt);
    }
    
    // 格式化按钮
    const formatBtn = document.getElementById('format-btn');
    if (formatBtn) {
        formatBtn.addEventListener('click', formatText);
    }
    
    // 保存格式化PROMPT按钮
    const saveFormatPromptBtn = document.getElementById('save-format-prompt-btn');
    if (saveFormatPromptBtn) {
        saveFormatPromptBtn.addEventListener('click', saveFormatPrompt);
    }
}

// 主题锁定功能
function lockTheme() {
    const themeInput = document.getElementById('theme-input');
    const theme = themeInput.value.trim();
    
    if (!theme) {
        alert('请输入要锁定的主题');
        return;
    }
    
    // 这里可以添加主题锁定的逻辑
    console.log('锁定主题:', theme);
    alert('主题已锁定: ' + theme);
}

// 加载PROMPT列表
function loadPromptList() {
    fetch('/load_prompt_list/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPromptList(data.prompts, 'prompt-list');
            } else {
                console.error('加载PROMPT列表失败:', data.error);
            }
        })
        .catch(error => {
            console.error('加载PROMPT列表时发生错误:', error);
        });
}

// 加载格式化PROMPT列表
function loadFormatPromptList() {
    fetch('/load_format_prompt_list/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPromptList(data.prompts, 'format-prompt-list');
            } else {
                console.error('加载格式化PROMPT列表失败:', data.error);
            }
        })
        .catch(error => {
            console.error('加载格式化PROMPT列表时发生错误:', error);
        });
}

// 显示PROMPT列表
function displayPromptList(prompts, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    prompts.forEach(prompt => {
        const promptItem = document.createElement('div');
        promptItem.className = 'prompt-item';
        promptItem.innerHTML = `
            <span class="prompt-name">${prompt.name}</span>
            <button class="delete-prompt-btn" onclick="deletePrompt('${prompt.name}', '${containerId}')">🗑️</button>
        `;
        
        // 双击加载PROMPT内容
        promptItem.addEventListener('dblclick', () => {
            loadPromptContent(prompt.name, containerId);
        });
        
        container.appendChild(promptItem);
    });
}

// 加载PROMPT内容
function loadPromptContent(promptName, containerId) {
    let apiUrl, targetTextareaId;
    
    if (containerId === 'prompt-list') {
        apiUrl = '/load_prompt_content/';
        targetTextareaId = 'prompt-input';
    } else if (containerId === 'format-prompt-list') {
        apiUrl = '/load_format_prompt_content/';
        targetTextareaId = 'format-prompt-input';
    }
    
    // 确保文件名包含.txt扩展名
    const filename = promptName.endsWith('.txt') ? promptName : promptName + '.txt';
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ filename: filename })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const textarea = document.getElementById(targetTextareaId);
            if (textarea) {
                textarea.value = data.content;
            }
            
            // 保存当前选择的文件到config.ini配置
            let saveConfigUrl;
            if (containerId === 'prompt-list') {
                saveConfigUrl = '/save_prompt_to_config/';
            } else if (containerId === 'format-prompt-list') {
                saveConfigUrl = '/save_format_prompt_to_config/';
            }
            
            if (saveConfigUrl) {
                fetch(saveConfigUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ filename: filename })
                })
                .then(response => response.json())
                .then(configData => {
                    if (configData.success) {
                        console.log('配置已保存:', configData.message);
                    } else {
                        console.error('保存配置失败:', configData.error);
                    }
                })
                .catch(error => {
                    console.error('保存配置时发生错误:', error);
                });
            }
        } else {
            alert('加载PROMPT内容失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('加载PROMPT内容时发生错误:', error);
        alert('加载PROMPT内容时发生错误');
    });
}

// 加载默认PROMPT
function loadDefaultPrompt() {
    fetch('/load_default_prompt/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.content) {
                const promptInput = document.getElementById('prompt-input');
                if (promptInput) {
                    promptInput.value = data.content;
                }
            }
        })
        .catch(error => {
            console.error('加载默认PROMPT时发生错误:', error);
        });
}

// 加载默认格式化PROMPT
function loadDefaultFormatPrompt() {
    fetch('/load_default_format_prompt/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.content) {
                const formatPromptInput = document.getElementById('format-prompt-input');
                if (formatPromptInput) {
                    formatPromptInput.value = data.content;
                }
            }
        })
        .catch(error => {
            console.error('加载默认格式化PROMPT时发生错误:', error);
        });
}

// 加载当前项目的文案内容
function loadCurrentProjectContent() {
    fetch('/load_paper_content_from_ini/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.content) {
                const generatedContent = document.getElementById('generated-content');
                if (generatedContent) {
                    generatedContent.value = data.content;
                }
            }
        })
        .catch(error => {
            console.error('加载当前项目文案内容时发生错误:', error);
        });
}

// 生成文案
function generateText() {
    const promptInput = document.getElementById('prompt-input');
    const generatedContent = document.getElementById('generated-content');
    const statusMessage = document.getElementById('status-message');
    const generateBtn = document.getElementById('generate-btn');
    
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        alert('请输入PROMPT');
        return;
    }
    
    // 禁用按钮，防止重复点击
    generateBtn.disabled = true;
    generateBtn.innerHTML = '🔄 生成中...';
    
    // 显示生成中状态
    statusMessage.innerHTML = '<div class="status-generating">🔄 正在生成文案...</div>';
    generatedContent.value = '';
    
    fetch('/generate_text/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            generatedContent.value = data.content;
            statusMessage.innerHTML = '<div class="status-success">✅ 文案生成成功</div>';
            
            // 生成成功后，重新加载当前项目的文案内容
            loadCurrentProjectContent();
        } else {
            statusMessage.innerHTML = '<div class="status-error">❌ 生成失败: ' + data.error + '</div>';
        }
    })
    .catch(error => {
        console.error('生成文案时发生错误:', error);
        statusMessage.innerHTML = '<div class="status-error">❌ 生成文案时发生错误</div>';
    })
    .finally(() => {
        // 恢复按钮状态
        generateBtn.disabled = false;
        generateBtn.innerHTML = '✨ 生成文案';
    });
}

// 格式化文案
function formatText() {
    const formatPromptInput = document.getElementById('format-prompt-input');
    const formattedContent = document.getElementById('formatted-content');
    const formatStatusMessage = document.getElementById('format-status-message');
    const formatBtn = document.getElementById('format-btn');
    
    const formatPrompt = formatPromptInput.value.trim();
    
    if (!formatPrompt) {
        alert('请输入格式化PROMPT');
        return;
    }
    
    // 禁用按钮，防止重复点击
    formatBtn.disabled = true;
    formatBtn.innerHTML = '🔄 格式化中...';
    
    // 显示格式化中状态
    formatStatusMessage.innerHTML = '<div class="status-generating">🔄 正在格式化文案...</div>';
    formattedContent.value = '';
    
    fetch('/format_text/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 
            prompt: formatPrompt
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            formatStatusMessage.innerHTML = '<div class="status-success">✅ 文案格式化成功，已保存到 paper.json</div>';
            // 加载并显示 paper.json 的内容
            loadPaperJsonContent();
        } else {
            formatStatusMessage.innerHTML = '<div class="status-error">❌ 格式化失败: ' + data.error + '</div>';
        }
    })
    .catch(error => {
        console.error('格式化文案时发生错误:', error);
        formatStatusMessage.innerHTML = '<div class="status-error">❌ 格式化文案时发生错误</div>';
    })
    .finally(() => {
        // 恢复按钮状态
        formatBtn.disabled = false;
        formatBtn.innerHTML = '🎨 格式化文案';
    });
}

// 加载当前项目的 paper.json 内容
function loadPaperJsonContent() {
    fetch('/load_paper_json/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const formattedContent = document.getElementById('formatted-content');
                if (formattedContent) {
                    // 如果content不为空，尝试格式化JSON显示
                    if (data.content && data.content.trim()) {
                        try {
                            // 解析JSON并重新格式化
                            const jsonData = JSON.parse(data.content);
                            formattedContent.value = JSON.stringify(jsonData, null, 2);
                        } catch (e) {
                            // 如果不是有效JSON，直接显示原内容
                            formattedContent.value = data.content;
                        }
                    } else {
                        formattedContent.value = '';
                    }
                }
            } else {
                console.error('加载 paper.json 失败:', data.error);
            }
        })
        .catch(error => {
            console.error('加载 paper.json 时发生错误:', error);
        });
}

// 保存PROMPT
function savePrompt() {
    const promptInput = document.getElementById('prompt-input');
    const promptContent = promptInput.value.trim();
    
    if (!promptContent) {
        alert('请输入PROMPT内容');
        return;
    }
    
    const promptName = prompt('请输入PROMPT文件名:');
    if (!promptName) {
        return;
    }
    
    fetch('/save_prompt/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 
            filename: promptName,
            content: promptContent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadPromptList(); // 重新加载列表
        } else {
            alert('保存失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('保存PROMPT时发生错误:', error);
        alert('保存PROMPT时发生错误');
    });
}

// 保存格式化PROMPT
function saveFormatPrompt() {
    const formatPromptInput = document.getElementById('format-prompt-input');
    const formatPrompt = formatPromptInput.value.trim();
    
    if (!formatPrompt) {
        alert('请输入格式化PROMPT内容');
        return;
    }
    
    const promptName = prompt('请输入格式化PROMPT文件名:');
    if (!promptName) {
        return;
    }
    
    fetch('/save_format_prompt/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 
            filename: promptName,
            content: formatPrompt
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadFormatPromptList(); // 重新加载列表
        } else {
            alert('保存失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('保存格式化PROMPT时发生错误:', error);
        alert('保存格式化PROMPT时发生错误');
    });
}

// 删除PROMPT
function deletePrompt(promptName, containerId) {
    if (!confirm('确定要删除这个PROMPT吗？')) {
        return;
    }
    
    let apiUrl;
    if (containerId === 'prompt-list') {
        apiUrl = '/delete_prompt/';
    } else if (containerId === 'format-prompt-list') {
        apiUrl = '/delete_format_prompt/';
    }
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ filename: promptName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('PROMPT删除成功');
            if (containerId === 'prompt-list') {
                loadPromptList();
            } else if (containerId === 'format-prompt-list') {
                loadFormatPromptList();
            }
        } else {
            alert('删除失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('删除PROMPT时发生错误:', error);
        alert('删除PROMPT时发生错误');
    });
}

// 获取CSRF token
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