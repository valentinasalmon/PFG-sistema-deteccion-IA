# 053 · Tareas

- [x] **T01**: `scripts/medir_salud.sh` y su temporizador de 15 minutos (`plataforma-monitoreo.service` y `.timer`), habilitado por `instalar_configuracion.sh`.
- [x] **T02**: `monitoreo.tf`: tema SNS con suscripción por correo, alarmas propias y de la EC2, tablero, y permiso `PutMetricData` limitado al espacio `evidentIA`.
- [x] **T03**: Validación local (Terraform, `shellcheck` y prueba del script contra producción con un `aws` falso).
- [x] **T04**: Guía de qué hacer con cada alerta.
- [ ] **T05**: La autora aplica Terraform, confirma la suscripción y prueba una alarma (CA3 y CA4).
