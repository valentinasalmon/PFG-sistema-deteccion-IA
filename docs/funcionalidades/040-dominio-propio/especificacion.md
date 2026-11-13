# 040 · Dominio propio

**Estado**: implementada en el repositorio (2026-11-13); falta aplicarla en AWS y delegar el dominio (autora). **Rama**: `funcionalidad/040-dominio-propio`. **Pedido**: la autora compró `evidentiaa.com.ar` y pidió integrarlo.

## Problema

La plataforma se publica en `<ip>.sslip.io`: la dirección no se ve profesional, SES no puede verificar un dominio propio y los correos salen desde una dirección suelta, con riesgo de caer en Spam. Configurar el DNS a mano (registro A, tres CNAME de DKIM y DMARC) en un panel externo es propenso a errores.

## Alcance

- Con la variable `dominio` completa, Terraform crea la zona en Route 53, el registro A al servidor, la identidad del dominio en SES con DKIM y la política DMARC; la salida `servidores_de_nombres` da los servidores para delegar el dominio en NIC Argentina.
- Un remitente del dominio no se verifica como dirección suelta: lo cubre la identidad del dominio.
- Sin dominio, nada cambia (sigue `sslip.io`).
- Guía de despliegue reescrita para `evidentiaa.com.ar`.

## Criterios de aceptación

- [x] **CA1**: Con `dominio` vacío, el plan de Terraform no crea recursos nuevos.
- [ ] **CA2**: Con `dominio = "evidentiaa.com.ar"`, `nslookup` devuelve la IP del servidor y `https://evidentiaa.com.ar/estado` responde con un certificado válido (autora).
- [ ] **CA3**: La identidad `evidentiaa.com.ar` figura como *Verified* en SES y un correo de la plataforma llega a la bandeja de entrada desde `notificaciones@evidentiaa.com.ar` (autora).
