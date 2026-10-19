"""Comandos de terminal de la aplicación (``flask administracion ...``).

Son una puerta de entrada como las rutas: solo usan la fábrica de servicios.

Realiza: funcionalidad 021 (alta de administradores fuera de la interfaz).
"""
import click
from flask import current_app
from flask.cli import AppGroup

from app.servicios.errores import NoEncontrado
from app.servicios.fabrica import crear_servicio_cuentas

administracion_cli = AppGroup("administracion", help="Tareas del Administrador de la plataforma.")


@administracion_cli.command("promover")
@click.argument("correo")
def promover(correo):
    """Da el rol de Administrador a la cuenta verificada con CORREO."""
    servicio = crear_servicio_cuentas(current_app.config, current_app.extensions["enviador_correo"])
    try:
        usuario = servicio.promover_administrador(correo)
    except NoEncontrado as error:
        raise click.ClickException(error.mensaje) from error
    click.echo(f"{usuario.nombre} {usuario.apellido} ({usuario.correo}) es Administrador.")


def registrar_comandos(aplicacion):
    """Registra los grupos de comandos en la aplicación."""
    aplicacion.cli.add_command(administracion_cli)
