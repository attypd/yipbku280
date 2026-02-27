import socket
import concurrent.futures
import random
import re
from datetime import datetime, timedelta

# --- 配置信息 ---
DOMAIN = "url.cdnhs.store"
SOURCE_FILE = "cvs_mylive.txt"
TOTAL_FILE = "total_live.txt"
PRIVATE_FILE = "private_only.txt"

def check_port(port):
    """
    底层 TCP 探测，确保万无一失绕过 Web 层拦截。
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.8) # 略微增加超时，确保稳定性
            if s.connect_ex((DOMAIN, int(port))) == 0:
                return str(port)
    except:
        pass
    return None

def run_scanner(port_list):
    """并行扫描，一旦找到可用端口立即停止后续扫描"""
    # 设为 120 并发，既能保证速度又不会对 GitHub Action 造成太大压力
    with concurrent.futures.ThreadPoolExecutor(max_workers=120) as executor:
        future_to_port = {executor.submit(check_port, p): p for p in port_list}
        for future in concurrent.futures.as_completed(future_to_port):
            result = future.result()
            if result:
                # 找到后强制关闭其他线程
                executor.shutdown(wait=False, cancel_futures=True)
                return result
    return None

def get_latest_port():
    """三阶段快速扫描"""
    # Stage 1: 核心区间 (40k-50k)
    print("Stage 1: Scanning core range (40k-50k)...")
    res = run_scanner(list(range(40000, 50001)))
    if res: return res

    # Stage 2: 扩展区间 (30k-40k & 50k-65k)
    print("Stage 2: Scanning regular range...")
    reg_list = list(range(30000, 40000)) + list(range(50001, 65536))
    random.shuffle(reg_list) # 随机化
    res = run_scanner(reg_list)
    if res: return res

    # Stage 3: 低频区间
    print("Stage 3: Scanning low port range (8k-30k)...")
    res = run_scanner(list(range(8000, 30000)))
    
    # 如果全部失败，返回最后的保底端口
    return res if res else "48559" 

def update_files():
    active_port = get_latest_port()
    # 修正时区显示为北京时间
    sync_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Success! Port: {active_port} | Sync Time: {sync_time}")

    # 针对每个文件执行精准替换
    for file_path in [SOURCE_FILE, TOTAL_FILE, PRIVATE_FILE]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                # 只在行内包含我们的主服务器域名时才替换端口
                if DOMAIN in line:
                    # 使用正则精准匹配 domain:port，不影响其他服务器的源
                    line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{active_port}', line)
                new_lines.append(line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Updated: {file_path}")
        except FileNotFoundError:
            print(f"File {file_path} not found, skipped.")

if __name__ == "__main__":
    update_files()
