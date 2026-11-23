/**
 * «Video» de «Qué miramos» en la portada (funcionalidad 050).
 *
 * Pedido de la autora (2026-11-18 y 2026-11-23): un video o una animación
 * «bien copada» de todo lo que hace el sistema. Es una animación propia en
 * SVG y CSS, con forma de video de 16:9: una cámara recorre la foto de un
 * choque y se acerca a lo que examina cada mirada (la ficha de metadatos, la
 * credencial C2PA, la zona que el ELA marca y la red neuronal sobre toda la
 * imagen) y termina con el informe. Pesa unos pocos kilobytes, toma los
 * colores de la identidad visual y no necesita bibliotecas.
 *
 * La lista de miradas de la portada funciona como capítulos. La animación es
 * decorativa (la lista dice lo mismo), por eso el lienzo y los subtítulos
 * quedan ocultos para los lectores de pantalla; el botón de pausa sí se anuncia.
 * No emite veredictos: el informe del final habla de indicios (RN27).
 *
 * Realiza: RF19 (portada); RN27; RNF10.
 */

/** Cámara de cada escena: [escala, desplazamiento x, desplazamiento y] sobre 640×360. */
const CAMARAS = [
  [1.3, 90, 30],
  [1.5, -500, -18],
  [1.7, -560, -228],
  [1, 0, 0],
  [0.8, -50, 30],
]

const SUBTITULOS = [
  ['01', 'Metadatos', 'Leemos con qué, cuándo y dónde se sacó la foto.'],
  ['02', 'C2PA', 'Buscamos la credencial de origen de quien la creó.'],
  ['03', 'ELA', 'Marcamos las zonas que se guardaron distinto.'],
  ['04', 'Red neuronal', 'Una mirada sobre toda la imagen: ¿la hizo una IA?'],
  ['', 'Informe', 'Todo junto, en un PDF sellado: indicios, no veredictos.'],
]

const FICHA = [
  ['CÁMARA', 'iPhone 15 Pro'],
  ['FECHA', '02/11/2026 14:31'],
  ['EDITOR', 'no registrado'],
  ['GPS', '-34.60, -58.38'],
]

const CALOR = [
  [0, 0, 0.25], [1, 0, 0.6], [2, 0, 0.3],
  [0, 1, 0.5], [1, 1, 0.95], [2, 1, 0.7],
  [0, 2, 0.2], [1, 2, 0.55], [2, 2, 0.35],
]

const NODOS = [
  [110, 110], [200, 150], [290, 120], [380, 160], [470, 120], [560, 150],
  [150, 230], [250, 205], [350, 230], [450, 205], [540, 240],
]
const ENLACES = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [6, 7], [7, 8], [8, 9], [9, 10],
  [0, 6], [1, 7], [2, 7], [3, 8], [4, 9], [5, 10], [3, 9]]

const INFORME = [
  ['Metadatos', 'leídos'],
  ['C2PA', 'sin credencial'],
  ['ELA', '1 zona para revisar'],
  ['Red neuronal', 'próximamente'],
]

function capa(escena, propia) {
  return `video__capa${escena === propia ? ' video__capa--activa' : ''}`
}

