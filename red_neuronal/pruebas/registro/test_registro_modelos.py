"""Pruebas del registro de modelos (tarea T20).

El registro de Hugging Face se prueba con un cliente simulado que guarda
los archivos en una carpeta: las pruebas no acceden a la red.
"""

import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from clasificador.registro.registro_modelos import (
    ErrorRegistro,
    RegistroHuggingFace,
    RegistroLocal,
    sellar_paquete,
)


@pytest.fixture
def paquete(tmp_path):
    """Paquete mínimo con modelo, ficha y métricas."""
    directorio = tmp_path / "paquete"
    directorio.mkdir()
    (directorio / "modelo.onnx").write_bytes(b"modelo de prueba")
    (directorio / "ficha.md").write_text("# Ficha", encoding="utf-8")
    (directorio / "metricas.json").write_text("{}", encoding="utf-8")
    return directorio


class _ClienteSimulado:
    """Imita los métodos de HfApi que usa el registro."""

    def __init__(self, raiz: Path):
        self.raiz = raiz
        self.etiquetas: dict[str, Path] = {}
        self.confirmaciones = 0

    def list_repo_refs(self, repositorio, repo_type):  # pylint: disable=unused-argument
        """Devuelve las etiquetas como objetos con atributo name."""
        return SimpleNamespace(tags=[SimpleNamespace(name=n) for n in self.etiquetas])

    def upload_folder(self, repo_id, folder_path, repo_type, commit_message):
        # pylint: disable=unused-argument
        """Copia la carpeta como una confirmación nueva."""
        self.confirmaciones += 1
        oid = f"confirmacion{self.confirmaciones}"
        shutil.copytree(folder_path, self.raiz / oid)
        return SimpleNamespace(oid=oid)

    def create_tag(self, repositorio, tag, revision, repo_type):  # pylint: disable=unused-argument
        """Asocia la etiqueta a la confirmación."""
        self.etiquetas[tag] = self.raiz / revision

    def hf_hub_download(self, repo_id, filename, revision, repo_type, local_dir):
        # pylint: disable=unused-argument
        """Copia el archivo de la etiqueta pedida."""
        Path(local_dir).mkdir(parents=True, exist_ok=True)
        return shutil.copy2(self.etiquetas[revision] / filename, Path(local_dir) / filename)


@pytest.fixture(params=["local", "hugging_face"])
def registro(request, tmp_path):
    """Las mismas pruebas corren sobre ambas implementaciones."""
    if request.param == "local":
        return RegistroLocal(tmp_path / "registro")
    (tmp_path / "hub").mkdir()
    return RegistroHuggingFace("alguien/clasificador", cliente=_ClienteSimulado(tmp_path / "hub"))


def test_publicar_y_obtener_una_version(registro, paquete, tmp_path):
    """Lo publicado se descarga con la huella verificada."""
    registro.publicar("1.0.0", paquete)
    assert registro.versiones() == ["1.0.0"]
    modelo = registro.obtener("1.0.0", tmp_path / "descarga")
    assert modelo.read_bytes() == b"modelo de prueba"


def test_las_versiones_son_inmutables(registro, paquete):
    """No se puede volver a publicar la misma versión."""
    registro.publicar("1.0.0", paquete)
    with pytest.raises(ErrorRegistro, match="inmutables"):
        registro.publicar("1.0.0", paquete)


def test_las_versiones_se_ordenan_numericamente(registro, paquete):
    """1.10.0 va después de 1.2.0."""
    for version in ("1.10.0", "1.2.0", "0.1.0"):
        registro.publicar(version, paquete)
    assert registro.versiones() == ["0.1.0", "1.2.0", "1.10.0"]


@pytest.mark.parametrize("version", ["1.0", "v1.0.0", "uno"])
def test_una_version_mal_formada_se_rechaza(registro, paquete, version):
    """Solo se acepta MAJOR.MINOR.PATCH."""
    with pytest.raises(ErrorRegistro, match="MAJOR.MINOR.PATCH"):
        registro.publicar(version, paquete)


def test_obtener_una_version_inexistente_falla(registro, tmp_path):
    """Se informa la versión que no existe."""
    with pytest.raises(ErrorRegistro, match="no existe"):
        registro.obtener("9.9.9", tmp_path)


def test_un_paquete_sin_ficha_no_se_publica(registro, paquete):
    """El modelo y la ficha son obligatorios."""
    (paquete / "ficha.md").unlink()
    with pytest.raises(ErrorRegistro, match="ficha.md"):
        registro.publicar("1.0.0", paquete)


def test_un_modelo_alterado_se_detecta(paquete, tmp_path):
    """Si alguien modifica el modelo publicado, obtener falla."""
    registro = RegistroLocal(tmp_path / "registro")
    registro.publicar("1.0.0", paquete)
    (tmp_path / "registro" / "v1.0.0" / "modelo.onnx").write_bytes(b"alterado")
    with pytest.raises(ErrorRegistro, match="huella"):
        registro.obtener("1.0.0", tmp_path / "descarga")


def test_sellar_registra_la_huella_de_cada_archivo(paquete):
    """huellas.json lista todos los archivos del paquete."""
    assert set(sellar_paquete(paquete)) == {"modelo.onnx", "ficha.md", "metricas.json"}
    assert (paquete / "huellas.json").is_file()


def test_sin_cliente_se_usa_hfapi_con_el_token_del_entorno(monkeypatch):
    """El token sale de la variable HF_TOKEN; crear el cliente no accede a la red."""
    monkeypatch.setenv("HF_TOKEN", "token-de-prueba")
    registro = RegistroHuggingFace("alguien/clasificador")
    assert type(registro.cliente).__name__ == "HfApi"
    assert registro.cliente.token == "token-de-prueba"
