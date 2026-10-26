import { Link } from 'react-router-dom'
import Estado from '../components/Estado'
import { useCarga } from '../useCarga'

export default function Consejos() {
  const carga = useCarga('/api/consejos/')

  return (
    <>
      <h1>Cómo aprender vocabulario</h1>
      <Estado carga={carga}>
        {({ estado, faltan, plan }) => (
          <div className="card">
            <h2>Tu plan</h2>
            {!estado.perfil.test_fecha ? (
              <>
                <p>Aún no haces el test de nivel. Con él te digo desde dónde empezar.</p>
                <Link className="btn" to="/nivel">
                  Hacer el test de nivel
                </Link>
              </>
            ) : (
              <>
                <p>
                  Nivel: <b>{estado.etiqueta}</b> (~{estado.perfil.vocab_estimado} palabras). Dominadas hasta ahora:{' '}
                  <b>{estado.total}</b> de {estado.meta}.
                </p>
                {faltan > 0 ? (
                  <>
                    <p>
                      Te faltan unas <b>{faltan}</b> palabras para la meta. Aprendiendo palabras nuevas cada día:
                    </p>
                    <table>
                      <thead>
                        <tr>
                          <th>Palabras nuevas al día</th>
                          <th>Tiempo para la meta</th>
                        </tr>
                      </thead>
                      <tbody>
                        {plan.map((p) => (
                          <tr key={p.por_dia}>
                            <td>{p.por_dia}</td>
                            <td>~{p.dias} días</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p className="muted">
                      Recomendado: 10 al día. Es el ritmo que casi todo el mundo sostiene sin quemarse.
                    </p>
                  </>
                ) : (
                  <p>Ya llegaste a la meta. Sigue repasando y agrega tus propias palabras.</p>
                )}
              </>
            )}
          </div>
        )}
      </Estado>

      <div className="card">
        <h2>Rutina diaria (15 a 20 minutos)</h2>
        <ol>
          <li>
            <b>Repasa primero (5 min).</b> Haz el quiz: las palabras que fallas aparecen más seguido.
          </li>
          <li>
            <b>Aprende pocas palabras nuevas (5 min).</b> Entre 5 y 10 al día; más de eso se olvida.
          </li>
          <li>
            <b>Úsalas (5 min).</b> Escribe o di en voz alta una frase propia con cada palabra nueva.
          </li>
          <li>
            <b>Escucha (5 min).</b> Un podcast o video corto en inglés con subtítulos en inglés.
          </li>
        </ol>
      </div>

      <div className="card">
        <h2>Qué funciona mejor</h2>
        <ul>
          <li>
            <b>Constancia sobre cantidad.</b> 15 minutos diarios rinden más que 2 horas el domingo.
          </li>
          <li>
            <b>Recordar activamente.</b> Intentar decir o escribir la palabra antes de ver la respuesta fija más que
            releer. Por eso el quiz va por encima de leer listas.
          </li>
          <li>
            <b>Repetición espaciada.</b> Repasar a los 1, 3, 7 y 14 días. La app ya prioriza lo que fallas.
          </li>
          <li>
            <b>Aprende en frases, no sueltas.</b> «I need water» enseña más que «water», porque ves cómo se usa.
          </li>
          <li>
            <b>Primero lo más frecuente.</b> Las 1000 palabras más comunes cubren la mayor parte de lo que se oye en el
            día a día, por eso empiezas por ahí.
          </li>
          <li>
            <b>Di las palabras en voz alta.</b> Usa el botón de audio y repite imitando la pronunciación.
          </li>
          <li>
            <b>Conecta con tu vida.</b> Ponle nombre en inglés a los objetos de tu casa y a tus tareas del día.
          </li>
          <li>
            <b>Acepta fallar.</b> El error es lo que más enseña, y la app lo registra para repasarlo.
          </li>
        </ul>
      </div>

      <div className="card">
        <h2>Para entrar a la industria del software</h2>
        <p>Tu trabajo ya ocurre en inglés: documentación, código, tickets y reuniones. Aprovecha eso.</p>
        <ul>
          <li>
            <b>Escribe tus commits y pull requests en inglés</b>, aunque el equipo sea hispanohablante. Es práctica diaria
            y gratis.
          </li>
          <li>
            <b>Lee documentación oficial y README en inglés</b> antes de buscar traducciones o videos en español.
          </li>
          <li>
            <b>Prepara tu standup por escrito:</b> «Yesterday I… Today I will… I am blocked by…». Tres frases, todos los
            días.
          </li>
          <li>
            <b>Explica tu código en voz alta en inglés</b> (rubber duck). Grábate y escúchate: es el mejor ensayo para una
            entrevista técnica.
          </li>
          <li>
            <b>Pon en inglés tu IDE, tu terminal y tu sistema.</b> Los mensajes de error son vocabulario que vas a
            necesitar.
          </li>
          <li>
            <b>Prepara 5 historias de entrevista</b> (un conflicto, un fallo, un logro, un reto técnico, un trabajo en
            equipo) y ensáyalas en inglés.
          </li>
          <li>
            <b>Contribuye a un proyecto open source pequeño:</b> los issues y las revisiones son comunicación técnica
            real.
          </li>
          <li>
            <b>Mira charlas de conferencias</b> (con subtítulos en inglés) sobre las tecnologías que usas.
          </li>
        </ul>
        <p className="muted">
          En la app: usa las categorías «Dev» desde el inicio. Con la oración de ejemplo, intenta cambiarla por una de tu
          propio proyecto.
        </p>
      </div>

      <div className="card">
        <h2>Complementos fuera de la app</h2>
        <ul>
          <li>Series o películas que ya conoces, con audio en inglés y subtítulos en inglés.</li>
          <li>
            Libros graduados (<i>graded readers</i>) de nivel básico.
          </li>
          <li>Canciones con letra: busca solo las palabras que se repiten.</li>
          <li>Un cuaderno donde anotes 3 frases al día sobre tu jornada, aunque sean simples.</li>
          <li>Cambiar el idioma del celular a inglés.</li>
          <li>Hablar con alguien, aunque sea 10 minutos por semana. Si no hay con quién, grábate hablando.</li>
        </ul>
      </div>
    </>
  )
}
