#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoMovie视频处理模块
原使用MoviePy库进行视频拼接和处理，现已注释等待FFMPEG实现
"""

import os
import logging
import subprocess
import configparser
import math
from typing import List, Optional, Tuple, Dict, Any
# MoviePy相关导入已注释，等待FFMPEG实现
# from moviepy import VideoFileClip, concatenate_videoclips, ColorClip
# from moviepy import CompositeVideoClip, TextClip

logger = logging.getLogger(__name__)

class VideoProcessor:
    """
    视频处理类，提供视频拼接、剪辑等功能
    """
    
    def __init__(self):
        self.temp_files = []  # 临时文件列表，用于清理
        self.ffmpeg_path = 'ffmpeg'  # FFMPEG可执行文件路径
    
    def generate_video_segment(self, project_path: str, segment_index: int, 
                              audio_duration: float, image_path: str) -> bool:
        """
        生成单个视频片段
        
        Args:
            project_path: 项目路径
            segment_index: 片段索引（从1开始）
            audio_duration: 音频时长（秒）
            image_path: 图片路径
            
        Returns:
            bool: 是否成功
        """
        try:
            # 读取项目配置
            parameter_file = os.path.join(project_path, 'parameter.ini')
            if not os.path.exists(parameter_file):
                logger.error(f"parameter.ini文件不存在: {parameter_file}")
                return False
            
            config = configparser.ConfigParser(interpolation=None)
            config.read(parameter_file, encoding='utf-8')
            
            # 获取淡入淡出设置
            fade_in_frames = config.getint('VIDEO_FADE', 'fade_in_frames', fallback=4)
            fade_out_frames = config.getint('VIDEO_FADE', 'fade_out_frames', fallback=4)
            video_fps = config.getint('VIDEO_FADE', 'video_fps', fallback=25)
            
            # 计算总帧数
            total_frames = math.ceil(audio_duration * video_fps)
            logger.info(f"片段{segment_index}: 音频时长={audio_duration}秒, 总帧数={total_frames}, FPS={video_fps}")
            
            # 创建TEMP目录
            temp_dir = os.path.join(project_path, 'TEMP')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成帧图片
            frames_generated = self._generate_frames_with_fade(
                image_path, temp_dir, segment_index, total_frames, 
                fade_in_frames, fade_out_frames
            )
            
            if not frames_generated:
                logger.error(f"生成帧图片失败: 片段{segment_index}")
                return False
            
            # 使用FFMPEG合成视频
            video_path = self._create_video_from_frames(
                temp_dir, segment_index, total_frames, video_fps, audio_duration,
                fade_in_frames, fade_out_frames
            )
            
            if not video_path:
                logger.error(f"合成视频失败: 片段{segment_index}")
                return False
            
            # 添加对应的音频文件
            video_with_audio_path = self._add_audio_to_video(
                video_path, project_path, segment_index
            )
            
            if not video_with_audio_path:
                logger.error(f"添加音频失败: 片段{segment_index}")
                return False
            
            # 添加字幕
            final_video_path = self._add_subtitles_to_video(
                video_with_audio_path, project_path, segment_index
            )
            
            if not final_video_path:
                logger.error(f"添加字幕失败: 片段{segment_index}")
                return False
            
            # 清理当前片段的临时帧文件
            self._cleanup_segment_temp_files(temp_dir, segment_index)
            
            # 移动到videos目录
            videos_dir = os.path.join(project_path, 'videos')
            os.makedirs(videos_dir, exist_ok=True)
            
            # 最终输出统一为mp4格式
            final_output_path = os.path.join(videos_dir, f'segment_{segment_index:03d}.mp4')
            if os.path.exists(final_video_path):
                # 如果是.mov格式，需要转换为.mp4
                if final_video_path.endswith('.mov'):
                    # 使用FFmpeg转换格式
                    cmd = [
                        self.ffmpeg_path,
                        '-i', final_video_path,
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-y',
                        final_output_path
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        os.remove(final_video_path)  # 删除临时.mov文件
                        logger.info(f"视频片段生成完成: {final_output_path}")
                        return True
                    else:
                        logger.error(f"格式转换失败: {result.stderr}")
                        return False
                else:
                    os.rename(final_video_path, final_output_path)
                    logger.info(f"视频片段生成完成: {final_output_path}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"生成视频片段失败: {e}")
            return False
    
    def concatenate_videos(self, video_paths: List[str], output_path: str, 
                          project_path: str, fps: int = 24, codec: str = 'libx264') -> bool:
        """
        拼接多个视频文件并添加背景音乐
        
        Args:
            video_paths: 视频文件路径列表
            output_path: 输出文件路径（应该在项目根目录）
            project_path: 项目路径
            fps: 输出视频帧率
            codec: 视频编码器
            
        Returns:
            bool: 是否成功
        """
        try:
            logger.info(f"开始拼接 {len(video_paths)} 个视频文件")
            
            # 检查输入文件
            valid_paths = []
            for path in video_paths:
                if os.path.exists(path):
                    valid_paths.append(path)
                    logger.info(f"找到视频文件: {path}")
                else:
                    logger.warning(f"视频文件不存在: {path}")
            
            if not valid_paths:
                logger.error("没有找到有效的视频文件")
                return False
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 使用_merge_video_segments_with_background_music方法进行合并
            return self._merge_video_segments_with_background_music(
                valid_paths, output_path, project_path
            )
            
        except Exception as e:
            logger.error(f"视频拼接失败: {e}")
            return False
        
        # 以下是原MoviePy实现，已注释
        # try:
        #     logger.info(f"开始拼接 {len(video_paths)} 个视频文件")
        #     
        #     # 检查输入文件
        #     valid_paths = []
        #     for path in video_paths:
        #         if os.path.exists(path):
        #             valid_paths.append(path)
        #             logger.info(f"找到视频文件: {path}")
        #         else:
        #             logger.warning(f"视频文件不存在: {path}")
        #     
        #     if not valid_paths:
        #         logger.error("没有找到有效的视频文件")
        #         return False
        #     
        #     # 加载视频片段
        #     clips = []
        #     for path in valid_paths:
        #         try:
        #             clip = VideoFileClip(path)
        #             clips.append(clip)
        #             logger.info(f"加载视频: {path}, 时长: {clip.duration}秒")
        #         except Exception as e:
        #             logger.error(f"加载视频失败 {path}: {e}")
        #             continue
        #     
        #     if not clips:
        #         logger.error("没有成功加载任何视频片段")
        #         return False
        #     
        #     # 拼接视频
        #     final_video = concatenate_videoclips(clips)
        #     
        #     # 确保输出目录存在
        #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
        #     
        #     # 输出视频
        #     logger.info(f"开始输出拼接视频: {output_path}")
        #     final_video.write_videofile(output_path, fps=fps, codec=codec, threads=os.cpu_count())
        #     
        #     # 清理内存
        #     final_video.close()
        #     for clip in clips:
        #         clip.close()
        #     
        #     logger.info(f"视频拼接完成: {output_path}")
        #     logger.info(f"总时长: {final_video.duration}秒")
        #     
        #     return True
        #     
        # except Exception as e:
        #     logger.error(f"视频拼接失败: {e}")
        #     return False
    
    def create_color_clip(self, color: Tuple[int, int, int], duration: float, 
                         size: Tuple[int, int] = (1920, 1080), fps: int = 24) -> Optional[object]:
        """
        创建纯色背景视频片段
        
        Args:
            color: RGB颜色值
            duration: 时长（秒）
            size: 视频尺寸
            fps: 帧率
            
        Returns:
            视频片段对象或None（原返回ColorClip，现等待FFMPEG实现）
        """
        # MoviePy实现已注释，等待FFMPEG实现
        logger.error("MoviePy创建颜色片段功能已弃用，等待FFMPEG实现")
        return None
        
        # 以下是原MoviePy实现，已注释
        # try:
        #     clip = ColorClip(size=size, color=color, duration=duration)
        #     clip = clip.with_fps(fps)
        #     return clip
        # except Exception as e:
        #     logger.error(f"创建颜色片段失败: {e}")
        #     return None
    
    def trim_video(self, input_path: str, output_path: str, 
                   start_time: float, end_time: float) -> bool:
        """
        剪辑视频片段
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            
        Returns:
            bool: 是否成功
        """
        # MoviePy实现已注释，等待FFMPEG实现
        logger.error("MoviePy视频剪辑功能已弃用，等待FFMPEG实现")
        return False
        
        # 以下是原MoviePy实现，已注释
        # try:
        #     if not os.path.exists(input_path):
        #         logger.error(f"输入视频文件不存在: {input_path}")
        #         return False
        #     
        #     # 加载视频
        #     clip = VideoFileClip(input_path)
        #     
        #     # 检查时间范围
        #     if start_time < 0 or end_time > clip.duration or start_time >= end_time:
        #         logger.error(f"时间范围无效: {start_time}-{end_time}, 视频时长: {clip.duration}")
        #         clip.close()
        #         return False
        #     
        #     # 剪辑片段
        #     trimmed_clip = clip.subclip(start_time, end_time)
        #     
        #     # 确保输出目录存在
        #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
        #     
        #     # 输出视频
        #     logger.info(f"剪辑视频: {start_time}s-{end_time}s -> {output_path}")
        #     trimmed_clip.write_videofile(output_path, threads=os.cpu_count())
        #     
        #     # 清理内存
        #     trimmed_clip.close()
        #     clip.close()
        #     
        #     logger.info(f"视频剪辑完成: {output_path}")
        #     return True
        #     
        # except Exception as e:
        #     logger.error(f"视频剪辑失败: {e}")
        #     return False
    
    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        获取视频信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            包含视频信息的字典或None
        """
        # MoviePy实现已注释，等待FFMPEG实现
        logger.error("MoviePy获取视频信息功能已弃用，等待FFMPEG实现")
        return None
        
        # 以下是原MoviePy实现，已注释
        # try:
        #     if not os.path.exists(video_path):
        #         logger.error(f"视频文件不存在: {video_path}")
        #         return None
        #     
        #     clip = VideoFileClip(video_path)
        #     
        #     info = {
        #         'path': video_path,
        #         'duration': clip.duration,
        #         'fps': clip.fps,
        #         'size': clip.size,
        #         'width': clip.w,
        #         'height': clip.h,
        #         'total_frames': int(clip.fps * clip.duration) if clip.fps else 0
        #     }
        #     
        #     clip.close()
        #     
        #     logger.info(f"视频信息: {info}")
        #     return info
        #     
        # except Exception as e:
        #     logger.error(f"获取视频信息失败: {e}")
        #     return None
    
    def resize_video(self, input_path: str, output_path: str, 
                    new_size: Tuple[int, int]) -> bool:
        """
        调整视频尺寸
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            new_size: 新的尺寸 (width, height)
            
        Returns:
            bool: 是否成功
        """
        # MoviePy实现已注释，等待FFMPEG实现
        logger.error("MoviePy视频尺寸调整功能已弃用，等待FFMPEG实现")
        return False
        
        # 以下是原MoviePy实现，已注释
        # try:
        #     if not os.path.exists(input_path):
        #         logger.error(f"输入视频文件不存在: {input_path}")
        #         return False
        #     
        #     # 加载视频
        #     clip = VideoFileClip(input_path)
        #     
        #     # 调整尺寸
        #     resized_clip = clip.resize(new_size)
        #     
        #     # 确保输出目录存在
        #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
        #     
        #     # 输出视频
        #     logger.info(f"调整视频尺寸: {clip.size} -> {new_size}")
        #     resized_clip.write_videofile(output_path, threads=os.cpu_count())
        #     
        #     # 清理内存
        #     resized_clip.close()
        #     clip.close()
        #     
        #     logger.info(f"视频尺寸调整完成: {output_path}")
        #     return True
        #     
        # except Exception as e:
        #     logger.error(f"视频尺寸调整失败: {e}")
        #     return False
    
    def add_subtitle(self, video_path: str, output_path: str, 
                    subtitle_text: str, start_time: float, duration: float,
                    font_size: int = 50, color: str = 'white', 
                    position: Tuple[str, str] = ('center', 'bottom'),
                    font_path: str = None, stroke_color: str = None, 
                    stroke_width: int = 0, auto_wrap: bool = True) -> bool:
        """
        为视频添加单个字幕
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            subtitle_text: 字幕文本
            start_time: 字幕开始时间（秒）
            duration: 字幕持续时间（秒）
            font_size: 字体大小
            color: 字体颜色
            position: 字幕位置 ('center', 'bottom') 等
            font_path: 字体文件路径，默认使用思源黑体
            stroke_color: 描边颜色，None表示无描边
            stroke_width: 描边宽度，0表示无描边
            auto_wrap: 是否自动换行，True时根据视频宽度的2/3自动换行
            
        Returns:
            bool: 是否成功
        """
        # MoviePy实现已注释，等待FFMPEG实现
        logger.error("MoviePy字幕添加功能已弃用，等待FFMPEG实现")
        return False
        
        # 以下是原MoviePy实现，已注释
        # try:
        #     if not os.path.exists(video_path):
        #         logger.error(f"输入视频文件不存在: {video_path}")
        #         return False
        #     
        #     # 默认使用思源黑体字体
        #     if font_path is None:
        #         font_path = os.path.join(os.path.dirname(__file__), 'Fonts', 'SourceHanSansCN-Regular.otf')  # 思源黑体          
        #     # 加载视频
        #     video = VideoFileClip(video_path)
        #     
        #     # 处理字幕文本自动换行
        #     if auto_wrap:
        #         subtitle_text = self._wrap_subtitle_text(subtitle_text, video.w, font_size)
        #     
        #     # 创建字幕
        #     subtitle = TextClip(
        #         text=subtitle_text,
        #         font=font_path,
        #         font_size=font_size,
        #         color=color,
        #         stroke_color=stroke_color,
        #         stroke_width=stroke_width
        #     ).with_position(position).with_duration(duration).with_start(start_time)
        #     
        #     # 合成视频和字幕
        #     final_video = CompositeVideoClip([video, subtitle])
        #     
        #     # 确保输出目录存在
        #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
        #     
        #     # 输出视频
        #     logger.info(f"添加字幕: '{subtitle_text}' 到视频 {video_path}")
        #     final_video.write_videofile(output_path, codec='libx264', threads=os.cpu_count())
        #     
        #     # 清理内存
        #     final_video.close()
        #     subtitle.close()
        #     video.close()
        #     
        #     logger.info(f"字幕添加完成: {output_path}")
        #     return True
        #     
        # except Exception as e:
        #     logger.error(f"添加字幕失败: {e}")
        #     return False
    
    def add_subtitles_batch(self, video_path: str, output_path: str,
                           subtitles: List[Dict[str, Any]],
                           font_size: int = 50, color: str = 'white',
                           position: Tuple[str, str] = ('center', 'bottom'),
                           font_path: str = None, stroke_color: str = None,
                           stroke_width: int = 0, auto_wrap: bool = True) -> bool:
        """
        为视频批量添加字幕
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            subtitles: 字幕列表，每个元素包含 {'text': str, 'start': float, 'duration': float}
            font_size: 字体大小
            color: 字体颜色
            position: 字幕位置
            font_path: 字体文件路径，默认使用思源黑体
            stroke_color: 描边颜色，None表示无描边
            stroke_width: 描边宽度，0表示无描边
            auto_wrap: 是否自动换行，True时根据视频宽度的2/3自动换行
            
        Returns:
            bool: 是否成功
        """
        # MoviePy实现已注释，等待FFMPEG实现
        logger.error("MoviePy批量字幕添加功能已弃用，等待FFMPEG实现")
        return False
        
        # 以下是原MoviePy实现，已注释
        # try:
        #     if not os.path.exists(video_path):
        #         logger.error(f"输入视频文件不存在: {video_path}")
        #         return False
        #     
        #     if not subtitles:
        #         logger.warning("字幕列表为空")
        #         return False
        #     
        #     # 默认使用思源黑体字体
        #     if font_path is None:
        #          font_path = os.path.join(os.path.dirname(__file__), 'Fonts', 'SourceHanSansCN-Regular.otf')
        #     
        #     # 加载视频
        #     video = VideoFileClip(video_path)
        #     
        #     # 创建所有字幕片段
        #     subtitle_clips = []
        #     for i, subtitle_info in enumerate(subtitles):
        #         try:
        #             text = subtitle_info.get('text', '')
        #             start = subtitle_info.get('start', 0)
        #             duration = subtitle_info.get('duration', 2)
        #             
        #             if not text:
        #                 logger.warning(f"跳过空字幕 {i}")
        #                 continue
        #             
        #             # 处理字幕文本自动换行
        #             if auto_wrap:
        #                 text = self._wrap_subtitle_text(text, video.w, font_size)
        #             
        #             subtitle = TextClip(
        #                 text=text,
        #                 font=font_path,
        #                 font_size=font_size,
        #                 color=color,
        #                 stroke_color=stroke_color,
        #                 stroke_width=stroke_width
        #             ).with_position(position).with_duration(duration).with_start(start)
        #             
        #             subtitle_clips.append(subtitle)
        #             logger.info(f"创建字幕 {i}: '{text}' ({start}s-{start+duration}s)")
        #             
        #         except Exception as e:
        #             logger.error(f"创建字幕 {i} 失败: {e}")
        #             continue
        #     
        #     if not subtitle_clips:
        #         logger.error("没有成功创建任何字幕")
        #         video.close()
        #         return False
        #     
        #     # 合成视频和所有字幕
        #     all_clips = [video] + subtitle_clips
        #     final_video = CompositeVideoClip(all_clips)
        #     
        #     # 确保输出目录存在
        #     os.makedirs(os.path.dirname(output_path), exist_ok=True)
        #     
        #     # 输出视频
        #     logger.info(f"批量添加 {len(subtitle_clips)} 个字幕到视频 {video_path}")
        #     final_video.write_videofile(output_path, codec='libx264', threads=os.cpu_count())
        #     
        #     # 清理内存
        #     final_video.close()
        #     for subtitle in subtitle_clips:
        #         subtitle.close()
        #     video.close()
        #     
        #     logger.info(f"批量字幕添加完成: {output_path}")
        #     return True
        #     
        # except Exception as e:
        #     logger.error(f"批量添加字幕失败: {e}")
        #     return False
    
    def _wrap_subtitle_text(self, text: str, video_width: int, font_size: int) -> str:
        """
        根据视频宽度自动换行字幕文本
        
        Args:
            text: 原始字幕文本
            video_width: 视频宽度（像素）
            font_size: 字体大小
            
        Returns:
            str: 换行后的字幕文本
        """
        try:
            # 计算字幕最大宽度（视频宽度的2/3）
            max_subtitle_width = int(video_width * 2 / 3)
            
            # 估算每个字符的平均宽度（基于字体大小）
            # 中文字符通常比英文字符宽，这里使用一个经验值
            avg_char_width = font_size * 0.8  # 经验值，可能需要根据实际字体调整
            
            # 计算每行最大字符数
            max_chars_per_line = int(max_subtitle_width / avg_char_width)
            
            # 如果文本长度小于等于最大字符数，直接返回
            if len(text) <= max_chars_per_line:
                return text
            
            # 进行换行处理
            lines = []
            current_line = ""
            
            for char in text:
                # 如果当前行加上新字符不超过最大长度
                if len(current_line + char) <= max_chars_per_line:
                    current_line += char
                else:
                    # 当前行已满，开始新行
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            
            # 添加最后一行
            if current_line:
                lines.append(current_line)
            
            # 用换行符连接所有行
            wrapped_text = '\n'.join(lines)
            
            logger.info(f"字幕自动换行: '{text}' -> '{wrapped_text}'")
            return wrapped_text
            
        except Exception as e:
            logger.error(f"字幕换行处理失败: {e}")
            return text  # 出错时返回原文本
    
    def _generate_frames_with_fade(self, image_path: str, temp_dir: str, 
                                  segment_index: int, total_frames: int,
                                  fade_in_frames: int, fade_out_frames: int) -> bool:
        """
        生成带淡入淡出效果的帧图片
        
        Args:
            image_path: 原始图片路径
            temp_dir: 临时目录
            segment_index: 片段索引
            total_frames: 总帧数
            fade_in_frames: 淡入帧数
            fade_out_frames: 淡出帧数
            
        Returns:
            bool: 是否成功
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"图片文件不存在: {image_path}")
                return False
            
            segment_temp_dir = os.path.join(temp_dir, f'segment_{segment_index:03d}')
            os.makedirs(segment_temp_dir, exist_ok=True)
            
            # 先生成一张标准图片作为模板
            template_frame_path = os.path.join(segment_temp_dir, 'template_frame.png')
            cmd = [
                self.ffmpeg_path,
                '-i', image_path,
                '-frames:v', '1',
                '-y',
                template_frame_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"生成模板帧失败: {result.stderr}")
                return False
            
            for frame_num in range(total_frames):
                frame_path = os.path.join(segment_temp_dir, f'frame_{frame_num:06d}.png')
                
                # 计算透明度
                alpha = 1.0
                need_fade_effect = False
                
                # 淡入效果
                if frame_num < fade_in_frames:
                    alpha = frame_num / fade_in_frames
                    need_fade_effect = True
                
                # 淡出效果
                elif frame_num >= total_frames - fade_out_frames:
                    alpha = (total_frames - frame_num) / fade_out_frames
                    need_fade_effect = True
                
                # 如果不需要淡入淡出效果，直接复制模板图片
                if not need_fade_effect:
                    import shutil
                    shutil.copy2(template_frame_path, frame_path)
                else:
                    # 应用黑色蒙版淡入淡出效果
                    cmd = [
                        self.ffmpeg_path,
                        '-i', image_path,
                        '-vf', f'format=rgba,colorchannelmixer=rr={alpha}:gg={alpha}:bb={alpha}:aa=1',
                        '-frames:v', '1',
                        '-y',
                        frame_path
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                    if result.returncode != 0:
                        logger.error(f"生成帧{frame_num}失败: {result.stderr}")
                        return False
            
            # 删除模板文件
            if os.path.exists(template_frame_path):
                os.remove(template_frame_path)
            
            logger.info(f"生成{total_frames}帧图片完成: {segment_temp_dir}")
            return True
            
        except Exception as e:
            logger.error(f"生成帧图片失败: {e}")
            return False
    
    def _create_video_from_frames(self, temp_dir: str, segment_index: int,
                                 total_frames: int, video_fps: int, 
                                 audio_duration: float, fade_in_frames: int = 0,
                                 fade_out_frames: int = 0) -> Optional[str]:
        """
        从帧图片创建视频
        
        Args:
            temp_dir: 临时目录
            segment_index: 片段索引
            total_frames: 总帧数
            video_fps: 视频帧率
            audio_duration: 音频时长
            
        Returns:
            视频文件路径或None
        """
        try:
            segment_temp_dir = os.path.join(temp_dir, f'segment_{segment_index:03d}')
            video_path = os.path.join(temp_dir, f'video_{segment_index:03d}.mp4')
            
            # 使用FFMPEG从帧图片创建视频，支持透明度
            # 检查是否有透明度帧
            has_fade_frames = fade_in_frames > 0 or fade_out_frames > 0
            
            if has_fade_frames:
                # 有淡入淡出效果，使用支持alpha通道的编码器
                video_path = video_path.replace('.mp4', '.mov')  # 改为mov格式
                cmd = [
                    self.ffmpeg_path,
                    '-framerate', str(video_fps),
                    '-i', os.path.join(segment_temp_dir, 'frame_%06d.png'),
                    '-t', str(audio_duration),
                    '-c:v', 'qtrle',  # QuickTime Animation RLE支持alpha通道
                    '-pix_fmt', 'rgba',
                    '-y',
                    video_path
                ]
            else:
                # 没有淡入淡出效果，使用标准编码器
                cmd = [
                    self.ffmpeg_path,
                    '-framerate', str(video_fps),
                    '-i', os.path.join(segment_temp_dir, 'frame_%06d.png'),
                    '-t', str(audio_duration),
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    video_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode != 0:
                logger.error(f"创建视频失败: {result.stderr}")
                return None
            
            logger.info(f"视频创建完成: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"创建视频失败: {e}")
            return None
    
    def _add_subtitles_to_video(self, video_path: str, project_path: str, 
                               segment_index: int) -> Optional[str]:
        """
        为视频添加字幕
        
        Args:
            video_path: 视频文件路径
            project_path: 项目路径
            segment_index: 片段索引
            
        Returns:
            添加字幕后的视频路径或None
        """
        try:
            # 读取项目配置
            parameter_file = os.path.join(project_path, 'parameter.ini')
            config = configparser.ConfigParser(interpolation=None)
            config.read(parameter_file, encoding='utf-8')
            
            # 获取字幕文本
            subtitle_text = config.get('PAPER_CONTENT', f'line_{segment_index}', fallback='')
            if not subtitle_text:
                logger.warning(f"未找到片段{segment_index}的字幕文本")
                return video_path
            
            # 获取字幕设置
            font_size = config.getint('VIDEO_SUBTITLE', 'size', fallback=24)
            font_color = config.get('VIDEO_SUBTITLE', 'color', fallback='#ffffff')
            stroke_width = config.getint('VIDEO_SUBTITLE', 'stroke_width', fallback=2)
            stroke_color = config.get('VIDEO_SUBTITLE', 'stroke_color', fallback='#000000')
            position = config.get('VIDEO_SUBTITLE', 'position', fallback='bottom-quarter')
            font_file = config.get('VIDEO_SUBTITLE', 'font', fallback='SourceHanSansCN-Regular.otf')
            
            # 构建字体文件路径
            font_path = os.path.join(os.path.dirname(__file__), 'Fonts', font_file)
            if not os.path.exists(font_path):
                logger.warning(f"指定字体文件不存在: {font_path}，使用默认字体")
                font_path = os.path.join(os.path.dirname(__file__), 'Fonts', 'SourceHanSansCN-Regular.otf')
                if not os.path.exists(font_path):
                    logger.warning(f"默认字体文件也不存在: {font_path}，将使用系统默认字体")
                    font_path = None
            
            # 输出路径，保持原格式
            if video_path.endswith('.mov'):
                output_path = video_path.replace('.mov', '_with_subtitle.mov')
            else:
                output_path = video_path.replace('.mp4', '_with_subtitle.mp4')
            
            # 构建字幕滤镜
            # 转换颜色格式
            font_color_rgb = font_color.replace('#', '0x')
            stroke_color_rgb = stroke_color.replace('#', '0x')
            
            # 设置字幕位置
            if position == 'bottom-quarter':
                subtitle_y = 'h*3/4'
            elif position == 'bottom-center':
                subtitle_y = 'h-th-20'
            elif position == 'center':
                subtitle_y = '(h-th)/2'
            elif position == 'top-center':
                subtitle_y = '20'
            else:
                subtitle_y = 'h*3/4'
            
            # 转义字幕文本中的特殊字符
            subtitle_text_escaped = subtitle_text.replace(':', '\\:').replace("'", "\\'").replace('"', '\\"')
            
            # 构建字幕滤镜参数
            if font_path and os.path.exists(font_path):
                # 使用测试验证的字体路径格式：转义冒号但不加引号
                font_path_escaped = font_path.replace('\\', '/').replace(':', '\\\\:')
                drawtext_filter = f"drawtext=fontfile={font_path_escaped}:text='{subtitle_text_escaped}':fontsize={font_size}:fontcolor={font_color_rgb}:x=(w-tw)/2:y={subtitle_y}:borderw={stroke_width}:bordercolor={stroke_color_rgb}"
                logger.info(f"使用自定义字体: {font_path}")
            else:
                drawtext_filter = f"drawtext=text='{subtitle_text_escaped}':fontsize={font_size}:fontcolor={font_color_rgb}:x=(w-tw)/2:y={subtitle_y}:borderw={stroke_width}:bordercolor={stroke_color_rgb}"
                logger.info("使用系统默认字体")
            
            # 使用FFMPEG添加字幕
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-vf', drawtext_filter,
                '-c:a', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode != 0:
                logger.error(f"添加字幕失败: {result.stderr}")
                return None
            
            logger.info(f"字幕添加完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"添加字幕失败: {e}")
            return None
    
    def _add_audio_to_video(self, video_path: str, project_path: str, 
                           segment_index: int) -> Optional[str]:
        """
        为视频添加对应的音频文件
        
        Args:
            video_path: 视频文件路径
            project_path: 项目路径
            segment_index: 片段索引
            
        Returns:
            添加音频后的视频路径或None
        """
        try:
            # 查找对应的音频文件（支持多种格式）
            audios_dir = os.path.join(project_path, 'audios')
            
            # 支持的音频格式列表，按优先级排序
            audio_extensions = ['.flac', '.wav', '.mp3', '.m4a', '.aac', '.ogg']
            audio_path = None
            
            # 按优先级查找音频文件
            for ext in audio_extensions:
                potential_path = os.path.join(audios_dir, f'script_{segment_index}_1{ext}')
                if os.path.exists(potential_path):
                    audio_path = potential_path
                    break
            
            # 检查音频文件是否存在，不存在则报错
            if audio_path is None:
                error_msg = f"音频文件不存在: script_{segment_index}_1.{{flac,wav,mp3,m4a,aac,ogg}}，请先生成对应的音频文件"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # 输出路径，保持原格式
            if video_path.endswith('.mov'):
                output_path = video_path.replace('.mov', '_with_audio.mov')
            else:
                output_path = video_path.replace('.mp4', '_with_audio.mp4')
            
            # 使用FFMPEG将音频添加到视频
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  # 复制视频流，不重新编码
                '-c:a', 'aac',   # 音频编码为AAC
                '-map', '0:v:0', # 映射第一个输入的视频流
                '-map', '1:a:0', # 映射第二个输入的音频流
                '-shortest',     # 以最短的流为准
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode != 0:
                logger.error(f"添加音频失败: {result.stderr}")
                return None
            
            logger.info(f"音频添加完成: {audio_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"添加音频失败: {e}")
            return None
    
    def _merge_video_segments_with_background_music(self, segment_files: List[str], 
                                                   output_path: str, project_path: str) -> bool:
        """
        合并视频片段并添加背景音乐
        
        Args:
            segment_files: 视频片段文件列表
            output_path: 输出文件路径
            project_path: 项目路径
            
        Returns:
            bool: 是否成功
        """
        try:
            if not segment_files:
                logger.error("没有视频片段文件可合并")
                return False
            
            # 创建临时文件列表
            temp_list_file = os.path.join(os.path.dirname(output_path), 'segments_list.txt')
            
            # 写入文件列表
            with open(temp_list_file, 'w', encoding='utf-8') as f:
                for segment_file in segment_files:
                    f.write(f"file '{segment_file}'\n")
            
            # 先合并视频片段（不包含音频）
            temp_video_path = output_path.replace('.mp4', '_temp_video.mp4')
            
            cmd = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', temp_list_file,
                '-c', 'copy',
                '-y',
                temp_video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode != 0:
                logger.error(f"合并视频失败: {result.stderr}")
                return False
            
            logger.info(f"视频片段合并完成: {temp_video_path}")
            
            # 读取项目配置获取背景音乐设置
            parameter_file = os.path.join(project_path, 'parameter.ini')
            config = configparser.ConfigParser(interpolation=None)
            config.read(parameter_file, encoding='utf-8')
            
            # 检查是否有背景音乐设置
            if config.has_section('VIDEO_BACKGROUND_MUSIC'):
                bgm_file = config.get('VIDEO_BACKGROUND_MUSIC', 'file', fallback='')
                if bgm_file and bgm_file != 'None' and bgm_file.strip():
                    # 添加背景音乐
                    success = self._add_background_music_to_video(
                        temp_video_path, output_path, project_path, bgm_file
                    )
                    
                    # 清理临时文件
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)
                    if os.path.exists(temp_list_file):
                        os.remove(temp_list_file)
                    
                    return success
            
            # 如果没有背景音乐，直接重命名临时文件
            if os.path.exists(temp_video_path):
                os.rename(temp_video_path, output_path)
            
            # 清理临时文件
            if os.path.exists(temp_list_file):
                os.remove(temp_list_file)
            
            # 清理整个TEMP目录
            temp_dir = os.path.join(project_path, 'TEMP')
            self._cleanup_all_temp_files(temp_dir)
            
            # 复制视频到output目录
            self._copy_video_to_output_dir(output_path)
            
            logger.info(f"最终视频生成完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"合并视频片段失败: {e}")
            return False
    
    def _add_background_music_to_video(self, video_path: str, output_path: str,
                                      project_path: str, bgm_filename: str) -> bool:
        """
        为视频添加背景音乐
        
        Args:
            video_path: 视频文件路径
            output_path: 输出文件路径
            project_path: 项目路径
            bgm_filename: 背景音乐文件名
            
        Returns:
            bool: 是否成功
        """
        try:
            # 查找背景音乐文件
            bgm_path = None
            
            # 在common/back_mus目录中查找
            common_bgm_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'back_mus')
            potential_bgm_path = os.path.join(common_bgm_dir, bgm_filename)
            
            if os.path.exists(potential_bgm_path):
                bgm_path = potential_bgm_path
            else:
                # 在项目目录中查找
                project_bgm_path = os.path.join(project_path, bgm_filename)
                if os.path.exists(project_bgm_path):
                    bgm_path = project_bgm_path
            
            if not bgm_path:
                logger.warning(f"背景音乐文件不存在: {bgm_filename}")
                # 如果找不到背景音乐，直接复制视频
                if os.path.exists(video_path):
                    os.rename(video_path, output_path)
                return True
            
            # 读取背景音乐设置
            parameter_file = os.path.join(project_path, 'parameter.ini')
            config = configparser.ConfigParser(interpolation=None)
            config.read(parameter_file, encoding='utf-8')
            
            volume = config.getfloat('VIDEO_BACKGROUND_MUSIC', 'volume', fallback=30) / 100.0
            fade_in = config.getfloat('VIDEO_BACKGROUND_MUSIC', 'fade_in', fallback=2.0)
            fade_out = config.getfloat('VIDEO_BACKGROUND_MUSIC', 'fade_out', fallback=2.0)
            loop_mode = config.get('VIDEO_BACKGROUND_MUSIC', 'loop_mode', fallback='loop')
            
            # 使用FFMPEG添加背景音乐
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-i', bgm_path,
                '-filter_complex',
                f'[1:a]volume={volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2',
                '-c:v', 'copy',
                '-y',
                output_path
            ]
            
            # 如果需要循环背景音乐
            if loop_mode == 'loop':
                cmd = [
                    self.ffmpeg_path,
                    '-i', video_path,
                    '-stream_loop', '-1',
                    '-i', bgm_path,
                    '-filter_complex',
                    f'[1:a]volume={volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2',
                    '-c:v', 'copy',
                    '-shortest',
                    '-y',
                    output_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode != 0:
                logger.error(f"添加背景音乐失败: {result.stderr}")
                # 如果添加背景音乐失败，直接复制原视频
                if os.path.exists(video_path):
                    os.rename(video_path, output_path)
                return True
            
            # 复制视频到output目录
            self._copy_video_to_output_dir(output_path)
            
            logger.info(f"背景音乐添加完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"添加背景音乐失败: {e}")
            # 如果出错，直接复制原视频
            if os.path.exists(video_path):
                os.rename(video_path, output_path)
            return True
    
    def _cleanup_segment_temp_files(self, temp_dir: str, segment_index: int):
        """
        清理指定片段的临时文件
        
        Args:
            temp_dir: 临时目录
            segment_index: 片段索引
        """
        try:
            segment_temp_dir = os.path.join(temp_dir, f'segment_{segment_index:03d}')
            if os.path.exists(segment_temp_dir):
                import shutil
                shutil.rmtree(segment_temp_dir)
                logger.info(f"清理片段{segment_index}临时文件: {segment_temp_dir}")
            
            # 清理临时视频文件
            temp_video_files = [
                os.path.join(temp_dir, f'video_{segment_index:03d}.mp4'),
                os.path.join(temp_dir, f'video_{segment_index:03d}.mov'),
                os.path.join(temp_dir, f'video_{segment_index:03d}_with_audio.mp4'),
                os.path.join(temp_dir, f'video_{segment_index:03d}_with_audio.mov')
            ]
            
            for temp_file in temp_video_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.info(f"删除临时视频文件: {temp_file}")
                    
        except Exception as e:
            logger.warning(f"清理片段{segment_index}临时文件失败: {e}")
    
    def _cleanup_all_temp_files(self, temp_dir: str):
        """
        清理整个TEMP目录
        
        Args:
            temp_dir: 临时目录路径
        """
        try:
            if os.path.exists(temp_dir):
                import shutil
                # 删除TEMP目录下的所有内容
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                logger.info(f"清理TEMP目录完成: {temp_dir}")
        except Exception as e:
            logger.warning(f"清理TEMP目录失败: {e}")
    
    def _copy_video_to_output_dir(self, video_path: str):
        """
        将视频文件复制到output目录
        
        Args:
            video_path: 视频文件路径
        """
        try:
            if not os.path.exists(video_path):
                logger.warning(f"视频文件不存在，无法复制到output目录: {video_path}")
                return
            
            # 获取项目根目录（AutoMovie目录）
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # 从common目录向上一级
            output_dir = os.path.join(project_root, 'output')
            
            # 确保output目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取视频文件名
            video_filename = os.path.basename(video_path)
            output_video_path = os.path.join(output_dir, video_filename)
            
            # 复制视频文件
            import shutil
            shutil.copy2(video_path, output_video_path)
            
            logger.info(f"视频已复制到output目录: {output_video_path}")
            
        except Exception as e:
            logger.error(f"复制视频到output目录失败: {e}")
    
    def cleanup(self):
        """
        清理临时文件
        """
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.info(f"删除临时文件: {temp_file}")
            except Exception as e:
                logger.warning(f"删除临时文件失败 {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def __del__(self):
        """析构函数，自动清理临时文件"""
        self.cleanup()


def create_demo_videos(output_dir: str = "TEST/demo_videos") -> List[str]:
    """
    创建一些演示视频文件用于测试
    
    Args:
        output_dir: 输出目录
        
    Returns:
        创建的视频文件路径列表
    """
    # MoviePy实现已注释，等待FFMPEG实现
    logger.error("MoviePy演示视频创建功能已弃用，等待FFMPEG实现")
    return []
    
    # 以下是原MoviePy实现，已注释
    # processor = VideoProcessor()
    # 
    # # 确保输出目录存在
    # os.makedirs(output_dir, exist_ok=True)
    # 
    # created_files = []
    # 
    # # 创建三个不同颜色的短视频
    # colors = [
    #     ((255, 0, 0), "red"),      # 红色
    #     ((0, 255, 0), "green"),    # 绿色
    #     ((0, 0, 255), "blue")      # 蓝色
    # ]
    # 
    # for color, name in colors:
    #     try:
    #         clip = processor.create_color_clip(color, duration=2.0, size=(640, 480))
    #         if clip:
    #             output_path = os.path.join(output_dir, f"{name}_clip.mp4")
    #             clip.write_videofile(output_path, fps=24, threads=os.cpu_count())
    #             clip.close()
    #             created_files.append(output_path)
    #             logger.info(f"创建演示视频: {output_path}")
    #     except Exception as e:
    #         logger.error(f"创建{name}视频失败: {e}")
    # 
    # return created_files


if __name__ == "__main__":
    # MoviePy测试代码已注释，等待FFMPEG实现
    print("MoviePy视频处理功能已弃用，等待FFMPEG实现")
    
    # 以下是原MoviePy测试代码，已注释
    # # 简单测试
    # logging.basicConfig(level=logging.INFO)
    # 
    # processor = VideoProcessor()
    # 
    # # 创建演示视频
    # demo_videos = create_demo_videos()
    # 
    # if demo_videos:
    #     # 测试拼接功能
    #     output_path = "TEST/demo_videos/concatenated_demo.mp4"
    #     success = processor.concatenate_videos(demo_videos, output_path)
    #     
    #     if success:
    #         print(f"演示视频拼接成功: {output_path}")
    #         
    #         # 获取视频信息
    #         info = processor.get_video_info(output_path)
    #         if info:
    #             print(f"拼接后视频信息: {info}")
    #         
    #         # 测试字幕功能（带描边）
    #         subtitle_output = "TEST/demo_videos/video_with_subtitle.mp4"
    #         subtitle_success = processor.add_subtitle(
    #             video_path=output_path,
    #             output_path=subtitle_output,
    #             subtitle_text="这是一个字幕演示",
    #             start_time=1.0,
    #             duration=3.0,
    #             font_size=60,
    #             color='white',
    #             stroke_color='black',
    #             stroke_width=3
    #         )
    #         
    #         if subtitle_success:
    #             print(f"单个字幕添加成功: {subtitle_output}")
    #         
    #         # 测试批量字幕功能
    #         batch_subtitle_output = "TEST/demo_videos/video_with_batch_subtitles.mp4"
    #         subtitles = [
    #             {'text': '第一段字幕', 'start': 0.5, 'duration': 2.0},
    #             {'text': '第二段字幕', 'start': 2.5, 'duration': 2.0},
    #             {'text': '第三段字幕', 'start': 4.5, 'duration': 1.5}
    #         ]
    #         
    #         batch_success = processor.add_subtitles_batch(
    #             video_path=output_path,
    #             output_path=batch_subtitle_output,
    #             subtitles=subtitles,
    #             font_size=50,
    #             color='white',
    #             stroke_color='black',
    #             stroke_width=2
    #         )
    #         
    #         if batch_success:
    #             print(f"批量字幕添加成功: {batch_subtitle_output}")
    #             
    #     else:
    #         print("演示视频拼接失败")
    # 
    # # 清理
    # processor.cleanup()