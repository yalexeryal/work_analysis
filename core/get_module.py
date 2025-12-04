from typing import Optional


def get_base_module(module_name: Optional[str]) -> Optional[str]:
    """
    Версия с более строгой проверкой - удаляет только числовые суффиксы
    после последнего дефиса.

    Args:
        module_name: Строка с названием модуля или None

    Returns:
        Строка с базовым названием модуля или исходное значение
    """
    if not module_name:
        return module_name

    parts = module_name.split('-')

    # Проверяем, что последняя часть состоит только из цифр
    # и не является пустой строкой
    if len(parts) > 1 and parts[-1].isdigit() and len(parts[-1]) > 0:
        return '-'.join(parts[:-1])

    return module_name

# import re
# from typing import Optional
#
# # любое содержимое до последнего дефиса + числовой суффикс
# CODE_RE = re.compile(r'^(?P<base>.+)-(?P<num>\d+)$')
#
# def strip_last_numeric_suffix(value: Optional[str]) -> Optional[str]:
#
#     if not value:
#         return value
#
#     m = CODE_RE.match(value.strip())
#     if not m:
#         return value  # нет числового суфикса после последнего дефиса
#
#     return m.group('base')
