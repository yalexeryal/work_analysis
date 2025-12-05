import os

def print_tree(root, prefix=''):
    try:
        # Получаем список элементов и сортируем
        items = sorted(os.listdir(root))
    except PermissionError:
        # Если нет доступа к директории — пропускаем
        return

    # Фильтруем элементы: исключаем .venv и .git
    filtered_items = []
    for item in items:
        if item not in ['.venv', '.git', '__pycache__', '.idea']:
            filtered_items.append(item)

    for i, item in enumerate(filtered_items):
        path = os.path.join(root, item)
        is_last = i == len(filtered_items) - 1
        connector = '└── ' if is_last else '├── '
        print(f"{prefix}{connector}{item}")

        if os.path.isdir(path):
            extension = '    ' if is_last else '│   '
            print_tree(path, prefix + extension)

if __name__ == '__main__':
    print_tree('.')
