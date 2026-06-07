#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
█████████████████████████████████████████████████████████████████████████████
█                    SOCKS5 PROXY FINDER - PROFESSIONAL EDITION              █
█              Find working SOCKS5 proxies like the one that works           █
█                        62.220.126.92:31405                                 █
█                  Fast | Accurate | Auto-save | Ready to use                █
█████████████████████████████████████████████████████████████████████████████
"""

import socket
import random
import time
import threading
import os
import sys
from struct import pack
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError
# ======================== Color Settings ========================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.WHITE, bold=False):
    """Print colored text"""
    bold_code = Colors.BOLD if bold else ""
    print(f"{bold_code}{color}{text}{Colors.END}")

def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display program banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                         🔥 SOCKS5 PROXY FINDER 🔥                            ║
║                                                                              ║
║              ⚡ Find working proxies for Telegram & Free Internet            ║
║                                                                              ║
║                           🚀 Fast & Automatic 🚀                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}
    """
    print(banner)

# ======================== SOCKS5 Protocol Test ========================
def test_socks5_proxy(server_ip: str, port: int, timeout: int = 2):
    """Test SOCKS5 proxy on a specific port - optimized"""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((server_ip, port))
        
        # SOCKS5 handshake
        sock.send(pack('BBB', 0x05, 0x01, 0x00))
        response = sock.recv(2)
        if len(response) < 2:
            return False
        
        ver, method = response
        if ver == 0x05 and method == 0x00:
            # Send CONNECT request
            cmd = pack('!BBBB', 0x05, 0x01, 0x00, 0x01)
            dest_ip = socket.inet_aton('8.8.8.8')
            dest_port = pack('!H', 53)
            sock.send(cmd + dest_ip + dest_port)
            response = sock.recv(4)
            if len(response) == 4 and response[1] == 0x00:
                return True
        return False
    except socket.timeout:
        return False
    except ConnectionRefusedError:
        return False
    except OSError as e:
        return False
    except:
        return False
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass
            

# class SafeScanner:
#     """Scanner with rate limiting and timeout protection"""
    
#     def __init__(self, max_workers=200, rate_limit=100):
#         self.max_workers = min(max_workers, 500)
#         self.rate_limit = rate_limit  # حداکثر درخواست در ثانیه
#         self.request_times = []
#         self.lock = threading.Lock()
    
#     def can_scan(self):
#         """Check if we're within rate limit"""
#         with self.lock:
#             now = time.time()
#             # پاک کردن درخواست‌های قدیمی‌تر از ۱ ثانیه
#             self.request_times = [t for t in self.request_times if now - t < 1]
            
#             if len(self.request_times) >= self.rate_limit:
#                 return False
            
#             self.request_times.append(now)
#             return True
    
