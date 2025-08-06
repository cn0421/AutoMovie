// 项目管理页面JavaScript代码

// 页面加载时获取当前项目信息
document.addEventListener('DOMContentLoaded', function() {
    loadCurrentProject();
    
    const createForm = document.querySelector('form');
    const createButton = document.querySelector('button[type="submit"]');
    
    createForm.addEventListener('submit', function(e) {
        e.preventDefault(); // 阻止默认表单提交
        
        // 获取表单数据
        const projectName = document.getElementById('project-name').value.trim();
        const projectDesc = document.getElementById('project-desc').value.trim();
        
        // 禁用按钮，防止重复提交
        createButton.disabled = true;
        createButton.innerHTML = '⏳ 创建中...';
        
        // 准备发送的数据
        const data = {
            project_name: projectName,
            project_desc: projectDesc
        };
        
        // 发送POST请求到创建项目API
        fetch('/create_project/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                // 项目创建成功，无需提示
                // 清空表单
                document.getElementById('project-name').value = '';
                document.getElementById('project-desc').value = '';
                // 刷新当前项目显示
                loadCurrentProject();
                // 刷新项目列表和统计信息
                loadProjectList();
                loadProjectStatistics();
            } else {
                // 创建失败
                alert('❌ 创建项目失败：' + result.error);
            }
        })
        .catch(error => {
            console.error('创建项目时发生错误:', error);
            alert('❌ 创建项目时发生网络错误，请检查网络连接');
        })
        .finally(() => {
            // 恢复按钮状态
            createButton.disabled = false;
            createButton.innerHTML = '✨ 创建项目';
        });
    });
});

// 加载当前项目信息
function loadCurrentProject() {
    fetch('/get_current_project/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.project && data.project.project_path) {
                // 显示当前项目信息
                document.getElementById('current-project-name').textContent = data.project.project_name || '未知项目';
                document.getElementById('current-project-path').textContent = data.project.project_path;
                document.getElementById('current-project-time').textContent = data.project.last_opened_time || '未知时间';
                document.getElementById('current-project-section').style.display = 'block';
            } else {
                // 隐藏当前项目区域
                document.getElementById('current-project-section').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('加载当前项目信息失败:', error);
            document.getElementById('current-project-section').style.display = 'none';
        });
    
    // 同时加载项目列表和统计信息
    loadProjectList();
    loadProjectStatistics();
}

// 加载项目统计信息
function loadProjectStatistics() {
    fetch('/get_project_statistics/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 更新统计数字
                document.getElementById('total-projects').textContent = data.total_projects;
                document.getElementById('completed-projects').textContent = data.completed_projects;
                document.getElementById('ongoing-projects').textContent = data.ongoing_projects;
            } else {
                console.error('获取项目统计信息失败:', data.error);
            }
        })
        .catch(error => {
            console.error('获取项目统计信息失败:', error);
        });
}

// 清除当前项目
function clearCurrentProject() {
    fetch('/clear_current_project/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 刷新当前项目显示
            loadCurrentProject();
        } else {
            alert('关闭项目失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        console.error('关闭项目失败:', error);
        alert('关闭项目失败');
    });
}

// 加载项目列表
function loadProjectList() {
    fetch('/get_project_list/')
        .then(response => response.json())
        .then(data => {
            const projectList = document.getElementById('project-list');
            
            if (data.success) {
                if (data.projects && data.projects.length > 0) {
                    // 生成项目列表HTML
                    let html = '';
                    data.projects.forEach(project => {
                          // 转义路径中的反斜杠
                          const escapedPath = project.path.replace(/\\/g, '\\\\');
                          const escapedName = project.name.replace(/'/g, "\\'");
                          
                          // 生成完成标签HTML
                          const completedTag = project.completed ? 
                              '<span class="completed-tag">完成</span>' : '';
                          
                          html += `
                              <div class="project-item" onclick="selectProjectItem('${escapedPath}', '${escapedName}')" ondblclick="openProjectDirectly('${escapedPath}', '${escapedName}')">
                                  <div class="project-info">
                                      <span class="project-name">${project.name}</span>
                                      <span class="project-time">${project.created_time}</span>
                                  </div>
                                  <div class="project-tags">
                                      ${completedTag}
                                  </div>
                              </div>
                          `;
                     });
                     
                     // 添加调试信息
                     console.log('项目列表加载完成，项目数量:', data.projects.length);
                     
                     // 添加全局变量存储选中的项目
                     window.selectedProject = null;
                    projectList.innerHTML = html;
                } else {
                    projectList.innerHTML = '<div class="empty-message">暂无项目，请先创建一个项目</div>';
                }
            } else {
                projectList.innerHTML = `<div class="error-message">加载项目列表失败: ${data.error || '未知错误'}</div>`;
            }
        })
        .catch(error => {
            console.error('加载项目列表失败:', error);
            document.getElementById('project-list').innerHTML = '<div class="error-message">加载项目列表失败</div>';
        });
}

// 选择项目项
function selectProjectItem(projectPath, projectName) {
    console.log('选择项目:', projectName, '路径:', projectPath);
    
    // 清除之前选中的项目样式
    const allItems = document.querySelectorAll('.project-item');
    allItems.forEach(item => {
        item.classList.remove('selected');
    });
    
    // 设置当前选中项目的样式
    event.target.closest('.project-item').classList.add('selected');
    
    // 存储选中的项目信息
    window.selectedProject = {
        path: projectPath,
        name: projectName
    };
}

// 打开选中的项目
function openSelectedProject() {
    if (!window.selectedProject) {
        alert('请先选择一个项目');
        return;
    }
    
    const projectPath = window.selectedProject.path;
    const projectName = window.selectedProject.name;
    
    openProject(projectPath, projectName);
}

// 双击直接打开项目
function openProjectDirectly(projectPath, projectName) {
    openProject(projectPath, projectName);
}

// 通用的打开项目函数
function openProject(projectPath, projectName) {
    fetch('/open_project/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            project_path: projectPath,
            project_name: projectName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 刷新当前项目显示
            loadCurrentProject();
        } else {
            alert('打开项目失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        console.error('打开项目失败:', error);
        alert('打开项目失败');
    });
}

// 刷新项目列表
function refreshProjectList() {
    loadProjectList();
    loadProjectStatistics();
}