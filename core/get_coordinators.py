from typing import Union, Optional, Dict, List
from config.modules import COORDINATORS


def get_coordinator_name(coord_id: Union[int, str]) -> str:
    """
    Получает имя координатора по ID.

    Args:
        coord_id: ID координатора (может быть числом или строкой)

    Returns:
        Имя координатора если найден, иначе строковое представление ID

    Examples:
        >>> get_coordinator_name(1)
        'Иван Иванов'
        >>> get_coordinator_name("unknown")
        'unknown'
    """
    # Приводим ID к строке для универсального сравнения
    search_id = str(coord_id)

    for coord_dict in COORDINATORS:
        # Проверяем все ключи в словаре (они могут быть разных типов)
        for key, value in coord_dict.items():
            if str(key) == search_id:
                return value

    return search_id

if __name__ == "__main__":
    coor_id = get_coordinator_name()
    print(coor_id)




