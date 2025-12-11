"""
Загрузка модулей и конфигураций из внешних файлов.
"""
from config.config_loader import ConfigManager

# Создаем менеджер конфигураций
config_manager = ConfigManager('config')
config = config_manager.get_config()

# Экспортируем переменные для обратной совместимости
DIPLOMA_MODULES = config['DIPLOMA_MODULES']
SELF_ASSIGNMENT_MODULES = config['SELF_ASSIGNMENT_MODULES']
holidays = config['HOLIDAYS']
extra_days = config['EXTRA_DAYS']
COORDINATORS = config['COORDINATORS_OLD_FORMAT']  # Старый формат для совместимости
LEAD_COORDINATORS_TO_PROFESSION = config['LEAD_COORDINATORS_TO_PROFESSION']
PROFESSION_TO_BLOCKS = config['PROFESSION_TO_BLOCKS']

# Экспортируем новые словари для удобства
BLOCK_TO_PROFESSION = config['BLOCK_TO_PROFESSION']
LEAD_COORDINATOR_TO_BLOCKS = config['LEAD_COORDINATOR_TO_BLOCKS']
COORDINATORS_DICT = config['COORDINATORS']  # Новый формат (словарь)

# Экспортируем менеджер для редактирования
CONFIG_MANAGER = config_managerNATORS_DICT = config['COORDINATORS']  # Новый формат (словарь)