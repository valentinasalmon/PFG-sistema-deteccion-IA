/**
 * Animación de «Qué miramos» en la portada (funcionalidad 050, interfaz).
 *
 * Pedido de la autora (2026-11-18): una animación que muestre lo que hace el
 * sistema, al estilo de un plano con marcas rotuladas. Dibuja una foto de un
 * choque dentro de las esquinas de visor del logo, una línea que la recorre y,
 * por turnos, la marca de cada mirada (metadatos, C2PA, ELA y red neuronal)
 * sobre la parte de la foto que examina. La mirada activa se resalta también
 * en la lista de al lado.
 *
 * Es decorativa: la misma información está en la lista, por eso queda oculta
 * para los lectores de pantalla. Solo avanza sola mientras está a la vista y
 * si la persona no pidió «reducir movimiento»; en ese caso muestra todas las
 * marcas quietas.
 *
 * Realiza: RF19 (portada); RNF10 (rendimiento y accesibilidad).
 */
function clase(indice, activa, quieta) {
  return `escaneo__marca${quieta || indice === activa ? ' escaneo__marca--activa' : ''}`
}

export default function EscaneoMiradas({ activa, quieta }) {
  return (
    <figure className={`escaneo${quieta ? ' escaneo--quieta' : ''}`} aria-hidden="true">
      <svg viewBox="0 0 400 290" className="escaneo__lienzo" focusable="false">
        <defs>
          <pattern id="escaneo-grilla" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M20 0H0V20" fill="none" className="escaneo__grilla" />
          </pattern>
          <linearGradient id="escaneo-barrido" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#a4cb3e" stopOpacity="0" />
            <stop offset="1" stopColor="#a4cb3e" stopOpacity="0.22" />
          </linearGradient>
        </defs>
        <rect width="400" height="290" rx="18" className="escaneo__fondo" />
        <rect width="400" height="290" rx="18" fill="url(#escaneo-grilla)" />

        {/* Esquinas de visor, como en el logo */}
        <path
          className="escaneo__visor"
          d="M40 62V44h18M342 44h18v18M360 246v18h-18M58 264H40v-18"
        />

        {/* La foto: un auto con el frente abollado contra un poste */}
        <g className="escaneo__foto">
          <path d="M52 228H348" />
          <path d="M300 228V92M292 92h16" />
          <path d="M84 206v-26l26-8 30-30h76l34 30 24 4 14 10v20" />
          <path d="M150 148l-12 24h46v-24zM196 148v24h44l-26-24z" />
          <path className="escaneo__abolladura" d="M286 182l-8 6 6 5-9 5 7 4" />
          <circle cx="126" cy="210" r="16" />
          <circle cx="250" cy="210" r="16" />
          <path d="M84 206h26M142 206h92M266 206h18" />
        </g>

        {/* 01 · Metadatos: la ficha oculta de la foto */}
        <g className={clase(0, activa, quieta)}>
          <rect x="56" y="58" width="104" height="44" rx="6" className="escaneo__ficha" />
          <path d="M66 72h56M66 82h76M66 92h40" className="escaneo__renglon" />
          <text x="40" y="32" className="escaneo__rotulo">01 METADATOS</text>
        </g>

        {/* 02 · C2PA: la credencial de origen */}
        <g className={clase(1, activa, quieta)}>
          <path d="M334 62l16 6v12c0 9-7 16-16 18-9-2-16-9-16-18V68z" className="escaneo__ficha" />
          <path d="M327 80l5 5 9-9" className="escaneo__renglon" />
          <text x="360" y="32" textAnchor="end" className="escaneo__rotulo">02 C2PA</text>
        </g>

        {/* 03 · ELA: la zona que se guardó distinto */}
        <g className={clase(2, activa, quieta)}>
          <rect x="262" y="166" width="40" height="40" className="escaneo__zona" />
          <rect x="268" y="172" width="12" height="12" className="escaneo__calor" />
          <rect x="282" y="184" width="12" height="12" className="escaneo__calor" />
          <path d="M302 176h26v-34" className="escaneo__guia" />
          <text x="328" y="134" textAnchor="middle" className="escaneo__rotulo">03 ELA</text>
        </g>

        {/* 04 · Red neuronal: una mirada sobre toda la imagen */}
        <g className={clase(3, activa, quieta)}>
          <path d="M70 120l50 30 60-20 70 30 50-24" className="escaneo__red" />
          <circle cx="70" cy="120" r="4" className="escaneo__nodo" />
          <circle cx="120" cy="150" r="4" className="escaneo__nodo" />
          <circle cx="180" cy="130" r="4" className="escaneo__nodo" />
          <circle cx="250" cy="160" r="4" className="escaneo__nodo" />
          <circle cx="300" cy="136" r="4" className="escaneo__nodo" />
          <rect x="56" y="244" width="140" height="8" rx="4" className="escaneo__barra" />
          <rect x="56" y="244" width="38" height="8" rx="4" className="escaneo__barra-valor" />
          <text x="206" y="253" className="escaneo__rotulo">04 RED NEURONAL</text>
        </g>

        {!quieta && (
          <rect x="40" y="44" width="320" height="34" className="escaneo__barrido" fill="url(#escaneo-barrido)" />
        )}
      </svg>
    </figure>
  )
}
