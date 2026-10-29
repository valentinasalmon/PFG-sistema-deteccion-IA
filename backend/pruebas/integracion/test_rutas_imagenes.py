"""Pruebas de las imágenes de los casos a través de la API.

Criterios de aceptación de la funcionalidad 006: CA1 a CA11. Las imágenes
de prueba se generan en memoria: nunca se usan imágenes de casos reales.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
# Las pruebas parametrizadas reciben muchos accesorios.
# pylint: disable=too-many-arguments,too-many-positional-arguments
import hashlib
import io
import re
from datetime import timedelta
from pathlib import Path

import pytest
from PIL import Image

from app.extensiones import db
from app.modelos.imagen import Imagen
from app.servicios import servicio_imagenes
from pruebas.conftest import (
    CONTRASENIA_VALIDA,
    crear_estudio,
    crear_estudio_pagado,
    entradas_auditoria,
)

CASO = {
    "espacio": "personal", "tipo": "automovilistico", "fecha_hecho": "2026-09-01",
    "lugar": "Av. Corrientes 1234",
}


def imagen_de_prueba(formato="PNG", color=(200, 30, 30), tamanio=(64, 48), modo="RGB"):
    """Imagen generada en memoria; el color cambia la huella."""
    salida = io.BytesIO()
    Image.new(modo, tamanio, color).save(salida, format=formato)
    return salida.getvalue()


def _cargar(cliente, id_caso, contenido, nombre="foto.png"):
    return cliente.post(
        f"/api/casos/{id_caso}/imagenes",
        data={"archivo": (io.BytesIO(contenido), nombre)},
        content_type="multipart/form-data",
    )


def _crear_caso(cliente, **cambios):
    return cliente.post("/api/casos", json={**CASO, **cambios}).get_json()["caso"]


def _directorio(aplicacion):
    return Path(aplicacion.config["DIRECTORIO_ALMACENAMIENTO"])


def _archivos(aplicacion):
    return sorted(p for p in _directorio(aplicacion).rglob("*") if p.is_file())


@pytest.fixture
def ana(cuenta):
    """Responsable de los casos."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def beto(cuenta):
    """Miembro del estudio de Ana."""
    return cuenta("beto@ejemplo.com", "Beto")


@pytest.fixture
def caso(ana):
    """Caso personal de Ana en Borrador."""
    return _crear_caso(ana)


@pytest.fixture
def estudio(ana, beto):
    """Estudio de Ana con Beto como miembro; devuelve su id."""
    return crear_estudio(ana, beto, "beto@ejemplo.com")


def _compartir(ana, beto, id_caso, nivel):
    ana.post(f"/api/casos/{id_caso}/accesos", json={"nivel": nivel, "id_usuario": beto.id_usuario})


# --- Cargar (CA1 a CA6) ---

def test_cargar_guarda_el_original_sin_modificar_con_su_huella(aplicacion, ana, caso):
    """CA1 (RN23) y CA11: claves aleatorias sin datos personales."""
    contenido = imagen_de_prueba()
    respuesta = _cargar(ana, caso["id"], contenido, "Choque Juan Pérez.png")

    assert respuesta.status_code == 201, respuesta.get_json()
    imagen = respuesta.get_json()["imagen"]
    huella = hashlib.sha256(contenido).hexdigest()
    assert imagen["huella"] == huella
    assert (imagen["nombre"], imagen["formato"], imagen["tamanio"]) == (
        "Choque Juan Pérez.png", "PNG", len(contenido),
    )
    assert (imagen["ancho"], imagen["alto"]) == (64, 48)
    assert imagen["cargada_por"] == "Ana López"
    assert imagen["miniatura"].startswith("/api/archivos/")
    with aplicacion.app_context():
        guardada = db.session.get(Imagen, imagen["id"])
        clave, clave_miniatura = guardada.clave, guardada.clave_miniatura
    assert re.fullmatch(r"imagenes/[0-9a-f]{32}", clave)
    assert re.fullmatch(r"miniaturas/[0-9a-f]{32}\.jpg", clave_miniatura)
    assert (_directorio(aplicacion) / clave).read_bytes() == contenido
    assert (_directorio(aplicacion) / clave_miniatura).is_file()
    entrada = entradas_auditoria(aplicacion, "imagen.carga")[-1]
    assert (entrada["resultado"], entrada["detalle"]["sha256"]) == ("exitoso", huella)
    assert entrada["tipo_recurso"] == "caso"


