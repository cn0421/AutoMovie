#!/usr/bin/env python3
import urllib.request
import json
from common.comfyui_client import ComfyUIClient

def debug_comfyui():
    try:
        client = ComfyUIClient()
        print(f"ComfyUI地址: {client.server_address}")
        
        # 加载工作流
        workflow = client._load_workflow_from_config('image')
        print("工作流加载成功")
        
        # 更新参数
        client._update_workflow_parameters(workflow, {
            'prompt_text': '测试提示词',
            'seed': 123456
        }, 'image')
        print("参数更新成功")
        
        # 准备请求数据
        data = json.dumps({
            'prompt': workflow,
            'client_id': client.client_id
        }).encode('utf-8')
        
        # 发送请求
        req = urllib.request.Request(f"http://{client.server_address}/prompt", data=data)
        req.add_header('Content-Type', 'application/json')
        
        try:
            response = urllib.request.urlopen(req)
            result = response.read().decode()
            print("成功:", result)
        except urllib.error.HTTPError as e:
            error_detail = e.read().decode()
            print(f"HTTP错误 {e.code}: {e.reason}")
            print("错误详情:", error_detail)
            
    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_comfyui()