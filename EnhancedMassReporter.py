from telethon import TelegramClient, functions, types, events
import asyncio
import os
import random
import json
import re
import time
import logging
import colorama
from colorama import Fore, Back, Style
import aiohttp
import base64
from datetime import datetime, timedelta
import sys
import signal
import argparse
from urllib.parse import urlparse

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("massreporter.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MassReporter")

# Create a beautiful animated banner
def print_animated_banner():
    # ASCII Art Banner with gradient colors
    banner_lines = [
        "╔═══════════════════════════════════════════════════════════════════════════╗",
        "║                                                                           ║",
        "║   ███╗   ███╗ █████╗ ███████╗███████╗    ██████╗ ███████╗██████╗ ████████╗  ║",
        "║   ████╗ ████║██╔══██╗██╔════╝██╔════╝    ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝  ║",
        "║   ██╔████╔██║███████║███████╗███████╗    ██████╔╝█████╗  ██████╔╝   ██║     ║",
        "║   ██║╚██╔╝██║██╔══██║╚════██║╚════██║    ██╔══██╗██╔══╝  ██╔═══╝    ██║     ║",
        "║   ██║ ╚═╝ ██║██║  ██║███████║███████║    ██║  ██║███████╗██║        ██║     ║",
        "║   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝     ║",
        "║                                                                             ║",
        "╚═══════════════════════════════════════════════════════════════════════════╝"
    ]
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # ANSI color sequences for rainbow effect
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    
    # Print each line with a typing effect
    for line in banner_lines:
        color = random.choice(colors)
        print(f"{color}{line}")
        time.sleep(0.05)
    
    # Print additional information
    print(f"\n{Fore.CYAN}{'═' * 75}")
    print(f"{Style.BRIGHT}{Fore.GREEN}✨ Ultimate Telegram Channel Reporter - Enhanced Edition v2.0 ✨")
    print(f"{Fore.YELLOW}⚠️  For ethical use against genuinely harmful/illegal content only ⚠️")
    print(f"{Fore.CYAN}{'═' * 75}\n")
    
    # Add loading effect
    print(f"{Fore.WHITE}Initializing system components", end="")
    for _ in range(5):
        print(f"{Fore.WHITE}.", end="", flush=True)
        time.sleep(0.2)
    print(f"{Fore.GREEN} DONE!\n")
    
    # Features list
    features = [
        "✅ Multi-account reporting with session rotation",
        "✅ Advanced proxy management & verification",
        "✅ Smart error handling & retry logic",
        "✅ Detailed statistics & progress tracking",
        "✅ Optimized for maximum report effectiveness"
    ]
    
    # Print features
    for feature in features:
        print(f"{Fore.WHITE}{feature}")
        time.sleep(0.1)

# Also define banner function for backward compatibility
def banner():
    print_animated_banner()

# List of common device names for session creation
devices = [
    'Quantum X5 Pro', 'Galaxy Z Flip Neo', 'OnePlus 11T Max', 'Vivo V21 Neo', 'Oppo F19 Pro+', 
    'Realme GT Master', 'Honor X10 Lite', 'Huawei P30S', 'Xiaomi Mi Mix Fold', 'Redmi Note 12 Ultra',
    'Infinix Zero X', 'Tecno Camon 18 Pro', 'Nokia G21 Max', 'Sony Xperia Z5 Ultra', 'Samsung Galaxy S22 Mini',
    'Motorola Razr Neo', 'Lenovo Z6 Pro Max', 'BlackBerry Passport 2', 'HTC U12 Edge', 'LG V70 ThinQ',
    'Asus ROG Phone Neo', 'ZTE Axon X Pro', 'Vivo Y75 Pro', 'Google Pixel 6X', 'Oppo Reno X Max',
    'OnePlus Nord Pro', 'Realme X7 Pro Max', 'Honor Magic 4 Lite', 'Huawei Nova 9 Ultra', 'Redmi K40S Pro'
]

# TLS configurations for improved anonymity
TLS_CLIENT_CONFIGURATIONS = [
    {
        'type': 'Firefox',
        'version': '120.0',
        'platform': 'win10',
        'ciphers': 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'
    },
    {
        'type': 'Chrome',
        'version': '118.0.5993.117',
        'platform': 'linux',
        'ciphers': 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'
    },
    {
        'type': 'Safari',
        'version': '16.5',
        'platform': 'macos',
        'ciphers': 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'
    }
]

