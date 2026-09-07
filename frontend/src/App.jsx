import { Routes, Route } from 'react-router-dom'

import BaseLayout from './layouts/BaseLayout'
import HomePage from './pages/HomePage/HomePage'
import ProductPage from './pages/ProductPage/ProductPage'
import HowItWorksPage from './pages/HowItWorksPage/HowItWorks'
import PricingPage from './pages/PricingPage/Pricing'
import SecurityPage from './pages/SecurityPage/Security'
import DocsPage from './pages/DocsPage/Docs'
import FaqPage from './pages/FAQPage/FAQ'
import LoginPage from './pages/LoginPage/LoginPage'
import RegisterPage from './pages/RegisterPage/RegisterPage'
import DashboardPage from './pages/DashboardPage/DashboardPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage/ForgotPasswordPage'
import BackupPage from './pages/BackupPage/BackupPage'
import VaultsPage from './pages/VaultsPage/VaultsPage'
import VaultPage from './pages/VaultPage/VaultPage'
import CreateVaultPage from './pages/CreateVaultPage/CreateVaultPage'
import CreatePasswordPage from './pages/CreatePasswordPage/CreatePasswordPage'
import VaultSettingsPage from './pages/VaultSettingsPage/VaultSettingsPage'
import PasswordPage from './pages/PasswordPage/PasswordPage'


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
            <Route path='/vaults/:vault_id' element={<VaultPage />} />
            <Route path='/vaults/create' element={<CreateVaultPage />} />
            <Route path='/vaults/:vault_id/settings' element={<VaultSettingsPage />} />
            <Route path='/vaults/:vault_id/entries/new' element={<CreatePasswordPage />} />
            <Route path='/vaults/:vault_id/entries/:service' element={<PasswordPage />} />
            
        </Route>
    </Routes>
  )
}

export default App
