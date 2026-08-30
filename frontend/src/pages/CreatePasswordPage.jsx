import { useState, useEffect } from "react"
import { NavLink, useParams } from "react-router-dom"
import './CreatePasswordPage.css'


function CreatePasswordPage() {
    const params = useParams()
    const vault_id = Number(params.vault_id)
    const [message, SetMessage] = useState('')
    const [error, SetError] = useState('')
    const [isLoading, SetLoading] = useState(true)
    const [service, SetService] = useState('')
    const [login, SetLogin] = useState('')
    const [password, SetPasword] = useState('')
    const [note, SetNote] = useState('')
    const [generatePassword, SetGeneratePassword] = useState(false)

    
    // Проверка есть ли доступ у пользователя к vault
    // сделать что-то типа загрузки
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
                // SetError(response_error)
                document.location.href = '/vaults'
                return
            } else {
                const text = await response.text()
                const parser = new DOMParser()
                const nginx_document = parser.parseFromString(text, 'text/html') 
                const nginx_error = nginx_document.title.slice(4)
                console.log(nginx_error)
                // SetError(nginx_error)
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
                    "password_data": {
                        "pas_data": {
                            "service": service,
                            "username": login,
                            "password": password,
                            "note": note
                        },
                        "gen": generatePassword
                    },
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
            SetError(response_error)
            return
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, 'text/html') 
            const nginx_error = nginx_document.title.slice(4)
            SetError(nginx_error)
            return
        }
    }
    
    if (isLoading) {
        return <div>
            <h1>Loading...</h1>
        </div>
    }
    
    return (
        <main>

<div className="form-messages">
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
</div>

<form type="submit" onSubmit={send_request}>
<div className="create-record-form">
  <h2>New Record</h2>

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

    <div className="form-group">
    <label htmlFor="password">Password</label>
    <div className="password-input-wrapper">
      <input
        type="password"
        id="password"
        name="password"
        placeholder="Enter password"
        value={password}
        onChange={event => SetPasword(event.target.value)}
        disabled={generatePassword}
        />
      <label className="generate-password-label">
        <input
          type="checkbox"
          name="generate_password"
          className="generate-password-checkbox"
          onChange={(e) => {
              SetGeneratePassword(e.target.checked)
              SetPasword('')
            }}
            />
        Generate
      </label>
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

  <button type="submit" className="submit-button">
    Create Record
  </button>
</div>
</form>
</main>
    )

}

export default CreatePasswordPage