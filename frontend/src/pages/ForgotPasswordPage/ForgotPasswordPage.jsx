import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useNotification } from '../../hooks/useNotification.js'

import './ForgotPasswordPage.css'



function ForgotPasswordPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [new_password, setNewPassword] = useState('')
    
    const [
        error,
        message,
        showError,
        showMessage
    ] = useNotification()

    function validate_data() {
        const clear_username = username.trim()
        const clear_password = password.trim()
        const clear_new_password = new_password.trim()

        let error_in_creds = ''
        

        if (clear_username.includes(' ')) {
            error_in_creds = "Username must not contain spaces"
        }
        else if (clear_password.includes(' ')) {
            error_in_creds = "Password must not contain spaces"
        }
        else if (clear_new_password.includes(' ')) {
            error_in_creds = "New password must not contain spaces"
        }
        else if (clear_username.length < 4 || clear_username.length > 32) {
            error_in_creds = "Wrong length of username"
        }
        else if (clear_password.length < 4 || clear_password.length > 32) {
            error_in_creds = "Wrong length of password"
        }
        else if (clear_new_password.length < 4 || clear_new_password.length > 32) {
            error_in_creds = "Wrong length of new password"
        } 
        else if (clear_password === clear_new_password) {
            error_in_creds = "Old password can't be the same as new password"
        }

        return {
            "username": clear_username,
            "password": clear_password,
            "new_password": clear_new_password,
            "error": error_in_creds
        }
    }


    async function change_password_request(e) {
        e.preventDefault()

        const data = validate_data()
        if (data["error"]) {
            showError(data['error'])
            return
        } 

        const url = "/web/change-password" 

        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "username": data['username'],
                    "current_password": data['password'],
                    "new_password": data['new_password']
                })
            }
        )

        
        if (response.ok) {
            document.location.href = '/login'
            return
        } else if (response.headers.get('content-type').includes("application/json")) {
            const response_data = await response.json()
            const response_error = response_data['detail'] || "No detail from server"
            showError(response_error)
            console.log(`RESPONSE: ${response_error}`)
            return 
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, 'text/html')
            const nginx_error = nginx_document.title.slice(4)
            showError(nginx_error)
            return 
        }
    }
    





    return (
    <section className="auth-section">
        <div className="auth-container">
            <div className="auth-card">
                <h1>Change password</h1>

                { error && 
                <div className='form-error'>{error}</div>}

                <form className="auth-form" id="auth-form" method="post" onSubmit={change_password_request}>
                    <div className="form-group">
                        <label htmlFor="username">username</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            placeholder="username"
                            onChange={event => {setUsername(event.target.value)}}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="current_password">current password</label>
                        <input
                            type="password"
                            id="current_password"
                            name="current_password"
                            placeholder="••••••••"
                            onChange={event => {setPassword(event.target.value)}}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="new_password">new password</label>
                        <input
                            type="password"
                            id="new_password"
                            name="new_password"
                            placeholder="••••••••"
                            onChange={event => {setNewPassword(event.target.value)}}
                            required
                        />
                    </div>

                    <button type="submit" className="auth-submit">Update password</button>
                </form>

                <div className="auth-links auth-links-center">
                    <p>Remembered? <NavLink to="/login">Log in</NavLink></p>
                </div>
            </div>
        </div>
    </section>
    ) 
}


export default ForgotPasswordPage