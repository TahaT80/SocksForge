#!/usr/bin/env python3
"""
SOCKS5 Proxy Port Scanner - OPTIMIZED EDITION
Fixed issues: threading limits, real-time progress, full results display
"""
import os
import socket
import time
import sys
import random
from struct import pack
from datetime import datetime
from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import requests
import concurrent.futures


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    HEADER = '\033[95m'

def print_colored(text: str, color: str = Colors.WHITE):
    print(f"{color}{text}{Colors.RESET}")


def comprehensive_test(server_ip: str, port: int):
    """Comprehensive test with final scoring"""
    proxy = f"socks5://{server_ip}:{port}"
    proxies = {'http': proxy, 'https': proxy}
    
    scores = {
        'port': port,
        'total_score': 0,
        'response_time': None,
        'speed': None,
        'reliability': 0
    }
    
    # Test 1: HTTP response time
    try:
        start = time.time()
        r = requests.get("http://httpbin.org/get", proxies=proxies, timeout=5)
        if r.status_code == 200:
            response_time = (time.time() - start) * 1000
            scores['response_time'] = response_time
            scores['total_score'] += max(0, 100 - response_time)
    except:
        pass
    
    # Test 2: Small download speed
    try:
        start = time.time()
        r = requests.get("http://httpbin.org/bytes/102400", proxies=proxies, timeout=5)
        if r.status_code == 200:
            elapsed = time.time() - start
            if elapsed > 0:
                speed = (102400 * 8) / (elapsed * 1024 * 1024)
                scores['speed'] = speed
                scores['total_score'] += min(50, speed * 10)
    except:
        pass
    
    # Test 3: Reliability
    success_count = 0
    for _ in range(3):
        try:
            r = requests.get("http://httpbin.org/status/200", proxies=proxies, timeout=2)
            if r.status_code == 200:
                success_count += 1
        except:
            pass
    scores['reliability'] = (success_count / 3) * 100
    scores['total_score'] += scores['reliability'] / 2
    
    return scores

def rank_proxies(server_ip: str, working_ports: list, max_workers: int = 8, verbose: bool = True):
    """Rank proxies by quality"""
    if verbose:
        print("\n🔍 Final Tesl")

    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(comprehensive_test, server_ip, port) for port in working_ports]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            
            if verbose:
                status = "✅" if result['total_score'] > 0 else "⚠️"
                print(f"   {status} Port {result['port']}: ", end="")
                
                if result['response_time']:
                    print(f"Time={result['response_time']:.0f}ms ", end="")
                if result['speed']:
                    print(f"Speed={result['speed']:.1f}Mbps ", end="")
                if result['reliability'] > 0:
                    print(f"Reliability={result['reliability']:.0f}% ", end="")
                print(f"| Score={result['total_score']:.0f}")
    
    results.sort(key=lambda x: x['total_score'], reverse=True)

    return results


def test_socks5_proxy(server_ip: str, port: int, timeout: int = 2) -> Tuple[bool, str]:
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
            return False, "No response"
        
        ver, method = response
        if ver == 0x05 and method == 0x00:
            # Send CONNECT request
            cmd = pack('!BBBB', 0x05, 0x01, 0x00, 0x01)
            dest_ip = socket.inet_aton('8.8.8.8')
            dest_port = pack('!H', 53)
            sock.send(cmd + dest_ip + dest_port)
            response = sock.recv(4)
            if len(response) == 4 and response[1] == 0x00:
                return True, "WORKING"
        return False, "Not SOCKS5"
    except socket.timeout:
        return False, "Timeout"
    except ConnectionRefusedError:
        return False, "Closed"
    except OSError as e:
        return False, f"OS Error"
    except:
        return False, "Error"
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass
# def test_socks5_proxy(server_ip: str, port: int, timeout: int = 2) -> Tuple[bool, str]:
#     """Test SOCKS5 proxy on a specific port - improved accuracy"""
#     sock = None
#     try:
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.settimeout(timeout)
#         sock.connect((server_ip, port))
        
