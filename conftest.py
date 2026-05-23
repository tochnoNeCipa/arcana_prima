"""
conftest.py — Глобальная конфигурация pytest.
Добавляет корень проекта и src/ в sys.path,
чтобы импорты работали и с src. и без него.
"""

import sys
import os

# Корень проекта (папка с pytest.ini)
ROOT = os.path.dirname(__file__)
SRC = os.path.join(ROOT, "src")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
