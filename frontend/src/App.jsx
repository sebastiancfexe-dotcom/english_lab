import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Consejos from './pages/Consejos'
import DictadoFrases from './pages/DictadoFrases'
import Inicio from './pages/Inicio'
import ListaVerbos from './pages/ListaVerbos'
import Login from './pages/Login'
import MisPalabras from './pages/MisPalabras'
import NivelIntro from './pages/NivelIntro'
import NivelResultado from './pages/NivelResultado'
import NivelTest from './pages/NivelTest'
import Oral from './pages/Oral'
import OralHistorial from './pages/OralHistorial'
import Progreso from './pages/Progreso'
import QuizVerbos from './pages/QuizVerbos'
import QuizVocab from './pages/QuizVocab'
import Registro from './pages/Registro'
import Tarjetas from './pages/Tarjetas'
import Vocabulario from './pages/Vocabulario'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="entrar" element={<Login />} />
        <Route path="registro" element={<Registro />} />
        <Route index element={<Inicio />} />
        <Route path="tarjetas" element={<Tarjetas />} />
        <Route path="quiz/vocabulario" element={<QuizVocab />} />
        <Route path="quiz/verbos" element={<QuizVerbos />} />
        <Route path="dictado/frases" element={<DictadoFrases />} />
        <Route path="oral" element={<Oral />} />
        <Route path="oral/historial" element={<OralHistorial />} />
        <Route path="vocabulario" element={<Vocabulario />} />
        <Route path="verbos" element={<ListaVerbos />} />
        <Route path="nivel" element={<NivelIntro />} />
        <Route path="nivel/test" element={<NivelTest />} />
        <Route path="nivel/resultado" element={<NivelResultado />} />
        <Route path="mis-palabras" element={<MisPalabras />} />
        <Route path="consejos" element={<Consejos />} />
        <Route path="progreso" element={<Progreso />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
