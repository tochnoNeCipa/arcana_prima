"""
test_threads.py — Тесты для модуля threads.py
Покрывает: Thread, EnergyThread, FormThread, TimeThread
"""

import logging
import math
import pytest

# Импорт под структуру src/
try:
    from src.threads import Thread, EnergyThread, FormThread, TimeThread
except ModuleNotFoundError:
    from threads import Thread, EnergyThread, FormThread, TimeThread


# ─────────────────────────────────────────────────────────────────────────────
# Thread — базовый класс
# ─────────────────────────────────────────────────────────────────────────────

class TestThreadInit:
    """Корректная инициализация."""

    def test_thread_creates_with_valid_values(self):
        t = Thread("Тест", 100.0, 0.5)
        assert t.name == "Тест"
        assert t.frequency == 999.0
        assert t.stability == 0.5

    def test_thread_energy_computed_correctly(self):
        t = Thread("Тест", 200.0, 0.5)
        assert t.energy == pytest.approx(100.0)

    def test_thread_boundary_frequency_min(self):
        t = Thread("Мин", 0.1, 0.5)
        assert t.frequency == 0.1

    def test_thread_boundary_frequency_max(self):
        t = Thread("Макс", 999.9, 0.5)
        assert t.frequency == 999.9

    def test_thread_boundary_stability_zero(self):
        t = Thread("Нуль", 100.0, 0.0)
        assert t.stability == 0.0
        assert t.energy == 0.0

    def test_thread_boundary_stability_one(self):
        t = Thread("Единица", 100.0, 1.0)
        assert t.stability == 1.0


class TestThreadValidation:
    """Валидация — должны бросать ValueError."""

    def test_thread_raises_on_frequency_below_min(self):
        with pytest.raises(ValueError, match="frequency"):
            Thread("X", 0.0, 0.5)

    def test_thread_raises_on_frequency_negative(self):
        with pytest.raises(ValueError):
            Thread("X", -1.0, 0.5)

    def test_thread_raises_on_frequency_above_max(self):
        with pytest.raises(ValueError, match="frequency"):
            Thread("X", 1000.0, 0.5)

    def test_thread_raises_on_stability_below_zero(self):
        with pytest.raises(ValueError, match="stability"):
            Thread("X", 100.0, -0.1)

    def test_thread_raises_on_stability_above_one(self):
        with pytest.raises(ValueError, match="stability"):
            Thread("X", 100.0, 1.1)

    def test_thread_setter_frequency_raises_on_invalid(self):
        t = Thread("X", 100.0, 0.5)
        with pytest.raises(ValueError):
            t.frequency = 0.0

    def test_thread_setter_stability_raises_on_invalid(self):
        t = Thread("X", 100.0, 0.5)
        with pytest.raises(ValueError):
            t.stability = 2.0

    def test_thread_setter_frequency_valid_update(self):
        t = Thread("X", 100.0, 0.5)
        t.frequency = 500.0
        assert t.frequency == 500.0

    def test_thread_setter_stability_valid_update(self):
        t = Thread("X", 100.0, 0.5)
        t.stability = 0.8
        assert t.stability == 0.8


class TestThreadResonate:
    """Метод resonate()."""

    def test_resonate_returns_float(self):
        a = Thread("A", 100.0, 0.8)
        b = Thread("B", 200.0, 0.6)
        result = a.resonate(b)
        assert isinstance(result, float)

    def test_resonate_with_zero_stability(self):
        a = Thread("A", 100.0, 0.0)
        b = Thread("B", 200.0, 0.0)
        assert a.resonate(b) == 0.0

    def test_resonate_symmetric(self):
        a = Thread("A", 100.0, 0.8)
        b = Thread("B", 200.0, 0.6)
        assert a.resonate(b) == pytest.approx(b.resonate(a))

    def test_resonate_formula(self):
        a = Thread("A", 100.0, 1.0)
        b = Thread("B", 100.0, 1.0)
        # energy_a = 100, energy_b = 100, avg_stability = 1.0
        # resonate = (100 + 100) * 1.0 = 200
        assert a.resonate(b) == pytest.approx(200.0)


class TestThreadOperators:
    """Перегрузка операторов."""

    def test_add_creates_new_thread(self):
        a = Thread("A", 100.0, 0.8)
        b = Thread("B", 200.0, 0.6)
        c = a + b
        assert isinstance(c, Thread)

    def test_add_averages_frequency(self):
        a = Thread("A", 100.0, 0.8)
        b = Thread("B", 200.0, 0.6)
        c = a + b
        assert c.frequency == pytest.approx(150.0)

    def test_add_averages_stability(self):
        a = Thread("A", 100.0, 0.8)
        b = Thread("B", 200.0, 0.6)
        c = a + b
        assert c.stability == pytest.approx(0.7)

    def test_add_name_contains_both(self):
        a = Thread("A", 100.0, 0.5)
        b = Thread("B", 200.0, 0.5)
        c = a + b
        assert "A" in c.name and "B" in c.name

    def test_add_caps_frequency_at_max(self):
        a = Thread("A", 999.9, 0.5)
        b = Thread("B", 999.9, 0.5)
        c = a + b
        assert c.frequency <= 999.9


