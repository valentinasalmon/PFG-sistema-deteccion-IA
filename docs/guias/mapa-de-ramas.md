# Mapa de ramas

Cómo evolucionó el código, agrupado por área (decisión del 2026-11-16; ver [flujo de trabajo](flujo-de-trabajo.md)). Cada rama ya integrada se conserva como **etiqueta** `archivo/<área>/<nombre>`: con `git switch --detach archivo/...` se ve el código exacto de ese momento, y el Pull Request guarda la revisión y la integración continua.

La trazabilidad completa es: requisito (`docs/especificacion/`) → funcionalidad (`docs/funcionalidades/NNN-…`) → rama → Pull Request → versión (`docs/versiones.md`).

## Ramas vivas

| Rama | Qué es |
|---|---|
| `main` | Producción (`evidentiaa.com.ar`) y etiquetas de versión |
| `desarrollo` | Integración |
| `interfaz/calidad-visual` | En curso: portada, identidad simulada, sensor de composición, galería y auditoría visual |
| `funcionalidad/010-red-neuronal` | Entrenamiento de la red (sesión de la red neuronal) |
| `funcionalidad/012-capa-4-activacion` | Activación de la capa 4 cuando se publique el modelo |
| `claude/…` | Ramas de trabajo de otras sesiones del agente (por ejemplo, la del informe) |

## Plataforma (18)

Funcionalidades del producto: cuentas, organizaciones, casos, imágenes, análisis (capas 1 a 3), informes, panel, planes, retención y baja.

