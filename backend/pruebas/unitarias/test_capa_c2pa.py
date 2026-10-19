"""Pruebas de la capa de credenciales de contenido C2PA (funcionalidad 009).

Las imágenes se generan en memoria y se firman con c2pa-python usando una
autoridad certificante creada para cada sesión de pruebas: nunca se usan
imágenes de casos reales. Las imágenes de la prueba de canales del TIF se
analizan solo si se indica su carpeta en ``IMAGENES_CANALES_TIF``.
"""
# Los accesorios de pytest se reciben como argumentos aunque no se usen en el cuerpo.
# pylint: disable=redefined-outer-name
import io
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import c2pa
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID, ObjectIdentifier
from PIL import Image

from app.analisis import credenciales_c2pa
from app.analisis.base import (
    NIVEL_MAXIMO,
    RECOMENDACION,
    TERMINOS_DE_VEREDICTO,
    CapaNoDisponible,
    ContextoImagen,
    texto_acotado,
)
from app.analisis.credenciales_c2pa import (
    ARCHIVOS_CONFIANZA,
    FIRMA_CONFIABLE,
    FIRMA_CONTENIDO_MODIFICADO,
    FIRMA_INVALIDA,
    FIRMA_NO_RECONOCIDA,
    CapaC2PA,
)
from app.analisis.registro import crear_capas

IA = "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
CAMARA = "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture"
CLAIM_SIGNING = ObjectIdentifier("1.3.6.1.4.1.62558.2.1")
CARGA = datetime(2026, 10, 19, 12, 0)


# --- Autoridad certificante y firma de imágenes de prueba ---

def _nombre(comun):
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "AR"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Pruebas de la plataforma"),
        x509.NameAttribute(NameOID.COMMON_NAME, comun),
    ])


def _uso_de_clave(firma, certificados):
    return x509.KeyUsage(
        digital_signature=firma, content_commitment=False, key_encipherment=False,
        data_encipherment=False, key_agreement=False, key_cert_sign=certificados,
        crl_sign=certificados, encipher_only=False, decipher_only=False,
    )


def _pem(certificado):
    return certificado.public_bytes(serialization.Encoding.PEM)


