"""Actualización automática del catálogo de aseguradoras de la SSN (052).

Pedido de la autora (2026-11-24): «una automatización de los registros de
seguros, que cada cierto tiempo consulte la página y baje el dataset
actualizado». Un temporizador semanal ejecuta ``actualizar``, que:

1. baja el CSV vigente de entidades activas (datos abiertos de la SSN);
2. le aplica la misma transformación que al archivo original: quita las
   reaseguradoras («Reaseg. Admitida» y «Reaseg. Local»), que no gestionan
   siniestros de asegurados (CP-18), y deja las columnas que usa la plataforma;
3. **lo valida antes de usarlo**: columnas esperadas, identificadores y CUIT sin
   repetir y una cantidad razonable. Si la lista nueva tiene menos del 80 % de
   las aseguradoras actuales, no la aplica: es más probable un archivo roto que
   un cierre masivo;
4. señala las revocaciones de la autorización para operar que la SSN anota en
   la denominación («Revocación autorización para operar no firme…»);
5. si cambió, la guarda, lo registra en la auditoría y avisa a los
   Administradores con las altas y las bajas, señalando las aseguradoras ya
   registradas en la plataforma que dejaron de figurar o están en revocación.

Las organizaciones registradas guardan su CUIT: una baja del catálogo no las
desactiva sola, la decisión es del Administrador.

Realiza: RN36, RN37 (CP-18); RNF06; 052.
"""
import csv
import hashlib
import io

from app.integraciones.fuente_ssn import FuenteSsnNoDisponible
from app.repositorios.catalogo_aseguradoras import Aseguradora
from app.servicios import auditoria
from app.utilidades.tiempo import ahora_utc

COLUMNAS_NECESARIAS = ("cia_id", "cia_denominacion", "cia_cuit", "cia_actividad_principal")
PREFIJO_REASEGURADORAS = "Reaseg."
MINIMO_ASEGURADORAS = 100
PROPORCION_MINIMA = 0.8
# La SSN anota en la denominación las revocaciones en trámite, por ejemplo
# «(Revocación autorización para operar no firme RESOL-2026-443-APN-SSN#MEC)».
MARCA_REVOCACION = "revocaci"


class CatalogoSsnInvalido(Exception):
    """El archivo bajado no tiene la forma o el tamaño esperados: no se aplica."""


class CatalogoSsnNoDisponible(Exception):
    """El portal de datos abiertos no respondió: se reintenta en la próxima ejecución."""


def transformar(contenido):
    """Del CSV de la SSN a la lista de aseguradoras que usa la plataforma.

    Raises:
        CatalogoSsnInvalido: si faltan columnas, hay datos repetidos o vacíos, o
            quedan menos de ``MINIMO_ASEGURADORAS``.
    """
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError as falla:
        raise CatalogoSsnInvalido("El archivo no está en UTF-8.") from falla
    lector = csv.DictReader(io.StringIO(texto))
    faltantes = [c for c in COLUMNAS_NECESARIAS if c not in (lector.fieldnames or [])]
    if faltantes:
        raise CatalogoSsnInvalido(f"Faltan columnas: {', '.join(faltantes)}.")
    aseguradoras = []
    for fila in lector:
        actividad = " ".join((fila["cia_actividad_principal"] or "").split())
        if actividad.startswith(PREFIJO_REASEGURADORAS):
            continue
        try:
            identificador = int(fila["cia_id"])
        except (TypeError, ValueError) as falla:
            raise CatalogoSsnInvalido(f"Registro inválido: {fila['cia_id']!r}.") from falla
        cuit = (fila["cia_cuit"] or "").strip()
        denominacion = " ".join((fila["cia_denominacion"] or "").split())
        if not denominacion or not (cuit.isdigit() and len(cuit) == 11):
            raise CatalogoSsnInvalido(f"Datos incompletos en el registro {identificador}.")
        aseguradoras.append(Aseguradora(identificador, denominacion, cuit, actividad))
    if len({a.id for a in aseguradoras}) != len(aseguradoras):
        raise CatalogoSsnInvalido("Hay números de registro repetidos.")
    if len({a.cuit for a in aseguradoras}) != len(aseguradoras):
        raise CatalogoSsnInvalido("Hay CUIT repetidos.")
    if len(aseguradoras) < MINIMO_ASEGURADORAS:
        raise CatalogoSsnInvalido(f"Solo trae {len(aseguradoras)} aseguradoras.")
    return aseguradoras


def en_revocacion(aseguradora):
    """Si la SSN anotó una revocación de la autorización para operar."""
    return MARCA_REVOCACION in aseguradora.denominacion.lower()


