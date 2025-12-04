"""
Загрузка конфигураций из YAML и JSON файлов.
"""
import yaml
import json
from datetime import date
from typing import Dict, List, Any
import os


def load_yaml_file(file_path: str) -> Any:
    """Загружает YAML файл."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        print(f"Текущая рабочая директория: {os.getcwd()}")
        raise


def load_json_file(file_path: str) -> Any:
    """Загружает JSON файл."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        print(f"Текущая рабочая директория: {os.getcwd()}")
        raise



class ConfigLoader:
    """Класс для загрузки всех конфигурационных данных."""

    def __init__(self, config_dir: str = 'config'):
        self.config_dir = config_dir

    def load_all(self) -> Dict[str, Any]:
        """Загружает все конфигурационные файлы."""
        config = {}

        # Загружаем координаторов
        coordinators_path = os.path.join(self.config_dir, 'coordinators.yaml')
        coordinators_data = load_yaml_file(coordinators_path)
        config['COORDINATORS'] = coordinators_data.get('coordinators', {})
        config['LEAD_COORDINATORS_TO_PROFESSION'] = coordinators_data.get('lead_coordinators_to_profession', {})

        # Загружаем профессии и блоки
        professions_path = os.path.join(self.config_dir, 'professions.yaml')
        professions_data = load_yaml_file(professions_path)
        config['PROFESSION_TO_BLOCKS'] = professions_data.get('profession_to_blocks', {})

        # Загружаем модули
        module_path = os.path.join(self.config_dir, 'modules.yaml')
        module_data = load_yaml_file(module_path)
        config['DIPLOMA_MODULES'] = module_data.get('diploma_modules', [])
        config['SELF_ASSIGNMENT_MODULES'] = module_data.get('self_assignment_modules', [])

        # Загружаем даты
        dates_path = os.path.join(self.config_dir, 'dates.json')
        dates_data = load_json_file(dates_path)
        config['HOLIDAYS'] = [date.fromisoformat(d) for d in dates_data.get('holidays', [])]
        config['EXTRA_DAYS'] = [date.fromisoformat(d) for d in dates_data.get('extra_days', [])]

        # Генерируем дополнительные словари для удобства
        config['BLOCK_TO_PROFESSION'] = self._create_block_to_profession(config['PROFESSION_TO_BLOCKS'])
        config['LEAD_COORDINATOR_TO_BLOCKS'] = self._create_lead_coordinator_to_blocks(
            config['LEAD_COORDINATORS_TO_PROFESSION'],
            config['PROFESSION_TO_BLOCKS']
        )

        # Дополняем дипломные модули (для обратной совместимости)
        config['DIPLOMA_MODULES'].extend([
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
        ])

        # Дополняем модули самозакрепления (для обратной совместимости)
        config['SELF_ASSIGNMENT_MODULES'].extend([
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
        ])

        # Преобразуем COORDINATORS в старый формат для обратной совместимости
        old_format_coordinators = []
        for uid, name in config['COORDINATORS'].items():
            old_format_coordinators.append({int(uid): name})
        config['COORDINATORS_OLD_FORMAT'] = old_format_coordinators

        return config

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

