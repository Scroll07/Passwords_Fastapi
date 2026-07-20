import { NavLink } from "react-router-dom";
import Logo from '../assets/images/logo.png'
import './BaseLayout.css'

function HeaderLayout() {
    return (
        <header className="site-header">
                <div className="container header-inner">
                    <NavLink to="/" className="logo">
                        <img src={Logo} alt="Pas CLI logo" className="logo-image" />
                        <span className="logo-text">Pas CLI</span>
                    </NavLink>

                    <nav className="main-nav">
                        <NavLink to="/product">Product</NavLink>
                        <NavLink to="/how_it_works">How It Works</NavLink>
                        <NavLink to="/pricing">Pricing</NavLink>
                        <NavLink to="/security">Security</NavLink>
                        <NavLink to="/docs">Docs</NavLink>
                        <NavLink to="/faq">FAQ</NavLink>
                    </nav>

                    <div className="header-actions">
                        <NavLink to="/dashboard" className="login-link">Dashboard</NavLink>
                        <NavLink to="/login" className="login-link">Login</NavLink>
                        <NavLink to="/register" className="signup-btn">Sign Up</NavLink>
                    </div>
                </div>
            </header>
    )
}

export default HeaderLayout