import websocket
import uuid
import json
import urllib.request
import urllib.parse
from PIL import Image
import io
import os
import logging
import configparser
import requests
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple

class ComfyUIClient:
    """ComfyUI WebSocket API客户端"""
    
    def __init__(self, server_address: str = None):
        # 如果没有提供server_address，从config.ini读取
        if server_address is None:
            server_address = self._load_comfyui_address()
        
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.logger = logging.getLogger(__name__)
        
    def _load_comfyui_address(self) -> str:
        """从config.ini加载ComfyUI地址"""
        try:
            # 获取项目根目录路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, 'config.ini')
            
            if os.path.exists(config_path):
                config = configparser.ConfigParser(interpolation=None)
                config.read(config_path, encoding='utf-8')
                
                # 优先从COMFYUI_CONFIG节读取，如果不存在则从SYSTEM_CONFIG节读取（向后兼容）
                if config.has_section('COMFYUI_CONFIG'):
                    address = config.get('COMFYUI_CONFIG', 'comfyui_address', fallback='http://127.0.0.1:8188/')
                elif config.has_section('SYSTEM_CONFIG'):
                    address = config.get('SYSTEM_CONFIG', 'comfyui_address', fallback='http://127.0.0.1:8188/')
                else:
                    address = 'http://127.0.0.1:8188/'
                
                # 移除http://前缀，只保留地址和端口
                if address.startswith('http://'):
                    address = address[7:]
                if address.startswith('https://'):
                    address = address[8:]
                if address.endswith('/'):
                    address = address[:-1]
                return address
            
            # 如果没有配置文件或配置，返回默认值
            return "127.0.0.1:8188"
            
        except Exception as e:
            self.logger.error(f"加载ComfyUI地址配置失败: {e}")
            return "127.0.0.1:8188"
    
    def _load_workflow_from_config(self, workflow_type: str = 'image') -> dict:
        """从config.ini和工作流文件加载工作流配置"""
        try:
            # 获取项目根目录路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, 'config.ini')
            
            workflow_filename = None
            
            # 从config.ini读取工作流文件名
            if os.path.exists(config_path):
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                
                # 优先从COMFYUI_CONFIG节读取，如果不存在则从SYSTEM_CONFIG节读取（向后兼容）
                if config.has_section('COMFYUI_CONFIG'):
                    if workflow_type == 'image':
                        workflow_filename = config.get('COMFYUI_CONFIG', 'image_workflow', fallback=None)
                    elif workflow_type == 'audio':
                        workflow_filename = config.get('COMFYUI_CONFIG', 'audio_workflow', fallback=None)
                elif config.has_section('SYSTEM_CONFIG'):
                    if workflow_type == 'image':
                        workflow_filename = config.get('SYSTEM_CONFIG', 'image_workflow', fallback=None)
                    elif workflow_type == 'audio':
                        workflow_filename = config.get('SYSTEM_CONFIG', 'audio_workflow', fallback=None)
            
            # 如果没有配置工作流文件，使用默认的
            if not workflow_filename:
                workflow_filename = 'Workflow.json'  # 默认工作流文件
            
            # 加载工作流文件
            workflow_path = os.path.join(project_root, 'common', 'Workflow', workflow_filename)
            
            if os.path.exists(workflow_path):
                with open(workflow_path, 'r', encoding='utf-8') as f:
                    workflow = json.load(f)
                self.logger.info(f"已加载工作流文件: {workflow_filename}")
                return workflow
            else:
                self.logger.error(f"工作流文件不存在: {workflow_path}")
                return self._get_default_workflow()
                
        except Exception as e:
            self.logger.error(f"加载工作流配置失败: {e}")
            return self._get_default_workflow()
    
    def _get_default_workflow(self) -> dict:
        """获取默认的工作流配置（简化版，实际使用配置文件中的工作流）"""
        self.logger.warning("使用默认工作流配置，建议检查配置文件中的工作流设置")
        return {}
    
    def _update_workflow_parameters(self, workflow: dict, params: dict, workflow_type: str = 'image'):
        """动态更新工作流参数"""
        try:
            placeholder_found = False
            
            # 根据工作流类型确定占位符
            if workflow_type == 'image':
                placeholder = '%AutoMovieclip%'
            elif workflow_type == 'audio':
                placeholder = '%AutoMovieSound%'
            else:
                placeholder = '%AutoMovieclip%'  # 默认
            
            # 遍历工作流中的所有节点
            for node_id, node_data in workflow.items():
                if 'inputs' not in node_data:
                    continue
                    
                node_inputs = node_data['inputs']
                class_type = node_data.get('class_type', '')
                
                # 更新KSampler节点的seed参数
                if class_type == 'KSampler':
                    if 'seed' in node_inputs and 'seed' in params:
                        node_inputs['seed'] = params['seed']
                        self.logger.info(f"已更新KSampler节点的seed: {params['seed']}")
                
                # 查找并替换CLIP提示词占位符（图像工作流）
                elif class_type == 'CLIPTextEncode':
                    if 'text' in node_inputs:
                        current_text = node_inputs.get('text', '')
                        # 查找特殊标记
                        if placeholder in current_text and 'prompt_text' in params:
                            # 替换占位符为实际提示词
                            node_inputs['text'] = current_text.replace(placeholder, params['prompt_text'])
                            placeholder_found = True
                            self.logger.info(f"已在节点{node_id}中替换CLIP占位符: {params['prompt_text']}")
                
                # 查找并替换CLIPTextEncodeFlux节点的clip_l参数（图像工作流）
                elif class_type == 'CLIPTextEncodeFlux':
                    if 'clip_l' in node_inputs:
                        current_text = node_inputs.get('clip_l', '')
                        # 查找特殊标记
                        if placeholder in current_text and 'prompt_text' in params:
                            # 替换占位符为实际提示词
                            node_inputs['clip_l'] = current_text.replace(placeholder, params['prompt_text'])
                            placeholder_found = True
                            self.logger.info(f"已在节点{node_id}中替换CLIPTextEncodeFlux占位符: {params['prompt_text']}")
                
                # 查找并替换音频相关节点的文本参数（音频工作流）
                elif workflow_type == 'audio':
                    # 检查所有可能包含文本的输入参数
                    for input_key, input_value in node_inputs.items():
                        if isinstance(input_value, str) and placeholder in input_value:
                            # 支持多种文本参数名称
                            text_param = params.get('tts_text') or params.get('prompt_text')
                            if text_param:
                                node_inputs[input_key] = input_value.replace(placeholder, text_param)
                                placeholder_found = True
                                self.logger.info(f"已在节点{node_id}的{input_key}参数中替换音频占位符: {text_param}")
                    # 注意：不再处理seed参数，保留工作流自带的seed值
            
            # 检查是否找到了占位符
            text_param = params.get('tts_text') or params.get('prompt_text')
            if text_param and not placeholder_found:
                error_msg = f"工作流中未找到占位符'{placeholder}'，请检查工作流配置"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            self.logger.info("工作流参数已更新")
            
        except Exception as e:
            self.logger.error(f"更新工作流参数失败: {e}")
            raise
          
    def queue_prompt(self, prompt: dict) -> dict:
        """提交prompt到ComfyUI队列"""
        try:
            p = {"prompt": prompt, "client_id": self.client_id}
            data = json.dumps(p).encode('utf-8')
            req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
            response = urllib.request.urlopen(req)
            return json.loads(response.read())
        except Exception as e:
            self.logger.error(f"Failed to queue prompt: {e}")
            raise
    
    def get_images_from_websocket(self, prompt: dict) -> List[str]:
        """通过WebSocket监听生成进度，然后获取保存的图像文件路径"""
        try:
            # 连接WebSocket
            ws = websocket.WebSocket()
            ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
            
            # 提交prompt并获取prompt_id
            prompt_id = self.queue_prompt(prompt)['prompt_id']
            
            while True:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['prompt_id'] == prompt_id:
                            if data['node'] is None:
                                break  # 执行完成
            
            ws.close()
            
            # 获取生成的图像文件列表
            history_url = f"http://{self.server_address}/history/{prompt_id}"
            response = urllib.request.urlopen(history_url)
            history = json.loads(response.read())
            
            file_paths = []
            if prompt_id in history:
                outputs = history[prompt_id].get('outputs', {})
                self.logger.info(f"ComfyUI输出节点: {list(outputs.keys())}")
                for node_id, output in outputs.items():
                    self.logger.info(f"节点 {node_id} 输出内容: {list(output.keys())}")
                    # 处理图像输出
                    if 'images' in output:
                        for image_info in output['images']:
                            filename = image_info['filename']
                            subfolder = image_info.get('subfolder', '')
                            file_url = f"http://{self.server_address}/view?filename={filename}&subfolder={subfolder}"
                            file_paths.append(file_url)
                            self.logger.info(f"找到图像文件: {filename}")
                    # 处理音频输出
                    elif 'audio' in output:
                        for audio_info in output['audio']:
                            filename = audio_info['filename']
                            subfolder = audio_info.get('subfolder', '')
                            file_url = f"http://{self.server_address}/view?filename={filename}&subfolder={subfolder}"
                            file_paths.append(file_url)
                            self.logger.info(f"找到音频文件: {filename}")
                    # 处理其他可能的文件输出
                    else:
                        for key, value in output.items():
                            if isinstance(value, list):
                                for item in value:
                                    if isinstance(item, dict) and 'filename' in item:
                                        filename = item['filename']
                                        subfolder = item.get('subfolder', '')
                                        file_url = f"http://{self.server_address}/view?filename={filename}&subfolder={subfolder}"
                                        file_paths.append(file_url)
                                        self.logger.info(f"找到文件: {filename} (类型: {key})")
            
            self.logger.info(f"总共找到 {len(file_paths)} 个文件")
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Failed to get files from websocket: {e}")
            raise
    
    def save_images_to_disk(self, image_urls: List[str], 
                           output_dir: str, 
                           filename_prefix: str = "script",
                           workflow: dict = None) -> List[str]:
        """从URL下载图像并保存到磁盘"""
        try:
            # 创建输出目录
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            saved_files = []
            
            for i, image_url in enumerate(image_urls):
                try:
                    # 下载图像
                    response = urllib.request.urlopen(image_url)
                    image_data = response.read()
                    
                    # 转换为PIL图像
                    image = Image.open(io.BytesIO(image_data))
                    
                    # 生成文件名
                    filename = os.path.join(output_dir, f"{filename_prefix}.png")
                    
                    # 保存图像
                    image.save(filename)
                    saved_files.append(filename)
                    
                    # 保存对应的工作流JSON文件
                    if workflow:
                        base_name = os.path.splitext(os.path.basename(filename))[0]
                        json_filename = os.path.join(output_dir, f"{base_name}.json")
                        try:
                            with open(json_filename, 'w', encoding='utf-8') as f:
                                json.dump(workflow, f, ensure_ascii=False, indent=2)
                            self.logger.info(f"已保存工作流文件: {json_filename}")
                        except Exception as json_e:
                            self.logger.error(f"保存工作流文件失败: {json_e}")
                    
                    self.logger.info(f"已保存图像: {filename} (尺寸: {image.size})")
                    
                except Exception as e:
                    self.logger.error(f"保存图像 {i} 失败: {e}")
            
            return saved_files
            
        except Exception as e:
            self.logger.error(f"保存图像到磁盘失败: {e}")
            raise
    
    def _load_paper_data(self, project_path: str) -> dict:
        """从项目路径的parameter.ini加载文案数据（仅用于音频生成）"""
        try:
            # 只从parameter.ini加载文案数据，不读取paper.json
            parameter_path = os.path.join(project_path, 'parameter.ini')
            if os.path.exists(parameter_path):
                config = configparser.ConfigParser()
                config.read(parameter_path, encoding='utf-8')
                
                # 检查是否有PAPER_CONTENT节
                if config.has_section('PAPER_CONTENT'):
                    paper_data = {'sentences': []}
                    
                    # 读取所有line_N项
                    for key, value in config.items('PAPER_CONTENT'):
                        if key.startswith('line_'):
                            try:
                                line_num = int(key.split('_')[1])
                                paper_data['sentences'].append({
                                    'id': line_num,
                                    'text': value.strip()
                                })
                            except (ValueError, IndexError):
                                continue
                    
                    # 按ID排序
                    paper_data['sentences'].sort(key=lambda x: x['id'])
                    
                    self.logger.info(f"已从parameter.ini加载 {len(paper_data['sentences'])} 个句子用于音频生成: {parameter_path}")
                    return paper_data
                else:
                    self.logger.warning(f"parameter.ini中没有PAPER_CONTENT节: {parameter_path}")
                    return {}
            else:
                self.logger.error(f"parameter.ini文件不存在: {parameter_path}")
                return {}
            
        except Exception as e:
            self.logger.error(f"从parameter.ini加载文案数据失败: {e}")
            return {}
    
    def _build_prompt_from_paper(self, paper_data: dict, sentence_id: int) -> str:
        """根据paper.json数据构建提示词 - 自动识别所有可用键值"""
        try:
            prompt_parts = []
            
            # 定义需要跳过的键（这些不是描述性内容）
            skip_keys = {'title', 'script', 'id', 'text'}
            
            # 自动提取character_profile中的所有键值
            character_profile = paper_data.get('character_profile', {})
            for key, value in character_profile.items():
                if key not in skip_keys and value and str(value).strip():
                    prompt_parts.append(str(value).strip())
                    self.logger.debug(f"添加character_profile键值: {key} = {value}")
            
            # 自动提取image_prompts中的所有键值
            image_prompts = paper_data.get('image_prompts', {})
            for key, value in image_prompts.items():
                if key not in skip_keys and value and str(value).strip():
                    prompt_parts.append(str(value).strip())
                    self.logger.debug(f"添加image_prompts键值: {key} = {value}")
            
            # 查找对应的句子数据
            sentences = paper_data.get('sentences', [])
            sentence_data = None
            for sentence in sentences:
                if sentence.get('id') == sentence_id:
                    sentence_data = sentence
                    break
            
            # 自动提取句子数据中的所有键值（除了id和text）
            if sentence_data:
                for key, value in sentence_data.items():
                    if key not in skip_keys and value and str(value).strip():
                        prompt_parts.append(str(value).strip())
                        self.logger.debug(f"添加句子键值: {key} = {value}")
            
            # 组合提示词
            prompt = ', '.join(prompt_parts)
            
            # 如果没有提取到任何内容，使用默认提示词
            if not prompt.strip():
                prompt = "anthropomorphic animal, masterpiece, best quality"
                self.logger.warning("未找到有效的提示词内容，使用默认提示词")
            
            self.logger.info(f"为句子ID {sentence_id} 构建的提示词: {prompt}")
            return prompt
            
        except Exception as e:
            self.logger.error(f"构建提示词失败: {e}")
            return "anthropomorphic animal, masterpiece, best quality"
    
    def generate_image(self, project_path: str, sentence_id: int = 1, seed: Optional[int] = None) -> List[str]:
        """生成图像的便捷方法"""
        try:
            # 生成15位随机seed
            if seed is None:
                import random
                seed = random.randint(100000000000000, 999999999999999)
            
            self.logger.info(f"生成图像 - 项目路径: {project_path}, 句子ID: {sentence_id}, 种子: {seed}")
            
            # 加载paper.json数据
            paper_data = self._load_paper_data(project_path)
            if not paper_data:
                raise Exception("无法加载paper.json数据")
            
            # 构建提示词
            prompt_text = self._build_prompt_from_paper(paper_data, sentence_id)
            
            # 从配置文件加载工作流
            workflow = self._load_workflow_from_config('image')
            if not workflow:
                raise Exception("无法加载工作流配置")
            
            # 动态更新工作流参数
            self._update_workflow_parameters(workflow, {
                'prompt_text': prompt_text,
                'seed': seed
            }, 'image')
            
            # 通过WebSocket获取图像URL
            image_urls = self.get_images_from_websocket(workflow)
            
            # 保存图像到项目的images目录
            output_dir = os.path.join(project_path, 'images')
            filename_prefix = f"script_{sentence_id}"
            saved_files = self.save_images_to_disk(image_urls, output_dir, filename_prefix, workflow)
            
            self.logger.info(f"成功生成 {len(saved_files)} 张图像")
            return saved_files
            
        except Exception as e:
            self.logger.error(f"生成图像失败: {e}")
            raise
    
    def generate_audio(self, project_path: str, sentence_id: int = 1) -> List[str]:
        """生成音频的便捷方法"""
        try:
            self.logger.info(f"生成音频 - 项目路径: {project_path}, 句子ID: {sentence_id}")
            
            # 加载paper.json数据
            paper_data = self._load_paper_data(project_path)
            if not paper_data:
                raise Exception("无法加载paper.json数据")
            
            # 计算句子数量（支持多种格式）
            sentence_count = 0
            if 'scenes' in paper_data:
                sentence_count = len(paper_data.get('scenes', []))
                data_format = "scenes"
            elif 'story' in paper_data:
                sentence_count = len(paper_data.get('story', []))
                data_format = "story"
            elif 'sentences' in paper_data:
                sentence_count = len(paper_data.get('sentences', []))
                data_format = "sentences"
            else:
                data_format = "unknown"
            
            self.logger.info(f"已加载paper.json数据，包含 {sentence_count} 个句子（格式: {data_format}）")
            
            # 获取句子文本
            sentence_text = self._get_sentence_text(paper_data, sentence_id)
            self.logger.info(f"获取到句子文本: {sentence_text}")
            
            # 从配置文件加载工作流
            workflow = self._load_workflow_from_config('audio')
            if not workflow:
                raise Exception("无法加载音频工作流配置")
            self.logger.info(f"已加载音频工作流配置，包含 {len(workflow)} 个节点")
            
            # 动态更新工作流参数（只更新文本，保留工作流自带的seed）
            self._update_workflow_parameters(workflow, {
                'tts_text': sentence_text
            }, 'audio')
            self.logger.info("工作流参数更新完成")
            
            # 通过WebSocket获取音频URL
            self.logger.info("开始通过WebSocket获取音频URL")
            audio_urls = self._get_audios_via_websocket(workflow)
            self.logger.info(f"获取到 {len(audio_urls)} 个音频URL: {audio_urls}")
            
            # 保存音频到项目的audios目录
            self.logger.info("开始保存音频文件到磁盘")
            saved_files = self._save_audios_to_disk(audio_urls, project_path, sentence_id, workflow)
            
            self.logger.info(f"成功生成 {len(saved_files)} 个音频文件: {saved_files}")
            return saved_files
            
        except Exception as e:
            self.logger.error(f"生成音频失败: {e}")
            import traceback
            self.logger.error(f"详细错误信息: {traceback.format_exc()}")
            raise
    
    def _get_sentence_text(self, paper_data: dict, sentence_id: int) -> str:
        """从paper.json数据中获取指定句子的文本"""
        try:
            # 尝试从 scenes 数组中获取（最新格式）
            scenes = paper_data.get('scenes', [])
            for scene in scenes:
                if scene.get('id') == sentence_id:
                    text = scene.get('text', '')
                    if text:
                        self.logger.info(f"从scenes数组找到句子ID {sentence_id} 的文本: {text}")
                        return text
            
            # 尝试从 story 数组中获取（新格式）
            story = paper_data.get('story', [])
            for sentence in story:
                if sentence.get('id') == sentence_id:
                    text = sentence.get('text', '')
                    if text:
                        self.logger.info(f"从story数组找到句子ID {sentence_id} 的文本: {text}")
                        return text
            
            # 尝试从 sentences 数组中获取（旧格式）
            sentences = paper_data.get('sentences', [])
            for sentence in sentences:
                if sentence.get('id') == sentence_id:
                    text = sentence.get('text', '')
                    if text:
                        self.logger.info(f"从sentences数组找到句子ID {sentence_id} 的文本: {text}")
                        return text
            
            self.logger.warning(f"未找到句子ID {sentence_id} 的文本，使用默认文本")
            return "Hello, this is a test audio."
            
        except Exception as e:
            self.logger.error(f"获取句子文本失败: {e}")
            return "Hello, this is a test audio."
    
    def _get_audios_via_websocket(self, workflow: dict) -> list:
        """通过WebSocket获取音频URL（复用图像获取逻辑）"""
        return self.get_images_from_websocket(workflow)
    
    def _save_audios_to_disk(self, audio_urls: list, project_path: str, sentence_index: int, workflow: dict) -> list:
        """保存音频文件到磁盘"""
        try:
            # 创建audios目录
            audios_dir = os.path.join(project_path, 'audios')
            os.makedirs(audios_dir, exist_ok=True)
            
            saved_files = []
            
            for i, audio_url in enumerate(audio_urls):
                try:
                    # 下载音频文件
                    response = requests.get(audio_url, timeout=30)
                    response.raise_for_status()
                    
                    # 确定文件扩展名
                    content_type = response.headers.get('content-type', '')
                    if 'audio/wav' in content_type:
                        ext = '.wav'
                    elif 'audio/mp3' in content_type:
                        ext = '.mp3'
                    elif 'audio/flac' in content_type:
                        ext = '.flac'
                    else:
                        # 从URL推断扩展名
                        parsed_url = urlparse(audio_url)
                        filename = os.path.basename(parsed_url.path)
                        _, ext = os.path.splitext(filename)
                        if not ext:
                            ext = '.wav'  # 默认扩展名
                    
                    # 生成文件名
                    audio_filename = f"script_{sentence_index}_{i+1}{ext}"
                    audio_path = os.path.join(audios_dir, audio_filename)
                    
                    # 保存音频文件
                    with open(audio_path, 'wb') as f:
                        f.write(response.content)
                    
                    saved_files.append(audio_path)
                    self.logger.info(f"音频已保存: {audio_path}")
                    
                except Exception as e:
                    self.logger.error(f"保存音频文件失败 {audio_url}: {e}")
                    continue
            
            # 保存工作流JSON文件
            if saved_files:
                workflow_filename = f"script_{sentence_index}_workflow.json"
                workflow_path = os.path.join(audios_dir, workflow_filename)
                
                with open(workflow_path, 'w', encoding='utf-8') as f:
                    json.dump(workflow, f, ensure_ascii=False, indent=2)
                
                saved_files.append(workflow_path)
                self.logger.info(f"工作流已保存: {workflow_path}")
            
            return saved_files
            
        except Exception as e:
            self.logger.error(f"保存音频文件失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试与ComfyUI服务器的连接"""
        try:
            # 尝试访问ComfyUI的基本信息接口
            response = urllib.request.urlopen(f"http://{self.server_address}/system_stats")
            return response.getcode() == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = ComfyUIClient()
    
    # 测试连接
    if client.test_connection():
        print("Connected to ComfyUI successfully!")
        
        # 生成图像
        try:
            project_path = "e:\\Code\\AutoMovie\\projects\\test"
            sentence_id = 1
            saved_files = client.generate_image(
                project_path=project_path,
                sentence_id=sentence_id
            )
            print(f"Generated images: {saved_files}")
        except Exception as e:
            print(f"Error generating image: {e}")
    else:
        print("Failed to connect to ComfyUI server")