import { useCallback, useEffect, useState } from 'react'
import { api } from './api'

/** GET a `ruta` al montar y cada vez que cambia. `recargar()` repite la petición. */
export function useCarga(ruta) {
  const [estado, setEstado] = useState({ datos: null, error: null, cargando: true })
  const [ronda, setRonda] = useState(0)

  useEffect(() => {
    let vigente = true
    setEstado((e) => ({ ...e, cargando: true, error: null }))
    api
      .get(ruta)
      .then((datos) => vigente && setEstado({ datos, error: null, cargando: false }))
      .catch((error) => vigente && setEstado({ datos: null, error, cargando: false }))
    return () => {
      vigente = false
    }
  }, [ruta, ronda])

  const recargar = useCallback(() => setRonda((n) => n + 1), [])
  return { ...estado, recargar }
}
