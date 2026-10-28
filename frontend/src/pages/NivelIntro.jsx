import { Link } from 'react-router-dom'
import Estado from '../components/Estado'
import { useCarga } from '../useCarga'

export default function NivelIntro() {
  const carga = useCarga('/api/nivel/')

  return (
    <>
      <h1>Examen de nivel</h1>
      <Estado carga={carga}>
        {({ perfil, niveles, examen }) => (
          <div className="card">
            <p>
              Es un examen de opción múltiple (inglés → español) que <b>sube de dificultad</b> a medida que aciertas.
              Empiezas en el nivel 1 y avanzas por {niveles.length} niveles.
            </p>
            <ul>
              <li>
                Pasas de nivel al acertar <b>{examen.aciertos}</b> palabras. El examen termina cuando fallas{' '}
                <b>{examen.fallos}</b> en un mismo nivel, y ese es tu nivel.
              </li>
              <li>
                Responde sin buscar nada. Si no la sabes, usa <b>«No la sé»</b>: es mejor que adivinar.
              </li>
              <li>
                Durante el examen verás tres barras: tu avance, el nivel de dificultad donde estás y la racha de aciertos
                del nivel.
              </li>
              <li>Al final verás las palabras que fallaste. Es una estimación y puedes repetirlo cuando quieras.</li>
            </ul>
            <p className="muted">
              Niveles: {niveles.map((n) => `${n.numero} ${n.nombre} (${n.cefr})`).join(' · ')}. La equivalencia con A1–C2
              es aproximada.
            </p>
            {perfil.test_fecha && (
              <p className="muted">
                Tu último resultado: ~{perfil.vocab_estimado} palabras (
                {new Date(perfil.test_fecha).toLocaleDateString('es-CO')}).
              </p>
            )}
            <Link className="btn" to="/nivel/test">
              Empezar el examen
            </Link>
          </div>
        )}
      </Estado>
    </>
  )
}
