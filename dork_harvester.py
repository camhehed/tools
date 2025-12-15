#!/usr/bin/env python3
"""
Google Dork Harvester
- Built-in dork database (GHDB inspired)
- Single engine (slow, stealth)
- Download found files
- Auto-categorize results
- Screenshot pages
- CSV export with metadata
- CAPTCHA queue for manual solving
- Progress tracking + auto-resume
"""

import requests
import sqlite3
import json
import time
import random
import argparse
import hashlib
import re
import os
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup

# Optional for screenshots
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# --- CONFIG ---
CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "delay_min": 30,  # Very slow to avoid CAPTCHA
    "delay_max": 90,
    "results_per_query": 50,
    "download_dir": "dork_downloads",
    "screenshot_dir": "dork_screenshots",
    "captcha_queue": "captcha_queue.txt",
}

# Built-in dork database (GHDB inspired)
DORK_DATABASE = {
    "exposed_files": [
        'filetype:sql "insert into" password',
        'filetype:sql "create table" users',
        'filetype:log "password"',
        'filetype:log username password',
        'filetype:cfg password',
        'filetype:ini password',
        'filetype:env DB_PASSWORD',
        'filetype:env AWS_SECRET',
        'filetype:bak inurl:password',
        'filetype:old password',
        'filetype:txt "password" "username"',
        'filetype:xls password',
        'filetype:xlsx password',
        'filetype:csv password',
        'filetype:json "password"',
        'filetype:yaml password',
        'filetype:yml api_key',
        'filetype:conf password',
        'filetype:config password',
    ],
    "admin_panels": [
        'intitle:"admin login"',
        'intitle:"administrator login"',
        'inurl:admin inurl:login',
        'inurl:adminpanel',
        'inurl:admin/login.php',
        'inurl:admin/index.php',
        'inurl:administrator/index.php',
        'inurl:admincp',
        'inurl:wp-admin',
        'inurl:wp-login.php',
        'intitle:"dashboard" inurl:admin',
        'inurl:phpmyadmin',
        'inurl:cpanel',
        'inurl:webmail',
        'intitle:"control panel" login',
    ],
    "database_dumps": [
        'filetype:sql site:pastebin.com',
        'filetype:sql site:github.com',
        'filetype:sql intext:CREATE TABLE',
        'inurl:dump.sql',
        'inurl:database.sql',
        'inurl:backup.sql',
        'inurl:db.sql',
        'intitle:"index of" database.sql',
        'intitle:"index of" dump.sql',
        'intitle:"index of" *.sql',
    ],
    "sensitive_dirs": [
        'intitle:"index of" .git',
        'intitle:"index of" .svn',
        'intitle:"index of" .env',
        'intitle:"index of" backup',
        'intitle:"index of" config',
        'intitle:"index of" private',
        'intitle:"index of" secret',
        'intitle:"index of" passwords',
        'intitle:"index of" credentials',
        'intitle:"index of" /admin/',
        'intitle:"index of" /uploads/',
        'intitle:"index of" /data/',
        'intitle:"index of" wp-content/uploads',
    ],
    "vulnerable_servers": [
        'inurl:/phpinfo.php',
        'intitle:"PHP Version" "PHP Credits"',
        'inurl:server-status "Apache Server Status"',
        'inurl:server-info "Apache Server Information"',
        '"Welcome to nginx" intitle:welcome',
        'intitle:"Apache2 Ubuntu Default Page"',
        'intitle:"Test Page for Apache"',
        'inurl:elmah.axd "Error Log"',
        '"Index of /" +.htaccess',
        'inurl:web.config filetype:config',
    ],
    "api_keys": [
        'filetype:json "api_key"',
        'filetype:json "apikey"',
        'filetype:json "secret_key"',
        'filetype:env "API_KEY"',
        'filetype:yaml "api_key"',
        'site:github.com "API_KEY" filetype:env',
        'site:github.com "AWS_SECRET_ACCESS_KEY"',
        'site:github.com "PRIVATE_KEY"',
        '"AIza" filetype:json -site:google.com',  # Google API keys
        '"sk_live_" filetype:json',  # Stripe keys
        '"sq0atp-" OR "sq0csp-"',  # Square keys
    ],
    "cameras": [
        'inurl:/view/index.shtml',
        'intitle:"Live View / - AXIS"',
        'inurl:"/control/userimage.html"',
        'intitle:"IP CAMERA Viewer"',
        'inurl:"ViewerFrame?Mode="',
        'intitle:"webcamXP 5"',
        'inurl:"/view.shtml"',
        'intitle:"Network Camera"',
    ],
    "printers": [
        'intitle:"HP LaserJet" inurl:info_configuration.htm',
        'intitle:"Printer Status" inurl:hp',
        'inurl:"/hp/device/this.LCDispatcher"',
        'intitle:"Web Image Monitor"',
        'intitle:"Xerox Phaser"',
        'inurl:"/PrinterInfo.htm"',
    ],
    "login_portals": [
        'inurl:"/remote/login" "please login"',
        'inurl:"/vpn/index.html"',
        'intitle:"Citrix" inurl:"/vpn/"',
        'intitle:"Outlook Web" inurl:owa',
        'intitle:"Sign In" inurl:login',
        'inurl:"sslvpn" OR inurl:"remote access"',
    ],
    "error_messages": [
        '"SQL syntax" "mysql_query"',
        '"ORA-" "Oracle error"',
        '"PostgreSQL query failed"',
        '"Warning: mysql_"',
        '"JDBC" "SQLException"',
        '"Microsoft OLE DB Provider for SQL Server"',
        '"Unclosed quotation mark"',
        '"syntax error at or near"',
        'intext:"Error Executing Database Query"',
    ],
}

