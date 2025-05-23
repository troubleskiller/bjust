"""
添加模拟数据到数据库的脚本
"""
from app import create_app, db
from app.model.homepage_models import BestPracticeCase
from datetime import datetime

def add_sample_data():
    """添加模拟数据到BestPracticeCase表"""
    
    # 创建应用实例并推入上下文
    app = create_app()
    with app.app_context():
        
        # 确保数据库表已创建
        db.create_all()
        
        # 定义模拟数据
        sample_cases = [
            {
                "case_dir_name": "highway_5g_scenario",
                "case_img_path": "/storage/best_cases/highway_5g_scenario/thumbnail.jpg",
                "case_type": "real_data",
                "case_title": "高速公路5G通信场景信道建模",
                "model_name": "Plana3.0,RayTracerX",
                "model_type_name": "态势感知模型,大尺度模型",
                "create_date_str": "2023-05-15"
            },
            {
                "case_dir_name": "urban_mmwave_analysis", 
                "case_img_path": "/storage/best_cases/urban_mmwave_analysis/thumbnail.jpg",
                "case_type": "simulation",
                "case_title": "城市毫米波通信信道特性分析",
                "model_name": "UrbanSim,WaveTrace",
                "model_type_name": "城市环境模型,射线追踪模型",
                "create_date_str": "2023-06-20"
            },
            {
                "case_dir_name": "indoor_wifi_optimization",
                "case_img_path": "/storage/best_cases/indoor_wifi_optimization/thumbnail.jpg", 
                "case_type": "real_data",
                "case_title": "室内WiFi网络覆盖优化",
                "model_name": "IndoorPlanner,CoverageOpt",
                "model_type_name": "室内传播模型,覆盖优化模型",
                "create_date_str": "2023-07-10"
            },
            {
                "case_dir_name": "satellite_communication",
                "case_img_path": "/storage/best_cases/satellite_communication/thumbnail.jpg",
                "case_type": "simulation", 
                "case_title": "卫星通信链路预算分析",
                "model_name": "SatLink,OrbitTrace",
                "model_type_name": "卫星链路模型,轨道计算模型",
                "create_date_str": "2023-08-05"
            },
            {
                "case_dir_name": "massive_mimo_beamforming",
                "case_img_path": "/storage/best_cases/massive_mimo_beamforming/thumbnail.jpg",
                "case_type": "real_data",
                "case_title": "大规模MIMO波束赋形技术研究",
                "model_name": "MIMOBeam,ArrayDesign",
                "model_type_name": "天线阵列模型,波束赋形模型", 
                "create_date_str": "2023-09-12"
            },
            {
                "case_dir_name": "iot_sensor_network",
                "case_img_path": "/storage/best_cases/iot_sensor_network/thumbnail.jpg",
                "case_type": "no_label",
                "case_title": "物联网传感器网络拓扑优化",
                "model_name": "IoTOptimizer",
                "model_type_name": "网络拓扑模型",
                "create_date_str": "2023-10-01"
            },
            {
                "case_dir_name": "vehicular_v2x_communication",
                "case_img_path": "/storage/best_cases/vehicular_v2x_communication/thumbnail.jpg",
                "case_type": "simulation",
                "case_title": "车联网V2X通信性能评估", 
                "model_name": "V2XSim,VehicularNet",
                "model_type_name": "车联网模型,移动性模型",
                "create_date_str": "2023-11-15"
            },
            {
                "case_dir_name": "smart_factory_wireless",
                "case_img_path": "/storage/best_cases/smart_factory_wireless/thumbnail.jpg",
                "case_type": "real_data",
                "case_title": "智能工厂无线网络部署方案",
                "model_name": "FactoryWireless,IndustrialNet",
                "model_type_name": "工业环境模型,无线部署模型",
                "create_date_str": "2023-12-03"
            }
        ]
        
        print("开始添加模拟数据...")
        
        # 检查是否已存在数据，避免重复添加
        existing_count = BestPracticeCase.query.count()
        if existing_count > 0:
            print(f"数据库中已存在 {existing_count} 条记录")
            choice = input("是否清空现有数据并重新添加？(y/N): ").strip().lower()
            if choice == 'y':
                # 清空现有数据
                BestPracticeCase.query.delete()
                db.session.commit()
                print("已清空现有数据")
            else:
                print("取消操作")
                return
        
        # 添加模拟数据
        for i, case_data in enumerate(sample_cases, 1):
            new_case = BestPracticeCase(
                case_dir_name=case_data["case_dir_name"],
                case_img_path=case_data["case_img_path"],
                case_type=case_data["case_type"],
                case_title=case_data["case_title"],
                model_name=case_data["model_name"],
                model_type_name=case_data["model_type_name"],
                create_date_str=case_data["create_date_str"]
            )
            
            db.session.add(new_case)
            print(f"添加第 {i} 条数据: {case_data['case_title']}")
        
        try:
            # 提交到数据库
            db.session.commit()
            print(f"\n✅ 成功添加了 {len(sample_cases)} 条模拟数据！")
            
            # 验证数据
            total_count = BestPracticeCase.query.count()
            print(f"数据库中现在共有 {total_count} 条记录")
            
            # 显示添加的数据
            print("\n📋 已添加的数据预览:")
            cases = BestPracticeCase.query.all()
            for case in cases:
                print(f"- {case.case_title} ({case.case_type})")
                
        except Exception as e:
            # 回滚事务
            db.session.rollback()
            print(f"❌ 添加数据时出错: {str(e)}")
            
def show_existing_data():
    """显示现有数据"""
    app = create_app()
    with app.app_context():
        cases = BestPracticeCase.query.all()
        if not cases:
            print("数据库中暂无数据")
            return
            
        print(f"\n📋 数据库中现有 {len(cases)} 条记录:")
        for i, case in enumerate(cases, 1):
            print(f"{i}. 标题: {case.case_title}")
            print(f"   类型: {case.case_type}")
            print(f"   目录: {case.case_dir_name}")
            print(f"   模型: {case.model_name}")
            print(f"   创建日期: {case.create_date_str}")
            print("-" * 50)

def clear_all_data():
    """清空所有数据"""
    app = create_app()
    with app.app_context():
        count = BestPracticeCase.query.count()
        if count == 0:
            print("数据库中没有数据")
            return
            
        choice = input(f"确认要删除 {count} 条记录吗？(y/N): ").strip().lower()
        if choice == 'y':
            BestPracticeCase.query.delete()
            db.session.commit()
            print(f"✅ 已删除 {count} 条记录")
        else:
            print("取消删除操作")

if __name__ == "__main__":
    print("=== 最佳实践案例数据管理工具 ===")
    print("1. 添加模拟数据")
    print("2. 查看现有数据") 
    print("3. 清空所有数据")
    print("0. 退出")
    
    while True:
        choice = input("\n请选择操作 (0-3): ").strip()
        
        if choice == "1":
            add_sample_data()
        elif choice == "2":
            show_existing_data()
        elif choice == "3":
            clear_all_data()
        elif choice == "0":
            print("再见！")
            break
        else:
            print("无效选择，请输入 0-3")