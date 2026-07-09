import { Routes, Route } from 'react-router-dom'

import BaseLayout from './layouts/BaseLayout'
import HomePage from './pages/HomePage'
// import './App.css'


function App() {
  return (
    <Routes>
        <Route element={<BaseLayout/>}>

            <Route path='/' element={<HomePage />} />







        </Route>
    </Routes>
  )
}

export default App
