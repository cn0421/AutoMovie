"""
音频处理模块
提供音频去除无声部分、时长计算等功能
"""

import os
import logging
import configparser
from typing import Tuple, Optional

try:
    import librosa
    import soundfile as sf
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioProcessor:
    """音频处理器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        if not AUDIO_LIBS_AVAILABLE:
            self.logger.warning("音频处理库未安装，某些功能可能不可用")
    
    def trim_silence(self, audio_path: str, output_path: str = None, 
                    silence_threshold: float = 0.01, frame_length: int = 2048, 
                    hop_length: int = 512, pre_pause: float = 0.0, 
                    post_pause: float = 0.0) -> Tuple[str, float]:
        """
        去除音频文件前后的无声部分，并添加指定的前后停顿
        
        参数:
            audio_path: 输入音频文件路径
            output_path: 输出音频文件路径，如果为None则覆盖原文件
            silence_threshold: 静音阈值（0-1之间）
            frame_length: 帧长度
            hop_length: 跳跃长度
            pre_pause: 前停顿时长（秒）
            post_pause: 后停顿时长（秒）
            
        返回:
            (处理后的文件路径, 音频时长)
        """
        if not AUDIO_LIBS_AVAILABLE:
            raise ImportError("音频处理库未安装，请安装 librosa 和 soundfile")
        
        try:
            # 读取音频文件
            self.logger.info(f"开始处理音频文件: {audio_path}")
            audio, sr = librosa.load(audio_path, sr=None)
            
            # 计算原始时长
            original_duration = len(audio) / sr
            self.logger.info(f"原始音频时长: {original_duration:.2f}秒")
            
            # 去除前后的静音部分
            # 使用librosa的trim函数，基于能量阈值
            audio_trimmed, index = librosa.effects.trim(
                audio, 
                top_db=20,  # 静音阈值（分贝）
                frame_length=frame_length,
                hop_length=hop_length
            )
            
            # 添加前后停顿
            if pre_pause > 0 or post_pause > 0:
                # 创建静音片段
                pre_silence_samples = int(pre_pause * sr) if pre_pause > 0 else 0
                post_silence_samples = int(post_pause * sr) if post_pause > 0 else 0
                
                pre_silence = np.zeros(pre_silence_samples)
                post_silence = np.zeros(post_silence_samples)
                
                # 拼接：前停顿 + 音频 + 后停顿
                audio_with_pauses = np.concatenate([pre_silence, audio_trimmed, post_silence])
                
                self.logger.info(f"添加了前停顿 {pre_pause:.2f}秒，后停顿 {post_pause:.2f}秒")
            else:
                audio_with_pauses = audio_trimmed
            
            # 计算处理后的时长
            final_duration = len(audio_with_pauses) / sr
            trimmed_duration = len(audio_trimmed) / sr
            self.logger.info(f"去除静音后时长: {trimmed_duration:.2f}秒")
            self.logger.info(f"最终音频时长: {final_duration:.2f}秒")
            self.logger.info(f"去除了 {original_duration - trimmed_duration:.2f}秒的静音")
            
            # 确定输出路径
            if output_path is None:
                output_path = audio_path
            
            # 保存处理后的音频
            sf.write(output_path, audio_with_pauses, sr)
            self.logger.info(f"处理后的音频已保存: {output_path}")
            
            return output_path, final_duration
            
        except Exception as e:
            self.logger.error(f"音频处理失败: {e}")
            raise
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        获取音频文件时长
        
        参数:
            audio_path: 音频文件路径
            
        返回:
            音频时长（秒）
        """
        if not AUDIO_LIBS_AVAILABLE:
            raise ImportError("音频处理库未安装，请安装 librosa")
        
        try:
            duration = librosa.get_duration(filename=audio_path)
            return duration
        except Exception as e:
            self.logger.error(f"获取音频时长失败: {e}")
            raise
    
    def create_project_parameter_ini(self, project_path: str) -> bool:
        """
        为新项目创建parameter.ini文件
        
        参数:
            project_path: 项目路径
            
        返回:
            是否创建成功
        """
        try:
            parameter_file = os.path.join(project_path, 'parameter.ini')
            
            # 如果parameter.ini已存在，不覆盖
            if os.path.exists(parameter_file):
                self.logger.info(f"parameter.ini已存在，跳过创建: {parameter_file}")
                return True
            
            # 创建默认配置文件
            self._create_default_parameter_ini(parameter_file)
            self.logger.info(f'项目parameter.ini文件创建成功: {parameter_file}')
            return True
            
        except Exception as e:
            self.logger.error(f'创建项目parameter.ini失败: {e}')
            return False
    
    def update_parameter_ini(self, project_path: str, script_id: int, duration: float) -> bool:
        """
        更新parameter.ini文件中的音频时长信息
        
        参数:
            project_path: 项目路径
            script_id: 脚本ID
            duration: 音频时长
            
        返回:
            是否更新成功
        """
        try:
            parameter_file = os.path.join(project_path, 'parameter.ini')
            
            # 如果parameter.ini不存在，创建一个
            if not os.path.exists(parameter_file):
                self.logger.info(f"parameter.ini不存在，创建新文件: {parameter_file}")
                self._create_default_parameter_ini(parameter_file)
            
            # 读取配置文件
            config = configparser.ConfigParser()
            config.read(parameter_file, encoding='utf-8')
            
            # 确保存在AUDIO_INFO节
            if not config.has_section('AUDIO_INFO'):
                config.add_section('AUDIO_INFO')
                self.logger.info("创建AUDIO_INFO配置节")
            
            # 确保存在VIDEO_SUBTITLE节（如果不存在则添加默认配置）
            if not config.has_section('VIDEO_SUBTITLE'):
                self._add_default_video_subtitle_config(config)
            
            # 设置音频时长
            duration_key = f'script_{script_id}_duration'
            config.set('AUDIO_INFO', duration_key, str(duration))
            
            # 写入配置文件
            with open(parameter_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.logger.info(f'音频时长已写入parameter.ini: {duration_key}={duration:.2f}秒')
            return True
            
        except Exception as e:
            self.logger.error(f'更新parameter.ini失败: {e}')
            return False
    
    def _create_default_parameter_ini(self, parameter_file: str):
        """
        创建带有默认配置的parameter.ini文件
        
        参数:
            parameter_file: parameter.ini文件路径
        """
        try:
            config = configparser.ConfigParser()
            
            # 添加默认的VIDEO_SUBTITLE配置
            self._add_default_video_subtitle_config(config)
            
            # 添加默认的音频停顿配置
            self._add_default_audio_pause_config(config)
            
            # 添加默认的背景音乐配置
            self._add_default_background_music_config(config)
            
            # 添加默认的视频淡入淡出配置
            self._add_default_video_fade_config(config)
            
            # 写入文件
            with open(parameter_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.logger.info(f"已创建带有默认配置的parameter.ini文件: {parameter_file}")
            
        except Exception as e:
            self.logger.error(f'创建默认parameter.ini文件失败: {e}')
            # 如果创建失败，至少创建一个空文件
            with open(parameter_file, 'w', encoding='utf-8') as f:
                f.write("")
    
    def _add_default_video_subtitle_config(self, config: configparser.ConfigParser):
        """
        添加默认的VIDEO_SUBTITLE配置到ConfigParser对象
        
        参数:
            config: ConfigParser对象
        """
        try:
            # 尝试从主配置文件读取默认值
            default_values = self._load_default_subtitle_config()
            
            # 添加VIDEO_SUBTITLE节
            config.add_section('VIDEO_SUBTITLE')
            
            # 设置默认值
            for key, value in default_values.items():
                config.set('VIDEO_SUBTITLE', key, value)
            
            self.logger.info("已添加默认VIDEO_SUBTITLE配置")
            
        except Exception as e:
            self.logger.error(f'添加默认VIDEO_SUBTITLE配置失败: {e}')
    
    def _load_default_subtitle_config(self) -> dict:
        """
        从主配置文件加载默认的字幕配置
        
        返回:
            dict: 默认字幕配置字典
        """
        default_config = {
            'font': 'Arial',
            'size': '24',
            'color': 'white',
            'position': 'bottom-quarter',
            'horizontal_align': 'center',
            'stroke_color': 'black',
            'stroke_width': '2'
        }
        
        try:
            # 获取项目根目录路径
            import os
            # 从common/audio_processor.py向上两级到达项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(project_root, 'config.ini')
            
            if os.path.exists(config_path):
                main_config = configparser.ConfigParser(interpolation=None)
                main_config.read(config_path, encoding='utf-8')
                
                # 如果主配置文件中有VIDEO_SUBTITLE节，使用其中的值
                if main_config.has_section('VIDEO_SUBTITLE'):
                    for key in default_config.keys():
                        if main_config.has_option('VIDEO_SUBTITLE', key):
                            default_config[key] = main_config.get('VIDEO_SUBTITLE', key)
                    
                    self.logger.info("已从主配置文件加载默认字幕配置")
                else:
                    self.logger.info("主配置文件中未找到VIDEO_SUBTITLE节，使用内置默认值")
            else:
                self.logger.warning("主配置文件不存在，使用内置默认值")
                
        except Exception as e:
            self.logger.error(f'加载默认字幕配置失败，使用内置默认值: {e}')
        
        return default_config
    
    def _add_default_video_fade_config(self, config: configparser.ConfigParser):
        """
        添加默认的视频淡入淡出配置到ConfigParser对象
        
        参数:
            config: ConfigParser对象
        """
        try:
            # 尝试从主配置文件读取默认值
            default_values = self._load_default_video_fade_config()
            
            # 添加VIDEO_FADE节
            config.add_section('VIDEO_FADE')
            
            # 设置默认值
            for key, value in default_values.items():
                config.set('VIDEO_FADE', key, str(value))
            
            self.logger.info("已添加默认VIDEO_FADE配置")
            
        except Exception as e:
            self.logger.error(f'添加默认VIDEO_FADE配置失败: {e}')
    
    def _load_default_video_fade_config(self) -> dict:
        """
        从主配置文件加载默认的视频淡入淡出配置
        
        返回:
            dict: 默认视频淡入淡出配置字典
        """
        default_config = {
            'fade_in_frames': 4,
            'fade_out_frames': 4,
            'video_fps': 25
        }
        
        try:
            # 获取项目根目录路径
            import os
            # 从common/audio_processor.py向上两级到达项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(project_root, 'config.ini')
            
            if os.path.exists(config_path):
                main_config = configparser.ConfigParser(interpolation=None)
                main_config.read(config_path, encoding='utf-8')
                
                # 如果主配置文件中有VIDEO_FADE_CONFIG节，使用其中的值
                if main_config.has_section('VIDEO_FADE_CONFIG'):
                    if main_config.has_option('VIDEO_FADE_CONFIG', 'default_fade_in_frames'):
                        default_config['fade_in_frames'] = main_config.getint('VIDEO_FADE_CONFIG', 'default_fade_in_frames')
                    if main_config.has_option('VIDEO_FADE_CONFIG', 'default_fade_out_frames'):
                        default_config['fade_out_frames'] = main_config.getint('VIDEO_FADE_CONFIG', 'default_fade_out_frames')
                    if main_config.has_option('VIDEO_FADE_CONFIG', 'default_video_fps'):
                        default_config['video_fps'] = main_config.getint('VIDEO_FADE_CONFIG', 'default_video_fps')
                    
                    self.logger.info(f"从主配置文件加载视频淡入淡出默认配置: {default_config}")
                else:
                    self.logger.info("主配置文件中未找到VIDEO_FADE_CONFIG节，使用内置默认值")
            else:
                self.logger.warning("主配置文件不存在，使用内置默认值")
                
        except Exception as e:
            self.logger.error(f'加载默认视频淡入淡出配置失败: {e}')
            
        return default_config
    
    def _add_default_audio_pause_config(self, config: configparser.ConfigParser):
        """
        添加默认的音频停顿配置到ConfigParser对象
        
        参数:
            config: ConfigParser对象
        """
        try:
            # 从主配置文件加载默认值
            default_values = self._load_default_audio_pause_config()
            
            # 添加AUDIO_PAUSE节
            config.add_section('AUDIO_PAUSE')
            
            # 设置默认值
            config.set('AUDIO_PAUSE', 'pre_pause', str(default_values['pre_pause']))
            config.set('AUDIO_PAUSE', 'post_pause', str(default_values['post_pause']))
            
            self.logger.info(f"已添加默认音频停顿配置: 前停顿={default_values['pre_pause']}秒, 后停顿={default_values['post_pause']}秒")
            
        except Exception as e:
            self.logger.error(f'添加默认音频停顿配置失败: {e}')
    
    def _load_default_audio_pause_config(self) -> dict:
        """
        从主配置文件加载默认的音频停顿配置
        
        返回:
            dict: 默认音频停顿配置字典
        """
        default_config = {
            'pre_pause': 0.25,
            'post_pause': 0.25
        }
        
        try:
            # 获取项目根目录路径
            import os
            # 从common/audio_processor.py向上两级到达项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(project_root, 'config.ini')
            
            if os.path.exists(config_path):
                main_config = configparser.ConfigParser(interpolation=None)
                main_config.read(config_path, encoding='utf-8')
                
                # 如果主配置文件中有AUDIO_PAUSE_CONFIG节，使用其中的值
                if main_config.has_section('AUDIO_PAUSE_CONFIG'):
                    if main_config.has_option('AUDIO_PAUSE_CONFIG', 'default_pre_pause'):
                        default_config['pre_pause'] = main_config.getfloat('AUDIO_PAUSE_CONFIG', 'default_pre_pause')
                    if main_config.has_option('AUDIO_PAUSE_CONFIG', 'default_post_pause'):
                        default_config['post_pause'] = main_config.getfloat('AUDIO_PAUSE_CONFIG', 'default_post_pause')
                    
                    self.logger.info(f"已从主配置文件加载默认音频停顿配置: 前停顿={default_config['pre_pause']}秒, 后停顿={default_config['post_pause']}秒")
                else:
                    self.logger.info("主配置文件中未找到AUDIO_PAUSE_CONFIG节，使用内置默认值")
            else:
                self.logger.warning("主配置文件不存在，使用内置默认值")
                
        except Exception as e:
            self.logger.error(f'加载默认音频停顿配置失败: {e}')
            
        return default_config
    
    def _add_default_background_music_config(self, config: configparser.ConfigParser):
        """
        添加默认的背景音乐配置到ConfigParser对象
        
        参数:
            config: ConfigParser对象
        """
        try:
            # 尝试从主配置文件读取默认值
            default_values = self._load_default_background_music_config()
            
            # 添加VIDEO_BACKGROUND_MUSIC节
            config.add_section('VIDEO_BACKGROUND_MUSIC')
            
            # 设置默认值
            for key, value in default_values.items():
                config.set('VIDEO_BACKGROUND_MUSIC', key, str(value))
            
            self.logger.info("已添加默认VIDEO_BACKGROUND_MUSIC配置")
            
        except Exception as e:
            self.logger.error(f'添加默认VIDEO_BACKGROUND_MUSIC配置失败: {e}')
    
    def _load_default_background_music_config(self) -> dict:
        """
        从主配置文件加载默认的背景音乐配置
        
        返回:
            dict: 默认背景音乐配置字典
        """
        default_config = {
            'file': '',
            'volume': 10,
            'fade_in': 2.0,
            'fade_out': 2.0,
            'loop_mode': 'loop'
        }
        
        try:
            # 获取项目根目录路径
            import os
            # 从common/audio_processor.py向上两级到达项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(project_root, 'config.ini')
            
            if os.path.exists(config_path):
                main_config = configparser.ConfigParser(interpolation=None)
                main_config.read(config_path, encoding='utf-8')
                
                # 如果主配置文件中有VIDEO_BACKGROUND_MUSIC节，使用其中的值
                if main_config.has_section('VIDEO_BACKGROUND_MUSIC'):
                    if main_config.has_option('VIDEO_BACKGROUND_MUSIC', 'default_file'):
                        default_config['file'] = main_config.get('VIDEO_BACKGROUND_MUSIC', 'default_file')
                    if main_config.has_option('VIDEO_BACKGROUND_MUSIC', 'default_volume'):
                        default_config['volume'] = main_config.getint('VIDEO_BACKGROUND_MUSIC', 'default_volume')
                    if main_config.has_option('VIDEO_BACKGROUND_MUSIC', 'default_fade_in'):
                        default_config['fade_in'] = main_config.getfloat('VIDEO_BACKGROUND_MUSIC', 'default_fade_in')
                    if main_config.has_option('VIDEO_BACKGROUND_MUSIC', 'default_fade_out'):
                        default_config['fade_out'] = main_config.getfloat('VIDEO_BACKGROUND_MUSIC', 'default_fade_out')
                    if main_config.has_option('VIDEO_BACKGROUND_MUSIC', 'default_loop_mode'):
                        default_config['loop_mode'] = main_config.get('VIDEO_BACKGROUND_MUSIC', 'default_loop_mode')
                    
                    self.logger.info(f"从主配置文件加载背景音乐默认配置: {default_config}")
                else:
                    self.logger.info("主配置文件中未找到VIDEO_BACKGROUND_MUSIC节，使用内置默认值")
            else:
                self.logger.warning(f"主配置文件不存在: {config_path}，使用内置默认值")
                
        except Exception as e:
            self.logger.error(f'加载默认背景音乐配置失败: {e}')
            
        return default_config
    
    def _load_audio_pause_from_parameter(self, project_path: str) -> Tuple[float, float]:
        """
        从项目的parameter.ini文件读取音频停顿配置
        
        参数:
            project_path: 项目路径
            
        返回:
            Tuple[float, float]: (前停顿时长, 后停顿时长)
        """
        try:
            parameter_file = os.path.join(project_path, 'parameter.ini')
            
            # 如果parameter.ini不存在，创建一个带默认配置的
            if not os.path.exists(parameter_file):
                self.logger.info(f"parameter.ini不存在，创建新文件: {parameter_file}")
                self._create_default_parameter_ini(parameter_file)
            
            # 读取配置文件
            config = configparser.ConfigParser()
            config.read(parameter_file, encoding='utf-8')
            
            # 确保存在AUDIO_PAUSE节
            if not config.has_section('AUDIO_PAUSE'):
                self.logger.info("parameter.ini中不存在AUDIO_PAUSE节，添加默认配置")
                self._add_default_audio_pause_config(config)
                # 保存更新后的配置
                with open(parameter_file, 'w', encoding='utf-8') as f:
                    config.write(f)
            
            # 读取停顿配置
            pre_pause = config.getfloat('AUDIO_PAUSE', 'pre_pause', fallback=0.25)
            post_pause = config.getfloat('AUDIO_PAUSE', 'post_pause', fallback=0.25)
            
            self.logger.info(f"从parameter.ini加载音频停顿配置: 前停顿={pre_pause:.2f}秒, 后停顿={post_pause:.2f}秒")
            return pre_pause, post_pause
            
        except Exception as e:
            self.logger.error(f'从parameter.ini加载音频停顿配置失败: {e}')
            # 返回默认值
            default_config = self._load_default_audio_pause_config()
            return default_config['pre_pause'], default_config['post_pause']
    
    def process_audio_after_generation(self, audio_path: str, project_path: str, 
                                     script_id: int) -> Tuple[str, float]:
        """
        音频生成后的完整处理流程：去除静音 + 添加停顿 + 更新parameter.ini
        
        参数:
            audio_path: 音频文件路径
            project_path: 项目路径
            script_id: 脚本ID
            
        返回:
            (处理后的文件路径, 音频时长)
        """
        try:
            # 1. 从parameter.ini读取停顿配置
            pre_pause, post_pause = self._load_audio_pause_from_parameter(project_path)
            
            # 2. 去除前后静音部分并添加停顿
            processed_path, duration = self.trim_silence(
                audio_path, 
                pre_pause=pre_pause, 
                post_pause=post_pause
            )
            
            # 3. 更新parameter.ini文件中的音频时长
            self.update_parameter_ini(project_path, script_id, duration)
            
            self.logger.info(f"音频处理完成: script_id={script_id}, 时长={duration:.2f}秒, 前停顿={pre_pause:.2f}秒, 后停顿={post_pause:.2f}秒")
            return processed_path, duration
            
        except Exception as e:
            self.logger.error(f"音频后处理失败: {e}")
            raise


def process_audio_file(audio_path: str, project_path: str, script_id: int) -> Tuple[str, float]:
    """
    便捷函数：处理音频文件（去除静音 + 更新parameter.ini）
    
    参数:
        audio_path: 音频文件路径
        project_path: 项目路径
        script_id: 脚本ID
        
    返回:
        (处理后的文件路径, 音频时长)
    """
    processor = AudioProcessor()
    return processor.process_audio_after_generation(audio_path, project_path, script_id)


# 使用示例
if __name__ == "__main__":
    # 测试音频处理
    processor = AudioProcessor()
    
    # 示例：处理音频文件
    try:
        audio_path = "test_audio.wav"
        project_path = "test_project"
        script_id = 1
        
        processed_path, duration = processor.process_audio_after_generation(
            audio_path, project_path, script_id
        )
        print(f"处理完成: {processed_path}, 时长: {duration:.2f}秒")
        
    except Exception as e:
        print(f"处理失败: {e}")