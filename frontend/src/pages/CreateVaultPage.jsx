import { useState, useEffect } from "react"
import { NavLink } from "react-router-dom"
import './CreateVaultPage.css'

function CreateVaultPage() {
    const [vaultName, setVaultName] = useState('') 
    const [vaultPassword, setVaultPassword] = useState('') 
    const [error, SetError] = useState('')


    function validate_data() {
        let validate_error = null
        const clearName = vaultName.trim()
        const clearPassword = vaultPassword.trim()

        if (! (0 < clearName.length < 33)) {
            validate_error = 'Wrong length of vault name'    
        } else if (! (0 < clearPassword.length < 33)) {
            validate_error = 'Wrong length of vault password'    
        } else if (clearPassword.includes(' ')) {
            validate_error = 'Master Password must not contain any spaces'
        }

        return {
            "name": clearName,
            "master_password": clearPassword,
            "error": validate_error
        }
    }
    
    async function createRequest(e) {
        e.preventDefault()
        
        const validated_data = validate_data()
        if (validated_data['error']) {
            await show_error(validated_data['error'])
            return
        }

        const url = '/web/vaults/create'
        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "content-type": "application/json"
                },
                body: JSON.stringify({
                    "vault_name": validated_data['name'],
                    "vault_master_password": validated_data['master_password'] 
                })
            }
        )
        const contentType = response.headers.get("content-type")

        if (response.ok) {
            document.location.href = '/vaults'
        } else if (contentType && contentType.includes("application/json")) {
            const response_data = await response.json()
            const server_message = response_data['detail']
            SetAccess(false)
            await show_error(server_message)
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, 'text/html') 
            const nginx_error = nginx_document.title.slice(4)
            await show_error(nginx_error)
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
        <section className="create-vault-section">
        <div className="container">
            <NavLink to="/vaults" className="vault-back-link">
                ← Back to vaults
            </NavLink>

            <div className="create-vault-card">
                <h1>Create vault</h1>
                <p>Create a secure vault for your passwords and private entries.</p>

            {error && 
                <div className="form-error">
                {error}
                </div>
            }

                <form className="auth-form" onSubmit={createRequest}>
                <div className="form-group">
                    <label htmlFor="vault_name">Vault name</label>
                    <input
                    type="text"
                    id="vault_name"
                    name="vault_name"
                    placeholder="For example: Personal"
                    value={vaultName}
                    onChange={(event) => setVaultName(event.target.value)}
                    required
                    minLength={1}
                    maxLength={32}
                    />

                    <label htmlFor="master_password">Master password</label>
                    <input
                    type="password"
                    id="master_password"
                    name="master_password"
                    placeholder="Password"
                    value={vaultPassword}
                    onChange={(event) => setVaultPassword(event.target.value)}
                    required
                    minLength={1}
                    maxLength={32}
                    />
                </div>


                <button type="submit" className="auth-submit">
                    Create vault
                </button>
                </form>
            </div>
        </div>
  </section>
    )

}

export default CreateVaultPage