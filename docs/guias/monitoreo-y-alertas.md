# Monitoreo y alertas (funcionalidad 053)

La plataforma se vigila sola con Amazon CloudWatch. Cada 5 minutos el servidor mide su salud; si algo falla, llega un correo con el asunto **ALARM: "deteccion-imagenes-…"**, y cuando se recupera, otro con **OK**.

## Ponerlo en marcha (una sola vez)

1. Integrar el Pull Request de `infraestructura/monitoreo` y esperar el despliegue. Cada despliegue instala el temporizador `plataforma-monitoreo.timer`.
2. Desde la carpeta `infraestructura/terraform/principal`, aplicar los cambios con el mismo comando de siempre ([guía de despliegue](despliegue-aws.md)): `terraform apply`. Muestra que crea el tema de alertas, la suscripción, 7 alarmas y el tablero, y que cambia el permiso del servidor. Escribir `yes`.
3. Llega un correo de **AWS Notifications** al correo de alertas: abrirlo y tocar **Confirm subscription**. Sin eso no llega ninguna alerta.
4. En la consola de AWS → **CloudWatch** → **Paneles** (*Dashboards*) → `deteccion-imagenes` aparecen las métricas a los 10 minutos.

## Probar una alarma (053 CA4)

En la consola de AWS → **EC2** → la instancia → **Conectar** → **Session Manager**:

```bash
sudo systemctl stop plataforma-web
```

A los 10 a 15 minutos llega el correo **ALARM … plataforma-caida**. Después:

```bash
sudo systemctl start plataforma-web
```

y a los 5 a 10 minutos llega **OK**.

## Qué hacer con cada alerta

Todas las revisiones se hacen por Session Manager.

| Alerta | Qué revisar | Qué hacer |
|---|---|---|
| **plataforma-caida** | `systemctl status plataforma-web nginx postgresql redis-server` y `journalctl -u plataforma-web -n 100` | Reiniciar lo que esté caído (`sudo systemctl restart plataforma-web`). Si el último despliegue la rompió, volver a la versión anterior con el despliegue de GitHub. |
| **servidor-sin-respuesta** | La instancia en la consola de EC2 | AWS intenta recuperarla sola; si en 15 minutos no vuelve, **Detener** e **Iniciar** la instancia (no *Terminar*). |
| **tareas-fallidas** | `systemctl list-units 'plataforma-*' --failed` y `journalctl -u <servicio> -n 50` | Corregir la causa y limpiar el estado con `sudo systemctl reset-failed`. El catálogo de la SSN falla si el portal está caído: se reintenta la semana siguiente. |
| **disco-lleno** | `df -h` y `sudo du -sh /opt/plataforma/* /var/log` | Borrar versiones viejas (se conservan 3) o registros; si no alcanza, agrandar el disco en Terraform. |
| **memoria-baja** | `free -m` y `top` | Reiniciar el trabajador (`sudo systemctl restart plataforma-trabajador`); si se repite, pasar a una instancia más grande. |
| **cpu-alta** | `top` | Suele ser un análisis pesado; si dura, revisar la cola de análisis. |
| **certificado-por-vencer** | `sudo certbot renew --dry-run` | Corregir lo que diga certbot y ejecutar `sudo certbot renew`. |

Además, el estado de cada servicio se ve en [evidentiaa.com.ar/estado](https://evidentiaa.com.ar/estado).
