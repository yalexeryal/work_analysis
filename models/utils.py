"""
Утилиты для работы с конфигурационными данными.
"""

from config.modules import (
    BLOCK_TO_PROFESSION,
    LEAD_COORDINATORS_TO_PROFESSION,
    LEAD_COORDINATOR_TO_BLOCKS,
    PROFESSION_TO_BLOCKS
)


def get_profession_for_block(block: str) -> str:
    """Получает профессию для блока."""
    return BLOCK_TO_PROFESSION.get(block)


def get_lead_coordinator_for_block(block: str) -> str:
    """Получает ведущего координатора для блока."""
    profession = get_profession_for_block(block)
    if not profession:
        return None

    for lead, professions in LEAD_COORDINATORS_TO_PROFESSION.items():
        if profession in professions:
            return lead
    return None


def get_blocks_for_lead_coordinator(lead_name: str) -> list:
    """Получает все блоки для ведущего координатора."""
    return LEAD_COORDINATOR_TO_BLOCKS.get(lead_name, [])


def get_blocks_for_profession(profession: str) -> list:
    """Получает все блоки для профессии."""
    return PROFESSION_TO_BLOCKS.get(profession, [])