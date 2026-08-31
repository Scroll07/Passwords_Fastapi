import { useState, useEffect } from "react"
import { NavLink } from "react-router-dom"
import './LoginPage.css'

function LoginPage() {
    const url = '/web/login'
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    
    function check_creds() {
        const clear_username = username.trim()
        const clear_password = password.trim()

        let error_in_creds = ''
        
        if (clear_username.includes(' ')) {
            error_in_creds = "Username must not contain spaces"
        }
        else if (clear_password.includes(' ')) {
            error_in_creds = "Password must not contain spaces"
        }
        else if (clear_username.length < 4 || clear_username.length > 32) {
            error_in_creds = "Wrong length of username"
        }
        else if (clear_password.length < 4 || clear_password.length > 32) {
            error_in_creds = "Wrong length of password"
        }

        return {
            "username": clear_username,
            "password": clear_password,
            "error": error_in_creds
        }
    }

    async function send_request(e) {
        e.preventDefault()

        const data = check_creds()

        if (data["error"]) {
            await show_error(data["error"])
            return
        }

        const response = await fetch(
            url,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'username': data["username"],
                    'password': data["password"]
                })
            }
        )

        if (response.ok) {
            window.location.href = "/vaults"
            return
        }
        
        if (response.headers.get("content-type").includes("application/json")) {
            const response_data = await response.json()
            const response_error = response_data["detail"] || "No detail of error from server"
            await show_error(response_error)
            return
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, "text/html")
            const nginx_error = nginx_document.title 
            await show_error(nginx_error.slice(4))
            return
        }
    }

    function sleep(ms) {
        return new Promise(resolve => {setTimeout(resolve, ms)})
    }
    async function show_error(error_text) {
        SetError(error_text)
        await sleep(3500)
        SetError('')
    }
    
    
    return (
        <section className="auth-section">
            <div className="auth-container">
                <div className="auth-card">
                    { error &&
                        <div className="form-error">{error}</div>
                    }
                                    
                    <h1>Login</h1>

                    <form className="auth-form" id="auth-form" method="post" onSubmit={send_request}>
                        <div className="form-group">
                            <label htmlFor="username">username</label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                placeholder="username"
                                required
                                value={username}
                                onChange={event => setUsername(event.target.value)}
                                />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">password</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                placeholder="••••••••"
                                required
                                value={password}
                                onChange={event => setPassword(event.target.value)}
                                />
                        </div>

                        <button type="submit" className="auth-submit">Sign in</button>
                    </form>

                    <div className="auth-links">
                        <NavLink to='/forgot-password'>Forgot password</NavLink>
                        <p>Don’t have an account? <NavLink to='/register'>Sign up</NavLink> </p>
                    </div>
                </div>
            </div>
        </section>
    )
}
    
    
    
    
    export default LoginPage