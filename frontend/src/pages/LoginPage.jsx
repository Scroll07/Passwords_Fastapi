import { useState, useEffect } from "react"
import { NavLink } from "react-router-dom"
import './LoginPage.css'

function LoginPage() {
    const url = '/api/login'
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    
    async function send_request(e) {

        e.preventDefault()

        try {
            setLoading(true)
            setError('')

            const response = await fetch(
                url,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        'username': username,
                        'password': password
                    })
                }
            )

            if (! response.ok) {
                setError(response)
            }
            
            const data = await response.json()
            console.log(data)

        }catch (err) {
            setError(err)
            console.log(err)
        }finally {
            setLoading(false)
        }

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
                <NavLink to='/web/forgot-password'>Forgot password</NavLink>
                <p>Don’t have an account? <NavLink to='/web/register'>Sign up</NavLink> </p>
            </div>
        </div>
    </div>
</section>
    )
}



export default LoginPage