#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV生成功能测试脚本
演示如何将发射机-接收机位置信息保存为CSV文件
"""

import csv
import os
import uuid
from typing import Dict, Any, List, Tuple, Optional

def generate_tx_rx_pairs_csv_demo(point_config: Dict[str, Any], task_uuid: str) -> Tuple[Optional[str], Optional[str]]:
    """
    演示版本的CSV生成函数
    """
    try:
        # 获取发射机和接收机位置列表
        tx_pos_list = point_config.get('tx_pos_list', [])
        rx_pos_list = point_config.get('rx_pos_list', [])
        
        if not tx_pos_list or not rx_pos_list:
            return None, "tx_pos_list and rx_pos_list are required"
        
        # 创建CSV文件目录
        csv_dir = 'demo_output'
        os.makedirs(csv_dir, exist_ok=True)
        
        # 生成CSV文件路径
        csv_filename = f"{task_uuid}_tx_rx_pairs.csv"
        csv_file_path = os.path.join(csv_dir, csv_filename)
        
        # 写入CSV文件
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # 写入标题行
            csv_writer.writerow([
                '接收机纬度', '接收机经度', '接收机高度', 
                '发射机纬度', '发射机经度', '发射机高度'
            ])
            
            # 生成所有发射机-接收机配对
            for tx_pos in tx_pos_list:
                for rx_pos in rx_pos_list:
                    row = [
                        rx_pos.get('lat', 0),      # 接收机纬度
                        rx_pos.get('lon', 0),      # 接收机经度  
                        rx_pos.get('height', 0),   # 接收机高度
                        tx_pos.get('lat', 0),      # 发射机纬度
                        tx_pos.get('lon', 0),      # 发射机经度
                        tx_pos.get('height', 0)    # 发射机高度
                    ]
                    csv_writer.writerow(row)
        
        print(f"✅ 成功生成CSV文件: {csv_file_path}")
        return csv_file_path, None
        
    except Exception as e:
        print(f"❌ 生成CSV文件时出错: {str(e)}")
        return None, f"Failed to generate CSV file: {str(e)}"

def main():
    """
    主测试函数
    """
    print("📊 开始测试CSV生成功能")
    print("-" * 50)
    
    # 模拟用户提供的数据
    test_point_config = {
        "tx_pos_list": [
            {"lat": 39.915, "lon": 116.404, "height": 30.0}
        ],
        "rx_pos_list": [
            {"lat": 39.916, "lon": 116.405, "height": 1.5},
            {"lat": 39.917, "lon": 116.406, "height": 1.5},
            {"lat": 39.918, "lon": 116.407, "height": 1.5}
        ]
    }
    
    # 生成测试任务UUID
    test_task_uuid = f"demo-task-{str(uuid.uuid4())[:8]}"
    
    print("📍 输入数据:")
    print(f"   发射机数量: {len(test_point_config['tx_pos_list'])}")
    print(f"   接收机数量: {len(test_point_config['rx_pos_list'])}")
    print(f"   任务UUID: {test_task_uuid}")
    print()
    
    # 调用CSV生成函数
    csv_file_path, error = generate_tx_rx_pairs_csv_demo(test_point_config, test_task_uuid)
    
    if error:
        print(f"❌ 生成失败: {error}")
        return
    
    # 读取并显示生成的CSV内容
    print("📋 生成的CSV内容:")
    print("-" * 30)
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for i, row in enumerate(csv_reader):
                if i == 0:
                    # 标题行
                    print("   " + " | ".join(row))
                    print("   " + "-" * (len(" | ".join(row))))
                else:
                    # 数据行
                    print(f"   {' | '.join(map(str, row))}")
    
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {e}")
        return
    
    print()
    print(f"✅ 测试完成！文件已保存到: {csv_file_path}")
    
    # 计算总配对数
    total_pairs = len(test_point_config['tx_pos_list']) * len(test_point_config['rx_pos_list'])
    print(f"📊 总共生成 {total_pairs} 个发射机-接收机配对")

if __name__ == "__main__":
    main() 