# File extensions to auto-download
DOWNLOAD_EXTENSIONS = [
    '.sql', '.txt', '.log', '.cfg', '.ini', '.env', '.bak', '.old',
    '.json', '.yaml', '.yml', '.xml', '.csv', '.xls', '.xlsx',
    '.conf', '.config', '.htaccess', '.htpasswd', '.key', '.pem',
]

# Result categories based on patterns
CATEGORY_PATTERNS = {
    "credential_leak": ["password", "passwd", "credentials", "secret", "api_key", "token"],
    "database_exposure": ["sql", "mysql", "postgres", "mongodb", "database", "dump"],
    "admin_access": ["admin", "administrator", "dashboard", "control panel", "cpanel"],
    "source_code": [".git", ".svn", "github", "source", "repository"],
    "config_file": ["config", ".env", ".cfg", ".ini", ".yaml", ".yml"],
    "vulnerable": ["phpinfo", "server-status", "error", "debug", "trace"],
    "api_exposure": ["api", "endpoint", "swagger", "graphql"],
    "iot_device": ["camera", "webcam", "printer", "router", "iot"],
}


class DorkHarvester:
    def __init__(self, db_path="dork_results.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers["User-Agent"] = CONFIG["user_agent"]
        self.setup_database()
        self.setup_directories()
        self.captcha_hits = 0
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                dork TEXT,
                category TEXT,
                url TEXT UNIQUE,
                title TEXT,
                snippet TEXT,
                domain TEXT,
                file_type TEXT,
                downloaded_path TEXT,
                screenshot_path TEXT,
                auto_category TEXT,
                severity TEXT,
                discovered_at TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                dork_hash TEXT PRIMARY KEY,
                page INTEGER,
                completed INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS dork_stats (
                dork TEXT PRIMARY KEY,
                results_count INTEGER,
                last_run TEXT
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_domain ON results(domain)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_category ON results(category)')
        conn.commit()
        conn.close()
        
    def setup_directories(self):
        Path(CONFIG["download_dir"]).mkdir(exist_ok=True)
        Path(CONFIG["screenshot_dir"]).mkdir(exist_ok=True)
        
    def get_progress(self, dork):
        dork_hash = hashlib.md5(dork.encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT page, completed FROM progress WHERE dork_hash = ?', (dork_hash,))
        row = c.fetchone()
        conn.close()
        return row if row else (0, 0)
        
    def save_progress(self, dork, page, completed=0):
        dork_hash = hashlib.md5(dork.encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO progress (dork_hash, page, completed) VALUES (?, ?, ?)',
                  (dork_hash, page, completed))
        conn.commit()
        conn.close()
        
    def save_result(self, dork, category, url, title, snippet):
        """Save a search result"""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Detect file type
        file_type = None
        for ext in DOWNLOAD_EXTENSIONS:
            if ext in url.lower():
                file_type = ext
                break
                
        # Auto-categorize
        auto_cat = self.auto_categorize(url + " " + (title or "") + " " + (snippet or ""))
        severity = self.assess_severity(url, snippet, auto_cat)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT OR IGNORE INTO results 
                (dork, category, url, title, snippet, domain, file_type, auto_category, severity, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dork, category, url, title, snippet, domain, file_type, 
                  auto_cat, severity, datetime.now().isoformat()))
            conn.commit()
            return c.lastrowid > 0  # True if new insert
        finally:
            conn.close()
            
    def auto_categorize(self, text):
        """Auto-categorize based on content patterns"""
        text_lower = text.lower()
        scores = {}
        for cat, patterns in CATEGORY_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            if score > 0:
                scores[cat] = score
        if scores:
            return max(scores, key=scores.get)
        return "unknown"
        
    def assess_severity(self, url, snippet, category):
        """Assess finding severity"""
        high_indicators = ["password", "secret", "api_key", "credentials", "private_key", "aws_secret"]
        medium_indicators = ["admin", "config", "database", ".sql", "backup"]
        
        combined = (url + " " + (snippet or "")).lower()
        
        if any(ind in combined for ind in high_indicators):
            return "HIGH"
        elif any(ind in combined for ind in medium_indicators):
            return "MEDIUM"
        return "LOW"
        
    def search_google(self, dork, num_results=50):
        """Search Google with a dork (slow, stealth mode)"""
        results = []
        
        # Google search URL
        base_url = "https://www.google.com/search"
        
        for start in range(0, num_results, 10):
            params = {
                "q": dork,
                "start": start,
                "num": 10,
                "hl": "en",
            }
            
            try:
                # Random delay
                delay = random.uniform(CONFIG["delay_min"], CONFIG["delay_max"])
                time.sleep(delay)
                
                resp = self.session.get(base_url, params=params, timeout=30)
                
                # Check for CAPTCHA
                if "captcha" in resp.text.lower() or resp.status_code == 429:
                    self.captcha_hits += 1
                    print(f"\n    [!] CAPTCHA detected (hit #{self.captcha_hits})")
                    self.queue_captcha(dork, start)
                    # Increase delay
                    CONFIG["delay_min"] = min(CONFIG["delay_min"] * 1.5, 120)
                    CONFIG["delay_max"] = min(CONFIG["delay_max"] * 1.5, 180)
                    break
                    
                # Parse results
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                for div in soup.find_all('div', class_='g'):
                    link = div.find('a')
                    if not link or not link.get('href'):
                        continue
                        
                    url = link['href']
                    if not url.startswith('http'):
                        continue
                    if 'google.com' in url:
                        continue
                        
                    # Get title
                    title_elem = div.find('h3')
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Get snippet
                    snippet_elem = div.find('div', class_='VwiC3b') or div.find('span', class_='aCOpRe')
                    snippet = snippet_elem.get_text() if snippet_elem else ""
                    
                    results.append({
                        "url": url,
                        "title": title,
                        "snippet": snippet
                    })
                    
                # Check if more results
                if not soup.find('a', id='pnnext'):
                    break
                    
            except Exception as e:
                print(f"\n    [-] Search error: {e}")
                break
                
        return results
        
    def search_duckduckgo(self, dork, num_results=50):
        """Alternative: Search DuckDuckGo"""
        results = []
        try:
            url = "https://html.duckduckgo.com/html/"
            data = {"q": dork}
            resp = self.session.post(url, data=data, timeout=30)
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for result in soup.find_all('div', class_='result'):
                link = result.find('a', class_='result__a')
                if not link:
                    continue
                    
                href = link.get('href', '')
                title = link.get_text()
                
                snippet_elem = result.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text() if snippet_elem else ""
                
                if href and href.startswith('http'):
                    results.append({
                        "url": href,
                        "title": title,
                        "snippet": snippet
                    })
                    
                if len(results) >= num_results:
                    break
                    
        except Exception as e:
            print(f"\n    [-] DDG search error: {e}")
            
        return results
        
    def queue_captcha(self, dork, page):
        """Queue a search for manual CAPTCHA solving"""
        with open(CONFIG["captcha_queue"], "a") as f:
            f.write(f"{datetime.now().isoformat()}|{dork}|{page}\n")
            
    def download_file(self, url, result_id):
        """Download a found file"""
        try:
            resp = self.session.get(url, timeout=60, stream=True)
            
            # Check size (max 50MB)
            content_length = int(resp.headers.get('content-length', 0))
            if content_length > 50 * 1024 * 1024:
                return None
                
            # Generate filename
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path) or f"file_{result_id}"
            # Sanitize
            filename = re.sub(r'[^\w\-_\.]', '_', filename)
            filename = f"{result_id}_{filename}"
            
            filepath = Path(CONFIG["download_dir"]) / filename
            
            content = b""
            for chunk in resp.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > 50 * 1024 * 1024:
                    return None
                    
            filepath.write_bytes(content)
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('UPDATE results SET downloaded_path = ? WHERE id = ?', (str(filepath), result_id))
            conn.commit()
            conn.close()
            
            return str(filepath)
            
        except Exception as e:
            print(f"\n    [-] Download failed: {e}")
            return None
            
    def screenshot_page(self, url, result_id):
        """Take screenshot of a page"""
        if not PLAYWRIGHT_AVAILABLE:
            return None
            
        try:
            filename = f"{result_id}.png"
            filepath = Path(CONFIG["screenshot_dir"]) / filename
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_viewport_size({"width": 1280, "height": 800})
                page.goto(url, timeout=30000)
                page.screenshot(path=str(filepath))
                browser.close()
                
            # Update database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('UPDATE results SET screenshot_path = ? WHERE id = ?', (str(filepath), result_id))
            conn.commit()
            conn.close()
            
            return str(filepath)
            
        except Exception as e:
            print(f"\n    [-] Screenshot failed: {e}")
            return None
            
    def print_progress(self, current_dork, dork_num, total_dorks, results_found):
        """Print progress"""
        pct = dork_num / total_dorks if total_dorks > 0 else 0
        bar_len = 30
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r[{bar}] {dork_num}/{total_dorks} | Results: {results_found} | CAPTCHAs: {self.captcha_hits}", end="", flush=True)
        
    def run_harvest(self, categories=None, custom_dorks=None, download=True, screenshot=False, engine="google"):
        """Main harvesting function"""
        # Build dork list
        dorks = []
        if custom_dorks:
            dorks = custom_dorks
        elif categories:
            for cat in categories:
                if cat in DORK_DATABASE:
                    for dork in DORK_DATABASE[cat]:
                        dorks.append((cat, dork))
        else:
            # All dorks
            for cat, dork_list in DORK_DATABASE.items():
                for dork in dork_list:
                    dorks.append((cat, dork))
                    
        total_dorks = len(dorks)
        total_results = 0
        
        print(f"\n{'='*60}")
        print(f"  Google Dork Harvester")
        print(f"  Dorks: {total_dorks}")
        print(f"  Engine: {engine}")
        print(f"  Delay: {CONFIG['delay_min']}-{CONFIG['delay_max']}s (anti-CAPTCHA)")
        print(f"  Download: {download} | Screenshot: {screenshot}")
        print(f"{'='*60}\n")
        
        search_func = self.search_google if engine == "google" else self.search_duckduckgo
        
        try:
            for i, (category, dork) in enumerate(dorks, 1):
                # Check resume
                start_page, completed = self.get_progress(dork)
                if completed:
                    print(f"\n[{i}/{total_dorks}] Skipping (completed): {dork[:50]}...")
                    continue
                    
                print(f"\n[{i}/{total_dorks}] {category}: {dork[:60]}...")
                
                results = search_func(dork, CONFIG["results_per_query"])
                new_results = 0
                
                for result in results:
                    is_new = self.save_result(
                        dork=dork,
                        category=category,
                        url=result["url"],
                        title=result["title"],
                        snippet=result["snippet"]
                    )
                    if is_new:
                        new_results += 1
                        total_results += 1
                        
                        # Get result ID
                        conn = sqlite3.connect(self.db_path)
                        c = conn.cursor()
                        c.execute('SELECT id, file_type, severity FROM results WHERE url = ?', (result["url"],))
                        row = c.fetchone()
                        conn.close()
                        
                        if row:
                            result_id, file_type, severity = row
                            
                            # Color-code severity
                            sev_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")
                            print(f"\n    {sev_color} [{severity}] {result['url'][:80]}")
                            
                            # Download files
                            if download and file_type:
                                print(f"        Downloading {file_type}...", end="")
                                path = self.download_file(result["url"], result_id)
                                print(f" {'✓' if path else '✗'}")
                                
                            # Screenshot
                            if screenshot:
                                print(f"        Screenshotting...", end="")
                                path = self.screenshot_page(result["url"], result_id)
                                print(f" {'✓' if path else '✗'}")
                                
                print(f"    Found {new_results} new results")
                self.save_progress(dork, 0, completed=1)
                
                # Update stats
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute('INSERT OR REPLACE INTO dork_stats (dork, results_count, last_run) VALUES (?, ?, ?)',
                          (dork, len(results), datetime.now().isoformat()))
                conn.commit()
                conn.close()
                
                self.print_progress(dork, i, total_dorks, total_results)
                
        except KeyboardInterrupt:
            print(f"\n\n[!] Harvest interrupted")
            
        print(f"\n\n{'='*60}")
        print(f"  Harvest Complete")
        print(f"  Total new results: {total_results}")
        print(f"  CAPTCHA hits: {self.captcha_hits}")
        print(f"  Results saved to: {self.db_path}")
        if self.captcha_hits:
            print(f"  CAPTCHA queue: {CONFIG['captcha_queue']}")
        print(f"{'='*60}\n")
        
        return total_results
        
    def export_csv(self, output_path="dork_results.csv"):
        """Export results to CSV"""
        import csv
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT dork, category, url, title, snippet, domain, 
                   file_type, auto_category, severity, discovered_at
            FROM results ORDER BY severity DESC, discovered_at DESC
        ''')
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Dork', 'Category', 'URL', 'Title', 'Snippet', 'Domain', 
                           'File Type', 'Auto Category', 'Severity', 'Discovered'])
            writer.writerows(c.fetchall())
            
        conn.close()
        print(f"[+] Exported to {output_path}")
        
    def get_stats(self):
        """Get harvest statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM results')
        total = c.fetchone()[0]
        c.execute('SELECT severity, COUNT(*) FROM results GROUP BY severity')
        by_severity = dict(c.fetchall())
        c.execute('SELECT auto_category, COUNT(*) FROM results GROUP BY auto_category')
        by_category = dict(c.fetchall())
        c.execute('SELECT domain, COUNT(*) FROM results GROUP BY domain ORDER BY COUNT(*) DESC LIMIT 10')
        top_domains = c.fetchall()
        conn.close()
        
        return {
            "total": total,
            "by_severity": by_severity,
            "by_category": by_category,
            "top_domains": top_domains
        }


def main():
    parser = argparse.ArgumentParser(description="Google Dork Harvester")
    parser.add_argument("-c", "--categories", nargs="+", help="Dork categories to use",
                        choices=list(DORK_DATABASE.keys()))
    parser.add_argument("-d", "--dorks", help="Custom dorks file (one per line)")
    parser.add_argument("-e", "--engine", default="google", choices=["google", "duckduckgo"],
                        help="Search engine")
    parser.add_argument("--no-download", action="store_true", help="Don't download files")
    parser.add_argument("--screenshot", action="store_true", help="Screenshot found pages")
    parser.add_argument("--export", help="Export results to CSV")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("-o", "--output", default="dork_results.db", help="SQLite database path")
    parser.add_argument("--list-categories", action="store_true", help="List available dork categories")
    args = parser.parse_args()
    
    if args.list_categories:
        print("\nAvailable dork categories:")
        for cat, dorks in DORK_DATABASE.items():
            print(f"  {cat}: {len(dorks)} dorks")
        print()
        return
        
    harvester = DorkHarvester(args.output)
    
    if args.stats:
        stats = harvester.get_stats()
        print(f"\n{'='*40}")
        print(f"  Harvest Statistics")
        print(f"{'='*40}")
        print(f"  Total results: {stats['total']}")
        print(f"\n  By severity:")
        for sev, count in stats['by_severity'].items():
            print(f"    {sev}: {count}")
        print(f"\n  By category:")
        for cat, count in stats['by_category'].items():
            print(f"    {cat}: {count}")
        print(f"\n  Top domains:")
        for domain, count in stats['top_domains']:
            print(f"    {domain}: {count}")
        print()
        
    elif args.export:
        harvester.export_csv(args.export)
        
    else:
        # Load custom dorks
        custom_dorks = None
        if args.dorks:
            with open(args.dorks) as f:
                custom_dorks = [("custom", line.strip()) for line in f if line.strip()]
                
        harvester.run_harvest(
            categories=args.categories,
            custom_dorks=custom_dorks,
            download=not args.no_download,
            screenshot=args.screenshot,
            engine=args.engine
        )


if __name__ == "__main__":
    main()
