// 系统配置页面JavaScript代码

// 全局变量
let currentApiList = [];
let selectedApiId = null;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 加载API列表
    refreshApiList();
    
    // 加载当前激活的API信息
    loadActiveApiInfo();
    
    // 先加载工作流文件列表，然后再加载保存的配置
    loadWorkflowList().then(() => {
        // 工作流列表加载完成后，再加载保存的配置
        loadSavedConfig();
    });
    
    // 定期更新状态信息
    setInterval(updateStatus, 30000);
});

// 标签页切换功能
function switchTab(tabId) {
    // 隐藏所有标签页内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // 移除所有标签按钮的激活状态
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // 显示选中的标签页内容
    document.getElementById(tabId).classList.add('active');
    
    // 激活对应的标签按钮
    event.target.classList.add('active');
}

// 刷新API列表
function refreshApiList() {
    fetch('/load_api_list/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentApiList = data.apis;
                renderApiList();
            } else {
                console.error('加载API列表失败:', data.error);
                // 如果没有API列表接口，显示空列表
                currentApiList = [];
                renderApiList();
            }
        })
        .catch(error => {
            console.error('加载API列表时发生错误:', error);
            // 显示空列表
            currentApiList = [];
            renderApiList();
        });
}

// 渲染API列表
function renderApiList() {
    const apiListContainer = document.getElementById('api-list');
    
    if (currentApiList.length === 0) {
        apiListContainer.innerHTML = '<div class="no-apis">暂无保存的API配置</div>';
        return;
    }
    
    const listHtml = currentApiList.map(api => `
        <div class="api-item ${api.status}" onclick="selectApi('${api.id}')" ondblclick="activateApi('${api.id}')" title="双击激活API">
            <div class="api-item-name">${api.name}</div>
            <div class="api-item-url">${api.api_url}</div>
            <div class="api-item-status ${api.status}">${api.status === 'active' ? '激活' : '未激活'}</div>
            <div class="api-item-actions">
                <button class="btn-delete" onclick="event.stopPropagation(); deleteApi('${api.id}')" title="删除">×</button>
            </div>
        </div>
    `).join('');
    
    apiListContainer.innerHTML = listHtml;
}

// 选择API
function selectApi(apiId) {
    selectedApiId = apiId;
    const api = currentApiList.find(a => a.id === apiId);
    
    if (api) {
        // 更新表单
        document.getElementById('current-api-id').value = apiId;
        document.getElementById('api-name').value = api.name;
        document.getElementById('api-url').value = api.api_url;
        document.getElementById('api-key').value = api.api_key;
        
        // 更新标题
        document.getElementById('config-panel-title').textContent = `编辑API: ${api.name}`;
        
        // 如果有选择的模型，更新模型下拉菜单
        if (api.selected_model) {
            const availableModelsSelect = document.getElementById('available-models');
            let optionExists = false;
            for (let i = 0; i < availableModelsSelect.options.length; i++) {
                if (availableModelsSelect.options[i].value === api.selected_model) {
                    optionExists = true;
                    break;
                }
            }
            
            if (!optionExists) {
                const option = document.createElement('option');
                option.value = api.selected_model;
                option.textContent = api.selected_model;
                availableModelsSelect.appendChild(option);
            }
            
            availableModelsSelect.value = api.selected_model;
        }
        
        // 更新列表中的选中状态
        document.querySelectorAll('.api-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[onclick="selectApi('${apiId}')"]`).classList.add('selected');
    }
}

// 激活API
function activateApi(apiId) {
    fetch('/activate_api/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ api_id: apiId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 找到被激活的API名称
            const activatedApi = currentApiList.find(api => api.id === apiId);
            const apiName = activatedApi ? activatedApi.name : 'API';
            console.log(`${apiName} 已成功激活！`);
            refreshApiList();
            // 更新当前激活的API信息
            loadActiveApiInfo();
        } else {
            alert('激活失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('激活API时发生错误:', error);
        alert('激活时发生错误');
    });
}

// 加载当前激活的API信息
function loadActiveApiInfo() {
    fetch('/get_active_api/')
        .then(response => response.json())
        .then(data => {
            const activeApiNameElement = document.getElementById('active-api-name');
            if (data.success && data.active_api) {
                activeApiNameElement.textContent = data.active_api.name;
                console.log('当前激活的API:', data.active_api.name);
            } else {
                activeApiNameElement.textContent = '无';
            }
        })
        .catch(error => {
            console.error('获取激活API信息时发生错误:', error);
            document.getElementById('active-api-name').textContent = '获取失败';
        });
}

// 删除API
function deleteApi(apiId) {
    if (confirm('确定要删除这个API配置吗？')) {
        fetch('/delete_api/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ api_id: apiId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('API配置已删除');
                refreshApiList();
                loadActiveApiInfo(); // 刷新当前激活的API信息
                if (selectedApiId === apiId) {
                    clearForm();
                }
            } else {
                alert('删除失败: ' + data.error);
            }
        })
        .catch(error => {
            console.error('删除API时发生错误:', error);
            alert('删除时发生错误');
        });
    }
}

