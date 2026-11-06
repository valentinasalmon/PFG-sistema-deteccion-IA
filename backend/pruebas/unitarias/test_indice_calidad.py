"""Pruebas del cálculo del Índice de Calidad del Software (018, RNF19 CA2)."""
import json

import pytest

from herramientas import indice_calidad as qi


def test_con_todos_los_componentes_es_el_promedio_ponderado():
    """Con los seis componentes, los pesos son los publicados."""
    componentes = {"Cb": 1, "Cf": 1, "E": 1, "K": 1, "D": 1, "U": 0.5}
    resultado = qi.calcular_indice(componentes)
    assert resultado["qi"] == pytest.approx(0.85)
    assert resultado["cumple"] is True
    assert resultado["provisorio"] is False


def test_sin_usabilidad_se_reescalan_los_pesos():
    """Sin SUS, el resultado es provisorio y los pesos efectivos suman 1."""
    componentes = {"Cb": 0.9, "Cf": 0.8, "E": 1, "K": 1, "D": 1, "U": None}
    resultado = qi.calcular_indice(componentes)
    assert resultado["provisorio"] is True
    assert sum(resultado["pesos"].values()) == pytest.approx(1)
    assert "U" not in resultado["pesos"]
    assert resultado["qi"] == pytest.approx((0.18 + 0.12 + 0.15 + 0.10 + 0.10) / 0.70, abs=1e-4)


def test_debajo_del_umbral_no_cumple_y_valores_invalidos_fallan():
    """QI < 0,75 no cumple; un componente fuera de [0, 1] o ninguno es un error."""
    assert qi.calcular_indice({"Cb": 0.5, "Cf": 0.5, "E": 0.5, "K": 0.5, "D": 0.5, "U": 0.5})[
        "cumple"] is False
    with pytest.raises(ValueError):
        qi.calcular_indice({"Cb": 1.2})
    with pytest.raises(ValueError):
        qi.calcular_indice({"U": None})


def test_puntaje_sus():
    """Fórmula de Brooke: todo neutro da 50; la mejor respuesta posible da 100."""
    assert qi.puntaje_sus([3] * 10) == 50
    assert qi.puntaje_sus([5, 1] * 5) == 100
    assert qi.puntaje_sus([1, 5] * 5) == 0
    with pytest.raises(ValueError):
        qi.puntaje_sus([3] * 9)


def test_lectores_de_cobertura(tmp_path):
    """Lee los JSON de coverage.py y de Vitest."""
    back = tmp_path / "coverage.json"
    back.write_text(json.dumps({"totals": {"percent_covered": 97.5}}))
    front = tmp_path / "coverage-summary.json"
    front.write_text(json.dumps({"total": {"lines": {"pct": 88}}}))
    assert qi.cobertura_backend(back) == pytest.approx(0.975)
    assert qi.cobertura_frontend(front) == pytest.approx(0.88)


def test_lectores_de_pylint_y_flake8(tmp_path):
    """Puntuación, funciones complejas y líneas duplicadas."""
    assert qi.puntuacion_pylint("Your code has been rated at 9.50/10") == pytest.approx(0.95)
    with pytest.raises(ValueError):
        qi.puntuacion_pylint("sin puntuación")
    salida = (
        "app/a.py:3:1: C901 'f' is too complex (12)\n"
        "app/b.py:9:1: C901 'g' is too complex (11)"
    )
    assert qi.complejidad_acotada(salida, 20) == pytest.approx(0.9)
    assert qi.complejidad_acotada("", 0) == 1.0
    duplicado = "R0801: Similar lines in 2 files\n==app.a:[10:30]\n==app.b:[5:25]\n"
    assert qi.sin_duplicar(duplicado, 200) == pytest.approx(0.9)
    assert qi.sin_duplicar("", 0) == 1.0
    codigo = "def f():\n    return 1\n\n\nclass C:\n    def g(self):\n        pass\n"
    (tmp_path / "m.py").write_text(codigo)
    assert qi.contar_funciones(tmp_path) == 2
    assert qi.contar_lineas(tmp_path) == 5


def test_informe_y_main(tmp_path, monkeypatch, capsys):
    """La línea de comandos imprime la tabla y sale con 0 si cumple."""
    back = tmp_path / "coverage.json"
    back.write_text(json.dumps({"totals": {"percent_covered": 95}}))
    monkeypatch.setattr(qi, "_ejecutar", lambda comando: "rated at 10.00/10")
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "m.py").write_text("def f():\n    return 1\n")
    codigo = qi.main(["--cobertura-backend", str(back), "--sus", "80",
                      "--directorio", str(tmp_path / "app")])
    salida = capsys.readouterr().out
    assert codigo == 0
    assert "Usabilidad (SUS)" in salida and "Cobertura del frontend" in salida
    assert "provisorio" in salida
