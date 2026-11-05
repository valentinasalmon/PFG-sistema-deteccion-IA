"""Pruebas del verificador del arnés (``verificar_arnes.py``).

Arman un repositorio mínimo en una carpeta temporal y comprueban que cada
control detecte lo que declara: enlaces rotos, comandos, ganchos, skills,
funcionalidades e índices desactualizados, números viejos y propuestas
pendientes. Se ejecutan con
``python3 -m unittest discover -s .claude/hooks -p "pruebas_*.py"``.

Realiza: funcionalidad 038 (CA6).
"""
import datetime
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

_ESPEC = importlib.util.spec_from_file_location(
    "verificar_arnes", Path(__file__).with_name("verificar_arnes.py")
)
verificar_arnes = importlib.util.module_from_spec(_ESPEC)
_ESPEC.loader.exec_module(verificar_arnes)

MAPA = """# Arnés

## Números del proceso (al 2026-01-01)

| Indicador | Valor |
|---|---|
| Commits (sin contar integraciones) | 0 |
"""


def _escribir(raiz, relativa, texto):
    """Crea un archivo con su carpeta."""
    ruta = raiz / relativa
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


def _repositorio_valido(raiz):
    """Un repositorio mínimo en el que todos los controles pasan."""
    _escribir(raiz, "CLAUDE.md", "| `/especificar` | Crea |\n[mapa](docs/arnes/README.md)\n")
    _escribir(raiz, ".claude/commands/especificar.md", "pasos\n")
    _escribir(raiz, ".claude/hooks/gancho.py", "")
    _escribir(raiz, ".claude/settings.json", json.dumps({"hooks": {"PreToolUse": [
        {"hooks": [{"command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/gancho.py\""}]}
    ]}}))
    (raiz / ".claude" / "skills" / "diseno").mkdir(parents=True)
    _escribir(raiz, "skills-lock.json", json.dumps({"skills": {"diseno": {}}}))
    _escribir(raiz, "docs/funcionalidades/README.md", "| 001 | Primera | Completado |\n")
    _escribir(raiz, "docs/funcionalidades/001-primera/especificacion.md", "# 001\n")
    _escribir(raiz, "docs/bitacora/README.md", "| 2026-01-01 | [Inicio](2026-01-01-inicio.md) |\n")
    _escribir(raiz, "docs/bitacora/2026-01-01-inicio.md", "# 2026-01-01 — Inicio\n")
    _escribir(raiz, "docs/arquitectura/decisiones/README.md", "| [0001](0001-algo.md) | Algo |\n")
    _escribir(raiz, "docs/arquitectura/decisiones/0001-algo.md", "# ADR-0001\n")
    _escribir(raiz, "docs/arnes/README.md", MAPA)
    _escribir(raiz, "docs/arnes/registro-de-cambios.md",
              "| 2026-01-01 | Inicio | Guías | Motivo |\n")


