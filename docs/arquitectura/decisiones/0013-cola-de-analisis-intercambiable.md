# ADR-0013: Cola de análisis intercambiable (RQ, hilo y sincrónica)

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Requisitos relacionados**: RF38, RF46, RNF13, RNF18, RNF22; complementa ADR-0004

## Contexto

ADR-0004 decide procesar los análisis con RQ y un proceso trabajador. En producción es lo correcto. Pero en el desarrollo obliga a levantar un trabajador en otra terminal, y si se olvida, los análisis quedan en cola sin avisar. En las pruebas automatizadas, depender de Redis y de un trabajador las vuelve lentas y frágiles.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| RQ en todos los entornos | Un solo camino | En el desarrollo hay que acordarse del trabajador; las pruebas necesitan Redis |
| Ejecutar el análisis dentro de la solicitud fuera de producción | Simple | La pantalla no muestra el progreso; no se parece a producción |
| Interfaz común con tres implementaciones | Cada entorno usa lo adecuado; el código del análisis es el mismo | Tres implementaciones pequeñas que mantener |

## Decisión

La cola tiene una interfaz `encolar(funcion, *argumentos)` con tres implementaciones, elegidas con `COLA_ANALISIS` (patrón Strategy):

- **`rq`** (producción, obligatoria): encola en Redis y lo ejecuta el trabajador (`backend/trabajador.py`).
- **`hilo`** (desarrollo, por defecto): ejecuta el trabajo en un hilo aparte, con su propio contexto de aplicación. La solicitud responde enseguida y la pantalla muestra el progreso real.
- **`sincronica`** (pruebas): ejecuta el trabajo en el momento, para que las pruebas sean deterministas.

El servicio confirma el análisis en la base **antes** de encolarlo. Un análisis que deja de avanzar durante `TIEMPO_MAXIMO_SIN_AVANCE` se marca como Fallido en la siguiente consulta, sea cual sea la cola (RF46 CA2).

## Consecuencias

- En el desarrollo no hace falta un trabajador aparte. Para probar el camino real: `COLA_ANALISIS=rq` y `python trabajador.py`.
- La lógica del análisis (`ServicioAnalisis.procesar`) no sabe qué cola la ejecuta.
- El hilo de desarrollo no sobrevive a un reinicio del servidor. Ese análisis queda Fallido por falta de avance, como pasaría con una caída del trabajador.