// 保存API配置
function saveApiConfig() {
    const apiName = document.getElementById('api-name').value;
    const apiUrl = document.getElementById('api-url').value;
    const apiKey = document.getElementById('api-key').value;
    const selectedModel = document.getElementById('available-models').value;
    const currentApiId = document.getElementById('current-api-id').value;
    
    if (!apiName || !apiUrl) {
        alert('请填写API名称和API接口地址');
        return;
    }
    
    const configData = {
        api_id: currentApiId || null,
        name: apiName,
        api_url: apiUrl,
        api_key: apiKey,
        selected_model: selectedModel
    };
    
    fetch('/save_api_config/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(configData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(currentApiId ? 'API配置已更新' : 'API配置已保存');
            refreshApiList();
            if (!currentApiId) {
                clearForm();
            }
        } else {
            alert('保存失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('保存API配置时发生错误:', error);
        alert('保存时发生错误');
    });
}

// 清空表单
function clearForm() {
    document.getElementById('current-api-id').value = '';
    document.getElementById('api-name').value = '';
    document.getElementById('api-url').value = '';
    document.getElementById('api-key').value = '';
    document.getElementById('available-models').innerHTML = '<option value="">请先点击"列出模型"</option>';
    document.getElementById('config-panel-title').textContent = '添加新API';
    selectedApiId = null;
    
    // 清除列表中的选中状态
    document.querySelectorAll('.api-item').forEach(item => {
        item.classList.remove('selected');
    });
}

// 保存系统参数
function saveSystemParams() {
    const systemParams = {
        enable_logs: document.getElementById('enable-logs').checked,
        content_generation_timeout: document.getElementById('content-generation-timeout').value,
        format_generation_timeout: document.getElementById('format-generation-timeout').value
    };
    
    fetch('/save_system_config/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(systemParams)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            console.log('系统参数保存成功:', result.message);
        } else {
            alert('系统参数保存失败: ' + result.error);
            console.error('系统参数保存失败:', result);
        }
    })
    .catch(error => {
        alert('保存系统参数时发生网络错误');
        console.error('网络错误:', error);
    });
}