#         # SOCKS5 handshake
#         sock.send(pack('BBB', 0x05, 0x01, 0x00))
#         response = sock.recv(2)
#         if len(response) < 2:
#             return False, "No response"
        
#         ver, method = response
#         if ver != 0x05 or method != 0x00:
#             return False, "Not SOCKS5"
        
#         # Send CONNECT request to 8.8.8.8:53
#         cmd = pack('!BBBB', 0x05, 0x01, 0x00, 0x01)
#         dest_ip = socket.inet_aton('8.8.8.8')
#         dest_port = pack('!H', 53)
#         sock.send(cmd + dest_ip + dest_port)
        
#         # Read full SOCKS5 response (10 bytes for IPv4)
#         response = sock.recv(10)
#         if len(response) < 10:
#             return False, "Incomplete response"
        
#         # Check reply code (byte 1)
#         if response[1] != 0x00:
#             return False, f"Proxy error: {response[1]}"
        
#         # Verify data transfer - send DNS query
#         dns_query = bytes.fromhex(
#             "0001000000010000000000000377777706676f6f676c6503636f6d0000010001"
#         )
#         sock.send(dns_query)
        
#         # Wait for DNS response
#         sock.settimeout(2)
#         dns_response = sock.recv(512)
        
#         if len(dns_response) > 50:  # Valid DNS response has reasonable size
#             return True, "WORKING"
#         else:
#             return False, "No data response"
            
#     except socket.timeout:
#         return False, "Timeout"
#     except ConnectionRefusedError:
#         return False, "Closed"
#     except:
#         return False, "Error"
#     finally:
#         if sock:
#             try:
#                 sock.close()
#             except:
#                 pass
            
def get_common_ports() -> List[int]:
    """Return a list of common proxy ports - optimized list"""
    return list(set([
        # SOCKS common ports
        1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089,
        1090, 9050, 9051, 9150, 9151,
        # HTTP/HTTPS proxy ports
        3128, 3129, 3130, 8000, 8001, 8008, 8080, 8081, 8082, 8085,
        8088, 8090, 8118, 8181, 8443, 8888, 8889, 9000, 9001, 9090,
        # High ports often used for proxies
        30000, 30001, 30002, 31000, 31101, 32000, 32193, 33000, 34000,
        40000, 40001, 40002, 50000, 55555, 60000, 65000, 65535
    ]))
    
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

def scan_common_ports(server_ip: str, timeout: int = 2, max_workers: int = 30) -> List[int]:
    """Scan only common proxy ports with optimized thread count"""
    common_ports = get_common_ports()
    working_ports = []
    completed = 0
    
    print_colored(f"\n🎯 Scanning COMMON PORTS on {server_ip}", Colors.CYAN)
    print_colored(f"📡 Total common ports: {len(common_ports)}", Colors.BLUE)
    print_colored(f"🔧 Threads: {max_workers}, Timeout: {timeout}s", Colors.BLUE)
    print_colored("=" * 70, Colors.WHITE)
    rate_limiter = RateLimiter(max_requests_per_second=500)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {
            executor.submit(test_socks5_proxy, server_ip, port, timeout): port 
            for port in common_ports
        }
        
        for future in as_completed(future_to_port):
            rate_limiter.wait_if_needed()
            port = future_to_port[future]
            completed += 1
            try:
                success, _ = future.result()
                if success:
                    working_ports.append(port)
                    print_colored(f"[{completed:3d}/{len(common_ports):3d}] ✅ Port {port} - WORKING!", Colors.GREEN)
                else:
                    if completed % 10 == 0:  # Show progress every 10 ports
                        print_colored(f"[{completed:3d}/{len(common_ports):3d}] Progress: {len(working_ports)} working", Colors.YELLOW)
            except:
                pass
    
    return working_ports

