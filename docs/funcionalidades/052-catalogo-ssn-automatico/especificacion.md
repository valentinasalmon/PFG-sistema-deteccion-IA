# 052 · Catálogo de aseguradoras de la SSN, actualizado solo

**Estado**: implementada (2026-11-26); falta verla correr en producción. **Rama**: `integraciones/catalogo-ssn`. **Pedido**: la autora (2026-11-24): «una automatización de los registros de seguros, que cada cierto tiempo consulte la página y baje el dataset actualizado».

## Problema

El catálogo de aseguradoras habilitadas (CP-18), que valida a las aseguradoras que se registran, era una copia fija del 2026-10-16. La SSN lo actualiza cada pocos meses: hay altas, cambios de denominación y revocaciones de la autorización para operar. Con la copia fija, una aseguradora nueva no se podía registrar y una revocada seguía figurando.

## Alcance

- **Una vez por semana** (los lunes a la madrugada, con un temporizador de systemd), la plataforma:
  1. consulta el conjunto de datos «Entidades aseguradoras y reaseguradoras activas» en datos.gob.ar (API de CKAN, licencia CC-BY-4.0);
  2. baja el CSV vigente, esté donde esté publicado;
  3. le aplica la misma transformación que al archivo original: sin reaseguradoras y con las columnas que usa la plataforma.
- **Valida antes de aplicar**:
  - las columnas esperadas;
  - números de registro y CUIT sin repetir;
  - CUIT de 11 dígitos;
  - al menos 100 aseguradoras;
  - si la lista nueva es menor al 80 % de la actual, no se aplica sin una persona (`--forzar`).
- **Si cambió**:
  - guarda la copia nueva fuera de la carpeta de la versión (`/opt/plataforma/datos/catalogos`), así no se pierde en cada despliegue;
  - la registra en la auditoría;
  - avisa por correo a los Administradores, con las altas, las bajas, los cambios y las **revocaciones** que la SSN anota en la denominación.
- **Para revisar**: las aseguradoras ya registradas en la plataforma que dejaron de figurar o están en revocación se destacan en el correo. No se desactivan solas: lo decide el Administrador.
- **Estado en `/estado`**: cuántas aseguradoras hay y de qué fecha es la versión de la SSN.
- El archivo del repositorio queda como punto de partida y se actualizó con la versión de la SSN del 2026-10-26.

## Criterios de aceptación

- [x] **CA1**: El comando baja el archivo real, lo aplica si cambió y no hace nada si está igual. Probado contra el portal real el 2026-11-26: detectó 4 cambios, entre ellos 2 revocaciones en trámite.
- [x] **CA2**: Un archivo roto (otras columnas, repetidos, muy corto) no se aplica; si el portal no responde, sale con error y no toca nada.
- [x] **CA3**: Las bajas y las revocaciones de aseguradoras registradas llegan al Administrador por correo, y todo cambio queda en la auditoría.
- [x] **CA4**: Todos los procesos ven la versión nueva sin reiniciarse.
- [x] **CA5**: `/estado` muestra la fecha y la cantidad.
- [ ] **CA6**: Corre en producción con el temporizador (`systemctl list-timers` muestra `plataforma-catalogo-ssn.timer`) y `/estado` muestra la versión de la SSN. **No verificado todavía.**
