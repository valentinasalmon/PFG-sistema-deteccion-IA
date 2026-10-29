from comun import *
W, H = 1700, 900
s = inicio(W, H)
s.append(panel(30, 40, 1640, 230, "INTEGRACIÓN Y DESPLIEGUE CONTINUOS · GITHUB"))
s.append(caja(60, 115, 260, 125, "Autora y agente de IA", ["Rama por funcionalidad,", "commits con coautoría"], tam=17))
s.append(caja(390, 115, 220, 125, "Pull request", ["Revisión de la autora", "e integración"], tam=17))
s.append(caja(680, 105, 560, 145, "", []))
s.append(f'<text x="960" y="135" text-anchor="middle" font-size="17" font-weight="700" fill="{TINTA}">Integración continua (GitHub Actions)</text>')
for j, c in enumerate(["Calidad", "Pruebas", "Capas", "Commits", "Dependencias", "Terraform"]):
    s.append(chip(705 + (j % 3) * 175, 152 + (j // 3) * 46, 160, 36, c))
s.append(caja(1310, 115, 330, 125, "Despliegue", ["Al integrar en main, con", "credenciales temporales (OIDC)"], tam=17))
s.append(linea([(320, 177), (388, 177)])); s.append(linea([(610, 177), (678, 177)])); s.append(linea([(1240, 177), (1308, 177)]))

s.append(panel(30, 320, 1340, 560, "AMAZON WEB SERVICES · REGIÓN IRLANDA · DEFINIDO CON TERRAFORM", oscuro=True))
s.append(cilindro(70, 410, 300, 120, "S3 de operación", ["Artefactos y respaldos"]))
s.append(caja(70, 570, 300, 110, "Systems Manager", ["Ejecuta el despliegue"]))
s.append(caja(70, 720, 300, 110, "Parameter Store", ["Secretos del sistema"]))
s.append(caja(470, 430, 400, 380, "", [], relleno=CELESTE))
s.append(f'<text x="670" y="468" text-anchor="middle" font-size="19" font-weight="700" fill="{TINTA}">Instancia EC2 t3.small</text>')
s.append(f'<text x="670" y="491" text-anchor="middle" font-size="15" fill="{TINTA2}">Disco cifrado · IP fija</text>')
for j, c in enumerate(["1 · Copia la versión nueva", "2 · Migra la base de datos", "3 · Verifica la salud", "4 · Si falla, vuelve a la anterior", "5 · Sella la huella de la versión"]):
    s.append(chip(500, 515 + j * 56, 340, 42, c, relleno=BLANCO, borde=AZUL))
s.append(cilindro(970, 410, 360, 120, "S3 de datos", ["Imágenes e informes cifrados"]))
s.append(caja(970, 570, 360, 110, "Amazon SES", ["Correos del sistema"]))
s.append(caja(970, 720, 360, 110, "Presupuesto", ["Alertas de gasto"]))
s.append(linea([(370, 470), (468, 520)])); s.append(linea([(370, 625), (468, 625)])); s.append(linea([(370, 775), (468, 730)]))
s.append(linea([(870, 520), (968, 470)])); s.append(linea([(870, 625), (968, 625)]))
s.append(caja(1420, 560, 250, 130, "Hedera", ["Registro público", "de la huella"], tam=18))
s.append(linea([(670, 810), (670, 858), (1395, 858), (1395, 625), (1418, 625)]))
s.append(etiqueta(1180, 858, "huella de la versión"))
# del despliegue a AWS
s.append(linea([(1475, 240), (1475, 290), (220, 290), (220, 408)]))
s.append(etiqueta(820, 290, "sube el artefacto y ordena el despliegue"))
open("infraestructura.svg", "w").write(fin(s))
