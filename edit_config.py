#!/usr/bin/env python3
"""
Скрипт для редактирования конфигурационных данных.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_editor import edit_config_from_cli

if __name__ == "__main__":
    edit_config_from_cli()