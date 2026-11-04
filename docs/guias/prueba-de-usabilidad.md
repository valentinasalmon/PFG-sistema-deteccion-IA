# Protocolo de la prueba de usabilidad

Guion para que la autora haga la prueba de usabilidad del cierre (funcionalidad 018). Demuestra RNF10 CA1: una persona del dominio, sin capacitación, completa el flujo principal sin ayuda, con al menos **5 participantes** y **80 % de éxito**. El puntaje SUS promedio se suma al Índice de Calidad ([QI](../calidad/indice-de-calidad.md)).

## 1. Participantes

| Perfil | Cantidad | Cómo conseguirlos |
|---|---|---|
| Abogados o abogadas que trabajen con siniestros o daños | 3 o más | Contactos del estudio entrevistado (2026-10-02) y colegas de la facultad |
| Personal de aseguradoras (liquidación, siniestros) | 2 o más | Contactos de la industria |

- Ninguno usó la plataforma antes ni vio demostraciones.
- 5 participantes alcanzan para detectar la mayoría de los problemas (Nielsen y Landauer, 1993). Si hay tiempo, conviene llegar a 8.

## 2. Preparación (una vez)

1. Usar **producción** (la versión que se entrega), no la máquina local.
2. Crear una cuenta de prueba por participante, o pedirle que se registre si la tarea 1 incluye el registro.
3. Tener 3 fotos de ejemplo **que no sean de casos reales** (por ejemplo, de un auto propio o de bancos de imágenes con licencia libre). Copiarlas al celular del participante si se prueba la carga desde el celular.
4. Imprimir esta planilla y el consentimiento, o tenerlos en una tableta.
5. Si se graba la pantalla, pedirlo en el consentimiento.

## 3. Consentimiento (leer y firmar antes de empezar)

> Te invito a probar evidentIA, una plataforma que forma parte de mi Proyecto Final de Grado. Lo que se evalúa es la plataforma, no a vos: si algo no sale, es un problema del diseño.
>
> La prueba dura unos 30 minutos. Te voy a pedir que hagas algunas tareas y que digas en voz alta lo que pensás mientras las hacés. Al final completás un cuestionario corto.
>
> Tus respuestas se usan solo para el proyecto, sin tu nombre. Las imágenes son de ejemplo: no vas a cargar datos reales. Podés dejar la prueba cuando quieras.
>
> [ ] Acepto participar. [ ] Acepto que se grabe la pantalla (opcional).
>
> Firma: ____________ Fecha: ____________

## 4. Guion

**Antes de las tareas (2 minutos):**
- «Pensá en voz alta: contame qué buscás, qué esperás que pase y si algo te sorprende.»
- «No te puedo ayudar durante las tareas. Si te trabás mucho, decímelo y pasamos a la siguiente.»

**Durante:** no explicar ni señalar. Si pregunta algo, responder «¿Qué harías si yo no estuviera?». Anotar el tiempo, los errores y las frases textuales.

**Corte:** una tarea se da por **fallida** si pasan 5 minutos sin avanzar, si la persona se rinde o si termina con un resultado incorrecto.

## 5. Tareas

Leer cada consigna tal cual. No usar las palabras de los botones.

| # | Consigna para el participante | Éxito cuando… | Tiempo esperado |
|---|---|---|---|
| T1 | «Ingresá a la plataforma con la cuenta que te di.» (o «Creá una cuenta como abogado/a») | Ve la pantalla de inicio | 1 min (3 min con registro) |
| T2 | «Tenés un siniestro de un auto. Registralo en la plataforma.» | Hay un caso nuevo con un título reconocible | 2 min |
| T3 | «Sumá al siniestro las tres fotos que te pasé.» | Las tres imágenes figuran en el caso | 2 min |
| T4 | «Averiguá si alguna de las fotos podría estar modificada.» | Inicia el análisis y llega a ver los resultados | 3 min |
| T5 | «Explicame con tus palabras qué dice el resultado de la segunda foto.» | Describe los indicios sin decir que la foto es «falsa» o «verdadera» con certeza | 2 min |
| T6 | «Conseguí un documento para presentar con este análisis.» | Descarga el informe PDF | 2 min |
| T7 | «Otra persona te mandó este informe. Comprobá que nadie lo modificó.» | Usa la verificación pública y ve el resultado | 2 min |
| T8 (opcional) | «Cargá una foto nueva desde tu celular.» | La imagen aparece en el caso | 3 min |

T5 comprueba RN27: la persona entiende que son indicios y no un veredicto.

## 6. Planilla de registro (una por participante)

Participante: P__ · Perfil: abogado/a ☐ aseguradora ☐ · Fecha: ____ · Dispositivo: ____

| Tarea | Éxito (sí / con dificultad / no) | Tiempo | Errores | Comentarios textuales |
|---|---|---|---|---|
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |
| T4 | | | | |
| T5 | | | | |
| T6 | | | | |
| T7 | | | | |
| T8 | | | | |

«Con dificultad» cuenta como éxito para la tasa, pero se anota para el análisis.

## 7. Cuestionario SUS (al terminar)

Para cada frase, marcar de **1 (totalmente en desacuerdo)** a **5 (totalmente de acuerdo)**. Responder rápido, sin pensar demasiado.

| # | Frase | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| 1 | Creo que me gustaría usar esta plataforma con frecuencia. | | | | | |
| 2 | Encontré la plataforma innecesariamente compleja. | | | | | |
| 3 | Me pareció fácil de usar. | | | | | |
| 4 | Creo que necesitaría la ayuda de una persona con conocimientos técnicos para usarla. | | | | | |
| 5 | Las distintas funciones de la plataforma están bien integradas. | | | | | |
| 6 | Encontré demasiadas inconsistencias en la plataforma. | | | | | |
| 7 | Imagino que la mayoría de las personas aprendería a usarla muy rápido. | | | | | |
| 8 | La encontré muy incómoda de usar. | | | | | |
| 9 | Me sentí muy seguro/a al usar la plataforma. | | | | | |
| 10 | Tuve que aprender muchas cosas antes de poder usarla. | | | | | |

Adaptación al español de la escala de Brooke (1996), con «sistema» reemplazado por «plataforma».

**Cálculo del puntaje (0 a 100):** a cada frase impar se le resta 1; a 5 se le resta cada frase par; la suma se multiplica por 2,5. Lo calcula la función `puntaje_sus` de `backend/herramientas/indice_calidad.py`.

**Cómo se lee:** 68 es el promedio de referencia; 80 o más es muy bueno; menos de 50 indica problemas serios.

## 8. Preguntas finales (2 minutos)

1. ¿Qué fue lo más difícil?
2. ¿Qué cambiarías primero?
3. ¿Usarías esta plataforma en tu trabajo? ¿Por qué?

## 9. Resultados

| Indicador | Cálculo | Objetivo |
|---|---|---|
| Tasa de éxito | Tareas exitosas / tareas intentadas (T1 a T7) | 80 % o más (RNF10 CA1) |
| SUS promedio | Promedio de los puntajes de los participantes | 68 o más |
| Tiempo por tarea | Mediana | Dentro del esperado |
| Problemas | Lista con la frecuencia y la gravedad (alta, media, baja) | Corregir los de gravedad alta antes de la entrega |

Con el SUS promedio se calcula el QI final:

```bash
python herramientas/indice_calidad.py --cobertura-backend coverage.json \
    --cobertura-frontend ../frontend/coverage/coverage-summary.json --sus <promedio>
```

Los resultados van a `docs/informe-final/insumos.md` y las planillas escaneadas a una carpeta privada, **no al repositorio**: tienen firmas.
