#!/usr/bin/env python3
"""
测试典型场景管理API接口
"""

import requests
import json
import sys
import os
import tempfile
import csv

# API基础URL（根据实际情况修改）
BASE_URL = "http://localhost:9001"

def create_test_input_file():
    """创建一个测试用的input CSV文件"""
    temp_dir = tempfile.mkdtemp()
    test_file_path = os.path.join(temp_dir, "test_input.csv")
    
    # 创建CSV内容
    csv_data = [
        [39.9200, 116.4200, 30.0, 39.9195, 116.4195, 1.5],
        [39.9200, 116.4200, 30.0, 39.9205, 116.4205, 1.5],
        [39.9200, 116.4200, 30.0, 39.9210, 116.4210, 1.5],
        [39.9250, 116.4250, 25.0, 39.9245, 116.4245, 1.5],
        [39.9250, 116.4250, 25.0, 39.9255, 116.4255, 1.5]
    ]
    
    with open(test_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(csv_data)
    
    return test_file_path, temp_dir

def cleanup_test_file(file_path, temp_dir):
    """清理测试文件"""
    try:
        os.remove(file_path)
        os.rmdir(temp_dir)
    except:
        pass

def test_get_prediction_types():
    """测试获取预测类型列表"""
    print("测试获取预测类型列表...")
    
    try:
        url = BASE_URL + "/api/v1/typical_scenarios/prediction_types"
        response = requests.get(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            prediction_types = result.get('data', [])
            print("✅ 获取预测类型列表测试成功")
            print(f"可用预测类型: {prediction_types}")
            return True, prediction_types[0] if prediction_types else "单点预测"
        else:
            print("❌ 获取预测类型列表测试失败")
            return False, "单点预测"
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取预测类型列表测试异常: {str(e)}")
        return False, "单点预测"
    except Exception as e:
        print(f"❌ 获取预测类型列表测试出错: {str(e)}")
        return False, "单点预测"

def test_add_typical_scenario(prediction_type):
    """测试添加典型场景"""
    print("测试添加典型场景...")
    
    # 创建测试input文件
    test_file_path, temp_dir = create_test_input_file()
    
    try:
        url = BASE_URL + "/api/v1/typical_scenarios"
        
        # 准备表单数据
        data = {
            'scenario_name': '测试场景_工厂园区',
            'prediction_type': prediction_type,
            'tif_image_name': 'nanjing'
        }
        
        # 准备文件数据
        with open(test_file_path, 'rb') as f:
            files = {'input_file': ('test_input.csv', f, 'text/csv')}
            
            print(f"请求URL: {url}")
            print(f"请求数据: {data}")
            print(f"上传文件: {test_file_path}")
            
            response = requests.post(url, data=data, files=files, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 添加典型场景测试成功")
            data = result.get('data', {})
            print(f"场景名称: {data.get('scenario_name', 'N/A')}")
            print(f"预测类型: {data.get('prediction_type', 'N/A')}")
            print(f"场景UUID: {data.get('scenario_uuid', 'N/A')}")
            print(f"文件夹名称: {data.get('folder_name', 'N/A')}")
            print(f"场景目录: {data.get('scenario_directory', 'N/A')}")
            return True, data.get('folder_name')  # 返回文件夹名称
        else:
            print("❌ 添加典型场景测试失败")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 添加典型场景测试异常: {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ 添加典型场景测试出错: {str(e)}")
        return False, None
    finally:
        cleanup_test_file(test_file_path, temp_dir)

def test_list_typical_scenarios():
    """测试获取典型场景列表"""
    print("测试获取典型场景列表...")
    
    try:
        url = BASE_URL + "/api/v1/typical_scenarios"
        response = requests.get(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            scenarios = data.get('scenarios', [])
            scenarios_by_type = data.get('scenarios_by_type', {})
            print("✅ 获取典型场景列表测试成功")
            print(f"场景总数: {len(scenarios)}")
            print("按类型分组:")
            for pred_type, type_scenarios in scenarios_by_type.items():
                print(f"  {pred_type}: {len(type_scenarios)}个场景")
                for scenario in type_scenarios:
                    print(f"    - {scenario.get('name')} ({scenario.get('folder_name')})")
            return True
        else:
            print("❌ 获取典型场景列表测试失败")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取典型场景列表测试异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 获取典型场景列表测试出错: {str(e)}")
        return False

def test_get_typical_scenario_info(scenario_identifier):
    """测试获取典型场景详细信息"""
    print(f"测试获取典型场景详细信息: {scenario_identifier}...")
    
    try:
        url = BASE_URL + f"/api/v1/typical_scenarios/{scenario_identifier}"
        response = requests.get(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取典型场景详细信息测试成功")
            data = result.get('data', {})
            print(f"场景名称: {data.get('scenario_name')}")
            print(f"预测类型: {data.get('prediction_type')}")
            print(f"场景UUID: {data.get('scenario_uuid')}")
            print(f"文件夹名称: {data.get('folder_name')}")
            print(f"TIF图像: {data.get('tif_image_name')}")
            print(f"创建时间: {data.get('created_at')}")
            files = data.get('files', [])
            print(f"包含文件: {len(files)}个")
            for file_info in files:
                print(f"  - {file_info.get('name')} ({file_info.get('size')} bytes)")
            return True
        else:
            print("❌ 获取典型场景详细信息测试失败")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 获取典型场景详细信息测试异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 获取典型场景详细信息测试出错: {str(e)}")
        return False

def test_delete_typical_scenario(scenario_identifier):
    """测试删除典型场景"""
    print(f"测试删除典型场景: {scenario_identifier}...")
    
    try:
        url = BASE_URL + f"/api/v1/typical_scenarios/{scenario_identifier}"
        response = requests.delete(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 删除典型场景测试成功")
            data = result.get('data', {})
            print(f"已删除场景: {data.get('scenario_name')} ({data.get('prediction_type')}) - {data.get('folder_name')}")
            return True
        else:
            print("❌ 删除典型场景测试失败")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 删除典型场景测试异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 删除典型场景测试出错: {str(e)}")
        return False

def test_list_typical_scenarios_by_type(prediction_type):
    """测试按预测类型获取典型场景列表"""
    print(f"测试按预测类型获取典型场景列表: {prediction_type}...")
    
    try:
        url = BASE_URL + f"/api/v1/typical_scenarios?prediction_type={prediction_type}"
        response = requests.get(url, timeout=10)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            scenarios = data.get('scenarios', [])
            returned_type = data.get('prediction_type')
            type_code = data.get('prediction_type_code')
            print("✅ 按预测类型获取典型场景列表测试成功")
            print(f"请求类型: {prediction_type}")
            print(f"返回类型: {returned_type}")
            print(f"类型代码: {type_code}")
            print(f"场景数量: {len(scenarios)}")
            for scenario in scenarios:
                print(f"  - {scenario.get('name')} ({scenario.get('folder_name')})")
            return True
        else:
            print("❌ 按预测类型获取典型场景列表测试失败")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 按预测类型获取典型场景列表测试异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 按预测类型获取典型场景列表测试出错: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("典型场景管理API测试")
    print("=" * 60)
    
    results = []
    test_scenario_identifier = None
    test_prediction_type = "单点预测"
    
    # 1. 测试获取预测类型列表
    success, prediction_type = test_get_prediction_types()
    results.append(success)
    if success:
        test_prediction_type = prediction_type
    print()
    
    # 2. 测试添加典型场景
    success, scenario_identifier = test_add_typical_scenario(test_prediction_type)
    results.append(success)
    if success:
        test_scenario_identifier = scenario_identifier
    print()
    
    # 3. 测试获取典型场景列表
    results.append(test_list_typical_scenarios())
    print()
    
    # 4. 测试按预测类型获取典型场景列表
    results.append(test_list_typical_scenarios_by_type(test_prediction_type))
    print()
    
    # 5. 测试获取典型场景详细信息
    if test_scenario_identifier:
        results.append(test_get_typical_scenario_info(test_scenario_identifier))
        print()
    
    # # 6. 测试删除典型场景
    # if test_scenario_identifier:
    #     results.append(test_delete_typical_scenario(test_scenario_identifier))
    #     print()
    
    # 总结测试结果
    print("=" * 60)
    print("测试结果总结:")
    print(f"成功: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("⚠️  部分测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 