@pytest.fixture(scope="module")
def autoridad():
    """Raíz y certificado de firma de prueba; ``raiz_pem`` se usa como lista de confianza."""
    ahora = datetime.now(timezone.utc)
    clave_raiz = ec.generate_private_key(ec.SECP256R1())
    raiz = (
        x509.CertificateBuilder()
        .subject_name(_nombre("Raíz de prueba")).issuer_name(_nombre("Raíz de prueba"))
        .public_key(clave_raiz.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(ahora - timedelta(days=1)).not_valid_after(ahora + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(_uso_de_clave(False, True), critical=True)
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(clave_raiz.public_key()), critical=False
        )
        .sign(clave_raiz, hashes.SHA256())
    )
    clave = ec.generate_private_key(ec.SECP256R1())
    hoja = (
        x509.CertificateBuilder()
        .subject_name(_nombre("Generador de prueba")).issuer_name(raiz.subject)
        .public_key(clave.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(ahora - timedelta(days=1)).not_valid_after(ahora + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(_uso_de_clave(True, False), critical=True)
        .add_extension(x509.ExtendedKeyUsage([CLAIM_SIGNING]), critical=False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(clave_raiz.public_key()),
            critical=False,
        )
        .sign(clave_raiz, hashes.SHA256())
    )
    firmante = c2pa.Signer.from_info(c2pa.C2paSignerInfo(
        c2pa.C2paSigningAlg.ES256,
        _pem(hoja) + _pem(raiz),
        clave.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
        None,
    ))
    return {"firmante": firmante, "raiz_pem": _pem(raiz)}


@pytest.fixture(scope="module")
def firmar(autoridad):
    """Imagen JPEG o PNG firmada con las acciones indicadas."""
    def _firmar(acciones, formato="jpeg"):
        original = io.BytesIO()
        Image.new("RGB", (64, 48), (200, 40, 40)).save(original, formato.upper())
        original.seek(0)
        manifiesto = {
            "claim_generator_info": [{"name": "Generador de prueba", "version": "1.0"}],
            "title": f"prueba.{formato}",
            "assertions": [{"label": "c2pa.actions", "data": {"actions": acciones}}],
        }
        destino = io.BytesIO()
        contexto = c2pa.Context(c2pa.Settings.from_dict({"verify": {"verify_after_sign": False}}))
        with c2pa.Builder(manifiesto, context=contexto) as constructor:
            constructor.sign(autoridad["firmante"], f"image/{formato}", original, destino)
        return destino.getvalue()
    return _firmar


@pytest.fixture(scope="module")
def capa_de_prueba(autoridad, tmp_path_factory):
    """Capa cuya lista de confianza contiene la raíz de prueba."""
    carpeta = tmp_path_factory.mktemp("confianza")
    for nombre in ARCHIVOS_CONFIANZA:
        (carpeta / nombre).write_bytes(autoridad["raiz_pem"])
    return CapaC2PA(carpeta)


def _contexto(formato="jpeg"):
    return ContextoImagen(formato, 64, 48, CARGA)


def _creada_con_ia(**extra):
    return {
        "action": "c2pa.created", "softwareAgent": {"name": "Modelo de prueba", "version": "2"},
        "digitalSourceType": IA, **extra,
    }


def _tabla(resultado):
    return {fila["campo"]: fila["valor"] for fila in resultado.detalle["tabla"]}


# --- Firma confiable (RF40 CA1, CA4) ---

def test_firma_confiable_que_declara_ia_tiene_el_nivel_maximo(capa_de_prueba, firmar):
    """CA1 (RN28): firma confiable y declaración de IA llevan el nivel al 100 %."""
    resultado = capa_de_prueba.analizar(firmar([_creada_con_ia()]), _contexto())

    assert resultado.nivel == NIVEL_MAXIMO == 100
    assert resultado.detalle["estado_firma"] == FIRMA_CONFIABLE
    assert [a.severidad for a in resultado.anomalias] == ["directo"]
    assert "el indicio más fuerte" in resultado.conclusion
    assert "generada por un modelo de inteligencia artificial" in resultado.conclusion
    assert resultado.conclusion.endswith(RECOMENDACION)


def test_informa_firmante_herramienta_y_acciones(capa_de_prueba, firmar):
    """CA4: se informan el firmante, la herramienta y las acciones registradas."""
    acciones = [_creada_con_ia(), {"action": "c2pa.converted"}, {"action": "c2pa.vendor.otra"}]

    tabla = _tabla(capa_de_prueba.analizar(firmar(acciones), _contexto()))

    assert tabla["Estado de la firma"].startswith("Confiable")
    assert tabla["Firmante"] == "Pruebas de la plataforma · Generador de prueba"
    assert tabla["Herramienta declarada"] == "Generador de prueba 1.0"
    assert tabla["Agente de software"] == "Modelo de prueba 2"
    assert tabla["Origen declarado"] == "generada por un modelo de inteligencia artificial"
    assert tabla["Acciones registradas"] == "creación, conversión de formato, c2pa.vendor.otra"
    assert tabla["Sello de tiempo de la firma"] == "Sin sello de tiempo verificable"
    assert "Fecha de la firma" not in tabla  # sin sello de tiempo no hay fecha confiable
    assert "Detalle de la validación" not in tabla


def test_png_firmado_tambien_se_verifica(capa_de_prueba, firmar):
    """Los PNG se leen igual que los JPEG."""
    resultado = capa_de_prueba.analizar(firmar([_creada_con_ia()], "png"), _contexto("png"))

    assert resultado.nivel == 100


def test_ediciones_registradas_con_firma_confiable(capa_de_prueba, firmar):
    """Las ediciones registradas con firma confiable son un indicio fuerte."""
    acciones = [
        {"action": "c2pa.created", "digitalSourceType": CAMARA},
        {"action": "c2pa.cropped", "softwareAgent": "Editor de prueba"},
        {"action": "c2pa.color_adjustments", "softwareAgent": "Editor de prueba"},
    ]

    resultado = capa_de_prueba.analizar(firmar(acciones), _contexto())

    assert resultado.nivel == 70
    assert [(a.campo, a.severidad) for a in resultado.anomalias] == [
        ("Acciones registradas (C2PA)", "fuerte"),
    ]
    assert "recorte, ajuste de color" in resultado.anomalias[0].descripcion
    assert _tabla(resultado)["Origen declarado"] == "captura de una cámara digital"


def test_captura_de_camara_sin_ediciones_no_suma_indicios(capa_de_prueba, firmar):
    """Credenciales confiables de una cámara, sin ediciones: nivel 0."""
    resultado = capa_de_prueba.analizar(
        firmar([{"action": "c2pa.created", "digitalSourceType": CAMARA}]), _contexto()
    )

    assert resultado.nivel == 0
    assert resultado.anomalias == []
    assert "no declaran generación por inteligencia artificial ni ediciones" in (
        resultado.conclusion
    )


def test_contenido_sintetico_sin_ia_no_llega_al_maximo(capa_de_prueba, firmar):
    """El 100 % se reserva para la declaración de IA; otro origen sintético llega a 90."""
    acciones = [{
        "action": "c2pa.created",
        "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/algorithmicMedia",
    }]

    resultado = capa_de_prueba.analizar(firmar(acciones), _contexto())

    assert resultado.nivel == 90
    assert "creada por un algoritmo" in resultado.conclusion


# --- Firma no confiable o inválida (RF40 CA2) ---

def test_firmante_fuera_de_la_lista_no_llega_al_maximo(firmar):
    """Con la lista oficial, la raíz de prueba no es reconocida."""
    resultado = CapaC2PA().analizar(firmar([_creada_con_ia()]), _contexto())

    assert resultado.detalle["estado_firma"] == FIRMA_NO_RECONOCIDA
    assert [(a.campo, a.severidad) for a in resultado.anomalias] == [
        ("Origen declarado (C2PA)", "fuerte"), ("Firma", "debil"),
    ]
    assert resultado.nivel == 70
    assert "no se puede confirmar quién la emitió" in resultado.anomalias[0].descripcion
    tabla = _tabla(resultado)
    assert tabla["Estado de la firma"].startswith("Firmante no reconocido")
    assert "lista de confianza de C2PA (signingCredential.untrusted)" in (
        tabla["Detalle de la validación"]
    )


def test_imagen_modificada_despues_de_firmarse(capa_de_prueba, firmar):
    """CA2: un byte cambiado después de firmar se informa con el detalle de la validación."""
    alterada = bytearray(firmar([_creada_con_ia()]))
    alterada[-200] ^= 0xFF

    resultado = capa_de_prueba.analizar(bytes(alterada), _contexto())

    assert resultado.detalle["estado_firma"] == FIRMA_CONTENIDO_MODIFICADO
    assert [a.severidad for a in resultado.anomalias] == ["moderado", "moderado"]
    assert resultado.nivel == 55
    firma = resultado.anomalias[1]
    assert "credenciales copiadas de otro archivo" in firma.descripcion
    assert "la imagen cambió después de firmarse (assertion.dataHash.mismatch)" in (
        firma.descripcion
    )


@pytest.mark.parametrize(("estado", "codigos", "esperado"), [
    ("Trusted", [], FIRMA_CONFIABLE),
    ("Valid", ["signingCredential.untrusted"], FIRMA_NO_RECONOCIDA),
    ("Valid", [], FIRMA_NO_RECONOCIDA),
    ("Invalid", ["assertion.dataHash.mismatch"], FIRMA_CONTENIDO_MODIFICADO),
    ("Invalid", ["signingCredential.untrusted", "claimSignature.mismatch"],
     FIRMA_CONTENIDO_MODIFICADO),
    ("Invalid", ["signingCredential.expired"], FIRMA_INVALIDA),
    ("Invalid", ["signingCredential.untrusted", "signingCredential.revoked"], FIRMA_INVALIDA),
])
def test_estado_de_la_firma(estado, codigos, esperado):
    """Clasificación de las fallas de c2pa-python en los cuatro estados de la firma."""
    validacion = {"failure": [{"code": c} for c in codigos]}

    assert CapaC2PA.estado_de_la_firma(estado, validacion) == esperado


def test_firma_invalida_con_ediciones():
    """CA2: credenciales no válidas, con una falla desconocida explicada en inglés."""
    datos = {
        "estado_firma": FIRMA_INVALIDA, "firmante": "", "herramientas": [], "agentes": [],
        "origenes": [], "acciones": ["c2pa.edited"],
        "fallas": [{"codigo": "codigo.desconocido", "explicacion": "unknown failure"}],
    }

    anomalias = CapaC2PA.hallazgos(datos)

    assert [(a.campo, a.severidad) for a in anomalias] == [
        ("Acciones registradas (C2PA)", "debil"), ("Firma", "moderado"),
    ]
    assert "unknown failure (codigo.desconocido)" in anomalias[1].descripcion
    assert CapaC2PA.calcular_nivel(datos, anomalias) == 45


# --- Sin credenciales (RF40 CA3, RN28) ---

@pytest.mark.parametrize("formato", ["jpeg", "png"])
def test_sin_credenciales_de_contenido(formato):
    """CA3 (RN28): sin manifiesto, nivel 0 y la aclaración de que no prueba autenticidad."""
    imagen = io.BytesIO()
    Image.new("RGB", (32, 32), (10, 10, 10)).save(imagen, formato.upper())

    resultado = CapaC2PA().analizar(imagen.getvalue(), _contexto(formato))

    assert resultado.nivel == 0
    assert resultado.detalle == {"tabla": [], "sin_credenciales": True, "estado_firma": None}
    assert resultado.conclusion.startswith("Sin credenciales de contenido.")
    assert "no constituye evidencia de autenticidad" in resultado.conclusion
    assert [a.severidad for a in resultado.anomalias] == ["neutro"]


# --- Fallas (CA5, RN26) ---

def test_credenciales_ilegibles_se_informan_como_anomalia(monkeypatch):
    """CA5: credenciales que no se pueden leer son una anomalía moderada."""
    def lector_que_falla(*_argumentos, **_opciones):
        raise c2pa.C2paError.Decoding("datos JUMBF dañados")

    monkeypatch.setattr(credenciales_c2pa.c2pa, "Reader", lector_que_falla)

    resultado = CapaC2PA().analizar(b"contenido", _contexto())

    assert resultado.nivel == 45
    assert resultado.anomalias[0].campo == "Manifiesto C2PA"
    assert "no se pudieron leer" in resultado.conclusion


def test_sin_biblioteca_la_capa_no_esta_disponible(monkeypatch):
    """CA5 (RN26): sin c2pa-python, la capa queda No disponible."""
    monkeypatch.setattr(credenciales_c2pa, "c2pa", None)

    with pytest.raises(CapaNoDisponible, match="c2pa-python no está instalada"):
        CapaC2PA().analizar(b"contenido", _contexto())


def test_sin_lista_de_confianza_la_capa_no_esta_disponible(tmp_path):
    """CA5 (RN26): sin la lista de confianza no se verifica nada."""
    capa = CapaC2PA(tmp_path)

    with pytest.raises(CapaNoDisponible, match="lista de confianza"):
        capa.analizar(b"contenido", _contexto())
    assert capa.version().endswith("lista de confianza no disponible)")


def test_version_registra_biblioteca_y_lista(monkeypatch):
    """RN29: la versión identifica c2pa-python y la lista de confianza usada."""
    version = CapaC2PA().version()

    assert version.startswith("1.0 (c2pa-python 0.38.0, lista de confianza ")
    assert "b3949271a07b/7182cb227c02" in version

    def no_instalada(_paquete):
        raise credenciales_c2pa.metadata.PackageNotFoundError

    monkeypatch.setattr(credenciales_c2pa.metadata, "version", no_instalada)
    assert "c2pa-python no disponible" in CapaC2PA().version()


# --- Textos y registro ---

def test_las_conclusiones_no_emiten_veredictos(capa_de_prueba, firmar):
    """RN27: ninguna conclusión usa términos de veredicto."""
    imagenes = [
        firmar([_creada_con_ia()]),
        firmar([{"action": "c2pa.edited"}]),
        firmar([{"action": "c2pa.created", "digitalSourceType": CAMARA}]),
        b"sin credenciales",
    ]
    for contenido in imagenes:
        resultado = capa_de_prueba.analizar(contenido, _contexto())
        textos = [resultado.conclusion, *(a.descripcion for a in resultado.anomalias)]
        for texto in textos:
            assert not any(t in texto.lower().split() for t in TERMINOS_DE_VEREDICTO), texto
            assert RECOMENDACION in resultado.conclusion


def test_fecha_de_firma_ilegible_se_muestra_tal_cual():
    """La fecha de la firma se muestra en UTC, o tal cual si no se entiende."""
    assert credenciales_c2pa._fecha_de_firma("ayer") == "ayer"  # pylint: disable=protected-access
    assert credenciales_c2pa._fecha_de_firma(  # pylint: disable=protected-access
        "2026-09-28T15:20:55-03:00"
    ) == "28/09/2026 18:20:55 UTC"


def test_firmante_no_reconocido_sin_otros_hallazgos_es_indicio_debil():
    """Un firmante fuera de la lista, sin otros hallazgos, es un indicio débil."""
    datos = {
        "estado_firma": FIRMA_NO_RECONOCIDA, "firmante": "Firmante X", "herramientas": [],
        "agentes": [], "origenes": ["digitalcapture"], "acciones": ["c2pa.created"], "fallas": [],
    }

    anomalias = CapaC2PA.hallazgos(datos)
    nivel = CapaC2PA.calcular_nivel(datos, anomalias)

    assert nivel == 20
    assert "presentan indicios débiles" in CapaC2PA.redactar_conclusion(nivel, anomalias, datos)


def test_solo_se_leen_las_declaraciones_de_acciones():
    """Solo cuentan las declaraciones ``c2pa.actions`` con acciones bien formadas."""
    manifiesto = {"assertions": [
        {"label": "stds.schema-org.CreativeWork", "data": {"actions": [{"action": "x"}]}},
        {"label": "c2pa.actions.v2", "data": {"actions": [{"action": "c2pa.created"}, "texto"]}},
        {"label": "c2pa.actions", "data": None},
    ]}

    assert CapaC2PA.acciones(manifiesto) == [{"action": "c2pa.created"}]


def test_los_datos_extraidos_se_acotan():
    """Un manifiesto puede traer estructuras o textos enormes."""
    assert texto_acotado({"a": 1}) == '{"a": 1}'
    assert texto_acotado("x" * 400) == "x" * 300 + "…"


def test_herramienta_del_manifiesto_antiguo():
    """Los manifiestos de la versión 1 de C2PA declaran ``claim_generator`` como texto."""
    lectura = {
        "estado": "Trusted",
        "manifiesto": {"claim_generator": "Editor/1.0", "signature_info": {}},
        "validacion": {"success": [{"code": "timeStamp.validated"}]},
    }

    datos = CapaC2PA.datos(lectura)

    assert datos["herramientas"] == ["Editor/1.0"]
    assert datos["sello_de_tiempo"].startswith("Válido, emitido por una autoridad fuera")


def test_la_capa_2_esta_registrada_despues_de_metadatos():
    """ADR-0006: la capa nueva se agrega al registro sin cambiar la de metadatos."""
    capas = crear_capas({"RUTA_EXIFTOOL": "exiftool", "CARPETA_CONFIANZA_C2PA": "/tmp/x"})

    assert [c.nombre for c in capas] == ["metadatos", "c2pa"]
    assert capas[1].carpeta_confianza == "/tmp/x"


# --- Prueba de canales del TIF (CA8), solo con las imágenes en la máquina local ---

CANALES = os.getenv("IMAGENES_CANALES_TIF")
ESPERADO_POR_CANAL = {
    "01_original": 100, "02_whatsapp_foto": 0, "03_whatsapp_documento": 100,
    "04_mail": 100, "05_captura": 0,
}


@pytest.mark.skipif(not CANALES, reason="Indicar la carpeta en IMAGENES_CANALES_TIF")
@pytest.mark.parametrize("generador", ["canales_gpt", "canales_gemini"])
def test_prueba_de_canales_del_tif(generador):
    """CA8: el manifiesto se conserva como documento y por correo, y se pierde como foto."""
    capa = CapaC2PA()
    for ruta in sorted(Path(CANALES, generador).glob("0*")):
        formato = "png" if ruta.suffix == ".png" else "jpeg"
        resultado = capa.analizar(ruta.read_bytes(), _contexto(formato))
        assert resultado.nivel == ESPERADO_POR_CANAL[ruta.stem], ruta.name
