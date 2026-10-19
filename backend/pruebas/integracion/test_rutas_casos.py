"""Pruebas de casos y permisos a través de la API.

Criterios de aceptación de la funcionalidad 005: CA1 a CA24.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=unused-argument,redefined-outer-name
# Las pruebas de varias personas reciben muchos accesorios.
# pylint: disable=too-many-arguments,too-many-positional-arguments
from datetime import date, timedelta

import pytest

from app.extensiones import db
from app.modelos.caso import Caso
from pruebas.conftest import CONTRASENIA_VALIDA, datos_registro, entradas_auditoria, extraer_token

CASO = {
    "espacio": "personal", "tipo": "automovilistico", "fecha_hecho": "2026-09-01",
    "lugar": "Av. Corrientes 1234, CABA", "expediente": "Expte. Nº 4.567/2026",
    "descripcion": "Choque en esquina.",
}


@pytest.fixture
def cuenta(aplicacion, correos):
    """Crea una cuenta verificada y devuelve un cliente con su sesión iniciada."""

    def _crear(correo, nombre="Ana"):
        cliente = aplicacion.test_client()
        cliente.post("/api/cuentas/registro", json=datos_registro(correo=correo, nombre=nombre))
        token = extraer_token(next(c for c in reversed(correos) if c.destinatario == correo))
        cliente.post("/api/cuentas/verificacion", json={"token": token})
        respuesta = cliente.post(
            "/api/sesion", json={"correo": correo, "contrasenia": CONTRASENIA_VALIDA}
        )
        cliente.id_usuario = respuesta.get_json()["usuario"]["id"]
        return cliente

    return _crear


@pytest.fixture
def ana(cuenta):
    """Referente del estudio."""
    return cuenta("ana@ejemplo.com")


@pytest.fixture
def beto(cuenta):
    """Miembro del estudio."""
    return cuenta("beto@ejemplo.com", "Beto")


@pytest.fixture
def carla(cuenta):
    """Miembro del estudio."""
    return cuenta("carla@ejemplo.com", "Carla")


def _sumar(referente, miembro, id_org, correo):
    id_inv = referente.post(
        f"/api/organizaciones/{id_org}/invitaciones", json={"correo": correo}
    ).get_json()["invitacion"]["id"]
    assert miembro.post(f"/api/invitaciones/{id_inv}/aceptacion").status_code == 200


@pytest.fixture
def estudio(ana, beto, carla):
    """Estudio de Ana con Beto y Carla como miembros; devuelve su id."""
    id_org = ana.post(
        "/api/organizaciones", json={"nombre": "Estudio Pérez", "tipo": "estudio_juridico"}
    ).get_json()["organizacion"]["id"]
    _sumar(ana, beto, id_org, "beto@ejemplo.com")
    _sumar(ana, carla, id_org, "carla@ejemplo.com")
    return id_org


def _crear(cliente, **cambios):
    respuesta = cliente.post("/api/casos", json={**CASO, **cambios})
    assert respuesta.status_code == 201, respuesta.get_json()
    return respuesta.get_json()["caso"]


def _ultima(aplicacion, accion):
    return entradas_auditoria(aplicacion, accion)[-1]


def _estado(cliente, id_caso, operacion):
    return cliente.post(f"/api/casos/{id_caso}/estado", json={"operacion": operacion})


# --- Crear y consultar (CA1 a CA6) ---

def test_crear_asigna_numero_borrador_y_responsable(aplicacion, ana):
    """CA1 (RN16)."""
    caso = _crear(ana)
    assert caso["numero"] == f"CASO-{date.today().year}-{caso['id']:06d}"
    assert caso["estado"] == "borrador"
    assert caso["responsable"]["id"] == ana.id_usuario
    assert caso["mi_permiso"] == "responsable"
    assert caso["espacio"] == {"tipo": "personal", "id": None, "nombre": "Personal"}
    assert caso["acciones"]["editar"] and caso["acciones"]["cerrar"]
    assert not caso["acciones"]["compartir"]
    assert _ultima(aplicacion, "caso.creacion")["id_recurso"] == str(caso["id"])
    otro = _crear(ana)
    assert otro["numero"] != caso["numero"]


def test_fecha_futura_se_rechaza(ana):
    """CA2."""
    manana = (date.today() + timedelta(days=1)).isoformat()
    respuesta = ana.post("/api/casos", json={**CASO, "fecha_hecho": manana})
    assert respuesta.status_code == 400
    assert "fecha_hecho" in respuesta.get_json()["errores"]


def test_datos_invalidos_se_marcan(ana):
    """CU18 4a: tipo, fecha y espacio inválidos."""
    respuesta = ana.post(
        "/api/casos",
        json={**CASO, "tipo": "otro", "fecha_hecho": "ayer", "espacio": "x", "lugar": ""}
    )
    assert set(respuesta.get_json()["errores"]) == {"tipo", "fecha_hecho", "espacio", "lugar"}


def test_espacio_de_otra_organizacion_se_rechaza(ana, cuenta, estudio):
    """CA3."""
    dani = cuenta("dani@ejemplo.com", "Dani")
    respuesta = dani.post("/api/casos", json={**CASO, "espacio": str(estudio)})
    assert respuesta.status_code == 400
    assert "espacio" in respuesta.get_json()["errores"]


def test_crear_en_la_organizacion(ana, estudio):
    """CA1: caso de organización."""
    caso = _crear(ana, espacio=str(estudio))
    assert caso["espacio"] == {"tipo": "organizacion", "id": estudio, "nombre": "Estudio Pérez"}
    assert caso["acciones"]["compartir"]


def test_sin_permiso_el_caso_no_existe(ana, beto, estudio):
    """CA4 (RNF05): ni personal ajeno ni de organización sin acceso."""
    personal = _crear(ana)
    de_estudio = _crear(ana, espacio=str(estudio))
    for id_caso in (personal["id"], de_estudio["id"], 9999):
        respuesta = beto.get(f"/api/casos/{id_caso}")
        assert respuesta.status_code == 404
        assert respuesta.get_json()["codigo"] == "no_encontrado"


def test_listado_paginado_sin_archivados_y_sin_ajenos(aplicacion, ana, beto, estudio):
    """CA5."""
    for _ in range(22):
        _crear(ana)
    archivado = _crear(ana)
    _estado(ana, archivado["id"], "cerrar")
    _estado(ana, archivado["id"], "archivar")
    _crear(beto)  # de otra persona
    primera = ana.get("/api/casos").get_json()
    assert (primera["total"], primera["paginas"], len(primera["casos"])) == (22, 2, 20)
    segunda = ana.get("/api/casos?pagina=2").get_json()
    assert len(segunda["casos"]) == 2
    numeros = [c["numero"] for c in primera["casos"] + segunda["casos"]]
    assert archivado["numero"] not in numeros
    assert len(set(numeros)) == 22
    assert beto.get("/api/casos").get_json()["total"] == 1


def test_filtros_del_listado(ana, estudio):
    """CA6: archivados, expediente sin tildes ni mayúsculas, número, tipo, espacio y fechas."""
    uno = _crear(ana, expediente="Expediente Nº 4567/2026 – Gómez", fecha_hecho="2026-01-10")
    _crear(
        ana, tipo="laboral", expediente="Otro 999", espacio=str(estudio), fecha_hecho="2026-05-10"
    )
    _estado(ana, uno["id"], "cerrar")
    _estado(ana, uno["id"], "archivar")

    def numeros(consulta):
        return [c["numero"] for c in ana.get(f"/api/casos?{consulta}").get_json()["casos"]]

    assert numeros("estado=archivado") == [uno["numero"]]
    assert numeros("expediente=gomez&estado=archivado") == [uno["numero"]]
    assert numeros("expediente=NO EXISTE") == []
    assert numeros("tipo=laboral") == numeros(f"espacio={estudio}")
    assert len(numeros("espacio=personal")) == 0
    assert len(numeros("desde=2026-05-01&hasta=2026-05-31")) == 1
    assert numeros(f"numero={uno['numero'][-6:]}&estado=archivado") == [uno["numero"]]
    assert ana.get("/api/casos?estado=otro").status_code == 400


# --- Editar y estados (CA7 a CA12) ---

def test_editar_registra_anterior_y_nuevo(aplicacion, ana):
    """CA7."""
    caso = _crear(ana)
    respuesta = ana.patch(
        f"/api/casos/{caso['id']}",
        json={"lugar": "Ruta 2 km 50", "fecha_hecho": "2026-08-15", "expediente": ""},
    )
    assert respuesta.status_code == 200
    assert respuesta.get_json()["caso"]["expediente"] is None
    assert _ultima(aplicacion, "caso.edicion")["detalle"]["cambios"] == {
        "lugar": {"anterior": "Av. Corrientes 1234, CABA", "nuevo": "Ruta 2 km 50"},
        "fecha_hecho": {"anterior": "2026-09-01", "nuevo": "2026-08-15"},
        "expediente": {"anterior": "Expte. Nº 4.567/2026", "nuevo": None},
    }
    assert ana.patch(f"/api/casos/{caso['id']}", json={"numero": "X"}).status_code == 400


def test_lector_no_edita_y_colaborador_si(aplicacion, ana, beto, carla, estudio):
    """CA7 (RN20)."""
    caso = _crear(ana, espacio=str(estudio))
    ana.post(
        f"/api/casos/{caso['id']}/accesos", json={"nivel": "lectura", "id_usuario": beto.id_usuario}
    )
    ana.post(
        f"/api/casos/{caso['id']}/accesos",
        json={"nivel": "colaboracion", "id_usuario": carla.id_usuario}
    )
    lectura = beto.get(f"/api/casos/{caso['id']}").get_json()["caso"]
    assert lectura["mi_permiso"] == "lectura"
    assert not lectura["acciones"]["editar"]
    assert beto.patch(f"/api/casos/{caso['id']}", json={"lugar": "X"}).status_code == 403
    assert carla.patch(f"/api/casos/{caso['id']}", json={"lugar": "X"}).status_code == 200
    assert _estado(carla, caso["id"], "cerrar").status_code == 403
    assert _ultima(aplicacion, "caso.cambio_estado")["detalle"]["motivo"] == "permiso_insuficiente"


def test_ciclo_de_estados_y_retencion(ana):
    """CA8 a CA11: cerrar, archivar, desarchivar y reabrir; vencimiento a 2 años."""
    caso = _crear(ana)
    cerrado = _estado(ana, caso["id"], "cerrar").get_json()["caso"]
    assert cerrado["estado"] == "cerrado"
    desde = cerrado["retencion_desde"]
    assert cerrado["retencion_vence"][:4] == str(int(desde[:4]) + 2)
    assert cerrado["retencion_vence"][4:10] == desde[4:10]
    assert ana.patch(f"/api/casos/{caso['id']}", json={"lugar": "X"}).get_json()["codigo"] == (
        "caso_solo_lectura"
    )
    archivado = _estado(ana, caso["id"], "archivar").get_json()["caso"]
    assert archivado["estado"] == "archivado"
    desarchivado = _estado(ana, caso["id"], "desarchivar").get_json()["caso"]
    assert (desarchivado["estado"], desarchivado["retencion_desde"]) == ("cerrado", desde)
    reabierto = _estado(ana, caso["id"], "reabrir").get_json()["caso"]
    assert (reabierto["estado"], reabierto["retencion_vence"]) == ("borrador", None)


@pytest.mark.parametrize(
    ("previas", "operacion"),
    [([], "archivar"), ([], "desarchivar"), ([], "reabrir"), (["cerrar"], "cerrar"),
     (["cerrar", "archivar"], "archivar")],
)
def test_transiciones_invalidas(aplicacion, ana, previas, operacion):
    """CA12 (RN18)."""
    caso = _crear(ana)
    for previa in previas:
        _estado(ana, caso["id"], previa)
    respuesta = _estado(ana, caso["id"], operacion)
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "transicion_invalida")


def test_en_analisis_no_se_cierra_ni_elimina(aplicacion, ana):
    """CA20."""
    caso = _crear(ana)
    with aplicacion.app_context():
        db.session.get(Caso, caso["id"]).estado = "en_analisis"
        db.session.commit()
    assert _estado(ana, caso["id"], "cerrar").get_json()["codigo"] == "caso_en_analisis"
    eliminar = ana.delete(f"/api/casos/{caso['id']}", json={"confirmacion": caso["numero"]})
    assert eliminar.get_json()["codigo"] == "caso_en_analisis"
    assert ana.post(
        f"/api/casos/{caso['id']}/transferencia", json={"destino": "beto@ejemplo.com"}
    ).get_json()["codigo"] == "caso_en_analisis"


# --- Compartir (CA13 a CA16) ---

def test_compartir_con_un_miembro_avisa(aplicacion, correos, ana, beto, estudio):
    """CA13."""
    caso = _crear(ana, espacio=str(estudio))
    correos.clear()
    respuesta = ana.post(
        f"/api/casos/{caso['id']}/accesos", json={"nivel": "lectura", "id_usuario": beto.id_usuario}
    )
    accesos = respuesta.get_json()["accesos"]
    assert [(a["usuario"]["id"], a["nivel"]) for a in accesos] == [(beto.id_usuario, "lectura")]
    assert [c.destinatario for c in correos] == ["beto@ejemplo.com"]
    assert "Te compartieron el caso" in correos[0].texto
    assert beto.get(f"/api/casos/{caso['id']}").status_code == 200
    assert _ultima(aplicacion, "caso.compartir")["detalle"]["nivel"] == "lectura"


def test_toda_la_organizacion_y_prevalece_el_mayor(ana, beto, carla, cuenta, estudio):
    """CA14: miembros actuales y futuros; prevalece el permiso más alto."""
    caso = _crear(ana, espacio=str(estudio))
    ana.post(f"/api/casos/{caso['id']}/accesos", json={"nivel": "lectura"})
    ana.post(
        f"/api/casos/{caso['id']}/accesos",
        json={"nivel": "colaboracion", "id_usuario": beto.id_usuario}
    )
    assert carla.get(f"/api/casos/{caso['id']}").get_json()["caso"]["mi_permiso"] == "lectura"
    assert beto.get(f"/api/casos/{caso['id']}").get_json()["caso"]["mi_permiso"] == "colaboracion"
    dani = cuenta("dani@ejemplo.com", "Dani")
    assert dani.get(f"/api/casos/{caso['id']}").status_code == 404
    _sumar(ana, dani, estudio, "dani@ejemplo.com")
    assert dani.get(f"/api/casos/{caso['id']}").status_code == 200
    assert dani.get("/api/casos").get_json()["total"] == 1


def test_no_se_comparte_un_caso_personal_ni_con_ajenos(aplicacion, ana, cuenta, estudio):
    """CA15 (RN13)."""
    personal = _crear(ana)
    respuesta = ana.post(f"/api/casos/{personal['id']}/accesos", json={"nivel": "lectura"})
    assert respuesta.get_json()["codigo"] == "caso_personal"
    dani = cuenta("dani@ejemplo.com", "Dani")
    de_estudio = _crear(ana, espacio=str(estudio))
    ajeno = ana.post(
        f"/api/casos/{de_estudio['id']}/accesos",
        json={"nivel": "lectura", "id_usuario": dani.id_usuario}
    )
    assert ajeno.status_code == 400
    assert _ultima(aplicacion, "caso.compartir")["detalle"]["motivo"] == "no_es_miembro"
    yo = ana.post(
        f"/api/casos/{de_estudio['id']}/accesos",
        json={"nivel": "lectura", "id_usuario": ana.id_usuario}
    )
    assert yo.status_code == 400


def test_modificar_y_revocar_se_aplican_y_avisan(correos, ana, beto, estudio):
    """CA16."""
    caso = _crear(ana, espacio=str(estudio))
    accesos = ana.post(
        f"/api/casos/{caso['id']}/accesos", json={"nivel": "lectura", "id_usuario": beto.id_usuario}
    ).get_json()["accesos"]
    id_acceso = accesos[0]["id"]
    correos.clear()
    ana.patch(f"/api/casos/{caso['id']}/accesos/{id_acceso}", json={"nivel": "colaboracion"})
    assert beto.patch(f"/api/casos/{caso['id']}", json={"lugar": "Nuevo"}).status_code == 200
    ana.delete(f"/api/casos/{caso['id']}/accesos/{id_acceso}")
    assert beto.get(f"/api/casos/{caso['id']}").status_code == 404
    asuntos = [c.asunto for c in correos]
    assert asuntos[0].startswith("Cambió tu permiso")
    assert asuntos[1].startswith("Ya no tenés acceso")
    assert ana.delete(f"/api/casos/{caso['id']}/accesos/{id_acceso}").status_code == 404


def test_compartir_con_toda_la_organizacion_avisa_a_todos(correos, ana, beto, carla, estudio):
    """CA14: el aviso llega a todos los miembros salvo al Responsable."""
    caso = _crear(ana, espacio=str(estudio))
    correos.clear()
    ana.post(f"/api/casos/{caso['id']}/accesos", json={"nivel": "colaboracion"})
    assert sorted(c.destinatario for c in correos) == ["beto@ejemplo.com", "carla@ejemplo.com"]


# --- Transferir (CA17, CA18) ---

def test_transferir_en_la_organizacion(aplicacion, correos, ana, beto, estudio):
    """CA17: el anterior conserva Colaboración y ambos reciben aviso."""
    caso = _crear(ana, espacio=str(estudio))
    correos.clear()
    respuesta = ana.post(
        f"/api/casos/{caso['id']}/transferencia", json={"destino": str(beto.id_usuario)}
    )
    assert respuesta.get_json()["caso"]["mi_permiso"] == "colaboracion"
    assert beto.get(f"/api/casos/{caso['id']}").get_json()["caso"]["mi_permiso"] == "responsable"
    assert sorted(c.destinatario for c in correos) == ["ana@ejemplo.com", "beto@ejemplo.com"]


def test_transferir_sin_conservar_permiso(ana, beto, estudio):
    """CA17: salvo que indique lo contrario."""
    caso = _crear(ana, espacio=str(estudio))
    ana.post(
        f"/api/casos/{caso['id']}/transferencia",
        json={"destino": str(beto.id_usuario), "conservar_colaboracion": False},
    )
    assert ana.get(f"/api/casos/{caso['id']}").status_code == 404


def test_transferir_a_quien_no_es_miembro_se_rechaza(ana, cuenta, estudio):
    """CA17."""
    dani = cuenta("dani@ejemplo.com", "Dani")
    caso = _crear(ana, espacio=str(estudio))
    for destino in (str(dani.id_usuario), str(ana.id_usuario), "x"):
        respuesta = ana.post(f"/api/casos/{caso['id']}/transferencia", json={"destino": destino})
        assert respuesta.status_code == 400


def test_transferir_un_caso_personal_requiere_aceptacion(aplicacion, correos, ana, beto):
    """CA18: el destinatario acepta y el caso pasa a su espacio personal."""
    caso = _crear(ana)
    correos.clear()
    respuesta = ana.post(
        f"/api/casos/{caso['id']}/transferencia", json={"destino": "Beto@Ejemplo.com"}
    )
    assert respuesta.get_json()["caso"]["transferencia_pendiente"]["correo"] == "beto@ejemplo.com"
    assert "Te quieren transferir" in correos[-1].asunto
    pendientes = beto.get("/api/casos/transferencias").get_json()["transferencias"]
    assert [p["numero"] for p in pendientes] == [caso["numero"]]
    assert beto.get(f"/api/casos/{caso['id']}").status_code == 404  # todavía no es suyo
    assert beto.post(f"/api/casos/{caso['id']}/transferencia/aceptacion").status_code == 200
    detalle = beto.get(f"/api/casos/{caso['id']}").get_json()["caso"]
    assert (detalle["mi_permiso"], detalle["espacio"]["tipo"]) == ("responsable", "personal")
    assert ana.get(f"/api/casos/{caso['id']}").status_code == 404
    assert "aceptó el caso" in correos[-1].texto


def test_rechazar_y_cancelar_una_transferencia_personal(correos, ana, beto):
    """CA18: rechazo del destinatario y cancelación del Responsable."""
    caso = _crear(ana)
    ana.post(f"/api/casos/{caso['id']}/transferencia", json={"destino": "beto@ejemplo.com"})
    beto.post(f"/api/casos/{caso['id']}/transferencia/rechazo")
    assert "rechazó la transferencia" in correos[-1].texto
    assert ana.get(f"/api/casos/{caso['id']}").get_json()["caso"]["transferencia_pendiente"] is None
    ana.post(f"/api/casos/{caso['id']}/transferencia", json={"destino": "beto@ejemplo.com"})
    assert ana.delete(f"/api/casos/{caso['id']}/transferencia").status_code == 200
    assert beto.post(f"/api/casos/{caso['id']}/transferencia/aceptacion").status_code == 404
    assert ana.delete(f"/api/casos/{caso['id']}/transferencia").status_code == 404


def test_transferir_un_caso_personal_a_un_correo_invalido(ana):
    """CA18: el destinatario debe ser otro usuario registrado."""
    caso = _crear(ana)
    for destino in ("nadie@ejemplo.com", "ana@ejemplo.com"):
        respuesta = ana.post(f"/api/casos/{caso['id']}/transferencia", json={"destino": destino})
        assert respuesta.status_code == 400


# --- Eliminar (CA19) ---

def test_eliminar_con_el_numero_avisa_a_quienes_tenian_acceso(
    aplicacion, correos, ana, beto, estudio
):
    """CA19."""
    caso = _crear(ana, espacio=str(estudio))
    ana.post(
        f"/api/casos/{caso['id']}/accesos", json={"nivel": "lectura", "id_usuario": beto.id_usuario}
    )
    incorrecta = ana.delete(f"/api/casos/{caso['id']}", json={"confirmacion": "CASO-0"})
    assert incorrecta.status_code == 400
    correos.clear()
    assert ana.delete(
        f"/api/casos/{caso['id']}", json={"confirmacion": caso["numero"].lower()}
    ).status_code == 200
    assert ana.get(f"/api/casos/{caso['id']}").status_code == 404
    assert [c.destinatario for c in correos] == ["beto@ejemplo.com"]
    resultados = [e["resultado"] for e in entradas_auditoria(aplicacion, "caso.eliminacion")]
    assert resultados == ["rechazado", "exitoso"]


def test_un_colaborador_no_elimina(ana, beto, estudio):
    """CA19 (RN20)."""
    caso = _crear(ana, espacio=str(estudio))
    ana.post(f"/api/casos/{caso['id']}/accesos", json={"nivel": "colaboracion"})
    respuesta = beto.delete(f"/api/casos/{caso['id']}", json={"confirmacion": caso["numero"]})
    assert respuesta.status_code == 403


# --- Reglas de la 004 (CA21 a CA23) ---

def test_responsable_de_casos_no_abandona_sin_transferir(aplicacion, ana, beto, estudio):
    """CA21."""
    caso = _crear(beto, espacio=str(estudio))
    respuesta = beto.post(f"/api/organizaciones/{estudio}/abandono", json={})
    assert (respuesta.status_code, respuesta.get_json()["codigo"]) == (409, "debe_transferir_casos")
    beto.post(f"/api/casos/{caso['id']}/transferencia", json={"destino": str(ana.id_usuario)})
    assert beto.post(f"/api/organizaciones/{estudio}/abandono", json={}).status_code == 200
    assert beto.get(f"/api/casos/{caso['id']}").status_code == 404  # su acceso ya no vale


def test_desvincular_pasa_los_casos_al_referente(aplicacion, ana, beto, estudio):
    """CA22 (RN14)."""
    caso = _crear(beto, espacio=str(estudio))
    otro = _crear(ana, espacio=str(estudio))
    ana.post(
        f"/api/casos/{otro['id']}/accesos",
        json={"nivel": "colaboracion", "id_usuario": beto.id_usuario}
    )
    ana.post(f"/api/casos/{caso['id']}/transferencia", json={"destino": str(ana.id_usuario)})
    ana.delete(f"/api/organizaciones/{estudio}/miembros/{beto.id_usuario}")
    detalle = ana.get(f"/api/casos/{caso['id']}").get_json()["caso"]
    assert detalle["responsable"]["id"] == ana.id_usuario
    accesos = ana.get(f"/api/casos/{otro['id']}").get_json()["accesos"]
    assert accesos == []
    entrada = _ultima(aplicacion, "caso.transferencia")
    assert entrada["detalle"]["motivo"] == "desvinculacion"


def test_eliminar_la_organizacion_elimina_sus_casos(aplicacion, ana, beto, estudio):
    """CA23 (RN09): la confirmación informa la cantidad."""
    _crear(ana, espacio=str(estudio))
    _crear(beto, espacio=str(estudio))
    personal = _crear(ana)
    organizacion = ana.get(f"/api/organizaciones/{estudio}").get_json()["organizacion"]
    assert organizacion["cantidad_casos"] == 2
    ana.delete(f"/api/organizaciones/{estudio}", json={"confirmacion": "Estudio Pérez"})
    with aplicacion.app_context():
        assert [c.id for c in Caso.query.all()] == [personal["id"]]
    assert _ultima(aplicacion, "organizacion.eliminacion")["detalle"]["casos_eliminados"] == 2


# --- Resumen, aseguradoras y auditoría (CA3, CA24) ---

def test_resumen_por_estado(ana):
    """Cantidad de casos por estado para el inicio."""
    _crear(ana)
    cerrado = _crear(ana)
    _estado(ana, cerrado["id"], "cerrar")
    assert ana.get("/api/casos/resumen").get_json()["por_estado"] == {"borrador": 1, "cerrado": 1}


def test_una_aseguradora_no_tiene_espacio_personal(aplicacion, correos):
    """CA3: el perfil Aseguradora crea casos en su aseguradora, no en el espacio personal."""
    cliente = aplicacion.test_client()
    cliente.post("/api/cuentas/registro", json=datos_registro(
        correo="rita@galicia.com", perfil="aseguradora", colegio=None, id_aseguradora=25,
    ))
    cliente.post("/api/cuentas/verificacion", json={"token": extraer_token(correos[-1])})
    cliente.post(
        "/api/sesion", json={"correo": "rita@galicia.com", "contrasenia": CONTRASENIA_VALIDA}
    )
    personal = cliente.post("/api/casos", json=CASO)
    assert "espacio" in personal.get_json()["errores"]
    id_org = cliente.get("/api/organizaciones").get_json()["organizaciones"][0]["id"]
    pendiente = cliente.post("/api/casos", json={**CASO, "espacio": str(id_org)})
    assert "espacio" in pendiente.get_json()["errores"]  # todavía no fue aprobada


def test_auditoria_de_casos(aplicacion, ana, beto, estudio):
    """CA24: cada operación queda registrada con el caso como recurso."""
    caso = _crear(ana, espacio=str(estudio))
    ana.patch(f"/api/casos/{caso['id']}", json={"lugar": "Otro"})
    ana.post(f"/api/casos/{caso['id']}/accesos", json={"nivel": "lectura"})
    _estado(ana, caso["id"], "cerrar")
    acciones = [
        e["accion"] for e in entradas_auditoria(aplicacion) if e["tipo_recurso"] == "caso"
    ]
    assert acciones == ["caso.creacion", "caso.edicion", "caso.compartir", "caso.cambio_estado"]
