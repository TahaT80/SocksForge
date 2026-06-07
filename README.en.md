<div align="center">

```
   _____            __        ______                     
  / ___/____  _____/ /_____  / ____/___  ____  __________
  \__ \/ __ \/ ___/ //_/ _ \/ /_  / __ \/ __ \/ ___/ ___/
 ___/ / /_/ / /__/ ,< /  __/ __/ / /_/ / /_/ / /  (__  ) 
/____/ .___/\___/_/|_|\___/_/    \____/\____/_/  /____/  
    /_/                                                  
```

### Fast • Multi-threaded • No Dependencies Beyond the Standard Library

A unified toolkit for **discovering SOCKS5 proxies** and **validating CDN-fronted IPs** for TLS tunnels.
Built for researchers, network engineers, and anyone who needs to find working proxy servers at scale.

[Features](#-features) • [Tools](#-tools) • [Installation](#-installation) • [Usage](#-usage) • [Output](#-output-format) • [Disclaimer](#-disclaimer)

> 🇮🇷 **[نسخهٔ فارسی](./README.md)** موجود است.

</div>

---

## ✨ Features

- 🔥 **Blazing-fast scanning** — multi-threaded engine with adaptive rate-limiting (up to ~500 req/s)
- 🎯 **5 scan modes** — specific range, random prioritised ranges, fast single-port, from-file, full port sweep
- 🇮🇷 **Iran-priority IP generator** — focuses on residential and ISP ranges known to host working SOCKS5 endpoints
- 🛡️ **CDN Fronting tester** — verifies IPs that work with a given SNI for TLS-based tunnels (v2ray, fragment, etc.)
- 📊 **Quality scoring** — every found proxy is benchmarked for response time, throughput, and reliability
- 💾 **Auto-save** — results are timestamped and dropped into the `result/` folder, plus ready-to-use `t.me/socks?…` deep links for Telegram
- 🎨 **Coloured terminal UI** — clear progress bars, live speed, and live hit counter
- 🪶 **Lightweight** — `IP&PROXY FINDER.py` and `cdn_tester.py` use **only the Python standard library**

---

## 🧰 Tools

This repository ships **three independent CLI tools** you can run separately or together.

| Script | Purpose | External deps |
| --- | --- | --- |
| `IP&PROXY FINDER.py` | SOCKS5 proxy scanner with 5 scan modes and live progress | **None** (stdlib only) |
| `Find port from IP.py` | Port-finder + quality benchmark (latency / speed / reliability) | `requests` |
| `cdn_tester.py` | CDN-fronting / SNI-spoofing IP validator (TLS handshake on port 443) | **None** (stdlib only) |

---

## 📦 Installation

Requirements: **Python 3.8+**

```bash
git clone https://github.com/<your-username>/SocksForge.git
cd SocksForge
```

Optional — only needed for the port-finder quality benchmark:

```bash
pip install requests
```

> 💡 Two of the three tools work out of the box on any fresh Python install.

---

## 🚀 Usage

### 1. SOCKS5 Proxy Finder (main tool)

```bash
python "IP&PROXY FINDER.py"
```

Interactive menu:

```
SELECT SCAN MODE:
  1. SCAN SPECIFIC RANGE (e.g., 62.220.126.x)
  2. RANDOM SCAN (priority to known working ranges)
  3. FAST PORT SCAN (check only port 29678 - very fast)
  4. SCAN FROM FILE (load IP list from text file)
  5. SCAN ALL PORTS (1080, 31405, 32193, 9050, etc.)
  0. EXIT
```

| Mode | Use it when… |
| --- | --- |
| **1 – Specific range** | You have a known IP prefix (e.g. `62.220.126`) and want to enumerate it |
| **2 – Random scan** | You want to discover new proxies across prioritised ISP ranges |
| **3 – Fast port** | You only need to test a single high-yield port (e.g. `29678`) on thousands of IPs |
| **4 – From file** | You already have a list of candidate IPs in `ips.txt` |
| **5 – All ports** | Full sweep across common SOCKS ports (1080, 9050, 31405, 32193, …) |

You will be asked for two parameters:

```
Threads  (10-50, default 20)
Timeout  (1-3  seconds, default 2)
```

### 2. Port Finder + Quality Benchmark

```bash
python "Find port from IP.py"
```

For every IP, it tries a list of candidate ports, runs the full SOCKS5 handshake, then **scores** each working proxy on:

- ⏱️  response time (ms)
- 🚀  download speed (Mbps)
- 🎯  reliability (3 consecutive HTTP requests)

Best candidates are written to `result/`.

### 3. CDN Fronting Tester

```bash
python cdn_tester.py
```

Reads IPs from `ips.txt` and checks which ones successfully complete a TLS handshake with a target SNI (default `www.hcaptcha.com`). Useful for:

- v2ray / Xray TLS tunnels
- fragment-based anti-censorship tools
- SNI-spoofing configurations

Tweak the constants at the top of the file:

```python
TARGET_SNI = "www.hcaptcha.com"   # the SNI you want to spoof
TIMEOUT    = 5                    # seconds
THREADS    = 50                   # concurrent workers
TEST_PORT  = 443                  # TLS port
```

---

## 📁 Output Format

Every scan writes a timestamped file into `result/`:

```
result/Find IP_20260107_224512.txt
```

Example content:

```
# IP Finder 
# Scan Date: 2026-01-07 22:45:12
##################################################

62.220.126.92
185.146.43.18
...

##################################################

https://t.me/socks?server=62.220.126.92&port=31405
https://t.me/socks?server=185.146.43.18&port=1080
...
```

The first block contains the **raw IPs**, the second block contains **ready-to-use Telegram deep-links**. Open them on a phone with Telegram installed to import the proxy in one tap.

---

## ⚙️ How it works

```
┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  IP source   │ -> │  TCP port probe  │ -> │ SOCKS5 handshake│
│  (range /    │    │  (connect_ex)    │    │  (RFC 1928)     │
│   file /     │    └──────────────────┘    └────────┬────────┘
│   random)    │                                      │
└──────────────┘                                      v
                                            ┌─────────────────┐
                                            │  Quality score  │
                                            │ (optional, tool │
                                            │   #2 only)      │
                                            └─────────────────┘
```

The SOCKS5 handshake performs a `CONNECT 8.8.8.8:53` request — a robust, DNS-independent liveness check that is valid on every IPv4 host.

---

## 🗂️ Project structure

```
SocksForge/
├── IP&PROXY FINDER.py     # main SOCKS5 scanner (stdlib only)
├── Find port from IP.py   # port scanner + quality benchmark
├── cdn_tester.py          # CDN-fronting / SNI-spoofing tester
├── ips.txt                # candidate IP list (one per line)
├── result/                # auto-created; scan outputs land here
├── README.md              # Persian documentation
└── README.en.md           # English documentation
```

---

## 🛠️ Tips for better hit-rates

- 🕐 Run scans at **off-peak hours** (e.g. 02:00 – 06:00 local time of the target range)
- 🌍 Combine **mode 2 (random)** with a wide count (10k–20k) for best discovery
- 🎯 For a known-good range, prefer **mode 1** with a custom port range
- 🧪 Always cross-check found proxies with **mode 2 of `Find port from IP.py`** — a fast port hit is not the same as a *stable* proxy
- 🚫 Avoid `172.16.x.x` and `10.x.x.x` — the generator already filters these reserved ranges

---

## 🧪 Tested on

- Windows 10 / 11
- Ubuntu 22.04
- macOS 13 (Ventura)

Python 3.8 – 3.12.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Ideas for contributions:

- Async (`asyncio` + `aiohttp`) port of the scanner
- Support for SOCKS4 and HTTP CONNECT proxies
- GeoIP-aware range prioritisation
- Web dashboard for live results

---

## ⚠️ Disclaimer

This project is provided **for educational and research purposes only**.

- Scanning hosts you do not own or have explicit permission to test **may be illegal** in your jurisdiction.
- The author(s) do not condone using this tool to violate any law, terms of service, or third-party rights.
- The CDN-fronting tester is intended for legitimate anti-censorship research. Respect the terms of every CDN you interact with.
- **You are solely responsible for your use of this software.**

By downloading, cloning, or running any script in this repository, you accept full responsibility for complying with all applicable laws.

---

## 📜 License

MIT — see `LICENSE` (add one if you plan to publish).

---

<div align="center">
Made with 🛠️ + ☕ — happy hunting.
</div>
