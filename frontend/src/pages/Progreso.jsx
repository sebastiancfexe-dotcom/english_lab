import { useState } from 'react'
import Estado from '../components/Estado'
import {
  BarrasH,
  Columnas,
  SERIES_ACTIVIDAD,
  Segmentado,
  TarjetaGrafica,
  Tile,
  fechaCorta,
  filasBloques,
  resumenPeriodo,
} from '../components/graficos'
import { useCarga } from '../useCarga'

const PERIODOS = [
  { valor: 7, nombre: '7 días' },
  { valor: 14, nombre: '14 días' },
  { valor: 30, nombre: '30 días' },
]

const fallos = (n) => `${n} fallo${n === 1 ? '' : 's'}`

export default function Progreso() {
  const carga = useCarga('/api/progreso/')
  const [dias, setDias] = useState(14)

  return (
    <>
      <div className="cabecera">
        <div>
          <h1>Progreso</h1>
          <p>Tus estadísticas de práctica.</p>
        </div>
      </div>

      <Segmentado etiqueta="Periodo" opciones={PERIODOS} valor={dias} onCambio={setDias} />

      <Estado carga={carga}>
        {({
          resumen,
          estado,
          actividad,
          bloques,
          resumen_oral: oral,
          por_tipo: porTipo,
          fallos_palabras: palabras,
          fallos_verbos: verbos,
        }) => {
          const tramo = actividad.slice(-dias)
          const p = resumenPeriodo(tramo)
          return (
            <>
              <div className="rejilla kpi">
                <Tile
                  etiqueta={`Respuestas · ${dias} días`}
                  valor={p.total}
                  sub={p.mejor.total ? `Mejor día: ${p.mejor.total} el ${fechaCorta(p.mejor.fecha)}` : 'Sin respuestas todavía'}
                  tendencia={tramo.map((d) => d.total)}
                />
                <Tile etiqueta="Precisión del periodo" valor={`${p.porcentaje}%`} sub={`${p.aciertos} aciertos de ${p.total}`} />
                <Tile
                  etiqueta="Días con práctica"
                  valor={`${p.diasActivos} de ${dias}`}
                  sub={`Racha actual: ${resumen.racha} ${resumen.racha === 1 ? 'día' : 'días'}`}
                />
                <Tile
                  etiqueta="Vocabulario dominado"
                  valor={estado.total}
                  sub={`de ${estado.meta} · ${estado.porcentaje_meta}% de la meta`}
                />
              </div>

              <TarjetaGrafica
                titulo="Actividad diaria"
                subtitulo={`Respuestas por día, últimos ${dias} días`}
                columnas={['Día', 'Aciertos', 'Fallos', 'Total']}
                filas={tramo.map((d) => [fechaCorta(d.fecha), d.aciertos, d.fallos, d.total])}
              >
                {p.total ? (
                  <Columnas datos={tramo} series={SERIES_ACTIVIDAD} altura={260} />
                ) : (
                  <p className="vacio-grafico">Aún no hay respuestas en este periodo.</p>
                )}
              </TarjetaGrafica>

              <div className="rejilla dos">
                <TarjetaGrafica
                  titulo="Precisión por tipo de práctica"
                  subtitulo="Porcentaje de aciertos acumulado"
                  columnas={['Tipo', 'Respuestas', 'Precisión']}
                  filas={porTipo.map((t) => [t.nombre, t.total, `${t.porcentaje}%`])}
                >
                  {porTipo.length ? (
                    <BarrasH
                      filas={porTipo.map((t) => ({
                        clave: t.nombre,
                        etiqueta: t.nombre,
                        valor: t.porcentaje,
                        detalle: `${t.total} respuestas`,
                      }))}
                    />
                  ) : (
                    <p className="vacio-grafico">Todavía no hay respuestas registradas.</p>
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

              {oral.total > 0 && (
                <div className="rejilla kpi">
                  <Tile etiqueta="Sesiones orales" valor={oral.total} sub={`en ${oral.dias} ${oral.dias === 1 ? 'día' : 'días'}`} />
                  <Tile etiqueta="Tiempo hablando" valor={`${oral.minutos} min`} sub="Acumulado" />
                  <Tile
                    etiqueta="Fluidez (últimas 5)"
                    valor={`${oral.promedio}/5`}
                    sub={oral.promedio_anterior ? `Las 5 anteriores: ${oral.promedio_anterior}/5` : 'Tu propia calificación'}
                  />
                </div>
              )}

              <div className="rejilla dos">
                <section className="card">
                  <h2>Palabras que más fallas</h2>
                  {palabras.length ? (
                    <table>
                      <tbody>
                        {palabras.map((x) => (
                          <tr key={x.ingles}>
                            <td>
                              <b>{x.ingles}</b> <span className="muted">= {x.espanol}</span>
                            </td>
                            <td className="num muted">{fallos(x.mal)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="muted">Todavía no hay fallos registrados.</p>
                  )}
                </section>

                <section className="card">
                  <h2>Verbos que más fallas</h2>
                  {verbos.length ? (
                    <table>
                      <tbody>
                        {verbos.map((v) => (
                          <tr key={v.infinitivo}>
                            <td>
                              <b>{v.infinitivo}</b> <span className="muted">→ {v.pasado} → {v.participio}</span>
                            </td>
                            <td className="num muted">{fallos(v.mal)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="muted">Todavía no hay fallos registrados.</p>
                  )}
                </section>
              </div>
            </>
          )
        }}
      </Estado>
    </>
  )
}
