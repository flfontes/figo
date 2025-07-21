import logging
import re
from datetime import datetime

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)


formatter = logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s:\n%(message)s')


command_line_output = logging.StreamHandler()
date_label = re.sub(
    r'[:,-]', '_', datetime.now().isoformat(sep='_', timespec='minutes')
)
file_output = logging.FileHandler(f'logs/debug_logs_{date_label}.log')


command_line_output.setFormatter(formatter)
file_output.setFormatter(formatter)

logger.addHandler(command_line_output)
logger.addHandler(file_output)