def test_cargar_jpeg_con_transparencia_y_paleta(ana, caso):
    """CA1: JPEG y PNG con distintos modos de color."""
    for contenido, nombre in (
        (imagen_de_prueba("JPEG"), "foto.jpg"),
        (imagen_de_prueba("PNG", (0, 0, 0, 0), modo="RGBA"), "transparente.png"),
        (imagen_de_prueba("PNG", 3, modo="P"), "paleta.png"),
    ):
        assert _cargar(ana, caso["id"], contenido, nombre).status_code == 201


@pytest.mark.parametrize("contenido, motivo, texto", [
    (b"esto no es una imagen", "formato", "formato real"),
    (imagen_de_prueba("GIF"), "formato", "formato real"),
    (imagen_de_prueba()[:60], "danada", "dañada"),
    (b"", "vacio", "vacío"),
])
def test_formato_real_invalido_se_rechaza(aplicacion, ana, caso, contenido, motivo, texto):
    """CA2 (RN22): el formato se decide por el contenido, no por la extensión."""
    respuesta = _cargar(ana, caso["id"], contenido, "foto.jpg")
    assert respuesta.status_code == 400
    assert texto in respuesta.get_json()["errores"]["archivo"]
    entrada = entradas_auditoria(aplicacion, "imagen.carga")[-1]
    assert (entrada["resultado"], entrada["detalle"]["motivo"]) == ("rechazado", motivo)
    assert not _archivos(aplicacion)


def test_sin_archivo_se_rechaza(ana, caso):
    """CA2: la solicitud tiene que traer el archivo."""
    respuesta = ana.post(f"/api/casos/{caso['id']}/imagenes", data={})
    assert respuesta.status_code == 400


def test_archivo_mayor_al_maximo_se_rechaza(aplicacion, ana, caso):
    """CA3: tamaño máximo por imagen."""
    aplicacion.config["TAMANIO_MAXIMO_IMAGEN"] = 50
    respuesta = _cargar(ana, caso["id"], imagen_de_prueba())
    assert respuesta.status_code == 400
    assert "tamaño máximo" in respuesta.get_json()["errores"]["archivo"]


def test_solicitud_mayor_al_limite_de_flask_responde_413(aplicacion, ana, caso):
    """CA3: Flask corta la solicitud antes de leerla y responde con el límite."""
    aplicacion.config["MAX_CONTENT_LENGTH"] = 100
    respuesta = _cargar(ana, caso["id"], imagen_de_prueba(tamanio=(400, 400)))
    assert respuesta.status_code == 413
    assert respuesta.get_json()["codigo"] == "archivo_demasiado_grande"
    assert "20 MB" in respuesta.get_json()["mensaje"]


def test_limite_de_imagenes_del_plan(aplicacion, ana, caso):
    """CA3 (RN15): el plan Personal limita las imágenes por caso."""
    aplicacion.config["PLAN_PERSONAL"] = {"nombre": "Personal", "imagenes_por_caso": 1}
    assert _cargar(ana, caso["id"], imagen_de_prueba()).status_code == 201
    respuesta = _cargar(ana, caso["id"], imagen_de_prueba(color=(1, 2, 3)))
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "limite_imagenes")
    assert "1 imágenes" in respuesta.get_json()["mensaje"]
    assert ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["limite"] == 1


def test_limite_de_una_organizacion_segun_su_plan(ana, estudio):
    """CA3: el límite de un caso de organización es el de su plan (Básico: 50)."""
    caso = _crear_caso(ana, espacio=str(estudio))
    assert ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["limite"] == 50


