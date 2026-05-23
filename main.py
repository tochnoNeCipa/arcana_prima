"""
main.py — Демонстрационный сценарий «Кодекс Нитей»
Связывает все модули и демонстрирует все четыре принципа ООП.
"""

import warnings

from src.threads import EnergyThread, FormThread, TimeThread
from src.spells import (
    BindSpell, CombinedSpell, CutSpell,
    LegendaryWeaveSpell, Rarity, WeaveSpell,
)
from src.artifacts import CrystalCore, RuneMatrix
from src.caster import Caster, execute_all


def separator(title: str = "") -> None:
    line = "═" * 60
    if title:
        print(f"\n{line}")
        print(f"  {title}")
        print(f"{line}")
    else:
        print(f"\n{line}\n")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Создание Нитяров
# ─────────────────────────────────────────────────────────────────────────────
separator("Часть 1 — Создание Нитяров")

varn = Caster(name="Архимаг Варн", energy=200.0)
sel = Caster(name="Ученица Сел", energy=40.0)

# Заклинания Варна (легендарные)
varn.learn(LegendaryWeaveSpell("Великое Плетение", cost=30.0, amplifier=3.0))
varn.learn(CutSpell("Разрыв Реальности", cost=20.0, rarity=Rarity.RARE, severity=0.4))
varn.learn(BindSpell("Вечные Оковы", cost=25.0, rarity=Rarity.LEGENDARY,
                     effect_name="Проклятие Нитей", duration=10))

# Составное заклинание Варна
grand_combo = CombinedSpell(
    "Апокалипсис Нитей",
    [
        CutSpell("Разрыв α", cost=15.0, severity=0.2),
        BindSpell("Привязь ω", cost=10.0, effect_name="Паралич"),
    ]
)
varn.learn(grand_combo)

# Заклинания Сел (базовые)
sel.learn(WeaveSpell("Нить Защиты", cost=8.0, bond_strength=2.0))
sel.learn(BindSpell("Малые Оковы", cost=5.0, effect_name="Замедление", duration=2))

print(f"\n{varn}")
print(f"\n{sel}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Нити и перегрузка оператора +
# ─────────────────────────────────────────────────────────────────────────────
separator("Часть 2 — Нити Реальности (Инкапсуляция)")

energy_thread = EnergyThread("Нить Молнии", frequency=500.0, stability=0.9, charge=2.5)
form_thread = FormThread("Нить Камня", frequency=200.0, stability=0.95, density=3.0)
time_thread = TimeThread("Нить Вечности", frequency=100.0, stability=0.7, age=12.0)

print(energy_thread)
print(form_thread)
print(time_thread)

# Перегрузка оператора +
merged = energy_thread + form_thread
print(f"\n➕ Слияние нитей: {energy_thread.name} + {form_thread.name}")
print(f"   Результат: {merged}")

# Резонанс нитей
print(f"\n🎵 Резонанс «{energy_thread.name}» и «{form_thread.name}»: "
      f"{energy_thread.resonate(form_thread):.2f}")
print(f"🎵 Резонанс «{time_thread.name}» и «{form_thread.name}»: "
      f"{time_thread.resonate(form_thread):.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Артефакты и предупреждение при замене
# ─────────────────────────────────────────────────────────────────────────────
separator("Часть 3 — Артефакты (Абстракция)")

rune_matrix = RuneMatrix("Матрица Хаоса", capacity=3)
crystal_core = CrystalCore("Кристалл Зари")

varn.equip(rune_matrix)
sel.equip(crystal_core)

# Демонстрация RuneMatrix
rune_matrix.store(energy_thread)
rune_matrix.store(time_thread)
print(f"\n{rune_matrix}")
energy_sum = rune_matrix.activate(form_thread)
print(f"⚡ RuneMatrix активирована → суммарная энергия: {energy_sum:.2f}")

# Демонстрация CrystalCore
amplified = crystal_core.activate(energy_thread)
print(f"💎 CrystalCore активирован → усиленная энергия: {amplified:.2f}")

# Попытка заменить артефакт — должно сработать предупреждение
separator("Замена артефакта (предупреждение)")
spare_crystal = CrystalCore("Запасной Кристалл")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    varn.equip(spare_crystal)
    if caught:
        print(f"⚠️ Предупреждение: {caught[0].message}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Дуэль (Полиморфизм)
# ─────────────────────────────────────────────────────────────────────────────
separator("Часть 4 — Дуэль Нитяров (Полиморфизм)")

print(f"\n⚔️  {varn.name} против {sel.name}!\n")

# Варн атакует
print(f"--- Ход {varn.name} ---")
print(varn.cast("Великое Плетение", sel))
print(varn.cast("Разрыв Реальности", sel))
print(varn.cast("Вечные Оковы", sel))

# Сел отвечает
print(f"\n--- Ход {sel.name} ---")
print(sel.cast("Нить Защиты", varn))
print(sel.cast("Малые Оковы", varn))

# ─────────────────────────────────────────────────────────────────────────────
# 5. Полиморфизм через execute_all (duck typing)
# ─────────────────────────────────────────────────────────────────────────────
separator("Часть 5 — execute_all (Duck Typing)")

mixed_spells = [
    WeaveSpell("Нить Хаоса", cost=5.0, bond_strength=1.5),
    CutSpell("Лезвие Теней", cost=8.0, severity=0.15),
    LegendaryWeaveSpell("Зеркало Нитей", cost=20.0, amplifier=2.5),
    grand_combo,                   # CombinedSpell — полиморфно с одиночными
]

execute_all(mixed_spells, varn, sel)

# ─────────────────────────────────────────────────────────────────────────────
# 6. Сравнение заклинаний (перегрузка >)
# ─────────────────────────────────────────────────────────────────────────────
separator("Часть 6 — Сравнение заклинаний")

legendary_spell = LegendaryWeaveSpell("Ультимейт", cost=50.0)
common_spell = WeaveSpell("Простое Плетение", cost=5.0)

print(f"Легендарное > Обычное? {legendary_spell > common_spell}")   # True
print(f"Обычное < Легендарное? {common_spell < legendary_spell}")   # True
print(f"Обычное == Обычное?   {common_spell == WeaveSpell('Ещё одно', cost=3.0)}")  # True

# ─────────────────────────────────────────────────────────────────────────────
# 7. MRO LegendaryWeaveSpell
# ─────────────────────────────────────────────────────────────────────────────
separator("Часть 7 — MRO LegendaryWeaveSpell")

print("Порядок разрешения методов (C3-линеаризация):")
for i, cls in enumerate(LegendaryWeaveSpell.__mro__):
    print(f"  {i + 1}. {cls}")

# ─────────────────────────────────────────────────────────────────────────────
# 8. Итоговый отчёт
# ─────────────────────────────────────────────────────────────────────────────
separator("Итоговый отчёт")

for caster in (varn, sel):
    print(caster)
    print(f"  Известные заклинания: {', '.join(caster.list_spells()) or 'нет'}")
    print()

print("Нити Реальности:")
for thread in (energy_thread, form_thread, time_thread, merged):
    print(f"  {thread}")

print("\n✅ Демонстрация завершена. Реальность Аркана Примы сохранена.")
