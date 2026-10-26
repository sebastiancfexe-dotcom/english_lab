import { Link } from 'react-router-dom'
import Estado from '../components/Estado'
import { useCarga } from '../useCarga'

const fecha = (iso) =>
  new Date(iso).toLocaleString('es-CO', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })

export default function OralHistorial() {
  const carga = useCarga('/api/oral/historial/')

  return (
    <>
      <h1>Historial de práctica oral</h1>
      <Estado carga={carga}>
        {({ registros, resumen_oral: r }) => (
          <>
            {r.total > 0 && (
              <>
                <div className="card grid">
                  <div className="stat">
                    <b>{r.total}</b>
                    <span>prácticas</span>
                  </div>
                  <div className="stat">
                    <b>{r.dias}</b>
                    <span>días distintos</span>
                  </div>
                  <div className="stat">
                    <b>{r.minutos}</b>
                    <span>minutos hablando</span>
                  </div>
                  <div className="stat">
                    <b>{r.promedio}/5</b>
                    <span>fluidez (últimas 5)</span>
                  </div>
                </div>
                {r.promedio_anterior && (
                  <p className="muted">
                    Las 5 prácticas anteriores promediaban {r.promedio_anterior}/5. Es tu propia calificación, así que
                    úsala para ver tu tendencia, no como una medida exacta.
                  </p>
                )}
              </>
            )}

            <div className="card">
              <table>
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Pregunta</th>
                    <th>Duración</th>
                    <th>Fluidez</th>
                    <th>Nota</th>
                  </tr>
                </thead>
                <tbody>
                  {registros.length ? (
                    registros.map((x) => (
                      <tr key={x.id}>
                        <td>{fecha(x.creado)}</td>
                        <td>{x.pregunta}</td>
                        <td>{x.duracion_seg} s</td>
                        <td>{x.autoevaluacion}/5</td>
                        <td className="muted">{x.notas}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5}>Aún no hay prácticas. Empieza con la pregunta del día.</td>
                    </tr>
                  )}
                </tbody>
              </table>
              <div className="fila">
                <Link className="btn" to="/oral">
                  Practicar ahora
                </Link>
              </div>
            </div>
          </>
        )}
      </Estado>
    </>
  )
}
