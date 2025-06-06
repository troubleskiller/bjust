#!/usr/bin/env python3
"""
测试tif_path功能的简单脚本
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://localhost:9001"

def get_first_typical_scenario_uuid():
    """获取第一个可用的典型场景UUID"""
    print("正在获取典型场景列表...")
    
    try:
        url = BASE_URL + "/api/v1/typical_scenarios"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            scenarios = result.get('data', {}).get('scenarios', [])
            
            for scenario in scenarios:
                if scenario.get('type') == 'directory_with_metadata' and scenario.get('uuid'):
                    scenario_uuid = scenario.get('uuid')
                    scenario_name = scenario.get('name', '未知场景')
                    print(f"✅ 找到典型场景: {scenario_name} (UUID: {scenario_uuid})")
                    return scenario_uuid, scenario_name
            
            print("❌ 未找到带有元数据的典型场景")
            return None, None
        else:
            print(f"❌ 获取典型场景列表失败: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ 获取典型场景列表异常: {str(e)}")
        return None, None

def test_typical_scenario_task():
    """测试典型场景任务创建"""
    print("\n" + "="*60)
    print("🧪 测试典型场景tif_path功能")
    print("="*60)
    
    # 获取典型场景
    scenario_uuid, scenario_name = get_first_typical_scenario_uuid()
    if not scenario_uuid:
        print("无法获取典型场景，测试终止")
        return False
    
    # 创建典型场景任务
    request_data = {
        "model_uuid": "MODEL-663477c0242d4fc89bbfa0fc43e96527",
        "prediction_mode": "link",
        "scenario_type": "typical_scenario",
        "point_config": {
            "scenario_uuid": scenario_uuid
        },
        "param_config": {
            "frequency_band": "5.9GHz",
            "modulation_mode": "QPSK",
            "modulation_order": 4
        }
    }
    
    print(f"\n🚀 创建典型场景任务...")
    print(f"使用场景: {scenario_name}")
    print(f"场景UUID: {scenario_uuid}")
    
    try:
        url = BASE_URL + "/api/v1/online_deduction/tasks"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=request_data, headers=headers, timeout=30)
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            task_uuid = data.get('task_uuid')
            status = data.get('status')
            message = data.get('message')
            task_folder_path = data.get('task_folder_path')
            scenario_info = data.get('scenario_info', {})
            
            print(f"\n✅ 任务创建成功!")
            print(f"任务UUID: {task_uuid}")
            print(f"任务状态: {status}")
            print(f"任务文件夹: {task_folder_path}")
            
            # 显示场景信息
            tif_image_name = scenario_info.get('tif_image_name')
            if tif_image_name:
                print(f"\n🗺️  TIF信息:")
                print(f"  TIF图像名称: {tif_image_name}")
                print(f"  TIF目录路径: /storage/tif/{tif_image_name}")
                print(f"  📌 注意: 不复制tif文件，直接传递tif目录路径给main.py")
                
            print(f"\n📋 完整场景信息:")
            print(json.dumps(scenario_info, indent=2, ensure_ascii=False))
            
            return True
        else:
            print("❌ 任务创建失败")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🧪 TIF_PATH功能测试")
    
    success = test_typical_scenario_task()
    
    if success:
        print("\n🎉 测试完成!")
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main() 