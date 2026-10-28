import { Link, Navigate } from 'react-router-dom'
import Estado, { Barra } from '../components/Estado'
import { useCarga } from '../useCarga'

export default function NivelResultado() {
  const carga = useCarga('/api/nivel/resultado/')
  // 404: todavía no hizo el test
  if (carga.error?.status === 404) return <Navigate to="/nivel" replace />

  return (
    <Estado carga={carga}>
      {({ estado, bloques, niveles, errores, completo }) => {
        const perfil = estado.perfil
        // Nivel alcanzado = el último aprobado; si no aprobó ninguno, el primero.
        const alcanzado = niveles[Math.min(Math.max(perfil.nivel_inicial - 1, 1), niveles.length) - 1]
        return (
          <>
            <h1>
              Tu nivel: {alcanzado.nombre} <span className="muted">({alcanzado.cefr})</span>
            </h1>

            <div className="card grid">
              <div className="stat">
                <b>~{perfil.vocab_estimado}</b>
                <span>palabras estimadas</span>
              </div>
              <div className="stat">
                <b>{completo ? '✓' : perfil.nivel_inicial}</b>
                <span>{completo ? 'núcleo completo' : 'nivel donde empiezas'}</span>
              </div>
              <div className="stat">
                <b>{estado.porcentaje_meta}%</b>
                <span>de la meta de {estado.meta}</span>
              </div>
            </div>

            <div className="card">
              <h2>Resultado por nivel</h2>
              <p className="muted">
                Nivel 1 = palabras más básicas, nivel 10 = las más difíciles del núcleo. Verde: nivel aprobado.
              </p>
              {bloques.map((b) => (
                <div key={b.numero}>
                  <p>
                    Nivel {b.numero} · {b.total ? `${b.dominio}%` : 'sin evaluar'}{' '}
                    <span className="muted">
                      ({b.aciertos}/{b.total} aciertos)
                    </span>
                  </p>
                  <Barra valor={b.dominio} color={(b.aprobado ?? b.dominio >= 80) ? 'var(--brand-mark)' : undefined} />
                </div>
              ))}
            </div>

            <div className="card">
              <h2>Palabras que fallaste</h2>
              {errores.length ? (
                <>
                  <p className="muted">{errores.length} en total. Repásalas: tu respuesta aparece tachada.</p>
                  <table>
                    <thead>
                      <tr>
                        <th>Inglés</th>
                        <th>Significa</th>
                        <th>Tu respuesta</th>
                        <th>Nivel</th>
                      </tr>
                    </thead>
                    <tbody>
                      {errores.map((e) => (
                        <tr key={e.ingles}>
                          <td>
                            <b>{e.ingles}</b>
                          </td>
                          <td>{e.correcta}</td>
                          <td className="muted">{e.elegida ? <s>{e.elegida}</s> : 'No la sé'}</td>
                          <td>{e.bloque}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              ) : (
                <p>¡No fallaste ninguna palabra!</p>
              )}
            </div>

            <div className="card">
              {completo ? (
                <>
                  <p>Dominas el núcleo. Ya puedes agregar tus propias palabras.</p>
                  <Link className="btn" to="/mis-palabras">
                    Agregar palabras
                  </Link>
                </>
              ) : (
                <>
                  <p>
                    Las palabras de los niveles anteriores al {perfil.nivel_inicial} se dan por conocidas. La práctica se
                    centra desde el nivel {perfil.nivel_inicial}, y avanzas al siguiente cuando domines el 80% del actual.
                  </p>
                  <div className="fila">
                    <Link className="btn" to="/tarjetas">
                      Practicar ahora
                    </Link>
                    <Link className="btn sec" to="/consejos">
                      Ver consejos para aprender
                    </Link>
                    <Link className="btn sec" to="/nivel">
                      Repetir el examen
                    </Link>
                  </div>
                </>
              )}
            </div>
          </>
        )
      }}
    </Estado>
  )
}