def test_duplicado_no_se_vuelve_a_guardar(aplicacion, ana, caso):
    """CA4."""
    contenido = imagen_de_prueba()
    _cargar(ana, caso["id"], contenido, "primera.png")
    archivos = _archivos(aplicacion)

    respuesta = _cargar(ana, caso["id"], contenido, "otra.png")

    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "imagen_duplicada")
    assert "primera.png" in respuesta.get_json()["mensaje"]
    assert _archivos(aplicacion) == archivos
    # En otro caso, la misma imagen sí se puede cargar.
    assert _cargar(ana, _crear_caso(ana)["id"], contenido).status_code == 201


def test_cada_archivo_se_valida_por_separado(ana, caso):
    """CA5: un archivo inválido no impide cargar los demás."""
    resultados = [
        _cargar(ana, caso["id"], contenido).status_code
        for contenido in (imagen_de_prueba(), b"texto", imagen_de_prueba(color=(9, 9, 9)))
    ]
    assert resultados == [201, 400, 201]
    assert len(ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"]) == 2


def test_lector_no_carga_ni_elimina(aplicacion, ana, beto, estudio):
    """CA6 (RN20): el Lector solo consulta."""
    caso = _crear_caso(ana, espacio=str(estudio))
    id_imagen = _cargar(ana, caso["id"], imagen_de_prueba()).get_json()["imagen"]["id"]
    _compartir(ana, beto, caso["id"], "lectura")

    assert _cargar(beto, caso["id"], imagen_de_prueba(color=(5, 5, 5))).status_code == 403
    assert beto.delete(f"/api/casos/{caso['id']}/imagenes/{id_imagen}").status_code == 403
    assert beto.get(f"/api/casos/{caso['id']}/imagenes").get_json()["puede_modificar"] is False


def test_colaborador_carga_y_elimina(ana, beto, estudio):
    """CA1 y CA9: el Colaborador también carga y elimina."""
    caso = _crear_caso(ana, espacio=str(estudio))
    _compartir(ana, beto, caso["id"], "colaboracion")
    respuesta = _cargar(beto, caso["id"], imagen_de_prueba())
    assert respuesta.status_code == 201
    assert respuesta.get_json()["imagen"]["cargada_por"] == "Beto López"
    id_imagen = respuesta.get_json()["imagen"]["id"]
    assert beto.delete(f"/api/casos/{caso['id']}/imagenes/{id_imagen}").status_code == 200


def test_caso_cerrado_no_admite_cambios(aplicacion, ana, caso):
    """CA6 (RN19)."""
    id_imagen = _cargar(ana, caso["id"], imagen_de_prueba()).get_json()["imagen"]["id"]
    ana.post(f"/api/casos/{caso['id']}/estado", json={"operacion": "cerrar"})

    respuesta = _cargar(ana, caso["id"], imagen_de_prueba(color=(7, 7, 7)))
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "caso_solo_lectura")
    assert ana.delete(f"/api/casos/{caso['id']}/imagenes/{id_imagen}").status_code == 409
    listado = ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()
    assert (listado["puede_modificar"], len(listado["imagenes"])) == (False, 1)


def test_sin_permiso_el_caso_no_existe(ana, beto, caso):
    """CA7 (RNF05)."""
    id_imagen = _cargar(ana, caso["id"], imagen_de_prueba()).get_json()["imagen"]["id"]
    assert beto.get(f"/api/casos/{caso['id']}/imagenes").status_code == 404
    assert _cargar(beto, caso["id"], imagen_de_prueba()).status_code == 404
    assert beto.get(f"/api/casos/{caso['id']}/imagenes/{id_imagen}/descarga").status_code == 404


def test_imagen_de_otro_caso_no_se_encuentra(ana, caso):
    """CA7: el id de la imagen tiene que ser del caso indicado."""
    id_imagen = _cargar(ana, caso["id"], imagen_de_prueba()).get_json()["imagen"]["id"]
    otro = _crear_caso(ana)
    assert ana.delete(f"/api/casos/{otro['id']}/imagenes/{id_imagen}").status_code == 404


# --- Consultar y enlaces (CA7, CA8) ---

