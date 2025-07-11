import json
import requests
import yaml  # 用于加载 YAML 配置文件
import os
from utils.decode_dict import decode_dict

# 加载配置文件
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "../config/config.yml")
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

# POST 请求函数
def post_with_data_packet(url: str, data_dict: dict):
    headers = {
        "Content-Type": "application/json"
    }

    # 把 dict 压缩为无多余空格的 JSON 字符串
    json_str = json.dumps(data_dict, separators=(',', ':'))

    # 发送 POST 请求，设置超时时间为 3 秒
    try:
        response = requests.post(url, data=json_str.encode('utf-8'), headers=headers, timeout=3)
        # 尝试解析返回为 JSON
        # return response.json() # 原始数据
        return decode_dict(response.json())
    except requests.exceptions.Timeout:
        return {"error": "请求超时"}
    except Exception:
        return response.text

# 发送到 Login 的函数
def send_to_login(uri: str, data_dict: dict):
    config = load_config()
    url = config["login"]["url"]  # 从配置文件中获取 URL
    return post_with_data_packet(f"{url}/{uri}", data_dict)

# 主函数
def main():
    payload = {
        "Channel": "dev",
        "Code": "q1",
    }
    result = send_to_login("auth", payload)
    print("返回结果：", result)

if __name__ == "__main__":
    main()