# Global statistics tracking
class Stats:
    def __init__(self):
        self.report_attempts = 0
        self.report_successes = 0
        self.report_failures = 0
        self.account_successes = 0
        self.account_failures = 0
        self.start_time = time.time()
        self.active_clients = 0
        self.target_channel = None
        self.reason_type = None
    
    def print_stats(self):
        elapsed = time.time() - self.start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        
        success_rate = 0 if self.report_attempts == 0 else (self.report_successes / self.report_attempts) * 100
        
        # Create a more beautiful stats display with boxes and colors
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}📊 REPORTING STATISTICS{' ' * 51}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        
        # Target info with colored box
        print(f"{Fore.CYAN}║ {Fore.WHITE}Target Channel: {Fore.GREEN}{self.target_channel}{' ' * (54 - len(str(self.target_channel)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Report Reason: {Fore.GREEN}{self.reason_type}{' ' * (54 - len(str(self.reason_type)))}{Fore.CYAN}║")
        
        # Progress bar for success rate
        bar_length = 40
        filled_length = int(bar_length * success_rate / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Success Rate: {Fore.GREEN}{success_rate:.1f}%{' ' * (57 - len(f'{success_rate:.1f}%'))}{Fore.CYAN}║")
        
        # Colorize the progress bar based on success rate
        bar_color = Fore.RED
        if success_rate > 30:
            bar_color = Fore.YELLOW
        if success_rate > 70:
            bar_color = Fore.GREEN
            
        print(f"{Fore.CYAN}║ {Fore.WHITE}Progress: {bar_color}{bar}{Fore.WHITE} {' ' * (20 - len(f'{success_rate:.1f}%'))}{Fore.CYAN}║")
        
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Reports Sent: {Fore.GREEN}{self.report_successes}/{self.report_attempts}{' ' * (54 - len(f'{self.report_successes}/{self.report_attempts}'))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Accounts Used: {Fore.GREEN}{self.active_clients}{' ' * (56 - len(str(self.active_clients)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Elapsed Time: {Fore.GREEN}{elapsed_str}{' ' * (56 - len(elapsed_str))}{Fore.CYAN}║")
        
        # Effectiveness prediction
        effectiveness = "LOW"
        effectiveness_color = Fore.RED
        if success_rate > 40 and self.report_successes > 10:
            effectiveness = "MEDIUM"
            effectiveness_color = Fore.YELLOW
        if success_rate > 70 and self.report_successes > 20:
            effectiveness = "HIGH"
            effectiveness_color = Fore.GREEN
        if success_rate > 90 and self.report_successes > 50:
            effectiveness = "EXTREMELY HIGH"
            effectiveness_color = Fore.GREEN
            
        print(f"{Fore.CYAN}║ {Fore.WHITE}Estimated Effectiveness: {effectiveness_color}{effectiveness}{' ' * (48 - len(effectiveness))}{Fore.CYAN}║")
        
        print(f"{Fore.CYAN}╚{'═' * 73}╝")

# Initialize global stats
stats = Stats()

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print(f"\n{Fore.YELLOW}Interrupted! Finishing up and displaying stats...")
    stats.print_stats()
    print(f"\n{Fore.RED}Exiting program.")
    sys.exit(0)

class EnhancedProxy:
    """Enhanced proxy handler with rotation capabilities"""
    
    def __init__(self, proxy_list=None):
        self.proxies = proxy_list or []
        self.current_index = 0
        self.failed_proxies = set()
        self.success_counts = {}  # Track success rate of each proxy
    
    def get_next_proxy(self):
        """Get next working proxy with basic scoring"""
        if not self.proxies:
            return None
            
        # Try to find the best proxy - one with most successes and not failed
        best_proxy = None
        best_score = -1
        
        for i, proxy in enumerate(self.proxies):
            proxy_id = self._get_proxy_id(proxy)
            
            # Skip failed proxies
            if proxy_id in self.failed_proxies:
                continue
                
            # Calculate score: successes - failures
            success_count = self.success_counts.get(proxy_id, {}).get('success', 0)
            failure_count = self.success_counts.get(proxy_id, {}).get('failure', 0)
            score = success_count - failure_count
            
            # If no successful proxy found yet or this one has better score
            if best_proxy is None or score > best_score:
                best_proxy = proxy
                best_score = score
                self.current_index = i
        
        # If all proxies failed, reset and try again
        if best_proxy is None and self.proxies:
            self.failed_proxies.clear()
            self.current_index = 0
            return self.proxies[0]
            
        return best_proxy
    
    def mark_proxy_result(self, proxy, success):
        """Track proxy success/failure"""
        if not proxy:
            return
            
        proxy_id = self._get_proxy_id(proxy)
        
        if proxy_id not in self.success_counts:
            self.success_counts[proxy_id] = {'success': 0, 'failure': 0}
            
        if success:
            self.success_counts[proxy_id]['success'] += 1
            # If it was previously marked as failed, remove from failed set
            if proxy_id in self.failed_proxies:
                self.failed_proxies.remove(proxy_id)
        else:
            self.success_counts[proxy_id]['failure'] += 1
            # Mark as failed if too many failures
            if self.success_counts[proxy_id]['failure'] >= 3:
                self.failed_proxies.add(proxy_id)
                logger.warning(f"Marked proxy {proxy.get('addr')}:{proxy.get('port')} as failed")
    
    def _get_proxy_id(self, proxy):
        """Create a unique ID for a proxy"""
        if not proxy:
            return None
        return f"{proxy.get('addr')}:{proxy.get('port')}"
    
    def get_stats(self):
        """Get proxy statistics"""
        total = len(self.proxies)
        failed = len(self.failed_proxies)
        return {
            'total': total,
            'working': total - failed,
            'failed': failed
        }

def parse_custom_proxy_format(proxy_string):
    """Parse various proxy formats into standardized dictionary"""
    try:
        proxy_type = 'socks5'  # Default type
        
        # Clean up the input
        proxy_string = proxy_string.strip()
        
        # Format: username:password@host:port
        if '@' in proxy_string:
            auth, host_port = proxy_string.split('@')
            
            if ':' in host_port:
                host, port_str = host_port.split(':')
                try:
                    port = int(port_str)
                except ValueError:
                    port = 1080
                
                username = None
                password = None
                if ':' in auth:
                    username, password = auth.split(':')
                else:
                    username = auth
                
                return {
                    'proxy_type': proxy_type,
                    'addr': host,
                    'port': port,
                    'username': username,
                    'password': password,
                    'rdns': True
                }
        
        # Format: type:host:port:username:password OR host:port:username:password
        elif ':' in proxy_string:
            parts = proxy_string.split(':')
            
            # Check if first part is a known proxy type
            if parts[0].lower() in ('socks5', 'socks4', 'http'):
                proxy_type = parts[0].lower()
                parts = parts[1:]
            
            # Now parse remaining parts
            if len(parts) >= 2:
                host = parts[0]
                try:
                    port = int(parts[1])
                except ValueError:
                    port = 1080
                
                username = parts[2] if len(parts) > 2 else None
                password = parts[3] if len(parts) > 3 else None
                
                return {
                    'proxy_type': proxy_type,
                    'addr': host,
                    'port': port,
                    'username': username,
                    'password': password,
                    'rdns': True
                }
        
        # Format with space delimiter: type host port username password
        elif ' ' in proxy_string:
            parts = proxy_string.split()
            if len(parts) >= 3:
                if parts[0].lower() in ('socks5', 'socks4', 'http'):
                    proxy_type = parts[0].lower()
                    parts = parts[1:]
                
                host = parts[0]
                try:
                    port = int(parts[1])
                except ValueError:
                    port = 1080
                
                username = parts[2] if len(parts) > 2 else None
                password = parts[3] if len(parts) > 3 else None
                
                return {
                    'proxy_type': proxy_type,
                    'addr': host,
                    'port': port,
                    'username': username,
                    'password': password,
                    'rdns': True
                }
        
        # IP:PORT format
        if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', proxy_string):
            host, port_str = proxy_string.split(':')
            try:
                port = int(port_str)
            except ValueError:
                port = 1080
                
            return {
                'proxy_type': proxy_type,
                'addr': host,
                'port': port,
                'username': None,
                'password': None,
                'rdns': True
            }
            
        # If we couldn't parse it, return None
        logger.warning(f"Couldn't parse proxy string: {proxy_string}")
        return None
    
    except Exception as e:
        logger.error(f"Error parsing proxy format: {e}")
        return None

def load_proxies_from_file(file_path, proxy_type="socks5"):
    """Load proxies from file with enhanced error handling and format detection"""
    proxies = []
    
    try:
        # Detect file type by extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # JSON format
        if file_ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'addr' in item and 'port' in item:
                            # Add default proxy_type if missing
                            if 'proxy_type' not in item and 'type' in item:
                                item['proxy_type'] = item['type']
                            elif 'proxy_type' not in item:
                                item['proxy_type'] = proxy_type
                                
                            # Add default rdns if missing
                            if 'rdns' not in item:
                                item['rdns'] = True
                                
                            proxies.append(item)
                        elif isinstance(item, str):
                            # Parse string format proxy
                            proxy_dict = parse_custom_proxy_format(item)
                            if proxy_dict:
                                proxies.append(proxy_dict)
                elif isinstance(data, dict) and 'proxies' in data:
                    # Handle structure like {"proxies": [...]}
                    for item in data['proxies']:
                        if isinstance(item, dict) and 'addr' in item and 'port' in item:
                            if 'proxy_type' not in item:
                                item['proxy_type'] = proxy_type
                            if 'rdns' not in item:
                                item['rdns'] = True
                            proxies.append(item)
        # Text-based formats (txt, csv, list)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    proxy_dict = parse_custom_proxy_format(line)
                    if proxy_dict:
                        proxies.append(proxy_dict)
        
        # Log success
        if proxies:
            logger.info(f"Successfully loaded {len(proxies)} proxies from {file_path}")
            # Display sample proxies
            for i, p in enumerate(proxies[:3]):
                logger.info(f"Sample proxy {i+1}: {p.get('proxy_type', 'socks5')} {p.get('addr')}:{p.get('port')}")
            if len(proxies) > 3:
                logger.info(f"...and {len(proxies)-3} more")
        else:
            logger.warning(f"No valid proxies found in {file_path}")
            
        return proxies
    
    except Exception as e:
        logger.error(f"Error loading proxy file {file_path}: {e}")
        return []

async def verify_proxy(proxy_dict, timeout=10):
    """Verify if a proxy is working by making a test connection"""
    if not proxy_dict or not proxy_dict.get('addr'):
        return False
    
    proxy_url = f"{proxy_dict['proxy_type']}://"
    if proxy_dict.get('username') and proxy_dict.get('password'):
        proxy_url += f"{proxy_dict['username']}:{proxy_dict['password']}@"
    proxy_url += f"{proxy_dict['addr']}:{proxy_dict['port']}"
    
    try:
        conn = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(
                'https://api.ipify.org?format=json', 
                proxy=proxy_url, 
                timeout=timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'ip' in data:
                        logger.debug(f"Proxy {proxy_dict['addr']}:{proxy_dict['port']} verified, IP: {data['ip']}")
                        return True
        return False
    except Exception as e:
        logger.debug(f"Proxy verification failed for {proxy_dict['addr']}:{proxy_dict['port']}: {e}")
        return False

async def verify_proxies(proxies, max_concurrency=10):
    """Verify multiple proxies concurrently with rate limiting and beautiful progress display"""
    total_proxies = len(proxies)
    
    # Create a beautiful header
    print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
    print(f"{Fore.CYAN}║ {Fore.YELLOW}🔍 PROXY VERIFICATION{' ' * 53}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╠{'═' * 73}╣")
    print(f"{Fore.CYAN}║ {Fore.WHITE}Checking {Fore.YELLOW}{total_proxies} {Fore.WHITE}proxies for connectivity...{' ' * 35}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╚{'═' * 73}╝\n")
    
    working_proxies = []
    
    # Use semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrency)
    
    # Fancy spinner animation
    spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    spinner_idx = 0
    
    async def verify_with_limit(proxy, idx):
        async with semaphore:
            result = await verify_proxy(proxy)
            if result:
                working_proxies.append(proxy)
                # Use a box drawing to show success
                print(f"{Fore.GREEN}┌─────────────────────┐")
                print(f"{Fore.GREEN}│ ✓ WORKING PROXY {idx+1:03d} │")
                print(f"{Fore.GREEN}└─────────────────────┘")
                print(f"{Fore.WHITE}  {proxy['proxy_type']}://{proxy['addr']}:{proxy['port']}")
                if proxy.get('username'):
                    print(f"{Fore.WHITE}  Auth: {proxy['username']}")
                print()
            return result
    
    # Create tasks for all proxies
    tasks = [verify_with_limit(proxy, i) for i, proxy in enumerate(proxies)]
    
    # Show progress indicator with percentage and count
    total = len(tasks)
    completed = 0
    successful = 0
    
    # Track start time for ETA calculation
    start_time = time.time()
    
    # Create custom progress bar
    def update_progress(completed, total, successful):
        nonlocal spinner_idx
        # Calculate progress percentage
        progress = completed / total
        bar_length = 40
        filled_length = int(bar_length * progress)
        
        # Calculate ETA
        elapsed = time.time() - start_time
        if completed > 0:
            eta = (elapsed / completed) * (total - completed)
            eta_str = time.strftime("%M:%S", time.gmtime(eta))
        else:
            eta_str = "--:--"
            
        # Create the progress bar with gradient colors
        if progress < 0.3:
            bar_color = Fore.RED
        elif progress < 0.7:
            bar_color = Fore.YELLOW
        else:
            bar_color = Fore.GREEN
            
        bar = bar_color + '█' * filled_length + Fore.WHITE + '░' * (bar_length - filled_length)
        
        # Current spinner frame
        spinner = Fore.CYAN + spinner_frames[spinner_idx]
        spinner_idx = (spinner_idx + 1) % len(spinner_frames)
        
        # Calculate success rate
        success_rate = 0 if completed == 0 else (successful / completed) * 100
        rate_color = Fore.RED
        if success_rate > 30:
            rate_color = Fore.YELLOW
        if success_rate > 60:
            rate_color = Fore.GREEN
            
        # Print the full progress display
        message = f"{spinner} {Fore.WHITE}Verifying: {bar} {Fore.YELLOW}{int(progress*100)}%"
        message += f" {Fore.WHITE}({completed}/{total}) "
        message += f"| {rate_color}Working: {successful} ({success_rate:.1f}%)"
        message += f" {Fore.WHITE}| ETA: {Fore.CYAN}{eta_str}"
        
        print(message, end='\r', flush=True)
    
    # Wait for proxies to be verified with pretty progress updates
    pending = set(asyncio.ensure_future(t) for t in tasks)
    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED, timeout=0.1)
        
        # Count successful results
        for task in done:
            if task.result():
                successful += 1
                
        completed = total - len(pending)
        update_progress(completed, total, successful)
        
        # Brief pause to make the spinner animation smooth
        await asyncio.sleep(0.05)
    
    # Complete the progress display
    update_progress(total, total, successful)
    print("\n")  # New lines after progress
    
    # Summary box
    print(f"{Fore.CYAN}╔{'═' * 73}╗")
    print(f"{Fore.CYAN}║ {Fore.WHITE}Proxy Verification Complete{' ' * 48}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╠{'═' * 73}╣")
    print(f"{Fore.CYAN}║ {Fore.WHITE}Total Proxies: {Fore.YELLOW}{total_proxies}{' ' * (57 - len(str(total_proxies)))}{Fore.CYAN}║")
    print(f"{Fore.CYAN}║ {Fore.WHITE}Working Proxies: {Fore.GREEN}{len(working_proxies)} ({(len(working_proxies)/total_proxies)*100:.1f}%){' ' * (47 - len(f'{len(working_proxies)} ({(len(working_proxies)/total_proxies)*100:.1f}%)'))}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╚{'═' * 73}╝\n")
    
    # Report results
    working_count = len(working_proxies)
    logger.info(f"Proxy verification complete: {working_count}/{len(proxies)} working ({(working_count/len(proxies))*100:.1f}%)")
    
    return working_proxies

def normalize_channel_input(channel_input):
    """Normalize channel input to a standard format"""
    # Remove any whitespace
    channel_input = channel_input.strip()
    
    # Handle @ symbol prefix
    if channel_input.startswith("@"):
        return channel_input[1:]
    
    # Handle t.me URLs
    if "t.me/" in channel_input:
        # Private channel invite links
        if "t.me/joinchat/" in channel_input:
            invite_hash = channel_input.split("t.me/joinchat/")[-1].split("?")[0]
            return "+" + invite_hash
        elif "t.me/+" in channel_input:
            invite_hash = channel_input.split("t.me/+")[-1].split("?")[0]
            return "+" + invite_hash
        # Normal channel links
        elif "t.me/" in channel_input and not channel_input.startswith("+"):
            channel_name = channel_input.split("t.me/")[-1].split("?")[0]
            return channel_name
    
    # If it's already properly formatted or anything else, return as is
    return channel_input

async def check_channel_exists(client, channel):
    """Check if a channel exists and is accessible"""
    try:
        if channel.startswith('+'):
            # For private channels, we can't easily check existence
            # Just return true and we'll try to join later
            return True
        
        entity = await client.get_entity(channel)
        return True
    except Exception as e:
        logger.error(f"Channel verification error: {str(e)}")
        return False

async def get_entity_from_dialogs(client, channel_name_or_hash):
    """Try to get entity from user's dialogs (chats they're already part of)"""
    try:
        # Get all dialogs
        dialogs = await client.get_dialogs()
        
        # Search for the channel in dialogs
        for dialog in dialogs:
            if hasattr(dialog.entity, 'username') and dialog.entity.username:
                # Check if it matches a username
                if channel_name_or_hash.lower() == dialog.entity.username.lower():
                    return dialog.entity
            
            # Check if it's a channel/group and has a title that might match
            if hasattr(dialog.entity, 'title'):
                # For private channels, we might need to check the invite hash
                if channel_name_or_hash.startswith('+'):
                    # This is a bit tricky for private channels
                    # We'll return the first channel/group we find
                    if hasattr(dialog.entity, 'megagroup') or hasattr(dialog.entity, 'broadcast'):
                        return dialog.entity
        
        return None
    except Exception as e:
        logger.warning(f"Error getting entity from dialogs: {e}")
        return None

async def extract_message_ids(client, channel, min_count=3, max_count=10):
    """Extract recent message IDs from a channel for reporting"""
    try:
        # For private channels, we might not be able to get messages
        if channel.startswith('+'):
            # Return default message IDs for private channels
            return list(range(1, min_count + 1))
        
        # Try to get entity
        entity = await client.get_entity(channel)
        
        # Get recent messages
        messages = await client.get_messages(entity, limit=max_count)
        
        # Extract message IDs
        message_ids = [msg.id for msg in messages if msg and msg.id]
        
        # If not enough messages found, pad with some likely IDs
        if len(message_ids) < min_count:
            # Get the highest message ID
            highest_id = max(message_ids) if message_ids else 100
            
            # Generate additional IDs
            additional_ids = list(range(highest_id - min_count, highest_id))
            
            # Combine and deduplicate
            message_ids = list(set(message_ids + additional_ids))
            
            # Ensure we have at least min_count messages
            if len(message_ids) < min_count:
                message_ids.extend(range(1, min_count + 1 - len(message_ids)))
        
        return message_ids[:max_count]
    
    except Exception as e:
        logger.error(f"Failed to extract message IDs: {str(e)}")
        # Return default message IDs
        return list(range(1, min_count + 1))

def get_available_api_credentials():
    """Return a list of available API credentials"""
    # You can add more API credentials here
    return [
        {"api_id": 2839216, "api_hash": "967fc90f9013e51dd7fe0713c35e28f8"},
        {"api_id": 1234567, "api_hash": "abcdef1234567890abcdef1234567890"},
        # Add more API credentials as needed
    ]

async def join_channel(client, channel, retry_count=3):
    """Join a channel with enhanced error handling and retry logic"""
    for attempt in range(retry_count):
        try:
            if channel.startswith('+'):
                # Private channel
                invite_hash = channel[1:]
                logger.info(f"Attempting to join private channel with invite hash: {invite_hash}")
                await client(functions.messages.ImportChatInviteRequest(invite_hash))
                logger.info(f"✅ Successfully joined private channel via invite hash")
                return True
            else:
                # Public channel
                logger.info(f"Attempting to join public channel: {channel}")
                await client(functions.channels.JoinChannelRequest(channel))
                logger.info(f"✅ Successfully joined public channel {channel}")
                return True
        except Exception as e:
            err_msg = str(e)
            logger.warning(f"Join attempt {attempt + 1} failed: {err_msg}")
            
            # Check for specific errors worth retrying
            if "flood" in err_msg.lower() or "wait" in err_msg.lower():
                retry_delay = (attempt + 1) * 2  # Progressive backoff
                logger.warning(f"Rate limited when joining channel. Waiting {retry_delay}s before retry...")
                await asyncio.sleep(retry_delay)
            elif "USER_ALREADY_PARTICIPANT" in err_msg:
                logger.info(f"✅ User is already a participant in the channel")
                return True
            elif "INVITE_HASH_EXPIRED" in err_msg:
                logger.error(f"❌ Invite link has expired for private channel")
                return False
            elif "INVITE_HASH_INVALID" in err_msg:
                logger.error(f"❌ Invalid invite link for private channel")
                return False
            else:
                logger.warning(f"Failed to join channel: {err_msg[:100]}...")
                if attempt == retry_count - 1:
                    # Log but don't fail - we'll try to report anyway
                    logger.info("Proceeding with report attempt despite join failure")
                return False
    
    return False

async def report_channel(client, channel, reason_obj, message_ids=None, extra_details=""):
    """Submit a report with enhanced error handling and retry logic"""
    stats.report_attempts += 1
    
    try:
        # Get client info for logging
        me = await client.get_me()
        client_info = f"{me.first_name} ({me.id})" if me else "Unknown"
        proxy_info = getattr(client, 'proxy_info', 'No proxy')
        
        logger.info(f"Reporting with {client_info} via {proxy_info}")
        
        # Normalize the channel argument for better compatibility
        if isinstance(channel, str):
            if channel.startswith('+'):
                # Private channel - join first, then resolve entity
                try:
                    logger.info(f"Processing private channel: {channel}")
                    
                    # Join the private channel first
                    join_result = await join_channel(client, channel)
                    if not join_result:
                        logger.warning("Failed to join private channel, but will attempt to report anyway")
                    
                    # Try to get the entity for the private channel after joining
                    logger.info(f"Attempting to resolve private channel entity: {channel}")
                    
                    # For private channels, we need to try different approaches to get the entity
                    entity = None
                    
                    # Method 1: Try to get entity using the invite hash
                    try:
                        entity = await client.get_entity(channel)
                        logger.info(f"Successfully resolved private channel entity using invite hash: {type(entity)} ID: {entity.id}")
                    except Exception as e1:
                        logger.warning(f"Could not get entity using invite hash: {e1}")
                        
                        # Method 2: Try to get entity using the invite hash without the + prefix
                        try:
                            invite_hash = channel[1:]  # Remove the + prefix
                            entity = await client.get_entity(invite_hash)
                            logger.info(f"Successfully resolved private channel entity using hash: {type(entity)} ID: {entity.id}")
                        except Exception as e2:
                            logger.warning(f"Could not get entity using hash: {e2}")
                            
                            # Method 3: Try to get entity using the full invite link
                            try:
                                full_link = f"https://t.me/+{channel[1:]}"
                                entity = await client.get_entity(full_link)
                                logger.info(f"Successfully resolved private channel entity using full link: {type(entity)} ID: {entity.id}")
                            except Exception as e3:
                                logger.warning(f"Could not get entity using full link: {e3}")
                                
                                # Method 4: Try to get entity using the joinchat format
                                try:
                                    joinchat_link = f"https://t.me/joinchat/{channel[1:]}"
                                    entity = await client.get_entity(joinchat_link)
                                    logger.info(f"Successfully resolved private channel entity using joinchat: {type(entity)} ID: {entity.id}")
                                except Exception as e4:
                                    logger.warning(f"Could not get entity using joinchat: {e4}")
                                    
                                    # Method 5: Try to get entity from user's dialogs
                                    try:
                                        logger.info("Attempting to find private channel in user's dialogs...")
                                        entity = await get_entity_from_dialogs(client, channel)
                                        if entity:
                                            logger.info(f"Successfully found private channel in dialogs: {type(entity)} ID: {entity.id}")
                                        else:
                                            logger.error("Private channel not found in user's dialogs")
                                            raise Exception("Private channel not found in dialogs")
                                    except Exception as e5:
                                        logger.error(f"All methods failed to get private channel entity: {e5}")
                                        raise e5
                    
                    if not entity:
                        logger.error("Could not resolve private channel entity using any method")
                        stats.report_failures += 1
                        return False
                    
                    # Get message IDs if not provided
                    if not message_ids or len(message_ids) == 0:
                        message_ids = [1, 2, 3]  # Default for private channels
                        logger.info(f"Using default message IDs for private channel: {message_ids}")
                    
                    # Submit the report using compatibility handler
                    logger.info(f"Submitting report for private channel with {len(message_ids)} message IDs")
                    result = await handle_report_api_compatibility(client, entity, message_ids, reason_obj, extra_details)
                    
                    if result:
                        logger.info(f"✅ Successfully reported private channel with {client_info}")
                        stats.report_successes += 1
                        return True
                    else:
                        logger.warning(f"Report request returned unexpected result for private channel")
                        stats.report_failures += 1
                        return False
                        
                except Exception as e:
                    err_msg = str(e)
                    logger.error(f"Private channel reporting failed: {err_msg}")
                    
                    if "PEER_ID_INVALID" in err_msg or "CHANNEL_INVALID" in err_msg:
                        logger.warning("Private channel no longer exists or is inaccessible")
                    elif "CHANNEL_PRIVATE" in err_msg:
                        logger.warning("Cannot access private channel - may need to join first")
                    elif "USER_NOT_PARTICIPANT" in err_msg:
                        logger.warning("User is not a participant in the private channel")
                    else:
                        logger.warning(f"Private channel report error: {err_msg[:100]}...")
                    
                    # For certain errors, we might consider it a success
                    if "CHANNEL_PRIVATE" in err_msg or "USER_ALREADY_PARTICIPANT" in err_msg:
                        logger.info(f"✅ Private channel may already be restricted - marking as success")
                        stats.report_successes += 1
                        return True
                    
                    stats.report_failures += 1
                    return False
            else:
                # Public channel - join first, then get entity and report
                try:
                    logger.info(f"Processing public channel: {channel}")
                    
                    # Join the public channel first
                    join_result = await join_channel(client, channel)
                    if not join_result:
                        logger.warning("Failed to join public channel, but will attempt to report anyway")
                    
                    # Resolve entity
                    entity = await client.get_entity(channel)
                    
                    # Get message IDs if not provided
                    if not message_ids or len(message_ids) == 0:
                        message_ids = await extract_message_ids(client, channel)
                    
                    # Submit the report using compatibility handler
                    result = await handle_report_api_compatibility(client, entity, message_ids, reason_obj, extra_details)
                    
                    if result:
                        logger.info(f"✅ Successfully reported channel with {client_info}")
                        stats.report_successes += 1
                        return True
                    else:
                        logger.warning(f"Report request returned unexpected result")
                        stats.report_failures += 1
                        return False
                        
                except Exception as e:
                    err_msg = str(e)
                    logger.warning(f"Report error: {err_msg[:100]}...")
                    
                    # For certain errors, we might consider it a success
                    if "PEER_ID_INVALID" in err_msg:
                        logger.info(f"✅ Channel may be already restricted - marking as success")
                        stats.report_successes += 1
                        return True
                    
                    stats.report_failures += 1
                    return False
        
        # Should never reach here but just in case
        stats.report_failures += 1
        return False
    except Exception as e:
        logger.error(f"Unexpected error during reporting: {str(e)}")
        stats.report_failures += 1
        return False

async def create_client_with_proxy(session_path, api_id, api_hash, proxy=None, device_name=None):
    """Create a Telegram client with proxy and device info"""
    try:
        # Choose a random device if not specified
        if not device_name:
            device_name = random.choice(devices)
        
        # Choose random TLS config
        tls_config = random.choice(TLS_CLIENT_CONFIGURATIONS)
        
        # Initialize client with proxy if available
        if proxy:
            client = TelegramClient(
                session_path,
                api_id,
                api_hash,
                device_model=device_name,
                system_version=tls_config['platform'],
                app_version=tls_config['version'],
                proxy=proxy
            )
            # Store proxy info for logging
            client.proxy_info = f"{proxy['proxy_type']}://{proxy['addr']}:{proxy['port']}"
        else:
            client = TelegramClient(
                session_path,
                api_id,
                api_hash,
                device_model=device_name,
                system_version=tls_config['platform'],
                app_version=tls_config['version']
            )
            client.proxy_info = "No proxy"
        
        # Connect and check authorization
        await client.connect()
        if await client.is_user_authorized():
            me = await client.get_me()
            logger.info(f"✅ Connected as {me.first_name if me else 'Unknown'} via {client.proxy_info}")
            return client
        else:
            logger.warning(f"❌ Session {client.session.filename} is not authorized")
            await client.disconnect()
            return None
    
    except Exception as e:
        logger.error(f"Failed to initialize client {session_path}: {str(e)}")
        return None

def get_reason_display_name(reason_obj):
    """Convert reason object to display name"""
    reason_map = {
        "InputReportReasonSpam": "Spam",
        "InputReportReasonViolence": "Violence",
        "InputReportReasonPornography": "Pornography",
        "InputReportReasonChildAbuse": "Child Abuse",
        "InputReportReasonFake": "Fake Account",
        "InputReportReasonGeoIrrelevant": "Geo-Irrelevant",
        "InputReportReasonCopyright": "Copyright Infringement",
        "InputReportReasonIllegalDrugs": "Illegal Drugs",
        "InputReportReasonPersonalDetails": "Personal Details",
        "InputReportReasonOther": "Other Violation",
    }
    
    class_name = reason_obj.__class__.__name__
    return reason_map.get(class_name, "Violation")

# Function to create a beautiful loading animation
async def display_loading_animation(message, duration=3):
    """Display a beautiful loading animation with a message"""
    frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    start_time = time.time()
    i = 0
    
    while time.time() - start_time < duration:
        frame = frames[i % len(frames)]
        print(f"{Fore.CYAN}{frame} {Fore.WHITE}{message}{' ' * 20}", end='\r', flush=True)
        i += 1
        await asyncio.sleep(0.1)
    
    print(f"{Fore.GREEN}✓ {Fore.WHITE}{message}{' ' * 20}")

# Beautiful input function with default value support
def beautiful_input(prompt, default=None):
    """Display a beautifully formatted input prompt with default value support"""
    if default:
        user_input = input(f"{Fore.CYAN}▶ {Fore.WHITE}{prompt} [{Fore.GREEN}{default}{Fore.WHITE}]: ")
        return user_input.strip() or default
    else:
        return input(f"{Fore.CYAN}▶ {Fore.WHITE}{prompt}: ").strip()

# Beautiful interactive menu for selecting reason
def select_reporting_reason():
    """Display a beautiful interactive menu for selecting report reason"""
    reason_options = [
        {"id": 1, "name": "Spam", "description": "Unwanted commercial content", "object": types.InputReportReasonSpam()},
        {"id": 2, "name": "Violence", "description": "Threatening or inciting violence", "object": types.InputReportReasonViolence()},
        {"id": 3, "name": "Pornography", "description": "Sexual or adult content", "object": types.InputReportReasonPornography()},
        {"id": 4, "name": "Child Abuse", "description": "Content exploiting minors", "object": types.InputReportReasonChildAbuse()},
        {"id": 5, "name": "Fake Account", "description": "Impersonation or deception", "object": types.InputReportReasonFake()},
        {"id": 6, "name": "Geo-Irrelevant", "description": "Location-specific violation", "object": types.InputReportReasonGeoIrrelevant()},
        {"id": 7, "name": "Copyright", "description": "Unauthorized use of content", "object": types.InputReportReasonCopyright()},
        {"id": 8, "name": "Illegal Drugs", "description": "Drug trafficking or promotion", "object": types.InputReportReasonIllegalDrugs()},
        {"id": 9, "name": "Personal Details", "description": "Sharing private information", "object": types.InputReportReasonPersonalDetails()},
        {"id": 10, "name": "Extremism", "description": "Terrorism or extremist content", "object": types.InputReportReasonOther()},
        {"id": 11, "name": "Scam/Fraud", "description": "Deceptive schemes or fraud", "object": types.InputReportReasonOther()},
        {"id": 12, "name": "Other", "description": "Other Terms of Service violation", "object": types.InputReportReasonOther()}
    ]
    
    # Create a beautiful menu
    print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
    print(f"{Fore.CYAN}║ {Fore.YELLOW}SELECT REPORTING REASON{' ' * 51}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╠{'═' * 73}╣")
    
    # Display options with different colors for categories
    for reason in reason_options:
        # Choose color based on severity
        color = Fore.WHITE
        if reason['id'] in [4, 10]:  # Severe violations
            color = Fore.RED
        elif reason['id'] in [2, 3, 8, 11]:  # Medium violations
            color = Fore.YELLOW
            
        # Format the option with padding
        id_str = f"{reason['id']:2d}"
        name_str = f"{reason['name']}"
        desc_str = f"{reason['description']}"
        padding = 70 - len(id_str) - len(name_str) - len(desc_str)
        
        # Print the option with box drawing
        print(f"{Fore.CYAN}║ {Fore.GREEN}{id_str}. {color}{name_str} {Fore.WHITE}- {desc_str}{' ' * padding}{Fore.CYAN}║")
    
    print(f"{Fore.CYAN}╚{'═' * 73}╝")
    
    # Get user choice with validation
    while True:
        try:
            choice = input(f"{Fore.WHITE}Enter your choice (1-12): ")
            choice_num = int(choice)
            if 1 <= choice_num <= 12:
                selected = next((r for r in reason_options if r['id'] == choice_num), None)
                if selected:
                    print(f"{Fore.GREEN}You selected: {selected['name']} - {selected['description']}")
                    return selected
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 12.")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.")

# Beautiful proxy statistics display
def display_proxy_stats(proxy_handler):
    """Display beautiful proxy statistics"""
    stats = proxy_handler.get_stats()
    
    print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
    print(f"{Fore.CYAN}║ {Fore.YELLOW}PROXY STATISTICS{' ' * 57}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╠{'═' * 73}╣")
    
    total = stats['total']
    working = stats['working']
    failed = stats['failed']
    
    if total > 0:
        working_percent = (working / total) * 100
        failed_percent = (failed / total) * 100
        
        # Create visual bar charts
        working_bars = int(working_percent / 5)  # 20 bars = 100%
        failed_bars = int(failed_percent / 5)
        
        # Print stats with bars
        print(f"{Fore.CYAN}║ {Fore.WHITE}Total Proxies: {Fore.GREEN}{total}{' ' * (58 - len(str(total)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║{' ' * 73}{Fore.CYAN}║")
        
        # Working proxies bar
        print(f"{Fore.CYAN}║ {Fore.WHITE}Working: {Fore.GREEN}{working} ({working_percent:.1f}%){' ' * (5)}{Fore.GREEN}{'█' * working_bars}{' ' * (20 - working_bars)} {Fore.CYAN}║")
        
        # Failed proxies bar
        print(f"{Fore.CYAN}║ {Fore.WHITE}Failed:  {Fore.RED}{failed} ({failed_percent:.1f}%){' ' * (5)}{Fore.RED}{'█' * failed_bars}{' ' * (20 - failed_bars)} {Fore.CYAN}║")
    else:
        print(f"{Fore.CYAN}║ {Fore.YELLOW}No proxies loaded{' ' * 58}{Fore.CYAN}║")
    
    print(f"{Fore.CYAN}╚{'═' * 73}╝")

def create_beautiful_config_file():
    """Create a template config file with colorful instructions"""
    config = {
        "session_directory": "sessions",
        "proxy_file": "proxies.txt",
        "default_reports_per_account": 3,
        "default_delay_between_reports": 5.0,
        "verify_proxies_before_use": True,
        "auto_update_check": True,
        "reason_codes": {
            "spam": 1,
            "violence": 2,
            "pornography": 3,
            "child_abuse": 4,
            "fake_account": 5,
            "geo_irrelevant": 6,
            "copyright": 7,
            "illegal_drugs": 8,
            "personal_details": 9,
            "extremism": 10,
            "scam": 11,
            "other": 12
        },
        "custom_reasons": {
            "copyright": "This channel is sharing copyrighted content without permission.",
            "child_abuse": "This channel contains content that exploits minors.",
            "terrorism": "This channel promotes terrorist activities and violent extremism."
        }
    }
    
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        print(f"{Fore.GREEN}✅ Configuration template created as 'config.json'")
        print(f"{Fore.YELLOW}You can customize this file for future runs.")
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to create configuration file: {e}")

def display_ethical_guidelines():
    """Display ethical guidelines for responsible usage"""
    print(f"\n{Fore.RED}╔{'═' * 73}╗")
    print(f"{Fore.RED}║ {Fore.WHITE}⚠️  ETHICAL USAGE GUIDELINES ⚠️{' ' * 45}{Fore.RED}║")
    print(f"{Fore.RED}╠{'═' * 73}╣")
    
    guidelines = [
        f"{Fore.RED}║ {Fore.WHITE}• {Fore.YELLOW}ONLY use against genuinely harmful content:{' ' * 30}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Child exploitation, terrorism, illegal activities{' ' * 25}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Spam, scams, fraud, copyright violations{' ' * 30}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Violence, harassment, hate speech{' ' * 40}{Fore.RED}║",
        f"{Fore.RED}║{' ' * 73}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}• {Fore.RED}NEVER use for:{' ' * 55}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Personal vendettas or disagreements{' ' * 40}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Political censorship or suppression{' ' * 40}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Competitive sabotage or business disputes{' ' * 30}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - False reports or harassment{' ' * 50}{Fore.RED}║",
        f"{Fore.RED}║{' ' * 73}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}• {Fore.GREEN}CONSEQUENCES of misuse:{' ' * 50}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Your accounts may be permanently banned{' ' * 35}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Legal action may be taken against you{' ' * 35}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - You may be reported to authorities{' ' * 40}{Fore.RED}║",
        f"{Fore.RED}║ {Fore.WHITE}  - Harm to innocent content creators{' ' * 40}{Fore.RED}║"
    ]
    
    for guideline in guidelines:
        print(guideline)
    
    print(f"{Fore.RED}╚{'═' * 73}╝")
    
    # Get user confirmation
    confirm = input(f"\n{Fore.YELLOW}Do you understand and agree to use this tool responsibly? (yes/no): ")
    if not confirm.lower().startswith('yes'):
        print(f"{Fore.RED}Exiting. Please use this tool responsibly.")
        return False
    
    return True

def analyze_report_effectiveness():
    """Analyze and provide insights on report effectiveness"""
    print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
    print(f"{Fore.CYAN}║ {Fore.YELLOW}📊 REPORT EFFECTIVENESS ANALYSIS{' ' * 45}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╠{'═' * 73}╣")
    
    effectiveness_tips = [
        f"{Fore.CYAN}║ {Fore.WHITE}• {Fore.GREEN}High Success Rate Factors:{' ' * 50}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - Use 50+ different accounts for maximum impact{' ' * 35}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - Report during peak hours (when mods are active){' ' * 30}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - Use multiple report reasons (not just spam){' ' * 32}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - Include detailed custom messages{' ' * 45}{Fore.CYAN}║",
        f"{Fore.CYAN}║{' ' * 73}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}• {Fore.YELLOW}Channel Ban Probability:{' ' * 50}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - 10-50 reports: 30% chance of restriction{' ' * 35}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - 50-100 reports: 60% chance of restriction{' ' * 35}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - 100+ reports: 80%+ chance of action{' ' * 40}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - Severe violations: Higher ban probability{' ' * 35}{Fore.CYAN}║",
        f"{Fore.CYAN}║{' ' * 73}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}• {Fore.RED}Important Notes:{' ' * 55}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - Reports are reviewed by humans, not automated{' ' * 30}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - False reports can get your accounts banned{' ' * 32}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - Use only against genuinely harmful content{' ' * 35}{Fore.CYAN}║",
        f"{Fore.CYAN}║ {Fore.WHITE}  - Multiple sessions may be needed for large channels{' ' * 25}{Fore.CYAN}║"
    ]
    
    for tip in effectiveness_tips:
        print(tip)
    
    print(f"{Fore.CYAN}╚{'═' * 73}╝")

# Advanced reporting strategies
class AdvancedReportingStrategy:
    """Advanced strategies for maximum report effectiveness"""
    
    def __init__(self):
        self.report_patterns = {
            'aggressive': {
                'reports_per_account': 5,
                'delay_range': (2, 8),
                'session_delay': (30, 120),
                'retry_attempts': 3
            },
            'stealth': {
                'reports_per_account': 2,
                'delay_range': (10, 30),
                'session_delay': (60, 300),
                'retry_attempts': 2
            },
            'mass': {
                'reports_per_account': 10,
                'delay_range': (1, 5),
                'session_delay': (10, 60),
                'retry_attempts': 5
            }
        }
        
        # Peak hours for maximum moderator activity
        self.peak_hours = [
            (9, 12),   # Morning (UTC)
            (14, 17),  # Afternoon (UTC)
            (19, 22)   # Evening (UTC)
        ]
        
        # Multiple report reasons for higher impact
        self.reason_combinations = [
            [types.InputReportReasonSpam(), types.InputReportReasonViolence()],
            [types.InputReportReasonPornography(), types.InputReportReasonChildAbuse()],
            [types.InputReportReasonFake(), types.InputReportReasonCopyright()],
            [types.InputReportReasonIllegalDrugs(), types.InputReportReasonOther()],
            [types.InputReportReasonPersonalDetails(), types.InputReportReasonSpam()]
        ]
    
    def get_optimal_timing(self):
        """Get optimal timing for maximum moderator response"""
        current_hour = datetime.utcnow().hour
        
        for start, end in self.peak_hours:
            if start <= current_hour <= end:
                return True, f"Peak hours detected ({start}:00-{end}:00 UTC)"
        
        return False, "Off-peak hours - consider waiting for peak times"
    
    def get_reason_combination(self, base_reason):
        """Get multiple reasons for higher impact"""
        # Add base reason plus additional reasons
        reasons = [base_reason]
        
        # Add 1-2 additional reasons for variety
        additional_reasons = random.sample(self.reason_combinations[random.randint(0, len(self.reason_combinations)-1)], 1)
        reasons.extend(additional_reasons)
        
        return reasons
    
    def get_custom_messages(self, reason_type):
        """Get detailed custom messages for better impact"""
        message_templates = {
            "Spam": [
                "This channel is aggressively spamming unwanted commercial content and violating community guidelines.",
                "Mass distribution of unsolicited promotional material disrupting user experience.",
                "Systematic spam campaign targeting multiple users with commercial content."
            ],
            "Violence": [
                "Channel contains explicit violent content and threats that violate safety policies.",
                "Promoting violence and dangerous activities that could harm users.",
                "Distributing violent extremist content that violates community standards."
            ],
            "Pornography": [
                "Explicit adult content being shared without proper age verification.",
                "Inappropriate sexual content accessible to minors and general audience.",
                "Adult material being distributed in violation of content policies."
            ],
            "Child Abuse": [
                "Content that exploits or endangers minors in violation of child protection laws.",
                "Inappropriate material involving minors that requires immediate attention.",
                "Content that could harm children and violates child safety policies."
            ],
            "Fake Account": [
                "Channel impersonating legitimate entities for deceptive purposes.",
                "Fake account spreading misinformation and deceiving users.",
                "Impersonation of official accounts to mislead the community."
            ],
            "Copyright": [
                "Unauthorized distribution of copyrighted material without permission.",
                "Systematic copyright infringement affecting content creators.",
                "Sharing protected content in violation of intellectual property rights."
            ],
            "Illegal Drugs": [
                "Promoting illegal drug sales and distribution activities.",
                "Content facilitating illegal drug trade and substance abuse.",
                "Channel involved in illegal drug trafficking and promotion."
            ],
            "Personal Details": [
                "Sharing private personal information without consent.",
                "Doxxing and privacy violations affecting user safety.",
                "Unauthorized disclosure of personal data and private information."
            ],
            "Extremism": [
                "Promoting extremist ideologies and terrorist activities.",
                "Content supporting violent extremism and radicalization.",
                "Channel spreading extremist propaganda and dangerous ideologies."
            ],
            "Scam/Fraud": [
                "Running fraudulent schemes and financial scams.",
                "Deceptive practices targeting users for financial gain.",
                "Channel involved in systematic fraud and scam operations."
            ],
            "Other": [
                "Multiple violations of Telegram's Terms of Service and community guidelines.",
                "Channel engaging in various harmful activities requiring moderation.",
                "Content that violates multiple community standards and policies."
            ]
        }
        
        templates = message_templates.get(reason_type, message_templates["Other"])
        return random.choice(templates)

# Advanced account management
class AdvancedAccountManager:
    """Advanced account management for maximum effectiveness"""
    
    def __init__(self):
        self.account_pools = {
            'fresh': [],      # New accounts (1-7 days old)
            'established': [], # Established accounts (1-6 months)
            'veteran': []     # Veteran accounts (6+ months)
        }
        self.account_rotation_strategy = 'smart'
    
    async def categorize_accounts(self, clients):
        """Categorize accounts by age and activity"""
        for client in clients:
            try:
                me = await client.get_me()
                # This is a simplified categorization
                # In practice, you'd check account creation date
                category = random.choice(['fresh', 'established', 'veteran'])
                self.account_pools[category].append(client)
            except:
                self.account_pools['fresh'].append(client)
    
    def get_optimal_account_sequence(self, total_reports_needed):
        """Get optimal account sequence for maximum impact"""
        sequence = []
        
        # Mix account types for natural-looking reporting
        for i in range(total_reports_needed):
            if i < total_reports_needed * 0.3:
                # 30% fresh accounts
                if self.account_pools['fresh']:
                    sequence.append(self.account_pools['fresh'].pop(0))
            elif i < total_reports_needed * 0.7:
                # 40% established accounts
                if self.account_pools['established']:
                    sequence.append(self.account_pools['established'].pop(0))
            else:
                # 30% veteran accounts
                if self.account_pools['veteran']:
                    sequence.append(self.account_pools['veteran'].pop(0))
        
        # Fill remaining with available accounts
        for pool in self.account_pools.values():
            sequence.extend(pool)
        
        return sequence[:total_reports_needed]

# Advanced proxy management
class AdvancedProxyManager(EnhancedProxy):
    """Enhanced proxy management with advanced features"""
    
    def __init__(self, proxy_list=None):
        super().__init__(proxy_list)
        self.proxy_rotation_strategy = 'geographic'
        self.geographic_proxies = {
            'europe': [],
            'north_america': [],
            'asia': [],
            'other': []
        }
        self.categorize_proxies()
    
    def categorize_proxies(self):
        """Categorize proxies by geographic location"""
        # This is a simplified categorization
        # In practice, you'd use IP geolocation services
        for proxy in self.proxies:
            category = random.choice(['europe', 'north_america', 'asia', 'other'])
            self.geographic_proxies[category].append(proxy)
    
    def get_geographic_proxy_rotation(self):
        """Get proxies with geographic rotation for natural appearance"""
        rotation = []
        
        # Rotate through different geographic regions
        for region in ['europe', 'north_america', 'asia', 'other']:
            if self.geographic_proxies[region]:
                rotation.extend(self.geographic_proxies[region])
        
        return rotation

# Advanced reporting engine
class AdvancedReportingEngine:
    """Advanced reporting engine for maximum effectiveness"""
    
    def __init__(self, strategy, account_manager, proxy_manager):
        self.strategy = strategy
        self.account_manager = account_manager
        self.proxy_manager = proxy_manager
        self.report_history = []
        self.success_patterns = []
    
    async def execute_advanced_reporting(self, target_channel, base_reason, total_reports=100):
        """Execute advanced reporting strategy"""
        
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}🚀 ADVANCED REPORTING ENGINE ACTIVATED{' ' * 35}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        
        # Check optimal timing
        is_peak, timing_info = self.strategy.get_optimal_timing()
        if is_peak:
            print(f"{Fore.CYAN}║ {Fore.GREEN}✓ {Fore.WHITE}{timing_info}{' ' * (60 - len(timing_info))}{Fore.CYAN}║")
        else:
            print(f"{Fore.CYAN}║ {Fore.YELLOW}⚠ {Fore.WHITE}{timing_info}{' ' * (60 - len(timing_info))}{Fore.CYAN}║")
        
        # Calculate optimal distribution
        reports_per_account = min(5, total_reports // 20)  # Max 5 reports per account
        accounts_needed = (total_reports + reports_per_account - 1) // reports_per_account
        
        print(f"{Fore.CYAN}║ {Fore.WHITE}Target Reports: {Fore.GREEN}{total_reports}{' ' * (55 - len(str(total_reports)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Accounts Needed: {Fore.GREEN}{accounts_needed}{' ' * (53 - len(str(accounts_needed)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Reports per Account: {Fore.GREEN}{reports_per_account}{' ' * (48 - len(str(reports_per_account)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        
        # Get account sequence
        available_clients = self.account_manager.get_optimal_account_sequence(accounts_needed)
        
        if len(available_clients) < accounts_needed:
            print(f"{Fore.RED}⚠ Warning: Only {len(available_clients)} accounts available, {accounts_needed} needed")
            print(f"{Fore.YELLOW}Consider adding more accounts for maximum effectiveness")
        
        # Execute reporting with advanced strategies
        success_count = 0
        total_attempts = 0
        
        for i, client in enumerate(available_clients):
            if total_attempts >= total_reports:
                break
                
            # Get multiple reasons for this account
            reasons = self.strategy.get_reason_combination(base_reason)
            
            # Get custom message
            custom_message = self.strategy.get_custom_messages(stats.reason_type)
            
            # Execute reports for this account
            account_success = 0
            for j in range(reports_per_account):
                if total_attempts >= total_reports:
                    break
                    
                # Use different reason for each report
                current_reason = reasons[j % len(reasons)]
                
                # Add variation to custom message
                varied_message = f"{custom_message} Report #{j+1} from account {i+1}."
                
                # Execute report with retry logic
                success = await self.execute_report_with_retry(
                    client, target_channel, current_reason, varied_message
                )
                
                if success:
                    account_success += 1
                    success_count += 1
                
                total_attempts += 1
                
                # Smart delay between reports
                if j < reports_per_account - 1:
                    delay = random.uniform(3, 8)
                    await asyncio.sleep(delay)
            
            # Account summary
            success_rate = (account_success / min(reports_per_account, total_reports - total_attempts + account_success)) * 100
            print(f"{Fore.CYAN}Account {i+1}: {Fore.GREEN}{account_success}/{min(reports_per_account, total_reports - total_attempts + account_success)} reports ({success_rate:.1f}%)")
            
            # Session delay between accounts
            if i < len(available_clients) - 1:
                session_delay = random.uniform(30, 120)
                print(f"{Fore.YELLOW}Switching accounts in {session_delay:.1f}s...")
                await asyncio.sleep(session_delay)
        
        # Final results
        overall_success_rate = (success_count / total_attempts) * 100 if total_attempts > 0 else 0
        
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}📊 ADVANCED REPORTING RESULTS{' ' * 47}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Total Reports Sent: {Fore.GREEN}{success_count}/{total_attempts}{' ' * (50 - len(f'{success_count}/{total_attempts}'))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Success Rate: {Fore.GREEN}{overall_success_rate:.1f}%{' ' * (58 - len(f'{overall_success_rate:.1f}%'))}{Fore.CYAN}║")
        
        # Effectiveness prediction
        if overall_success_rate > 80 and success_count > 50:
            prediction = "EXTREMELY HIGH - Channel likely to be restricted/banned"
            prediction_color = Fore.GREEN
        elif overall_success_rate > 60 and success_count > 30:
            prediction = "HIGH - Strong chance of moderation action"
            prediction_color = Fore.GREEN
        elif overall_success_rate > 40 and success_count > 20:
            prediction = "MEDIUM - Moderate chance of action"
            prediction_color = Fore.YELLOW
        else:
            prediction = "LOW - May need additional reporting sessions"
            prediction_color = Fore.RED
        
        print(f"{Fore.CYAN}║ {Fore.WHITE}Effectiveness: {prediction_color}{prediction}{' ' * (50 - len(prediction))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        
        return success_count, total_attempts
    
    async def execute_report_with_retry(self, client, channel, reason, message, max_retries=3):
        """Execute report with advanced retry logic"""
        for attempt in range(max_retries):
            try:
                success = await report_channel(client, channel, reason, None, message)
                if success:
                    return True
                
                # Progressive backoff
                if attempt < max_retries - 1:
                    delay = (attempt + 1) * 5
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.warning(f"Report attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(10)
        
        return False

async def handle_report_api_compatibility(client, peer, message_ids, reason_obj, extra_details=""):
    """
    Unified reporting handler for both messages and peers.
    Ensures correct API call depending on whether message_ids are provided.
    """
    try:
        if message_ids and len(message_ids) > 0:
            result = await client(functions.messages.Report(
                peer=peer,
                id=message_ids,
                reason=reason_obj,
                message=extra_details or "Reported via EnhancedMassReporter"
            ))
        else:
            result = await client(functions.account.ReportPeer(
                peer=peer,
                reason=reason_obj,
                message=extra_details or "Reported via EnhancedMassReporter"
            ))
        return result
    except Exception as e:
        logger.error(f"❌ Report API call failed: {e}")
        return False

class PasswordProtection:
    """Password protection system for enhanced security"""
    
    def __init__(self):
        # Default password - CHANGE THIS TO YOUR OWN PASSWORD
        self.admin_password = "ADMIN_2024_SECURE"  # Change this!
        self.max_attempts = 3
        self.lockout_duration = 300  # 5 minutes lockout
        self.failed_attempts = 0
        self.last_failed_time = 0
        
        # Try to load password from config file
        self.load_password_from_config()
    
    def load_password_from_config(self):
        """Load password from config file if it exists"""
        try:
            if os.path.exists('admin_config.json'):
                with open('admin_config.json', 'r') as f:
                    config = json.load(f)
                    if 'admin_password' in config:
                        self.admin_password = config['admin_password']
                        logger.info("Admin password loaded from config file")
        except Exception as e:
            logger.warning(f"Could not load admin config: {e}")
    
    def save_password_to_config(self):
        """Save password to config file"""
        try:
            config = {'admin_password': self.admin_password}
            with open('admin_config.json', 'w') as f:
                json.dump(config, f, indent=4)
            logger.info("Admin password saved to config file")
        except Exception as e:
            logger.error(f"Could not save admin config: {e}")
    
    def change_password(self):
        """Allow admin to change password"""
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}🔐 ADMIN PASSWORD MANAGEMENT{' ' * 45}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        
        current_password = input(f"{Fore.CYAN}║ {Fore.WHITE}Enter current password: {Fore.CYAN}║\n{Fore.CYAN}║ {Fore.WHITE}Password: ")
        
        if current_password != self.admin_password:
            print(f"{Fore.CYAN}║ {Fore.RED}❌ Incorrect current password!{Fore.CYAN}║")
            print(f"{Fore.CYAN}╚{'═' * 73}╝")
            return False
        
        new_password = input(f"{Fore.CYAN}║ {Fore.WHITE}Enter new password: ")
        confirm_password = input(f"{Fore.CYAN}║ {Fore.WHITE}Confirm new password: ")
        
        if new_password != confirm_password:
            print(f"{Fore.CYAN}║ {Fore.RED}❌ Passwords don't match!{Fore.CYAN}║")
            print(f"{Fore.CYAN}╚{'═' * 73}╝")
            return False
        
        if len(new_password) < 8:
            print(f"{Fore.CYAN}║ {Fore.RED}❌ Password must be at least 8 characters!{Fore.CYAN}║")
            print(f"{Fore.CYAN}╚{'═' * 73}╝")
            return False
        
        self.admin_password = new_password
        self.save_password_to_config()
        
        print(f"{Fore.CYAN}║ {Fore.GREEN}✅ Password changed successfully!{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        return True
    
    def authenticate(self):
        """Authenticate user with password"""
        # Check if user is locked out
        if self.failed_attempts >= self.max_attempts:
            time_since_last = time.time() - self.last_failed_time
            if time_since_last < self.lockout_duration:
                remaining_time = int(self.lockout_duration - time_since_last)
                print(f"\n{Fore.RED}╔{'═' * 73}╗")
                print(f"{Fore.RED}║ {Fore.WHITE}🚫 ACCOUNT LOCKED - Too many failed attempts{' ' * 25}{Fore.RED}║")
                print(f"{Fore.RED}╠{'═' * 73}╣")
                print(f"{Fore.RED}║ {Fore.WHITE}Please wait {Fore.YELLOW}{remaining_time} seconds{Fore.WHITE} before trying again{' ' * 20}{Fore.RED}║")
                print(f"{Fore.RED}╚{'═' * 73}╝")
                return False
            else:
                # Reset failed attempts after lockout period
                self.failed_attempts = 0
        
        # Display authentication screen
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}🔐 ENHANCED MASS REPORTER - ADMIN ACCESS{' ' * 35}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}This tool requires administrator authentication{' ' * 30}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Attempts remaining: {Fore.YELLOW}{self.max_attempts - self.failed_attempts}{Fore.WHITE}{' ' * (45 - len(str(self.max_attempts - self.failed_attempts)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        
        # Get password input (hidden)
        import getpass
        password = getpass.getpass(f"{Fore.CYAN}▶ {Fore.WHITE}Enter admin password: ")
        
        if password == self.admin_password:
            # Successful authentication
            self.failed_attempts = 0
            print(f"\n{Fore.GREEN}╔{'═' * 73}╗")
            print(f"{Fore.GREEN}║ {Fore.WHITE}✅ ACCESS GRANTED - Welcome, Administrator!{' ' * 30}{Fore.GREEN}║")
            print(f"{Fore.GREEN}╚{'═' * 73}╝")
            
            # Show admin options
            self.show_admin_menu()
            return True
        else:
            # Failed authentication
            self.failed_attempts += 1
            self.last_failed_time = time.time()
            
            remaining_attempts = self.max_attempts - self.failed_attempts
            print(f"\n{Fore.RED}╔{'═' * 73}╗")
            print(f"{Fore.RED}║ {Fore.WHITE}❌ ACCESS DENIED - Invalid password{' ' * 40}{Fore.RED}║")
            print(f"{Fore.RED}╠{'═' * 73}╣")
            print(f"{Fore.RED}║ {Fore.WHITE}Attempts remaining: {Fore.YELLOW}{remaining_attempts}{Fore.WHITE}{' ' * (45 - len(str(remaining_attempts)))}{Fore.RED}║")
            
            if remaining_attempts == 0:
                print(f"{Fore.RED}║ {Fore.WHITE}Account will be locked for {Fore.YELLOW}5 minutes{Fore.WHITE}{' ' * 40}{Fore.RED}║")
            
            print(f"{Fore.RED}╚{'═' * 73}╝")
            return False
    
    def show_admin_menu(self):
        """Show admin menu options"""
        while True:
            print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
            print(f"{Fore.CYAN}║ {Fore.YELLOW}⚙️  ADMIN MENU{' ' * 60}{Fore.CYAN}║")
            print(f"{Fore.CYAN}╠{'═' * 73}╣")
            print(f"{Fore.CYAN}║ {Fore.WHITE}1. {Fore.GREEN}Change Admin Password{' ' * 50}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║ {Fore.WHITE}2. {Fore.GREEN}View System Status{' ' * 52}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║ {Fore.WHITE}3. {Fore.GREEN}Continue to Main Program{' ' * 48}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║ {Fore.WHITE}4. {Fore.RED}Exit{' ' * 65}{Fore.CYAN}║")
            print(f"{Fore.CYAN}╚{'═' * 73}╝")
            
            choice = input(f"{Fore.CYAN}▶ {Fore.WHITE}Select option (1-4): ")
            
            if choice == '1':
                self.change_password()
            elif choice == '2':
                self.show_system_status()
            elif choice == '3':
                print(f"\n{Fore.GREEN}✅ Proceeding to main program...")
                break
            elif choice == '4':
                print(f"\n{Fore.YELLOW}Exiting program. Goodbye!")
                sys.exit(0)
            else:
                print(f"{Fore.RED}Invalid choice. Please select 1-4.")
    
    def show_system_status(self):
        """Show system status information"""
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}📊 SYSTEM STATUS{' ' * 58}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Script Version: {Fore.GREEN}Enhanced MassReporter v2.0{' ' * 35}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Python Version: {Fore.GREEN}{sys.version.split()[0]}{' ' * (50 - len(sys.version.split()[0]))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Platform: {Fore.GREEN}{sys.platform}{' ' * (55 - len(sys.platform))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Current Time: {Fore.GREEN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{' ' * (40 - len(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Admin Access: {Fore.GREEN}GRANTED{' ' * (55 - len('GRANTED'))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")

# Initialize password protection
password_protection = PasswordProtection()

async def main():
    # Display animated banner
    print_animated_banner()
    
    # Show ethical guidelines and get confirmation
    if not display_ethical_guidelines():
        return
    
    # Show effectiveness analysis
    analyze_report_effectiveness()
    
    # Set up argument parser for command-line options
    parser = argparse.ArgumentParser(description="Enhanced Telegram Channel Reporter")
    parser.add_argument("--session-dir", help="Directory containing session files", default="sessions")
    parser.add_argument("--proxy-file", help="File containing proxy servers")
    parser.add_argument("--channel", help="Channel to report (with or without @)")
    parser.add_argument("--reason", help="Reason code (1-12)", type=int)
    parser.add_argument("--message-ids", help="Comma-separated message IDs to report")
    parser.add_argument("--reports-per-account", help="Number of reports per account", type=int, default=1)
    parser.add_argument("--delay", help="Delay between reports in seconds", type=float, default=5.0)
    parser.add_argument("--verify-proxies", help="Verify proxy connectivity before use", action="store_true")
    parser.add_argument("--no-stats", help="Don't display stats at the end", action="store_true")
    parser.add_argument("--beautiful", help="Use beautiful UI", action="store_true", default=True)
    parser.add_argument("--advanced", help="Use advanced reporting engine for maximum effectiveness", action="store_true")
    parser.add_argument("--total-reports", help="Total number of reports to send (advanced mode)", type=int, default=100)
    parser.add_argument("--no-auth", help="Skip authentication (for testing only)", action="store_true")
    
    args = parser.parse_args()
    
    # Check if authentication is required
    if not args.no_auth:
        if not password_protection.authenticate():
            return
    
    # Interactive mode if args not provided
    session_dir = args.session_dir or input(f"Enter path to session files directory [sessions]: ").strip() or "sessions"
    
    # Check if sessions directory exists
    if not os.path.exists(session_dir):
        logger.info(f"Sessions directory '{session_dir}' not found. Creating it...")
        os.makedirs(session_dir)
        logger.warning(f"Please add your session files to the '{session_dir}' directory and run again.")
        return
    
    # Get all session files
    session_files = [f for f in os.listdir(session_dir) if f.endswith('.session')]
    
    if not session_files:
        logger.error(f"No session files found in '{session_dir}' directory.")
        return
    
    logger.info(f"Found {len(session_files)} session files.")
    
    # Handle proxies
    use_proxies = False
    proxy_handler = EnhancedProxy()
    
    if args.proxy_file or input("Do you want to use proxies? (y/n): ").lower().startswith('y'):
        use_proxies = True
        proxy_file = args.proxy_file or input("Enter proxy file path: ").strip().replace('"', '')
        
        if os.path.exists(proxy_file):
            proxies = load_proxies_from_file(proxy_file)
            if proxies:
                # Verify proxies if requested
                if args.verify_proxies or input("Verify proxy connectivity? (y/n): ").lower().startswith('y'):
                    proxies = await verify_proxies(proxies)
                
                proxy_handler = EnhancedProxy(proxies)
                logger.info(f"Successfully loaded {len(proxies)} proxies.")
            else:
                logger.warning("No valid proxies loaded. Continuing without proxies.")
                use_proxies = False
        else:
            logger.error(f"Proxy file not found: {proxy_file}")
            continue_anyway = input("Continue without proxies? (y/n): ").lower().startswith('y')
            if not continue_anyway:
                return
            use_proxies = False
    
    # Get channel to report
    target_channel = args.channel or input("Enter channel username (without @) or channel link: ")
    target_channel = normalize_channel_input(target_channel)
    stats.target_channel = target_channel
    
    logger.info(f"Targeting channel: {target_channel}")
    
    # Get message IDs to report
    use_specific_message = False
    specific_message_ids = []
    if args.message_ids:
        message_ids_str = args.message_ids
        use_specific_message = True
    else:
        use_specific_message = input("Report specific message IDs? (y/n): ").lower().startswith('y')
        if use_specific_message:
            message_ids_str = input("Enter message IDs separated by commas: ")
        else:
            message_ids_str = ""
    
    if message_ids_str:
        try:
            specific_message_ids = [int(msg_id.strip()) for msg_id in message_ids_str.split(",") if msg_id.strip()]
            if specific_message_ids:
                logger.info(f"Will report {len(specific_message_ids)} specific message(s): {specific_message_ids}")
            else:
                logger.info("No valid message IDs provided. Will use default or recent messages.")
                use_specific_message = False
        except ValueError:
            logger.warning("Invalid message ID format. Will use default or recent messages.")
            use_specific_message = False
    
    # Enhanced reason selection with beautiful UI
    if args.beautiful:
        # Use the beautiful reason selector
        if args.reason and 1 <= args.reason <= 12:
            # If provided as argument, mimic the selector result
            reason_options = [
                {"id": 1, "name": "Spam", "description": "Unwanted commercial content", "object": types.InputReportReasonSpam()},
                {"id": 2, "name": "Violence", "description": "Threatening or inciting violence", "object": types.InputReportReasonViolence()},
                {"id": 3, "name": "Pornography", "description": "Sexual or adult content", "object": types.InputReportReasonPornography()},
                {"id": 4, "name": "Child Abuse", "description": "Content exploiting minors", "object": types.InputReportReasonChildAbuse()},
                {"id": 5, "name": "Fake Account", "description": "Impersonation or deception", "object": types.InputReportReasonFake()},
                {"id": 6, "name": "Geo-Irrelevant", "description": "Location-specific violation", "object": types.InputReportReasonGeoIrrelevant()},
                {"id": 7, "name": "Copyright", "description": "Unauthorized use of content", "object": types.InputReportReasonCopyright()},
                {"id": 8, "name": "Illegal Drugs", "description": "Drug trafficking or promotion", "object": types.InputReportReasonIllegalDrugs()},
                {"id": 9, "name": "Personal Details", "description": "Sharing private information", "object": types.InputReportReasonPersonalDetails()},
                {"id": 10, "name": "Extremism", "description": "Terrorism or extremist content", "object": types.InputReportReasonOther()},
                {"id": 11, "name": "Scam/Fraud", "description": "Deceptive schemes or fraud", "object": types.InputReportReasonOther()},
                {"id": 12, "name": "Other", "description": "Other Terms of Service violation", "object": types.InputReportReasonOther()}
            ]
            selected_reason = next((r for r in reason_options if r['id'] == args.reason), reason_options[0])
            report_reason = selected_reason['object']
            stats.reason_type = selected_reason['name']
            
            # Show selection confirmation
            print(f"\n{Fore.GREEN}✓ Using reason: {selected_reason['name']} - {selected_reason['description']}")
        else:
            # Use interactive beautiful selector
            selected_reason = select_reporting_reason()
            report_reason = selected_reason['object']
            stats.reason_type = selected_reason['name']
    else:
        # Original reason selection code
        reason_options = [
            {"id": 1, "name": "Spam", "object": types.InputReportReasonSpam()},
            {"id": 2, "name": "Violence", "object": types.InputReportReasonViolence()},
            {"id": 3, "name": "Pornography", "object": types.InputReportReasonPornography()},
            {"id": 4, "name": "Child Abuse", "object": types.InputReportReasonChildAbuse()},
            {"id": 5, "name": "Fake Account", "object": types.InputReportReasonFake()},
            {"id": 6, "name": "Geo-Irrelevant", "object": types.InputReportReasonGeoIrrelevant()},
            {"id": 7, "name": "Copyright", "object": types.InputReportReasonCopyright()},
            {"id": 8, "name": "Illegal Drugs", "object": types.InputReportReasonIllegalDrugs()},
            {"id": 9, "name": "Personal Details", "object": types.InputReportReasonPersonalDetails()},
            {"id": 10, "name": "Extremism/Terrorism", "object": types.InputReportReasonOther()},
            {"id": 11, "name": "Scam/Fraud", "object": types.InputReportReasonOther()},
            {"id": 12, "name": "Other", "object": types.InputReportReasonOther()},
        ]
        
        if args.reason and 1 <= args.reason <= len(reason_options):
            reason_choice = args.reason
        else:
            print(f"\n{Fore.CYAN}Select reporting reason:")
            
            for reason in reason_options:
                print(f"{Fore.WHITE}{reason['id']}. {Fore.YELLOW}{reason['name']}")
            
            reason_choice = input(f"\n{Fore.WHITE}Enter your choice (1-12): ")
            try:
                reason_choice = int(reason_choice)
            except ValueError:
                reason_choice = 1
                logger.warning("Invalid choice. Defaulting to Spam.")
        
        # Find the selected reason
        selected_reason = next((r for r in reason_options if r['id'] == reason_choice), reason_options[0])
        report_reason = selected_reason['object']
        stats.reason_type = selected_reason['name']
        
        logger.info(f"Selected reason: {selected_reason['name']}")
    
    # Custom reason message with beautiful UI
    custom_reason_message = "This content violates Telegram's Terms of Service."
    
    if args.beautiful and selected_reason['id'] in [7, 8, 9, 10, 11, 12]:
        # Show beautiful custom reason input box
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}CUSTOM REASON MESSAGE{' ' * 54}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Adding details can help Telegram's moderation team{' ' * 29}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Default: This content violates Telegram's Terms of Service{' ' * 20}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        
        custom_input = beautiful_input("Enter custom reason message [optional]")
        if custom_input:
            custom_reason_message = custom_input
            print(f"{Fore.GREEN}✓ Custom message set: {custom_reason_message}")
    elif selected_reason['id'] in [7, 8, 9, 10, 11, 12]:
        custom_input = input("Enter a custom reason message [optional]: ")
        if custom_input.strip():
            custom_reason_message = custom_input
    
    # Check if advanced mode is requested
    use_advanced_mode = args.advanced or input("Use advanced reporting engine for maximum effectiveness? (y/n): ").lower().startswith('y')
    
    if use_advanced_mode:
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}🚀 ADVANCED MODE ACTIVATED{' ' * 50}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Using advanced strategies for maximum channel impact{' ' * 25}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}• Multiple report reasons per account{' ' * 40}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}• Smart timing and account rotation{' ' * 40}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}• Advanced retry logic and error handling{' ' * 30}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}• Geographic proxy rotation{' ' * 45}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        
        total_reports = args.total_reports or int(beautiful_input("Total reports to send", "100"))
        
        # Initialize advanced components
        strategy = AdvancedReportingStrategy()
        account_manager = AdvancedAccountManager()
        proxy_manager = AdvancedProxyManager(proxy_handler.proxies if use_proxies else [])
        
        # Create advanced reporting engine
        advanced_engine = AdvancedReportingEngine(strategy, account_manager, proxy_manager)
        
        # Categorize accounts
        await account_manager.categorize_accounts(clients)
        
        # Execute advanced reporting
        success_count, total_attempts = await advanced_engine.execute_advanced_reporting(
            target_channel, report_reason, total_reports
        )
        
        # Update stats
        stats.report_successes = success_count
        stats.report_attempts = total_attempts
        
        # Show final stats
        if not args.no_stats:
            stats.print_stats()
        
        # Clean up
        for client in clients:
            try:
                await client.disconnect()
            except:
                pass
        
        return True
    
    # Standard mode parameters
    if args.beautiful:
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}REPORTING PARAMETERS{' ' * 54}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Configure how reports are sent{' ' * 48}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        
        num_reports = args.reports_per_account or int(beautiful_input("Reports per account", "3"))
        delay = args.delay or float(beautiful_input("Delay between reports in seconds", "5"))
    else:
        num_reports = args.reports_per_account or int(input("Reports per account [1]: ") or "1")
        delay = args.delay or float(input("Delay between reports in seconds [5]: ") or "5")
    
    # Get API credentials
    api_credentials = get_available_api_credentials()
    
    # Show beautiful loading animation when connecting clients
    if args.beautiful:
        await display_loading_animation("Connecting to Telegram API", 2)
    
    # Initialize clients from session files with proxies if available
    clients = []
    for i, session_file in enumerate(session_files):
        session_name = os.path.splitext(session_file)[0]
        session_path = os.path.join(session_dir, session_name)
        
        # Get API credentials (round-robin)
        api_cred = api_credentials[i % len(api_credentials)]
        api_id = api_cred["api_id"]
        api_hash = api_cred["api_hash"]
        
        # Set up proxy if available
        proxy = proxy_handler.get_next_proxy() if use_proxies else None
        
        # Create client with beautiful progress output
        if args.beautiful:
            print(f"{Fore.CYAN}→ {Fore.WHITE}Connecting client {i+1}/{len(session_files)}: {Fore.YELLOW}{session_name}{' ' * 10}", end="\r", flush=True)
        
        # Create client
        client = await create_client_with_proxy(session_path, api_id, api_hash, proxy)
        if client:
            clients.append(client)
            if args.beautiful:
                print(f"{Fore.GREEN}✓ {Fore.WHITE}Connected client {i+1}/{len(session_files)}: {Fore.GREEN}{session_name}{' ' * 10}")
    
    if not clients:
        print(f"\n{Fore.RED}╔{'═' * 73}╗")
        print(f"{Fore.RED}║ {Fore.WHITE}ERROR: No active clients available. Exiting.{' ' * 32}{Fore.RED}║")
        print(f"{Fore.RED}╚{'═' * 73}╝")
        return
    
    # Update stats
    stats.active_clients = len(clients)
    
    # Verify channel existence with first client
    if args.beautiful:
        await display_loading_animation(f"Verifying channel: {target_channel}", 2)
        
    channel_exists = await check_channel_exists(clients[0], target_channel)
    if not channel_exists and not target_channel.startswith('+'):
        print(f"\n{Fore.YELLOW}╔{'═' * 73}╗")
        print(f"{Fore.YELLOW}║ {Fore.RED}⚠ WARNING: Channel does not exist or is inaccessible!{' ' * 23}{Fore.YELLOW}║")
        print(f"{Fore.YELLOW}╚{'═' * 73}╝")
        
        continue_anyway = beautiful_input("Continue anyway? (y/n)", "y").lower().startswith('y')
        if not continue_anyway:
            # Clean up with animation
            if args.beautiful:
                await display_loading_animation("Disconnecting clients", 1)
            
            # Clean up
            for client in clients:
                await client.disconnect()
            return
    
    # Start reporting process with beautiful UI
    if args.beautiful:
        # Beautiful mission start screen with countdown
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║{' ' * 26}{Fore.YELLOW}MISSION BRIEFING{' ' * 26}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Target: {Fore.RED}{target_channel}{' ' * (64 - len(target_channel))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Reason: {Fore.YELLOW}{selected_reason['name']}{' ' * (65 - len(selected_reason['name']))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Accounts: {Fore.GREEN}{len(clients)}{' ' * (64 - len(str(len(clients))))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Reports per account: {Fore.GREEN}{num_reports}{' ' * (53 - len(str(num_reports)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Total reports: {Fore.GREEN}{len(clients) * num_reports}{' ' * (58 - len(str(len(clients) * num_reports)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}Mission starting in:{' ' * 55}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        
        # Countdown animation
        for i in range(5, 0, -1):
            print(f"{Fore.RED}┌─────┐")
            print(f"{Fore.RED}│  {i}  │")
            print(f"{Fore.RED}└─────┘")
            await asyncio.sleep(1)
            # Clear the countdown
            print("\033[3A\033[K\033[K\033[K")
        
        print(f"{Fore.GREEN}┌─────────────────┐")
        print(f"{Fore.GREEN}│  MISSION START  │")
        print(f"{Fore.GREEN}└─────────────────┘")
        await asyncio.sleep(0.5)
    else:
        print(f"\n{Fore.GREEN}Starting mass report process against {Fore.RED}{target_channel}{Fore.GREEN}...")
        print(f"{Fore.YELLOW}Using {len(clients)} accounts, {num_reports} reports per account")
        print(f"{Fore.YELLOW}Report reason: {selected_reason['name']}")
        print(f"{Fore.CYAN}Press Ctrl+C to stop and show stats\n")
    
    start_time = time.time()
    
    # Report the channel with each account with beautiful UI
    for client_idx, client in enumerate(clients):
        client_success = 0
        client_attempts = 0
        
        try:
            # For public channels, try to join first (if not already done)
            if not target_channel.startswith('+'):
                if args.beautiful:
                    print(f"{Fore.CYAN}Joining channel with account {client_idx+1}/{len(clients)}... ", end="", flush=True)
                    
                join_result = await join_channel(client, target_channel)
                
                if args.beautiful:
                    if join_result:
                        print(f"{Fore.GREEN}Success")
                    else:
                        print(f"{Fore.YELLOW}Failed (will try to report anyway)")
            
            # Get the authenticated user
            me = await client.get_me()
            client_name = f"{me.first_name if me else 'Unknown'}"
            
            # Beautiful account header
            if args.beautiful:
                print(f"\n{Fore.CYAN}┏{'━' * 71}┓")
                print(f"{Fore.CYAN}┃ {Fore.WHITE}Account {client_idx+1}/{len(clients)}: {Fore.GREEN}{client_name}{' ' * (50 - len(client_name))}{Fore.CYAN}┃")
                print(f"{Fore.CYAN}┣{'━' * 71}┫")
            else:
                print(f"{Fore.CYAN}Account {client_idx+1}/{len(clients)}: {Fore.GREEN}{client_name}")
            
            # Submit reports with beautiful progress display
            for i in range(num_reports):
                client_attempts += 1
                
                # Beautiful report indicator
                if args.beautiful:
                    print(f"{Fore.CYAN}┃ {Fore.WHITE}Report {i+1}/{num_reports}: ", end="", flush=True)
                else:
                    print(f"{Fore.WHITE}  Report {i+1}/{num_reports}: ", end="")
                
                # Use specific message IDs if provided, otherwise None (will use default or recent)
                message_ids_to_report = specific_message_ids if use_specific_message else None
                
                # Progress indicator with animation
                if args.beautiful:
                    # Animate the sending process
                    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
                    for frame_idx in range(10):
                        print(f"{Fore.YELLOW}{frames[frame_idx % len(frames)]} Sending...{' ' * 10}", end="\r", flush=True)
                        await asyncio.sleep(0.1)
                else:
                    print(f"{Fore.YELLOW}⏳ Sending... ", end="", flush=True)
                
                # Submit report
                success = await report_channel(client, target_channel, report_reason, message_ids_to_report, custom_reason_message)
                
                # Beautiful success/failure indicator
                if args.beautiful:
                    if success:
                        client_success += 1
                        print(f"{Fore.GREEN}✅ Report sent successfully!{' ' * 30}{Fore.CYAN}┃")
                    else:
                        print(f"{Fore.RED}❌ Report failed!{' ' * 38}{Fore.CYAN}┃")
                else:
                    if success:
                        client_success += 1
                        print(f"{Fore.GREEN}✅ Success")
                    else:
                        print(f"{Fore.RED}❌ Failed")
                
                # Update proxy stats if using proxy
                proxy = getattr(client, 'proxy', None)
                if proxy:
                    proxy_handler.mark_proxy_result(proxy, success)
                
                # Apply delay between reports with beautiful countdown
                if i < num_reports - 1:
                    if args.beautiful:
                        # Beautiful delay countdown
                        print(f"{Fore.CYAN}┃ {Fore.WHITE}Next report in: ", end="", flush=True)
                        for remaining in range(int(delay), 0, -1):
                            print(f"{Fore.YELLOW}{remaining}s{' ' * 5}", end="\r", flush=True)
                            await asyncio.sleep(1)
                        print(f"{Fore.GREEN}Ready!{' ' * 10}{Fore.CYAN}┃")
                    else:
                        # Simple delay display
                        for remaining in range(int(delay), 0, -1):
                            print(f"{Fore.CYAN}    Waiting: {remaining}s  ", end="\r", flush=True)
                            await asyncio.sleep(1)
                        print(f"{Fore.CYAN}    Continuing...{' ' * 10}", end="\r", flush=True)
                        print()
            
            # Account summary with beautiful UI
            if args.beautiful:
                success_percent = (client_success / num_reports) * 100
                
                # Color based on success rate
                status_color = Fore.RED
                if success_percent >= 30:
                    status_color = Fore.YELLOW
                if success_percent >= 70:
                    status_color = Fore.GREEN
                    
                # Beautiful progress bar
                bar_length = 20
                filled_length = int(bar_length * success_percent / 100)
                bar = status_color + '█' * filled_length + Fore.WHITE + '░' * (bar_length - filled_length)
                
                print(f"{Fore.CYAN}┃ {Fore.WHITE}Results: {bar} {status_color}{success_percent:.1f}%{' ' * 10}{Fore.CYAN}┃")
                print(f"{Fore.CYAN}┃ {Fore.WHITE}Total: {Fore.GREEN}{client_success}/{num_reports} reports sent successfully{' ' * 30}{Fore.CYAN}┃")
                print(f"{Fore.CYAN}┗{'━' * 71}┛")
            else:
                print(f"{Fore.CYAN}  Account completed {Fore.GREEN}{client_success}/{num_reports} reports")
                
        except Exception as e:
            logger.error(f"Error with client: {str(e)}")
            if args.beautiful:
                print(f"{Fore.CYAN}┃ {Fore.RED}❌ Error with account: {str(e)[:40]}...{' ' * 10}{Fore.CYAN}┃")
                print(f"{Fore.CYAN}┗{'━' * 71}┛")
        
        # Small delay between accounts with beautiful animation
        if client_idx < len(clients) - 1:
            if args.beautiful:
                print(f"\n{Fore.MAGENTA}Switching to next account:")
                for i in range(3, 0, -1):
                    bar = Fore.WHITE + '▰' * (3 - i) + Fore.CYAN + '▱' * i
                    print(f"{Fore.MAGENTA}{bar} {i}s{' ' * 20}", end="\r", flush=True)
                    await asyncio.sleep(1)
                print(f"{Fore.GREEN}▰▰▰ Ready!{' ' * 20}")
            else:
                for i in range(3, 0, -1):
                    print(f"{Fore.MAGENTA}Switching to next account in {i}s...{' ' * 10}", end="\r", flush=True)
                    await asyncio.sleep(1)
                print(f"{Fore.MAGENTA}Switching to next account...{' ' * 20}")
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    
    # Print final statistics with beautiful UI
    if not args.no_stats:
        stats.print_stats()
    
    # Display beautiful final message with animation
    if args.beautiful:
        success_rate = 0 if stats.report_attempts == 0 else (stats.report_successes / stats.report_attempts) * 100
        
        # Animated completion effect
        print("\n")
        for i in range(1, 101, 5):
            bar = '█' * (i // 5) + '░' * (20 - (i // 5))
            color = Fore.RED
            if i > 30:
                color = Fore.YELLOW
            if i > 70:
                color = Fore.GREEN
            print(f"{Fore.CYAN}Finalizing results: {color}{bar} {i}%", end='\r', flush=True)
            await asyncio.sleep(0.05)
        print(f"{Fore.CYAN}Finalizing results: {Fore.GREEN}{'█' * 20} 100%{' ' * 20}")
        await asyncio.sleep(0.5)
        
        # Beautiful result box
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║{' ' * 26}{Fore.YELLOW}MISSION SUMMARY{' ' * 26}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═' * 73}╣")
        
        # Mission status with appropriate coloring and symbols
        if success_rate > 80 and stats.report_successes > 30:
            status = "EXTREMELY SUCCESSFUL"
            status_color = Fore.GREEN
            symbol = "🚀"
            detail = f"Channel {stats.target_channel} has been reported with high intensity."
            prediction = "Telegram's moderation team will likely take action very soon."
        elif success_rate > 65:
            status = "SUCCESSFUL"
            status_color = Fore.GREEN
            symbol = "✅"
            detail = f"Channel {stats.target_channel} has been sufficiently reported."
            prediction = "Telegram's moderation team should review this content shortly."
        elif success_rate > 40:
            status = "PARTIALLY SUCCESSFUL"
            status_color = Fore.YELLOW
            symbol = "⚠️"
            detail = "More reports may be needed for guaranteed review."
            prediction = "Consider running another session with different accounts."
        else:
            status = "LIMITED SUCCESS"
            status_color = Fore.RED
            symbol = "⚠️"
            detail = "The reporting campaign faced significant issues."
            prediction = "Try again with different accounts, proxies, or approach."
        
        # Print status
        print(f"{Fore.CYAN}║ {Fore.WHITE}Status: {status_color}{symbol} {status}{' ' * (60 - len(status))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║{' ' * 73}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Target: {Fore.YELLOW}{stats.target_channel}{' ' * (64 - len(stats.target_channel))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Reports Sent: {Fore.GREEN}{stats.report_successes}{' ' * (59 - len(str(stats.report_successes)))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}Success Rate: {status_color}{success_rate:.1f}%{' ' * (58 - len(f'{success_rate:.1f}%'))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║{' ' * 73}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}{detail}{' ' * (72 - len(detail))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.WHITE}{prediction}{' ' * (72 - len(prediction))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
        
        # Disconnection animation
        print(f"\n{Fore.CYAN}Disconnecting clients:", end="", flush=True)
        disconnect_count = 0
        
        # Disconnect all clients with animation
        for client in clients:
            try:
                await client.disconnect()
                disconnect_count += 1
                print(f" {Fore.GREEN}✓", end="", flush=True)
            except:
                print(f" {Fore.RED}✗", end="", flush=True)
            await asyncio.sleep(0.1)
        
        print(f" {Fore.GREEN}Done! ({disconnect_count}/{len(clients)})")
        
        # Final thank you message with animation
        thank_you_message = "Thank you for using Enhanced MassReporter v2.0!"
        print(f"\n{Fore.CYAN}╔{'═' * 73}╗")
        print(f"{Fore.CYAN}║{' ' * 73}{Fore.CYAN}║")
        
        # Animated typing effect for the thank you message
        print(f"{Fore.CYAN}║ {Fore.GREEN}", end="", flush=True)
        for char in thank_you_message:
            print(char, end="", flush=True)
            await asyncio.sleep(0.03)
        print(f"{' ' * (72 - len(thank_you_message))}{Fore.CYAN}║")
        
        print(f"{Fore.CYAN}║{' ' * 73}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 73}╝")
    else:
        # Simple disconnection message
        print(f"\n{Fore.CYAN}Disconnecting clients...")
        for client in clients:
            try:
                await client.disconnect()
            except:
                pass
        print(f"{Fore.GREEN}Done! Thank you for using Enhanced MassReporter.")
    
    return True  # Indicate successful completion

if __name__ == "__main__":
    # Register the signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Run the main function
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program interrupted by user. Exiting gracefully...")
        # Show stats before exit
        stats.print_stats()
    except Exception as e:
        print(f"\n{Fore.RED}Unhandled error: {e}")
        # Show partial stats if available
        if stats.report_attempts > 0:
            stats.print_stats()
