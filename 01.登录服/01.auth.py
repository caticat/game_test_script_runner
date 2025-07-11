# 测试登录认证

from utils.print_dict import print_dict
from utils.login_poster import send_to_login

# 认证
def auth():
    payload = {
        "Channel": "dev",
        "Code": "q1",
    }
    result = send_to_login("auth_step", payload)
    print_dict(result, "返回结果:")
    return result

# 选服
def selectArea(result_auth):
    if "ResultId" in result_auth and result_auth["ResultId"] != 0:
        print("认证失败")
        return
    
    payload = {
        "OpenId": result_auth["OpenId"],
        "AreaId": 1,
        "LoginToken": result_auth["LoginToken"],
    }
    result = send_to_login("select_area", payload)
    print_dict(result, "返回结果:")


# 主函数
def main():
    result_auth = auth()
    selectArea(result_auth)

if __name__ == "__main__":
    main()