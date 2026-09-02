import { useState, useEffect } from "react"
import { NavLink, useParams } from "react-router-dom"
import { useNotification } from '../hooks/useNotification.js'
import './CreatePasswordPage.css'

function CreatePasswordPage() {
    const params = useParams()
    const vault_id = Number(params.vault_id)
    const [isLoading, SetLoading] = useState(true)
    const [service, SetService] = useState('')
    const [login, SetLogin] = useState('')
    const [password, SetPasword] = useState('')
    const [note, SetNote] = useState('')
    const [generatePassword, SetGeneratePassword] = useState(false)

    const [
            error,
            message,
            showError,
            showMessage
        ] = useNotification()

    useEffect(() => {
        async function check_user_access() {
            const url = `/web/vaults/${vault_id}/status`
            const response = await fetch(
                url,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                }
            )
            const contentType = response.headers.get("content-type")
            if (response.ok) {
                SetLoading(false)
                return
            } else if (contentType && contentType.includes('application/json')){
                const response_data = await response.json()
                const response_error = response_data['detail'] || "No detail from server"
                console.log(response_error)
                document.location.href = '/vaults'
                return
            } else {
                const text = await response.text()
                const parser = new DOMParser()
                const nginx_document = parser.parseFromString(text, 'text/html')
                const nginx_error = nginx_document.title.slice(4)
                console.log(nginx_error)
                document.location.href = '/vaults'
                return
            }
        }

        check_user_access()
    }, [])

    async function send_request(e) {
        e.preventDefault()

        const url = `/web/vaults/${vault_id}/passwords/add`
        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "content-type": "application/json"
                },
                body: JSON.stringify({
                        "pas_data": {
                            "service": service,
                            "username": login,
                            "password": password,
                            "note": note
                        },
                        "gen": generatePassword
                })
            }
        )
        const contentType = response.headers.get("content-type")
        if (response.ok) {
            document.location.href = `/vaults/${vault_id}`
            return
        } else if (contentType && contentType.includes('application/json')){
            const response_data = await response.json()
            const response_error = response_data['detail'] || "No detail from server"
            await showError(response_error)
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

    if (isLoading) {
        return (
            <section className="create-password-section">
                <div className="container">
                    <h1>Loading...</h1>
                </div>
            </section>
        )
    }




    return (
        <section className="create-password-section">
            <div className="container">
                <NavLink to={`/vaults/${vault_id}`} className="vault-back-link">
                    ← Back to vault
                </NavLink>

                <div className="create-password-card">
                    <h1>New Record</h1>
                    <p>Add a new password entry to your vault.</p>

                    {error &&
                        <div className="form-error">
                        {error}
                        </div>
                    }

                    <form className="auth-form" onSubmit={send_request}>
                        <div className="form-group">
                            <label htmlFor="service">Service</label>
                            <input
                                type="text"
                                id="service"
                                name="service"
                                placeholder="e.g. Google"
                                required
                                value={service}
                                onChange={event => SetService(event.target.value)}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="login">Login</label>
                            <input
                                type="text"
                                id="login"
                                name="login"
                                placeholder="e.g. user@example.com"
                                required
                                value={login}
                                onChange={event => SetLogin(event.target.value)}
                            />
                        </div>

                        <div className="form-group password-group">
                            <div className="password-left">
                                <label htmlFor="password">Password</label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    placeholder="Enter password"
                                    value={password}
                                    onChange={event => SetPasword(event.target.value)}
                                    disabled={generatePassword}
                                />
                            </div>
                            <div className="password-right">
                                <label className="generate-password-label">
                                    Generate
                                </label>
                                <input
                                    type="checkbox"
                                    name="generate_password"
                                    className="generate-password-checkbox"
                                    onChange={(e) => {
                                        SetGeneratePassword(e.target.checked)
                                        SetPasword('')
                                    }}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="note">Note (optional)</label>
                            <textarea
                                id="note"
                                name="note"
                                rows={3}
                                placeholder="Additional information"
                                value={note}
                                onChange={event => SetNote(event.target.value)}
                            />
                        </div>

                        <button type="submit" className="auth-submit">
                            Create Record
                        </button>
                    </form>
                </div>
            </div>
        </section>
    )
}

export default CreatePasswordPage
