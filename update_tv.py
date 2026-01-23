import requests
import re
import time

# 从 APK 中提取的后端验证接口和配置
AUTH_URL = "http://64.32.9.99:7999/index.php" # 核心刷号接口
UA = "CloudTV/6.4.5 (Android/12)" # 模拟 App 访问身份

def fetch_latest_token():
    """模拟 App 刷号获取最新的 Token"""
    try:
        # 模拟 App 启动时的握手请求
        params = {"m": "init", "v": "6.4.5"} 
        resp = requests.get(AUTH_URL, params=params, headers={"User-Agent": UA}, timeout=10)
        
        # 使用正则从返回数据中提取 32 位哈希 Token
        # 注意：这里的正则根据 APK 返回格式调整
        match = re.search(r'[a-f0-9]{32}', resp.text)
        if match:
            return match.group(0)
    except Exception as e:
        print(f"刷号失败: {e}")
    return None

def update_file(new_token):
    """更新 live.txt 中的所有链接"""
    file_path = "live.txt"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            # 找到含有 mitv:// 的行，替换其中的 32 位 Token
            if "mitv://" in line:
                updated_line = re.sub(r'/[a-f0-9]{32}\.ts', f'/{new_token}.ts', line)
                new_lines.append(updated_line)
            else:
                new_lines.append(line)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"成功更新 Token 为: {new_token}")
        return True
    except Exception as e:
        print(f"文件处理失败: {e}")
        return False

if __name__ == "__main__":
    token = fetch_latest_token()
    if token:
        update_file(token)
    else:
        print("未获取到有效 Token，请检查后台接口状态。")
