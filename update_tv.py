import requests
import re
import os

def get_new_token():
    # 模拟 APP 初始化接口
    auth_url = "http://64.32.9.99:7999/index.php?m=init&v=6.4.5"
    headers = {"User-Agent": "CloudTV/6.4.5 (Android/12)"}
    try:
        response = requests.get(auth_url, headers=headers, timeout=15)
        # 匹配 32 位 Token
        tokens = re.findall(r'[a-f0-9]{32}', response.text)
        if tokens:
            t = tokens[0]
            print(f">>> [成功] 抓取到新 Token: {t}")
            return t
        print(">>> [错误] 接口返回内容中没找到 Token")
    except Exception as e:
        print(f">>> [报错] 接口请求异常: {e}")
    return None

def force_update():
    new_token = get_new_token()
    if not new_token: return

    # 自动识别仓库内所有的 txt 文件进行更新
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    if not txt_files:
        print(">>> [错误] 目录下没找到任何 .txt 文件")
        return

    for target_file in txt_files:
        print(f">>> 正在处理文件: {target_file}")
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配所有 32 位哈希值并替换
        old_tokens = re.findall(r'[a-f0-9]{32}', content)
        if not old_tokens:
            print(f">>> [警告] 文件内未识别到直播源格式")
            continue

        new_content = re.sub(r'[a-f0-9]{32}', new_token, content)
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f">>> [完成] {target_file} 已更新 {len(old_tokens)} 处链接")

if __name__ == "__main__":
    force_update()
