"""Inicio de sesión con Google por OpenID Connect (funcionalidad 027, ADR-0019).

Usa el flujo de código de autorización con PKCE, del lado del servidor:

1. ``url_autorizacion`` arma la dirección de Google con ``state`` (contra la
   falsificación de solicitudes), ``nonce`` (contra la reutilización del
   token) y el desafío PKCE.
2. Google devuelve un código a ``/api/google/retorno``; ``canjear_codigo`` lo
   cambia por el *ID token* en el *token endpoint*, autenticándose con el
   secreto del cliente y el verificador PKCE.
3. ``identidad_del_token`` valida emisor, audiencia, vencimiento y ``nonce``
   y devuelve los datos de la persona.

La firma del *ID token* no se verifica con las claves públicas de Google:
el token llega por una conexión TLS directa con Google, autenticada con el
secreto del cliente, y en ese caso OpenID Connect Core 1.0 (sección
3.1.3.7, punto 6) admite validar el emisor por TLS. Así no se agrega una
biblioteca de JWT.

Realiza: RF52 (CA1, CA2).
"""
import base64
import json
import time
from dataclasses import dataclass
from urllib import error, parse, request

URL_AUTORIZACION = "https://accounts.google.com/o/oauth2/v2/auth"
URL_TOKEN = "https://oauth2.googleapis.com/token"
EMISORES = ("https://accounts.google.com", "accounts.google.com")
RUTA_RETORNO = "/api/google/retorno"
TIEMPO_ESPERA = 10  # segundos
TOLERANCIA_RELOJ = 60  # segundos de diferencia admitida con el reloj de Google


class ErrorGoogle(Exception):
    """Google no respondió o devolvió una identidad que no se puede aceptar."""


@dataclass
class IdentidadGoogle:
    """Datos de la persona que informa Google en el *ID token*."""

    sub: str
    correo: str
    correo_verificado: bool
    nombre: str
    apellido: str


class ClienteGoogle:
    """Cliente OpenID Connect de Google para la plataforma.

    El identificador y el secreto del cliente llegan por la configuración
    (parámetros cifrados de SSM en producción); nunca están en el repositorio.
    """

    def __init__(self, id_cliente, secreto, url_frontend, tiempo_espera=TIEMPO_ESPERA):
        self.id_cliente = id_cliente
        self.secreto = secreto
        # El frontend y la API comparten el dominio: Nginx (o Vite en
        # desarrollo) envía /api al backend.
        self.url_retorno = url_frontend.rstrip("/") + RUTA_RETORNO
        self.tiempo_espera = tiempo_espera

    def url_autorizacion(self, estado, nonce, desafio):
        """Dirección de Google a la que se envía a la persona para autorizar el acceso."""
        parametros = {
            "client_id": self.id_cliente,
            "redirect_uri": self.url_retorno,
            "response_type": "code",
            "scope": "openid email profile",
            "state": estado,
            "nonce": nonce,
            "code_challenge": desafio,
            "code_challenge_method": "S256",
            "prompt": "select_account",
        }
        return f"{URL_AUTORIZACION}?{parse.urlencode(parametros)}"

    def _publicar_formulario(self, url, datos):
        """Envía un formulario por POST y devuelve la respuesta JSON."""
        solicitud = request.Request(
            url, data=parse.urlencode(datos).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "Accept": "application/json"},
        )
        try:
            with request.urlopen(solicitud, timeout=self.tiempo_espera) as respuesta:
                return json.loads(respuesta.read() or b"{}")
        except error.HTTPError as falla:
            raise ErrorGoogle(f"Google rechazó el código: {falla.code}") from falla
        except (error.URLError, TimeoutError, ValueError) as falla:
            raise ErrorGoogle(f"Google no respondió: {falla}") from falla

    def canjear_codigo(self, codigo, verificador, nonce):
        """Cambia el código de autorización por la identidad de la persona.

        Raises:
            ErrorGoogle: si Google rechaza el código o el *ID token* no es válido.
        """
        respuesta = self._publicar_formulario(URL_TOKEN, {
            "code": codigo,
            "client_id": self.id_cliente,
            "client_secret": self.secreto,
            "redirect_uri": self.url_retorno,
            "grant_type": "authorization_code",
            "code_verifier": verificador,
        })
        token_id = respuesta.get("id_token")
        if not token_id:
            raise ErrorGoogle("Google no devolvió el ID token.")
        return self.identidad_del_token(token_id, nonce)

    def identidad_del_token(self, token_id, nonce, ahora=None):
        """Valida el *ID token* recibido de Google y devuelve la identidad.

        Raises:
            ErrorGoogle: emisor, audiencia, vencimiento o ``nonce`` incorrectos.
        """
        datos = _carga_del_token(token_id)
        ahora = time.time() if ahora is None else ahora
        if datos.get("iss") not in EMISORES:
            raise ErrorGoogle("El ID token no lo emitió Google.")
        if datos.get("aud") != self.id_cliente:
            raise ErrorGoogle("El ID token es para otra aplicación.")
        if float(datos.get("exp", 0)) + TOLERANCIA_RELOJ < ahora:
            raise ErrorGoogle("El ID token venció.")
        if not nonce or datos.get("nonce") != nonce:
            raise ErrorGoogle("El nonce del ID token no coincide.")
        if not datos.get("sub") or not datos.get("email"):
            raise ErrorGoogle("El ID token no trae la cuenta o el correo.")
        return IdentidadGoogle(
            sub=str(datos["sub"]),
            correo=str(datos["email"]).strip().lower(),
            correo_verificado=datos.get("email_verified") in (True, "true"),
            nombre=str(datos.get("given_name") or "")[:100],
            apellido=str(datos.get("family_name") or "")[:100],
        )


def _carga_del_token(token_id):
    """Decodifica la parte central (los datos) de un JWT, sin verificar la firma."""
    try:
        carga = token_id.split(".")[1]
        carga += "=" * (-len(carga) % 4)
        datos = json.loads(base64.urlsafe_b64decode(carga))
    except (IndexError, ValueError) as falla:
        raise ErrorGoogle("El ID token no tiene un formato válido.") from falla
    if not isinstance(datos, dict):
        raise ErrorGoogle("El ID token no tiene un formato válido.")
    return datos


def crear_cliente_google(configuracion):
    """El cliente de Google, o None si falta el identificador o el secreto."""
    id_cliente = configuracion.get("GOOGLE_ID_CLIENTE")
    secreto = configuracion.get("GOOGLE_SECRETO_CLIENTE")
    if not id_cliente or not secreto:
        return None
    return ClienteGoogle(id_cliente, secreto, configuracion["URL_FRONTEND"])
