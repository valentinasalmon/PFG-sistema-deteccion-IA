from comun import *
W, H = 1720, 960
s = inicio(W, H)
# Personas
s.append(panel(30, 40, 290, 860, "PERSONAS"))
personas = [("Abogado o aseguradora", ["Navegador web"]),
            ("Celular del usuario", ["QR de un solo uso"]),
            ("Persona afectada", ["Enlace sin cuenta,", "con declaración"]),
            ("Tercero que verifica", ["Escanea el QR", "del informe"])]
for i, (t, l) in enumerate(personas):
    y = 120 + i * 190
    s.append(caja(55, y, 240, 140, t, l, tam=17, dy=16))
    s.append(persona(175, y + 30))
    s.append(linea([(295, y + 70), (338, y + 70)], flecha=False))

# Servidor
s.append(panel(360, 40, 890, 860, "SERVIDOR EC2 · AWS, REGIÓN IRLANDA", oscuro=True))
s.append(linea([(338, 175), (338, 760)], flecha=False))
s.append(linea([(338, 175), (408, 175)]))
s.append(etiqueta(338, 115, "HTTPS"))
s.append(caja(408, 120, 812, 100, "Nginx", ["Proxy inverso · TLS · límites de pedidos · cabeceras de seguridad"]))
s.append(caja(408, 290, 240, 120, "Interfaz React", ["Archivos estáticos", "(Vite)"]))
s.append(linea([(528, 220), (528, 288)]))
s.append(etiqueta(528, 258, "/"))
# API con capas
s.append(caja(690, 290, 250, 360, "", [], relleno=CELESTE))
s.append(f'<text x="815" y="323" text-anchor="middle" font-size="18" font-weight="700" fill="{TINTA}">API REST Flask</text>')
s.append(f'<text x="815" y="345" text-anchor="middle" font-size="15" fill="{TINTA2}">Gunicorn</text>')
for i, c in enumerate(["Rutas", "Servicios", "Repositorios", "Modelos"]):
    y = 368 + i * 68
    s.append(chip(720, y, 190, 44, c, relleno=BLANCO, borde=AZUL))
    if i < 3:
        s.append(linea([(815, y + 44), (815, y + 66)], ancho=1.6))
s.append(linea([(815, 220), (815, 288)]))
s.append(etiqueta(815, 258, "/api"))
# Redis y trabajador
s.append(cilindro(985, 290, 235, 120, "Redis", ["Sesiones y cola"]))
s.append(linea([(940, 350), (983, 350)]))
s.append(caja(985, 470, 235, 270, "", []))
s.append(f'<text x="1102" y="503" text-anchor="middle" font-size="17" font-weight="700" fill="{TINTA}">Trabajador de análisis</text>')
s.append(f'<text x="1102" y="524" text-anchor="middle" font-size="15" fill="{TINTA2}">RQ, en segundo plano</text>')
for i, c in enumerate(["1 · Metadatos EXIF/XMP", "2 · Credenciales C2PA", "3 · ELA", "4 · Clasificador (ONNX)"]):
    s.append(chip(1003, 540 + i * 40, 200, 32, c))
s.append(f'<text x="1102" y="720" text-anchor="middle" font-size="14.5" fill="{TINTA2}">Motor de reglas → informe PDF</text>')
s.append(linea([(1102, 410), (1102, 468)]))
# PostgreSQL
s.append(cilindro(690, 720, 250, 140, "PostgreSQL", ["Casos, análisis", "y auditoría"]))
s.append(linea([(815, 650), (815, 718)]))
s.append(linea([(1102, 740), (1102, 790), (942, 790)]))

# Servicios externos
s.append(panel(1300, 40, 390, 860, "SERVICIOS EXTERNOS"))
ext = [("Amazon S3", ["Imágenes e informes", "cifrados y versionados"]),
       ("Hedera Consensus Service", ["Sello de tiempo de las huellas:", "imágenes, informes y versiones"]),
       ("Amazon SES", ["Correos y notificaciones"]),
       ("Google", ["Inicio de sesión", "(OpenID Connect)"])]
for i, (t, l) in enumerate(ext):
    y = 120 + i * 190
    s.append(caja(1340, y, 325, 140, t, l, tam=17))
    s.append(linea([(1275, y + 70), (1338, y + 70)]))
s.append(linea([(1275, 190), (1275, 760)], flecha=False))
s.append(linea([(1220, 605), (1275, 605)], flecha=False))
s.append(linea([(905, 290), (905, 255), (1275, 255)], flecha=False))
s.append(etiqueta(1150, 255, "hacia los servicios externos"))
s.append(f'<text x="{W/2}" y="938" text-anchor="middle" font-size="13.5" fill="{TINTA2}">Las flechas indican el sentido de las solicitudes. Todo el tráfico externo viaja cifrado.</text>')
open("arquitectura.svg", "w").write(fin(s))
