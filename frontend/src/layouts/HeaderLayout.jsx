import { NavLink } from "react-router-dom";
import Logo from '../assets/images/logo.png'
import './BaseLayout.css'

function HeaderLayout() {
    return (
        <header className="site-header">
                <div className="container header-inner">
                    <NavLink to="/web/" className="logo">
                        <img src={Logo} alt="Pas CLI logo" className="logo-image" />
                        <span className="logo-text">Pas CLI</span>
                    </NavLink>

                    <nav className="main-nav">
                        <NavLink to="/web/product">Product</NavLink>
                        <NavLink to="/web/how_it_works">How It Works</NavLink>
                        <NavLink to="/web/pricing">Pricing</NavLink>
                        <NavLink to="/web/security">Security</NavLink>
                        <NavLink to="/web/docs">Docs</NavLink>
                        <NavLink to="/web/faq">FAQ</NavLink>
                    </nav>

                    <div className="header-actions">
                        <NavLink to="/web/dashboard" className="login-link">Dashboard</NavLink>
                        <NavLink to="/web/login" className="login-link">Login</NavLink>
                        <NavLink to="/web/register" className="signup-btn">Sign Up</NavLink>
                    </div>
                </div>
            </header>
    )
}

export default HeaderLayout