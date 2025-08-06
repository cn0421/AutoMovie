/**
 * 首页JavaScript功能模块
 * 主要负责README.md内容的Markdown渲染
 */

(function() {
    'use strict';
    
    /**
     * 简单的Markdown渲染函数
     * @param {string} markdown - 原始Markdown文本
     * @returns {string} 渲染后的HTML
     */
    function renderMarkdown(markdown) {
        let html = markdown
            // 处理标题
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // 处理粗体
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // 处理代码块
            .replace(/```([\s\S]*?)```/g, '<pre style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto;"><code>$1</code></pre>')
            // 处理行内代码
            .replace(/`([^`]+)`/g, '<code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px;">$1</code>')
            // 处理无序列表
            .replace(/^- (.*$)/gim, '<li>$1</li>')
            // 处理有序列表
            .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
            // 处理段落（双换行）
            .replace(/\n\n/g, '</p><p>')
            // 处理单换行
            .replace(/\n/g, '<br>');
        
        // 包装列表项
        html = html.replace(/(<li>.*?<\/li>)/gs, function(match) {
            if (!match.includes('<ul>') && !match.includes('<ol>')) {
                return '<ul style="margin-left: 20px; margin-bottom: 20px;">' + match + '</ul>';
            }
            return match;
        });
        
        // 包装段落
        if (!html.startsWith('<h1>') && !html.startsWith('<h2>') && !html.startsWith('<h3>')) {
            html = '<p>' + html + '</p>';
        }
        
        return html;
    }
    
    /**
     * 初始化首页功能
     */
    function initIndexPage() {
        const contentDiv = document.getElementById('readme-content');
        
        if (!contentDiv) {
            console.error('未找到readme-content容器');
            return;
        }
        
        // 获取从后端传递的README内容
        const readmeContent = window.readmeContent;
        
        if (readmeContent) {
            contentDiv.innerHTML = renderMarkdown(readmeContent);
        } else {
            contentDiv.innerHTML = '<p>无法加载README.md内容</p>';
        }
    }
    
    // 页面加载完成后初始化
    document.addEventListener('DOMContentLoaded', initIndexPage);
    
    // 导出到全局（如果需要）
    window.AutoMovie = window.AutoMovie || {};
    window.AutoMovie.Index = {
        renderMarkdown: renderMarkdown,
        init: initIndexPage
    };
    
})();