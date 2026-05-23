"""
threads.py — Нити Реальности (Инкапсуляция)
Каждый объект мироздания сплетён из Нитей: Энергии, Формы и Времени.
"""

from __future__ import annotations


class Thread:
    """
    Базовый класс Нити Реальности.
    Инкапсуляция: внутренние параметры скрыты через приватные поля (__name mangling).
    Доступ снаружи — только через @property с валидацией.
    """

    def __init__(self, name: str, frequency: float, stability: float) -> None:
        self.__name: str = name
        self.frequency = frequency    # через сеттер — с валидацией
        self.stability = stability    # через сеттер — с валидацией

    # ── name ─────────────────────────────────────────────────────────────────
    @property
    def name(self) -> str:
        return self.__name

    # ── frequency ────────────────────────────────────────────────────────────
    @property
    def frequency(self) -> float:
        return self.__frequency

    @frequency.setter
    def frequency(self, value: float) -> None:
        if not (0.1 <= value <= 999.9):
            raise ValueError(
                f"frequency должна быть в диапазоне [0.1, 999.9], получено: {value}"
            )
        self.__frequency = float(value)

    # ── stability ─────────────────────────────────────────────────────────────
    @property
    def stability(self) -> float:
        return self.__stability

    @stability.setter
    def stability(self, value: float) -> None:
        if not (0.0 <= value <= 1.0):
            raise ValueError(
                f"stability должна быть в диапазоне [0.0, 1.0], получено: {value}"
            )
        self.__stability = float(value)

    # ── energy ───────────────────────────────────────────────────────────────
    @property
    def energy(self) -> float:
        """Вычисляемое свойство: энергия = частота × стабильность."""
        return self.__frequency * self.__stability

    # ── resonate ──────────────────────────────────────────────────────────────
    def resonate(self, other: "Thread") -> float:
        """
        Взаимодействие двух нитей.
        Возвращает суммарную энергию с учётом стабильности обеих.
        """
        return (self.energy + other.energy) * ((self.stability + other.stability) / 2)

    # ── operator overloading ──────────────────────────────────────────────────
    def __add__(self, other: "Thread") -> "Thread":
        """Слияние двух нитей → новая нить с усреднёнными параметрами."""
        new_freq = min((self.frequency + other.frequency) / 2, 999.9)
        new_stab = min((self.stability + other.stability) / 2, 1.0)
        new_name = f"{self.name}+{other.name}"
        return Thread(new_name, new_freq, new_stab)

    # ── dunder ────────────────────────────────────────────────────────────────
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.__name!r}, "
            f"frequency={self.__frequency}, "
            f"stability={self.__stability})"
        )

    def __str__(self) -> str:
        return (
            f"[Нить «{self.__name}»] "
            f"частота={self.__frequency:.1f} | "
            f"стабильность={self.__stability:.2f} | "
            f"энергия={self.energy:.2f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Дочерние классы нитей
# ─────────────────────────────────────────────────────────────────────────────

class EnergyThread(Thread):
    """
    Нить Энергии — хранит заряд и усиливает резонанс пропорционально ему.
    """

    def __init__(self, name: str, frequency: float, stability: float, charge: float = 1.0) -> None:
        super().__init__(name, frequency, stability)
        if charge < 0:
            raise ValueError(f"charge не может быть отрицательным, получено: {charge}")
        self.__charge = charge

    @property
    def charge(self) -> float:
        return self.__charge

    @charge.setter
    def charge(self, value: float) -> None:
        if value < 0:
            raise ValueError(f"charge не может быть отрицательным, получено: {value}")
        self.__charge = value

    def resonate(self, other: Thread) -> float:
        """Резонанс усилен зарядом нити."""
        base = super().resonate(other)
        return base * self.__charge

    def __str__(self) -> str:
        return super().__str__() + f" | заряд={self.__charge:.2f}"


class FormThread(Thread):
    """
    Нить Формы — несёт информацию о физической структуре объекта.
    Поле density (плотность) влияет на резонанс: более плотные нити резонируют стабильнее.
    """

    def __init__(self, name: str, frequency: float, stability: float, density: float = 1.0) -> None:
        super().__init__(name, frequency, stability)
        if density <= 0:
            raise ValueError(f"density должна быть > 0, получено: {density}")
        self.__density = density

    @property
    def density(self) -> float:
        return self.__density

    @density.setter
    def density(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"density должна быть > 0, получено: {value}")
        self.__density = value

    def resonate(self, other: Thread) -> float:
        """Резонанс масштабируется логарифмически от плотности."""
        import math
        base = super().resonate(other)
        return base * (1 + math.log1p(self.__density))

    def __str__(self) -> str:
        return super().__str__() + f" | плотность={self.__density:.2f}"


class TimeThread(Thread):
    """
    Нить Времени — содержит временной сдвиг объекта.
    age (возраст, тысячелетий) снижает стабильность резонанса.
    """

    def __init__(self, name: str, frequency: float, stability: float, age: float = 0.0) -> None:
        super().__init__(name, frequency, stability)
        if age < 0:
            raise ValueError(f"age не может быть отрицательным, получено: {age}")
        self.__age = age

    @property
    def age(self) -> float:
        return self.__age

    @age.setter
    def age(self, value: float) -> None:
        if value < 0:
            raise ValueError(f"age не может быть отрицательным, получено: {value}")
        self.__age = value

    def resonate(self, other: Thread) -> float:
        """Чем старше нить — тем слабее резонанс (временной износ)."""
        base = super().resonate(other)
        decay = 1 / (1 + self.__age * 0.1)
        return base * decay

    def __str__(self) -> str:
        return super().__str__() + f" | возраст={self.__age:.1f} тыс. лет"
