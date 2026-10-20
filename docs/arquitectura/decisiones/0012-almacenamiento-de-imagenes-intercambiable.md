# ADR-0012: Almacenamiento de imágenes intercambiable (S3 y carpeta local)

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Requisitos relacionados**: RF34 – RF36, RNF03, RNF09, RNF18, RNF22; RN21, RN23

## Contexto

Las imágenes de los casos son la evidencia: no pueden modificarse, solo deben verlas quienes tienen permiso y, al eliminarse un caso, deben borrarse con todas sus versiones. En producción van a un bucket de S3 privado, cifrado y versionado (RNF03). En el desarrollo, en WSL2 (ADR-0009), y en las pruebas automatizadas, depender de AWS o de otro contenedor agrega costo y fragilidad.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| S3 en todos los entornos | Un solo camino | Requiere cuenta y credenciales de AWS para desarrollar y probar |
| MinIO (S3 compatible) en `docker compose` para el desarrollo | Misma API que producción | Otro contenedor; los enlaces apuntan a otro puerto y suman configuración |
| Interfaz común con dos implementaciones (S3 y carpeta local) | El desarrollo y las pruebas no dependen de nada externo; S3 se prueba con `moto` | Dos implementaciones que mantener |

## Decisión

Se define una interfaz de almacenamiento (`guardar`, `leer`, `eliminar` y `enlace`) con dos implementaciones elegidas por configuración (patrón Strategy, como el correo):

- **`AlmacenamientoS3`** (producción): sube el original sin modificarlo con cifrado del lado del servidor y, al eliminar, borra todas las versiones del objeto. Los enlaces son URL prefirmadas.
- **`AlmacenamientoLocal`** (desarrollo y pruebas): guarda en una carpeta que está en `.gitignore`. Los enlaces son tokens firmados con vencimiento que sirve la ruta `/api/archivos/<token>`.

En ambos casos:
- Los enlaces vencen a los 5 minutos.
- Las claves de los archivos son aleatorias y no contienen datos personales (RNF09 CA2).
- Los archivos se escriben antes de confirmar la base y se borran después de confirmarla. Si la base falla, se borran los archivos recién escritos. Si falla un borrado, queda en el log y la operación no se cae.

## Consecuencias

- El desarrollo no necesita instalar nada nuevo. Las pruebas no usan la red: la carpeta local es temporal y S3 se simula con `moto`.
- Producción exige `S3_BUCKET` y siempre usa S3, aunque la variable `ALMACENAMIENTO` diga otra cosa.
- La creación del bucket con cifrado, versionado y bloqueo de acceso público queda para la infraestructura (funcionalidad 017, Terraform).
- El análisis (funcionalidad 007) lee los originales con `leer`, sin depender de dónde están guardados.
