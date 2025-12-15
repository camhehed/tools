#!/usr/bin/env python3
"""
IP Range Scanner
- ASN lookup to get IP ranges
- Top 1000 ports scanning
- Stealth mode (randomized, slow)
- Banner grabbing + service detection
- SSL certificate extraction
- HTTP title extraction
- SQLite storage with timestamps
- Progress tracking + auto-resume
"""

import socket
import ssl
import sqlite3
import json
import time
import random
import argparse
import struct
import ipaddress
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# --- CONFIG ---
CONFIG = {
    "threads": 5,  # Low for stealth
    "timeout": 3,
    "delay_min": 0.5,  # Stealth delays
    "delay_max": 2.0,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# Top 1000 ports (nmap default)
TOP_1000_PORTS = [
    1,3,4,6,7,9,13,17,19,20,21,22,23,24,25,26,30,32,33,37,42,43,49,53,70,79,80,81,82,83,84,85,88,89,90,99,100,
    106,109,110,111,113,119,125,135,139,143,144,146,161,163,179,199,211,212,222,254,255,256,259,264,280,301,306,
    311,340,366,389,406,407,416,417,425,427,443,444,445,458,464,465,481,497,500,512,513,514,515,524,541,543,544,
    545,548,554,555,563,587,593,616,617,625,631,636,646,648,666,667,668,683,687,691,700,705,711,714,720,722,726,
    749,765,777,783,787,800,801,808,843,873,880,888,898,900,901,902,903,911,912,981,987,990,992,993,995,999,1000,
    1001,1002,1007,1009,1010,1011,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,
    1037,1038,1039,1040,1041,1042,1043,1044,1045,1046,1047,1048,1049,1050,1051,1052,1053,1054,1055,1056,1057,1058,
    1059,1060,1061,1062,1063,1064,1065,1066,1067,1068,1069,1070,1071,1072,1073,1074,1075,1076,1077,1078,1079,1080,
    1081,1082,1083,1084,1085,1086,1087,1088,1089,1090,1091,1092,1093,1094,1095,1096,1097,1098,1099,1100,1102,1104,
    1105,1106,1107,1108,1110,1111,1112,1113,1114,1117,1119,1121,1122,1123,1124,1126,1130,1131,1132,1137,1138,1141,
    1145,1147,1148,1149,1151,1152,1154,1163,1164,1165,1166,1169,1174,1175,1183,1185,1186,1187,1192,1198,1199,1201,
    1213,1216,1217,1218,1233,1234,1236,1244,1247,1248,1259,1271,1272,1277,1287,1296,1300,1301,1309,1310,1311,1322,
    1328,1334,1352,1417,1433,1434,1443,1455,1461,1494,1500,1501,1503,1521,1524,1533,1556,1580,1583,1594,1600,1641,
    1658,1666,1687,1688,1700,1717,1718,1719,1720,1721,1723,1755,1761,1782,1783,1801,1805,1812,1839,1840,1862,1863,
    1864,1875,1900,1914,1935,1947,1971,1972,1974,1984,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,
    2010,2013,2020,2021,2022,2030,2033,2034,2035,2038,2040,2041,2042,2043,2045,2046,2047,2048,2049,2065,2068,2099,
    2100,2103,2105,2106,2107,2111,2119,2121,2126,2135,2144,2160,2161,2170,2179,2190,2191,2196,2200,2222,2251,2260,
    2288,2301,2323,2366,2381,2382,2383,2393,2394,2399,2401,2492,2500,2522,2525,2557,2601,2602,2604,2605,2607,2608,
    2638,2701,2702,2710,2717,2718,2725,2800,2809,2811,2869,2875,2909,2910,2920,2967,2968,2998,3000,3001,3003,3005,
    3006,3007,3011,3013,3017,3030,3031,3052,3071,3077,3128,3168,3211,3221,3260,3261,3268,3269,3283,3300,3301,3306,
    3322,3323,3324,3325,3333,3351,3367,3369,3370,3371,3372,3389,3390,3404,3476,3493,3517,3527,3546,3551,3580,3659,
    3689,3690,3703,3737,3766,3784,3800,3801,3809,3814,3826,3827,3828,3851,3869,3871,3878,3880,3889,3905,3914,3918,
    3920,3945,3971,3986,3995,3998,4000,4001,4002,4003,4004,4005,4006,4045,4111,4125,4126,4129,4224,4242,4279,4321,
    4343,4443,4444,4445,4446,4449,4550,4567,4662,4848,4899,4900,4998,5000,5001,5002,5003,5004,5009,5030,5033,5050,
    5051,5054,5060,5061,5080,5087,5100,5101,5102,5120,5190,5200,5214,5221,5222,5225,5226,5269,5280,5298,5357,5405,
    5414,5431,5432,5440,5500,5510,5544,5550,5555,5560,5566,5631,5633,5666,5678,5679,5718,5730,5800,5801,5802,5810,
    5811,5815,5822,5825,5850,5859,5862,5877,5900,5901,5902,5903,5904,5906,5907,5910,5911,5915,5922,5925,5950,5952,
    5959,5960,5961,5962,5963,5987,5988,5989,5998,5999,6000,6001,6002,6003,6004,6005,6006,6007,6009,6025,6059,6100,
    6101,6106,6112,6123,6129,6156,6346,6389,6502,6510,6543,6547,6565,6566,6567,6580,6646,6666,6667,6668,6669,6689,
    6692,6699,6779,6788,6789,6792,6839,6881,6901,6969,7000,7001,7002,7004,7007,7019,7025,7070,7100,7103,7106,7200,
    7201,7402,7435,7443,7496,7512,7625,7627,7676,7741,7777,7778,7800,7911,7920,7921,7937,7938,7999,8000,8001,8002,
    8007,8008,8009,8010,8011,8021,8022,8031,8042,8045,8080,8081,8082,8083,8084,8085,8086,8087,8088,8089,8090,8093,
    8099,8100,8180,8181,8192,8193,8194,8200,8222,8254,8290,8291,8292,8300,8333,8383,8400,8402,8443,8500,8600,8649,
    8651,8652,8654,8701,8800,8873,8888,8899,8994,9000,9001,9002,9003,9009,9010,9011,9040,9050,9071,9080,9081,9090,
    9091,9099,9100,9101,9102,9103,9110,9111,9200,9207,9220,9290,9415,9418,9485,9500,9502,9503,9535,9575,9593,9594,
    9595,9618,9666,9876,9877,9878,9898,9900,9917,9929,9943,9944,9968,9998,9999,10000,10001,10002,10003,10004,10009,
    10010,10012,10024,10025,10082,10180,10215,10243,10566,10616,10617,10621,10626,10628,10629,10778,11110,11111,
    11967,12000,12174,12265,12345,13456,13722,13782,13783,14000,14238,14441,14442,15000,15002,15003,15004,15660,
    15742,16000,16001,16012,16016,16018,16080,16113,16992,16993,17877,17988,18040,18101,18988,19101,19283,19315,
    19350,19780,19801,19842,20000,20005,20031,20221,20222,20828,21571,22939,23502,24444,24800,25734,25735,26214,
    27000,27352,27353,27355,27356,27715,28201,30000,30718,30951,31038,31337,32768,32769,32770,32771,32772,32773,
    32774,32775,32776,32777,32778,32779,32780,32781,32782,32783,32784,32785,33354,33899,34571,34572,34573,35500,
    38292,40193,40911,41511,42510,44176,44442,44443,44501,45100,48080,49152,49153,49154,49155,49156,49157,49158,
    49159,49160,49161,49163,49165,49167,49175,49176,49400,49999,50000,50001,50002,50003,50006,50300,50389,50500,
    50636,50800,51103,51493,52673,52822,52848,52869,54045,54328,55055,55056,55555,55600,56737,56738,57294,57797,
    58080,60020,60443,61532,61900,62078,63331,64623,64680,65000,65129,65389
]

# Service detection patterns
SERVICE_PATTERNS = {
    b"SSH-": "SSH",
    b"220": "FTP/SMTP",
    b"HTTP/": "HTTP",
    b"* OK": "IMAP",
    b"+OK": "POP3",
    b"MySQL": "MySQL",
    b"PostgreSQL": "PostgreSQL",
    b"mongo": "MongoDB",
    b"redis": "Redis",
    b"<?xml": "XML Service",
    b"<html": "HTTP",
    b"SMB": "SMB",
    b"RFB": "VNC",
}


class IPScanner:
    def __init__(self, db_path="ip_scan_results.db"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY,
                ip TEXT,
                port INTEGER,
                state TEXT,
                service TEXT,
                banner TEXT,
                ssl_cn TEXT,
                ssl_issuer TEXT,
                ssl_san TEXT,
                http_title TEXT,
                scanned_at TEXT,
                UNIQUE(ip, port)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                range_id TEXT PRIMARY KEY,
                current_ip TEXT,
                completed INTEGER
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_ip ON scan_results(ip)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_port ON scan_results(port)')
        conn.commit()
        conn.close()

    def save_result(self, ip, port, state, service=None, banner=None, 
                    ssl_cn=None, ssl_issuer=None, ssl_san=None, http_title=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT OR REPLACE INTO scan_results 
                (ip, port, state, service, banner, ssl_cn, ssl_issuer, ssl_san, http_title, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ip, port, state, service, banner, ssl_cn, ssl_issuer, ssl_san, http_title, 
                  datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()

    def get_progress(self, range_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT current_ip, completed FROM progress WHERE range_id = ?', (range_id,))
        row = c.fetchone()
        conn.close()
        return row if row else (None, 0)

    def save_progress(self, range_id, current_ip, completed=0):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO progress (range_id, current_ip, completed) VALUES (?, ?, ?)',
                  (range_id, current_ip, completed))
        conn.commit()
        conn.close()

    def get_asn_ranges(self, asn):
        """Get IP ranges for an ASN"""
        print(f"\n[*] Looking up ASN {asn}...")
        ranges = []
        try:
            # Try bgpview API
            url = f"https://api.bgpview.io/asn/{asn}/prefixes"
            resp = requests.get(url, timeout=30, headers={"User-Agent": CONFIG["user_agent"]})
            if resp.status_code == 200:
                data = resp.json()
                for prefix in data.get("data", {}).get("ipv4_prefixes", []):
                    ranges.append(prefix["prefix"])
                print(f"    [+] Found {len(ranges)} IPv4 ranges for AS{asn}")
        except Exception as e:
            print(f"    [-] ASN lookup error: {e}")
        return ranges

    def grab_banner(self, ip, port):
        """Grab service banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CONFIG["timeout"])
            sock.connect((ip, port))
            
            # Send probe for HTTP
            if port in [80, 8080, 8000, 8888, 8008]:
                sock.send(b"GET / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n")
            elif port in [443, 8443, 4443]:
                return None  # Handle SSL separately
            else:
                sock.send(b"\r\n")
            
            banner = sock.recv(1024)
            sock.close()
            return banner
        except:
            return None

    def detect_service(self, banner):
        """Detect service from banner"""
        if not banner:
            return None
        for pattern, service in SERVICE_PATTERNS.items():
            if pattern in banner:
                return service
        return "Unknown"

    def get_ssl_info(self, ip, port):
        """Extract SSL certificate information"""
        result = {"cn": None, "issuer": None, "san": []}
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((ip, port), timeout=CONFIG["timeout"]) as sock:
                with context.wrap_socket(sock, server_hostname=ip) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    
                    # Parse certificate
                    import ssl as ssl_module
                    cert_dict = ssl_module._ssl._test_decode_cert(cert) if hasattr(ssl_module._ssl, '_test_decode_cert') else {}
                    
                    # Try alternate method
                    try:
                        from cryptography import x509
                        from cryptography.hazmat.backends import default_backend
                        cert_obj = x509.load_der_x509_certificate(cert, default_backend())
                        result["cn"] = cert_obj.subject.rfc4514_string()
                        result["issuer"] = cert_obj.issuer.rfc4514_string()
                        try:
                            san = cert_obj.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                            result["san"] = [name.value for name in san.value]
                        except:
                            pass
                    except ImportError:
                        # Fallback without cryptography
                        pass
        except:
            pass
        return result

    def get_http_title(self, ip, port, use_ssl=False):
        """Extract HTTP page title"""
        try:
            proto = "https" if use_ssl else "http"
            resp = requests.get(
                f"{proto}://{ip}:{port}",
                timeout=CONFIG["timeout"],
                headers={"User-Agent": CONFIG["user_agent"]},
                verify=False,
                allow_redirects=True
            )
            # Extract title
            import re
            match = re.search(r'<title[^>]*>([^<]+)</title>', resp.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:200]
        except:
            pass
        return None

    def scan_port(self, ip, port):
        """Scan a single port with stealth delay"""
        time.sleep(random.uniform(CONFIG["delay_min"], CONFIG["delay_max"]))
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CONFIG["timeout"])
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                # Port is open, gather info
                banner = None
                service = None
                ssl_info = {"cn": None, "issuer": None, "san": []}
                http_title = None
                
                # SSL ports
                if port in [443, 8443, 4443, 993, 995, 465, 636]:
                    ssl_info = self.get_ssl_info(ip, port)
                    if port in [443, 8443, 4443]:
                        http_title = self.get_http_title(ip, port, use_ssl=True)
                        service = "HTTPS"
                else:
                    banner = self.grab_banner(ip, port)
                    service = self.detect_service(banner)
                    if port in [80, 8080, 8000, 8888, 8008]:
                        http_title = self.get_http_title(ip, port, use_ssl=False)
                        service = "HTTP"
                
                banner_str = banner.decode('utf-8', errors='ignore')[:500] if banner else None
                san_str = ",".join(ssl_info["san"][:10]) if ssl_info["san"] else None
                
                self.save_result(
                    ip=ip, port=port, state="open", service=service,
                    banner=banner_str, ssl_cn=ssl_info["cn"],
                    ssl_issuer=ssl_info["issuer"], ssl_san=san_str,
                    http_title=http_title
                )
                return {"port": port, "state": "open", "service": service, "ssl_cn": ssl_info["cn"]}
        except:
            pass
        return None

    def print_progress(self, current, total, open_ports, current_ip):
        """Print progress bar"""
        pct = current / total if total > 0 else 0
        bar_len = 40
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r[{bar}] {pct*100:.1f}% | IP: {current_ip} | Open: {open_ports}", end="", flush=True)

    def scan_range(self, cidr, ports=None):
        """Scan an IP range"""
        if ports is None:
            ports = TOP_1000_PORTS
            
        network = ipaddress.ip_network(cidr, strict=False)
        ips = list(network.hosts())
        total_scans = len(ips) * len(ports)
        
        range_id = cidr.replace("/", "_")
        resume_ip, completed = self.get_progress(range_id)
        
        # Find resume point
        start_idx = 0
        if resume_ip and not completed:
            try:
                start_idx = next(i for i, ip in enumerate(ips) if str(ip) == resume_ip)
                print(f"[*] Resuming from {resume_ip}")
            except StopIteration:
                pass
        
        print(f"\n{'='*60}")
        print(f"  Scanning: {cidr}")
        print(f"  IPs: {len(ips)} | Ports: {len(ports)} | Total: {total_scans}")
        print(f"  Mode: Stealth (delay {CONFIG['delay_min']}-{CONFIG['delay_max']}s)")
        print(f"{'='*60}\n")
        
        open_count = 0
        scans_done = start_idx * len(ports)
        
        # Randomize port order for each IP (stealth)
        for ip_idx, ip in enumerate(ips[start_idx:], start=start_idx):
            ip_str = str(ip)
            shuffled_ports = ports.copy()
            random.shuffle(shuffled_ports)
            
            for port in shuffled_ports:
                result = self.scan_port(ip_str, port)
                if result:
                    open_count += 1
                    ssl_info = f" | CN: {result['ssl_cn']}" if result.get('ssl_cn') else ""
                    print(f"\n    [+] {ip_str}:{result['port']} - {result['service']}{ssl_info}")
                
                scans_done += 1
                self.print_progress(scans_done, total_scans, open_count, ip_str)
            
            self.save_progress(range_id, ip_str)
        
        self.save_progress(range_id, str(ips[-1]) if ips else "", completed=1)
        
        print(f"\n\n{'='*60}")
        print(f"  Completed: {cidr}")
        print(f"  Open ports found: {open_count}")
        print(f"  Results saved to: {self.db_path}")
        print(f"{'='*60}\n")
        
        return open_count


def main():
    parser = argparse.ArgumentParser(description="IP Range Scanner")
    parser.add_argument("-r", "--range", help="CIDR range (e.g., 192.168.1.0/24)")
    parser.add_argument("-l", "--list", help="File containing CIDR ranges")
    parser.add_argument("-a", "--asn", help="ASN number to scan (e.g., 15169)")
    parser.add_argument("-o", "--output", default="ip_scan_results.db", help="SQLite database path")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Threads (keep low for stealth)")
    parser.add_argument("--fast", action="store_true", help="Disable stealth delays")
    args = parser.parse_args()
    
    if not args.range and not args.list and not args.asn:
        parser.error("Provide -r range, -l range_list, or -a asn")
    
    CONFIG["threads"] = args.threads
    if args.fast:
        CONFIG["delay_min"] = 0
        CONFIG["delay_max"] = 0
    
    scanner = IPScanner(args.output)
    ranges = []
    
    if args.asn:
        ranges.extend(scanner.get_asn_ranges(args.asn.replace("AS", "").replace("as", "")))
    if args.range:
        ranges.append(args.range)
    if args.list:
        with open(args.list) as f:
            ranges.extend([line.strip() for line in f if line.strip()])
    
    total_open = 0
    for cidr in ranges:
        try:
            total_open += scanner.scan_range(cidr)
        except KeyboardInterrupt:
            print("\n[!] Interrupted - progress saved")
            break
        except Exception as e:
            print(f"\n[-] Error scanning {cidr}: {e}")
            continue
    
    print(f"\n[*] Grand total open ports: {total_open}")


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
