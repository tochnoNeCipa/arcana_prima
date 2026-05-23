"""
artifacts.py — Артефакты-Исполнители (Абстракция)
Пользователь знает только интерфейс activate() — детали скрыты внутри.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from src.threads import Thread


# ─────────────────────────────────────────────────────────────────────────────
# Абстрактный базовый класс
# ─────────────────────────────────────────────────────────────────────────────

class Artifact(ABC):
    """
    Абстрактный артефакт.
    Абстракция: пользователь вызывает activate() — внутренняя логика скрыта.
    """

    def __init__(self, name: str, durability: int = 100) -> None:
        self.name = name
        self.__durability = durability

    @property
    def durability(self) -> int:
        return self.__durability

    def _reduce_durability(self, amount: int = 1) -> None:
        """Внутренний метод снижения прочности (не часть публичного API)."""
        self.__durability = max(0, self.__durability - amount)

    @property
    def is_broken(self) -> bool:
        return self.__durability <= 0

    @abstractmethod
    def activate(self, thread: Thread) -> float:
        """Активировать артефакт с нитью; возвращает результирующую энергию."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, durability={self.__durability})"

    def __str__(self) -> str:
        status = "⚠️ СЛОМАН" if self.is_broken else f"прочность={self.__durability}"
        return f"[Артефакт «{self.name}»] {status}"


# ─────────────────────────────────────────────────────────────────────────────
# Конкретные артефакты
# ─────────────────────────────────────────────────────────────────────────────

class CrystalCore(Artifact):
    """
    Кристальное Ядро — усиливает резонанс нити на коэффициент 1.5.
    Каждая активация снижает прочность на 2.
    """

    AMPLIFY_FACTOR: float = 1.5

    def __init__(self, name: str = "Кристальное Ядро", durability: int = 100) -> None:
        super().__init__(name, durability)

    def activate(self, thread: Thread) -> float:
        if self.is_broken:
            raise RuntimeError(f"Артефакт «{self.name}» сломан и не может быть активирован!")
        result = thread.energy * self.AMPLIFY_FACTOR
        self._reduce_durability(2)
        return result

    def __str__(self) -> str:
        return super().__str__() + f" | усиление ×{self.AMPLIFY_FACTOR}"


class RuneMatrix(Artifact):
    """
    Руническая Матрица — накапливает нити (до capacity) и суммирует их энергию.
    """

    def __init__(self, name: str = "Руническая Матрица",
                 capacity: int = 5, durability: int = 100) -> None:
        super().__init__(name, durability)
        self._capacity = capacity
        self._stored_threads: List[Thread] = []

    def store(self, thread: Thread) -> None:
        """Добавить нить в матрицу."""
        if len(self._stored_threads) >= self._capacity:
            raise OverflowError(
                f"Руническая Матрица заполнена ({self._capacity}/{self._capacity}). "
                "Освободите слот перед добавлением."
            )
        self._stored_threads.append(thread)

    def activate(self, thread: Thread) -> float:
        """Суммирует энергию всех накопленных нитей + переданной нити."""
        if self.is_broken:
            raise RuntimeError(f"Артефакт «{self.name}» сломан!")
        self._reduce_durability(1)
        total = thread.energy + sum(t.energy for t in self._stored_threads)
        return total

    @property
    def stored_count(self) -> int:
        return len(self._stored_threads)

    def __str__(self) -> str:
        return (
            super().__str__()
            + f" | нитей: {self.stored_count}/{self._capacity}"
        )
