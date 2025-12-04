"""
Списки модулей для фильтрации.
Автоматически сгенерировано редактором конфигурации.
"""
from datetime import date

# Список модулей для фильтрации дипломных работ (включаем)
DIPLOMA_MODULES = [
    'dip-abi', 'dip-dmar', 'diplom-abu', 'diplom-aml', 'diplom-awh', 'diplom-ban', 'diplom-banpro',
    'diplom-da', 'diplom-dau', 'diplom-deg', 'diplom-degneo', 'diplom-degpro', 'diplom-ds', 'diplom-dsu',
    'diplom-mlecv', 'diplom-mlenlp', 'diplom-oca', 'diplom-ocamid', 'diplom-prmlec', 'diplom-prmlen',
    'diplom-prmleu', 'diplom-sal', 'diplom-salban', 'diplom-smle', 'diplom-sup', 'diplom-supn', 'fan',
    'fbtrx', 'fcpp', 'fcppiot', 'fcppqt', 'ffe', 'ffjs', 'ffops', 'ffopsj', 'ffpy', 'ffs', 'ffsmid',
    'ffsmidjs', 'ffsmidpd', 'fgo', 'fgolpro', 'fib', 'fibdef', 'fibweb', 'fios', 'fibtp', 'fjd', 'fntw', 'fonec',
    'fonecmid', 'fonecmid-prod', 'fpae', 'fpbi', 'fpd', 'fpdx', 'fqa', 'fqamid', 'fqapy', 'fshan',
    'fshdevops', 'fshfe', 'fshjd', 'fshqa', 'fspd', 'fsppue', 'fsql', 'fsqlp', 'fsys', 'pyda-diplom',
    'shpaefin'
]

# Модули с самозакреплением (эксперты сами берут в работу)
SELF_ASSIGNMENT_MODULES = [
    'abd', 'abt', 'acv', 'aiba', 'aic', 'als', 'apid', 'apid-oca', 'arch-sal', 'atra', 'bash', 'cicd', 'codeplc',
    'course-fops', 'dfd', 'dfd-ds', 'dmar', 'dwh-sqld', 'fps', 'fsqlp', 'git-fops', 'gobase', 'gomult', 'imba',
    'info-dmar', 'info-fops', 'info-oca', 'info-sys', 'ispm', 'maa', 'mbp', 'mbpn', 'mca', 'mdpa', 'net', 'oca-b',
    'okmid', 'phd', 'rnfda', 'rnfdap', 'roman', 'scada', 'sdbsql', 'sdm', 'sflt', 'shcicd', 'shclopro', 'shkonf',
    'shkuber', 'shmicros', 'shmon-dev', 'shter', 'shvirtd', 'skds', 'slina', 'slinb', 'slinc', 'smon', 'sql',
    'sql-asinhr', 'ssoca', 'stpy', 'svirt', 'sysdb', 'syssec', 'tab', 'tl', 'tra_arh', 'upk', 'xls', 'yzda'
]

# Добавляем праздники
holidays = [
    date(2025, 12, 31), date(2026, 1, 1), date(2026, 1, 2),
    date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7),
    date(2026, 1, 8), date(2026, 1, 9), date(2026, 2, 23),
    date(2026, 5, 1), date(2026, 5, 11), date(2026, 6, 12),
    date(2026, 11, 4)
]

# Добавляем рабочие выходные (по необходимости)
extra_days = [date(2025, 4, 27), date(2025, 11, 2)]

# Словарь координаторов
COORDINATORS = [
    {7930978: 'Ирина Рыбакова'},
    {7998125: 'Настя Рябова'},
    {7834874: 'Ольга Самойлова'},
    {8772068: 'Елена Левина'},
    {6151878: 'Виктория Пятыгина'},
    {7906436: 'Варвара Бутковская'},
    {8366269: 'Наталья Збеглова'},
    {7148627: 'Максим Зайкин'},
    {8232264: 'Полина Савченко'},
    {8557079: 'Елена Безрученкова'},
    {8187353: 'Александр Нестеров'},
    {8881338: 'Евгений Синякин'},
    {8281784: 'Елена Максимова'},
    {8242201: 'Евгения Аникина'},
    {7183929: 'Асия Яблочкова'},
    {8453121: 'Ксения Райская'},
    {7985503: 'Анна Суханова'},
    {8620712: 'Дияз Сейфетдинов'},
    {8078713: 'Олег Гежин'},
    {5810125: 'Ольга Соболева'},
    {7150186: 'Росина Савицкая'},
    {7183936: 'Елена Зайцева'},
    {7864914: 'Нурлан Асанбеков'},
]

