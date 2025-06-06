#!/usr/bin/env python3
"""
测试场景选择功能的API接口
"""

import requests
import json
import sys

# API基础URL（根据实际情况修改）
BASE_URL = "http://localhost:9001"

def test_get_typical_scenarios():
    """测试获取典型场景列表"""
    print("测试获取典型场景列表...")
    
    try:
        url = BASE_URL + "/api/v1/online_deduction/typical_scenarios"
        response = requests.get(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            scenarios = result.get('data', [])
            print(f"✅ 获取典型场景列表成功")
            print(f"可用场景: {scenarios}")
            return True
        else:
            print(f"❌ 获取典型场景列表失败")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取典型场景列表异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 获取典型场景列表出错: {str(e)}")
        return False

def test_manual_selection_scenario():
    """测试自主选点场景"""
    print("测试自主选点场景...")
    
    data = {
        "model_uuid": "uuid-model-001",
        "prediction_mode": "link",
        "scenario_type": "manual_selection",
        "point_config": {
            "scenario_description": "北京CBD商业区5G信号覆盖预测",
            "tx_pos_list": [
                {"lat": 39.9160, "lon": 116.4050, "height": 30.0}
            ],
            "rx_pos_list": [
                {"lat": 39.9150, "lon": 116.4040, "height": 1.5},
                {"lat": 39.9170, "lon": 116.4060, "height": 1.5}
            ]
        },
        "param_config": {
            "frequency_band": "3.5GHz"
        }
    }
    
    return test_api_call("/api/v1/online_deduction/tasks", data, "自主选点")

def test_typical_scenario():
    """测试典型场景"""
    print("测试典型场景...")
    
    data = {
        "model_uuid": "uuid-model-002", 
        "prediction_mode": "point",
        "scenario_type": "typical_scenario",
        "point_config": {
            "scenario_name": "城市商业区"
        },
        "param_config": {
            "frequency_band": "2.4GHz"
        }
    }
    
    return test_api_call("/api/v1/online_deduction/tasks", data, "典型场景")

def test_custom_upload_scenario():
    """测试自定义上传场景"""
    print("测试自定义上传场景...")
    
    data = {
        "model_uuid": "uuid-model-003",
        "prediction_mode": "situation", 
        "scenario_type": "custom_upload",
        "point_config": {
            "scenario_description": "用户自定义的工厂厂区WiFi覆盖场景",
            "tx_pos_list": [
                {"lat": 39.9100, "lon": 116.4000, "height": 5.0},
                {"lat": 39.9120, "lon": 116.4020, "height": 5.0}
            ],
            "area_bounds": {
                "min_lat": 39.9090,
                "min_lon": 116.3990,
                "max_lat": 39.9130,
                "max_lon": 116.4030
            },
            "resolution_m": 1.0
        },
        "param_config": {
            "frequency_band": "5GHz"
        }
    }
    
    return test_api_call("/api/v1/online_deduction/tasks", data, "自定义上传")

def test_api_call(endpoint, data, scenario_name):
    """执行API调用测试"""
    try:
        url = BASE_URL + endpoint
        headers = {'Content-Type': 'application/json'}
        
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {scenario_name}场景测试成功")
            task_data = result.get('data', {})
            print(f"任务UUID: {task_data.get('task_uuid', 'N/A')}")
            
            # 如果是典型场景，检查是否返回了CSV内容
            if data.get('scenario_type') == 'typical_scenario':
                csv_content = task_data.get('scenario_csv_content')
                scenario_info = task_data.get('scenario_info', {})
                if csv_content:
                    print(f"典型场景CSV内容长度: {len(csv_content)} 字符")
                    print(f"CSV内容预览: {csv_content[:100]}..." if len(csv_content) > 100 else f"CSV内容: {csv_content}")
                    print(f"场景名称: {scenario_info.get('scenario_name', 'N/A')}")
                    print(f"预测类型: {scenario_info.get('prediction_type', 'N/A')}")
                    print(f"TIF图像: {scenario_info.get('tif_image_name', 'N/A')}")
                else:
                    print("⚠️  典型场景未返回CSV内容")
            
            return True
        else:
            print(f"❌ {scenario_name}场景测试失败")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {scenario_name}场景测试异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ {scenario_name}场景测试出错: {str(e)}")
        return False
    
    print("-" * 50)

def test_create_prediction_task(scenario_name, test_data):
    """测试创建预测任务"""
    print(f"测试{scenario_name}场景的预测任务创建...")
    
    try:
        url = BASE_URL + "/api/v1/online_deduction/tasks"
        headers = {'Content-Type': 'application/json'}
        
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {scenario_name}场景测试成功")
            task_data = result.get('data', {})
            print(f"任务UUID: {task_data.get('task_uuid', 'N/A')}")
            
            # 如果是典型场景，检查是否返回了CSV内容
            if test_data.get('scenario_type') == 'typical_scenario':
                csv_content = task_data.get('scenario_csv_content')
                scenario_info = task_data.get('scenario_info', {})
                if csv_content:
                    print(f"典型场景CSV内容长度: {len(csv_content)} 字符")
                    print(f"CSV内容预览: {csv_content[:100]}..." if len(csv_content) > 100 else f"CSV内容: {csv_content}")
                    print(f"场景名称: {scenario_info.get('scenario_name', 'N/A')}")
                    print(f"预测类型: {scenario_info.get('prediction_type', 'N/A')}")
                    print(f"TIF图像: {scenario_info.get('tif_image_name', 'N/A')}")
                else:
                    print("⚠️  典型场景未返回CSV内容")
            
            return True
        else:
            print(f"❌ {scenario_name}场景测试失败")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {scenario_name}场景测试异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ {scenario_name}场景测试出错: {str(e)}")
        return False
    finally:
        print("-" * 50)

def test_scenario_api():
    """测试场景API"""
    print("=" * 60)
    print("场景API测试")
    print("=" * 60)
    
    results = []
    scenario_uuid = None
    
    # 首先尝试获取一个典型场景的UUID
    print("获取典型场景信息...")
    try:
        list_url = BASE_URL + "/api/v1/typical_scenarios"
        list_response = requests.get(list_url, timeout=10)
        if list_response.status_code == 200:
            list_result = list_response.json()
            scenarios = list_result.get('data', {}).get('scenarios', [])
            if scenarios:
                # 查找带有元数据的典型场景
                for scenario in scenarios:
                    if scenario.get('type') == 'directory_with_metadata' and scenario.get('uuid'):
                        scenario_uuid = scenario.get('uuid')
                        print(f"找到典型场景: {scenario.get('name')} (UUID: {scenario_uuid})")
                        break
        
        if not scenario_uuid:
            print("未找到典型场景，使用默认UUID进行测试")
            scenario_uuid = "default-test-uuid"
    except Exception as e:
        print(f"获取典型场景信息失败: {e}")
        scenario_uuid = "default-test-uuid"
    
    # 1. 测试自主选点
    test_data = {
        "task_name": "北京市朝阳区信号覆盖预测",
        "task_type": "single_point_prediction",
        "scenario_type": "manual_selection",
        "point_config": {
            "scenario_description": "北京朝阳区商业中心区域的信号覆盖预测分析",
            "tx_pos_list": [
                {"lat": 39.9200, "lon": 116.4200, "height": 30.0},
                {"lat": 39.9250, "lon": 116.4250, "height": 25.0}
            ],
            "rx_pos_list": [
                {"lat": 39.9195, "lon": 116.4195, "height": 1.5},
                {"lat": 39.9205, "lon": 116.4205, "height": 1.5},
                {"lat": 39.9210, "lon": 116.4210, "height": 1.5},
                {"lat": 39.9245, "lon": 116.4245, "height": 1.5},
                {"lat": 39.9255, "lon": 116.4255, "height": 1.5}
            ],
            "area_bounds": {
                "min_lat": 39.9100,
                "min_lon": 116.4100,
                "max_lat": 39.9300,
                "max_lon": 116.4300
            },
            "resolution_m": 50.0
        },
        "tif_image_name": "nanjing",
        "model_params": {
            "frequency": 1800,
            "power": 40,
            "antenna_height": 30
        }
    }
    results.append(test_create_prediction_task("自主选点", test_data))
    
    # 2. 测试典型场景
    test_data = {
        "task_name": "典型场景_城市商业区预测",
        "task_type": "single_point_prediction",
        "scenario_type": "typical_scenario",
        "point_config": {
            "scenario_uuid": scenario_uuid
        },
        "tif_image_name": "nanjing",
        "model_params": {
            "frequency": 1800,
            "power": 40,
            "antenna_height": 30
        }
    }
    results.append(test_create_prediction_task("典型场景", test_data))
    
    # 3. 测试自定义上传
    test_data = {
        "task_name": "自定义场景_工业园区预测",
        "task_type": "single_point_prediction",
        "scenario_type": "custom_upload",
        "point_config": {
            "scenario_description": "工业园区特殊环境下的信号传播预测"
        },
        "tif_image_name": "nanjing",
        "model_params": {
            "frequency": 1800,
            "power": 40,
            "antenna_height": 30
        }
    }
    results.append(test_create_prediction_task("自定义上传", test_data))
    
    # 总结测试结果
    print("=" * 60)
    print("测试结果总结:")
    print(f"成功: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("场景选择功能API测试（更新版）")
    print("=" * 60)
    
    # 使用新的测试API
    success = test_scenario_api()
    
    if success:
        print("\n🎉 所有场景选择功能测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 