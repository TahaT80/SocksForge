#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDN Fronting Tester - Find working IPs for TLS Tunnels
Compatible with SNI-Spoofing project config format
"""

import socket
import ssl
import sys
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ========== CONFIGURATION ==========
TARGET_SNI = "www.hcaptcha.com"  # The SNI that must work
TIMEOUT = 5  # Connection timeout in seconds
THREADS = 50  # Number of concurrent threads
MAX_RESULTS = 100  # Maximum IPs to save
TEST_PORT = 443  # HTTPS port

# ========== COLORS FOR OUTPUT ==========
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_color(text, color='OKGREEN'):
    print(f"{getattr(Colors, color.upper(), Colors.OKGREEN)}{text}{Colors.ENDC}")

# ========== TEST FUNCTION ==========
def test_ip(ip, sni, timeout=TIMEOUT):
    """
    Test if an IP works with given SNI
    Returns: (ip, success, status_code, response_ms, error)
    """
    start_time = time.time()
    
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Connect to IP
        sock.connect((ip, TEST_PORT))
        
        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # SSL handshake with SNI
        ssock = context.wrap_socket(sock, server_hostname=sni)
        
        # Send HTTP request
        request = f"GET / HTTP/1.1\r\nHost: {sni}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
        ssock.sendall(request.encode())
        
        # Get response
        response = ssock.recv(4096)
        ssock.close()
        
        response_time = (time.time() - start_time) * 1000
        
        # Parse HTTP response
        response_str = response.decode('utf-8', errors='ignore')
        
        # Extract status code
        status_code = 0
        if 'HTTP/' in response_str:
            try:
                status_code_line = response_str.split('\r\n')[0]
                status_code = int(status_code_line.split(' ')[1])
            except:
                pass
        
        # Success codes: 200, 301, 302, 403, 404 are all acceptable
        if status_code in [200, 301, 302, 403, 404, 406]:
            return (ip, True, status_code, response_time, None)
        else:
            return (ip, False, status_code, response_time, f"HTTP {status_code}")
            
    except socket.timeout:
        return (ip, False, 0, timeout*1000, "Timeout")
    except socket.error as e:
        if "Connection refused" in str(e):
            return (ip, False, 0, 0, "Connection Refused")
        return (ip, False, 0, 0, f"Socket Error")
    except ssl.SSLError as e:
        if "wrong version number" in str(e).lower():
            return (ip, False, 0, 0, "Not SSL (port 443 not SSL)")
        elif "certificate verify failed" in str(e).lower():
            return (ip, True, 403, 0, "SSL Cert Error")  # Still works for spoofing
        return (ip, False, 0, 0, f"SSL Error")
    except Exception as e:
        return (ip, False, 0, 0, f"Error: {str(e)[:30]}")

# ========== LOAD IPS FROM FILE ==========
def load_ips_from_file(filepath):
    """Load and validate IPs from file"""
    ips = []
    invalid_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Handle different formats
                if ',' in line:
                    parts = line.split(',')
                else:
                    parts = line.split()
                
                for part in parts:
                    # Clean the IP
                    ip = part.strip().strip('"').strip("'")
                    
                    # Validate IP format
                    ip_parts = ip.split('.')
                    if len(ip_parts) == 4:
                        try:
                            octets = [int(x) for x in ip_parts]
                            if all(0 <= x <= 255 for x in octets):
                                if ip not in ips:  # Remove duplicates
                                    ips.append(ip)
                            else:
                                invalid_count += 1
                        except ValueError:
                            invalid_count += 1
                    else:
                        invalid_count += 1
                        
    except FileNotFoundError:
        print_color(f"\n[ERROR] File {filepath} not found!", 'FAIL')
        return []
    except Exception as e:
        print_color(f"\n[ERROR] Reading file: {e}", 'FAIL')
        return []
    
    print_color(f"\n[STATS] Loaded {len(ips)} valid unique IPs", 'OKCYAN')
    if invalid_count > 0:
        print(f"       Skipped {invalid_count} invalid entries")
    
    return ips

# ========== SAVE RESULTS ==========
def save_results(working_ips, results_detail, target_sni):
    """Save results in multiple formats"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create results directory
    os.makedirs("result", exist_ok=True)
    
    # Save as JSON config (compatible with SNI-Spoofing)
    json_file = os.path.join("result", f"config_{timestamp}.json")
    configs = []
    
    for ip in working_ips[:MAX_RESULTS]:
        config = {
            "LISTEN_HOST": "0.0.0.0",
            "LISTEN_PORT": 40443,
            "CONNECT_IP": ip,
            "CONNECT_PORT": 443,
            "FAKE_SNI": target_sni
        }
        configs.append(config)
    
    # Write JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        if len(configs) == 1:
            json.dump(configs[0], f, indent=2, ensure_ascii=False)
        else:
            json.dump(configs, f, indent=2, ensure_ascii=False)
    
    # Save as simple IP list
    ips_file = os.path.join("result", f"working_ips_{timestamp}.txt")
    with open(ips_file, 'w', encoding='utf-8') as f:
        f.write(f"# Working IPs for SNI: {target_sni}\n")
        f.write(f"# Date: {datetime.now()}\n")
        f.write(f"# Total: {len(working_ips)}\n\n")
        for ip in working_ips:
            f.write(f"{ip}\n")
    
    # Save as config lines for easy copy/paste
    config_lines_file = os.path.join("result", f"config_lines_{timestamp}.txt")
    with open(config_lines_file, 'w', encoding='utf-8') as f:
        for ip in working_ips[:MAX_RESULTS]:
            f.write(f'{{"LISTEN_HOST":"0.0.0.0","LISTEN_PORT":40443,"CONNECT_IP":"{ip}","CONNECT_PORT":443,"FAKE_SNI":"{target_sni}"}}\n')
    
    # Create ready-to-use config for SNI-Spoofing
    ready_config = os.path.join("result", "READY_TO_USE_CONFIG.json")
    if working_ips:
        with open(ready_config, 'w', encoding='utf-8') as f:
            best_ip = working_ips[0]
            json.dump({
                "LISTEN_HOST": "0.0.0.0",
                "LISTEN_PORT": 40443,
                "CONNECT_IP": best_ip,
                "CONNECT_PORT": 443,
                "FAKE_SNI": target_sni
            }, f, indent=2, ensure_ascii=False)
    
    return json_file, ips_file, config_lines_file

