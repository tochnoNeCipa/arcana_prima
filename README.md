# Кодекс Нитей — Магическая система Аркана Примы

![Python CI](https://github.com/ВАШ_ЛОГИН/arcana_prima/actions/workflows/ci.yml/badge.svg)

Учебный проект по дисциплине **Python: ООП · Тестирование · CI/CD**.  
Реализует магическую систему «Кодекс Нитей» с демонстрацией всех четырёх принципов ООП.

## Структура проекта

```
arcana_prima/
├── src/                   # Исходный код
│   ├── threads.py         # Нити Реальности (Инкапсуляция)
│   ├── spells.py          # Заклинания (Наследование + Полиморфизм)
│   ├── artifacts.py       # Артефакты (Абстракция)
│   └── caster.py          # Нитяры и интерфейсы
├── tests/                 # Автотесты (149 тестов, покрытие 99%)
│   ├── test_threads.py
│   ├── test_spells.py
│   └── test_artifacts_caster.py
├── .github/workflows/
│   └── ci.yml             # GitHub Actions pipeline
├── main.py                # Демонстрационный сценарий
├── conftest.py            # Конфигурация pytest
├── pytest.ini
├── requirements.txt
└── ARCHITECTURE.md        # UML-диаграмма и описание архитектуры
```

## Принципы ООП

| Принцип | Реализация |
|---|---|
| **Инкапсуляция** | `Thread` — приватные `__frequency`, `__stability` с `@property` и валидацией |
| **Наследование** | `Spell → WeaveSpell → LegendaryWeaveSpell`, `CutSpell`, `BindSpell` |
| **Полиморфизм** | Единый `cast()` для всех заклинаний, `execute_all()` через duck typing |
| **Абстракция** | `Artifact(ABC)`, `ArcaneInterface(Protocol)` скрывают детали реализации |

## Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Демонстрация
python main.py

# Тесты
pytest tests/ -v

# Покрытие
coverage run -m pytest tests/
coverage report -m

# HTML-отчёт
pytest --html=report.html --self-contained-html
```

## CI/CD

При каждом `push` в `main` автоматически:
1. Устанавливаются зависимости
2. Запускаются все 149 тестов
3. Проверяется покрытие кода (≥ 99%)
4. Генерируется HTML-отчёт
5. Проверяется стиль кода (ruff)