// 保存ComfyUI配置
function saveComfyUIConfig() {
    const comfyUIConfig = {
        comfyui_address: document.getElementById('comfyui-address').value,
        image_workflow: document.getElementById('image-workflow').value,
        audio_workflow: document.getElementById('audio-workflow').value
    };
    
    // 验证工作流文件中的提示词插入标志
    const validationErrors = [];
    
    // 验证图像工作流
    if (comfyUIConfig.image_workflow) {
        if (!validateWorkflowFile(comfyUIConfig.image_workflow, '%AutoMovieclip%')) {
            validationErrors.push('图像生成工作流文件中缺少提示词插入标志 "%AutoMovieclip%"');
        }
    }
    
    // 验证音频工作流
    if (comfyUIConfig.audio_workflow) {
        if (!validateWorkflowFile(comfyUIConfig.audio_workflow, '%AutoMovieSound%')) {
            validationErrors.push('音频生成工作流文件中缺少提示词插入标志 "%AutoMovieSound%"');
        }
    }
    
    // 如果有验证错误，显示错误信息并停止保存
    if (validationErrors.length > 0) {
        const errorMessage = '工作流验证失败：\n\n' + validationErrors.join('\n\n') + 
            '\n\n请确保工作流文件中包含正确的提示词插入标志，这样系统才能正确替换提示词。';
        alert(errorMessage);
        return;
    }
    
    fetch('/save_system_config/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(comfyUIConfig)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            console.log('ComfyUI设置保存成功！');
            console.log('ComfyUI设置保存成功:', result.message);
        } else {
            alert('ComfyUI设置保存失败: ' + result.error);
            console.error('ComfyUI设置保存失败:', result);
        }
    })
    .catch(error => {
        alert('保存ComfyUI设置时发生网络错误');
        console.error('网络错误:', error);
    });
}

// 验证工作流文件中是否包含指定的提示词插入标志
function validateWorkflowFile(workflowFileName, requiredFlag) {
    // 如果没有选择工作流文件，跳过验证
    if (!workflowFileName) {
        return true;
    }
    
    try {
        // 发送同步请求验证工作流文件
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/validate_workflow/', false); // false表示同步请求
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        
        const requestData = {
            workflow_file: workflowFileName,
            required_flag: requiredFlag
        };
        
        xhr.send(JSON.stringify(requestData));
        
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            return response.success && response.has_flag;
        } else {
            console.error('验证工作流文件时发生错误:', xhr.status, xhr.statusText);
            return false;
        }
    } catch (error) {
        console.error('验证工作流文件时发生异常:', error);
        return false;
    }
}

// 保存配置（保留原函数以兼容）
function saveConfig() {
    // 合并所有配置并保存
    const allConfig = {
        enable_logs: document.getElementById('enable-logs').checked,
        content_generation_timeout: document.getElementById('content-generation-timeout').value,
        format_generation_timeout: document.getElementById('format-generation-timeout').value,
        comfyui_address: document.getElementById('comfyui-address').value,
        image_workflow: document.getElementById('image-workflow').value,
        audio_workflow: document.getElementById('audio-workflow').value
    };
    
    fetch('/save_system_config/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(allConfig)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            console.log('所有配置保存成功:', result.message);
        } else {
            alert('配置保存失败: ' + result.error);
            console.error('配置保存失败:', result);
        }
    })
    .catch(error => {
        alert('保存配置时发生网络错误');
        console.error('网络错误:', error);
    });
}

// 列出模型
function listModels() {
    const apiKey = document.getElementById('api-key').value;
    const apiUrl = document.getElementById('api-url').value;
    
    if (!apiUrl) {
        alert('请先输入API接口地址');
        return;
    }
    
    // 显示加载状态
    const availableModelsSelect = document.getElementById('available-models');
    availableModelsSelect.innerHTML = '<option value="">正在加载模型列表...</option>';
    
    // 构建模型列表API地址
    let modelsUrl = apiUrl;
    if (!modelsUrl.endsWith('/')) {
        modelsUrl += '/';
    }
    modelsUrl += 'models';
    
    // 发送请求到指定的API
    fetch(modelsUrl, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 200) {
            return response.json();
        } else {
            throw new Error(`获取失败: ${response.status} ${response.statusText}`);
        }
    })
    .then(data => {
        // 兼容返回是 {"data": [...]} 或直接是 [...]
        const models = data.data || data;
        
        // 转换为可搜索的下拉菜单
        createSearchableSelect(models);
    })
    .catch(error => {
        console.error('获取模型列表失败:', error);
        availableModelsSelect.innerHTML = '<option value="">获取失败，请检查API KEY</option>';
        alert('获取模型列表失败: ' + error.message);
    });
}

