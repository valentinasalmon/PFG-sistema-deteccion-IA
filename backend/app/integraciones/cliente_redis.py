"""Adaptador mínimo para Redis.

En esta funcionalidad solo verifica la conexión; a partir de la
funcionalidad 007 Redis se usa como cola de tareas (ADR-0004).
"""
import redis


class ClienteRedis:
    """Envuelve el cliente de la biblioteca ``redis``."""

    TIEMPO_ESPERA_SEGUNDOS = 2

    def __init__(self, url):
        """Guarda la URL de conexión, sin conectarse todavía.

        Args:
            url: cadena de conexión, por ejemplo ``redis://localhost:6379/0``.
        """
        self.url = url

    def verificar_conexion(self):
        """Envía un PING a Redis.

        Returns:
            True si Redis respondió; False si no está disponible.
        """
        try:
            cliente = redis.Redis.from_url(
                self.url,
                socket_connect_timeout=self.TIEMPO_ESPERA_SEGUNDOS,
                socket_timeout=self.TIEMPO_ESPERA_SEGUNDOS,
            )
            return bool(cliente.ping())
        except redis.RedisError:
            return False