def fast_random_scan(server_ip: str, num_ports: int = 500, start_port: int = 1000, 
                     end_port: int = 65535, max_workers: int = 50, timeout: int = 2) -> List[int]:
    """Fast random port scan with optimized thread count"""
    available_ports = list(range(start_port, end_port + 1))
    if num_ports > len(available_ports):
        num_ports = len(available_ports)
    
    test_ports = random.sample(available_ports, num_ports)
    working_ports = []
    completed = 0
    lock = threading.Lock()
    
    print_colored(f"\n🎲 FAST RANDOM SCAN on {server_ip}", Colors.CYAN)
    print_colored(f"📡 Port range: {start_port}-{end_port}", Colors.BLUE)
    print_colored(f"🔢 Testing {num_ports} random ports", Colors.BLUE)
    print_colored(f"🔧 Threads: {max_workers}, Timeout: {timeout}s", Colors.BLUE)
    print_colored("=" * 70, Colors.WHITE)
    
    start_time = time.time()
    rate_limiter = RateLimiter(max_requests_per_second=500)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {
            executor.submit(test_socks5_proxy, server_ip, port, timeout): port 
            for port in test_ports
        }
        
        for future in as_completed(future_to_port):
            rate_limiter.wait_if_needed()
            
            with lock:
                completed += 1
                port = future_to_port[future]
            
            try:
                success, _ = future.result()
                if success:
                    with lock:
                        working_ports.append(port)
                    print_colored(f"[{completed:4d}/{num_ports:4d}] ✅ Port {port} WORKING!", Colors.GREEN)
                elif completed % 50 == 0:
                    print_colored(f"[{completed:4d}/{num_ports:4d}] Progress: {len(working_ports)} found so far", Colors.YELLOW)
            except:
                pass
    
    elapsed = time.time() - start_time
    print_colored(f"\n✅ Random scan completed in {elapsed:.2f} seconds", Colors.GREEN)
    print_colored(f"📊 Scanned {completed} ports, found {len(working_ports)} working", Colors.YELLOW)
    
    return working_ports

def fast_sequential_scan(server_ip: str, start_port: int, end_port: int,step:int,
                         max_workers: int = 50, timeout: int = 2) -> List[int]:
    """Fast sequential scan with real-time progress for ALL ports"""
    total_ports = int((end_port - start_port + 1)/step)
    ports = list(range(start_port, end_port + 1,step))
    os.system('cls')
    print_colored(f"⚡ FAST SEQUENTIAL SCAN on {server_ip}", Colors.CYAN)
    print_colored(f"📡 Port range: {start_port}-{end_port} (Total: {total_ports} ports)", Colors.BLUE)
    print_colored(f"🔧 Threads: {max_workers}, Timeout: {timeout}s", Colors.BLUE)
    print_colored("=" * 70, Colors.WHITE)
    
    results = {}
    completed = 0
    lock = threading.Lock()
    start_time = time.time()
    working = []
    # Create a pool with limited workers
    rate_limiter = RateLimiter(max_requests_per_second=500)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {
            executor.submit(test_socks5_proxy, server_ip, port, timeout): port 
            for port in ports
        }
        
        # Process results as they complete
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            rate_limiter.wait_if_needed()

            try:
                success, _ = future.result()
                with lock:
                    results[port] = success
                # Show real-time results
                if success:
                    working.append(port)
                    
                elif completed % max_workers == 0 :
                    # Show progress regularly or for small ranges show all
                    percent = (completed / (total_ports)) * 100
                    speed = completed / (time.time() - start_time)
                    os.system('cls')
                    print_colored(f"⚡ FAST SEQUENTIAL SCAN on {server_ip}", Colors.CYAN)
                    print_colored(f"📡 Port range: {start_port}-{end_port} (Total: {total_ports} ports)", Colors.BLUE)
                    print_colored(f"🔧 Threads: {max_workers}, Timeout: {timeout}s", Colors.BLUE)
                    print_colored("=" * 70, Colors.WHITE)
                    print_colored(f"📊 Progress: {completed}/{(total_ports)} ({percent:.1f}%) | Speed: {speed:.0f} ports/sec | Found: {len(working)}| Port: {port}", Colors.HEADER)
                    if working:
                        print_colored(f"\n✅ Port {working} - WORKING!", Colors.GREEN)
                    
            except Exception as e:
                with lock:
                    results[port] = False
            with lock:
                completed += 1
    
    elapsed = time.time() - start_time
    
    # Extract working ports
    working_ports = [port for port in ports if results.get(port, False)]
    
    # Display final summary
    print_colored("\n" + "=" * 70, Colors.CYAN)
    print_colored("FINAL RESULTS:", Colors.BOLD + Colors.YELLOW)
    print_colored("=" * 70, Colors.CYAN)
    
    if working_ports:
        for port in working_ports:
            print_colored(f"✅ Port {port} - Working SOCKS5 Proxy", Colors.GREEN)
    else:
        print_colored("❌ No working ports found", Colors.RED)
    
    print_colored("\n" + "=" * 70, Colors.CYAN)
    print_colored(f"✅ SCAN COMPLETE in {elapsed:.2f} seconds!", Colors.GREEN)
    print_colored(f"📊 Statistics:", Colors.YELLOW)
    print_colored(f"   Total ports tested: {total_ports}", Colors.WHITE)
    print_colored(f"   ✅ Working ports: {len(working_ports)}", Colors.GREEN if working_ports else Colors.RED)
    print_colored(f"   ⚡ Speed: {total_ports/elapsed:.1f} ports/second", Colors.BLUE)
    
    return working_ports

