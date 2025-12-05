#!/usr/bin/env python3
import subprocess
import sys


def install_requirements():
    """Установка необходимых пакетов"""
    requirements = ['PyYAML']

    for package in requirements:
        print(f"Устанавливаю {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    print("\nУстановка завершена!")
    print("\nЗапустите приложение командой:")
    print("python config_editor_gui.py")


if __name__ == "__main__":
    try:
        install_requirements()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка установки: {e}")
        sys.exit(1)