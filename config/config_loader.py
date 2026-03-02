"""
Загрузка и сохранение конфигураций из YAML и JSON файлов.
"""
import yaml
import json
from datetime import date, datetime
from typing import Dict, List, Any, Union
import os
from pathlib import Path


def load_yaml_file(file_path: str) -> Any:
    """Загружает YAML файл."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        raise
    except yaml.YAMLError as e:
        print(f"Ошибка чтения YAML файла {file_path}: {e}")
        raise


def save_yaml_file(file_path: str, data: Any) -> None:
    """Сохраняет данные в YAML файл."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"Данные успешно сохранены в {file_path}")
    except Exception as e:
        print(f"Ошибка сохранения YAML файла {file_path}: {e}")
        raise


def load_json_file(file_path: str) -> Any:
    """Загружает JSON файл."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON файла {file_path}: {e}")
        raise


def save_json_file(file_path: str, data: Any) -> None:
    """Сохраняет данные в JSON файл."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"Данные успешно сохранены в {file_path}")
    except Exception as e:
        print(f"Ошибка сохранения JSON файла {file_path}: {e}")
        raise


class ConfigManager:
    """Класс для управления конфигурационными данными."""

    def __init__(self, config_dir: str = 'config'):
        self.config_dir = config_dir
        self.config = {}
        self.load_all()

    def load_all(self) -> Dict[str, Any]:
        """Загружает все конфигурационные файлы."""
        config = {}

        # Пути к файлам
        self.coordinators_path = os.path.join(self.config_dir, 'coordinators.yaml')
        self.professions_path = os.path.join(self.config_dir, 'professions.yaml')
        self.module_path = os.path.join(self.config_dir, 'module.yaml')
        self.dates_path = os.path.join(self.config_dir, 'dates.json')

        # Загружаем координаторов
        coordinators_data = load_yaml_file(self.coordinators_path)
        config['COORDINATORS'] = coordinators_data.get('coordinators', {})
        config['LEAD_COORDINATORS_TO_PROFESSION'] = coordinators_data.get('lead_coordinators_to_profession', {})

        # Загружаем профессии и блоки
        professions_data = load_yaml_file(self.professions_path)
        config['PROFESSION_TO_BLOCKS'] = professions_data.get('profession_to_blocks', {})

        # Загружаем модули
        module_data = load_yaml_file(self.module_path)
        config['DIPLOMA_MODULES'] = module_data.get('diploma_modules', [])
        config['SELF_ASSIGNMENT_MODULES'] = module_data.get('self_assignment_modules', [])

        # Загружаем даты
        dates_data = load_json_file(self.dates_path)
        config['HOLIDAYS'] = [date.fromisoformat(d) for d in dates_data.get('holidays', [])]
        config['EXTRA_DAYS'] = [date.fromisoformat(d) for d in dates_data.get('extra_days', [])]

        # Генерируем дополнительные словари для удобства
        config['BLOCK_TO_PROFESSION'] = self._create_block_to_profession(config['PROFESSION_TO_BLOCKS'])
        config['LEAD_COORDINATOR_TO_BLOCKS'] = self._create_lead_coordinator_to_blocks(
            config['LEAD_COORDINATORS_TO_PROFESSION'],
            config['PROFESSION_TO_BLOCKS']
        )

        # Дополняем дипломные модули (для обратной совместимости)
        self._extend_diploma_modules(config)

        # Дополняем модули самозакрепления (для обратной совместимости)
        self._extend_self_assignment_modules(config)

        # Преобразуем COORDINATORS в старый формат для обратной совместимости
        config['COORDINATORS_OLD_FORMAT'] = self._convert_to_old_format(config['COORDINATORS'])

        self.config = config
        return config

    def _extend_diploma_modules(self, config: Dict):
        """Дополняет дипломные модули."""
        extended = [
            'diplom-aml', 'diplom-awh', 'diplom-ban', 'diplom-banpro',
            'diplom-da', 'diplom-dau', 'diplom-deg', 'diplom-degneo', 'diplom-degpro',
            'diplom-ds', 'diplom-dsu', 'diplom-mlecv', 'diplom-mlenlp', 'diplom-oca',
            'diplom-ocamid', 'diplom-prmlec', 'diplom-prmlen', 'diplom-prmleu',
            'diplom-sal', 'diplom-salban', 'diplom-smle', 'diplom-sup', 'diplom-supn',
            'fan', 'fbtrx', 'fcpp', 'fcppiot', 'fcppqt', 'ffe', 'ffjs', 'ffops', 'ffopsj',
            'ffpy', 'ffs', 'ffsmid', 'ffsmidjs', 'ffsmidpd', 'fgo', 'fgolpro', 'fib',
            'fibdef', 'fibweb', 'fios', 'fibtp', 'fjd', 'fntw', 'fonec', 'fonecmid',
            'fonecmid-prod', 'fpae', 'fpbi', 'fpd', 'fpdx', 'fqa', 'fqamid', 'fqapy',
            'fshan', 'fshdevops', 'fshfe', 'fshjd', 'fshqa', 'fspd', 'fsppue', 'fsql',
            'fsqlp', 'fsys', 'pyda-diplom', 'shpaefin'
        ]
        config['DIPLOMA_MODULES'].extend([m for m in extended if m not in config['DIPLOMA_MODULES']])

    def _extend_self_assignment_modules(self, config: Dict):
        """Дополняет модули самозакрепления."""
        extended = [
            'aiba', 'aic', 'als', 'apid', 'apid-oca', 'arch-sal', 'atra', 'bash',
            'cicd', 'codeplc', 'course-fops', 'dfd', 'dfd-ds', 'dmar', 'dwh-sqld',
            'fps', 'fsqlp', 'git-fops', 'gobase', 'gomult', 'imba', 'info-dmar',
            'info-fops', 'info-oca', 'info-sys', 'ispm', 'maa', 'mbp', 'mbpn',
            'mca', 'mdpa', 'net', 'oca-b', 'okmid', 'phd', 'rnfda', 'rnfdap',
            'roman', 'scada', 'sdbsql', 'sdm', 'sflt', 'shcicd', 'shclopro',
            'shkonf', 'shkuber', 'shmicros', 'shmon-dev', 'shter', 'shvirtd',
            'skds', 'slina', 'slinb', 'slinc', 'smon', 'sql', 'sql-asinhr',
            'ssoca', 'stpy', 'svirt', 'sysdb', 'syssec', 'tab', 'tl', 'tra_arh',
            'upk', 'xls', 'yzda'
        ]
        config['SELF_ASSIGNMENT_MODULES'].extend([m for m in extended if m not in config['SELF_ASSIGNMENT_MODULES']])

    def _convert_to_old_format(self, coordinators_dict: Dict) -> List[Dict]:
        """Конвертирует координаторов в старый формат."""
        old_format = []
        for uid, name in coordinators_dict.items():
            old_format.append({int(uid): name})
        return old_format

    def _create_block_to_profession(self, profession_to_blocks: Dict) -> Dict:
        """Создает обратный словарь блок -> профессия."""
        block_to_profession = {}
        for profession, blocks in profession_to_blocks.items():
            for block in blocks:
                block_to_profession[block] = profession
        return block_to_profession

    def _create_lead_coordinator_to_blocks(self, lead_to_profession: Dict, profession_to_blocks: Dict) -> Dict:
        """Создает словарь ведущий координатор -> блоки."""
        lead_to_blocks = {}
        for lead, professions in lead_to_profession.items():
            blocks = []
            for profession in professions:
                blocks.extend(profession_to_blocks.get(profession, []))
            lead_to_blocks[lead] = blocks
        return lead_to_blocks

    # Методы для сохранения данных

    def save_coordinators(self):
        """Сохраняет координаторов в YAML файл."""
        data = {
            'coordinators': self.config['COORDINATORS'],
            'lead_coordinators_to_profession': self.config['LEAD_COORDINATORS_TO_PROFESSION']
        }
        save_yaml_file(self.coordinators_path, data)

    def save_professions(self):
        """Сохраняет профессии и блоки в YAML файл."""
        data = {
            'profession_to_blocks': self.config['PROFESSION_TO_BLOCKS']
        }
        save_yaml_file(self.professions_path, data)

    def save_modules(self):
        """Сохраняет модули в YAML файл."""
        # Сохраняем только базовые модули (без расширенных)
        data = {
            'diploma_modules': [m for m in self.config['DIPLOMA_MODULES'] if m.startswith(('dip-', 'diplom-'))],
            'self_assignment_modules': self.config['SELF_ASSIGNMENT_MODULES']
        }
        save_yaml_file(self.module_path, data)

    def save_dates(self):
        """Сохраняет даты в JSON файл."""
        data = {
            'holidays': [d.isoformat() for d in self.config['HOLIDAYS']],
            'extra_days': [d.isoformat() for d in self.config['EXTRA_DAYS']]
        }
        save_json_file(self.dates_path, data)

    def save_all(self):
        """Сохраняет все конфигурационные файлы."""
        self.save_coordinators()
        self.save_professions()
        self.save_modules()
        self.save_dates()
        print("Все конфигурационные файлы успешно сохранены")

    # Методы для редактирования данных

    def add_coordinator(self, uid: int, name: str):
        """Добавляет нового координатора."""
        self.config['COORDINATORS'][str(uid)] = name
        self.save_coordinators()

    def remove_coordinator(self, uid: int):
        """Удаляет координатора."""
        uid_str = str(uid)
        if uid_str in self.config['COORDINATORS']:
            del self.config['COORDINATORS'][uid_str]
            self.save_coordinators()
        else:
            print(f"Координатор с UID {uid} не найден")

    def update_coordinator(self, uid: int, new_name: str):
        """Обновляет имя координатора."""
        uid_str = str(uid)
        if uid_str in self.config['COORDINATORS']:
            self.config['COORDINATORS'][uid_str] = new_name
            self.save_coordinators()
        else:
            print(f"Координатор с UID {uid} не найден")

    def add_holiday(self, holiday_date: date):
        """Добавляет праздничный день."""
        if holiday_date not in self.config['HOLIDAYS']:
            self.config['HOLIDAYS'].append(holiday_date)
            self.save_dates()
        else:
            print(f"Дата {holiday_date} уже в списке праздников")

    def remove_holiday(self, holiday_date: date):
        """Удаляет праздничный день."""
        if holiday_date in self.config['HOLIDAYS']:
            self.config['HOLIDAYS'].remove(holiday_date)
            self.save_dates()
        else:
            print(f"Дата {holiday_date} не найдена в списке праздников")

    def add_diploma_module(self, module: str):
        """Добавляет дипломный модуль."""
        if module not in self.config['DIPLOMA_MODULES']:
            self.config['DIPLOMA_MODULES'].append(module)
            self.save_modules()
        else:
            print(f"Модуль {module} уже в списке дипломных")

    def remove_diploma_module(self, module: str):
        """Удаляет дипломный модуль."""
        if module in self.config['DIPLOMA_MODULES']:
            self.config['DIPLOMA_MODULES'].remove(module)
            self.save_modules()
        else:
            print(f"Модуль {module} не найден в списке дипломных")

    def get_config(self) -> Dict[str, Any]:
        """Возвращает текущую конфигурацию."""
        return self.config.copy()

    def reload(self):
        """Перезагружает конфигурацию из файлов."""
        self.load_all()