def test_listado_con_vista_previa_y_datos_tecnicos(ana, beto, estudio):
    """CA7: el Lector ve la vista previa por un enlace firmado."""
    caso = _crear_caso(ana, espacio=str(estudio))
    _cargar(ana, caso["id"], imagen_de_prueba(tamanio=(1200, 900)))
    _compartir(ana, beto, caso["id"], "lectura")

    listado = beto.get(f"/api/casos/{caso['id']}/imagenes").get_json()

    assert listado["tamanio_maximo"] == 20 * 1024 * 1024
    imagen = listado["imagenes"][0]
    assert set(imagen) >= {"nombre", "formato", "tamanio", "ancho", "alto", "huella", "cargada_en"}
    miniatura = beto.get(imagen["miniatura"])
    assert miniatura.status_code == 200
    assert miniatura.mimetype == "image/jpeg"
    assert "Content-Disposition" not in miniatura.headers
    assert max(Image.open(io.BytesIO(miniatura.data)).size) == 480


def test_descargar_el_original_con_enlace_firmado(aplicacion, ana, caso):
    """CA8: el original llega idéntico, como descarga, y queda en la auditoría."""
    contenido = imagen_de_prueba()
    id_imagen = _cargar(ana, caso["id"], contenido, "foto ñ.png").get_json()["imagen"]["id"]

    url = ana.get(f"/api/casos/{caso['id']}/imagenes/{id_imagen}/descarga").get_json()["url"]
    archivo = aplicacion.test_client().get(url)

    assert archivo.status_code == 200
    assert archivo.data == contenido
    assert archivo.mimetype == "image/png"
    assert "attachment" in archivo.headers["Content-Disposition"]
    assert "foto%20%C3%B1.png" in archivo.headers["Content-Disposition"]
    entrada = entradas_auditoria(aplicacion, "imagen.descarga")[-1]
    assert entrada["detalle"]["sha256"] == hashlib.sha256(contenido).hexdigest()


def test_enlace_alterado_o_vencido_no_entrega_nada(aplicacion, ana, caso):
    """CA8: los enlaces vencen y no se pueden alterar."""
    id_imagen = _cargar(ana, caso["id"], imagen_de_prueba()).get_json()["imagen"]["id"]
    descarga = f"/api/casos/{caso['id']}/imagenes/{id_imagen}/descarga"
    url = ana.get(descarga).get_json()["url"]
    assert ana.get(url + "x").status_code == 404

    aplicacion.config["VIGENCIA_ENLACE_ARCHIVO"] = timedelta(seconds=-1)
    vencido = ana.get(descarga).get_json()["url"]
    assert ana.get(vencido).status_code == 404


# --- Eliminar (CA9, CA10) ---

def test_eliminar_borra_los_archivos_y_audita_la_huella(aplicacion, ana, caso):
    """CA9 (RF36 CA1)."""
    contenido = imagen_de_prueba()
    id_imagen = _cargar(ana, caso["id"], contenido).get_json()["imagen"]["id"]

    respuesta = ana.delete(f"/api/casos/{caso['id']}/imagenes/{id_imagen}")

    assert respuesta.status_code == 200
    assert not _archivos(aplicacion)
    assert ana.get(f"/api/casos/{caso['id']}/imagenes").get_json()["imagenes"] == []
    entrada = entradas_auditoria(aplicacion, "imagen.eliminacion")[-1]
    assert entrada["detalle"]["sha256"] == hashlib.sha256(contenido).hexdigest()


def test_eliminar_el_caso_borra_sus_imagenes(aplicacion, ana, caso):
    """CA10 (RN21): la auditoría conserva las huellas."""
    huellas = sorted(
        _cargar(ana, caso["id"], imagen_de_prueba(color=(i, i, i))).get_json()["imagen"]["huella"]
        for i in (1, 2)
    )
    otro = _crear_caso(ana)
    _cargar(ana, otro["id"], imagen_de_prueba(color=(3, 3, 3)))

    ana.delete(f"/api/casos/{caso['id']}", json={"confirmacion": caso["numero"]})

    assert len(_archivos(aplicacion)) == 2  # quedan el original y la miniatura del otro caso
    entrada = entradas_auditoria(aplicacion, "caso.eliminacion")[-1]
    assert sorted(entrada["detalle"]["sha256_eliminados"]) == huellas


