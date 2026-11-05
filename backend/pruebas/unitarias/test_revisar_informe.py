"""Pruebas del revisor automático del informe final (funcionalidad 039)."""
from herramientas import revisar_informe as revisor

INFORME = """Resumen
El sistema analiza imágenes. Se realizó una encuesta (Köbis et al., 2021).
# **CAPÍTULO I - DEFINICIÓN DEL PROYECTO**
## **Origen**
El proyecto se origina en Corrientes (Porter, 2018) y en la Tabla 1 se resume.
## **Vacía**
## **Otra**
- un ítem que no debería estar
##### **Tabla 1.** Componentes
| a | b |
*Nota. Elaboración propia.*
##### **Tabla 3.** Salteada
| a | b |
Este párrafo largo se repite exactamente igual en dos lugares distintos del informe y por eso \
tiene que aparecer como duplicado cuando el revisor lo compara con el resto del texto del cuerpo, \
porque un evaluador lo marcaría enseguida.
Este párrafo largo se repite exactamente igual en dos lugares distintos del informe y por eso \
tiene que aparecer como duplicado cuando el revisor lo compara con el resto del texto del cuerpo, \
porque un evaluador lo marcaría enseguida.
El costo es [completar] y la imagen es falsa según EvidentIA.
# **CAPÍTULO III: ENTORNO**
Texto.
# **Bibliografía**
Köbis, N. C., & Soraperra, I. (2021). Fooled twice. iScience.
Anderson, D. J. (2010). Kanban. Blue Hole Press.
"""


def reglas(severidad=None):
    """Reglas encontradas en el informe de ejemplo."""
    return {h.regla for h in revisor.revisar(INFORME) if severidad in (None, h.severidad)}


def test_detecta_los_errores_estructurales():
    """Sección vacía, duplicado, capítulo salteado y tabla salteada son errores."""
    errores = reglas(revisor.ERROR)
    assert {"Sección vacía", "Párrafo duplicado", "Numeración de capítulos",
            "Numeración de tablas", "Marcador sin completar",
            "Redacción de veredicto"} <= errores


def test_detecta_citas_y_bibliografia():
    """Cita sin entrada, entrada sin citar, desorden y «&» en la bibliografía."""
    encontradas = reglas()
    assert "Cita sin entrada en la bibliografía" in encontradas      # Porter (2018)
    assert "Entrada de la bibliografía sin citar" in encontradas     # Anderson (2010)
    assert "Bibliografía fuera de orden" in encontradas
    assert "Conector de autores" in encontradas


def test_detecta_redaccion():
    """Pasado, viñetas, término mal escrito y tabla sin nota."""
    encontradas = reglas()
    assert {"Tiempo verbal", "Lista con viñetas", "Término", "Tabla sin nota"} <= encontradas


def test_un_informe_correcto_no_tiene_errores():
    """Un texto prolijo pasa sin errores."""
    texto = ("Resumen\nEl sistema se describe (Anderson, 2010).\n"
             "# **CAPÍTULO I - DEFINICIÓN DEL PROYECTO**\nTexto del capítulo.\n"
             "# **Bibliografía**\nAnderson, D. J. (2010). Kanban. Blue Hole Press.\n")
    errores = [h for h in revisor.revisar(texto) if h.severidad == revisor.ERROR
               and h.regla != "Capítulos faltantes"]
    assert errores == []


def test_la_linea_de_comandos_devuelve_1_con_errores(tmp_path, capsys):
    """El código de salida permite usarlo como control."""
    archivo = tmp_path / "informe.txt"
    archivo.write_text(INFORME, encoding="utf-8")
    assert revisor.main([str(archivo)]) == 1
    assert "Revisión automática del informe" in capsys.readouterr().out
