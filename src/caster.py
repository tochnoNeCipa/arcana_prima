"""
caster.py — Нитяры и интерфейсы (Абстракция + Полиморфизм)
"""

from __future__ import annotations

import warnings
from typing import Dict, List, Optional, Protocol, runtime_checkable

from src.spells import Spell
from src.artifacts import Artifact


# ─────────────────────────────────────────────────────────────────────────────
# Protocol — структурная типизация (duck typing с аннотациями)
# ─────────────────────────────────────────────────────────────────────────────

@runtime_checkable
class ArcaneInterface(Protocol):
    """
    Любой класс с методами cast() и describe() автоматически является
    реализацией ArcaneInterface — без явного наследования (duck typing).
    """

    def cast(self, caster: object, target: object) -> str:
        ...

    def describe(self) -> str:
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Класс Нитяра
# ─────────────────────────────────────────────────────────────────────────────

class Caster:
    """
    Нитяр — маг, владеющий заклинаниями и артефактами.
    Абстракция: внутренняя книга заклинаний скрыта (__spell_book).
    """

    def __init__(self, name: str, energy: float,
                 artifact: Optional[Artifact] = None) -> None:
        self.name = name
        self.energy = energy
        self.artifact: Optional[Artifact] = None
        self.effects: List[str] = []          # активные эффекты от заклинаний
        self.__spell_book: Dict[str, Spell] = {}

        if artifact is not None:
            self.equip(artifact)

    # ── spell book ────────────────────────────────────────────────────────────

    def learn(self, spell: Spell) -> None:
        """Добавить заклинание в книгу."""
        self.__spell_book[spell.name] = spell
        print(f"📖 {self.name} выучил заклинание «{spell.name}».")

    def forget(self, spell_name: str) -> None:
        """Удалить заклинание по имени."""
        if spell_name not in self.__spell_book:
            raise KeyError(f"Заклинание «{spell_name}» не найдено в книге {self.name}.")
        del self.__spell_book[spell_name]
        print(f"❌ {self.name} забыл заклинание «{spell_name}».")

    def cast(self, spell_name: str, target: object) -> str:
        """Применить заклинание из книги к цели."""
        if spell_name not in self.__spell_book:
            raise KeyError(f"У {self.name} нет заклинания «{spell_name}».")
        spell = self.__spell_book[spell_name]
        if self.energy < spell.cost:
            return f"⚠️ {self.name} не хватает энергии для «{spell_name}» (нужно {spell.cost}, есть {self.energy:.1f})."
        return spell.cast(self, target)

    def get_spell(self, spell_name: str) -> Spell:
        """Получить объект заклинания по имени (read-only доступ)."""
        if spell_name not in self.__spell_book:
            raise KeyError(f"Заклинание «{spell_name}» не найдено.")
        return self.__spell_book[spell_name]

    def list_spells(self) -> List[str]:
        """Список имён всех известных заклинаний."""
        return list(self.__spell_book.keys())

    # ── artifact ──────────────────────────────────────────────────────────────

    def equip(self, artifact: Artifact) -> None:
        """Экипировать артефакт; предупреждение при замене."""
        if self.artifact is not None:
            warnings.warn(
                f"⚠️ {self.name} заменяет артефакт «{self.artifact.name}» "
                f"на «{artifact.name}»!",
                UserWarning,
                stacklevel=2,
            )
        self.artifact = artifact
        print(f"💎 {self.name} экипировал артефакт «{artifact.name}».")

    # ── dunder ────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        """Количество заклинаний в книге."""
        return len(self.__spell_book)

    def __repr__(self) -> str:
        return (
            f"Caster(name={self.name!r}, energy={self.energy}, "
            f"spells={len(self)}, artifact={self.artifact!r})"
        )

    def __str__(self) -> str:
        artifact_str = self.artifact.name if self.artifact else "нет"
        effects_str = ", ".join(self.effects) if self.effects else "нет"
        return (
            f"╔══ Нитяр: {self.name}\n"
            f"║  Энергия: {self.energy:.1f}\n"
            f"║  Заклинаний: {len(self)}\n"
            f"║  Артефакт: {artifact_str}\n"
            f"╚══ Эффекты: {effects_str}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Вспомогательная функция (Полиморфизм — duck typing)
# ─────────────────────────────────────────────────────────────────────────────

def execute_all(spells: list, caster: object, target: object) -> None:
    """
    Применяет все заклинания из списка к цели.
    Полиморфизм через duck typing: любой объект с методом cast() подходит.
    isinstance() не используется.
    """
    print(f"\n{'═' * 50}")
    print(f"⚡ Массовое применение заклинаний ({len(spells)} шт.)")
    print(f"{'═' * 50}")
    for spell in spells:
        result = spell.cast(caster, target)
        print(result)
    print(f"{'═' * 50}\n")
