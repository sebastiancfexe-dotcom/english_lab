import { Fragment, useEffect, useState } from 'react'
import { Link, NavLink, Navigate, Outlet, useLocation } from 'react-router-dom'
import { BASE } from '../api'
import { useAuth } from '../auth'
import Icono from './Iconos'

const GRUPOS = [
  {
    titulo: 'Principal',
    enlaces: [
      ['/', 'Panel', 'panel'],
      ['/progreso', 'Progreso', 'progreso'],
      ['/nivel', 'Mi nivel', 'nivel'],
    ],
  },
  {
    titulo: 'Practicar',
    enlaces: [
      ['/tarjetas', 'Tarjetas', 'tarjetas'],
      ['/quiz/vocabulario', 'Quiz', 'quiz'],
      ['/quiz/verbos', 'Verbos', 'verbos'],
      ['/dictado/frases', 'Frases', 'frases'],
      ['/oral', 'Hablar', 'hablar'],
    ],
  },
  {
    titulo: 'Biblioteca',
    enlaces: [
      ['/vocabulario', 'Vocabulario', 'vocabulario'],
      ['/verbos', 'Lista de verbos', 'lista'],
      ['/mis-palabras', 'Mis palabras', 'agregar'],
      ['/consejos', 'Consejos', 'consejos'],
    ],
  },
]

const PUBLICAS = ['/entrar', '/registro']

function Marca() {
  return (
    <Link className="logo" to="/">
      <span className="logo-marca">EL</span>
      <b>English Lab</b>
    </Link>
  )
}

export default function Layout() {
  const { usuario, cargando, salir } = useAuth()
  const { pathname } = useLocation()
  const [abierta, setAbierta] = useState(false)
  const publica = PUBLICAS.includes(pathname)

  useEffect(() => {
    window.scrollTo(0, 0)
    setAbierta(false)
  }, [pathname])

  if (cargando) return null
  if (!usuario && !publica) return <Navigate to="/entrar" replace />
  if (usuario && publica) return <Navigate to="/" replace />

  if (publica) {
    return (
      <div className="acceso">
        <div className="acceso-caja">
          <Marca />
          <Outlet />
        </div>
      </div>
    )
  }

  return (
    <>
      <aside className={`sidebar ${abierta ? 'abierta' : ''}`}>
        <Marca />
        <nav className="menu" aria-label="Principal">
          {GRUPOS.map((g) => (
            <Fragment key={g.titulo}>
              <div className="menu-grupo">{g.titulo}</div>
              {g.enlaces.map(([ruta, nombre, icono]) => (
                <NavLink key={ruta} to={ruta} end={ruta === '/'}>
                  <Icono nombre={icono} />
                  {nombre}
                </NavLink>
              ))}
            </Fragment>
          ))}
        </nav>
        <div className="sesion">
          <div className="sesion-usuario">
            <span className="avatar">{usuario.username[0]}</span>
            <div style={{ minWidth: 0 }}>
              <div className="sesion-nombre">{usuario.username}</div>
              <div className="sesion-rol">{usuario.is_staff ? 'Administrador' : 'Estudiante'}</div>
            </div>
          </div>
          <div className="sesion-botones">
            {usuario.is_staff && (
              <a className="btn sec" href={`${BASE}/admin/`} target="_blank" rel="noreferrer">
                <Icono nombre="admin" /> Admin
              </a>
            )}
            <button className="btn sec" type="button" onClick={salir}>
              <Icono nombre="salir" /> Salir
            </button>
          </div>
        </div>
      </aside>

      <div className={`velo ${abierta ? 'visible' : ''}`} onClick={() => setAbierta(false)} />

      <div className="contenido">
        <header className="barra-movil">
          <button type="button" aria-label="Abrir el menú" onClick={() => setAbierta(true)}>
            <Icono nombre="menu" />
          </button>
          <Marca />
        </header>
        <main>
          <Outlet />
        </main>
      </div>
    </>
  )
}
