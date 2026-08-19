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
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DasboardPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import BackupPage from './pages/BackupPage'
import VaultsPage from './pages/VaultsPage'

import './App.css'


function App() {
  return (
    <Routes>
        <Route element={<BaseLayout/>}>

            <Route path='/' element={<HomePage />} />
            <Route path='/product' element={<ProductPage />} />
            <Route path='/how_it_works' element={<HowItWorksPage />} />
            <Route path='/pricing' element={<PricingPage />} />
            <Route path='/security' element={<SecurityPage />} />
            <Route path='/docs' element={<DocsPage />} />
            <Route path='/faq' element={<FaqPage />} />
            <Route path='/login' element={<LoginPage />} />
            <Route path='/register' element={<RegisterPage />} />
            <Route path='/dashboard' element={<DashboardPage />} />
            <Route path='/forgot-password' element={<ForgotPasswordPage />} />
            <Route path='/backups/:backup_id' element={<BackupPage />} />
            <Route path='/vaults' element={<VaultsPage />} />
            
        </Route>
    </Routes>
  )
}

export default App