LEAD_COORDINATORS_TO_PROFESSION = {
    "Ирина Панина": ['da', 'dau', 'deg'],
    "Виктория Пятыгина": ['pydp', 'ds', 'dsu', 'aml', 'dll'],
    "Евгения Сергеева": ['an', 'shan', 'jd', 'shjd', 'cpp', 'cppqt', 'cppiot', 'cpppue'],
    "Элионора Петрова": ['qa', 'qamid', 'qapy', 'qamidpy', 'shqa', 'ios', 'go', 'golpro'],
    "Анастасия Трещина": ['shdevops', 'sys', 'fops', 'abi', 'abu', 'dmar', 'pbi', 'pdx', 'ban', 'banpro'],
    "Мария Пескова": ['sal', 'pal', 'awh', 'sup', 'sql', 'sqlp'],
    "Оксана Махонина": ['spd', 'pd', 'fpy'],
    "Наталья Нагаева": ['onec', 'onecmid', 'git', 'sib'],
    "Юлия Похвищева": ['ntw', 'pae'],
    "Алёна Хохлова": ['shfe', 'fe', 'fsmid', 'fsmidjs', 'fsmidpd', 'btrx', 'btrxpro'],
    "Денис Кобин": ['oca', 'ocamid'],
}

PROFESSION_TO_BLOCKS = {
    "an": ['info-an', 'КТ', 'AND', 'ANDIN', 'ANDAD', 'BONUS-AN', 'FAN', ],
    "shan": ['BONUS-SHAN', 'FSHAN'],
    "jd": ['info-jd', 'JDPTL', 'JAVA', 'JM', 'ALGO', 'JAVACORE', 'JPAT', 'JADV', 'JSPR', 'JCLO', 'JDATA', 'SHMICROS',
           'FJD'],
    "shjd": ['BONUS-SHJD', 'FSHJD'],
    "cpp": ['INFO-CPP', 'CPPS', 'CPPM', 'ALGOCPP', 'CPPL', 'SQLCPP', 'MAP', 'DPCPP', 'FCPP'],
    "cppqt": ['qt', 'FCPPQT'],
    "cppiot": ['iot', 'fcppiot'],
    "cpppue": ['pue', 'fcppue'],
    "fe": ['BAFE', 'HTML', 'MQ', 'PB', 'BJS', 'BHJ', 'AJS', 'AHJ', 'RA', 'FFE'],
    "btrx": [',INFO-BTRX', ',BWEB', 'BPATTI', 'BPATTC', 'BCONT', 'BBAY', 'FBTRX'],
    "btrxpro": ['INFO-BTRXPRO', 'BWEBPRO'],
    "shfe": ['INFO-SHFE', 'SHFEJS', 'FSHFE'],
    "fsmid": ['INFO-FSMID', 'BHJ', 'BPHP', 'APHP', 'LRV', 'FFSMID'],
    "fsmidjs": ['NDSE', 'NDTNF', 'FFSMIDJS'],
    "fsmidpd": ['PY', 'PYAPI', 'FSWEBPY', 'FFSMIDPD'],
    "sys": ['INFO-SYS', 'SLINA', 'SLINB', 'SLINC', 'BASH', 'NET', 'SVIRT', 'CICD', 'ISPM', 'SMON', 'SFLT', 'SYSDB',
            'SDBSQL', 'SYSSEC', 'FSYS'],
    "fops": ['INFO-FOPS', 'COURSE-FOPS', 'GIT-FOPS', 'SHVIRTD', 'SHTER', 'SHKONF', 'SHCICD-DEV', 'SHMON-DEV',
             'SHMICROS', 'SHKUBER', 'SHCLOPRO', 'FFOPS'],
    "shdevops": ['info-shdevops', 'FSHDEVOPS'],
    "1": [],
    "2": [],
    "3": [],

}

# Создание словаря из двух словарей
# BLOCK_TO_LEAD_COORDINATORS = {}
#
# for name, profession in LEAD_COORDINATORS_TO_PROFESSION.items():
#     blocks = PROFESSION_TO_BLOCKS.get(profession, [])
#     for block in blocks:
#         BLOCK_TO_LEAD_COORDINATORS[block] = name
#
# print(BLOCK_TO_LEAD_COORDINATORS)
