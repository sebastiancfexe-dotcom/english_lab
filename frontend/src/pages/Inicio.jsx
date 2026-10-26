import { useState } from 'react'
import { Link } from 'react-router-dom'
import Estado, { Barra } from '../components/Estado'
import Icono from '../components/Iconos'
import {
  Anillo,
  BarrasH,
  Columnas,
  SERIES_ACTIVIDAD,
  TarjetaGrafica,
  Tile,
  fechaCorta,
  filasBloques,
  resumenPeriodo,
} from '../components/graficos'
import { useAuth } from '../auth'
import { useCarga } from '../useCarga'

const DIAS_GRAFICA = 14

export default function Inicio() {
  const { usuario } = useAuth()
  const carga = useCarga('/api/inicio/')
  const [categoria, setCategoria] = useState('')

  // Con una categoría elegida, los botones de vocabulario la llevan en la URL.
  const destino = (ruta, extra = '') => {
    const params = new URLSearchParams(extra)
    if (categoria) params.set('categoria', categoria)
    const texto = params.toString()
    return texto ? `${ruta}?${texto}` : ruta
  }

  return (
    <Estado carga={carga}>
      {({ resumen, estado, actividad, bloques, resumen_oral: oral, categorias, categorias_tech: tech, tiempos }) => {
        const reciente = actividad.slice(-DIAS_GRAFICA)
        const periodo = resumenPeriodo(reciente)
        const hizoTest = Boolean(estado.perfil.test_fecha)

        return (
          <>
            <div className="cabecera">
              <div>
                <h1>Hola, {usuario.username}</h1>
                <p>Así va tu inglés. Practica un poco cada día y sube tu racha.</p>
              </div>
              <Link className="btn" to="/tarjetas">
                Practicar ahora
              </Link>
            </div>

            {!hizoTest ? (
              <div className="card marca heroe">
                <div>
                  <h2>Empieza por tu nivel</h2>
                  <p>Un test de 50 preguntas rápidas me dice cuántas palabras conoces y desde dónde practicar.</p>
                  <Link className="btn" to="/nivel">
                    Hacer el test de nivel
                  </Link>
                </div>
              </div>
            ) : (
              <div className="card heroe">
                <div>
                  <div className="muted">Nivel de vocabulario · {estado.etiqueta}</div>
                  <div className="heroe-cifra">
                    {estado.total} <small>de {estado.meta} palabras dominadas</small>
                  </div>
                  <p style={{ margin: '10px 0 14px' }}>
                    {estado.bloque_activo ? (
                      <>
                        Ahora trabajas el <b>bloque {estado.bloque_activo}</b> de {estado.ultimo_bloque}.
                      </>
                    ) : (
                      'Completaste el núcleo.'
                    )}
                  </p>
                  <Barra valor={estado.porcentaje_meta} />
                  <div className="fila">
                    <Link className="btn sec" to="/nivel/resultado">
                      Ver mi nivel
                    </Link>
                    <Link className="btn sec" to="/consejos">
                      Consejos
                    </Link>
                    {estado.desbloqueado || usuario.is_staff ? (
                      <Link className="btn sec" to="/mis-palabras">
                        Agregar mis palabras
                      </Link>
                    ) : (
                      <span className="muted" style={{ alignSelf: 'center', fontSize: 13.5 }}>
                        Tus propias palabras se desbloquean con {estado.desbloquea_en}.
                      </span>
                    )}
                  </div>
                </div>
                <Anillo valor={estado.porcentaje_meta} etiqueta="de la meta" />
              </div>
            )}

            <div className="rejilla kpi">
              <Tile
                etiqueta="Racha"
                valor={resumen.racha}
                sub={resumen.racha === 1 ? 'día seguido' : 'días seguidos'}
              />
              <Tile
                etiqueta="Respuestas hoy"
                valor={resumen.hoy}
                sub={`${periodo.total} en los últimos ${DIAS_GRAFICA} días`}
                tendencia={reciente.map((d) => d.total)}
              />
              <Tile
                etiqueta="Precisión"
                valor={`${resumen.porcentaje}%`}
                sub={`${resumen.aciertos} aciertos de ${resumen.total}`}
              />
              <Tile
                etiqueta="Práctica oral"
                valor={oral.total ? `${oral.minutos} min` : '—'}
                sub={oral.total ? `${oral.total} sesiones · fluidez ${oral.promedio}/5` : 'Aún sin sesiones'}
              />
            </div>

            <div className="rejilla dos">
              <TarjetaGrafica
                titulo="Actividad"
                subtitulo={`Respuestas por día, últimos ${DIAS_GRAFICA} días`}
                columnas={['Día', 'Aciertos', 'Fallos', 'Total']}
                filas={reciente.map((d) => [fechaCorta(d.fecha), d.aciertos, d.fallos, d.total])}
              >
                {periodo.total ? (
                  <Columnas datos={reciente} series={SERIES_ACTIVIDAD} />
                ) : (
                  <p className="vacio-grafico">Aún no hay respuestas en este periodo. Empieza con unas tarjetas.</p>
                )}
              </TarjetaGrafica>

              <TarjetaGrafica
                titulo="Dominio por bloque"
                subtitulo="Palabras dominadas de cada bloque del núcleo"
                columnas={['Bloque', 'Dominadas', 'Total', '%']}
                filas={bloques.map((b) => [`Bloque ${b.numero}`, b.dominadas, b.total, `${b.porcentaje}%`])}
              >
                <BarrasH filas={filasBloques(bloques, estado.bloque_activo)} />
              </TarjetaGrafica>
            </div>

            <h2 style={{ margin: '28px 0 12px' }}>Practicar</h2>
            <div className="rejilla acciones">
              <section className="card accion">
                <div className="accion-icono">
                  <Icono nombre="tarjetas" />
                </div>
                <h2>Vocabulario diario</h2>
                <p className="muted">Sin elegir categoría, practicas tu bloque actual.</p>
                <select value={categoria} onChange={(e) => setCategoria(e.target.value)} aria-label="Categoría">
                  <option value="">Mi bloque actual</option>
                  {categorias.map((c) => (
                    <option key={c.slug} value={c.slug}>
                      {c.nombre}
                    </option>
                  ))}
                </select>
                <div className="fila">
                  <Link className="btn" to={destino('/tarjetas')}>
                    Tarjetas
                  </Link>
                  <Link className="btn sec" to={destino('/quiz/vocabulario')}>
                    Quiz
                  </Link>
                  <Link className="btn sec" to={destino('/quiz/vocabulario', 'modo=dictado')}>
                    Dictado
                  </Link>
                </div>
              </section>

              <section className="card accion">
                <div className="accion-icono">
                  <Icono nombre="hablar" />
                </div>
                <h2>Frases y práctica oral</h2>
                <p className="muted">Escucha, escribe y habla con frases completas.</p>
                <div className="fila">
                  <Link className="btn" to="/dictado/frases">
                    Dictado de frases
                  </Link>
                  <Link className="btn sec" to="/dictado/frases?tema=dev">
                    Frases de desarrollo
                  </Link>
                  <Link className="btn sec" to="/oral">
                    Pregunta del día
                  </Link>
                </div>
              </section>

              <section className="card accion">
                <div className="accion-icono">
                  <Icono nombre="verbos" />
                </div>
                <h2>Verbos</h2>
                <p className="muted">Completa la oración con la forma correcta del verbo.</p>
                <div className="fila">
                  {tiempos.map((t, i) => (
                    <Link key={t.clave} className={`btn ${i === 0 ? '' : 'sec'}`} to={`/quiz/verbos?tiempo=${t.clave}`}>
                      {t.nombre}
                    </Link>
                  ))}
                </div>
              </section>
            </div>

            {tech.length > 0 && (
              <section className="card" style={{ marginTop: 16 }}>
                <h2>Inglés para desarrolladores</h2>
                <p className="muted">
                  Vocabulario del día a día en la industria, con oración de ejemplo. Llevas {estado.tecnicas_dominadas} de{' '}
                  {estado.tecnicas_total} términos dominados.
                </p>
                <div style={{ margin: '12px 0' }}>
                  <Barra
                    valor={
                      estado.tecnicas_total ? Math.round((100 * estado.tecnicas_dominadas) / estado.tecnicas_total) : 0
                    }
                  />
                </div>
                <table>
                  <tbody>
                    {tech.map((c) => (
                      <tr key={c.slug}>
                        <td>{c.nombre}</td>
                        <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                          <Link className="btn sec chico" to={`/tarjetas?categoria=${c.slug}`}>
                            Tarjetas
                          </Link>{' '}
                          <Link className="btn sec chico" to={`/quiz/vocabulario?categoria=${c.slug}`}>
                            Quiz
                          </Link>{' '}
                          <Link className="btn sec chico" to={`/quiz/vocabulario?modo=dictado&categoria=${c.slug}`}>
                            Dictado
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            )}
          </>
        )
      }}
    </Estado>
  )
}
