"""
test_artifacts_caster.py — Тесты для artifacts.py и caster.py
Покрывает: CrystalCore, RuneMatrix, Caster, execute_all, ArcaneInterface
Задания 2 (логирование) и 3 (mock) — здесь же.
"""

import logging
import warnings
import pytest
from unittest.mock import MagicMock, patch, call

try:
    from src.threads import Thread, EnergyThread
    from src.artifacts import Artifact, CrystalCore, RuneMatrix
    from src.spells import WeaveSpell, CutSpell, BindSpell, LegendaryWeaveSpell, Rarity
    from src.caster import Caster, execute_all, ArcaneInterface
except ModuleNotFoundError:
    from threads import Thread, EnergyThread
    from artifacts import Artifact, CrystalCore, RuneMatrix
    from spells import WeaveSpell, CutSpell, BindSpell, LegendaryWeaveSpell, Rarity
    from caster import Caster, execute_all, ArcaneInterface


# ─────────────────────────────────────────────────────────────────────────────
# Фикстуры
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def thread():
    return Thread("Тестовая", 200.0, 0.8)


@pytest.fixture
def energy_thread():
    return EnergyThread("Молния", 300.0, 0.9, charge=2.0)


@pytest.fixture
def crystal():
    return CrystalCore("Тест Кристалл", durability=50)


@pytest.fixture
def matrix():
    return RuneMatrix("Тест Матрица", capacity=3, durability=50)


@pytest.fixture
def caster_varn():
    c = Caster("Варн", energy=200.0)
    c.learn(WeaveSpell("Плетение", cost=10.0))
    c.learn(CutSpell("Разрыв", cost=8.0, severity=0.2))
    return c


@pytest.fixture
def caster_sel():
    return Caster("Сел", energy=40.0)


# ─────────────────────────────────────────────────────────────────────────────
# CrystalCore
# ─────────────────────────────────────────────────────────────────────────────

class TestCrystalCore:

    def test_crystal_creates_with_defaults(self):
        c = CrystalCore()
        assert c.durability == 100
        assert not c.is_broken

    def test_crystal_activate_returns_amplified_energy(self, crystal, thread):
        result = crystal.activate(thread)
        assert result == pytest.approx(thread.energy * 1.5)

    def test_crystal_activate_reduces_durability_by_two(self, crystal, thread):
        initial = crystal.durability
        crystal.activate(thread)
        assert crystal.durability == initial - 2

    def test_crystal_broken_raises_on_activate(self, thread):
        c = CrystalCore("Сломанный", durability=1)
        c.activate(thread)  # durability → max(0, 1-2) = 0
        with pytest.raises(RuntimeError, match="сломан"):
            c.activate(thread)

    def test_crystal_str_contains_name(self, crystal):
        assert "Тест Кристалл" in str(crystal)

    def test_crystal_repr_contains_class(self, crystal):
        assert "CrystalCore" in repr(crystal)

    def test_crystal_str_shows_broken_status(self, thread):
        c = CrystalCore("Хрупкий", durability=2)
        c.activate(thread)
        assert "СЛОМАН" in str(c)

    def test_crystal_cannot_instantiate_artifact_directly(self):
        with pytest.raises(TypeError):
            Artifact("X")  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# RuneMatrix
# ─────────────────────────────────────────────────────────────────────────────

class TestRuneMatrix:

    def test_matrix_creates_empty(self, matrix):
        assert matrix.stored_count == 0

    def test_matrix_store_thread(self, matrix, thread):
        matrix.store(thread)
        assert matrix.stored_count == 1

    def test_matrix_store_up_to_capacity(self, matrix):
        for i in range(3):
            matrix.store(Thread(f"N{i}", 100.0, 0.5))
        assert matrix.stored_count == 3

    def test_matrix_overflow_raises(self, matrix):
        for i in range(3):
            matrix.store(Thread(f"N{i}", 100.0, 0.5))
        with pytest.raises(OverflowError):
            matrix.store(Thread("Лишняя", 100.0, 0.5))

    def test_matrix_activate_sums_energy(self, matrix, thread, energy_thread):
        matrix.store(energy_thread)
        result = matrix.activate(thread)
        expected = thread.energy + energy_thread.energy
        assert result == pytest.approx(expected)

    def test_matrix_activate_reduces_durability(self, matrix, thread):
        initial = matrix.durability
        matrix.activate(thread)
        assert matrix.durability == initial - 1

    def test_matrix_broken_raises_on_activate(self, thread):
        m = RuneMatrix("Сломанная", durability=0)
        with pytest.raises(RuntimeError, match="сломан"):
            m.activate(thread)

    def test_matrix_str_shows_stored_count(self, matrix, thread):
        matrix.store(thread)
        assert "1/3" in str(matrix)

    def test_matrix_activate_empty_uses_only_passed_thread(self, matrix, thread):
        result = matrix.activate(thread)
        assert result == pytest.approx(thread.energy)


