#!/usr/bin/env python3
"""
完整的在线推演功能测试脚本
包括：创建任务、查询状态、获取结果、停止任务
"""

import requests
import json
import sys
import time

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

def create_prediction_task(scenario_uuid=None):
    """创建预测任务"""
    print("\n" + "="*60)
    print("🚀 创建在线推演预测任务")
    print("="*60)
    
    if scenario_uuid:
        # 使用典型场景
        request_data = {
            "model_uuid": "uuid-model-001",
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
        print("使用典型场景创建任务")
    else:
        # 使用手动选点
        request_data = {
            "model_uuid": "uuid-model-001",
            "prediction_mode": "link",
            "scenario_type": "manual_selection",
            "point_config": {
                "scenario_description": "测试场景 - 城市环境信号预测",
                "tx_pos_list": [
                    {"lat": 39.9200, "lon": 116.4200, "height": 30.0}
                ],
                "rx_pos_list": [
                    {"lat": 39.9195, "lon": 116.4195, "height": 1.5},
                    {"lat": 39.9205, "lon": 116.4205, "height": 1.5}
                ]
            },
            "param_config": {
                "frequency_band": "5.9GHz",
                "modulation_mode": "QPSK", 
                "modulation_order": 4
            }
        }
        print("使用手动选点创建任务")
    
    print("请求数据:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        url = BASE_URL + "/api/v1/online_deduction/tasks"
        headers = {'Content-Type': 'application/json'}
        
        print(f"\n发送POST请求到: {url}")
        response = requests.post(url, json=request_data, headers=headers, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            data = result.get('data', {})
            task_uuid = data.get('task_uuid')
            status = data.get('status')
            message = data.get('message')
            
            print(f"\n✅ 任务创建成功!")
            print(f"任务UUID: {task_uuid}")
            print(f"任务状态: {status}")
            print(f"状态描述: {message}")
            
            # 显示任务文件夹信息
            task_folder_name = data.get('task_folder_name')
            task_folder_path = data.get('task_folder_path')
            if task_folder_name:
                print(f"任务文件夹: {task_folder_name}")
            if task_folder_path:
                print(f"文件夹路径: {task_folder_path}")
            
            # 如果是典型场景，显示CSV内容
            if request_data['scenario_type'] == 'typical_scenario':
                csv_content = data.get('scenario_csv_content')
                scenario_info = data.get('scenario_info')
                if csv_content:
                    print(f"\n📄 典型场景CSV内容预览:")
                    lines = csv_content.split('\n')[:3]
                    for i, line in enumerate(lines):
                        if line.strip():
                            print(f"  {line}")
                    if len(lines) > 3:
                        print("  ...")
                
                if scenario_info:
                    print(f"\n🏷️  场景信息:")
                    print(f"  场景名称: {scenario_info.get('scenario_name', 'N/A')}")
                    print(f"  预测类型: {scenario_info.get('prediction_type', 'N/A')}")
                    print(f"  TIF图像: {scenario_info.get('tif_image_name', 'N/A')}")
                    print(f"  创建时间: {scenario_info.get('created_at', 'N/A')}")
            
            return task_uuid
        else:
            print("响应内容:")
            print(json.dumps(response.json() if response.headers.get('content-type', '').startswith('application/json') 
                           else response.text, indent=2, ensure_ascii=False))
            print(f"\n❌ 任务创建失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

def get_task_status(task_uuid):
    """获取任务状态"""
    print(f"\n📊 查询任务状态: {task_uuid}")
    print("-" * 40)
    
    try:
        url = BASE_URL + f"/api/v1/online_deduction/tasks/{task_uuid}/status"
        response = requests.get(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            status = data.get('status')
            message = data.get('message')
            created_at = data.get('created_at')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            
            print(f"✅ 任务状态: {status}")
            print(f"状态描述: {message}")
            print(f"创建时间: {created_at}")
            print(f"开始时间: {start_time}")
            print(f"结束时间: {end_time}")
            
            # 显示进程状态（如果有）
            process_status = data.get('process_status')
            if process_status:
                print(f"进程状态: {process_status.get('status', 'N/A')}")
                print(f"进程ID: {process_status.get('pid', 'N/A')}")
            
            return status
        else:
            print(f"❌ 查询状态失败: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ 查询异常: {str(e)}")
        return None

def get_task_result(task_uuid):
    """获取任务结果"""
    print(f"\n📄 获取任务结果: {task_uuid}")
    print("-" * 40)
    
    try:
        url = BASE_URL + f"/api/v1/online_deduction/tasks/{task_uuid}/result"
        response = requests.get(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            status = data.get('status')
            message = data.get('message')
            csv_content = data.get('result_csv_content')
            completed_at = data.get('completed_at')
            
            print(f"✅ 任务状态: {status}")
            print(f"状态描述: {message}")
            
            if status == 'COMPLETED' and csv_content:
                print(f"完成时间: {completed_at}")
                print(f"\n📊 输出CSV结果:")
                print("=" * 50)
                # 显示CSV内容的前几行
                lines = csv_content.split('\n')
                for i, line in enumerate(lines[:10]):  # 显示前10行
                    if line.strip():
                        print(f"{i+1:2d}: {line}")
                if len(lines) > 10:
                    print(f"... (共 {len(lines)} 行)")
                print("=" * 50)
                print(f"CSV内容总长度: {len(csv_content)} 字符")
                return csv_content
            elif status == 'IN_PROGRESS':
                started_at = data.get('started_at')
                print(f"开始时间: {started_at}")
                print("⏳ 任务仍在进行中...")
            else:
                print("📋 任务未完成或无结果")
            
            return None
        else:
            print(f"❌ 获取结果失败: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ 获取异常: {str(e)}")
        return None

def stop_task(task_uuid):
    """停止任务"""
    print(f"\n🛑 停止任务: {task_uuid}")
    print("-" * 40)
    
    try:
        url = BASE_URL + f"/api/v1/online_deduction/tasks/{task_uuid}/stop"
        response = requests.post(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            status = data.get('status')
            message = data.get('message')
            
            print(f"✅ 停止成功")
            print(f"任务状态: {status}")
            print(f"状态描述: {message}")
            return True
        else:
            print(f"❌ 停止失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 停止异常: {str(e)}")
        return False

def monitor_task_progress(task_uuid, max_wait_time=60):
    """监控任务进度"""
    print(f"\n⏱️  监控任务进度 (最大等待 {max_wait_time} 秒)")
    print("=" * 60)
    
    start_time = time.time()
    check_count = 0
    
    while time.time() - start_time < max_wait_time:
        check_count += 1
        print(f"\n第 {check_count} 次检查...")
        
        status = get_task_status(task_uuid)
        
        if status == 'COMPLETED':
            print("🎉 任务已完成!")
            return True
        elif status == 'ABORTED':
            print("❌ 任务已中止!")
            return False
        elif status == 'IN_PROGRESS':
            print("⏳ 任务进行中，等待5秒后再次检查...")
            time.sleep(5)
        else:
            print(f"❓ 未知状态: {status}")
            time.sleep(2)
    
    print(f"\n⏰ 监控超时 ({max_wait_time} 秒)")
    return False

def main():
    """主测试函数"""
    print("🧪 在线推演完整功能测试")
    print("=" * 60)
    
    # 1. 获取典型场景UUID（可选）
    scenario_uuid, scenario_name = get_first_typical_scenario_uuid()
    
    # 2. 创建预测任务
    task_uuid = create_prediction_task(scenario_uuid)
    
    if not task_uuid:
        print("\n❌ 任务创建失败，测试终止")
        sys.exit(1)
    
    # 3. 立即查询一次状态
    initial_status = get_task_status(task_uuid)
    
    # 4. 监控任务进度
    if initial_status == 'IN_PROGRESS':
        print("\n📈 任务正在运行，开始监控进度...")
        task_completed = monitor_task_progress(task_uuid, max_wait_time=30)
        
        if task_completed:
            # 5. 获取最终结果
            csv_result = get_task_result(task_uuid)
            if csv_result:
                print(f"\n🎊 测试完成! 获得 {len(csv_result)} 字符的CSV结果")
            else:
                print("\n⚠️  任务完成但未获取到结果")
        else:
            # 6. 演示停止任务功能
            print("\n⏹️  演示停止任务功能...")
            stop_success = stop_task(task_uuid)
            if stop_success:
                print("✅ 任务停止功能测试成功")
            
            # 查看停止后的状态
            get_task_status(task_uuid)
    else:
        # 任务可能已经完成或失败
        csv_result = get_task_result(task_uuid)
        if csv_result:
            print(f"\n🎊 任务已完成! 获得 {len(csv_result)} 字符的CSV结果")
    
    print("\n" + "=" * 60)
    print("🏁 在线推演功能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main() 