def test_eliminar_la_organizacion_borra_las_imagenes_de_sus_casos(aplicacion, ana, estudio):
    """CA10: la organización se elimina con sus casos y sus archivos."""
    caso = _crear_caso(ana, espacio=str(estudio))
    huella = _cargar(ana, caso["id"], imagen_de_prueba()).get_json()["imagen"]["huella"]

    respuesta = ana.delete(f"/api/organizaciones/{estudio}", json={"confirmacion": "Estudio Pérez"})

    assert respuesta.status_code == 200
    assert not _archivos(aplicacion)
    entrada = entradas_auditoria(aplicacion, "organizacion.eliminacion")[-1]
    assert entrada["detalle"]["sha256_eliminados"] == [huella]


def test_eliminar_la_cuenta_borra_las_imagenes_de_sus_organizaciones(aplicacion, ana):
    """CA10: la baja elimina la organización de un solo miembro con sus archivos."""
    id_org = crear_estudio_pagado(ana, "Estudio Solo")
    caso = _crear_caso(ana, espacio=str(id_org))
    _cargar(ana, caso["id"], imagen_de_prueba())

    respuesta = ana.delete("/api/perfil", json={"contrasenia": CONTRASENIA_VALIDA})

    assert respuesta.status_code == 200
    assert not _archivos(aplicacion)


# --- Fallas del almacenamiento ---

def test_si_falla_el_guardado_no_quedan_archivos_sueltos(aplicacion, ana, caso, monkeypatch):
    """Si falla el segundo archivo, se borra el primero y la imagen no se registra."""
    almacenamiento = aplicacion.extensions["almacenamiento"]
    guardar = almacenamiento.guardar

    def guardar_solo_el_original(clave, contenido, tipo_mime):
        if clave.startswith("miniaturas/"):
            raise OSError("disco lleno")
        guardar(clave, contenido, tipo_mime)

    monkeypatch.setattr(almacenamiento, "guardar", guardar_solo_el_original)
    with pytest.raises(OSError):
        _cargar(ana, caso["id"], imagen_de_prueba())
    assert not _archivos(aplicacion)
    with aplicacion.app_context():
        assert Imagen.query.count() == 0


def test_si_falla_el_borrado_del_archivo_la_imagen_igual_se_elimina(
    aplicacion, ana, caso, monkeypatch, caplog
):
    """La falla queda en el log para borrar el archivo a mano; la operación no se cae."""
    id_imagen = _cargar(ana, caso["id"], imagen_de_prueba()).get_json()["imagen"]["id"]

    def fallar(clave):
        raise OSError("sin conexión")

    monkeypatch.setattr(aplicacion.extensions["almacenamiento"], "eliminar", fallar)
    # Las pruebas de migraciones configuran el log de Alembic y apagan los existentes.
    monkeypatch.setattr(servicio_imagenes.registro_log, "disabled", False)
    respuesta = ana.delete(f"/api/casos/{caso['id']}/imagenes/{id_imagen}")

    assert respuesta.status_code == 200
    assert "No se pudo borrar el archivo imagenes/" in caplog.text


def test_cargar_heic_del_iphone(aplicacion, ana, caso):
    """024 (RF53 CA3): el HEIC se guarda sin convertir y su vista previa es JPEG."""
    contenido = imagen_de_prueba("HEIF")
    respuesta = _cargar(ana, caso["id"], contenido, "IMG_0001.HEIC")

    assert respuesta.status_code == 201, respuesta.get_json()
    imagen = respuesta.get_json()["imagen"]
    assert imagen["formato"] == "HEIC"
    with aplicacion.app_context():
        guardada = db.session.get(Imagen, imagen["id"])
        clave, miniatura, tipo = guardada.clave, guardada.clave_miniatura, guardada.tipo_mime
    assert (_directorio(aplicacion) / clave).read_bytes() == contenido
    assert (_directorio(aplicacion) / miniatura).read_bytes().startswith(b"\xff\xd8\xff")
    assert tipo == "image/heic"
