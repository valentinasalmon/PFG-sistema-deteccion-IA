/**
 * Ilustraciones propias de evidentIA (funcionalidad 034).
 *
 * Trazo verde bosque, rellenos lima y azul suave, y las esquinas de visor de
 * la marca. Son decorativas (``aria-hidden``): el texto que las acompaña da
 * el sentido. Las animaciones internas (escaneo, brillo) se detienen con
 * «reducir movimiento» desde el CSS global.
 *
 * Realiza: RNF10 (identidad visual y estados vacíos con contexto).
 */

export function IlustracionVisor({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 420 300" aria-hidden="true" focusable="false">
      <rect
        x="40"
        y="46"
        width="250"
        height="190"
        rx="14"
        fill="#ffffff"
        stroke="#c7d0cb"
        strokeWidth="2"
        transform="rotate(-6 165 141)"
      />
      <rect
        x="70"
        y="40"
        width="250"
        height="190"
        rx="14"
        fill="#e8effa"
        stroke="#9db4dc"
        strokeWidth="2"
        transform="rotate(-2 195 135)"
      />
      <g transform="translate(100 34)">
        <rect width="250" height="190" rx="14" fill="#9bb7c9" />
        <path d="M0 110 L250 70 V190 H0Z" fill="#6f7f72" />
        <path d="M0 150 L250 120 V190 H0Z" fill="#3b443d" />
        <circle cx="190" cy="48" r="20" fill="#f1e3c2" />
        <rect x="42" y="112" width="160" height="44" rx="20" fill="#c43c32" />
        <circle cx="78" cy="160" r="15" fill="#1b1d1c" />
        <circle cx="168" cy="160" r="15" fill="#1b1d1c" />
        <ellipse cx="150" cy="118" rx="44" ry="30" fill="#f2a33a" opacity=".55">
          <animate attributeName="opacity" values=".25;.65;.25" dur="3s" repeatCount="indefinite" />
        </ellipse>
        <rect x="0" y="20" width="250" height="3" fill="#a4cb3e">
          <animate attributeName="y" values="8;180;8" dur="4s" repeatCount="indefinite" />
        </rect>
      </g>
      <g stroke="#a4cb3e" strokeWidth="5" fill="none" strokeLinecap="round">
        <path d="M86 52 V22 H116" />
        <path d="M334 22 H364 V52" />
        <path d="M86 210 V240 H116" />
        <path d="M334 240 H364 V210" />
      </g>
      <g transform="translate(300 196)">
        <rect width="104" height="80" rx="14" fill="#17291f" />
        <circle cx="52" cy="40" r="22" fill="#a4cb3e" />
        <circle cx="52" cy="40" r="11" fill="#17291f" />
        <ellipse cx="52" cy="40" rx="3" ry="9" fill="#a4cb3e" />
      </g>
    </svg>
  )
}

export function IlustracionCarpeta({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <path
        d="M30 40a8 8 0 0 1 8-8h36l10 10h78a8 8 0 0 1 8 8v70a8 8 0 0 1-8 8H38a8 8 0 0 1-8-8z"
        fill="#eef6dc"
        stroke="#3e6110"
        strokeWidth="3"
      />
      <rect x="52" y="56" width="70" height="52" rx="6" fill="#fff" stroke="#c7d0cb" strokeWidth="2" />
      <circle cx="130" cy="96" r="20" fill="#fff" stroke="#2f5da8" strokeWidth="5" />
      <path d="M144 110l16 16" stroke="#2f5da8" strokeWidth="7" strokeLinecap="round" />
      <g stroke="#a4cb3e" strokeWidth="4" fill="none" strokeLinecap="round">
        <path d="M18 30V18h12" />
        <path d="M170 18h12v12" />
        <path d="M18 120v12h12" />
        <path d="M170 132h12v-12" />
      </g>
    </svg>
  )
}

export function IlustracionEquipo({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <path
        d="M60 70 L100 50 L140 70 L100 100Z"
        fill="none"
        stroke="#c7d0cb"
        strokeWidth="3"
        strokeDasharray="6 6"
      />
      <circle cx="100" cy="50" r="24" fill="#a4cb3e" />
      <circle cx="100" cy="44" r="8" fill="#17291f" />
      <path d="M86 62a14 10 0 0 1 28 0" fill="#17291f" />
      <circle cx="56" cy="80" r="20" fill="#e8effa" stroke="#2f5da8" strokeWidth="3" />
      <circle cx="56" cy="76" r="6" fill="#2f5da8" />
      <circle cx="144" cy="80" r="20" fill="#e8effa" stroke="#2f5da8" strokeWidth="3" />
      <circle cx="144" cy="76" r="6" fill="#2f5da8" />
      <circle cx="100" cy="112" r="20" fill="#eef6dc" stroke="#3e6110" strokeWidth="3" />
      <path d="M92 112l6 6 10-12" stroke="#3e6110" strokeWidth="4" fill="none" strokeLinecap="round" />
    </svg>
  )
}

export function IlustracionCadena({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <g fill="#fff" stroke="#17291f" strokeWidth="3">
        <rect x="14" y="54" width="46" height="46" rx="10" />
        <rect x="77" y="54" width="46" height="46" rx="10" fill="#a4cb3e" />
        <rect x="140" y="54" width="46" height="46" rx="10" />
      </g>
      <path d="M60 77h17M123 77h17" stroke="#17291f" strokeWidth="3" />
      <text x="37" y="82" fontFamily="monospace" fontSize="11" textAnchor="middle" fill="#4e5b54">
        9f2c
      </text>
      <path d="M90 76l7 7 13-14" stroke="#17291f" strokeWidth="4" fill="none" strokeLinecap="round" />
      <text x="163" y="82" fontFamily="monospace" fontSize="11" textAnchor="middle" fill="#4e5b54">
        41ab
      </text>
      <text x="100" y="128" fontFamily="sans-serif" fontSize="11" textAnchor="middle" fill="#4e5b54">
        Sellado en Hedera
      </text>
    </svg>
  )
}

