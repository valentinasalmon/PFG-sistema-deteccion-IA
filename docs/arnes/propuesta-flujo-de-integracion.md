# Propuesta: configuración de GitHub para el flujo de integración (pendiente de aprobación de la autora)

Funcionalidad 039, 2026-11-05. El agente no tiene acceso a la configuración del repositorio en GitHub, y dos de los cambios afectan cómo se cuentan los datos del informe: por eso los decide la autora.

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

## 3. Etiquetar cada versión de producción (recomendado)

Hoy hay una sola etiqueta (`v0.1`) para 14 pasos a producción. Dos opciones:
- **Manual**: al integrar `desarrollo` en `main`, `git tag -a v0.N -m "…"` y `git push origin v0.N` (ya está en la guía de flujo de trabajo).
- **Automática**: que el trabajo de despliegue de la integración continua cree la etiqueta después de un despliegue correcto. Requiere darle permiso de escritura al flujo (`permissions: contents: write`) y es un cambio en el camino de producción: el agente lo implementa si la autora lo aprueba.

## 4. Limpieza inicial de ramas (para correr una vez)

La sesión del agente no puede borrar ramas ajenas (el remoto responde 403: solo puede subir a su propia rama). Desde la máquina de la autora, en la raíz del repositorio:

```bash
infraestructura/scripts/limpiar_ramas.sh
```

Muestra qué haría sin tocar nada. Si está de acuerdo:

```bash
infraestructura/scripts/limpiar_ramas.sh --aplicar --archivar
```

Al 2026-11-05 borra 52 ramas integradas o superadas, guarda en etiquetas `archivo/…` las 2 que tenían contenido propio (el sello desde el navegador, abandonado por Hedera, y una corrección de la 024 ya superada) y conserva las ramas con trabajo en curso.

## Cómo aprobarlo

Responder en la sesión o aplicar los pasos 1 y 4 directamente. Al decidir, registrar el resultado en `registro-de-cambios.md` y cambiar la primera línea de este archivo de «pendiente» a «aprobada» o «rechazada».
