import { Link } from 'react-router-dom'
import Estado from '../components/Estado'
import { useCarga } from '../useCarga'

export default function NivelIntro() {
  const carga = useCarga('/api/nivel/')

  return (
    <>
      <h1>Test de nivel</h1>
      <Estado carga={carga}>
        {({ perfil, preguntas_total: total }) => (
          <div className="card">
            <p>
              Son <b>{total} preguntas</b> de opción múltiple (inglés → español), repartidas en 10 bloques de dificultad
              creciente.
            </p>
            <ul>
              <li>
                Responde rápido, sin buscar nada. Si no la sabes, usa <b>«No la sé»</b>: adivinar baja la precisión de tu
                resultado.
              </li>
              <li>Con tus aciertos estimo cuántas palabras conoces y desde qué bloque conviene empezar.</li>
              <li>Es una estimación. Puedes repetir el test cuando quieras.</li>
            </ul>
            {perfil.test_fecha && (
              <p className="muted">
                Tu último resultado: ~{perfil.vocab_estimado} palabras (
                {new Date(perfil.test_fecha).toLocaleDateString('es-CO')}).
              </p>
            )}
            <Link className="btn" to="/nivel/test">
              Empezar el test
            </Link>
          </div>
        )}
      </Estado>
    </>
  )
}