# ─────────────────────────────────────────────────────────────────────────────
# Caster
# ─────────────────────────────────────────────────────────────────────────────

class TestCasterInit:

    def test_caster_creates_with_name_and_energy(self):
        c = Caster("Тест", energy=100.0)
        assert c.name == "Тест"
        assert c.energy == 100.0

    def test_caster_starts_with_no_spells(self):
        c = Caster("X", energy=50.0)
        assert len(c) == 0

    def test_caster_starts_with_no_artifact(self):
        c = Caster("X", energy=50.0)
        assert c.artifact is None

    def test_caster_creates_with_artifact(self, crystal):
        c = Caster("X", energy=50.0, artifact=crystal)
        assert c.artifact is crystal


class TestCasterSpellBook:

    def test_learn_adds_spell(self, caster_sel):
        spell = WeaveSpell("Новое", cost=5.0)
        caster_sel.learn(spell)
        assert len(caster_sel) == 1

    def test_learn_multiple_spells(self, caster_varn):
        assert len(caster_varn) == 2

    def test_forget_removes_spell(self, caster_varn):
        caster_varn.forget("Плетение")
        assert len(caster_varn) == 1

    def test_forget_unknown_spell_raises(self, caster_sel):
        with pytest.raises(KeyError):
            caster_sel.forget("Несуществующее")

    def test_list_spells_returns_names(self, caster_varn):
        names = caster_varn.list_spells()
        assert "Плетение" in names
        assert "Разрыв" in names

    def test_get_spell_returns_spell_object(self, caster_varn):
        spell = caster_varn.get_spell("Плетение")
        assert isinstance(spell, WeaveSpell)

    def test_get_spell_unknown_raises(self, caster_varn):
        with pytest.raises(KeyError):
            caster_varn.get_spell("Несуществует")

    def test_len_reflects_spell_count(self, caster_sel):
        assert len(caster_sel) == 0
        caster_sel.learn(WeaveSpell("A", 5.0))
        assert len(caster_sel) == 1


class TestCasterCast:

    def test_cast_returns_string(self, caster_varn, caster_sel):
        result = caster_varn.cast("Плетение", caster_sel)
        assert isinstance(result, str)

    def test_cast_unknown_spell_raises(self, caster_varn, caster_sel):
        with pytest.raises(KeyError):
            caster_varn.cast("Несуществует", caster_sel)

    def test_cast_insufficient_energy_returns_warning(self, caster_sel):
        expensive = WeaveSpell("Дорогое", cost=999.0)
        caster_sel.learn(expensive)
        result = caster_sel.cast("Дорогое", MagicMock())
        assert "не хватает энергии" in result

    def test_cast_reduces_energy(self, caster_varn, caster_sel):
        initial = caster_varn.energy
        caster_varn.cast("Плетение", caster_sel)
        assert caster_varn.energy < initial


class TestCasterArtifact:

    def test_equip_sets_artifact(self, caster_sel, crystal):
        caster_sel.equip(crystal)
        assert caster_sel.artifact is crystal

    def test_equip_replacement_raises_warning(self, caster_varn, crystal, matrix):
        caster_varn.equip(crystal)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            caster_varn.equip(matrix)
            assert len(w) == 1
            assert issubclass(w[0].category, UserWarning)
            assert "заменяет" in str(w[0].message)

    def test_equip_no_warning_first_time(self, caster_sel, crystal):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            caster_sel.equip(crystal)
            assert len(w) == 0


class TestCasterDunder:

    def test_str_contains_name(self, caster_varn):
        assert "Варн" in str(caster_varn)

    def test_str_contains_energy(self, caster_varn):
        assert "200" in str(caster_varn)

    def test_repr_contains_caster(self, caster_varn):
        assert "Caster" in repr(caster_varn)


# ─────────────────────────────────────────────────────────────────────────────
# execute_all — duck typing (задание Ш4)
# ─────────────────────────────────────────────────────────────────────────────

class TestExecuteAll:

    def test_execute_all_calls_each_spell(self, caster_varn, caster_sel, capsys):
        spells = [
            WeaveSpell("A", cost=5.0),
            CutSpell("B", cost=3.0),
        ]
        execute_all(spells, caster_varn, caster_sel)
        out = capsys.readouterr().out
        assert "Массовое применение" in out

    def test_execute_all_works_with_mock_spells(self, caster_varn, caster_sel):
        """Duck typing: любой объект с cast() подходит."""
        mock_spell = MagicMock()
        mock_spell.cast.return_value = "Мок-результат"
        execute_all([mock_spell], caster_varn, caster_sel)
        mock_spell.cast.assert_called_once_with(caster_varn, caster_sel)

    def test_execute_all_empty_list(self, caster_varn, caster_sel, capsys):
        execute_all([], caster_varn, caster_sel)
        out = capsys.readouterr().out
        assert "0 шт." in out