def save_results(working_ports: List[int], server_ip: str, scan_type: str):
    """Save results to file with better formatting"""
    if not working_ports:
        print_colored("\n⚠️ No working ports found to save.", Colors.YELLOW)
        return
    Final_results = rank_proxies(server_ip,working_ports)
    workig_final_port = []
    for i in Final_results:
        if i['total_score'] > 0:
            workig_final_port.append(i)  
            
            
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # IP-only file for Shir o Khorshid
    import os
    # ایجاد پوشه result اگر وجود نداشته باشد
    result_dir = "result"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # ساخت مسیر کامل فایل داخل پوشه result
    filename = os.path.join(result_dir, f"Port_Links_{server_ip}_{timestamp}.txt")

    with open(filename, "w", encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("SOCKS5 PROXY SCAN RESULTS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Target Server: {server_ip}\n")
        f.write(f"Scan Type: {scan_type}\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Working Ports Found: {len(workig_final_port)}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("WORKING PORTS:\n")
        f.write("-" * 40 + "\n")
        for port in workig_final_port:
            f.write(f"✅ {port['port']} | Time={port['response_time']:.0f}ms | Speed={port['speed']:.1f}Mbps  \n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("PROXY STRINGS (for Telegram):\n")
        f.write("-" * 40 + "\n")
        for port in working_ports:
            f.write(f"https://t.me/socks?server={server_ip}&port={port['port']}\n")
        
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("socks config (for v2ray):\n")
        f.write("-" * 40 + "\n")
        for i,port in enumerate(workig_final_port):
            f.write(f"socks://Og@{server_ip}:{port['port']}#Taha{i}\n")
            
        # Add command line example
        f.write("\n" + "=" * 60 + "\n")
        f.write("Usage in Telegram:\n")
        f.write("-" * 40 + "\n")
        f.write("Settings → Advanced → Connection Type → SOCKS5\n")
        f.write(f"Server: {server_ip}\n")
        f.write("Port: [one of the ports above]\n")
    
    print_colored(f"\n💾 Results saved to: {filename}", Colors.GREEN)
    
    
def main():
    while True:
        print_colored("\n" + "=" * 70, Colors.CYAN)
        print_colored("   SOCKS5 PROXY SCANNER - OPTIMIZED EDITION", Colors.BOLD + Colors.CYAN)
        print_colored("=" * 70, Colors.CYAN)
        
        # Get server IP
        server = input(f"\n{Colors.GREEN}Enter IP (Default: 62.220.126.92): {Colors.RESET}").strip()
        if not server:
            server = "62.220.126.92"
        
        print_colored(f"\n🎯 Target: {server}", Colors.YELLOW)
        print_colored("\nSelect scan type:", Colors.WHITE)
        print("  1. SCAN COMMON PORTS (60 ports - very fast)")
        print("  2. FAST random scan (500 random ports)")
        print("  3. FAST sequential scan (specific range - shows all)")
        print("  4. Quick test (single port)")
        print("  5. Change IP address")
        print("  0. Exit")
        
        choice = input(f"\n{Colors.GREEN}Enter choice (0-5): {Colors.RESET}").strip()
        
        if choice == "0":
            print_colored("👋 Goodbye!", Colors.CYAN)
            break
        
        elif choice == "1":
            try:
                threads = int(input("Number of threads (default 30): ") or 30)
                timeout = int(input("Timeout seconds (default 2): ") or 2)
                
                # Limit threads to reasonable number
                threads = min(threads, 50)
                
                working = scan_common_ports(server, timeout, threads)
                
                if working:
                    print_colored(f"\n✅ Found {len(working)} working ports!", Colors.GREEN)
                    save_results(working, server, "Common Ports Scan")
                else:
                    print_colored("\n❌ No working ports found.", Colors.RED)
                
                input("\nPress Enter to continue...")
                
            except ValueError:
                print_colored("❌ Invalid input!", Colors.RED)
                time.sleep(1)
        
        elif choice == "2":
            try:
                num = min(int(input("Number of random ports (default 500): ") or 500), 5000)
                threads = min(int(input("Number of threads (default 20): ") or 20), 100)
                timeout = int(input("Timeout seconds (default 2): ") or 2)
                
                working = fast_random_scan(server, num, 1000, 65535, threads, timeout)
                
                if working:
                    save_results(working, server, f"Random Scan ({num} ports)")
                else:
                    print_colored("\n❌ No working ports found.", Colors.RED)
                
                input("\nPress Enter to continue...")
                
            except ValueError:
                print_colored("❌ Invalid input!", Colors.RED)
                time.sleep(1)
        
        elif choice == "3":
            try:
                start = int(input("Start port (default 29000): ") or 29000)
                end = int(input("End port (default 33000): ") or 33000)
                step = int(input("step (default 1): ") or 1)
                threads = min(int(input("Number of threads (default 20): ") or 20), 100)
                timeout = int(input("Timeout seconds (default 2): ") or 2)
                
                # Validate range
                if start > end:
                    print_colored("❌ Start port must be less than end port!", Colors.RED)
                    time.sleep(1)
                    continue
                
                if end - start > 10000:
                    print_colored("⚠️ Large range detected! This may take a while.", Colors.YELLOW)
                    confirm = input("Continue? (y/n): ")
                    if confirm.lower() != 'y':
                        continue
                
                working = fast_sequential_scan(server, start, end,step, threads, timeout)
                
                if working:
                    save_results(working, server, f"Sequential Scan ({start}-{end})")
                else:
                    print_colored(f"\n❌ No working ports found in range {start}-{end}", Colors.RED)
                
                input("\nPress Enter to continue...")
                
            except ValueError:
                print_colored("❌ Invalid input!", Colors.RED)
                time.sleep(1)
        
        elif choice == "4":
            try:
                port = int(input("Port to test: "))
                timeout = int(input("Timeout seconds (default 3): ") or 3)
                
                print_colored(f"\n🔍 Testing port {port}...", Colors.CYAN)
                success, message = test_socks5_proxy(server, port, timeout)
                
                if success:
                    print_colored(f"✅ Port {port} is WORKING!", Colors.GREEN)
                    save_port = input("Save this port? (y/n): ").lower()
                    if save_port == 'y':
                        save_results([port], server, f"Single Port Test ({port})")
                else:
                    print_colored(f"❌ Port {port} is NOT working - {message}", Colors.RED)
                
                input("\nPress Enter to continue...")
                
            except ValueError:
                print_colored("❌ Invalid input!", Colors.RED)
                time.sleep(1)
        
        elif choice == "5":
            continue
        
        else:
            print_colored("❌ Invalid choice!", Colors.RED)
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⚠️ Program interrupted by user", Colors.YELLOW)
        sys.exit(0)