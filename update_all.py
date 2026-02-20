import requests
import concurrent.futures
import re
import random
from datetime import datetime, timedelta

# --- Configuration ---
DOMAIN = "url.cdnhs.store"
SOURCE_FILE = "cvs_mylive.txt"
TOTAL_FILE = "total_live.txt"
PRIVATE_FILE = "private_only.txt"

def check_port(port):
    """Probe port: Supports 200 OK and 302 Redirect"""
    test_url = f"http://{DOMAIN}:{port}/mytv.php?id=3"
    try:
        # 1.5s timeout for high-speed skipping
        res = requests.head(test_url, timeout=1.5, allow_redirects=False)
        if res.status_code in [200, 302]:
            return str(port)
    except:
        return None
    return None

def run_scanner(port_list):
    """Parallel scanner with randomized order and instant exit"""
    random.shuffle(port_list)
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_port = {executor.submit(check_port, p): p for p in port_list}
        for future in concurrent.futures.as_completed(future_to_port):
            result = future.result()
            if result:
                # Stop all other threads immediately when a port is found
                executor.shutdown(wait=False, cancel_futures=True)
                return result
    return None

def get_latest_port():
    """Three-stage Scanning: Core -> Regular -> Low Port (8k-65k)"""
    # Stage 1: Core Range (40k - 50k)
    print("Stage 1: Scanning core range (40k-50k)...")
    res = run_scanner(list(range(40000, 50001)))
    if res: return res
    
    # Stage 2: Regular Range (30k-40k & 50k-65k)
    print("Stage 2: Scanning regular range...")
    reg_list = list(range(30000, 40000)) + list(range(50001, 65536))
    res = run_scanner(reg_list)
    if res: return res
    
    # Stage 3: Low Port Range (8k-30k) - Prevent missing low ports
    print("Stage 3: Scanning low port range (8k-30k)...")
    res = run_scanner(list(range(8000, 30000)))
    
    return res if res else "48559" # Final fallback

def update_files():
    active_port = get_latest_port()
    # UTC+8 Beijing Time for Auto-Sync
    sync_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    total_data = []
    private_data = []
    is_private_section = False 
    
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # --- CRITICAL: Only replace target domain, skip others ---
            if DOMAIN in line:
                updated_line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{active_port}', line)
            else:
                updated_line = line # Keep other sources untouched
            
            total_data.append(updated_line)
            
            # Identify and extract private section
            if "私密频道" in updated_line:
                is_private_section = True
            
            if is_private_section:
                private_data.append(updated_line)
                
    except Exception as e:
        print(f"Error during file processing: {e}")
        return

    # 1. Output total_live.txt (Full list + Time label)
    with open(TOTAL_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(total_data))
        f.write(f"\n\n# Auto-Sync: {sync_time} | Active Port: {active_port}")

    # 2. Output private_only.txt (Private channels only)
    if private_data:
        with open(PRIVATE_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(private_data))
            f.write(f"\n\n# Sync: {sync_time}")

    print(f"Success! Port: {active_port} | Sync Time: {sync_time}")

if __name__ == "__main__":
    update_files()
