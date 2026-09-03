import { useState, useEffect } from "react"
import { NavLink, useParams } from "react-router-dom"
import { useNotification } from '../../hooks/useNotification.js'

function PasswordPage() {
    const params = useParams()
    const vault_id = Number(params.vault_id)
    const service = String(params.service)
    const [entrie, SetEntrie] = useState({})    
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [note, setNote] = useState('')
    const [isLoading, setLoading] = useState(true)
    const [showPassword, setShowPassword] = useState(false)
    const [canEditEntrie, setCanEditEntrie] = useState(false)
    const [
        error,
        message,
        showError,
        showMessage
    ] = useNotification()

    async function get_password_data() {
        const url = `/web/vaults/${vault_id}/passwords/get`
        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "service": service,
                    "strict": true,
                    "get_all": false
                })
            }
        )

        const contentType = response.headers.get("content-type")
        
        if (response.ok) {
            const response_data = await response.json()
            const entrie = response_data['passwords'][0]
            SetEntrie(entrie)
            setUsername(entrie['username'])
            setPassword(entrie['password'])
            setNote(entrie['note'])
        } else if (contentType && contentType.includes('application/json')){
            const response_data = await response.json()
            const response_error = response_data['detail'] || "No detail from server"
            showError(response_error)
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
                // SetLoading(false)
                return true
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
                document.location.href = `/vaults/${vault_id}`
                return
            }
        }
    
        const access = check_user_access()
        
        if (access) {
            get_password_data()
        } else {
            return
        }
    }, [])

    async function update_password(e) {
        e.preventDefault()

        if (!canEditEntrie) {
            return
        }
        
        const validated_data = validate_update_data()
        if (validated_data['error']) {
            showError(validated_data['error'])
            return
        }
        
        const url = `/web/vaults/${vault_id}/passwords/update`
        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    'content-type': "application/json"
                },
                body: {
                    "service": service,
                    "username": validated_data['username'],
                    "password": validated_data['password'],
                    "note": validated_data['note']
                }
            }
        )
    }

    function validate_update_data() {
        const clearUsername = username.trim()
        const clearPassword = password.trim()
        const clearNote = note.trim()
        const error = ''
        if ( ! (0 < clearUsername.length < 32)) {
            error = "Wrong length of username"
        } else if ( ! (0 < clearPassword.length < 32)) {
            error = "Wrong length of password"
        } else if ( ! (0 <= clearNote.length < 256)) {
            error = "Note is too long"
        }

        return {
            "username": clearUsername,
            "password": clearPassword,
            "note": clearNote,
            "error": error
        }

        
    }


return (
    <main>
        <section className="password-page-section">
            <div className="container">

                {message && (
                    <div className="success-message">
                        {message}
                    </div>
                )}

                {error && (
                    <div className="form-error">
                        {error}
                    </div>
                )}

                <div className="password-page-topbar">
                    <NavLink
                        to={`/vaults/${vault_id}`}
                        className="password-page-back-link"
                    >
                        ← Back to vault
                    </NavLink>
                </div>

                <div className="password-page-card">
                    <div className="password-page-heading">
                        <h1>{service}</h1>
                        <button type="button" onClick={() => 
                            setShowPassword(! showPassword)}>
                            {showPassword ? "Hide password" : "Show password"}
                        </button>
                        <button type="button" onClick={() => 
                            setCanEditEntrie(! canEditEntrie)}>
                            {canEditEntrie ? "Cancel Editing" : "Edit Entrie"}
                        </button>
                    </div>

                    <form
                        className="password-page-form"
                        onSubmit={update_password}
                    >
                        {/* <div className="form-group">
                            <label htmlFor="service">
                                Service
                            </label>

                            <input
                                type="text"
                                id="service"
                                name="service"
                                value={service || ""}
                                readOnly
                            />
                        </div> */}

                        <div className="form-group">
                            <label htmlFor="username">
                                Username
                            </label>

                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={username}
                                onChange={(event) =>
                                    setUsername(event.target.value)
                                }
                                placeholder="Username or email"
                                readOnly={canEditEntrie ? false : true}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">
                                Password
                            </label>

                            <input
                                type={showPassword ? "text" : 'password'}
                                id="password"
                                name="password"
                                value={password}
                                onChange={(event) =>
                                    setPassword(event.target.value)
                                }
                                placeholder="Password"
                                readOnly={canEditEntrie ? false : true}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="note">
                                Note
                            </label>

                            <textarea
                                id="note"
                                name="note"
                                value={note}
                                onChange={(event) =>
                                    setNote(event.target.value)
                                }
                                placeholder="Optional secure note"
                                readOnly={canEditEntrie ? false : true}
                                rows={5}
                            />
                        </div>

                        <div className="password-page-actions">
                            <button
                                type="submit"
                                className="password-page-save-button"
                            >
                                Save changes
                            </button>
                        </div>
                    </form>
                </div>

            </div>
        </section>
    </main>
)





}

export default PasswordPage