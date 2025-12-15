#!/usr/bin/env python3
"""
Breach Data Finder
- Monitor paste sites (Pastebin, Ghostbin, Rentry, etc.)
- Telegram channel scraper
- Twitter/X breach announcement monitoring
- Forum monitoring
- Dehashed/LeakCheck/IntelX API integration
- Tor support for onion sources
- Auto-download and index findings
- Hash deduplication
- SQLite storage with full-text search
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
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse

# Optional imports
try:
    import socks
    import socket
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False

try:
    from telethon import TelegramClient
    from telethon.tl.functions.messages import GetHistoryRequest
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

# --- CONFIG ---
CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "delay_min": 2,
    "delay_max": 5,
    "download_dir": "breach_downloads",
    "tor_proxy": "socks5h://127.0.0.1:9050",
    "max_content_size": 50 * 1024 * 1024,  # 50MB max download
    "debug": False,  # Set True to see API responses
}

# Keywords to hunt
DEFAULT_KEYWORDS = [
    "database dump", "db dump", "sql dump", "data breach", "leaked",
    "combolist", "combo list", "email:pass", "user:pass", "credentials",
    "dump", "leak", "breach", "hacked", "pwned", "dox", "doxxed",
    "fullz", "cc dump", "credit card", "ssn", "passport",
    "netflix", "spotify", "fortnite", "minecraft", "roblox",
    "gmail", "yahoo", "hotmail", "outlook", "icloud",
    "vpn", "nordvpn", "expressvpn", "accounts", "logins",
    "config", "sqli", "injection", "exploit", "0day",
]

# Paste sites to monitor
PASTE_SITES = [
    {"name": "Pastebin", "search_url": "https://psbdmp.ws/api/v3/search/{keyword}", "type": "api"},
    {"name": "Rentry", "url": "https://rentry.co", "type": "scrape"},
    {"name": "Ghostbin", "url": "https://ghostbin.me", "type": "scrape"},
    {"name": "Dpaste", "url": "https://dpaste.org", "type": "scrape"},
    {"name": "Hastebin", "url": "https://hastebin.com", "type": "scrape"},
]

# Known Telegram leak channels (examples - add your own)
TELEGRAM_CHANNELS = [
    # Add channel usernames here
    # "example_leak_channel",
]

# Breach notification accounts to monitor
TWITTER_ACCOUNTS = [
    "haveibeenpwned",
    "breach_report", 
    "darkaboratory",
]

# External API configs (add your keys)
API_KEYS = {
    "dehashed": "",  # Your Dehashed API key
    "leakcheck": "",  # Your LeakCheck API key
    "intelx": "",  # Your Intelligence X API key
}


class BreachFinder:
    def __init__(self, db_path="breach_data.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers["User-Agent"] = CONFIG["user_agent"]
        self.tor_session = None
        self.setup_database()
        self.setup_directories()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Main findings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY,
                source TEXT,
                source_url TEXT,
                title TEXT,
                content_hash TEXT UNIQUE,
                content_preview TEXT,
                keywords_matched TEXT,
                file_path TEXT,
                size_bytes INTEGER,
                discovered_at TEXT,
                processed INTEGER DEFAULT 0
            )
        ''')
        
        # Indexed credentials/data
        c.execute('''
            CREATE TABLE IF NOT EXISTS indexed_data (
                id INTEGER PRIMARY KEY,
                finding_id INTEGER,
                data_type TEXT,
                value TEXT,
                context TEXT,
                FOREIGN KEY(finding_id) REFERENCES findings(id)
            )
        ''')
        
        # Monitoring progress
        c.execute('''
            CREATE TABLE IF NOT EXISTS monitor_state (
                source TEXT PRIMARY KEY,
                last_check TEXT,
                last_id TEXT
            )
        ''')
        
        # Full-text search
        c.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS findings_fts USING fts5(
                title, content_preview, keywords_matched,
                content='findings',
                content_rowid='id'
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def setup_directories(self):
        Path(CONFIG["download_dir"]).mkdir(exist_ok=True)
        
    def setup_tor(self):
        """Setup Tor SOCKS proxy"""
        if not TOR_AVAILABLE:
            print("[-] PySocks not installed. Run: pip install pysocks")
            return False
        self.tor_session = requests.Session()
        self.tor_session.proxies = {
            "http": CONFIG["tor_proxy"],
            "https": CONFIG["tor_proxy"]
        }
        self.tor_session.headers["User-Agent"] = CONFIG["user_agent"]
        # Test Tor
        try:
            resp = self.tor_session.get("https://check.torproject.org/api/ip", timeout=30)
            data = resp.json()
            if data.get("IsTor"):
                print(f"[+] Tor connected via {data.get('IP')}")
                return True
        except Exception as e:
            print(f"[-] Tor connection failed: {e}")
        return False
        
    def hash_content(self, content):
        """Generate content hash for deduplication"""
        if isinstance(content, str):
            content = content.encode()
        return hashlib.sha256(content).hexdigest()
        
    def is_duplicate(self, content_hash):
        """Check if content already exists"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id FROM findings WHERE content_hash = ?', (content_hash,))
        result = c.fetchone()
        conn.close()
        return result is not None
        
    def save_finding(self, source, url, title, content, keywords_matched, file_path=None):
        """Save a finding to database"""
        content_hash = self.hash_content(content)
        if self.is_duplicate(content_hash):
            return None
            
        preview = content[:2000] if isinstance(content, str) else content.decode('utf-8', errors='ignore')[:2000]
        size = len(content) if isinstance(content, bytes) else len(content.encode())
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO findings 
                (source, source_url, title, content_hash, content_preview, 
                 keywords_matched, file_path, size_bytes, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (source, url, title, content_hash, preview,
                  ",".join(keywords_matched), file_path, size, datetime.now().isoformat()))
            finding_id = c.lastrowid
            
            # Update FTS
            c.execute('INSERT INTO findings_fts(rowid, title, content_preview, keywords_matched) VALUES (?, ?, ?, ?)',
                      (finding_id, title, preview, ",".join(keywords_matched)))
            
            conn.commit()
            return finding_id
        finally:
            conn.close()
            
    def download_content(self, url, filename=None, use_tor=False):
        """Download content from URL"""
        session = self.tor_session if use_tor and self.tor_session else self.session
        try:
            resp = session.get(url, timeout=60, stream=True)
            
            # Check size
            content_length = int(resp.headers.get('content-length', 0))
            if content_length > CONFIG["max_content_size"]:
                print(f"    [-] File too large: {content_length / 1024 / 1024:.1f}MB")
                return None
                
            content = b""
            for chunk in resp.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > CONFIG["max_content_size"]:
                    print(f"    [-] Download exceeded max size")
                    return None
                    
            if filename:
                file_path = Path(CONFIG["download_dir"]) / filename
                file_path.write_bytes(content)
                return str(file_path)
            return content
        except Exception as e:
            print(f"    [-] Download failed: {e}")
            return None
            
    def match_keywords(self, text, keywords=None):
        """Check text for keywords"""
        if keywords is None:
            keywords = DEFAULT_KEYWORDS
        text_lower = text.lower()
        matched = [kw for kw in keywords if kw.lower() in text_lower]
        return matched
        
    # === PASTE SITE MONITORING ===
    
    def scrape_pastebin_dumps(self, keywords=None):
        """Search Pastebin via psbdmp.ws API"""
        print("\n[*] Searching Pastebin dumps...")
        if keywords is None:
            keywords = DEFAULT_KEYWORDS[:10]  # Top keywords
            
        findings = 0
        for keyword in keywords:
            time.sleep(random.uniform(CONFIG["delay_min"], CONFIG["delay_max"]))
            try:
                url = f"https://psbdmp.ws/api/v3/search/{keyword}"
                resp = self.session.get(url, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    
                    if CONFIG["debug"]:
                        print(f"    [DEBUG] Response type: {type(data)}, preview: {str(data)[:200]}")
                    
                    # Handle both list and dict responses
                    if isinstance(data, list):
                        pastes = data[:20]
                    elif isinstance(data, dict):
                        pastes = data.get("data", [])[:20]
                    else:
                        pastes = []
                    
                    for paste in pastes:
                        # Handle different response formats
                        if isinstance(paste, dict):
                            paste_id = paste.get("id") or paste.get("ID") or paste.get("key")
                            paste_title = paste.get("tags") or paste_id
                        elif isinstance(paste, str):
                            paste_id = paste
                            paste_title = paste
                        else:
                            continue
                            
                        if not paste_id:
                            continue
                            
                        paste_url = f"https://pastebin.com/raw/{paste_id}"
                        
                        # Get full content
                        time.sleep(random.uniform(1, 2))  # Rate limit
                        try:
                            content_resp = self.session.get(paste_url, timeout=30)
                            if content_resp.status_code == 200:
                                content = content_resp.text
                                matched = self.match_keywords(content)
                                if matched:
                                    finding_id = self.save_finding(
                                        source="Pastebin",
                                        url=paste_url,
                                        title=paste_title,
                                        content=content,
                                        keywords_matched=matched
                                    )
                                    if finding_id:
                                        findings += 1
                                        print(f"    [+] New finding: {paste_url} ({len(matched)} keywords)")
                        except Exception as fetch_err:
                            if CONFIG["debug"]:
                                print(f"    [DEBUG] Failed to fetch {paste_id}: {fetch_err}")
            except Exception as e:
                print(f"    [-] Error searching '{keyword}': {e}")
                
        print(f"    [*] Pastebin: {findings} new findings")
        return findings
        
    def scrape_rentry(self):
        """Scrape Rentry.co recent pastes"""
        print("\n[*] Checking Rentry.co...")
        # Rentry doesn't have a public API, would need to monitor known URLs
        # Placeholder for future implementation
        return 0
    
    def scrape_paste_sites(self, keywords=None):
        """Scrape multiple paste aggregator sites"""
        print("\n[*] Checking paste aggregators...")
        if keywords is None:
            keywords = DEFAULT_KEYWORDS[:5]
            
        findings = 0
        
        # PasteBin recent (public)
        try:
            time.sleep(random.uniform(2, 4))
            # Scrape pastebin's archive if accessible
            resp = self.session.get("https://pastebin.com/archive", timeout=30)
            if resp.status_code == 200:
                # Extract paste links
                import re
                paste_ids = re.findall(r'href="/([a-zA-Z0-9]{8})"', resp.text)
                print(f"    [*] Found {len(paste_ids)} recent pastes on Pastebin archive")
                
                for paste_id in paste_ids[:15]:  # Check first 15
                    time.sleep(random.uniform(1, 3))
                    paste_url = f"https://pastebin.com/raw/{paste_id}"
                    try:
                        content_resp = self.session.get(paste_url, timeout=15)
                        if content_resp.status_code == 200:
                            content = content_resp.text
                            matched = self.match_keywords(content)
                            if matched:
                                finding_id = self.save_finding(
                                    source="Pastebin_Archive",
                                    url=paste_url,
                                    title=f"paste_{paste_id}",
                                    content=content,
                                    keywords_matched=matched
                                )
                                if finding_id:
                                    findings += 1
                                    print(f"    [+] Archive find: {paste_url} ({len(matched)} keywords)")
                    except:
                        continue
        except Exception as e:
            print(f"    [-] Pastebin archive error: {e}")
        
        # Dpaste.org recent
        try:
            time.sleep(random.uniform(2, 4))
            resp = self.session.get("https://dpaste.org/", timeout=30)
            if resp.status_code == 200:
                import re
                paste_ids = re.findall(r'href="/([a-zA-Z0-9]+)"', resp.text)
                for paste_id in paste_ids[:10]:
                    if len(paste_id) < 4:
                        continue
                    time.sleep(random.uniform(1, 2))
                    paste_url = f"https://dpaste.org/{paste_id}/raw"
                    try:
                        content_resp = self.session.get(paste_url, timeout=15)
                        if content_resp.status_code == 200:
                            content = content_resp.text
                            matched = self.match_keywords(content)
                            if matched:
                                finding_id = self.save_finding(
                                    source="Dpaste",
                                    url=paste_url,
                                    title=f"dpaste_{paste_id}",
                                    content=content,
                                    keywords_matched=matched
                                )
                                if finding_id:
                                    findings += 1
                                    print(f"    [+] Dpaste find: {paste_url}")
                    except:
                        continue
        except Exception as e:
            print(f"    [-] Dpaste error: {e}")
            
        print(f"    [*] Paste sites: {findings} new findings")
        return findings
        
    # === TELEGRAM MONITORING ===
    
    async def scrape_telegram_channel(self, channel, api_id, api_hash, limit=100):
        """Scrape Telegram channel for leaks"""
        if not TELEGRAM_AVAILABLE:
            print("[-] Telethon not installed. Run: pip install telethon")
            return 0
            
        findings = 0
        client = TelegramClient('breach_session', api_id, api_hash)
        await client.start()
        
        try:
            entity = await client.get_entity(channel)
            messages = await client(GetHistoryRequest(
                peer=entity,
                limit=limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))
            
            for msg in messages.messages:
                if msg.message:
                    matched = self.match_keywords(msg.message)
                    if matched:
                        finding_id = self.save_finding(
                            source=f"Telegram:{channel}",
                            url=f"https://t.me/{channel}/{msg.id}",
                            title=f"Telegram message {msg.id}",
                            content=msg.message,
                            keywords_matched=matched
                        )
                        if finding_id:
                            findings += 1
                            
                # Check for file attachments
                if msg.media and hasattr(msg.media, 'document'):
                    doc = msg.media.document
                    for attr in doc.attributes:
                        if hasattr(attr, 'file_name'):
                            if any(ext in attr.file_name.lower() for ext in ['.txt', '.sql', '.csv', '.json', '.db']):
                                # Download file
                                file_path = await client.download_media(msg, CONFIG["download_dir"])
                                if file_path:
                                    with open(file_path, 'rb') as f:
                                        content = f.read()
                                    finding_id = self.save_finding(
                                        source=f"Telegram:{channel}",
                                        url=f"https://t.me/{channel}/{msg.id}",
                                        title=attr.file_name,
                                        content=content,
                                        keywords_matched=["file_attachment"],
                                        file_path=file_path
                                    )
                                    if finding_id:
                                        findings += 1
                                        print(f"    [+] Downloaded: {attr.file_name}")
        finally:
            await client.disconnect()
            
        return findings
        
    # === TWITTER/X MONITORING ===
    
    def check_twitter_accounts(self):
        """Check Twitter breach notification accounts (via Nitter)"""
        print("\n[*] Checking Twitter/X accounts...")
        findings = 0
        
        # Use Nitter instances (Twitter scraping alternative)
        nitter_instances = [
            "https://nitter.net",
            "https://nitter.privacydev.net",
            "https://nitter.poast.org",
        ]
        
        for account in TWITTER_ACCOUNTS:
            for instance in nitter_instances:
                try:
                    url = f"{instance}/{account}"
                    resp = self.session.get(url, timeout=30)
                    if resp.status_code == 200:
                        # Parse tweets for keywords
                        text = resp.text
                        matched = self.match_keywords(text)
                        if matched:
                            # Save reference (not full content due to ToS)
                            self.save_finding(
                                source=f"Twitter:{account}",
                                url=f"https://twitter.com/{account}",
                                title=f"@{account} activity",
                                content=f"Keyword matches found in recent tweets",
                                keywords_matched=matched
                            )
                            findings += 1
                        break  # Success, move to next account
                except:
                    continue  # Try next Nitter instance
                    
            time.sleep(random.uniform(1, 3))
            
        print(f"    [*] Twitter: {findings} accounts with activity")
        return findings
        
    # === API INTEGRATIONS ===
    
    def search_dehashed(self, query, query_type="email"):
        """Search Dehashed API"""
        if not API_KEYS["dehashed"]:
            return []
            
        print(f"\n[*] Searching Dehashed for {query}...")
        try:
            headers = {"Accept": "application/json"}
            auth = (API_KEYS["dehashed"].split(":")[0], API_KEYS["dehashed"].split(":")[1])
            url = f"https://api.dehashed.com/search?query={query_type}:{query}"
            resp = self.session.get(url, auth=auth, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                entries = data.get("entries", [])
                print(f"    [+] Found {len(entries)} results")
                return entries
        except Exception as e:
            print(f"    [-] Dehashed error: {e}")
        return []
        
    def search_leakcheck(self, query, query_type="email"):
        """Search LeakCheck API"""
        if not API_KEYS["leakcheck"]:
            return []
            
        print(f"\n[*] Searching LeakCheck for {query}...")
        try:
            url = f"https://leakcheck.io/api/public?key={API_KEYS['leakcheck']}&check={query}&type={query_type}"
            resp = self.session.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    results = data.get("sources", [])
                    print(f"    [+] Found in {len(results)} breaches")
                    return results
        except Exception as e:
            print(f"    [-] LeakCheck error: {e}")
        return []
        
    def search_intelx(self, query):
        """Search Intelligence X"""
        if not API_KEYS["intelx"]:
            return []
            
        print(f"\n[*] Searching IntelX for {query}...")
        try:
            headers = {"x-key": API_KEYS["intelx"]}
            # Start search
            search_url = "https://2.intelx.io/intelligent/search"
            resp = self.session.post(search_url, headers=headers, json={
                "term": query,
                "maxresults": 100,
                "media": 0,
                "timeout": 20
            }, timeout=30)
            
            if resp.status_code == 200:
                search_id = resp.json().get("id")
                # Get results
                time.sleep(5)
                results_url = f"https://2.intelx.io/intelligent/search/result?id={search_id}"
                results_resp = self.session.get(results_url, headers=headers, timeout=30)
                if results_resp.status_code == 200:
                    data = results_resp.json()
                    records = data.get("records", [])
                    print(f"    [+] Found {len(records)} results")
                    return records
        except Exception as e:
            print(f"    [-] IntelX error: {e}")
        return []
        
    # === DATA PARSING/INDEXING ===
    
    def extract_emails(self, text):
        """Extract email addresses from text"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(pattern, text)))
        
    def extract_credentials(self, text):
        """Extract email:password patterns"""
        patterns = [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})[:\|;]([^\s:;\|]+)',
            r'([a-zA-Z0-9_]+)[:\|;]([^\s:;\|]+)',
        ]
        creds = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            creds.extend(matches)
        return creds
        
    def index_finding(self, finding_id):
        """Parse and index a finding's content"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT content_preview, file_path FROM findings WHERE id = ?', (finding_id,))
        row = c.fetchone()
        
        if not row:
            return
            
        content = row[0]
        file_path = row[1]
        
        # If we have a file, read it
        if file_path and Path(file_path).exists():
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read()
            except:
                pass
                
        # Extract data
        emails = self.extract_emails(content)
        creds = self.extract_credentials(content)
        
        # Index emails
        for email in emails[:1000]:  # Limit
            c.execute('INSERT INTO indexed_data (finding_id, data_type, value) VALUES (?, ?, ?)',
                      (finding_id, 'email', email))
                      
        # Index credentials
        for user, pwd in creds[:1000]:
            c.execute('INSERT INTO indexed_data (finding_id, data_type, value, context) VALUES (?, ?, ?, ?)',
                      (finding_id, 'credential', user, pwd[:50]))
                      
        c.execute('UPDATE findings SET processed = 1 WHERE id = ?', (finding_id,))
        conn.commit()
        conn.close()
        
        return len(emails), len(creds)
        
    # === MAIN MONITORING LOOP ===
    
    def print_progress(self, source, findings, elapsed):
        """Print status"""
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] {source}: {findings} findings | Elapsed: {elapsed:.0f}s", end="", flush=True)
        
    def run_monitor(self, keywords=None, use_tor=False, telegram_config=None):
        """Main monitoring loop"""
        print(f"\n{'='*60}")
        print(f"  Breach Data Finder - Starting Monitor")
        print(f"  Keywords: {len(keywords or DEFAULT_KEYWORDS)}")
        print(f"  Tor: {'Enabled' if use_tor else 'Disabled'}")
        print(f"{'='*60}\n")
        
        if use_tor:
            self.setup_tor()
            
        cycle = 0
        total_findings = 0
        start_time = time.time()
        
        try:
            while True:
                cycle += 1
                print(f"\n[Cycle {cycle}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Pastebin
                findings = self.scrape_pastebin_dumps(keywords)
                total_findings += findings
                
                # Other paste sites
                findings = self.scrape_paste_sites(keywords)
                total_findings += findings
                
                # Twitter
                findings = self.check_twitter_accounts()
                total_findings += findings
                
                # Index unprocessed findings
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute('SELECT id FROM findings WHERE processed = 0')
                unprocessed = c.fetchall()
                conn.close()
                
                for (fid,) in unprocessed:
                    emails, creds = self.index_finding(fid) or (0, 0)
                    if emails or creds:
                        print(f"    [*] Indexed finding {fid}: {emails} emails, {creds} credentials")
                
                elapsed = time.time() - start_time
                print(f"\n[*] Cycle {cycle} complete. Total findings: {total_findings} | Runtime: {elapsed/3600:.1f}h")
                
                # Progress bar for wait
                wait_time = 300  # 5 minutes between cycles
                print(f"[*] Waiting {wait_time}s until next cycle...")
                for i in range(wait_time):
                    pct = i / wait_time
                    bar = "█" * int(30 * pct) + "░" * (30 - int(30 * pct))
                    print(f"\r    [{bar}] {wait_time - i}s", end="", flush=True)
                    time.sleep(1)
                print()
                
        except KeyboardInterrupt:
            print(f"\n\n[!] Monitor stopped after {cycle} cycles")
            print(f"[*] Total findings: {total_findings}")
            print(f"[*] Runtime: {(time.time() - start_time)/3600:.2f} hours")
            print(f"[*] Results saved to: {self.db_path}")
            
    def search_local(self, query):
        """Search local database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT f.id, f.source, f.title, f.source_url, f.discovered_at
            FROM findings_fts fts
            JOIN findings f ON f.id = fts.rowid
            WHERE findings_fts MATCH ?
            LIMIT 100
        ''', (query,))
        results = c.fetchall()
        conn.close()
        return results
        
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM findings')
        total_findings = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM indexed_data WHERE data_type = "email"')
        total_emails = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM indexed_data WHERE data_type = "credential"')
        total_creds = c.fetchone()[0]
        c.execute('SELECT source, COUNT(*) FROM findings GROUP BY source')
        by_source = c.fetchall()
        conn.close()
        return {
            "total_findings": total_findings,
            "total_emails": total_emails,
            "total_credentials": total_creds,
            "by_source": by_source
        }


def main():
    parser = argparse.ArgumentParser(description="Breach Data Finder")
    parser.add_argument("-m", "--monitor", action="store_true", help="Start continuous monitoring")
    parser.add_argument("-s", "--search", help="Search local database")
    parser.add_argument("-k", "--keywords", help="Custom keywords file (one per line)")
    parser.add_argument("--tor", action="store_true", help="Use Tor for .onion sources")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("-o", "--output", default="breach_data.db", help="SQLite database path")
    parser.add_argument("--dehashed", help="Search Dehashed API for email/domain")
    parser.add_argument("--leakcheck", help="Search LeakCheck API for email")
    parser.add_argument("--intelx", help="Search IntelX for any term")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    
    if args.debug:
        CONFIG["debug"] = True
    
    finder = BreachFinder(args.output)
    
    # Load custom keywords
    keywords = None
    if args.keywords:
        with open(args.keywords) as f:
            keywords = [line.strip() for line in f if line.strip()]
    
    if args.stats:
        stats = finder.get_stats()
        print(f"\n{'='*40}")
        print(f"  Database Statistics")
        print(f"{'='*40}")
        print(f"  Total findings: {stats['total_findings']}")
        print(f"  Indexed emails: {stats['total_emails']}")
        print(f"  Indexed credentials: {stats['total_credentials']}")
        print(f"\n  By source:")
        for source, count in stats['by_source']:
            print(f"    {source}: {count}")
        print()
        
    elif args.search:
        results = finder.search_local(args.search)
        print(f"\n[*] Found {len(results)} results for '{args.search}':\n")
        for id, source, title, url, date in results:
            print(f"  [{id}] {source} - {title}")
            print(f"      URL: {url}")
            print(f"      Date: {date}\n")
            
    elif args.dehashed:
        results = finder.search_dehashed(args.dehashed)
        for entry in results[:20]:
            print(f"  {entry.get('email', 'N/A')} | {entry.get('password', 'N/A')} | {entry.get('database_name', 'N/A')}")
            
    elif args.leakcheck:
        results = finder.search_leakcheck(args.leakcheck)
        for source in results:
            print(f"  Found in: {source.get('name', 'Unknown')} ({source.get('date', 'N/A')})")
            
    elif args.intelx:
        results = finder.search_intelx(args.intelx)
        for record in results[:20]:
            print(f"  {record.get('name', 'N/A')} | {record.get('type', 'N/A')} | {record.get('date', 'N/A')}")
            
    elif args.monitor:
        finder.run_monitor(keywords=keywords, use_tor=args.tor)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