| Rama original | Fecha | Pull Request | Etiqueta |
|---|---|---|---|
| `funcionalidad/003-auditoria` | 2026-10-16 | [#5](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/5) | `archivo/plataforma/003-auditoria` |
| `funcionalidad/004-organizaciones` | 2026-10-16 | [#6](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/6) | `archivo/plataforma/004-organizaciones` |
| `funcionalidad/020-registro-por-pasos` | 2026-10-16 | [#4](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/4) | `archivo/plataforma/020-registro-por-pasos` |
| `funcionalidad/021-administrador-inicial` | 2026-10-16 | [#8](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/8) | `archivo/plataforma/021-administrador-inicial` |
| `funcionalidad/021-organizaciones-de-aseguradoras` | 2026-10-16 | [#7](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/7) | `archivo/plataforma/021-organizaciones-de-aseguradoras` |
| `funcionalidad/005-casos` | 2026-10-19 | [#9](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/9) | `archivo/plataforma/005-casos` |
| `funcionalidad/006-imagenes` | 2026-10-19 | [#11](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/11) | `archivo/plataforma/006-imagenes` |
| `funcionalidad/007-motor-de-analisis` | 2026-10-19 | [#12](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/12) | `archivo/plataforma/007-motor-de-analisis` |
| `funcionalidad/008-informe-pdf` | 2026-10-19 | [#13](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/13) | `archivo/plataforma/008-informe-pdf` |
| `funcionalidad/009-capa-c2pa` | 2026-10-19 | [#15](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/15) | `archivo/plataforma/009-capa-c2pa` |
| `funcionalidad/019-baja-de-cuenta` | 2026-10-19 | [#10](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/10) | `archivo/plataforma/019-baja-de-cuenta` |
| `funcionalidad/011-capa-ela` | 2026-10-20 | [#19](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/19) | `archivo/plataforma/011-capa-ela` |
| `funcionalidad/013-panel-y-notificaciones` | 2026-10-21 | [#21](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/21) | `archivo/plataforma/013-panel-y-notificaciones` |
| `funcionalidad/014-planes-y-tablero` | 2026-10-21 | [#23](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/23) | `archivo/plataforma/014-planes-y-tablero` |
| `funcionalidad/015-retencion` | 2026-10-21 | [#24](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/24) | `archivo/plataforma/015-retencion` |
| `correccion/025-informe-detallado` | 2026-10-26 | [#39](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/39) | `archivo/plataforma/correccion-025-informe-detallado` |
| `funcionalidad/024-carga-desde-celular` | 2026-10-26 | [#35](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/35) | `archivo/plataforma/024-carga-desde-celular` |
| `funcionalidad/025-informe-por-rubro` | 2026-10-26 | [#37](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/37) | `archivo/plataforma/025-informe-por-rubro` |

## Interfaz (17)

Rediseño, portada, pulido de UX en tandas, acceso, pantallas a lo ancho, accesibilidad y sensores visuales.

| Rama original | Fecha | Pull Request | Etiqueta |
|---|---|---|---|
| `correccion/022-quitar-muestra-acceso` | 2026-10-21 | [#31](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/31) | `archivo/interfaz/correccion-022-quitar-muestra-acceso` |
| `funcionalidad/022-rediseno-interfaz` | 2026-10-21 | [#22](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/22) | `archivo/interfaz/022-rediseno-interfaz` |
| `recursos/marca-evidentia` | 2026-10-21 | integrada con otra rama | `archivo/interfaz/recursos-marca-evidentia` |
| `funcionalidad/028-mejoras-interfaz` | 2026-10-28 | [#47](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/47) | `archivo/interfaz/028-mejoras-interfaz` |
| `funcionalidad/028-tercera-tanda` | 2026-10-29 | [#50](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/50) | `archivo/interfaz/028-tercera-tanda` |
| `funcionalidad/033-portada` | 2026-10-29 | [#52](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/52) | `archivo/interfaz/033-portada` |
| `funcionalidad/034-pulido-ux` | 2026-10-29 | [#53](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/53) | `archivo/interfaz/034-pulido-ux` |
| `funcionalidad/034-pulido-ux-segunda-tanda` | 2026-10-30 | [#60](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/60) | `archivo/interfaz/034-pulido-ux-segunda-tanda` |
| `funcionalidad/034-portada-nueva` | 2026-10-31 | [#64](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/64) | `archivo/interfaz/034-portada-nueva` |
| `funcionalidad/034-cuarta-tanda` | 2026-11-02 | [#65](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/65) | `archivo/interfaz/034-cuarta-tanda` |
| `funcionalidad/034-quinta-tanda` | 2026-11-02 | [#67](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/67) | `archivo/interfaz/034-quinta-tanda` |
| `funcionalidad/037-acceso-y-pantallas` | 2026-11-05 | [#82](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/82) | `archivo/interfaz/037-acceso-y-pantallas` |
| `funcionalidad/038-acceso-compacto` | 2026-11-09 | [#87](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/87) | `archivo/interfaz/038-acceso-compacto` |
| `funcionalidad/039-correcciones-produccion` | 2026-11-11 | [#89](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/89) | `archivo/interfaz/039-correcciones-produccion` |
| `funcionalidad/041-accesibilidad-wcag` | 2026-11-16 | [#94](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/94) | `archivo/interfaz/041-accesibilidad-wcag` |
| `funcionalidad/043-teclado-y-dns` | 2026-11-16 | [#95](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/95) | `archivo/interfaz/043-teclado-y-dns` |
| `funcionalidad/044-portada-y-identidad` | 2026-11-16 | integrada con otra rama | `archivo/interfaz/044-portada-y-identidad` |

## Hedera (10)

Sello de tiempo: primero Blockchain Federal Argentina (016, reemplazada) y después Hedera (023), informe verificable (026) y versión desplegada (029).

| Rama original | Fecha | Pull Request | Etiqueta |
|---|---|---|---|
| `correccion/016-sello-tsa2` | 2026-10-21 | [#28](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/28) | `archivo/hedera/correccion-016-sello-tsa2` |
| `correccion/016-sello-tsaapi` | 2026-10-21 | [#29](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/29) | `archivo/hedera/correccion-016-sello-tsaapi` |
| `correccion/016-sello-verificacion` | 2026-10-21 | [#30](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/30) | `archivo/hedera/correccion-016-sello-verificacion` |
| `funcionalidad/016-sello-bfa` | 2026-10-21 | [#26](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/26) | `archivo/hedera/016-sello-bfa` |
| `funcionalidad/016-sello-desde-navegador` | 2026-10-21 | integrada con otra rama | `archivo/hedera/016-sello-desde-navegador` |
| `documentacion/hedera-celular-e-informe-final` | 2026-10-25 | [#33](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/33) | `archivo/hedera/documentacion-hedera-celular-e-informe-final` |
| `documentacion/plan-hedera-y-cierre` | 2026-10-25 | integrada con otra rama | `archivo/hedera/documentacion-plan-hedera-y-cierre` |
| `funcionalidad/023-sello-hedera` | 2026-10-25 | [#34](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/34) | `archivo/hedera/023-sello-hedera` |
| `correccion/sello-antes-del-informe` | 2026-11-02 | [#71](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/71) | `archivo/hedera/correccion-sello-antes-del-informe` |
| `documentacion/prueba-hedera-testnet` | 2026-11-02 | [#72](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/72) | `archivo/hedera/documentacion-prueba-hedera-testnet` |

## Integraciones (6)

Servicios externos: Google (027), Clarity (031), cobro con Cresium (032) e identidad con Identik (035).

| Rama original | Fecha | Pull Request | Etiqueta |
|---|---|---|---|
| `documentacion/027-prueba-local` | 2026-10-26 | integrada con otra rama | `archivo/integraciones/documentacion-027-prueba-local` |
| `funcionalidad/027-inicio-con-google` | 2026-10-26 | [#42](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/42) | `archivo/integraciones/027-inicio-con-google` |
| `funcionalidad/032-pago-en-el-registro` | 2026-10-29 | [#51](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/51) | `archivo/integraciones/032-pago-en-el-registro` |
| `correccion/024-027-pendientes` | 2026-10-30 | [#54](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/54) | `archivo/integraciones/correccion-024-027-pendientes` |
| `funcionalidad/031-clarity` | 2026-10-30 | [#61](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/61) | `archivo/integraciones/031-clarity` |
| `funcionalidad/035-identidad-aseguradoras` | 2026-11-04 | [#80](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/80) | `archivo/integraciones/035-identidad-aseguradoras` |

## Infraestructura (5)

AWS con Terraform (017), seguridad (030), integración continua y dominio propio (040).

| Rama original | Fecha | Pull Request | Etiqueta |
|---|---|---|---|
| `funcionalidad/017-infraestructura-aws` | 2026-10-19 | [#16](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/16) | `archivo/infraestructura/017-infraestructura-aws` |
| `correccion/017-despliegue-oidc` | 2026-10-20 | [#18](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/18) | `archivo/infraestructura/correccion-017-despliegue-oidc` |
| `correccion/integracion-continua` | 2026-10-26 | [#41](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/41) | `archivo/infraestructura/correccion-integracion-continua` |
| `funcionalidad/030-seguridad` | 2026-10-26 | [#43](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/43) | `archivo/infraestructura/030-seguridad` |
| `funcionalidad/040-dominio-propio` | 2026-11-13 | [#91](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/91) | `archivo/infraestructura/040-dominio-propio` |

## Documentacion (5)

Cierre y materiales (018), arnés del agente de IA (036), kit de usabilidad (042) y decisiones de alcance.

| Rama original | Fecha | Pull Request | Etiqueta |
|---|---|---|---|
| `documentacion/decisiones-de-alcance` | 2026-10-19 | integrada con otra rama | `archivo/documentacion/documentacion-decisiones-de-alcance` |
| `documentacion/decisiones-y-cresium` | 2026-11-02 | [#69](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/69) | `archivo/documentacion/documentacion-decisiones-y-cresium` |
| `funcionalidad/036-arnes` | 2026-11-02 | [#73](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/73) | `archivo/documentacion/036-arnes` |
| `funcionalidad/018-cierre` | 2026-11-04 | [#81](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/81) | `archivo/documentacion/018-cierre` |
| `funcionalidad/042-kit-usabilidad` | 2026-11-16 | integrada con otra rama | `archivo/documentacion/042-kit-usabilidad` |

## Red neuronal (1)

Clasificador de la capa 4 integrado con ONNX (012). El entrenamiento sigue en `funcionalidad/010-red-neuronal`.

| Rama original | Fecha | Pull Request | Etiqueta |
|---|---|---|---|
| `funcionalidad/012-capa-4-onnx` | 2026-11-06 | [#84](https://github.com/valentinasalmon/PFG-sistema-deteccion-IA/pull/84) | `archivo/red-neuronal/012-capa-4-onnx` |