class PruebasVerificador(unittest.TestCase):
    """Cada control detecta su problema y no da falsos positivos."""

    def setUp(self):
        """Repositorio temporal válido y verificador apuntando a él."""
        self._temporal = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.raiz = Path(self._temporal.name)
        _repositorio_valido(self.raiz)
        self._originales = (
            verificar_arnes.RAIZ, verificar_arnes.MAPA_ARNES, verificar_arnes.REGISTRO
        )
        verificar_arnes.RAIZ = self.raiz
        verificar_arnes.MAPA_ARNES = self.raiz / "docs" / "arnes" / "README.md"
        verificar_arnes.REGISTRO = self.raiz / "docs" / "arnes" / "registro-de-cambios.md"

    def tearDown(self):
        """Restaura las rutas reales y borra la carpeta temporal."""
        (verificar_arnes.RAIZ, verificar_arnes.MAPA_ARNES,
         verificar_arnes.REGISTRO) = self._originales
        self._temporal.cleanup()

    def _controlar(self, control):
        """Informe de un solo control."""
        informe = verificar_arnes.Informe()
        control(informe)
        return informe

    def test_repositorio_al_dia_no_tiene_errores(self):
        """Sin git, los controles de historial se omiten y el resto pasa."""
        informe = verificar_arnes.verificar()
        self.assertEqual(informe.errores, [])
        self.assertEqual(informe.avisos, [])

    def test_detecta_enlace_roto_y_ignora_urls_y_codigo(self):
        """Un enlace a un archivo inexistente es error; URLs y código no."""
        _escribir(self.raiz, "docs/guia.md",
                  "[ok](arnes/README.md) [web](https://x.org) [falta](no-existe.md)\n"
                  "```\n[en codigo](tampoco.md)\n```\n")
        errores = self._controlar(verificar_arnes.revisar_enlaces).errores
        self.assertEqual(len(errores), 1)
        self.assertIn("no-existe.md", errores[0])

    def test_detecta_comando_sin_archivo_y_archivo_sin_declarar(self):
        """La tabla de CLAUDE.md y la carpeta de comandos deben coincidir."""
        _escribir(self.raiz, "CLAUDE.md", "| `/planificar` | Plan |\n")
        errores = self._controlar(verificar_arnes.revisar_comandos).errores
        self.assertEqual(len(errores), 2)

    def test_detecta_gancho_configurado_inexistente(self):
        """Un script de settings.json que no existe es error."""
        (self.raiz / ".claude" / "hooks" / "gancho.py").unlink()
        self.assertEqual(len(self._controlar(verificar_arnes.revisar_ganchos).errores), 1)

    def test_detecta_skill_sin_origen_registrado(self):
        """Una skill instalada sin registro en skills-lock.json es error."""
        (self.raiz / ".claude" / "skills" / "otra").mkdir()
        errores = self._controlar(verificar_arnes.revisar_skills).errores
        self.assertEqual(len(errores), 1)
        self.assertIn("otra", errores[0])

    def test_detecta_funcionalidad_fuera_de_la_tabla_o_sin_especificacion(self):
        """Carpeta sin fila en la tabla y sin especificación: dos errores."""
        (self.raiz / "docs" / "funcionalidades" / "002-segunda").mkdir()
        self.assertEqual(len(self._controlar(verificar_arnes.revisar_funcionalidades).errores), 2)

    def test_detecta_bitacora_y_adr_fuera_del_indice(self):
        """Entradas y ADR nuevos que no se agregaron al índice son error."""
        _escribir(self.raiz, "docs/bitacora/2026-01-02-otra.md", "# x\n")
        _escribir(self.raiz, "docs/arquitectura/decisiones/0002-otra.md", "# x\n")
        self.assertEqual(len(self._controlar(verificar_arnes.revisar_indices).errores), 2)

    def test_avisa_propuesta_pendiente(self):
        """Una propuesta marcada como pendiente genera un aviso."""
        _escribir(self.raiz, "docs/arnes/propuesta-algo.md",
                  "# Propuesta (pendiente de aprobación)\n")
        self.assertEqual(len(self._controlar(verificar_arnes.revisar_propuestas).avisos), 1)

    def test_numeros_desactualizados_avisan_y_se_actualizan(self):
        """Con números distintos avisa; con --actualizar reescribe la tabla y la fecha."""
        reales = {"Commits (sin contar integraciones)": "5"}
        original = verificar_arnes.numeros_reales
        verificar_arnes.numeros_reales = lambda: reales
        try:
            informe = verificar_arnes.Informe()
            verificar_arnes.revisar_numeros(informe)
            self.assertEqual(len(informe.avisos), 1)
            verificar_arnes.revisar_numeros(informe, actualizar=True, hoy=datetime.date(2026, 2, 3))
            texto = verificar_arnes.MAPA_ARNES.read_text(encoding="utf-8")
            self.assertIn("(al 2026-02-03)", texto)
            self.assertIn("| Commits (sin contar integraciones) | 5 |", texto)
            informe_final = verificar_arnes.Informe()
            verificar_arnes.revisar_numeros(informe_final)
            self.assertEqual(informe_final.avisos, [])
        finally:
            verificar_arnes.numeros_reales = original

    def test_avisa_cambio_del_arnes_sin_registrar(self):
        """Un commit que toca CLAUDE.md después del último registro genera un aviso."""
        comandos = [
            ["git", "init", "-q"],
            ["git", "-c", "user.name=a", "-c", "user.email=a@b", "add", "-A"],
            ["git", "-c", "user.name=a", "-c", "user.email=a@b", "commit", "-qm", "inicio",
             "--date", "2026-01-01T10:00:00"],
        ]
        for comando in comandos:
            subprocess.run(
                comando, cwd=self.raiz, check=True,
                env={"GIT_COMMITTER_DATE": "2026-01-01T10:00:00", "PATH": "/usr/bin:/bin"},
            )
        _escribir(self.raiz, "CLAUDE.md", "| `/especificar` | Crea y más |\n")
        subprocess.run(
            ["git", "-c", "user.name=a", "-c", "user.email=a@b", "commit", "-qam", "regla nueva",
             "--date", "2026-01-05T10:00:00"],
            cwd=self.raiz, check=True,
            env={"GIT_COMMITTER_DATE": "2026-01-05T10:00:00", "PATH": "/usr/bin:/bin"},
        )
        avisos = self._controlar(verificar_arnes.revisar_registro).avisos
        self.assertEqual(len(avisos), 1)
        self.assertIn("regla nueva", avisos[0])

    def test_avisa_ramas_integradas_sin_borrar_y_respeta_las_recientes(self):
        """Una rama remota integrada y vieja genera aviso; main, la base y las recientes no."""
        entorno = {"GIT_COMMITTER_DATE": "2026-01-01T10:00:00", "PATH": "/usr/bin:/bin"}
        for comando in (
            ["git", "init", "-q"],
            ["git", "-c", "user.name=a", "-c", "user.email=a@b", "add", "-A"],
            ["git", "-c", "user.name=a", "-c", "user.email=a@b", "commit", "-qm", "inicio",
             "--date", "2026-01-01T10:00:00"],
        ):
            subprocess.run(comando, cwd=self.raiz, check=True, env=entorno)
        for rama in ("desarrollo", "main", "funcionalidad/001-vieja"):
            subprocess.run(["git", "update-ref", f"refs/remotes/origin/{rama}", "HEAD"],
                           cwd=self.raiz, check=True)
        informe = verificar_arnes.Informe()
        enero = datetime.datetime(2026, 1, 10).timestamp()
        verificar_arnes.revisar_ramas(informe, ahora=enero)
        self.assertEqual(len(informe.avisos), 1)
        self.assertIn("1 ramas remotas", informe.avisos[0])
        self.assertIn("funcionalidad/001-vieja", informe.avisos[0])
        reciente = verificar_arnes.Informe()
        verificar_arnes.revisar_ramas(reciente, ahora=datetime.datetime(2026, 1, 1, 12).timestamp())
        self.assertEqual(reciente.avisos, [])

    def test_ramas_sin_base_no_revisa(self):
        """Sin la rama base en el clon (integración continua), el control no opina."""
        informe = verificar_arnes.Informe()
        verificar_arnes.revisar_ramas(informe)
        self.assertEqual(informe.avisos, [])

    def test_modo_sesion_nunca_bloquea(self):
        """El resumen para el inicio de sesión sale con 0 aunque haya errores."""
        (self.raiz / ".claude" / "hooks" / "gancho.py").unlink()
        self.assertEqual(verificar_arnes.main(["--sesion"]), 0)
        self.assertEqual(verificar_arnes.main([]), 1)


if __name__ == "__main__":
    unittest.main()
