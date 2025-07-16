# 测试重构后的代码

import sys
import os
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        from utils.config_manager import ConfigManager
        self.config_manager = ConfigManager()
    
    def test_get_config(self):
        config = self.config_manager.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn("login", config)
        self.assertIn("gate", config)
    
    def test_get_login_config(self):
        login_config = self.config_manager.get_login_config()
        self.assertIsInstance(login_config, dict)
        self.assertIn("url", login_config)
        self.assertIn("host", login_config)
        self.assertIn("port", login_config)
    
    def test_get_gate_config(self):
        gate_config = self.config_manager.get_gate_config()
        self.assertIsInstance(gate_config, dict)
        self.assertIn("host", gate_config)
        self.assertIn("port", gate_config)
    
    def test_get_proto_path(self):
        proto_path = self.config_manager.get_proto_path()
        self.assertIsInstance(proto_path, str)
        self.assertTrue(len(proto_path) > 0)

class TestBaseTCPClient(unittest.TestCase):
    def setUp(self):
        from utils.base_tcp_client import BaseTCPClient
        self.client = BaseTCPClient("login")
    
    def test_init(self):
        self.assertEqual(self.client.server_type, "login")
        self.assertIsInstance(self.client.command_handlers, dict)
        self.assertIsInstance(self.client.ack_handlers, dict)
        self.assertIn("quit", self.client.command_handlers)
    
    def test_add_command(self):
        def test_command(client):
            pass
        
        self.client.add_command("test", test_command)
        self.assertIn("test", self.client.command_handlers)
        self.assertEqual(self.client.command_handlers["test"], test_command)
    
    def test_add_ack_handler(self):
        def test_handler(seq, payload):
            pass
        
        self.client.add_ack_handler(999, test_handler)
        self.assertIn("custom_999", self.client.ack_handlers)
        proto_id, handler = self.client.ack_handlers["custom_999"]
        self.assertEqual(proto_id, 999)
        self.assertEqual(handler, test_handler)

class TestUtilityFunctions(unittest.TestCase):
    def test_formatters(self):
        from utils.utils import Utils
        test_dict = {"key": "value", "number": 123}
        
        try:
            Utils.print_dict(test_dict, "测试:")
        except Exception as e:
            self.fail(f"print_dict raised an exception: {e}")
    
    def test_time_utils(self):
        from utils.utils import Utils
        
        time_str = "2025-01-01 12:00:00"
        timestamp = Utils.str_to_timestamp(time_str)
        self.assertIsInstance(timestamp, int)
        self.assertGreater(timestamp, 0)
        
        converted_str = Utils.timestamp_to_str(timestamp)
        self.assertEqual(converted_str, time_str)

def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestBaseTCPClient))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过!")
    else:
        print(f"\n❌ 有 {len(result.failures)} 个测试失败")
        print(f"❌ 有 {len(result.errors)} 个测试错误")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
