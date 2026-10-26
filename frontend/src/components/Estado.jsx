/** Estados comunes de una pantalla que carga datos: cargando, error y datos listos. */
export default function Estado({ carga, children }) {
  if (carga.cargando && !carga.datos) return <p className="muted">Cargando…</p>
  if (carga.error) {
    return (
      <div className="card">
        <p className="error">No se pudo cargar: {carga.error.message}</p>
        <button className="btn sec" type="button" onClick={carga.recargar}>
          Reintentar
        </button>
      </div>
    )
  }
  return carga.datos ? children(carga.datos) : null
}

export function Barra({ valor, color }) {
  return (
    <div className="barra">
      <i style={{ width: `${valor}%`, ...(color ? { background: color } : {}) }} />
    </div>
  )
}

export function Vacio() {
  return (
    <div className="card">
      Aún no hay datos. Ejecuta <code>python manage.py cargar_datos</code>.
    </div>
  )
}
