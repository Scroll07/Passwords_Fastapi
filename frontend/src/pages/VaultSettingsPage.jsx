import { useState, useEffect } from 'react'
import { NavLink, useParams } from 'react-router-dom'
import { useNotification } from '../hooks/useNotification.js'
import './VaultSettingsPage.css'

function VaultSettingsPage() {
    const params = useParams()
    const vault_id = Number(params.vault_id)
    const [isLoading, SetLoading] = useState(true)
    const [vault, SetVault] = useState({})    
    const [pinned, SetPinned] = useState()
    const [new_name, SetNewName] = useState('')
    const [
        error,
        message,
        showError,
        showMessage
    ] = useNotification()


    async function get_vault_data() {
        const url = `/web/vaults/${vault_id}/info`
        const response = await fetch(
            url,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )

        const contentType = response.headers.get("content-type")
        
        if (response.ok) {
            const response_data = await response.json()
            const vault = response_data['vault']
            SetVault(vault)
            SetPinned(vault['pinned'])
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
                document.location.href = '/vaults'
                return
            }
        }
    
        const access = check_user_access()
        if (access) {
            get_vault_data()
            SetLoading(false)
        } else {
            return
        }
    }, [])

    async function change_pin(e) {
        e.preventDefault()

        const url = `/web/vaults/${vault_id}/change-pin`
        const response = await fetch(
                url,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
        const contentType = response.headers.get("content-type")

        if (response.ok) {
            const response_data = await response.json()
            await get_vault_data()
            showMessage(response_data['detail'])
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
        
    async function rename_backup(e) {
        e.preventDefault()

        const url = `/web/vaults/${vault_id}/rename`
        const response = await fetch(
                url,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(new_name.trim())
                }
            )
        const contentType = response.headers.get("content-type")

        if (response.ok) {
            const response_data = await response.json()
            await get_vault_data()
            showMessage( response_data['detail'])
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


    async function delete_backup(e) {
        e.preventDefault()

        const confirmed = window.confirm("Delete this vault permanently? All entries will be removed and cannot be restored.")
        if (!confirmed) {
            return
        }

        const url = `/web/vaults/${vault_id}`
        const response = await fetch(
                url,
                {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
        const contentType = response.headers.get("content-type")

        if (response.ok) {
            document.location.href = '/vaults'                        
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


    return (
        <main className="vault-settings-section">
            <div className="container">

                {message && <div className="success-message">{message}</div>}
                {error && <div className="form-error">{error}</div>}

                <div className="vault-settings-topbar">
                    <NavLink to={`/vaults/${vault_id}`} className="vault-settings-back-link">
                        ← Back to vault
                    </NavLink>
                    <span className={`vault-settings-badge ${pinned ? 'vault-settings-badge--pinned' : 'vault-settings-badge--unpinned'}`}>
                        {pinned ? 'Pinned' : 'Not pinned'}
                    </span>
                </div>

                <div className="vault-settings-heading">
                    <h1>{vault.name || 'Vault'} settings</h1>
                    <p>Manage settings and actions for this vault.</p>
                </div>

                <div className="vault-settings-card">
                    <h2>General</h2>
                    <p className="vault-settings-card-desc">
                        {pinned
                            ? 'This vault is pinned for quick access.'
                            : 'Pin this vault for quick access.'}
                    </p>
                    <form onSubmit={change_pin}>
                    <button className="vault-settings-btn vault-settings-btn--secondary">
                        {pinned ? 'Unpin vault' : 'Pin vault'}
                    </button>
                    </form>
                </div>

                <div className="vault-settings-card">
                    <h2>Rename vault</h2>
                    <form className="vault-settings-form" onSubmit={rename_backup}>
                        <div className="form-group">
                            <input
                                type="text"
                                value={new_name}
                                onChange={(event) => SetNewName(event.target.value)}
                                placeholder="New vault name"
                            />
                        </div>
                        <button type="submit" className="vault-settings-btn vault-settings-btn--accent">
                            Save name
                        </button>
                    </form>
                </div>

                <div className="vault-settings-card vault-settings-card--danger">
                    <h2>Danger zone</h2>
                    <p className="vault-settings-card-desc">
                        Deleting a vault permanently removes its entries and cannot be undone.
                    </p>
                    <form onSubmit={delete_backup}>
                        <button type="submit" className="vault-settings-btn vault-settings-btn--danger">
                            Delete vault
                        </button>
                    </form>
                </div>

            </div>
        </main>
    )



}

export default VaultSettingsPage