# ========== MAIN FUNCTION ==========
def main():
    print_color("=" * 70, 'HEADER')
    print_color("     🔥 CDN FRONTING TESTER - Working IP Finder 🔥", 'OKGREEN')
    print_color("     Find IPs that work with your SNI configuration", 'OKGREEN')
    print_color("=" * 70, 'HEADER')
    
    print_color(f"\n[TARGET] SNI: {TARGET_SNI}", 'OKCYAN')
    print_color(f"[SETUP] Timeout: {TIMEOUT}s, Threads: {THREADS}", 'OKCYAN')
    
    # Get IP file path
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        print("\n[USAGE]")
        print(f"   python3 {sys.argv[0]} <ip_list_file>")
        print("\n[EXAMPLE]")
        print(f"   python3 {sys.argv[0]} ips.txt")
        print()
        filepath = input("[INPUT] Enter IP file path: ").strip()
    
    # Load IPs
    print_color(f"\n[LOADING] Reading IPs from {filepath}...", 'OKBLUE')
    ips = load_ips_from_file(filepath)
    
    if not ips:
        print_color("\n[ERROR] No valid IPs found!", 'FAIL')
        print_color("\n[TIPS]", 'WARNING')
        print("   1. Use Akamai IP range (2.16.0.0 to 2.23.255.255)")
        print("   2. Put one IP per line in the file")
        print("   3. Save file as UTF-8 format")
        return
    
    print_color(f"\n[TESTING] {len(ips)} IPs with SNI: {TARGET_SNI}", 'OKGREEN')
    print_color(f"[PROGRESS] Starting with {THREADS} threads...\n", 'OKBLUE')
    
    # Start testing
    results = []
    working_ips = []
    start_time = time.time()
    completed = 0
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(test_ip, ip, TARGET_SNI): ip for ip in ips}
        
        for future in as_completed(futures):
            completed += 1
            ip, success, status_code, response_time, error = future.result()
            
            # Show progress
            if completed % 50 == 0 or completed == len(ips):
                percent = (completed / len(ips)) * 100
                print(f"\r[PROGRESS] {completed}/{len(ips)} ({percent:.1f}%)", end="", flush=True)
            
            if success:
                working_ips.append(ip)
                results.append((ip, True, status_code, response_time))
                # Show successful IP immediately
                print(f"\r[WORKING] ✅ {ip:15} | Status: {status_code} | Time: {response_time:.0f}ms    ")
            else:
                results.append((ip, False, status_code, 0))
    
    total_time = time.time() - start_time
    
    # Remove duplicates (if any)
    working_ips = list(dict.fromkeys(working_ips))
    
    # Show final results
    print("\n")
    print_color("=" * 70, 'OKCYAN')
    print_color("[FINAL RESULTS]", 'OKGREEN')
    print_color("=" * 70, 'OKCYAN')
    
    print(f"\n[SUCCESS] Working IPs found: {len(working_ips)}")
    print(f"[RATE] Success rate: {(len(working_ips)/len(ips))*100:.1f}%")
    print(f"[TIME] Total test time: {total_time:.1f} seconds")
    
    if working_ips:
        # Sort by response time (fastest first)
        ip_time_map = {}
        for ip, success, status, rtime in results:
            if success and ip not in ip_time_map:
                ip_time_map[ip] = rtime
        
        working_ips_sorted = sorted(ip_time_map.items(), key=lambda x: x[1])
        working_ips = [ip for ip, _ in working_ips_sorted]
        
        # Show top 20 IPs
        print_color("\n[TOP 20 IPS] (Fastest first):", 'OKGREEN')
        print("-" * 70)
        print(f"{'#':<6} {'IP':<18} {'Response Time':<12} {'Quality':<10}")
        print("-" * 70)
        
        for i, (ip, rtime) in enumerate(working_ips_sorted[:20], 1):
            if rtime < 150:
                quality = "🚀 Excellent"
            elif rtime < 300:
                quality = "⚡ Good"
            else:
                quality = "📡 Acceptable"
            print(f"{i:<6} {ip:<18} {rtime:<12.0f}ms {quality}")
        
        # Show IPs ready for copy/paste
        print_color("\n" + "=" * 70, 'OKGREEN')
        print_color("[COPY THESE IPs] For your CONNECT_IP field:", 'OKGREEN')
        print_color("=" * 70, 'OKGREEN')
        print("\n" + " ".join(working_ips[:50]))
        
        # Show sample config
        print_color("\n" + "=" * 70, 'OKCYAN')
        print_color("[SAMPLE CONFIG] For SNI-Spoofing project:", 'OKCYAN')
        print_color("=" * 70, 'OKCYAN')
        
        if working_ips:
            sample_config = {
                "LISTEN_HOST": "0.0.0.0",
                "LISTEN_PORT": 40443,
                "CONNECT_IP": working_ips[0],
                "CONNECT_PORT": 443,
                "FAKE_SNI": TARGET_SNI
            }
            print(json.dumps(sample_config, indent=2))
        
        # Save files
        json_file, ips_file, config_lines_file = save_results(working_ips, results, TARGET_SNI)
        
        print_color(f"\n[SAVED] Files saved to 'result' folder:", 'OKYELLOW')
        print(f"   📁 JSON Config: {json_file}")
        print(f"   📁 IP List: {ips_file}")
        print(f"   📁 Config Lines: {config_lines_file}")
        
        # Instructions for SNI-Spoofing
        print_color("\n" + "=" * 70, 'OKGREEN')
        print_color("[HOW TO USE WITH SNI-SPOOFING]", 'OKGREEN')
        print_color("=" * 70, 'OKGREEN')
        print("1. Copy one of the IPs from above")
        print("2. Edit your config.json file:")
        print(f'   "CONNECT_IP": "YOUR_WORKING_IP",')
        print(f'   "FAKE_SNI": "{TARGET_SNI}"')
        print("3. Run: python3 main.py")
        
    else:
        print_color("\n[FAILED] No working IPs found!", 'FAIL')
        print_color("\n[TIPS TO FIX]", 'WARNING')
        print("   1. Get a larger IP list (5000+ IPs from Akamai range)")
        print("   2. Try a different SNI (e.g., www.google.com or www.cloudflare.com)")
        print("   3. Increase TIMEOUT value (line 19)")
        print("   4. Check your internet connection")
        print("   5. Make sure port 443 is not blocked")
    
    print_color("\n" + "=" * 70, 'OKCYAN')
    print_color("[DONE] Testing completed", 'OKGREEN')
    print_color("=" * 70, 'OKCYAN')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\n[STOPPED] Test interrupted by user.", 'WARNING')
        sys.exit(0)
    except Exception as e:
        print_color(f"\n[ERROR] {e}", 'FAIL')
        import traceback
        traceback.print_exc()
        sys.exit(1)