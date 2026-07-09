import { NavLink, Outlet } from "react-router-dom"

import Logo from '../../public/logo.png'
import Telegram from '../assets/images/telegram.png'
import Gmail from '../assets/images/gmail.png'
import GitHub from '../assets/images/github.png'

import './BaseLayout.css'

function BaseLayout() {
    return (
        <body>
            <header className="site-header">
                <div className="container header-inner">
                    <NavLink to="/" className="logo">
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
                        <NavLink to="/web/register" className="signup-btn">Sing Up</NavLink>
                    </div>
                </div>
            </header>

            <main>
                <Outlet />
            </main>

            <footer className="site-footer">
                <div className="container">
                    <div className="footer-top">
                        <div className="footer-brand">
                            <NavLink to="/" className="logo">
                                <img src={Logo} alt="Pas CLI logo" className="logo-image" />
                                <span className="logo-text">Pas CLI</span>
                            </NavLink>

                            <p>
                                A secure, API-first CLI password manager
                                for developers.
                            </p>

                            <div className="socials">
                                <a href="https://web.telegram.org/k/#@Bot_Passwordbot" target="_blank" rel="noopener noreferrer">
                                    <img src={Telegram} alt="Telegram" />
                                </a>
                                <a href="https://github.com/Scroll07/Passwords_Fastapi" target="_blank" rel="noopener noreferrer">
                                    <img src={GitHub} alt="Git Hub" />
                                </a>
                                <a href="mailto:vovanikolaev140707@gmai.com" target="_blank" rel="noopener noreferrer">
                                    <img src={Gmail} alt="Gmail" />
                                </a>
                            </div>
                        </div>

                        <div className="footer-column">
                            <h3>Product</h3>
                            <NavLink to="/web/product">Features</NavLink>
                            <NavLink to="/web/how_it_works">How It Works</NavLink>
                            <NavLink to="/web/pricing">Pricing</NavLink>
                            <NavLink to="/web/security">Security</NavLink>
                        </div>

                        <div className="footer-column">
                            <h3>Resources</h3>
                            <NavLink to="/web/docs">Documentation</NavLink>
                            <NavLink to="/web/faq">FAQ</NavLink>
                            <NavLink to="#">API Reference</NavLink>
                            <NavLink to="#">Status</NavLink>
                        </div>

                        <div className="footer-column">
                            <h3>Company</h3>
                            <a href="#">About</a>
                            <a href="#">Contact</a>
                            <a href="#">Privacy</a>
                            <a href="#">Terms</a>
                        </div>
                    </div>

                    <div className="footer-bottom">
                        <p>© 2026 Pas CLI. All rights reserved.</p>

                        <div className="footer-legal">
                            <a href="#">Privacy Policy</a>
                            <a href="#">Terms of Service</a>
                            <a href="#">Cookie Policy</a>
                        </div>
                    </div>
                </div>
            </footer>
        </body>
    )
}

export default BaseLayout