// 创建可搜索的下拉菜单
function createSearchableSelect(models) {
    const originalSelect = document.getElementById('available-models');
    const parentDiv = originalSelect.parentNode;
    
    // 移除原有的select和任何搜索框
    const existingSearchInput = parentDiv.querySelector('.model-search-input');
    if (existingSearchInput) {
        existingSearchInput.remove();
    }
    
    // 创建容器
    const searchableContainer = document.createElement('div');
    searchableContainer.className = 'searchable-select-container';
    searchableContainer.style.cssText = `
        position: relative;
        width: 100%;
    `;
    
    // 创建输入框
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'searchable-select-input';
    searchInput.placeholder = '请选择或搜索模型...';
    searchInput.style.cssText = `
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        box-sizing: border-box;
        cursor: pointer;
    `;
    
    // 创建下拉选项容器
    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'searchable-select-options';
    optionsContainer.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        border-radius: 0 0 4px 4px;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        display: none;
    `;
    
    // 存储所有模型数据
    const allModels = [{id: '', name: '请选择模型'}].concat(models.map(model => ({
        id: model.id || '未知模型',
        name: model.id || '未知模型'
    })));
    
    let selectedValue = '';
    
    // 创建选项
    function createOptions(filteredModels = allModels) {
        optionsContainer.innerHTML = '';
        filteredModels.forEach(model => {
            const option = document.createElement('div');
            option.className = 'searchable-select-option';
            option.textContent = model.name;
            option.setAttribute('data-value', model.id);
            option.style.cssText = `
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
            `;
            
            option.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f8f9fa';
            });
            
            option.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'white';
            });
            
            option.addEventListener('click', function() {
                selectedValue = this.getAttribute('data-value');
                searchInput.value = this.textContent;
                optionsContainer.style.display = 'none';
                
                // 更新原始select的值
                let option = originalSelect.querySelector(`option[value="${selectedValue}"]`);
                if (!option) {
                    option = document.createElement('option');
                    option.value = selectedValue;
                    option.textContent = this.textContent;
                    originalSelect.appendChild(option);
                }
                originalSelect.value = selectedValue;
                
                // 触发change事件
                const event = new Event('change', { bubbles: true });
                originalSelect.dispatchEvent(event);
            });
            
            optionsContainer.appendChild(option);
        });
    }
    
    // 初始化选项
    createOptions();
    
    // 输入框事件
    searchInput.addEventListener('focus', function() {
        optionsContainer.style.display = 'block';
    });
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const filteredModels = allModels.filter(model => 
            model.name.toLowerCase().includes(searchTerm)
        );
        createOptions(filteredModels);
        optionsContainer.style.display = 'block';
    });
    
    // 点击外部关闭下拉菜单
    document.addEventListener('click', function(e) {
        if (!searchableContainer.contains(e.target)) {
            optionsContainer.style.display = 'none';
        }
    });
    
    // 组装容器
    searchableContainer.appendChild(searchInput);
    searchableContainer.appendChild(optionsContainer);
    
    // 隐藏原始select但保留其功能
    originalSelect.style.display = 'none';
    
    // 插入新的可搜索下拉菜单
    parentDiv.insertBefore(searchableContainer, originalSelect);
}

// 选择模型
function selectModel() {
    const selectedModel = document.getElementById('available-models').value;
    
    if (!selectedModel) {
        alert('请先选择一个模型');
        return;
    }
    
    // 将选中的模型名称填入模型名称字段
    document.getElementById('model-name').value = selectedModel;
    
    console.log(`已选择模型: ${selectedModel}`);
    alert(`已选择模型: ${selectedModel}\n请点击"保存API"按钮来保存配置`);
}

// 重置系统参数
function resetSystemParams() {
    if (confirm('确定要重置系统参数为默认值吗？')) {
        // 从服务器获取默认值
        fetch('/load_default_values/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const defaults = data.defaults;
                document.getElementById('enable-logs').checked = defaults.enable_logs_default;
                document.getElementById('content-generation-timeout').value = defaults.content_generation_timeout_default;
                document.getElementById('format-generation-timeout').value = defaults.format_generation_timeout_default;
                
                alert('系统参数已重置为默认值！');
                console.log('系统参数已重置为默认值！');
            } else {
                // 如果获取失败，使用硬编码默认值
                document.getElementById('enable-logs').checked = true;
                document.getElementById('content-generation-timeout').value = '300';
                document.getElementById('format-generation-timeout').value = '120';
                alert('系统参数已重置为默认值！');
            }
        })
        .catch(error => {
            console.error('获取默认值失败:', error);
            // 如果获取失败，使用硬编码默认值
            document.getElementById('enable-logs').checked = true;
            document.getElementById('content-generation-timeout').value = '300';
            document.getElementById('format-generation-timeout').value = '120';
            alert('系统参数已重置为默认值！');
        });
    }
}

// 重置ComfyUI配置
function resetComfyUIConfig() {
    if (confirm('确定要重置ComfyUI设置为默认值吗？')) {
        // 从服务器获取默认值
        fetch('/load_default_values/')
        .then(response => response.json())
        .then(data => {
            if (data.comfyui_config) {
                const comfyuiDefaults = data.comfyui_config;
                document.getElementById('comfyui-address').value = comfyuiDefaults.comfyui_address || 'http://192.168.1.85:8188/';
                document.getElementById('image-workflow').value = comfyuiDefaults.image_workflow || '';
                document.getElementById('audio-workflow').value = comfyuiDefaults.audio_workflow || '';
                
                alert('ComfyUI设置已重置为默认值！');
                console.log('ComfyUI设置已重置为默认值！');
            } else {
                // 如果获取失败，使用硬编码默认值
                document.getElementById('comfyui-address').value = 'http://192.168.1.85:8188/';
                document.getElementById('image-workflow').value = '';
                document.getElementById('audio-workflow').value = '';
                alert('ComfyUI设置已重置为默认值！');
            }
        })
        .catch(error => {
            console.error('获取默认值失败:', error);
            // 如果获取失败，使用硬编码默认值
            document.getElementById('comfyui-address').value = 'http://192.168.1.85:8188/';
            document.getElementById('image-workflow').value = '';
            document.getElementById('audio-workflow').value = '';
            alert('ComfyUI设置已重置为默认值！');
        });
    }
}

// 重置配置（保留原函数以兼容）
function resetConfig() {
    if (confirm('确定要重置所有配置为默认值吗？')) {
        // 重置所有表单字段
        document.getElementById('model-name').value = '';
        document.getElementById('api-url').value = '';
        document.getElementById('api-key').value = '';
        document.getElementById('available-models').innerHTML = '<option value="">请先点击"列出模型"</option>';
        document.getElementById('enable-logs').checked = true;
        document.getElementById('comfyui-address').value = 'http://192.168.1.85:8188/';
        document.getElementById('content-generation-timeout').value = '300';
        document.getElementById('format-generation-timeout').value = '120';
        document.getElementById('image-workflow').value = '';
        document.getElementById('audio-workflow').value = '';
        
        alert('所有配置已重置为默认值！');
        console.log('所有配置已重置为默认值！');
    }
}

// 加载保存的配置
function loadSavedConfig() {
    // 同时加载模型配置和系统配置
    Promise.all([
        fetch('/load_model_config/').then(response => response.json()),
        fetch('/load_system_config/').then(response => response.json())
    ])
    .then(([modelData, systemData]) => {
        // 加载模型配置
        if (modelData.success && modelData.config) {
            const config = modelData.config;
            
            // 填充表单字段
            if (config.api_key) {
                document.getElementById('api-key').value = config.api_key;
            }
            if (config.api_url) {
                document.getElementById('api-url').value = config.api_url;
            }
            if (config.model_name) {
                document.getElementById('model-name').value = config.model_name;
            }
            
            // 如果有选择的模型，添加到下拉菜单并选中
            if (config.selected_model) {
                const availableModelsSelect = document.getElementById('available-models');
                
                // 检查是否已存在该选项
                let optionExists = false;
                for (let i = 0; i < availableModelsSelect.options.length; i++) {
                    if (availableModelsSelect.options[i].value === config.selected_model) {
                        optionExists = true;
                        break;
                    }
                }
                
                // 如果不存在，添加该选项
                if (!optionExists) {
                    const option = document.createElement('option');
                    option.value = config.selected_model;
                    option.textContent = config.selected_model;
                    availableModelsSelect.appendChild(option);
                }
                
                // 选中该模型
                availableModelsSelect.value = config.selected_model;
            }
            
            console.log('已加载保存的模型配置');
        } else {
            console.log('没有找到保存的模型配置或配置为空');
        }
        
        // 加载系统配置
        if (systemData.success && systemData.config) {
            const systemConfig = systemData.config;
            
            // 填充系统配置字段
            if (systemConfig.enable_logs !== undefined) {
                document.getElementById('enable-logs').checked = systemConfig.enable_logs;
            }
            if (systemConfig.comfyui_address) {
                document.getElementById('comfyui-address').value = systemConfig.comfyui_address;
            }
            if (systemConfig.image_workflow) {
                document.getElementById('image-workflow').value = systemConfig.image_workflow;
            }
            if (systemConfig.audio_workflow) {
                document.getElementById('audio-workflow').value = systemConfig.audio_workflow;
            }
            if (systemConfig.content_generation_timeout) {
                document.getElementById('content-generation-timeout').value = systemConfig.content_generation_timeout;
            }
            if (systemConfig.format_generation_timeout) {
                document.getElementById('format-generation-timeout').value = systemConfig.format_generation_timeout;
            }
            
            console.log('已加载保存的系统配置');
        } else {
            console.log('没有找到保存的系统配置或配置为空，使用默认值');
        }
    })
    .catch(error => {
        console.error('加载配置时发生错误:', error);
    });
}

// 获取CSRF token的函数
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

// 更新状态信息
function updateStatus() {
    // 更新系统状态信息
    const now = new Date();
    const uptime = Math.floor(Math.random() * 300) + 120; // 模拟运行时间
    const hours = Math.floor(uptime / 60);
    const minutes = uptime % 60;
    document.getElementById('uptime-status').textContent = `⏱️ ${hours}小时${minutes}分钟`;
}

// 加载工作流文件列表
function loadWorkflowList() {
    return fetch('/load_workflow_list/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 填充图像工作流下拉菜单
                const imageWorkflowSelect = document.getElementById('image-workflow');
                imageWorkflowSelect.innerHTML = '<option value="">请选择图像生成工作流</option>';
                
                // 填充音频工作流下拉菜单
                const audioWorkflowSelect = document.getElementById('audio-workflow');
                audioWorkflowSelect.innerHTML = '<option value="">请选择音频生成工作流</option>';
                
                // 添加工作流选项
                data.workflows.forEach(workflow => {
                    const imageOption = document.createElement('option');
                    imageOption.value = workflow;
                    imageOption.textContent = workflow;
                    imageWorkflowSelect.appendChild(imageOption);
                    
                    const audioOption = document.createElement('option');
                    audioOption.value = workflow;
                    audioOption.textContent = workflow;
                    audioWorkflowSelect.appendChild(audioOption);
                });
                
                console.log('工作流列表加载成功');
                return data; // 返回数据以便链式调用
            } else {
                console.error('加载工作流列表失败:', data.error);
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('加载工作流列表时发生错误:', error);
            throw error;
        });
}