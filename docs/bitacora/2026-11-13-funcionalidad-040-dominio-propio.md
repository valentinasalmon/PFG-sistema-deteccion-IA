# 2026-11-13 · 040: dominio propio

## Contexto

La autora no encontró libre `evidentia.com` ni variantes baratas en `.com` y compró **`evidentiaa.com.ar`**. Pidió integrarlo y saber qué falta subir o integrar. Además, la ejecución de la integración continua de `main` de la 039 (PR #90) quedó en cola desde el 2026-11-11 por una demora de GitHub Actions y no arrancó sola; se le indicó cancelarla y volver a ejecutarla.

## Hecho

- `infraestructura/terraform/principal/dns.tf`: zona de Route 53, registro A, identidad del dominio en SES con Easy DKIM (tres CNAME) y DMARC en modo observación, todo condicionado a la variable `dominio`.
- `correo.tf`: un remitente del dominio ya no se verifica como dirección suelta. Salida nueva `servidores_de_nombres`.
- Guía de despliegue reescrita para `evidentiaa.com.ar`.
- Se sumaron a esta rama los dos commits de documentación de la 039 que quedaron fuera del PR #89 (Hedera en febrero de 2027 y pendientes al día).

## Decisiones

- **DNS en Route 53 administrado por Terraform** en vez de cargar registros a mano en NIC Argentina o en Cloudflare: los registros de DKIM son largos y fáciles de copiar mal, y así el DNS queda versionado como el resto de la infraestructura. Costo: US$ 0,50 por mes. La autora solo delega el dominio una vez.
- **La plataforma en el dominio raíz** (`evidentiaa.com.ar`), sin `www`: el certificado se pide para un solo nombre y evita un segundo registro sin certificado.

## Verificación

`terraform fmt -check` sin cambios. `terraform validate` no se pudo correr en el entorno del agente (el registro de proveedores de Terraform no es accesible); lo corre el trabajo «Infraestructura» de la integración continua en el Pull Request.

## Pendiente

- Autora: reejecutar el despliegue de la 039 en `main`; aplicar Terraform con el dominio, delegar en NIC Argentina, pedir el certificado, probar los correos y pedir la salida del modo de prueba de SES.