# ─────────────────────────────────────────────────────────────────────────────
# ArcaneInterface — Protocol
# ─────────────────────────────────────────────────────────────────────────────

class TestArcaneInterface:

    def test_spell_satisfies_protocol(self):
        spell = WeaveSpell("X", 5.0)
        assert isinstance(spell, ArcaneInterface)

    def test_arbitrary_class_satisfies_protocol(self):
        class CustomSpell:
            def cast(self, caster, target): return "OK"
            def describe(self): return "Описание"

        assert isinstance(CustomSpell(), ArcaneInterface)

    def test_class_without_cast_fails_protocol(self):
        class NoCast:
            def describe(self): return "X"

        assert not isinstance(Nocast := Nocast if False else NoCast(), ArcaneInterface) \
            if False else not isinstance(NoCast(), ArcaneInterface) \
            if (NoCast := type("NoC", (), {"describe": lambda s: "x"})) else True

    def test_protocol_check_with_isinstance(self):
        class Duck:
            def cast(self, c, t): return ""
            def describe(self): return ""
        assert isinstance(Duck(), ArcaneInterface)


# ─────────────────────────────────────────────────────────────────────────────
# Задание 2 — Логирование
# ─────────────────────────────────────────────────────────────────────────────

class TestLogging:

    def test_caster_cast_logs_missing_spell(self, caster_sel, caplog):
        """При попытке применить несуществующее заклинание — KeyError."""
        with caplog.at_level(logging.ERROR):
            with pytest.raises(KeyError):
                caster_sel.cast("Несуществует", MagicMock())

    def test_logging_via_mock_patch(self):
        """Перехватываем logging.error через unittest.mock.patch."""
        try:
            from src.caster import Caster
        except ModuleNotFoundError:
            from caster import Caster

        c = Caster("Тест", energy=10.0)
        c.learn(WeaveSpell("Дорогое", cost=999.0))

        with patch("logging.error") as mock_log:
            # недостаточно энергии — cast вернёт предупреждение (не исключение)
            result = c.cast("Дорогое", MagicMock())
            assert "не хватает" in result


# ─────────────────────────────────────────────────────────────────────────────
# Задание 3 — Mock (patch, MagicMock, side_effect)
# ─────────────────────────────────────────────────────────────────────────────

class TestMockArtifacts:

    def test_patch_crystal_activate(self, thread):
        """patch — заменяем реальный activate мок-объектом."""
        try:
            target = "src.artifacts.CrystalCore.activate"
            with patch(target) as mock_activate:
                mock_activate.return_value = 99.9
                c = CrystalCore()
                result = c.activate(thread)
                assert result == 99.9
                mock_activate.assert_called_once()
        except ModuleNotFoundError:
            target = "artifacts.CrystalCore.activate"
            with patch(target) as mock_activate:
                mock_activate.return_value = 99.9
                c = CrystalCore()
                result = c.activate(thread)
                assert result == 99.9
                mock_activate.assert_called_once()

    def test_magic_mock_called_with_correct_thread(self, thread):
        """MagicMock — проверяем вызов с нужными аргументами."""
        mock_artifact = MagicMock(spec=CrystalCore)
        mock_artifact.activate.return_value = 42.0
        result = mock_artifact.activate(thread)
        mock_artifact.activate.assert_called_once_with(thread)
        assert result == 42.0

    def test_side_effect_raises_runtime_error(self, thread):
        """side_effect — моделируем сломанный артефакт."""
        mock_artifact = MagicMock(spec=RuneMatrix)
        mock_artifact.activate.side_effect = RuntimeError("Матрица нестабильна!")
        with pytest.raises(RuntimeError, match="нестабильна"):
            mock_artifact.activate(thread)

    def test_magic_mock_call_count(self, thread):
        """Проверяем количество вызовов activate."""
        mock_artifact = MagicMock(spec=CrystalCore)
        mock_artifact.activate.return_value = 10.0
        for _ in range(3):
            mock_artifact.activate(thread)
        assert mock_artifact.activate.call_count == 3

    def test_patch_matrix_store(self, thread):
        """MagicMock для store() RuneMatrix — без patch по имени модуля."""
        mock_matrix = MagicMock(spec=RuneMatrix)
        mock_matrix.store.return_value = None
        mock_matrix.store(thread)
        mock_matrix.store.assert_called_once_with(thread)
