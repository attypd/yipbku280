import requests
import re
import os

# 1. 获取最新授权 Token
def get_new_token():
    # 这是从你提供的刷号工具中分析出的初始化接口
    auth_url = "http://64.32.9.99:7999/index.php?m=init&v=6.4.5"
    headers = {
        "User-Agent": "CloudTV/6.4.5 (Android/12)",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(auth_url, headers=headers, timeout=15)
        # 在返回的乱码或 JSON 中匹配 32 位的哈希字符串
        tokens = re.findall(r'[a-f0-9]{32}', response.text)
        if tokens:
            new_token = tokens[0]
            print(f"成功获取新 Token: {new_token}")
            return new_token
    except Exception as e:
        print(f"请求失败: {e}")
    return None

# 2. 自动寻找并更新 TXT 文件
def update_all_txt_files(new_token):
    # 获取当前目录下所有的 txt 文件
    target_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    
    if not target_files:
        print("错误：仓库里没找到任何 .txt 文件！")
        return

    for file_name in target_files:
        print(f"正在处理文件: {file_name}")
        
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用正则替换掉链接中的 32 位 Token
        # 匹配格式：/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.ts
        pattern = r'/[a-f0-9]{32}\.ts'
        replacement = f'/{new_token}.ts'
        
        # 检查是否能匹配到
        if not re.search(pattern, content):
            print(f"警告：在 {file_name} 中没找到符合格式的直播链接。")
            continue

        # 执行全局替换
        new_content = re.sub(pattern, replacement, content)
        
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"文件 {file_name} 已成功更新！")

if __name__ == "__main__":
    token = get_new_token()
    if token:
        update_all_txt_files(token)
    else:
        print("未能获取 Token，停止更新。")
