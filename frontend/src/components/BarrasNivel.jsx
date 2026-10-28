import { Barra } from './Estado'

/** Fila de tramos (uno por nivel, o uno por acierto de una racha): verdes los hechos y resaltado el actual. */
function Tramos({ total, hechos, actual, etiqueta }) {
  return (
    <div
      className="tramos"
      style={{ gridTemplateColumns: `repeat(${total}, 1fr)` }}
      role="img"
      aria-label={etiqueta}
    >
      {Array.from({ length: total }, (_, i) => (
        <i key={i} className={i < hechos ? 'hecho' : i === actual ? 'actual' : ''} />
      ))}
    </div>
  )
}

/**
 * Las tres barras del quiz: avance de la prueba, nivel de dificultad (escalera 1–N) y racha de aciertos del nivel.
 * `niveles` es la lista [{numero, nombre, cefr}] que entrega la API.
 */
export default function BarrasNivel({ avance, textoAvance, niveles, nivel, aprobados, racha, rachaMeta, textoRacha }) {
  const actual = niveles.find((n) => n.numero === nivel)
  return (
    <div className="card barras-nivel">
      <div>
        <div className="bn-cab">
          <span>Progreso</span>
          <b>{textoAvance}</b>
        </div>
        <Barra valor={avance} />
      </div>
      <div>
        <div className="bn-cab">
          <span>Dificultad</span>
          <b>
            Nivel {nivel} · {actual?.nombre} <span className="muted">({actual?.cefr})</span>
          </b>
        </div>
        <Tramos
          total={niveles.length}
          hechos={aprobados}
          actual={nivel - 1}
          etiqueta={`Nivel ${nivel} de ${niveles.length}`}
        />
      </div>
      <div>
        <div className="bn-cab">
          <span>Racha en este nivel</span>
          <b>{textoRacha}</b>
        </div>
        <Tramos total={rachaMeta} hechos={racha} actual={-1} etiqueta={textoRacha} />
      </div>
    </div>
  )
}
