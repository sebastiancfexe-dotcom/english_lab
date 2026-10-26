import { useEffect, useRef, useState } from 'react'

/* Gráficas hechas a mano en SVG/HTML. Reglas: marcas finas, cuadrícula discreta, valores siempre visibles
   (etiqueta, tooltip o tabla), y el color de la serie nunca se usa para texto. */

const MES = new Intl.DateTimeFormat('es-CO', { day: 'numeric', month: 'short' })
const DIA_LARGO = new Intl.DateTimeFormat('es-CO', { weekday: 'long', day: 'numeric', month: 'long' })
// las fechas llegan como AAAA-MM-DD: se construyen a mediodía para que la zona horaria no cambie el día
const aFecha = (iso) => new Date(`${iso}T12:00:00`)

function useAncho(ref) {
  const [ancho, setAncho] = useState(0)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    setAncho(el.clientWidth)
    const obs = new ResizeObserver(() => setAncho(el.clientWidth))
    obs.observe(el)
    return () => obs.disconnect()
  }, [ref])
  return ancho
}

/** Tope del eje con números redondos; las marcas son 0, mitad y tope. */
function topeLimpio(max) {
  const pasos = [4, 6, 8, 10, 12, 16, 20, 30, 40, 60, 80, 100, 120, 160, 200, 300, 400, 600, 800, 1000]
  return pasos.find((p) => p >= max) ?? Math.ceil(max / 100) * 100
}

/** Rectángulo con las esquinas superiores redondeadas y la base recta. */
function rectSuperior(x, y, w, h, r) {
  const k = Math.min(r, h, w / 2)
  return `M${x},${y + h}V${y + k}Q${x},${y} ${x + k},${y}H${x + w - k}Q${x + w},${y} ${x + w},${y + k}V${y + h}Z`
}

/* ---------------- Anillo (un solo valor contra su meta) ---------------- */

export function Anillo({ valor, etiqueta, tamano = 176 }) {
  const grosor = 16
  const r = (tamano - grosor) / 2
  const c = 2 * Math.PI * r
  const pct = Math.max(0, Math.min(100, valor))
  return (
    <div style={{ width: tamano, height: tamano, position: 'relative', flex: 'none' }}>
      <svg width={tamano} height={tamano} role="img" aria-label={`${pct}% ${etiqueta}`}>
        <g transform={`rotate(-90 ${tamano / 2} ${tamano / 2})`} fill="none" strokeWidth={grosor}>
          <circle cx={tamano / 2} cy={tamano / 2} r={r} stroke="var(--track)" />
          <circle
            cx={tamano / 2}
            cy={tamano / 2}
            r={r}
            stroke="var(--brand)"
            strokeLinecap="round"
            strokeDasharray={`${(c * pct) / 100} ${c}`}
            style={{ transition: 'stroke-dasharray 0.6s ease' }}
          />
        </g>
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'grid', placeContent: 'center', textAlign: 'center' }}>
        <div style={{ fontSize: 36, fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1 }}>{pct}%</div>
        <div className="muted" style={{ fontSize: 12.5, marginTop: 4 }}>
          {etiqueta}
        </div>
      </div>
    </div>
  )
}

/* ---------------- Tile de estadística con mini-tendencia ---------------- */

function Sparkline({ valores, ancho = 96, alto = 34 }) {
  if (valores.length < 2) return null
  const max = Math.max(1, ...valores)
  const px = (i) => 4 + (i * (ancho - 8)) / (valores.length - 1)
  const py = (v) => alto - 5 - (v / max) * (alto - 10)
  const puntos = valores.map((v, i) => `${px(i)},${py(v)}`)
  const n = valores.length - 1
  return (
    <svg width={ancho} height={alto} aria-hidden="true" style={{ flex: 'none' }}>
      <polyline points={puntos.join(' ')} fill="none" stroke="#cbd5e1" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      <polyline
        points={`${puntos[n - 1]} ${puntos[n]}`}
        fill="none"
        stroke="var(--brand-mark)"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx={px(n)} cy={py(valores[n])} r="4" fill="var(--brand-mark)" stroke="#fff" strokeWidth="2" />
    </svg>
  )
}

export function Tile({ etiqueta, valor, sub, tendencia }) {
  return (
    <div className="card tile">
      <div className="tile-et">{etiqueta}</div>
      <div className="tile-fila">
        <div className="tile-valor">{valor}</div>
        {tendencia && <Sparkline valores={tendencia} />}
      </div>
      {sub && <div className="tile-sub">{sub}</div>}
    </div>
  )
}

