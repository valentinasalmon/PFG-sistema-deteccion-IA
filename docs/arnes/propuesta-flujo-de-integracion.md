# Propuesta: configuración de GitHub para el flujo de integración (pendiente de aprobación de la autora)

Funcionalidad 045, 2026-11-05. El agente no tiene acceso a la configuración del repositorio en GitHub, y dos de los cambios afectan cómo se cuentan los datos del informe: por eso los decide la autora.

## 1. Borrar la rama al integrar (recomendado, sin contras)

**Qué**: *Settings* → *General* → *Pull Requests* → marcar **Automatically delete head branches**.

**Por qué**: la guía ya decía que la rama se borra al integrar y no se hacía; quedaron 51 ramas integradas vivas. Con esta opción GitHub la borra sola al integrar el Pull Request, y desde la página del Pull Request se puede restaurar si hiciera falta.

## 2. Integrar las funcionalidades con *squash* (a decidir)

**Qué**: *Settings* → *General* → *Pull Requests* → dejar habilitado **Allow squash merging** y usarlo para los Pull Requests de funcionalidad, corrección y documentación hacia `desarrollo`. El paso de `desarrollo` a `main` sigue con *merge*.

| A favor | En contra |
|---|---|
| `desarrollo` queda con un commit por funcionalidad: historial legible y fácil de revertir | Los commits individuales quedan solo en el Pull Request de GitHub, no en la historia de `desarrollo` |
| Desaparecen los commits de seguimiento sueltos y los merges «traer desarrollo» | **Cambian las métricas del informe**: la cantidad de commits y el porcentaje con co-autoría de IA bajarían a uno por Pull Request (GitHub conserva las líneas `Co-Authored-By` en el commit unificado) |

**Recomendación del agente**: aplicarlo **después de la entrega**, o desde ya si la autora prefiere un historial limpio; en ese caso, las métricas del informe se citan «al 2026-11-05» o se cuentan por Pull Request.

## 3. Etiquetas de versión (ya resuelto)

`docs/versiones.md` fija que la versión se etiqueta al completar un hito y que la etiqueta la crea la autora. Quedan sin etiquetar la v0.2 y la v0.3 (hitos alcanzados). La política de la 045 se alineó con eso: el paso de `desarrollo` a `main` es por hito o por una corrección urgente, no después de cada funcionalidad.

## 4. Limpieza inicial de ramas (para correr una vez)

La sesión del agente no puede borrar ramas ajenas (el remoto responde 403: solo puede subir a su propia rama). Desde la máquina de la autora, en la raíz del repositorio:

```bash
infraestructura/scripts/limpiar_ramas.sh
```

Muestra qué haría sin tocar nada. Si está de acuerdo:

```bash
infraestructura/scripts/limpiar_ramas.sh --aplicar --archivar
```

Al 2026-11-16 borra 58 ramas integradas o superadas, guarda en etiquetas `archivo/…` las 2 abandonadas con contenido propio (el sello desde el navegador, reemplazado por Hedera, y una corrección de la 024 ya superada) y conserva las ramas con trabajo en curso o con cambios sin integrar de otras sesiones.

## Cómo aprobarlo

Responder en la sesión o aplicar los pasos 1 y 4 directamente. Al decidir, registrar el resultado en `registro-de-cambios.md` y cambiar la primera línea de este archivo de «pendiente» a «aprobada» o «rechazada».
