"""Almacenamiento de archivos (patrón Strategy).

Dos implementaciones intercambiables con la misma interfaz:

- ``AlmacenamientoS3``: producción. Bucket privado con cifrado en reposo y
  versionado (RNF03 CA1); los enlaces son URL prefirmadas de S3.
- ``AlmacenamientoLocal``: desarrollo y pruebas. Guarda los archivos en una
  carpeta del servidor que nunca se sube al repositorio; los enlaces son
  tokens firmados que sirve la ruta ``/api/archivos/<token>``.

Las claves de los archivos las arma el servicio: son aleatorias y no
contienen datos personales (RNF09 CA2).

Realiza: RF34 (CA1), RF35 (CA2), RF36 (CA1); RNF03 (CA1), RNF18 (CA2).
"""
from pathlib import Path
from urllib.parse import quote

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

PROPOSITO_ENLACE = "archivo-almacenado"


class ArchivoNoDisponible(Exception):
    """El enlace venció, fue alterado o el archivo ya no existe."""


class AlmacenamientoS3:
    """Archivos en un bucket de Amazon S3 (o compatible)."""

    def __init__(self, cliente, bucket, cifrado=None):
        """
        Args:
            cliente: cliente de S3 de boto3.
            cifrado: valor de ``ServerSideEncryption`` (por ejemplo ``"AES256"``),
                o None si el bucket ya cifra por defecto.
        """
        self.cliente = cliente
        self.bucket = bucket
        self.cifrado = cifrado

    def guardar(self, clave, contenido, tipo_mime):
        """Sube el archivo tal cual, sin modificarlo (RN23)."""
        extra = {"ServerSideEncryption": self.cifrado} if self.cifrado else {}
        self.cliente.put_object(
            Bucket=self.bucket, Key=clave, Body=contenido, ContentType=tipo_mime, **extra
        )

    def leer(self, clave):
        """Devuelve el contenido del archivo (para el análisis de la funcionalidad 007)."""
        return self.cliente.get_object(Bucket=self.bucket, Key=clave)["Body"].read()

    def eliminar(self, clave):
        """Elimina el archivo con todas sus versiones (RF36 CA1, RN21)."""
        paginas = self.cliente.get_paginator("list_object_versions").paginate(
            Bucket=self.bucket, Prefix=clave
        )
        for pagina in paginas:
            for version in pagina.get("Versions", []) + pagina.get("DeleteMarkers", []):
                if version["Key"] == clave:
                    self.cliente.delete_object(
                        Bucket=self.bucket, Key=clave, VersionId=version["VersionId"]
                    )

    def enlace(self, clave, segundos, nombre_descarga=None):
        """URL prefirmada de corta duración (RF35 CA2)."""
        parametros = {"Bucket": self.bucket, "Key": clave}
        if nombre_descarga:
            parametros["ResponseContentDisposition"] = disposicion_de_descarga(nombre_descarga)
        return self.cliente.generate_presigned_url(
            "get_object", Params=parametros, ExpiresIn=segundos
        )


class AlmacenamientoLocal:
    """Archivos en una carpeta local, con enlaces firmados que sirve la API."""

    def __init__(self, directorio, clave_secreta):
        self.directorio = Path(directorio)
        self._firmador = URLSafeTimedSerializer(clave_secreta, salt=PROPOSITO_ENLACE)

    def _ruta(self, clave):
        ruta = (self.directorio / clave).resolve()
        if self.directorio.resolve() not in ruta.parents:
            raise ArchivoNoDisponible("Clave de archivo inválida.")
        return ruta

    def guardar(self, clave, contenido, tipo_mime):  # pylint: disable=unused-argument
        """Escribe el archivo tal cual, sin modificarlo (RN23)."""
        ruta = self._ruta(clave)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_bytes(contenido)

    def leer(self, clave):
        """Devuelve el contenido del archivo."""
        return self._ruta(clave).read_bytes()

    def eliminar(self, clave):
        """Elimina el archivo; no hay versiones en la carpeta local."""
        self._ruta(clave).unlink(missing_ok=True)

    def enlace(self, clave, segundos, nombre_descarga=None):
        """Ruta de la API con un token firmado que vence a los ``segundos``."""
        token = self._firmador.dumps(
            {"clave": clave, "nombre": nombre_descarga, "vigencia": segundos}
        )
        return f"/api/archivos/{token}"

    def abrir_enlace(self, token):
        """Valida el token de ``enlace`` y devuelve ``(contenido, nombre_descarga)``.

        Raises:
            ArchivoNoDisponible: si el token venció, fue alterado o el archivo no existe.
        """
        try:
            # La vigencia viaja firmada dentro del token: primero se valida la
            # firma para leerla y después se controla el vencimiento con ella.
            datos = self._firmador.loads(token)
            self._firmador.loads(token, max_age=datos["vigencia"])
        except (BadSignature, SignatureExpired, KeyError, TypeError) as error:
            raise ArchivoNoDisponible("El enlace venció o no es válido.") from error
        ruta = self._ruta(datos["clave"])
        if not ruta.is_file():
            raise ArchivoNoDisponible("El archivo ya no existe.")
        return ruta.read_bytes(), datos.get("nombre")


def disposicion_de_descarga(nombre):
    """Cabecera ``Content-Disposition`` de descarga, con el nombre en UTF-8."""
    return f"attachment; filename*=UTF-8''{quote(nombre)}"


def crear_almacenamiento(configuracion):
    """Elige la implementación según ``ALMACENAMIENTO`` (``"s3"`` o ``"local"``)."""
    if configuracion["ALMACENAMIENTO"] == "s3":
        # Se importa aquí: boto3 tarda en cargar y no hace falta en desarrollo.
        import boto3  # pylint: disable=import-outside-toplevel

        cliente = boto3.client(
            "s3",
            region_name=configuracion["S3_REGION"],
            endpoint_url=configuracion["S3_ENDPOINT"] or None,
        )
        return AlmacenamientoS3(cliente, configuracion["S3_BUCKET"], configuracion["S3_CIFRADO"])
    return AlmacenamientoLocal(
        configuracion["DIRECTORIO_ALMACENAMIENTO"], configuracion["SECRET_KEY"]
    )
