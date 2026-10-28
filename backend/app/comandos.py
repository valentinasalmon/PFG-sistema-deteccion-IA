"""Comandos de terminal de la aplicación (``flask administracion ...``).

Son una puerta de entrada como las rutas: solo usan la fábrica de servicios.

Realiza: funcionalidad 021 (alta de administradores fuera de la interfaz).
"""
import click
from flask import current_app
from flask.cli import AppGroup

from app.servicios.contrasenias import validar_politica
from app.servicios.errores import ErrorValidacion, NoEncontrado
from app.servicios.fabrica import (
    crear_servicio_cuentas,
    crear_servicio_sellos,
    crear_servicio_versiones,
    crear_tema_de_sellos,
    crear_tareas_de_retencion,
)

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


CORREO_DE_DEMOSTRACION = "demo@evidentia.local"


@administracion_cli.command("cuenta-de-demostracion")
@click.option("--correo", default=CORREO_DE_DEMOSTRACION, show_default=True)
@click.password_option("--contrasenia", help="Se pide en la terminal si no se indica.")
def cuenta_de_demostracion(correo, contrasenia):
    """Crea o restablece una abogada de demostración, sin rol de Administrador (028).

    Sirve para mostrar la plataforma, también en producción: no trae ninguna
    contraseña fija, se escribe en la terminal y tiene que cumplir la política.
    """
    try:
        validar_politica(contrasenia)
    except ErrorValidacion as error:
        raise click.ClickException(error.errores.get("contrasenia", error.mensaje)) from error
    servicio = crear_servicio_cuentas(current_app.config, current_app.extensions["enviador_correo"])
    usuario = servicio.preparar_cuenta_de_prueba(
        correo, contrasenia, administradora=False, nombre=("Lucía", "Demo"),
        estudio="Estudio de demostración evidentIA",
    )
    click.echo(f"Cuenta lista: {usuario.correo} (Abogada, sin rol de Administrador).")


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


sellos_cli = AppGroup("sellos", help="Sello de tiempo en Hedera (funcionalidad 023).")


@sellos_cli.command("procesar")
def procesar_sellos():
    """Pide y confirma los sellos pendientes. La ejecuta un timer cada 15 minutos (RF37 CA3)."""
    resultado = crear_servicio_sellos(current_app.config).procesar()
    click.echo(f"Sellos: {resultado['sellados']} sellado(s), {resultado['en_curso']} en curso.")


@sellos_cli.command("registrar-version")
@click.option("--commit", required=True, help="Commit desplegado (40 caracteres).")
@click.option("--huella", required=True, help="SHA-256 del artefacto desplegado.")
def registrar_version(commit, huella):
    """Registra la versión desplegada y sella su huella en Hedera (029). Lo llama desplegar.sh."""
    try:
        version = crear_servicio_versiones(current_app.config).registrar(commit, huella)
    except ErrorValidacion as error:
        raise click.ClickException(error.mensaje) from error
    estado = version.sello_estado or "desactivado"
    click.echo(f"Versión {version.version} ({commit[:7]}): sello {estado}.")


@sellos_cli.command("crear-tema")
@click.option(
    "--red", type=click.Choice(["testnet", "mainnet"]), default="testnet", show_default=True
)
@click.option("--cuenta", prompt="Account ID de Hedera (0.0.…)", help="Cuenta que paga y publica.")
def crear_tema(red, cuenta):
    """Crea el tema de Hedera de la plataforma; se ejecuta una sola vez por red.

    La clave privada se pide sin mostrarla en pantalla, para que no quede en el
    historial de la terminal ni en ningún archivo.
    """
    clave = click.prompt("Clave privada (no se muestra)", hide_input=True)
    try:
        tema = crear_tema_de_sellos(red, cuenta, clave)
    except Exception as falla:  # pylint: disable=broad-exception-caught
        raise click.ClickException(f"No se pudo crear el tema: {falla}") from falla
    click.echo(f"Tema creado en {red}: {tema}")


def registrar_comandos(aplicacion):
    """Registra los grupos de comandos en la aplicación."""
    aplicacion.cli.add_command(administracion_cli)
    aplicacion.cli.add_command(retencion_cli)
    aplicacion.cli.add_command(sellos_cli)