def comparar(actuales, nuevas):
    """Altas, bajas y cambios de denominación o actividad entre dos catálogos."""
    por_id_actual = {a.id: a for a in actuales}
    por_id_nuevo = {a.id: a for a in nuevas}
    return {
        "altas": [a for i, a in por_id_nuevo.items() if i not in por_id_actual],
        "bajas": [a for i, a in por_id_actual.items() if i not in por_id_nuevo],
        "modificadas": [
            a for i, a in por_id_nuevo.items()
            if i in por_id_actual and a != por_id_actual[i]
        ],
        # Revocaciones que aparecen ahora (en una alta o en un cambio de denominación).
        "revocaciones": [
            a for i, a in por_id_nuevo.items()
            if en_revocacion(a) and not (i in por_id_actual and en_revocacion(por_id_actual[i]))
        ],
    }


class ServicioCatalogoSsn:
    """Baja, valida y aplica la versión nueva del catálogo."""

    def __init__(  # pylint: disable=too-many-arguments
        self, fuente, catalogo, registro, *, organizaciones=None, usuarios=None, correos=None
    ):
        """
        Args:
            fuente: ``FuenteSsn``.
            catalogo: ``CatalogoAseguradoras`` con carpeta para la copia actualizada.
            registro: ``ServicioAuditoria``.
            organizaciones: ``RepositorioOrganizaciones``, para ver quién quedó afuera.
            usuarios: ``RepositorioUsuarios``, para avisar a los Administradores.
            correos: ``ServicioCorreos``; None no avisa.
        """
        self.fuente = fuente
        self.catalogo = catalogo
        self.registro = registro
        self.organizaciones = organizaciones
        self.usuarios = usuarios
        self.correos = correos

    def actualizar(self, forzar=False):
        """Baja el catálogo y lo aplica si cambió.

        Args:
            forzar: aplica aunque la lista nueva sea mucho más corta (lo decide una persona).

        Returns:
            dict con ``cambio`` (bool), ``total``, ``altas``, ``bajas``, ``modificadas``
            (listas de ``Aseguradora``) y ``afectadas`` (organizaciones registradas
            que dejaron de figurar).

        Raises:
            CatalogoSsnNoDisponible: si el portal no responde.
            CatalogoSsnInvalido: si el archivo no pasa las validaciones.
        """
        try:
            contenido, recurso = self.fuente.descargar()
        except FuenteSsnNoDisponible as falla:
            raise CatalogoSsnNoDisponible(str(falla)) from falla
        nuevas = transformar(contenido)
        actuales = self.catalogo.todas()
        if not forzar and len(nuevas) < PROPORCION_MINIMA * len(actuales):
            raise CatalogoSsnInvalido(
                f"La lista nueva trae {len(nuevas)} aseguradoras y la actual {len(actuales)}: "
                "no se aplica sin revisarla (usar --forzar)."
            )
        diferencias = comparar(actuales, nuevas)
        cambio = any(diferencias.values())
        afectadas = []
        if cambio:
            self.catalogo.guardar(nuevas, {
                "fuente": recurso["url"],
                "actualizado_en_la_fuente": recurso["actualizado"],
                "aplicado": ahora_utc().isoformat(timespec="seconds"),
                "sha256": hashlib.sha256(contenido).hexdigest(),
            })
            afectadas = self._afectadas(diferencias["bajas"] + diferencias["revocaciones"])
            self.registro.registrar(
                auditoria.CATALOGO_ACTUALIZACION, auditoria.EXITOSO,
                detalle={
                    "total": len(nuevas),
                    "altas": [a.id for a in diferencias["altas"]],
                    "bajas": [a.id for a in diferencias["bajas"]],
                    "modificadas": [a.id for a in diferencias["modificadas"]],
                    "revocaciones": [a.id for a in diferencias["revocaciones"]],
                    "organizaciones_afectadas": [o.id for o in afectadas],
                },
                confirmar=True,
            )
            self._avisar(diferencias, afectadas, len(nuevas))
        return {"cambio": cambio, "total": len(nuevas), "afectadas": afectadas, **diferencias}

    def _afectadas(self, bajas):
        if not bajas or self.organizaciones is None:
            return []
        return [o for o in (self.organizaciones.obtener_por_cuit(a.cuit) for a in bajas) if o]

    def _avisar(self, diferencias, afectadas, total):
        if self.correos is None or self.usuarios is None:
            return
        for administrador in self.usuarios.administradores():
            self.correos.enviar_aviso_catalogo_ssn(
                administrador, diferencias, afectadas, total
            )
