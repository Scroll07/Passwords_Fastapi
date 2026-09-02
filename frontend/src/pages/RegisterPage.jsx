import { useState, useEffect } from "react"
import { NavLink } from "react-router-dom"
import { useNotification } from '../hooks/useNotification.js'

import './RegisterPage.css'



function RegisterPage() {
    const url = '/api/register'
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [confirm_password, setConfirmPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [
        error,
        message,
        showError,
        showMessage
    ] = useNotification()


    function check_creds() {
        const clear_username = username.trim()
        const clear_password = password.trim()
        const clear_confirm_password = confirm_password.trim()

        let error_in_creds = ''
        

        if (clear_username.includes(' ')) {
            error_in_creds = "Username must not contain spaces"
        }
        else if (clear_password.includes(' ')) {
            error_in_creds = "Password must not contain spaces"
        }
        else if (clear_confirm_password.includes(' ')) {
            error_in_creds = "Confirm password must not contain spaces"
        }
        else if (clear_username.length < 4 || clear_username.length > 32) {
            error_in_creds = "Wrong length of username"
        }
        else if (clear_password.length < 4 || clear_password.length > 32) {
            error_in_creds = "Wrong length of password"
        }
        else if (clear_confirm_password.length < 4 || clear_confirm_password.length > 32) {
            error_in_creds = "Wrong length of confirm password"
        }
        else if (clear_password != clear_confirm_password) {
            error_in_creds = "Passwords should be the same"
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
            setError(data["error"])
            return
        }

        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "username": data["username"],
                    "password": data["password"]
                })
            }
        )

        if (response.ok) {
            window.location.href = "/login"
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


        


    return (
        <section className="auth-section">
        <div className="auth-container">
            <div className="auth-card">
                
                { error &&
                    <div className="form-error">{error}</div>
                }
                
                <h1>Create account</h1>

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

                    <div className="form-group">
                        <label htmlFor="confirm_password">confirm password</label>
                        <input
                            type="password"
                            id="confirm_password"
                            name="confirm_password"
                            placeholder="••••••••"
                            required
                            value={confirm_password}
                            onChange={event => setConfirmPassword(event.target.value)}
                        />
                    </div>

                    <button type="submit" className="auth-submit">Create account</button>
                </form>

                <div className="auth-links auth-links-center">
                    <p>Already have an account? <NavLink to="/login">Log In</NavLink></p>
                </div>
            </div>
        </div>
        </section>



    )
}


export default RegisterPage