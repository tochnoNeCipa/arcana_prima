"""
spells.py — Иерархия Заклинаний (Наследование + Полиморфизм)
Все заклинания наследуют абстрактный Spell и реализуют единый интерфейс cast().
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List


# ─────────────────────────────────────────────────────────────────────────────
# Вспомогательные типы
# ─────────────────────────────────────────────────────────────────────────────

class Rarity(Enum):
    COMMON = auto()
    RARE = auto()
    LEGENDARY = auto()

    def __str__(self) -> str:
        labels = {
            Rarity.COMMON: "Обычное",
            Rarity.RARE: "Редкое",
            Rarity.LEGENDARY: "Легендарное",
        }
        return labels[self]


# ─────────────────────────────────────────────────────────────────────────────
# Абстрактный базовый класс
# ─────────────────────────────────────────────────────────────────────────────

class Spell(ABC):
    """
    Абстрактный класс всех заклинаний.
    Наследование: конкретные заклинания обязаны реализовать cast() и describe().
    """

    def __init__(self, name: str, cost: float, rarity: Rarity = Rarity.COMMON) -> None:
        self.name = name
        if cost < 0:
            raise ValueError(f"cost не может быть отрицательным, получено: {cost}")
        self.cost = cost
        self.rarity = rarity

    @abstractmethod
    def cast(self, caster: object, target: object) -> str:
        """Применить заклинание: caster — кастующий, target — цель."""
        ...

    @abstractmethod
    def describe(self) -> str:
        """Описание заклинания."""
        ...

    # ── сравнение по редкости ─────────────────────────────────────────────
    def __gt__(self, other: "Spell") -> bool:
        return self.rarity.value > other.rarity.value

    def __lt__(self, other: "Spell") -> bool:
        return self.rarity.value < other.rarity.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Spell):
            return NotImplemented
        return self.rarity.value == other.rarity.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, cost={self.cost}, rarity={self.rarity})"

    def __str__(self) -> str:
        return f"[{self.rarity}] {self.name} (стоимость: {self.cost})"


# ─────────────────────────────────────────────────────────────────────────────
# Конкретные заклинания
# ─────────────────────────────────────────────────────────────────────────────

class WeaveSpell(Spell):
    """
    Заклинание Плетения — создаёт новую связь между объектами.
    Уменьшает энергию кастера на cost.
    """

    def __init__(self, name: str, cost: float, rarity: Rarity = Rarity.COMMON,
                 bond_strength: float = 1.0) -> None:
        super().__init__(name, cost, rarity)
        self.bond_strength = bond_strength

    def cast(self, caster: object, target: object) -> str:
        caster_name = getattr(caster, "name", str(caster))
        target_name = getattr(target, "name", str(target))

        # уменьшаем энергию кастера, если это возможно
        if hasattr(caster, "energy"):
            caster.energy = max(0.0, caster.energy - self.cost)

        return (
            f"✨ {caster_name} сплетает нити вокруг {target_name}! "
            f"Сила связи: {self.bond_strength:.1f}. "
            f"Стоимость: {self.cost} ед. энергии."
        )

    def describe(self) -> str:
        return (
            f"Заклинание Плетения «{self.name}» — создаёт нерушимую связь "
            f"между двумя объектами мироздания. "
            f"Сила связи: {self.bond_strength:.1f}."
        )


class CutSpell(Spell):
    """
    Заклинание Разрыва — снижает стабильность цели на severity.
    """

    def __init__(self, name: str, cost: float, rarity: Rarity = Rarity.COMMON,
                 severity: float = 0.1) -> None:
        super().__init__(name, cost, rarity)
        self.severity = severity

    def cast(self, caster: object, target: object) -> str:
        caster_name = getattr(caster, "name", str(caster))
        target_name = getattr(target, "name", str(target))

        if hasattr(caster, "energy"):
            caster.energy = max(0.0, caster.energy - self.cost)

        # если цель — это Thread, применяем эффект
        if hasattr(target, "stability"):
            new_stab = max(0.0, target.stability - self.severity)
            target.stability = new_stab
            stab_info = f"Стабильность {target_name}: {new_stab:.2f}"
        else:
            stab_info = f"Нити {target_name} дестабилизированы на {self.severity:.2f}"

        return (
            f"⚔️ {caster_name} разрывает нити {target_name}! "
            f"{stab_info}. "
            f"Стоимость: {self.cost} ед. энергии."
        )

    def describe(self) -> str:
        return (
            f"Заклинание Разрыва «{self.name}» — рассекает нити цели, "
            f"снижая её стабильность на {self.severity:.2f}."
        )


class BindSpell(Spell):
    """
    Заклинание Привязи — накладывает постоянный эффект на цель.
    """

    def __init__(self, name: str, cost: float, rarity: Rarity = Rarity.COMMON,
                 effect_name: str = "Оковы", duration: int = 3) -> None:
        super().__init__(name, cost, rarity)
        self.effect_name = effect_name
        self.duration = duration

    def cast(self, caster: object, target: object) -> str:
        caster_name = getattr(caster, "name", str(caster))
        target_name = getattr(target, "name", str(target))

        if hasattr(caster, "energy"):
            caster.energy = max(0.0, caster.energy - self.cost)

        # сохраняем эффект на цели, если она поддерживает это
        if hasattr(target, "effects"):
            target.effects.append(self.effect_name)

        return (
            f"🔒 {caster_name} накладывает «{self.effect_name}» на {target_name}! "
            f"Длительность: {self.duration} ходов. "
            f"Стоимость: {self.cost} ед. энергии."
        )

    def describe(self) -> str:
        return (
            f"Заклинание Привязи «{self.name}» — создаёт постоянный эффект «{self.effect_name}» "
            f"на {self.duration} ходов."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Расширенные заклинания
# ─────────────────────────────────────────────────────────────────────────────

class LegendaryWeaveSpell(WeaveSpell):
    """
    Легендарное Заклинание Плетения — усиливает базовый эффект через super().cast().
    MRO: LegendaryWeaveSpell → WeaveSpell → Spell → ABC → object
    """

    def __init__(self, name: str, cost: float, amplifier: float = 2.0) -> None:
        super().__init__(name, cost, rarity=Rarity.LEGENDARY,
                         bond_strength=10.0 * amplifier)
        self.amplifier = amplifier

    def cast(self, caster: object, target: object) -> str:
        # вызываем родительский cast()
        base_result = super().cast(caster, target)
        caster_name = getattr(caster, "name", str(caster))
        return (
            f"🌟 [ЛЕГЕНДАРНОЕ] {base_result}\n"
            f"   ⚡ {caster_name} высвобождает первородные Нити! "
            f"Усилитель: ×{self.amplifier}. Реальность трепещет!"
        )

    def describe(self) -> str:
        return (
            f"[ЛЕГЕНДАРНОЕ] Великое Плетение «{self.name}» — "
            f"первородная магия, усиленная в {self.amplifier}×. "
            f"Изменяет саму ткань Аркана Примы."
        )


# MRO вывод и объяснение
# LegendaryWeaveSpell.__mro__:
#   LegendaryWeaveSpell → WeaveSpell → Spell → ABC → object
# Python использует алгоритм C3-линеаризации:
#   1. LegendaryWeaveSpell — сам класс
#   2. WeaveSpell          — прямой родитель
#   3. Spell               — родитель WeaveSpell
#   4. ABC                 — родитель Spell (через наследование от ABC)
#   5. object              — корень всей иерархии Python


class CombinedSpell(Spell):
    """
    Составное заклинание (паттерн Composite).
    Принимает список заклинаний и применяет все в одном cast().
    Полиморфизм: работает как одиночное заклинание благодаря duck typing.
    """

    def __init__(self, name: str, spells: List[Spell]) -> None:
        if not spells:
            raise ValueError("CombinedSpell должен содержать хотя бы одно заклинание")
        total_cost = sum(s.cost for s in spells)
        max_rarity = max(spells, key=lambda s: s.rarity.value).rarity
        super().__init__(name, total_cost, max_rarity)
        self._spells = list(spells)

    def cast(self, caster: object, target: object) -> str:
        results = []
        for spell in self._spells:
            results.append(spell.cast(caster, target))
        combined = "\n".join(f"  ↳ {r}" for r in results)
        return f"💫 Составное заклинание «{self.name}»:\n{combined}"

    def describe(self) -> str:
        parts = "\n".join(f"  • {s.describe()}" for s in self._spells)
        return f"Составное заклинание «{self.name}» ({len(self._spells)} частей):\n{parts}"

    def __len__(self) -> int:
        return len(self._spells)
