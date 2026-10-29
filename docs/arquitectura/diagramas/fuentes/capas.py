from comun import *
W, H = 1500, 900
s = inicio(W, H)
s.append(panel(30, 40, 560, 800, "BACKEND · ARQUITECTURA EN CAPAS", oscuro=True))
capas = [("Rutas", ["Reciben el pedido HTTP, validan", "los datos y devuelven la respuesta"]),
         ("Servicios", ["Reglas de negocio, permisos", "y registro de auditoría"]),
         ("Repositorios", ["Consultas y escrituras", "en la base de datos"]),
         ("Modelos", ["Tablas de la base", "(SQLAlchemy y Alembic)"])]
for i, (t, l) in enumerate(capas):
    y = 120 + i * 150
    s.append(caja(70, y, 330, 110, t, l))
    if i < 3:
        s.append(linea([(235, y + 110), (235, y + 148)]))
s.append(cilindro(110, 735, 250, 90, "PostgreSQL"))
s.append(linea([(235, 680), (235, 733)]))
s.append(caja(420, 430, 150, 140, "Tareas", ["en segundo", "plano (RQ)"], tam=16, relleno=CELESTE))
s.append(linea([(495, 430), (495, 355), (402, 355)]))
s.append(f'<text x="310" y="868" text-anchor="middle" font-size="14" fill="{TINTA2}">Cada capa depende solo de la inferior; import-linter lo verifica en cada cambio.</text>')

s.append(panel(650, 40, 820, 800, "PIEZAS INTERCAMBIABLES · PATRÓN STRATEGY"))
grupos = [("Capas de análisis", ["Metadatos", "C2PA", "ELA", "Clasificador"]),
          ("Almacenamiento de archivos", ["Local", "Amazon S3"]),
          ("Cola de trabajos", ["Sincrónica", "En hilo", "RQ"]),
          ("Sello de tiempo", ["Simulado", "Hedera"])]
for i, (t, ops) in enumerate(grupos):
    y = 120 + i * 175
    s.append(caja(690, y, 740, 140, "", []))
    s.append(f'<text x="725" y="{y+40}" font-size="18" font-weight="700" fill="{TINTA}">{esc(t)}</text>')
    s.append(f'<text x="725" y="{y+63}" font-size="14.5" fill="{TINTA2}">Una interfaz común; la implementación se elige por configuración</text>')
    ancho = 150
    for j, o in enumerate(ops):
        s.append(chip(725 + j * (ancho + 18), y + 82, ancho, 38, o))
s.append(linea([(400, 300), (648, 300)]))
s.append(etiqueta(520, 272, "usan cada pieza por su interfaz"))
s.append(f'<text x="1060" y="868" text-anchor="middle" font-size="14" fill="{TINTA2}">Gracias a este patrón, el sello migra de Blockchain Federal Argentina a Hedera sin modificar el resto del sistema.</text>')
open("capas.svg", "w").write(fin(s))
