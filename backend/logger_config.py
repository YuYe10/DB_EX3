"""
Advanced logging configuration with color support for zsh shell.
"""
import logging
import os
from datetime import datetime

# ANSI 颜色代码
class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # Emoji icons for different log types
    EMOJI_MAP = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'SUCCESS': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔴',
        'REQUEST': '→',
        'RESPONSE': '←',
        'DATABASE': '💾',
        'AUTH': '🔐',
        'VALIDATION': '✓',
    }
    
    # Color mapping for log levels
    LEVEL_COLORS = {
        'DEBUG': Colors.BRIGHT_BLACK,
        'INFO': Colors.BRIGHT_BLUE,
        'SUCCESS': Colors.BRIGHT_GREEN,
        'WARNING': Colors.BRIGHT_YELLOW,
        'ERROR': Colors.BRIGHT_RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }
    
    # HTTP method colors
    METHOD_COLORS = {
        'GET': Colors.CYAN,
        'POST': Colors.GREEN,
        'PUT': Colors.YELLOW,
        'DELETE': Colors.RED,
        'PATCH': Colors.MAGENTA,
        'OPTIONS': Colors.BRIGHT_BLACK,
    }
    
    # HTTP status code colors
    def get_status_color(self, status_code):
        """Get color for HTTP status code"""
        status_code = int(status_code) if isinstance(status_code, (int, str)) else 0
        if status_code >= 500:
            return Colors.BRIGHT_RED
        elif status_code >= 400:
            return Colors.BRIGHT_YELLOW
        elif status_code >= 300:
            return Colors.BRIGHT_CYAN
        elif status_code >= 200:
            return Colors.BRIGHT_GREEN
        else:
            return Colors.BRIGHT_BLACK
    
    def format(self, record):
        """Format log record with colors"""
        # Get base info
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        level_name = record.levelname
        message = record.getMessage()
        
        # Get appropriate color and emoji
        color = self.LEVEL_COLORS.get(level_name, Colors.RESET)
        emoji = self.EMOJI_MAP.get(level_name, '•')
        
        # Parse special log types from message
        if message.startswith('REQUEST:'):
            emoji = self.EMOJI_MAP['REQUEST']
            color = Colors.BRIGHT_BLUE
        elif message.startswith('RESPONSE:'):
            emoji = self.EMOJI_MAP['RESPONSE']
            # Extract status code for color coding
            if '200' in message:
                color = Colors.BRIGHT_GREEN
            elif '400' in message or '404' in message:
                color = Colors.BRIGHT_YELLOW
            elif '500' in message:
                color = Colors.BRIGHT_RED
            else:
                color = Colors.BRIGHT_CYAN
        elif message.startswith('DATABASE:'):
            emoji = self.EMOJI_MAP['DATABASE']
            color = Colors.BRIGHT_MAGENTA
        elif message.startswith('AUTH:'):
            emoji = self.EMOJI_MAP['AUTH']
            color = Colors.BRIGHT_CYAN
        elif 'ERROR' in level_name or 'error' in message.lower():
            emoji = self.EMOJI_MAP['ERROR']
            color = Colors.BRIGHT_RED
        elif 'SUCCESS' in message.upper():
            emoji = self.EMOJI_MAP['SUCCESS']
            color = Colors.BRIGHT_GREEN
        
        # Parse HTTP methods from message
        method_color = Colors.RESET
        for method in self.METHOD_COLORS.keys():
            if f' {method} ' in message:
                method_color = self.METHOD_COLORS[method]
                message = message.replace(f' {method} ', f'{method_COLOR}{method}{Colors.RESET} ')
                break
        
        # Format the log line
        timestamp_str = f"{Colors.DIM}{timestamp}{Colors.RESET}"
        level_str = f"{color}{emoji} {level_name:8}{Colors.RESET}"
        
        # Add source info if available
        source = ""
        if record.name and record.name != 'root':
            source = f"{Colors.DIM}[{record.name}]{Colors.RESET}"
        
        # Build final log line
        if source:
            log_line = f"{timestamp_str} {level_str} {source} {message}"
        else:
            log_line = f"{timestamp_str} {level_str} {message}"
        
        return log_line


class PlainFormatter(logging.Formatter):
    """Plain formatter for file logging (no colors)"""
    
    def format(self, record):
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        level_name = record.levelname
        message = record.getMessage()
        source = f"[{record.name}]" if record.name and record.name != 'root' else ""
        
        if source:
            return f"{timestamp} {level_name:8} {source} {message}"
        else:
            return f"{timestamp} {level_name:8} {message}"


def setup_logging(log_dir='logs', console_level=logging.DEBUG, file_level=logging.INFO):
    """
    Set up logging with colored console output and plain file output.
    
    Args:
        log_dir: Directory for log files
        console_level: Logging level for console output
        file_level: Logging level for file output
    """
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (colored)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler (plain text)
    file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'))
    file_handler.setLevel(file_level)
    file_handler.setFormatter(PlainFormatter())
    root_logger.addHandler(file_handler)
    
    # Error file handler (for errors only)
    error_handler = logging.FileHandler(os.path.join(log_dir, 'error.log'))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(PlainFormatter())
    root_logger.addHandler(error_handler)
    
    return root_logger


# Helper functions for different log types
def log_request(method, path, **kwargs):
    """Log incoming request"""
    logger = logging.getLogger('request')
    logger.info(f"REQUEST: {method} {path}")
    if kwargs:
        logger.debug(f"  Parameters: {kwargs}")


def log_response(status_code, method, path, elapsed=None):
    """Log outgoing response"""
    logger = logging.getLogger('response')
    elapsed_str = f" ({elapsed:.2f}ms)" if elapsed else ""
    logger.info(f"RESPONSE: {status_code} {method} {path}{elapsed_str}")


def log_database(operation, table, **kwargs):
    """Log database operation"""
    logger = logging.getLogger('database')
    logger.info(f"DATABASE: {operation} on {table}")
    if kwargs:
        logger.debug(f"  Details: {kwargs}")


def log_auth(action, user=None, **kwargs):
    """Log authentication event"""
    logger = logging.getLogger('auth')
    user_str = f" ({user})" if user else ""
    logger.info(f"AUTH: {action}{user_str}")
    if kwargs:
        logger.debug(f"  Details: {kwargs}")


def log_validation(field, status, message=None):
    """Log validation result"""
    logger = logging.getLogger('validation')
    if status:
        logger.debug(f"VALIDATION: ✓ {field} passed")
    else:
        logger.warning(f"VALIDATION: ✗ {field} failed - {message or 'Unknown error'}")


def log_error(title, error, **kwargs):
    """Log error with context"""
    logger = logging.getLogger('error')
    logger.error(f"ERROR: {title} - {str(error)}")
    if kwargs:
        logger.debug(f"  Context: {kwargs}")