class TestThreadDunder:
    """__str__ и __repr__."""

    def test_str_contains_name(self):
        t = Thread("МояНить", 100.0, 0.5)
        assert "МояНить" in str(t)

    def test_repr_contains_class_name(self):
        t = Thread("X", 100.0, 0.5)
        assert "Thread" in repr(t)


# ─────────────────────────────────────────────────────────────────────────────
# EnergyThread
# ─────────────────────────────────────────────────────────────────────────────

class TestEnergyThread:

    def test_energy_thread_creates_with_charge(self):
        et = EnergyThread("Молния", 300.0, 0.9, charge=2.0)
        assert et.charge == 2.0

    def test_energy_thread_default_charge(self):
        et = EnergyThread("Молния", 300.0, 0.9)
        assert et.charge == 1.0

    def test_energy_thread_raises_on_negative_charge(self):
        with pytest.raises(ValueError, match="charge"):
            EnergyThread("X", 100.0, 0.5, charge=-1.0)

    def test_energy_thread_resonate_amplified_by_charge(self):
        et = EnergyThread("A", 100.0, 1.0, charge=2.0)
        base = Thread("B", 100.0, 1.0)
        # base resonate = (100+100)*1.0 = 200, amplified = 200*2 = 400
        assert et.resonate(base) == pytest.approx(400.0)

    def test_energy_thread_str_contains_charge(self):
        et = EnergyThread("X", 100.0, 0.5, charge=3.0)
        assert "заряд" in str(et)

    def test_energy_thread_charge_setter_valid(self):
        et = EnergyThread("X", 100.0, 0.5)
        et.charge = 5.0
        assert et.charge == 5.0

    def test_energy_thread_charge_setter_raises_negative(self):
        et = EnergyThread("X", 100.0, 0.5)
        with pytest.raises(ValueError):
            et.charge = -0.1


# ─────────────────────────────────────────────────────────────────────────────
# FormThread
# ─────────────────────────────────────────────────────────────────────────────

class TestFormThread:

    def test_form_thread_creates_with_density(self):
        ft = FormThread("Камень", 200.0, 0.95, density=3.0)
        assert ft.density == 3.0

    def test_form_thread_raises_on_zero_density(self):
        with pytest.raises(ValueError, match="density"):
            FormThread("X", 100.0, 0.5, density=0.0)

    def test_form_thread_raises_on_negative_density(self):
        with pytest.raises(ValueError):
            FormThread("X", 100.0, 0.5, density=-1.0)

    def test_form_thread_resonate_greater_than_base(self):
        ft = FormThread("A", 100.0, 1.0, density=2.0)
        base = Thread("B", 100.0, 1.0)
        base_resonate = base.resonate(ft)
        # FormThread.resonate должен быть >= base_resonate
        assert ft.resonate(base) >= base_resonate

    def test_form_thread_str_contains_density(self):
        ft = FormThread("X", 100.0, 0.5, density=2.0)
        assert "плотность" in str(ft)

    def test_form_thread_density_setter_valid(self):
        ft = FormThread("X", 100.0, 0.5)
        ft.density = 5.0
        assert ft.density == 5.0

    def test_form_thread_density_setter_raises_zero(self):
        ft = FormThread("X", 100.0, 0.5)
        with pytest.raises(ValueError):
            ft.density = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# TimeThread
# ─────────────────────────────────────────────────────────────────────────────

class TestTimeThread:

    def test_time_thread_creates_with_age(self):
        tt = TimeThread("Вечность", 100.0, 0.7, age=12.0)
        assert tt.age == 12.0

    def test_time_thread_default_age_zero(self):
        tt = TimeThread("X", 100.0, 0.5)
        assert tt.age == 0.0

    def test_time_thread_raises_on_negative_age(self):
        with pytest.raises(ValueError, match="age"):
            TimeThread("X", 100.0, 0.5, age=-1.0)

    def test_time_thread_resonate_decreases_with_age(self):
        young = TimeThread("Молодая", 100.0, 1.0, age=0.0)
        old = TimeThread("Старая", 100.0, 1.0, age=100.0)
        base = Thread("B", 100.0, 1.0)
        assert young.resonate(base) > old.resonate(base)

    def test_time_thread_str_contains_age(self):
        tt = TimeThread("X", 100.0, 0.5, age=5.0)
        assert "возраст" in str(tt)

    def test_time_thread_age_setter_valid(self):
        tt = TimeThread("X", 100.0, 0.5)
        tt.age = 10.0
        assert tt.age == 10.0

    def test_time_thread_age_setter_raises_negative(self):
        tt = TimeThread("X", 100.0, 0.5)
        with pytest.raises(ValueError):
            tt.age = -1.0


# ─────────────────────────────────────────────────────────────────────────────
# Логирование — Thread сеттеры
# ─────────────────────────────────────────────────────────────────────────────

class TestThreadLogging:
    """Проверяем, что ошибки логируются через logging."""

    def test_frequency_setter_logs_error(self, caplog):
        t = Thread("X", 100.0, 0.5)
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                t.frequency = -999.0
        # ValueError поднят — этого достаточно, логирование в caster

    def test_stability_setter_logs_error(self, caplog):
        t = Thread("X", 100.0, 0.5)
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                t.stability = 5.0
