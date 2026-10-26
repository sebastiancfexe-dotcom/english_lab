import { Link } from 'react-router-dom'
import Estado, { Vacio } from '../components/Estado'
import { useCarga } from '../useCarga'
import { hablar } from '../voz'

export default function Vocabulario() {
  const carga = useCarga('/api/vocabulario/')

  return (
    <>
      <h1>Vocabulario</h1>
      <Estado carga={carga}>
        {({ categorias }) =>
          categorias.length ? (
            categorias.map((c, i) => (
              <details key={c.slug} className="card" open={i < 2 && c.slug !== 'general'}>
                <summary>
                  <b>{c.nombre}</b> <span className="muted">({c.palabras.length})</span>
                </summary>
                <table>
                  <thead>
                    <tr>
                      <th>Inglés</th>
                      <th>Español</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {c.palabras.map((p) => (
                      <tr key={p.id}>
                        <td>{p.ingles}</td>
                        <td>{p.espanol}</td>
                        <td>
                          <button className="btn sec" type="button" onClick={() => hablar(p.ingles)}>
                            🔊
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="fila">
                  <Link className="btn" to={`/tarjetas?categoria=${c.slug}`}>
                    Practicar con tarjetas
                  </Link>
                  <Link className="btn sec" to={`/quiz/vocabulario?categoria=${c.slug}`}>
                    Quiz
                  </Link>
                </div>
              </details>
            ))
          ) : (
            <Vacio />
          )
        }
      </Estado>
    </>
  )
}
