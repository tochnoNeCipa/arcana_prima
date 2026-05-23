# ARCHITECTURE.md — Магическая система «Кодекс Нитей»

## Мир Аркана Прима

Магия здесь — точная наука о **Нитях Реальности**. Маги-Нитяры программируют
Артефакты-Исполнители, подчиняясь единому Кодексу (принципам ООП).

---

## Структура проекта

```
arcana_prima/
├── threads.py      # Нити Реальности      — Инкапсуляция
├── spells.py       # Иерархия заклинаний  — Наследование + Полиморфизм
├── artifacts.py    # Артефакты            — Абстракция
├── caster.py       # Нитяры и интерфейсы  — Абстракция + Полиморфизм
└── main.py         # Демонстрационный сценарий
```

---

## UML-диаграмма классов

```
┌─────────────────────────────────────────────────────────────────┐
│                        НИТИ РЕАЛЬНОСТИ                          │
│                                                                  │
│  Thread                                                          │
│  ├── __name: str          (приватное)                           │
│  ├── __frequency: float   (0.1–999.9, приватное)               │
│  ├── __stability: float   (0.0–1.0, приватное)                 │
│  ├── energy → float       (@property, вычисляемое)             │
│  ├── resonate(other) → float                                    │
│  └── __add__(other) → Thread                                    │
│       │                                                          │
│       ├── EnergyThread  [+charge: float]                        │
│       ├── FormThread    [+density: float]                       │
│       └── TimeThread    [+age: float]                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ЗАКЛИНАНИЯ                                 │
│                                                                  │
│  <<abstract>> Spell (ABC)                                        │
│  ├── name: str                                                   │
│  ├── cost: float                                                 │
│  ├── rarity: Rarity (Enum)                                      │
│  ├── <<abstract>> cast(caster, target) → str                    │
│  └── <<abstract>> describe() → str                              │
│       │                                                          │
│       ├── WeaveSpell      [+bond_strength: float]               │
│       │    └── LegendaryWeaveSpell [+amplifier: float]          │
│       ├── CutSpell        [+severity: float]                     │
│       ├── BindSpell       [+effect_name, +duration]             │
│       └── CombinedSpell   [+_spells: List[Spell]]  (Composite) │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      АРТЕФАКТЫ                                  │
│                                                                  │
│  <<abstract>> Artifact (ABC)                                     │
│  ├── name: str                                                   │
│  ├── __durability: int    (приватное)                           │
│  └── <<abstract>> activate(thread) → float                      │
│       │                                                          │
│       ├── CrystalCore    [AMPLIFY_FACTOR = 1.5]                 │
│       └── RuneMatrix     [+_stored_threads, +capacity]          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       НИТЯРЫ                                    │
│                                                                  │
│  Caster                                                          │
│  ├── name: str                                                   │
│  ├── energy: float                                               │
│  ├── artifact: Artifact (опционально)                           │
│  ├── effects: List[str]                                          │
│  ├── __spell_book: Dict[str, Spell]  (приватное)               │
│  ├── learn(spell)                                               │
│  ├── forget(spell_name)                                         │
│  ├── cast(spell_name, target) → str                             │
│  ├── equip(artifact)                                            │
│  └── __len__() → int                                            │
│                                                                  │
│  <<Protocol>> ArcaneInterface                                    │
│  ├── cast(caster, target) → str                                 │
│  └── describe() → str                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Принципы ООП → Классы

| Принцип | Файл | Ключевые классы |
|---|---|---|
| **Инкапсуляция** | `threads.py` | `Thread`, `EnergyThread`, `FormThread`, `TimeThread` |
| **Наследование** | `spells.py` | `Spell → WeaveSpell → LegendaryWeaveSpell`, `CutSpell`, `BindSpell`, `CombinedSpell` |
| **Полиморфизм** | `spells.py`, `caster.py` | `cast()` — единый интерфейс, `execute_all()` — duck typing |
| **Абстракция** | `artifacts.py`, `caster.py` | `Artifact`, `CrystalCore`, `RuneMatrix`, `ArcaneInterface` |

---

## Иерархия наследования

```
object
 └── Thread
      ├── EnergyThread
      ├── FormThread
      └── TimeThread

ABC
 └── Spell
      ├── WeaveSpell
      │    └── LegendaryWeaveSpell
      ├── CutSpell
      ├── BindSpell
      └── CombinedSpell

ABC
 └── Artifact
      ├── CrystalCore
      └── RuneMatrix
```

**MRO LegendaryWeaveSpell** (C3-линеаризация):
```
LegendaryWeaveSpell → WeaveSpell → Spell → ABC → object
```

---

## Ключевые решения

- **Приватные поля** через `__field` (name mangling) в `Thread` и `Artifact` — защита от некорректного изменения.
- **`@property` + сеттер с валидацией** — единственный безопасный способ изменить состояние извне.
- **`ABC` + `abstractmethod`** — гарантирует, что конкретные классы реализуют контракт.
- **`typing.Protocol`** (`ArcaneInterface`) — структурная типизация: duck typing с аннотациями.
- **`CombinedSpell`** (Composite) — полиморфизм: работает как одиночное заклинание.
- **`execute_all()`** — демонстрирует duck typing без `isinstance()`.
