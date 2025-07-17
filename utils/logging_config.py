import logging
import os
import sys
from datetime import datetime


def _supports_color():
    """Check if the current environment supports ANSI color codes"""
    # Check if we're in a TTY (terminal)
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check environment variables
    term = os.environ.get('TERM', '').lower()
    colorterm = os.environ.get('COLORTERM', '').lower()
    
    # Known terminals that support color
    if 'color' in term or 'xterm' in term or 'screen' in term or colorterm:
        return True
    
    # Check for common CI environments that support color
    ci_envs = ['GITHUB_ACTIONS', 'GITLAB_CI', 'CIRCLECI', 'TRAVIS', 'JENKINS_URL']
    if any(env in os.environ for env in ci_envs):
        return True
    
    # Default to False for safety
    return False


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def __init__(self, *args, use_colors=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-detect color support if not explicitly set
        self.use_colors = use_colors if use_colors is not None else _supports_color()
    
    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)
        
        # Only apply colors if supported
        if not self.use_colors:
            return log_message
        
        # Add color to the log level
        level_name = record.levelname
        if level_name in self.COLORS:
            # Extract module name from logger name for cleaner display
            module_name = self._get_module_name(record.name)
            
            # Color the level name
            colored_level = f"{self.COLORS[level_name]}{level_name}{self.COLORS['RESET']}"
            
            # Replace the level name in the message with colored version
            log_message = log_message.replace(level_name, colored_level)
            
            # Highlight module name in bright cyan
            if module_name:
                log_message = log_message.replace(
                    record.name, 
                    f"\033[96m{module_name}\033[0m"  # Bright cyan
                )
        
        return log_message
    
    def _get_module_name(self, logger_name):
        """Extract a clean module name from the logger name"""
        if not logger_name:
            return "root"
        
        # Handle common patterns
        if logger_name.startswith('components.'):
            return logger_name.split('.')[-1]  # Just the component name
        elif logger_name.startswith('callbacks.'):
            return logger_name.split('.')[-1]  # Just the callback name
        elif logger_name.startswith('utils.'):
            return logger_name.split('.')[-1]  # Just the utility name
        elif '.' in logger_name:
            return logger_name.split('.')[-1]  # Last part of dotted name
        
        return logger_name


def setup_logging(debug=False, log_file=None, force_colors=None):
    """
    Set up logging configuration for the dashboard application
    
    Args:
        debug (bool): Enable debug level logging
        log_file (str): Optional log file path
        force_colors (bool): Force enable/disable colors (None = auto-detect)
    """
    # Set the log level
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Check environment variables for color control
    if force_colors is None:
        force_colors_env = os.environ.get('FORCE_COLORS', '').lower()
        if force_colors_env in ('true', '1', 'yes', 'on'):
            force_colors = True
        elif force_colors_env in ('false', '0', 'no', 'off'):
            force_colors = False
        # Otherwise leave as None for auto-detection
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Enhanced console formatter with module names and colors
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        use_colors=force_colors
    )
    
    # Simple colored formatter for non-debug mode
    simple_console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        use_colors=force_colors
    )
    
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter if debug else simple_console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified) - no colors in file
    if log_file:
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Set specific loggers for different modules
    logging.getLogger('dash').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    return logger


def get_logger(name):
    """
    Get a logger with the specified name
    
    Args:
        name (str): Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
def init_dashboard_logging():
    """Initialize logging for the dashboard application"""
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    log_file = os.environ.get('LOG_FILE')
    
    if not log_file:
        # Default log file location
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        log_file = os.path.join(log_dir, f'dashboard_{datetime.now().strftime("%Y%m%d")}.log')
    
    return setup_logging(debug=debug_mode, log_file=log_file)