#     def scan_with_timeout(self, func, timeout=30):
#         """Run scan with global timeout"""
#         with ThreadPoolExecutor(max_workers=1) as executor:
#             future = executor.submit(func)
#             try:
#                 return future.result(timeout=timeout)
#             except TimeoutError:
#                 print_colored(f"⚠️ Scan timed out after {timeout} seconds", Colors.YELLOW)
#                 return [], 0
# ======================== Quick Port Check ========================
def quick_port_check(ip, port, timeout=1):
    """Very fast port check (just checking if port is open)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

# ======================== IP Generation Functions ========================
def generate_ips_from_range(ip_prefix):
    """
    Generate ALL IPs from a specific prefix
    Example: "62.220.126" → 62.220.126.1 to 62.220.126.255
    Example: "62.220" → 62.220.0.1 to 62.220.255.254
    """
    ips = []
    parts = ip_prefix.strip().split('.')
    
    if len(parts) == 3:
        # Full /24 range (1-255)
        a, b, c = int(parts[0]), int(parts[1]), int(parts[2])
        for d in range(1, 256):
            ips.append(f"{a}.{b}.{c}.{d}")
            
    elif len(parts) == 2:
        # /16 range (0-255 for last two octets)
        a, b = int(parts[0]), int(parts[1])
        for c in range(0, 256):
            for d in range(1, 255):
                ips.append(f"{a}.{b}.{c}.{d}")
                
    elif len(parts) == 1:
        # /8 range (very large - be careful)
        a = int(parts[0])
        for b in range(0, 256):
            for c in range(0, 256):
                for d in range(1, 255):
                    ips.append(f"{a}.{b}.{c}.{d}")
    
    return ips

def generate_iran_priority_ips(count=5000):
    """
    تولید IPهای ایرانی با اولویت رنج‌های شناخته شده برای سوکسی تلگرام
    70% از رنج‌های مطمئن ایرانی، 30% از رنج‌های احتمالی ایرانی
    """
    # رنج‌های ثابت شده ایران که برای تلگرام کار می‌کنند
    iran_priority_ranges = [
        # رنج‌های اصلی مخابرات
        ("185.146", 2),     # مخابرات تهران
        ("185.143", 2),     # مخابرات اصفهان
        ("185.144", 2),     # مخابرات مشهد
        ("185.145", 2),     # مخابرات شیراز
        ("185.147", 2),     # مخابرات تبریز
        
        # رنج‌های شرکت ارتباطات زیرساخت
        ("81.12", 2),       # AS12880
        ("62.220", 2),      # AS43754
        ("185.235", 2),     # AS206188
        
        # رنج‌های همراه اول
        ("37.32", 2),       # همراه اول
        ("37.148", 2),      # همراه اول
        ("5.124", 2),       # همراه اول
        
        # رنج‌های آسیاتک
        ("78.39", 2),       # آسیاتک
        ("83.123", 2),      # آسیاتک
    ]
    
    # رنج‌های احتمالی دیگه
    iran_secondary_ranges = [
        ("185.173", 2),     # ISP های کوچیک
        ("185.119", 2),     # ISP های شرق کشور
        ("185.148", 2),     # ISP های جنوب
        ("195.191", 2),     # دیتاسنترها
        ("94.182", 2),      # رایتل
        ("31.7", 2),        # های وب
        ("5.160", 2),       # ایرانسل
        ("5.202", 2),       # مبین نت
        ("46.100", 2),      # مخابرات
        ("46.143", 2),      # ایرانسل
        ("46.51", 2),       # رایتل
        ("46.167", 2),      # شاتل
        ("46.209", 2),      # پارس آنلاین
        ("46.224", 2),      # مبین نت
        ("93.110", 2),      # آسیاتک
        ("95.38", 2),       # ایرانسل
        ("95.81", 2),       # مخابرات
        ("95.162", 2),      # شاتل
        ("151.239", 2),     # رایتل
        ("164.138", 2),     # دیتاسنتر ایران
        ("178.22", 2),      # های وب
        ("178.157", 2),     # پارس آنلاین
        ("185.158", 2),     # ISP های جدید
        ("185.165", 2),     # ISP های تهران
        ("185.180", 2),     # ISP های شمال
        ("185.211", 2),     # دیتاسنتر
        ("194.225", 2),     # عسلویه
        ("212.33", 2),      # مخابرات
    ]
    
    # حذف رنج‌های غیرقابل استفاده
    INVALID_RANGES = [
        "172.16",  # خصوصی (باید حذف بشه)
        "10.10",   # خصوصی (باید حذف بشه)
    ]
    
    ips = set()
    max_attempts = count * 3  # حداکثر تلاش برای جلوگیری از حلقه بی‌نهایت
    attempts = 0
    
    # 70% از رنج‌های اولویت دار (مطمئن‌تر)
    priority_count = int(count * 0.7)
    priority_ratio = 0.8  # 80% از این 70% از رنج‌های خیلی مطمئن
    
    while len(ips) < priority_count and attempts < max_attempts:
        attempts += 1
        
        # انتخاب رنج
        if random.random() < priority_ratio:
            prefix, octets = random.choice(iran_priority_ranges)
        else:
            prefix, octets = random.choice(iran_secondary_ranges)
        
        # رد کردن رنج‌های نامعتبر
        if prefix in INVALID_RANGES:
            continue
        
        # تولید IP معتبر
        if octets == 2:
            # فرمت: prefix.c.d
            # c می‌تواند 0-255 باشد اما d باید 1-254
            c = random.randint(0, 255)
            d = random.randint(1, 254)
            
            # حذف IPهای رزرو شده و برادکست
            if d == 0 or d == 255:
                continue
            
            ip = f"{prefix}.{c}.{d}"
        else:
            # فرمت: prefix با تعداد octet های مشخص
            current_parts = prefix.split('.')
            remaining = 4 - len(current_parts)
            parts = []
            for i in range(remaining):
                if i == remaining - 1:  # آخرین octet
                    parts.append(str(random.randint(1, 254)))
                else:
                    parts.append(str(random.randint(0, 255)))
            ip = f"{prefix}.{'.'.join(parts)}"
        
        ips.add(ip)
    
    # اگر به تعداد کافی نرسیدیم، با رنج‌های تصادفی ادامه بده
    random_count = count - len(ips)
    random_ranges = [
        "5.124", "5.202", "5.160", "31.7", "31.24", "31.214",
        "37.32", "37.98", "37.148", "46.100", "46.143", "46.209",
        "78.39", "78.109", "78.157", "80.66", "80.71", "80.75",
        "81.91", "81.12", "81.28", "83.123", "83.147", "83.170",
        "85.133", "85.185", "85.239", "89.144", "89.165", "89.235",
        "91.98", "91.99", "91.106", "93.110", "93.114", "93.115",
        "94.182", "94.183", "94.184", "95.38", "95.81", "95.162",
        "151.239", "151.246", "151.247", "164.138", "164.215",
        "176.46", "176.102", "176.123", "178.22", "178.131", "178.157",
        "185.80", "185.87", "185.143", "188.34", "188.118", "188.121",
        "194.225", "194.226", "195.146", "212.16", "212.33", "212.105",
        "213.176", "213.195", "213.217",
    ]
    
    attempts = 0
    while len(ips) < count and attempts < max_attempts:
        attempts += 1
        prefix = random.choice(random_ranges)
        c = random.randint(1, 254)
        d = random.randint(1, 254)
        ip = f"{prefix}.{c}.{d}"
        ips.add(ip)
    
    result = list(ips)[:count]
    
    # اضافه کردن پورت‌ها به IPها (اختیاری)
    # اگر نیاز به پورت دارید، این بخش رو فعال کنید
    # socks_ports = [1080, 1081, 9050, 9051, 9150, 1085, 1086, 1087, 8080, 3128, 8085, 9999]
    # result_with_ports = [f"{ip}:{random.choice(socks_ports)}" for ip in result]
    # return result_with_ports
    
    return result



def generate_priority_ips(count=5000):
    """
    Generate random IPs prioritizing known working ranges for Telegram SOCKS proxies
    70% from proven ranges, 30% completely random
    """
    # Ranges that have previously yielded working proxies for Telegram
    priority_ranges = [
        # Residential proxy ranges (most reliable for Telegram)
        ("185.146", 2),      # Iranian residential range
        ("185.143", 2),      # Iranian residential range  
        ("81.12", 2),        # Iranian IP range
        ("62.220", 2),       # Iranian IP range
        ("185.235", 2),      # Iranian IP range
        
        # European residential ranges
        ("194.36", 2),       # Netherlands/Germany
        ("193.106", 2),      # Eastern Europe
        ("91.211", 2),       # Baltic region
        ("185.216", 2),      # European proxies
        
        # Cloud providers (less reliable but faster)
        ("13.32", 2),        # AWS CloudFront
        ("104.16", 2),       # Cloudflare
        ("34.64", 2),        # Google Cloud
        ("157.240", 2),      # Facebook/Meta (some work)
    ]
    
    # Common SOCKS ports that work with Telegram
    
    ips = set()
    
    # 70% from priority ranges
    priority_count = int(count * 0.7)
    for _ in range(priority_count):
        prefix, octets = random.choice(priority_ranges)
        if octets == 2:
            # Format: x.x.x
            c = random.randint(0, 255)
            d = random.randint(1, 254)
            ip = f"{prefix}.{c}.{d}"
        else:
            # Format: x.x.x.x
            remaining = 4 - prefix.count('.') - 1
            parts = []
            for _ in range(remaining):
                parts.append(str(random.randint(0, 255)))
            ip = f"{prefix}.{'.'.join(parts)}"
        
        # Add port information for better proxy generation
        ips.add(ip)
    
    # 30% completely random (but restricted to routable IPs)
    random_count = count - len(ips)
    for _ in range(random_count):
        # Generate routable, non-reserved IPs
        while True:
            a = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
                               32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 45, 46, 47, 49, 50, 51, 52, 
                               54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 
                               71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 
                               88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 
                               104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 
                               118, 119, 120, 121, 122, 123, 124, 125, 126, 128, 129, 130, 131, 132, 
                               133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 
                               147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 
                               161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 
                               175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 
                               189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 
                               203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 
                               217, 218, 219, 220, 221, 222, 223])
            
            # Skip reserved/private ranges
            if a == 10: continue  # 10.0.0.0/8 private
            if a == 127: continue  # 127.0.0.0/8 loopback
            if a == 169: continue  # 169.254.0.0/16 link-local
            if a == 172 and random.randint(16, 31): continue  # 172.16.0.0/12 private
            if a == 192 and random.randint(0, 1): continue  # 192.168.0.0/16 private
            if a == 224: continue  # Multicast
            if a >= 225: continue  # Reserved
            
            b = random.randint(0, 255)
            c = random.randint(0, 255)
            d = random.randint(1, 254)
            ip = f"{a}.{b}.{c}.{d}"
            
            # Add port
            ips.add(ip)
            break

    return list(ips)[:count]

def load_ips_from_file(filename):
    """Load IP list from text file (one IP per line)"""
    try:
        with open(filename, 'r') as f:
            ips = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return ips
    except FileNotFoundError:
        return []

# ======================== Scanning Functions ========================
def scan_single_ip(ip, ports, timeout=2):
    """Scan a single IP for multiple ports"""
    working_ports = []
    for port in ports:
        if test_socks5_proxy(ip, port, timeout):
            working_ports.append(port)
    return ip, working_ports

# ======================== RateLimiter ========================
class RateLimiter:
    def __init__(self, max_requests_per_second=100):
        self.max_requests = max_requests_per_second
        self.requests = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            self.requests = [t for t in self.requests if now - t < 1]
            
            if len(self.requests) >= self.max_requests:
                oldest = min(self.requests)
                wait_time = 1 - (now - oldest)
                if wait_time > 0:
                    time.sleep(wait_time)
                self.requests = [t for t in self.requests if time.time() - t < 1]
            
            self.requests.append(time.time())

def fast_port_scan(ips, target_port, max_workers=20, timeout=1):
    """Ultra-fast scan for a specific port"""
    working = []
    tested = 0
    lock = threading.Lock()
    start_time = time.time()

    rate_limiter = RateLimiter(max_requests_per_second=500)
    print_colored(f"\n🚀 Fast scanning port {target_port} with {max_workers} threads...", Colors.CYAN)
    print_colored(f"📊 Total IPs to check: {len(ips)}\n", Colors.YELLOW)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(quick_port_check, ip, target_port, timeout): ip for ip in ips}
        
        for future in as_completed(future_to_ip):
            rate_limiter.wait_if_needed()
            tested += 1
            ip = future_to_ip[future]
            
            if future.result():
                # Port is open, now test full SOCKS5
                if test_socks5_proxy(ip, target_port, timeout=2):
                    with lock:
                        working.append((ip, target_port))
                    print_colored(f"✅✅✅ FOUND: {ip}:{target_port}", Colors.GREEN, bold=True)
                    print_colored(f"   Telegram link: https://t.me/socks?server={ip}&port={target_port}", Colors.CYAN)
            
            if tested % 1000 == 0:
                percent = (tested / len(ips)) * 100
                speed = tested / (time.time() - start_time)
                print_colored(f"📊 Progress: {tested}/{len(ips)} ({percent:.1f}%) | Speed: {speed:.0f} IPs/sec | Found: {len(working)}", Colors.BLUE)
    
    elapsed = time.time() - start_time
    return working, elapsed

def full_scan(ips, ports, max_workers=20, timeout=2):
    """Complete scan checking multiple ports"""
    working = []
    tested = 0
    lock = threading.Lock()
    start_time = time.time()
    
    
    rate_limiter = RateLimiter(max_requests_per_second=500)  # 500 درخواست در ثانیه
    print_colored(f"\n🚀 Starting full scan with {max_workers} threads...", Colors.CYAN)
    print_colored(f"🎯 Testing ports: {ports[:5]}{'...' if len(ports)>5 else ''} (total: {len(ports)})", Colors.YELLOW)
    print_colored(f"📊 Total IPs: {len(ips)}", Colors.YELLOW)
    print_colored(f"📊 Total test: {len(ips)*len(ports)}\n", Colors.YELLOW)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(scan_single_ip, ip, ports, timeout): ip for ip in ips}
        for future in as_completed(future_to_ip):
            tested += 1
            rate_limiter.wait_if_needed()  # کنترل نرخ درخواست‌ها
            ip, found_ports = future.result()
            if found_ports:
                with lock:
                    for port in found_ports:
                        working.append((ip, port))
                
                for port in found_ports:
                    print_colored(f"✅✅✅ FOUND: {ip}:{port}", Colors.GREEN, bold=True)
                    print_colored(f"   Telegram link: https://t.me/socks?server={ip}&port={port}", Colors.CYAN)
            
            if tested % max_workers == 0:
                percent = (tested / len(ips)) * 100
                speed = tested / (time.time() - start_time)
                print_colored(f"📊 Progress: {tested}/{len(ips)} ({percent:.1f}%) | Speed: {speed:.0f} IPs/sec | Found: {len(working)}", Colors.HEADER)
    
    elapsed = time.time() - start_time
    return working, elapsed

# ======================== Save Results ========================
def save_results(proxies, scan_info):
    """Save found proxies to files"""
    if not proxies:
        print_colored("\n⚠️ No proxies found to save.", Colors.YELLOW)
        return False

    # IP-only file for Shir o Khorshid
    import os
    # ایجاد پوشه result اگر وجود نداشته باشد
    result_dir = "result"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # ساخت مسیر کامل فایل داخل پوشه result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    telegram_file = os.path.join(result_dir, f"Find IP_{timestamp}.txt")



    with open(telegram_file, 'w') as f:
        f.write(f"# IP Finder \n")
        f.write(f"# Scan Date: {datetime.now()}\n")
        f.write("#" * 50 + "\n\n")
        for ip, port in proxies:
            f.write(f"{ip}\n")
        f.write("\n\n#" * 50 + "\n\n")
        for ip, port in proxies:
            f.write(f"https://t.me/socks?server={ip}&port={port}\n")
            
    print_colored(f"\n💾 Results saved to:", Colors.GREEN, bold=True)
    print_colored(f"   • {telegram_file} - Telegram links", Colors.WHITE)
    
    return True

def display_results(proxies):
    """Display found proxies in a nice format"""
    if not proxies:
        print_colored("\n❌ No working SOCKS5 proxies found!", Colors.RED, bold=True)
        return
    
    print_colored(f"\n{'='*60}", Colors.CYAN, bold=True)
    print_colored(f"📋 WORKING SOCKS5 PROXIES FOUND: {len(proxies)}", Colors.GREEN, bold=True)
    print_colored(f"{'='*60}", Colors.CYAN, bold=True)
    
    for i, (ip, port) in enumerate(proxies, 1):
        print_colored(f"\n{i}. {Colors.GREEN}{ip}:{port}{Colors.END}")
        print_colored(f"   Telegram: https://t.me/socks?server={ip}&port={port}", Colors.CYAN)
    
    print_colored(f"\n{'='*60}", Colors.CYAN, bold=True)
    print_colored(f"💡 How to use in Telegram:", Colors.YELLOW, bold=True)
    print_colored(f"   1. Go to Settings → Advanced → Connection Type", Colors.WHITE)
    print_colored(f"   2. Select SOCKS5", Colors.WHITE)
    print_colored(f"   3. Enter Server IP and Port", Colors.WHITE)
    print_colored(f"   4. Save and enjoy free internet!", Colors.WHITE)

def port_genarate(start: int, end: int, step: int) -> list:
    """
    Generate a list of ports within range
    
    Args:
        start: Starting port (inclusive)
        end: Ending port (exclusive)
        step: Step between ports
    
    Returns:
        List of port numbers
    """
    if start < 1 or end > 65535 or start >= end:
        print_colored(f"❌ Invalid port range: {start}-{end}", Colors.RED)
        return [1080, 31405, 32193]  # بازگشت به پیش‌فرض
    
    return list(range(start, end,step))
# ======================== Main Menu ========================
def main():
    while True:
        print_banner()
        
        print_colored(f"\n{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.END}")
        print_colored(f"{Colors.YELLOW}{Colors.BOLD}SELECT SCAN MODE:{Colors.END}")
        print_colored(f"  1. 🎯 SCAN SPECIFIC RANGE (e.g., 62.220.126.x)", Colors.WHITE)
        print_colored(f"  2. 🌍 RANDOM SCAN (priority to known working ranges)", Colors.WHITE)
        print_colored(f"  3. ⚡ FAST PORT SCAN (check only port 31405 - very fast)", Colors.WHITE)
        print_colored(f"  4. 📁 SCAN FROM FILE (load IP list from text file)", Colors.WHITE)
        print_colored(f"  5. 🔄 SCAN ALL PORTS (1080, 31405, 32193, 9050, etc.)", Colors.WHITE)
        print_colored(f"  0. 🚪 EXIT", Colors.WHITE)
        
        choice = input(f"\n{Colors.GREEN}Enter your choice (0-5): {Colors.END}").strip()
        
        if choice == "0":
            print_colored("\n👋 Goodbye! Thanks for using SOCKS5 Proxy Finder!", Colors.CYAN, bold=True)
            break
        
        # Common settings
        try:
            max_workers = min(int(input(f"{Colors.GREEN}Threads (10-50, default 20): {Colors.END}").strip() or "20"), 100)
            timeout = int(input(f"{Colors.GREEN}Timeout seconds (1-3, default 2): {Colors.END}").strip() or "2")
        except:
            max_workers = 20
            timeout = 2
        
        # Known working ports
        common_ports = [      
        # SOCKS common ports
        1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089,
        1090, 9050, 9051, 9150, 9151,

        # High ports often used for proxies
        30000, 30001, 30002, 31000, 31101, 32000, 32193, 33000, 34000,
        40000, 40001, 40002, 50000, 55555, 60000, 65000, 65535]
        fast_port = 29678  # The port that worked for you
        
        ips = []
        scan_mode_desc = ""
        
        if choice == "1":
            # Specific range scan
            print_colored(f"\n{Colors.CYAN}📝 Example: 62.220.126 (scans 62.220.126.1 to .255){Colors.END}")
            ip_range = input(f"{Colors.GREEN}Enter IP prefix (e.g., 62.220.126): {Colors.END}").strip()
            ips = generate_ips_from_range(ip_range)
            scan_mode_desc = f"Range: {ip_range}.x"
            
            if not ips:
                print_colored(f"\n{Colors.RED}❌ Invalid format! Use format like: 62.220.126{Colors.END}")
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
                continue
            
            print_colored(f"\n{Colors.BLUE}📊 IPs in this range: {len(ips)}{Colors.END}")
            
            # Port selection
            print_colored(f"\n{Colors.YELLOW}Port options:{Colors.END}")
            print_colored(f"  1. Only port {fast_port} (the one that worked)", Colors.WHITE)
            print_colored(f"  2. range srart to end", Colors.WHITE)
            print_colored(f"  3. All common ports", Colors.WHITE)
            port_choice = input(f"{Colors.GREEN}Choice (1-3): {Colors.END}").strip()           
            

            
            if port_choice == "1":
                results, elapsed = fast_port_scan(ips, fast_port, max_workers, timeout)
            elif port_choice == "2":
                
                print_colored(f"\n{Colors.YELLOW}Port options:{Colors.END}")
                start_choice = int(input(f"{Colors.GREEN} start default 29000 : {Colors.END}")or 29000)
                end_choice = int(input(f"{Colors.GREEN} end default 33000:  {Colors.END}") or 33000)
                step_choice = int(input(f"{Colors.GREEN} step default 2:  {Colors.END}") or 2)
                results, elapsed = full_scan(ips, port_genarate(start_choice,end_choice,step_choice), max_workers, timeout)
            else:
                results, elapsed = full_scan(ips, common_ports, max_workers, timeout)
        
        elif choice == "2":
            # Random scan
            count = int(input(f"{Colors.GREEN}Number of random IPs (2000-20000, default 5000): {Colors.END}").strip() or "5000")
            ips = generate_priority_ips(count)
            scan_mode_desc = f"Random scan ({count} IPs)"
            
            print_colored(f"\n{Colors.BLUE}📊 Generated {len(ips)} IPs{Colors.END}")
            results, elapsed = full_scan(ips, common_ports, max_workers, timeout)
        
        elif choice == "3":
            # Fast port scan
            count = int(input(f"{Colors.GREEN}Number of random IPs (5000-50000, default 10000): {Colors.END}").strip() or "10000")
            ips = generate_priority_ips(count)
            scan_mode_desc = f"Fast scan on port {fast_port} ({count} IPs)"
            
            print_colored(f"\n{Colors.BLUE}📊 Generated {len(ips)} IPs{Colors.END}")
            results, elapsed = fast_port_scan(ips, fast_port, max_workers=20, timeout=1)
        
        elif choice == "4":
            # File scan
            filename = input(f"{Colors.GREEN}Enter filename with IPs (one per line): {Colors.END}").strip()
            ips = load_ips_from_file(filename)
            
            if not ips:
                print_colored(f"\n{Colors.RED}❌ File not found or no valid IPs in file!{Colors.END}")
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
                continue
            
            print_colored(f"\n{Colors.GREEN}✅ Loaded {len(ips)} IPs from file{Colors.END}")
            scan_mode_desc = f"File scan ({filename})"
            
            # Port selection
            print_colored(f"\n{Colors.YELLOW}Port options:{Colors.END}")
            print_colored(f"  1. Only port {fast_port} (the one that worked)", Colors.WHITE)
            print_colored(f"  2. range srart to end", Colors.WHITE)
            print_colored(f"  3. All common ports", Colors.WHITE)
            port_choice = input(f"{Colors.GREEN}Choice (1-3): {Colors.END}").strip()           
            

            
            if port_choice == "1":
                results, elapsed = fast_port_scan(ips, fast_port, max_workers, timeout)
            elif port_choice == "2":
                
                print_colored(f"\n{Colors.YELLOW}Port options:{Colors.END}")
                start_choice = int(input(f"{Colors.GREEN} start default 29000 : {Colors.END}")or 29000)
                end_choice = int(input(f"{Colors.GREEN} end default 33000:  {Colors.END}") or 33000)
                step_choice = int(input(f"{Colors.GREEN} step default 2:  {Colors.END}") or 2)
                results, elapsed = full_scan(ips, port_genarate(start_choice,end_choice,step_choice), max_workers, timeout)
            else:
                results, elapsed = full_scan(ips, common_ports, max_workers, timeout)
            
                    
        elif choice == "5":
            # Full port scan on priority ranges
            count = int(input(f"{Colors.GREEN}Number of random IPs (2000-10000, default 3000): {Colors.END}").strip() or "3000")
            print_colored(f"\n{Colors.YELLOW}IP options:{Colors.END}")
            print_colored(f"  1. All random IP ", Colors.WHITE)
            print_colored(f"  2. Only Iran IP", Colors.WHITE)
            ip_choice = input(f"{Colors.GREEN}Choice (1-2): {Colors.END}").strip()   
            if ip_choice =='1':
                ips = generate_priority_ips(count)
            elif ip_choice =='2':
                ips = generate_iran_priority_ips(count)
            scan_mode_desc = f"Full port scan ({count} IPs)"
            
            print_colored(f"\n{Colors.BLUE}📊 Generated {len(ips)} IPs{Colors.END}")
            results, elapsed = full_scan(ips, common_ports, max_workers, timeout)
        
        else:
            print_colored(f"\n{Colors.RED}❌ Invalid choice!{Colors.END}")
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
            continue
        
        # Display scan statistics
        print_colored(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print_colored(f"{Colors.GREEN}✅ SCAN COMPLETED!{Colors.END}")
        print_colored(f"{Colors.YELLOW}⏱️  Time: {elapsed:.1f} seconds{Colors.END}")
        print_colored(f"{Colors.YELLOW}⚡ Speed: {len(ips)/elapsed:.0f} IPs/second{Colors.END}")
        print_colored(f"{Colors.GREEN}🎯 Working proxies found: {len(results)}{Colors.END}")
        print_colored(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        if results:
            display_results(results)
            save_results(results, scan_mode_desc)
        
        elif results is not None:
            print_colored(f"\n{Colors.RED}❌ No working SOCKS5 proxies found!{Colors.END}")
            print_colored(f"\n{Colors.YELLOW}Suggestions:{Colors.END}")
            print_colored(f"   • Try increasing number of IPs to scan", Colors.WHITE)
            print_colored(f"   • Try a different IP range", Colors.WHITE)
            print_colored(f"   • Try increasing timeout to 3 seconds", Colors.WHITE)
            print_colored(f"   • Try again at different time (proxies change frequently)", Colors.WHITE)
        
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored(f"\n\n{Colors.RED}⚠️ Scan interrupted by user{Colors.END}")
    except Exception as e:
        print_colored(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.END}")
        print_colored(f"{Colors.YELLOW}Try running with: python socks5_finder.py{Colors.END}")