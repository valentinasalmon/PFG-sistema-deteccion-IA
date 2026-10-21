# 014 · Planes, pago simulado y tablero de administración

**Requisitos**: RF19, RF20, RF21, RF22 · **Reglas**: RN13, RN15, RN35 · **Cuestiones**: CP-01 (pago simulado), CP-02 (planes)

## Objetivo

Que cada espacio de trabajo vea su plan y su consumo, y que el Referente pueda cambiar de plan con un pago **simulado** que aplica el plan de verdad sin cobrar nada. El Administrador tiene un tablero con indicadores agregados y listados de solo lectura.

## Criterios de aceptación

- [x] **CA1 (RF19 CA2)**: un análisis que supera el límite mensual del plan se rechaza. El mensaje indica el límite y la fecha de renovación: el primer día del mes siguiente.
- [x] **CA2 (RF19 CA3)**: los límites de cada plan son datos de configuración. Hoy el plan Personal tiene 10 análisis por mes, el Básico 100 y el Profesional 500.
- [x] **CA3 (RF20 CA1)**:
  - el Referente y los miembros ven el plan, los límites y el consumo del mes (miembros y análisis);
  - el abogado ve el consumo de su espacio personal en «Mi perfil».
- [x] **CA4 (RF20 CA2)**:
  - el Referente elige otro plan y ve un paso de **pago simulado**, presentado como tal y sin pedir datos de tarjeta;
  - al confirmar, el plan se aplica de inmediato y se audita como `organizacion.cambio_plan` con `pago: simulado`;
  - no se puede bajar a un plan con menos lugares que los miembros actuales.
- [x] **CA5 (RF21 CA1)**: el Administrador ve, con un rango de fechas opcional:
  - cuentas por perfil;
  - organizaciones por tipo y por plan;
  - casos por estado y por tipo;
  - análisis por mes;
  - altas de cuentas por mes.
- [x] **CA6 (RF21 CA2, RF22 CA2)**: ningún indicador ni listado permite identificar o abrir un caso, una imagen o un informe.
- [x] **CA7 (RF22 CA1)**: los listados de cuentas y de organizaciones se pueden buscar y paginar, y no permiten modificar nada.
- [x] **CA8 (RF21 CA3)**: cualquier otra cuenta recibe acceso denegado (403).
