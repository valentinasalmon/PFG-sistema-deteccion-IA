"""Comandos de terminal de la aplicación (``flask administracion ...``).

Son una puerta de entrada como las rutas: solo usan la fábrica de servicios.

Realiza: funcionalidad 021 (alta de administradores fuera de la interfaz).
"""
import click
from flask import current_app
from flask.cli import AppGroup

from app.servicios.errores import NoEncontrado
from app.servicios.fabrica import crear_servicio_cuentas, crear_tareas_de_retencion

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


CORREO_DE_PRUEBA = "prueba@evidentia.local"
CONTRASENIA_DE_PRUEBA = "Prueba12345"


@administracion_cli.command("cuenta-de-prueba")
@click.option("--correo", default=CORREO_DE_PRUEBA, show_default=True)
@click.option("--contrasenia", default=CONTRASENIA_DE_PRUEBA, show_default=True)
def cuenta_de_prueba(correo, contrasenia):
    """Crea o restablece una cuenta verificada y Administradora para probar todo.

    Solo funciona fuera de producción: en el servidor real las cuentas se crean
    desde el registro y los administradores con ``promover``.
    """
    if current_app.config.get("NOMBRE") == "produccion":
        raise click.ClickException("La cuenta de prueba no se puede crear en producción.")
    servicio = crear_servicio_cuentas(current_app.config, current_app.extensions["enviador_correo"])
    usuario = servicio.preparar_cuenta_de_prueba(correo, contrasenia)
    click.echo(f"Cuenta lista: {usuario.correo} / {contrasenia} (Abogado, Administrador).")


retencion_cli = AppGroup("retencion", help="Retención de los casos (funcionalidad 015).")


@retencion_cli.command("procesar")
def procesar_retencion():
    """Avisa a 30 días y destruye los casos vencidos. La ejecuta un timer diario (RF49, RF50)."""
    tareas = crear_tareas_de_retencion(
        current_app.config, current_app.extensions["enviador_correo"],
        current_app.extensions.get("almacenamiento"),
    )
    resultado = tareas.procesar()
    click.echo(
        f"Retención: {resultado['avisados']} aviso(s), "
        f"{resultado['destruidos']} caso(s) destruido(s)."
    )


def registrar_comandos(aplicacion):
    """Registra los grupos de comandos en la aplicación."""
    aplicacion.cli.add_command(administracion_cli)
    aplicacion.cli.add_command(retencion_cli)
