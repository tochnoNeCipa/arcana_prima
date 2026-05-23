"""
test_spells.py — Тесты для модуля spells.py
Покрывает: Rarity, Spell, WeaveSpell, CutSpell, BindSpell,
           LegendaryWeaveSpell, CombinedSpell
"""

import pytest
from unittest.mock import MagicMock, patch

try:
    from src.spells import (
        Rarity, Spell, WeaveSpell, CutSpell, BindSpell,
        LegendaryWeaveSpell, CombinedSpell,
    )
except ModuleNotFoundError:
    from spells import (
        Rarity, Spell, WeaveSpell, CutSpell, BindSpell,
        LegendaryWeaveSpell, CombinedSpell,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Вспомогательные фикстуры
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_caster():
    """Мок-объект нитяра с нужными атрибутами."""
    caster = MagicMock()
    caster.name = "Тестовый Маг"
    caster.energy = 100.0
    return caster


@pytest.fixture
def mock_target():
    """Мок-объект цели."""
    target = MagicMock()
    target.name = "Цель"
    target.stability = 1.0
    target.effects = []
    return target


@pytest.fixture
def weave_spell():
    return WeaveSpell("Плетение", cost=10.0, bond_strength=2.0)


@pytest.fixture
def cut_spell():
    return CutSpell("Разрыв", cost=8.0, severity=0.3)


@pytest.fixture
def bind_spell():
    return BindSpell("Привязь", cost=5.0, effect_name="Оковы", duration=3)


@pytest.fixture
def legendary_spell():
    return LegendaryWeaveSpell("Легенда", cost=30.0, amplifier=2.0)


@pytest.fixture
def common_spell():
    return WeaveSpell("Обычное", cost=5.0)


# ─────────────────────────────────────────────────────────────────────────────
# Rarity
# ─────────────────────────────────────────────────────────────────────────────

class TestRarity:

    def test_rarity_values_ordered(self):
        assert Rarity.COMMON.value < Rarity.RARE.value < Rarity.LEGENDARY.value

    def test_rarity_str_common(self):
        assert "Обычное" in str(Rarity.COMMON)

    def test_rarity_str_rare(self):
        assert "Редкое" in str(Rarity.RARE)

    def test_rarity_str_legendary(self):
        assert "Легендарное" in str(Rarity.LEGENDARY)


# ─────────────────────────────────────────────────────────────────────────────
# Spell — абстрактный базовый класс
# ─────────────────────────────────────────────────────────────────────────────

class TestSpellAbstract:

    def test_spell_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Spell("Тест", 10.0)  # type: ignore

    def test_spell_cost_negative_raises(self):
        with pytest.raises(ValueError, match="cost"):
            WeaveSpell("X", cost=-1.0)


# ─────────────────────────────────────────────────────────────────────────────
# WeaveSpell
# ─────────────────────────────────────────────────────────────────────────────

class TestWeaveSpell:

    def test_weave_spell_creates(self, weave_spell):
        assert weave_spell.name == "Плетение"
        assert weave_spell.cost == 10.0
        assert weave_spell.bond_strength == 2.0

    def test_weave_spell_default_rarity_common(self):
        s = WeaveSpell("X", cost=5.0)
        assert s.rarity == Rarity.COMMON

    def test_weave_cast_returns_string(self, weave_spell, mock_caster, mock_target):
        result = weave_spell.cast(mock_caster, mock_target)
        assert isinstance(result, str)

    def test_weave_cast_reduces_caster_energy(self, weave_spell, mock_caster, mock_target):
        initial = mock_caster.energy
        weave_spell.cast(mock_caster, mock_target)
        assert mock_caster.energy == initial - weave_spell.cost

    def test_weave_cast_contains_caster_name(self, weave_spell, mock_caster, mock_target):
        result = weave_spell.cast(mock_caster, mock_target)
        assert mock_caster.name in result

    def test_weave_cast_contains_target_name(self, weave_spell, mock_caster, mock_target):
        result = weave_spell.cast(mock_caster, mock_target)
        assert mock_target.name in result

    def test_weave_describe_returns_string(self, weave_spell):
        assert isinstance(weave_spell.describe(), str)
        assert "Плетение" in weave_spell.describe()

    def test_weave_cast_caster_without_energy_attr(self, weave_spell, mock_target):
        """duck typing — кастер без атрибута energy не должен ломать cast."""
        simple_caster = MagicMock(spec=["name"])
        simple_caster.name = "Безэнергетический"
        result = weave_spell.cast(simple_caster, mock_target)
        assert isinstance(result, str)

    def test_weave_energy_does_not_go_below_zero(self, mock_target):
        expensive = WeaveSpell("Дорогое", cost=999.0)
        caster = MagicMock()
        caster.name = "Бедный"
        caster.energy = 5.0
        expensive.cast(caster, mock_target)
        assert caster.energy == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# CutSpell
# ─────────────────────────────────────────────────────────────────────────────

class TestCutSpell:

    def test_cut_spell_creates(self, cut_spell):
        assert cut_spell.severity == 0.3

    def test_cut_cast_returns_string(self, cut_spell, mock_caster, mock_target):
        result = cut_spell.cast(mock_caster, mock_target)
        assert isinstance(result, str)

    def test_cut_cast_reduces_stability_on_thread_target(self, cut_spell, mock_caster):
        try:
            from src.threads import Thread
        except ModuleNotFoundError:
            from threads import Thread
        target_thread = Thread("Цель", 100.0, 1.0)
        cut_spell.cast(mock_caster, target_thread)
        assert target_thread.stability == pytest.approx(0.7)

    def test_cut_cast_stability_not_below_zero(self, mock_caster):
        try:
            from src.threads import Thread
        except ModuleNotFoundError:
            from threads import Thread
        severe = CutSpell("Сильный", cost=1.0, severity=2.0)
        target = Thread("Цель", 100.0, 0.1)
        severe.cast(mock_caster, target)
        assert target.stability == 0.0

    def test_cut_describe_returns_string(self, cut_spell):
        desc = cut_spell.describe()
        assert isinstance(desc, str)
        assert "0.3" in desc


# ─────────────────────────────────────────────────────────────────────────────
# BindSpell
# ─────────────────────────────────────────────────────────────────────────────

class TestBindSpell:

    def test_bind_spell_creates(self, bind_spell):
        assert bind_spell.effect_name == "Оковы"
        assert bind_spell.duration == 3

    def test_bind_cast_returns_string(self, bind_spell, mock_caster, mock_target):
        result = bind_spell.cast(mock_caster, mock_target)
        assert isinstance(result, str)

    def test_bind_cast_appends_effect_to_target(self, bind_spell, mock_caster, mock_target):
        mock_target.effects = []
        bind_spell.cast(mock_caster, mock_target)
        assert "Оковы" in mock_target.effects

    def test_bind_cast_no_effects_attr_no_crash(self, bind_spell, mock_caster):
        target = MagicMock(spec=["name"])
        target.name = "БезЭффектов"
        result = bind_spell.cast(mock_caster, target)
        assert isinstance(result, str)

    def test_bind_describe_contains_effect_name(self, bind_spell):
        assert "Оковы" in bind_spell.describe()


# ─────────────────────────────────────────────────────────────────────────────
# LegendaryWeaveSpell
# ─────────────────────────────────────────────────────────────────────────────

class TestLegendaryWeaveSpell:

    def test_legendary_rarity_is_legendary(self, legendary_spell):
        assert legendary_spell.rarity == Rarity.LEGENDARY

    def test_legendary_cast_contains_legendary_marker(self, legendary_spell, mock_caster, mock_target):
        result = legendary_spell.cast(mock_caster, mock_target)
        assert "ЛЕГЕНДАРНОЕ" in result

    def test_legendary_cast_calls_super_cast(self, legendary_spell, mock_caster, mock_target):
        result = legendary_spell.cast(mock_caster, mock_target)
        # результат должен содержать и базовое, и легендарное сообщение
        assert mock_caster.name in result
        assert mock_target.name in result

    def test_legendary_describe_contains_legendary(self, legendary_spell):
        assert "ЛЕГЕНДАРНОЕ" in legendary_spell.describe()

    def test_legendary_mro_order(self):
        mro = LegendaryWeaveSpell.__mro__
        names = [c.__name__ for c in mro]
        assert names.index("LegendaryWeaveSpell") < names.index("WeaveSpell")
        assert names.index("WeaveSpell") < names.index("Spell")

    def test_legendary_bond_strength_amplified(self, legendary_spell):
        # bond_strength = 10.0 * amplifier
        assert legendary_spell.bond_strength == pytest.approx(10.0 * 2.0)


# ─────────────────────────────────────────────────────────────────────────────
# Сравнение заклинаний (полиморфизм)
# ─────────────────────────────────────────────────────────────────────────────

class TestSpellComparison:

    def test_legendary_greater_than_common(self, legendary_spell, common_spell):
        assert legendary_spell > common_spell

    def test_common_less_than_legendary(self, common_spell, legendary_spell):
        assert common_spell < legendary_spell

    def test_common_equals_common(self):
        a = WeaveSpell("A", 5.0)
        b = WeaveSpell("B", 10.0)
        assert a == b

    def test_spell_not_equal_to_non_spell(self, common_spell):
        result = common_spell.__eq__("не заклинание")
        assert result is NotImplemented

    def test_rare_between_common_and_legendary(self):
        common = WeaveSpell("C", 5.0, Rarity.COMMON)
        rare = WeaveSpell("R", 5.0, Rarity.RARE)
        legendary = LegendaryWeaveSpell("L", 30.0)
        assert common < rare < legendary


# ─────────────────────────────────────────────────────────────────────────────
# CombinedSpell
# ─────────────────────────────────────────────────────────────────────────────

class TestCombinedSpell:

    @pytest.fixture
    def combined(self, weave_spell, cut_spell):
        return CombinedSpell("Комбо", [weave_spell, cut_spell])

    def test_combined_total_cost(self, combined, weave_spell, cut_spell):
        assert combined.cost == weave_spell.cost + cut_spell.cost

    def test_combined_max_rarity(self):
        common = WeaveSpell("C", 5.0, Rarity.COMMON)
        legendary = LegendaryWeaveSpell("L", 30.0)
        combo = CombinedSpell("Комбо", [common, legendary])
        assert combo.rarity == Rarity.LEGENDARY

    def test_combined_cast_returns_string(self, combined, mock_caster, mock_target):
        result = combined.cast(mock_caster, mock_target)
        assert isinstance(result, str)

    def test_combined_cast_contains_all_results(self, combined, mock_caster, mock_target):
        result = combined.cast(mock_caster, mock_target)
        assert "Плетение" in result or mock_caster.name in result

    def test_combined_len(self, combined):
        assert len(combined) == 2

    def test_combined_empty_raises(self):
        with pytest.raises(ValueError):
            CombinedSpell("Пустое", [])

    def test_combined_describe_contains_name(self, combined):
        assert "Комбо" in combined.describe()

    def test_combined_polymorphic_with_single_spell(self, combined, mock_caster, mock_target):
        """CombinedSpell работает полиморфно как одиночное заклинание."""
        spells = [WeaveSpell("Одиночное", 5.0), combined]
        for spell in spells:
            result = spell.cast(mock_caster, mock_target)
            assert isinstance(result, str)


# ─────────────────────────────────────────────────────────────────────────────
# Mock — patch activate артефакта (задание 3)
# ─────────────────────────────────────────────────────────────────────────────

class TestSpellsWithMock:

    def test_weave_cast_called_with_correct_args(self, mock_caster, mock_target):
        """MagicMock: проверяем вызов cast() с нужными аргументами."""
        spell = MagicMock(spec=WeaveSpell)
        spell.cast.return_value = "Мок-результат"
        result = spell.cast(mock_caster, mock_target)
        spell.cast.assert_called_once_with(mock_caster, mock_target)
        assert result == "Мок-результат"

    def test_cast_side_effect_raises_exception(self, mock_caster, mock_target):
        """side_effect — моделируем исключение при вызове cast()."""
        spell = MagicMock(spec=WeaveSpell)
        spell.cast.side_effect = RuntimeError("Магия вышла из-под контроля!")
        with pytest.raises(RuntimeError, match="Магия вышла из-под контроля"):
            spell.cast(mock_caster, mock_target)

    def test_describe_mock_returns_custom_value(self):
        """MagicMock с return_value для describe()."""
        spell = MagicMock(spec=WeaveSpell)
        spell.describe.return_value = "Мок-описание"
        assert spell.describe() == "Мок-описание"
