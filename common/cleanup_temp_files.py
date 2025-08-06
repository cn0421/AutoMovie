#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量清理项目临时文件脚本
用于清理所有项目TEMP目录中的临时文件，释放磁盘空间
"""

import os
import shutil
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_temp_files.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_directory_size(directory):
    """获取目录大小（MB）"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        logger.warning(f"计算目录大小失败 {directory}: {e}")
    return total_size / (1024 * 1024)  # 转换为MB

def cleanup_project_temp(project_path):
    """清理单个项目的TEMP目录"""
    temp_dir = os.path.join(project_path, 'TEMP')
    
    if not os.path.exists(temp_dir):
        return 0
    
    # 计算清理前的大小
    size_before = get_directory_size(temp_dir)
    
    if size_before < 1:  # 小于1MB就不清理了
        return 0
    
    try:
        # 清理TEMP目录内容
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        
        logger.info(f"清理项目 {os.path.basename(project_path)}: {size_before:.2f} MB")
        return size_before
        
    except Exception as e:
        logger.error(f"清理项目 {os.path.basename(project_path)} 失败: {e}")
        return 0

def main():
    """主函数"""
    projects_dir = "D:/code/AutoMovie/projects"
    
    if not os.path.exists(projects_dir):
        logger.error(f"项目目录不存在: {projects_dir}")
        return
    
    total_cleaned = 0
    project_count = 0
    
    logger.info("开始批量清理项目临时文件...")
    
    # 遍历所有项目目录
    for project_name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_name)
        
        if os.path.isdir(project_path):
            cleaned_size = cleanup_project_temp(project_path)
            if cleaned_size > 0:
                total_cleaned += cleaned_size
                project_count += 1
    
    logger.info(f"清理完成！共清理 {project_count} 个项目，释放空间 {total_cleaned:.2f} MB ({total_cleaned/1024:.2f} GB)")

if __name__ == "__main__":
    main()