export default function VideoMiradas({ escena, duracion, reproduciendo, pausado, alternar, quieta }) {
  const [escala, x, y] = CAMARAS[escena]
  const [numero, titulo, texto] = SUBTITULOS[escena]
  return (
    <figure
      className={`video${quieta ? ' video--quieta' : ''}${reproduciendo ? '' : ' video--pausado'}`}
      data-escena={escena}
    >
      <div className="video__pantalla" aria-hidden="true">
        <svg viewBox="0 0 640 360" className="video__lienzo" focusable="false">
          <defs>
            <pattern id="video-grilla" width="24" height="24" patternUnits="userSpaceOnUse">
              <path d="M24 0H0V24" fill="none" className="video__grilla" />
            </pattern>
            <radialGradient id="video-luz" cx="0.5" cy="0.4" r="0.7">
              <stop offset="0" stopColor="#a4cb3e" stopOpacity="0.16" />
              <stop offset="1" stopColor="#a4cb3e" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="video-barrido" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="#a4cb3e" stopOpacity="0" />
              <stop offset="1" stopColor="#a4cb3e" stopOpacity="0.28" />
            </linearGradient>
          </defs>
          <rect width="640" height="360" className="video__fondo" />
          <rect width="640" height="360" fill="url(#video-grilla)" />
          <rect width="640" height="360" fill="url(#video-luz)" />

          <g
            className="video__camara"
            style={{ transform: `translate(${x}px, ${y}px) scale(${escala})` }}
          >
            {/* La foto: un auto con el frente contra un poste */}
            <g className="video__foto">
              <path d="M70 290H590" />
              <path d="M478 290V112M466 112h24M478 140l-14 10" />
              <path d="M130 262v-38l40-12 46-44h118l52 44 38 6 22 14v30" />
              <path d="M224 178l-18 34h68v-34zM286 178v34h66l-40-34z" />
              <path d="M130 262h36M214 262h142M404 262h42" />
              <circle cx="190" cy="266" r="24" />
              <circle cx="190" cy="266" r="9" />
              <circle cx="380" cy="266" r="24" />
              <circle cx="380" cy="266" r="9" />
              <path d="M146 224h16M300 196h14" />
              <path className="video__abolladura" d="M446 226l12 8-9 7 13 8-10 6" />
              <path className="video__restos" d="M492 282l8-4M506 286l10 1M488 274l4-7" />
            </g>

            {/* 01 · Metadatos: la ficha oculta */}
            <g className={capa(escena, 0)}>
              <rect x="56" y="58" width="236" height="104" rx="10" className="video__ficha" />
              <text x="72" y="80" className="video__rotulo">01 METADATOS · EXIF</text>
              {FICHA.map(([clave, valor], indice) => (
                <g key={clave} className="video__linea" style={{ '--i': indice }}>
                  <text x="72" y={102 + indice * 17} className="video__clave">{clave}</text>
                  <text x="140" y={102 + indice * 17} className="video__valor">{valor}</text>
                </g>
              ))}
            </g>

            {/* 02 · C2PA: la credencial de origen */}
            <g className={capa(escena, 1)}>
              <g className="video__sello">
                <path d="M556 74l26 10v20c0 15-11 26-26 30-15-4-26-15-26-30V84z" className="video__escudo" />
                <path d="M546 104h20" className="video__trazo" />
              </g>
              <text x="556" y="156" textAnchor="middle" className="video__rotulo">02 C2PA</text>
              <text x="556" y="172" textAnchor="middle" className="video__valor">sin credencial</text>
            </g>

            {/* 03 · ELA: la zona que se guardó distinto */}
            <g className={capa(escena, 2)}>
              {CALOR.map(([columna, fila, intensidad]) => (
                <rect
                  key={`${columna}-${fila}`}
                  x={436 + columna * 12}
                  y={220 + fila * 12}
                  width="11"
                  height="11"
                  className="video__calor"
                  style={{ '--intensidad': intensidad, '--i': columna + fila }}
                />
              ))}
              <rect x="430" y="214" width="48" height="48" className="video__zona" />
              <path d="M478 238h34" className="video__guia" />
              <text x="516" y="234" className="video__rotulo">03 ELA</text>
              <text x="516" y="250" className="video__valor">zona para revisar</text>
            </g>

            {/* 04 · Red neuronal: toda la imagen */}
            <g className={capa(escena, 3)}>
              {ENLACES.map(([desde, hasta], indice) => (
                <path
                  key={`${desde}-${hasta}`}
                  d={`M${NODOS[desde].join(' ')}L${NODOS[hasta].join(' ')}`}
                  className="video__enlace"
                  pathLength="1"
                  style={{ '--i': indice }}
                />
              ))}
              {NODOS.map(([cx, cy], indice) => (
                <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="5" className="video__nodo" style={{ '--i': indice }} />
              ))}
              <rect x="72" y="314" width="200" height="8" rx="4" className="video__medidor" />
              <rect x="72" y="314" width="200" height="8" rx="4" className="video__medidor-valor" />
              <text x="284" y="322" className="video__rotulo">04 RED NEURONAL · PRÓXIMAMENTE</text>
            </g>
          </g>

          {/* Barrido del escáner y esquinas de visor, fijos en la pantalla */}
          <rect x="-60" y="24" width="60" height="312" className="video__barrido" fill="url(#video-barrido)" />
          <path d="M0 24V336" className="video__barrido video__barrido-linea" />
          <path className="video__visor" d="M24 54V24h30M586 24h30v30M616 306v30h-30M54 336H24v-30" />
          <circle cx="44" cy="44" r="4" className="video__rec" />
          <text x="54" y="48" className="video__clave">REC · ANÁLISIS</text>
        </svg>

        {/* El informe del final */}
        <div className={`video__informe${escena === 4 ? ' video__informe--activo' : ''}`}>
          <span className="video__informe-etq">Informe · PDF sellado</span>
          <ul>
            {INFORME.map(([mirada, estado], indice) => (
              <li key={mirada} style={{ '--i': indice }}>
                <b>{mirada}</b>
                <span>{estado}</span>
              </li>
            ))}
          </ul>
          <span className="video__informe-pie">Indicios, no veredictos</span>
        </div>

      </div>

      <p className="video__subtitulo" aria-hidden="true" key={escena}>
        {numero && <span className="video__subtitulo-num">{numero}</span>}
        <b>{titulo}</b> {texto}
      </p>

      <div className="video__controles">
        <button
          type="button"
          className="video__boton"
          onClick={alternar}
          aria-label={pausado ? 'Reproducir la animación' : 'Pausar la animación'}
        >
          <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            {pausado ? <path d="M8 5v14l11-7z" /> : <path d="M7 5h4v14H7zM13 5h4v14h-4z" />}
          </svg>
        </button>
        <ol className="video__progreso" aria-hidden="true">
          {SUBTITULOS.map(([, nombre], indice) => (
            <li
              key={nombre}
              className={indice < escena ? 'video__tramo video__tramo--visto' : 'video__tramo'}
            >
              {indice === escena && (
                <span
                  className="video__tramo-avance"
                  style={{ '--duracion': `${duracion}ms` }}
                />
              )}
            </li>
          ))}
        </ol>
      </div>
    </figure>
  )
}
