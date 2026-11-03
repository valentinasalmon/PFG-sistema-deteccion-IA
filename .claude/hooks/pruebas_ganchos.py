"""Pruebas de los ganchos del arnés (funcionalidad 036, CA6).

Se ejecutan con la biblioteca estándar, sin instalar nada:

    python3 -m unittest discover -s .claude/hooks -p "pruebas_*.py"

La integración continua las corre en el trabajo del backend.
"""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import proteger_secretos  # noqa: E402  pylint: disable=wrong-import-position
import revisar_estilo  # noqa: E402  pylint: disable=wrong-import-position


def _correr(modulo, pedido):
    """Ejecuta el gancho con el pedido dado y devuelve ``(codigo, salida_de_error)``."""
    error = io.StringIO()
    with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(pedido))), \
            mock.patch.object(sys, "stderr", error):
        codigo = modulo.main()
    return codigo, error.getvalue()


class ProtegerSecretos(unittest.TestCase):
    """CA2: bloquea los secretos y deja pasar lo demás."""

    def test_bloquea_leer_o_editar_secretos(self):
        """Archivos secretos por herramientas de archivos."""
        for herramienta, ruta in [
            ("Read", "/repo/backend/.env"),
            ("Read", "/repo/backend/.env.produccion"),
            ("Edit", "/repo/infraestructura/terraform/principal/terraform.tfvars"),
            ("Write", "/repo/infraestructura/terraform/principal/backend.hcl"),
            ("Read", "/repo/terraform.tfstate"),
            ("Read", "/repo/terraform.tfstate.backup"),
            ("Read", "/home/autora/.ssh/servidor.pem"),
        ]:
            codigo, error = _correr(
                proteger_secretos, {"tool_name": herramienta, "tool_input": {"file_path": ruta}}
            )
            self.assertEqual(codigo, 2, ruta)
            self.assertIn("Bloqueado por el arnés", error)

    def test_permite_ejemplos_y_codigo(self):
        """Los archivos de ejemplo y el código no se bloquean."""
        for ruta in [
            "/repo/backend/.env.ejemplo",
            "/repo/infraestructura/terraform/principal/terraform.tfvars.ejemplo",
            "/repo/backend/app/configuracion/entornos.py",
            "/repo/.gitignore",
        ]:
            codigo, _ = _correr(
                proteger_secretos, {"tool_name": "Read", "tool_input": {"file_path": ruta}}
            )
            self.assertEqual(codigo, 0, ruta)

    def test_bloquea_comandos_que_usan_secretos(self):
        """Un secreto como argumento de un comando se bloquea."""
        for comando in [
            "cat backend/.env",
            "git add infraestructura/terraform/principal/terraform.tfvars",
            "grep HEDERA backend.hcl",
            "cp terraform.tfstate /tmp/",
            "cat > backend/.env <<'EOF'\nCLAVE=x\nEOF",
        ]:
            codigo, _ = _correr(
                proteger_secretos, {"tool_name": "Bash", "tool_input": {"command": comando}}
            )
            self.assertEqual(codigo, 2, comando)

    def test_permite_mensajes_de_commit_y_comandos_comunes(self):
        """Nombrar un secreto en un mensaje de commit no lo abre."""
        for comando in [
            'git commit -m "documentacion: no subir terraform.tfvars ni .env"',
            "ls -la && cat README.md",
            "cp backend/.env.ejemplo /tmp/copia",
            "flake8 app/",
        ]:
            codigo, _ = _correr(
                proteger_secretos, {"tool_name": "Bash", "tool_input": {"command": comando}}
            )
            self.assertEqual(codigo, 0, comando)

    def test_entrada_invalida_no_bloquea(self):
        """Si Claude Code manda algo inesperado, el gancho no traba el trabajo."""
        with mock.patch.object(sys, "stdin", io.StringIO("no es json")):
            self.assertEqual(proteger_secretos.main(), 0)


class RevisarEstilo(unittest.TestCase):
    """CA3: revisa solo lo que corresponde y no traba si falta la herramienta."""

    def test_ignora_archivos_fuera_del_codigo(self):
        """Documentación y otros archivos no se revisan."""
        raiz = revisar_estilo.RAIZ
        for ruta in [raiz / "docs" / "arnes" / "README.md", raiz / "README.md",
                     raiz / "backend" / "requirements.txt"]:
            self.assertIsNone(revisar_estilo.comando_para(ruta), ruta)

    def test_sin_herramienta_no_bloquea(self):
        """Sin flake8 ni ESLint instalados, sigue de largo."""
        ruta = revisar_estilo.BACKEND / "app" / "__init__.py"
        with mock.patch.object(revisar_estilo, "_primero_que_exista", return_value=None):
            codigo, _ = _correr(
                revisar_estilo, {"tool_name": "Edit", "tool_input": {"file_path": str(ruta)}}
            )
        self.assertEqual(codigo, 0)

    def test_devuelve_los_errores_al_agente(self):
        """Si la herramienta encuentra errores, sale con 2 y los muestra."""
        ruta = revisar_estilo.BACKEND / "app" / "__init__.py"
        fallo = mock.Mock(returncode=1, stdout="app/__init__.py:1:1: F401 'os' imported but unused",
                          stderr="")
        with mock.patch.object(revisar_estilo, "_primero_que_exista", return_value="/bin/flake8"), \
                mock.patch.object(revisar_estilo.subprocess, "run", return_value=fallo):
            codigo, error = _correr(
                revisar_estilo, {"tool_name": "Edit", "tool_input": {"file_path": str(ruta)}}
            )
        self.assertEqual(codigo, 2)
        self.assertIn("F401", error)


if __name__ == "__main__":
    unittest.main()
