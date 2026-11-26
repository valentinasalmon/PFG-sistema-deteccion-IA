# 2026-11-26 · Monitoreo y alertas con CloudWatch (053)

## Qué se hizo

- Script `medir_salud.sh` que cada 15 minutos publica en CloudWatch cinco métricas:
  - si el sitio responde;
  - las tareas fallidas;
  - el disco;
  - la memoria;
  - los días del certificado.
- Siete alarmas con aviso por correo (SNS) al fallar y al recuperarse, un tablero y el permiso mínimo para publicar métricas.
- Guía de qué hacer con cada alerta: [monitoreo-y-alertas.md](../guias/monitoreo-y-alertas.md).

## Decisiones tomadas

- **CloudWatch y no un servicio externo** (Datadog, Sentry, UptimeRobot): ya está en la cuenta de AWS, no suma otro proveedor que reciba datos de la plataforma (Ley 25.326) y cuesta cerca de USD 1,50 por mes.
- **Script propio y no el agente de CloudWatch**: el agente es otro programa para instalar y mantener en la EC2. Con `aws cloudwatch put-metric-data`, que ya está instalado, alcanza para cinco métricas.
- **La salud se mide de punta a punta** (`https://evidentiaa.com.ar/api/salud`, desde el mismo servidor): una sola métrica cubre Nginx, el certificado, la aplicación, la base y Redis. Si el servidor entero se cae, deja de publicar, y la alarma trata la falta de datos como caída.
- **Sin dato del certificado no se publica un 0**: evita alarmas falsas cuando `openssl` no puede conectarse un momento.
- **La recuperación de la EC2 ante fallas de hardware queda en AWS**: la recuperación automática simplificada viene activa en las t3, según la documentación de EC2 consultada.

- **Cada 15 minutos y no cada 5** (pedido de la autora: «es un MVP; si se lleva a producción comercial, sí»). Una caída se avisa a los 30 minutos como mucho. Se sacó la métrica de carga, porque la CPU ya la publica AWS sin costo. Para una operación comercial alcanza con cambiar dos números (temporizador y `monitoreo.tf`).

## Problemas encontrados y cómo se resolvieron

- Para validar Terraform en el entorno del agente hizo falta permitir la descarga de proveedores (`registry.terraform.io` y `releases.hashicorp.com`).
- La unidad de systemd se escribió con la herramienta de archivos por el mismo motivo que en la 052: el gancho de secretos bloquea un comando de la terminal que nombre la ruta del archivo de entorno.
- El gancho `revisar_commit.py` frenó un commit con el tipo `infraestructura`, que no es un tipo válido (las áreas van en el nombre de la rama, no en el tipo del commit). Se rehízo como `funcionalidad(053)`.

## Pendientes

- La autora aplica Terraform, confirma la suscripción y prueba una alarma (053 CA3 y CA4).