export function IlustracionCelular({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <rect x="70" y="12" width="64" height="126" rx="12" fill="#17291f" />
      <rect x="76" y="24" width="52" height="96" rx="4" fill="#9bb7c9" />
      <path d="M76 84 L128 70 V120 H76Z" fill="#3b443d" />
      <rect x="84" y="80" width="34" height="14" rx="6" fill="#c43c32" />
      <circle cx="160" cy="44" r="20" fill="#a4cb3e" />
      <path
        d="M160 54V34M152 41l8-8 8 8"
        stroke="#17291f"
        strokeWidth="4"
        fill="none"
        strokeLinecap="round"
      />
      <path d="M40 60h20M30 76h30" stroke="#c7d0cb" strokeWidth="4" strokeLinecap="round" />
    </svg>
  )
}

export function IlustracionInforme({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <path d="M50 14h70l30 30v94H50z" fill="#fff" stroke="#17291f" strokeWidth="3" />
      <path d="M120 14v30h30" fill="#eef6dc" stroke="#17291f" strokeWidth="3" />
      <path d="M64 58h56M64 72h70M64 86h40" stroke="#c7d0cb" strokeWidth="5" strokeLinecap="round" />
      <g fill="#17291f">
        <rect x="64" y="100" width="8" height="8" />
        <rect x="76" y="100" width="4" height="8" />
        <rect x="64" y="112" width="4" height="12" />
        <rect x="72" y="116" width="12" height="8" />
        <rect x="88" y="100" width="6" height="6" />
      </g>
      <circle cx="132" cy="114" r="18" fill="#a4cb3e" />
      <path d="M124 114l6 6 10-12" stroke="#17291f" strokeWidth="4" fill="none" strokeLinecap="round" />
    </svg>
  )
}

export function IlustracionCorreo({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <rect x="36" y="40" width="128" height="86" rx="12" fill="#fff" stroke="#17291f" strokeWidth="3" />
      <path d="M38 46l62 44 62-44" fill="none" stroke="#17291f" strokeWidth="3" />
      <circle cx="152" cy="40" r="20" fill="#a4cb3e" />
      <path d="M144 40l6 6 10-12" stroke="#17291f" strokeWidth="4" fill="none" strokeLinecap="round" />
      <path d="M14 70h14M8 86h20" stroke="#c7d0cb" strokeWidth="4" strokeLinecap="round" />
    </svg>
  )
}

export function IlustracionReloj({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <circle cx="100" cy="75" r="50" fill="#e8effa" stroke="#2f5da8" strokeWidth="4" />
      <path d="M100 45v30l20 14" stroke="#17291f" strokeWidth="6" fill="none" strokeLinecap="round" />
      <path d="M100 25a50 50 0 0 1 50 50" stroke="#a4cb3e" strokeWidth="8" fill="none" strokeLinecap="round">
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 100 75"
          to="360 100 75"
          dur="3s"
          repeatCount="indefinite"
        />
      </path>
    </svg>
  )
}

export function IlustracionRoto({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <g stroke="#a4cb3e" strokeWidth="5" fill="none" strokeLinecap="round">
        <path d="M30 44V22h22" />
        <path d="M148 22h22v22" />
        <path d="M30 106v22h22" />
        <path d="M148 128h22v-22" />
      </g>
      <path d="M58 40h50l-8 30 14 10-10 30H58z" fill="#e8ece9" stroke="#4e5b54" strokeWidth="3" />
      <path
        d="M118 40h24v70h-34l10-30-14-10z"
        fill="#fff"
        stroke="#4e5b54"
        strokeWidth="3"
        transform="rotate(8 130 75)"
      />
      <text
        x="100"
        y="146"
        fontFamily="Sora, sans-serif"
        fontWeight="800"
        fontSize="18"
        textAnchor="middle"
        fill="#17291f"
      >
        404
      </text>
    </svg>
  )
}

export function IlustracionEscudo({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <path
        d="M100 14l50 18v38c0 30-21 54-50 64-29-10-50-34-50-64V32z"
        fill="#eef6dc"
        stroke="#3e6110"
        strokeWidth="4"
      />
      <path d="M78 74l16 16 30-34" stroke="#17291f" strokeWidth="7" fill="none" strokeLinecap="round" />
    </svg>
  )
}

export function IlustracionAlerta({ clase = '' }) {
  return (
    <svg className={`ilustracion ${clase}`} viewBox="0 0 200 150" aria-hidden="true" focusable="false">
      <path d="M50 14h70l30 30v94H50z" fill="#fff" stroke="#17291f" strokeWidth="3" />
      <path d="M64 58h56M64 72h70M64 86h40" stroke="#c7d0cb" strokeWidth="5" strokeLinecap="round" />
      <circle cx="132" cy="112" r="20" fill="#fef3f2" stroke="#b42318" strokeWidth="4" />
      <path d="M132 102v12M132 121v.5" stroke="#b42318" strokeWidth="5" strokeLinecap="round" />
    </svg>
  )
}