/* ---------------- Barras horizontales (magnitud por categoría) ---------------- */

export function BarrasH({ filas }) {
  return (
    <ul className="barrash">
      {filas.map((f) => (
        <li key={f.clave} title={`${f.etiqueta}: ${f.valor}%${f.detalle ? ` (${f.detalle})` : ''}`}>
          <div className="bh-cab">
            <span>
              {f.etiqueta}
              {f.destacado && <span className="etiqueta-chip">Ahora</span>}
            </span>
            <span className="bh-val">
              <b>{f.valor}%</b> {f.detalle && <span className="muted">· {f.detalle}</span>}
            </span>
          </div>
          <div className="bh-pista">
            <i style={{ width: `${Math.max(f.valor, f.valor > 0 ? 1.5 : 0)}%` }} />
          </div>
        </li>
      ))}
    </ul>
  )
}

/* ---------------- Columnas apiladas por día ---------------- */

/** datos: [{fecha, ...valores}]; series: [{clave, nombre, color}] apiladas de abajo hacia arriba. */
export function Columnas({ datos, series, altura = 230 }) {
  const caja = useRef(null)
  const ancho = useAncho(caja)
  const [activo, setActivo] = useState(null)

  const izq = 34
  const der = 6
  const arriba = 22
  const abajo = 26
  const w = Math.max(ancho, 220)
  const plotW = w - izq - der
  const plotH = altura - arriba - abajo
  const total = (d) => series.reduce((s, x) => s + d[x.clave], 0)
  const maxTotal = Math.max(0, ...datos.map(total))
  const tope = topeLimpio(Math.max(maxTotal, 1))
  const banda = plotW / datos.length
  const grosor = Math.min(24, banda * 0.62)
  const y = (v) => arriba + plotH - (v / tope) * plotH
  const paso = Math.max(1, Math.ceil(52 / banda))

  const iMax = maxTotal > 0 ? datos.findIndex((d) => total(d) === maxTotal) : -1
  const iUltimo = datos.length - 1
  const rotulados = new Set([iMax, total(datos[iUltimo]) > 0 ? iUltimo : -1].filter((i) => i >= 0))

  const centro = (i) => izq + banda * i + banda / 2
  const d = activo === null ? null : datos[activo]

  return (
    <div>
      <div className="leyenda">
        {series.map((s) => (
          <span key={s.clave}>
            <i style={{ background: s.color }} />
            {s.nombre}
          </span>
        ))}
      </div>
      <div className="grafico-caja" ref={caja} style={{ height: altura }}>
        {ancho > 0 && (
          <svg width={w} height={altura} role="img" aria-label="Respuestas por día">
            {[0, tope / 2, tope].map((v) => (
              <g key={v}>
                <line x1={izq} x2={w - der} y1={y(v)} y2={y(v)} stroke={v === 0 ? '#d7dcd5' : 'var(--grid)'} strokeWidth="1" />
                <text x={izq - 8} y={y(v) + 4} textAnchor="end" fontSize="11" fill="var(--muted)">
                  {v}
                </text>
              </g>
            ))}

            {activo !== null && (
              <rect x={izq + banda * activo} y={arriba} width={banda} height={plotH} fill="var(--hover)" rx="6" />
            )}

            {datos.map((dia, i) => {
              const visibles = series.filter((s) => dia[s.clave] > 0)
              let base = y(0)
              return visibles.map((s, k) => {
                const alto = Math.max(3, (dia[s.clave] / tope) * plotH)
                const esUltimo = k === visibles.length - 1
                const recorte = esUltimo ? 0 : 2 // 2px de superficie entre segmentos
                const h = Math.max(1, alto - recorte)
                const top = base - alto
                base = top
                const x = centro(i) - grosor / 2
                return esUltimo ? (
                  <path key={`${i}-${s.clave}`} d={rectSuperior(x, top, grosor, h, 4)} fill={s.color} />
                ) : (
                  <rect key={`${i}-${s.clave}`} x={x} y={top + recorte} width={grosor} height={h} fill={s.color} />
                )
              })
            })}

            {[...rotulados].map((i) => (
              <text key={`v${i}`} x={centro(i)} y={y(total(datos[i])) - 7} textAnchor="middle" fontSize="11.5" fontWeight="700" fill="var(--ink)">
                {total(datos[i])}
              </text>
            ))}

            {datos.map(
              (dia, i) =>
                (iUltimo - i) % paso === 0 && (
                  <text key={`x${i}`} x={centro(i)} y={altura - 7} textAnchor="middle" fontSize="11" fill="var(--muted)">
                    {i === iUltimo ? 'Hoy' : MES.format(aFecha(dia.fecha))}
                  </text>
                ),
            )}

            {datos.map((dia, i) => (
              <rect
                key={`h${i}`}
                x={izq + banda * i}
                y={arriba}
                width={banda}
                height={plotH + abajo}
                fill="transparent"
                tabIndex={0}
                aria-label={`${DIA_LARGO.format(aFecha(dia.fecha))}: ${series.map((s) => `${s.nombre} ${dia[s.clave]}`).join(', ')}`}
                onPointerEnter={() => setActivo(i)}
                onPointerLeave={() => setActivo(null)}
                onFocus={() => setActivo(i)}
                onBlur={() => setActivo(null)}
                style={{ outline: 'none' }}
              />
            ))}
          </svg>
        )}
        {d && (
          <div className="tooltip" style={{ left: Math.min(Math.max(centro(activo), 80), w - 80) }}>
            <div className="tooltip-fecha">{DIA_LARGO.format(aFecha(d.fecha))}</div>
            {series.map((s) => (
              <div className="tooltip-fila" key={s.clave}>
                <span>
                  <i className="tooltip-clave" style={{ background: s.color }} />
                  {s.nombre}
                </span>
                <b>{d[s.clave]}</b>
              </div>
            ))}
            <div className="tooltip-fila" style={{ borderTop: '1px solid var(--grid)', marginTop: 4, paddingTop: 4 }}>
              <span>Total</span>
              <b>{total(d)}</b>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/* ---------------- Tarjeta de gráfica con vista de tabla ---------------- */

export function TarjetaGrafica({ titulo, subtitulo, columnas, filas, children }) {
  const [tabla, setTabla] = useState(false)
  return (
    <section className="card">
      <div className="grafico-cab">
        <div>
          <h2>{titulo}</h2>
          {subtitulo && <p>{subtitulo}</p>}
        </div>
        <button className="btn-tabla" type="button" aria-pressed={tabla} onClick={() => setTabla(!tabla)}>
          {tabla ? 'Ver gráfica' : 'Ver tabla'}
        </button>
      </div>
      {tabla ? (
        <div style={{ maxHeight: 300, overflowY: 'auto' }}>
          <table>
            <thead>
              <tr>
                {columnas.map((c, i) => (
                  <th key={c} className={i > 0 ? 'num' : ''}>
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filas.map((f) => (
                <tr key={f[0]}>
                  {f.map((celda, i) => (
                    <td key={i} className={i > 0 ? 'num' : ''}>
                      {celda}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        children
      )}
    </section>
  )
}

/* ---------------- Filtro de periodo ---------------- */

export function Segmentado({ etiqueta, opciones, valor, onCambio }) {
  return (
    <div className="filtros">
      <span className="filtros-et">{etiqueta}</span>
      <div className="segmentado" role="group" aria-label={etiqueta}>
        {opciones.map((o) => (
          <button key={o.valor} type="button" aria-pressed={o.valor === valor} onClick={() => onCambio(o.valor)}>
            {o.nombre}
          </button>
        ))}
      </div>
    </div>
  )
}

export const fechaCorta = (iso) => MES.format(aFecha(iso))

export const SERIES_ACTIVIDAD = [
  { clave: 'aciertos', nombre: 'Aciertos', color: 'var(--brand)' },
  { clave: 'fallos', nombre: 'Fallos', color: 'var(--neutral-series)' },
]

/** Totales de un tramo de la lista de actividad diaria. */
export function resumenPeriodo(actividad) {
  const total = actividad.reduce((s, d) => s + d.total, 0)
  const aciertos = actividad.reduce((s, d) => s + d.aciertos, 0)
  const mejor = actividad.reduce((m, d) => (d.total > m.total ? d : m), { total: 0 })
  return {
    total,
    aciertos,
    porcentaje: total ? Math.round((100 * aciertos) / total) : 0,
    diasActivos: actividad.filter((d) => d.total > 0).length,
    mejor,
  }
}

export const filasBloques = (bloques, activo) =>
  bloques.map((b) => ({
    clave: b.numero,
    etiqueta: `Bloque ${b.numero}`,
    valor: b.porcentaje,
    detalle: b.asumido ? 'dado por conocido' : `${b.dominadas} de ${b.total}`,
    destacado: b.numero === activo,
  }))
