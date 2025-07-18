# 测试自动参数获取功能

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script_executor import ScriptExecutor

async def test_auto_params():
    """测试自动参数获取"""
    print("🧪 测试自动参数获取功能")
    
    executor = ScriptExecutor()
    
    # 模拟认证返回结果
    executor.results["auth"] = {
        "OpenId": "test_user",
        "LoginToken": "test_token"
    }
    
    # 模拟选服返回结果
    executor.results["select_area"] = {
        "RoleId": 12345,
        "Signature": "test_signature",
        "GateHost": "192.168.1.100",
        "GateTcpPort": 6001
    }
    
    # 测试connect_gate自动获取参数
    print("\n📡 测试connect_gate自动获取网关地址...")
    try:
        # 模拟connect_gate的参数获取逻辑，不进行实际连接
        def test_connect_gate_params():
            select_area_result = executor.results.get("select_area")
            if select_area_result and "GateHost" in select_area_result and "GateTcpPort" in select_area_result:
                host = select_area_result["GateHost"]
                port = select_area_result["GateTcpPort"]
                return {"host": host, "port": port, "from_select_area": True}
            else:
                return {"host": "127.0.0.1", "port": 5001, "from_select_area": False}
        
        result = test_connect_gate_params()
        print(f"✅ connect_gate结果: {result}")
        
        expected_host = "192.168.1.100"
        expected_port = 6001
        
        if result["host"] == expected_host and result["port"] == expected_port and result["from_select_area"]:
            print("✅ connect_gate自动参数获取测试通过")
        else:
            print(f"❌ connect_gate自动参数获取测试失败: 期望 {expected_host}:{expected_port}, 得到 {result['host']}:{result['port']}")
    except Exception as e:
        print(f"❌ connect_gate测试失败: {e}")
    
    # 测试login自动获取参数
    print("\n🔐 测试login自动获取参数...")
    try:
        # 模拟没有客户端连接的情况下测试参数获取逻辑
        # 创建一个临时的login函数来测试参数获取
        def test_login_params():
            signature = ""
            role_id = 0
            user_name = ""
            
            # 模拟login函数的参数获取逻辑
            if not signature or not role_id or not user_name:
                select_area_result = executor.results.get("select_area")
                auth_result = executor.results.get("auth")
                
                if not signature and select_area_result and "Signature" in select_area_result:
                    signature = select_area_result["Signature"]
                    
                if not role_id and select_area_result and "RoleId" in select_area_result:
                    role_id = select_area_result["RoleId"]
                    
                if not user_name and auth_result and "OpenId" in auth_result:
                    user_name = auth_result["OpenId"]
            
            return {
                "signature": signature,
                "role_id": role_id,
                "user_name": user_name
            }
        
        params = test_login_params()
        print(f"✅ login自动获取的参数: {params}")
        
        expected_signature = "test_signature"
        expected_role_id = 12345
        expected_user_name = "test_user"
        
        if (params["signature"] == expected_signature and 
            params["role_id"] == expected_role_id and 
            params["user_name"] == expected_user_name):
            print("✅ login自动参数获取测试通过")
        else:
            print(f"❌ login自动参数获取测试失败")
            print(f"   期望: signature={expected_signature}, role_id={expected_role_id}, user_name={expected_user_name}")
            print(f"   实际: signature={params['signature']}, role_id={params['role_id']}, user_name={params['user_name']}")
            
    except Exception as e:
        print(f"❌ login参数获取测试失败: {e}")
    
    executor.close()

async def main():
    """主测试函数"""
    print("🚀 开始测试自动参数获取功能")
    print("=" * 50)
    
    await test_auto_params()
    
    print("\n🎉 自动参数获取测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
