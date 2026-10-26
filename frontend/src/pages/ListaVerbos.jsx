import Estado from '../components/Estado'
import { useCarga } from '../useCarga'

export default function ListaVerbos() {
  const carga = useCarga('/api/verbos/')

  return (
    <>
      <h1>Lista de verbos</h1>
      <Estado carga={carga}>
        {({ verbos }) => (
          <div className="card">
            <table>
              <thead>
                <tr>
                  <th>Presente</th>
                  <th>3.ª persona</th>
                  <th>Pasado</th>
                  <th>Participio</th>
                  <th>Español</th>
                </tr>
              </thead>
              <tbody>
                {verbos.length ? (
                  verbos.map((v) => (
                    <tr key={v.infinitivo}>
                      <td>
                        <b>{v.infinitivo}</b>
                        {v.irregular && (
                          <span className="muted" title="Irregular">
                            {' '}
                            *
                          </span>
                        )}
                      </td>
                      <td>{v.tercera_persona}</td>
                      <td>{v.pasado}</td>
                      <td>{v.participio}</td>
                      <td>{v.espanol}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5}>
                      Aún no hay verbos. Ejecuta <code>python manage.py cargar_datos</code>.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
            <p className="muted">* verbo irregular</p>
          </div>
        )}
      </Estado>
    </>
  )
}
