import { Routes, Route } from 'react-router-dom'

import BaseLayout from './layouts/BaseLayout'
import HomePage from './pages/HomePage'
import ProductPage from './pages/ProductPage'
import HowItWorksPage from './pages/HowItWorks'
import PricingPage from './pages/Pricing'
import SecurityPage from './pages/Security'
import DocsPage from './pages/Docs'
import FaqPage from './pages/FAQ'
import LoginPage from './pages/LoginPage'
// import './App.css'

function App() {
  return (
    <Routes>
        <Route element={<BaseLayout/>}>

            <Route path='/web/' element={<HomePage />} />
            <Route path='/web/product' element={<ProductPage />} />
            <Route path='/web/how_it_works' element={<HowItWorksPage />} />
            <Route path='/web/pricing' element={<PricingPage />} />
            <Route path='/web/security' element={<SecurityPage />} />
            <Route path='/web/docs' element={<DocsPage />} />
            <Route path='/web/faq' element={<FaqPage />} />
            <Route path='/web/login' element={<LoginPage />} />
        </Route>
    </Routes>
  )
}

export default App
