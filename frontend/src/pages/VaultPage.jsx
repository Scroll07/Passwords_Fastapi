import { useState, useEffect } from 'react'
import { useParams, NavLink } from 'react-router-dom'
import './VaultPage.css'


function VaultPage() {
    const params = useParams()
    const vault_id = Number(params.vault_id)
    const [master_password, SetMasterPassword] = useState('')
    const [entries, SetEntries] = useState([])
    const [message, SetMessage] = useState('')
    const [error, SetError] = useState('')
    const [access, SetAccess] = useState(false)
    const [vault, SetVault] = useState({})    
    

    // ================================================================================================
    // Проверка vault status
    // Попытка ввести master_password чтобы разблокировать vault
    // Если разблокирован то отобразить таблицу с паролями (id, service, name, ****, note)
    // (можно сделать обрезанный note например первые 16 символов и троеточие)
    // Строка для поиска записей (в будущем)
    // каждая запись в таблице это ссылка на "entrie" (отдельную страницу с данными и действиями)
    // ================================================================================================

    useEffect(() => {
        async function get_vault_status() {
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
                const response_data = await response.json()
                access = response_data['access']
                SetAccess(access)
                SetMessage(response_data['detail'])
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

        get_vault_status()
    }, [access])

    // useEffect(() => {
    //     async function get_vault_data() {
    //         const url = `/web/vaults/${vault_id}/info`
    //         const response = await fetch(
    //             url,
    //             {
    //                 method: "GET",
    //                 headers: {
    //                     "Content-Type": "application/json"
    //                 }
    //             }
    //         )

    //         const contentType = response.headers.get("content-type")
            
    //         if (response.ok) {
    //             const response_data = await response.json()
    //             const vault = response_data['vault']
    //             SetVault(vault)
    //         } else if (contentType && contentType.includes('application/json')){
    //             const response_data = await response.json()
    //             const response_error = response_data['detail'] || "No detail from server"
    //             SetError(response_error)
    //             return
    //         } else {
    //             const text = await response.text()
    //             const parser = new DOMParser()
    //             const nginx_document = parser.parseFromString(text, 'text/html') 
    //             const nginx_error = nginx_document.title.slice(4)
    //             SetError(nginx_error)
    //             return
    //         }
    
    //     }

    //     async function get_vault_entries() {
    //         const url = `/web/vaults/${vault_id}/passwords/get`
    //         const response = await fetch(
    //             url,
    //             {
    //                 method: "POST",
    //                 headers: {
    //                     "Content-Type": "application/json"
    //                 },
    //                 body: JSON.stringify({
    //                     "get_all": true,
    //                     'service': ""
    //                 })
    //             }
    //         )

    //         const contentType = response.headers.get("content-type")

    //         if (response.ok) {
    //             const response_data = await response.json()
    //             const entries = response_data['passwords']
    //             SetEntries(entries)
    //         } else if (contentType && contentType.includes('application/json')){
    //             const response_data = await response.json()
    //             const response_error = response_data['detail'] || "No detail from server"
    //             SetError(response_error)
    //             return
    //         } else {
    //             const text = await response.text()
    //             const parser = new DOMParser()
    //             const nginx_document = parser.parseFromString(text, 'text/html') 
    //             const nginx_error = nginx_document.title.slice(4)
    //             SetError(nginx_error)
    //             return
    //         }
            
    //     }



    //     get_vault_data()
    //     get_vault_entries()
    // }, [])


    async function verify_password_request(e) {
        e.preventDefault()

        const url = `/web/vaults/${vault_id}/unlock`
        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: master_password.trim()
                // body: JSON.stringify({
                //     "vault_master_password": master_password.trim()
                // })
            }
        )
        
        const contentType = response.headers.get("content-type")

        if (response.ok) {
            const response_data = await response.json()
            const server_message = response_data['detail']
            SetAccess(true) 
            SetMessage(server_message)
        } else if (contentType && contentType.includes("application/json")) {
            const response_data = await response.json()
            const server_message = response_data['detail']
            SetAccess(false)
            SetError(server_message)
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, 'text/html') 
            const nginx_error = nginx_document.title.slice(4)
            SetError(nginx_error)
            return  
        }
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
    
            
            {!access && 
                <form className="vault-form" id="master_password-form" method="post" onSubmit={verify_password_request}>
                    <div className="form-group">
                        <label htmlFor="master_password">Master Password</label>
                        <input
                            type="password"
                            id="master_password"
                            name="master_password"
                            placeholder="Master password"
                            required
                            value={master_password}
                            onChange={event => SetMasterPassword(event.target.value)}
                            />
                    </div>
    
                    <button type="submit" className="vault-submit">Unlock vault</button>
                </form>
            }

            {access && 
                <section className="vault-section">
                <div className="container">
                    <div className="vaults-page-actions">
                        <NavLink to="/vaults" className="vault-back-link">
                            ← Back to vaults
                        </NavLink>

                        <NavLink to="/vaults/create" className="create-vault-link">
                            Create new vault
                        </NavLink>
                    </div>

                    <div className="vault-header">
                    {vault.length > 0 &&
                    <div>
                        <p className="vault-label">Vault</p>

                        <h1>{vault.name}</h1>

                        <div className="vault-meta">
                        <span>
                            Entries: <strong>{vault.entries}</strong>
                        </span>

                        <span>
                            Created: <strong>{vault.created_at_formatted}</strong>
                        </span>
                        </div>
                    </div>
                    }

                    <NavLink
                        to={`/vaults/${vault.id}/settings`}
                        className="vault-settings-button"
                    >
                        Vault settings
                    </NavLink>

                    </div>
                    <div className="vault-block">
                    <div className="vault-block-header">
                        <div>
                        <h2>Entries</h2>
                        <p>Saved credentials and secure notes.</p>
                        </div>

                        <NavLink
                        to={`/vaults/${vault.id}/entries/new`}
                        className="vault-add-entry-button"
                        >
                        Add entry
                        </NavLink>
                    </div>

                    <div className="vault-toolbar">
                        {/* <input
                        type="search"
                        className="vault-search"
                        placeholder="Search entries..."
                        value={searchValue}
                        onChange={(event) => setSearchValue(event.target.value)}
                        /> */}

                        {/* <div className="sort-links">
                        <span className="sort-label">Sort by:</span>

                        <button
                            type="button"
                            className={`sort-link ${
                            sorting === SORT_BY.CREATED_AT ? "sort-link-active" : ""
                            }`}
                            onClick={() => setSort(SORT_BY.CREATED_AT)}
                        >
                            Date
                        </button>

                        <button
                            type="button"
                            className={`sort-link ${
                            sorting === SORT_BY.SERVICE ? "sort-link-active" : ""
                            }`}
                            onClick={() => setSort(SORT_BY.SERVICE)}
                        >
                            Service
                        </button>

                        <button
                            type="button"
                            className={`sort-link ${
                            sorting === SORT_BY.NAME ? "sort-link-active" : ""
                            }`}
                            onClick={() => setSort(SORT_BY.NAME)}
                        >
                            Name
                        </button>
                        </div> */}
                    </div>

                    {entries.length === 0 ? (
                        <div className="vault-empty-state">
                        <h3>There are no entries yet</h3>
                        <p>Create your first password entry in this vault.</p>

                        <NavLink
                            to={`/vaults/${vault.id}/passwords/new`}
                            className="vault-add-entry-button"
                        >
                            Add first entry
                        </NavLink>
                        </div>
                    ) : ( // НЕПОНЯТНЫЙ МОМЕНТ
                        <div className="vault-table-wrapper">
                        <table className="vault-table">
                            <thead>
                            <tr>
                                <th>Service</th>
                                <th>Name</th>
                                <th>Username</th>
                                <th>Password</th>
                                <th>Note</th>
                                <th>Created</th>
                                {
                                    // можно добавить кнопку show и при нажатии будет показывать\скрывать пароль
                                }
                            </tr>
                            </thead>

                            <tbody>
                            {entries.map((entry) => (
                                <tr key={entry.id}>
                                <td>
                                    <NavLink
                                    to={`/vaults/${vault.id}/passwords/${entry.id}`}
                                    className="entry-name"
                                    >
                                    {entry.service}
                                    </NavLink>
                                </td>

                                <td>{entry.name}</td>

                                <td>{entry.username}</td>

                                <td className="entry-password-mask">
                                    ••••••••
                                </td>

                                <td className="entry-note">
                                    {entry.note
                                    ? `${entry.note.slice(0, 16)}...` // НЕПОНЯТНЫЙ МОМЕНТ
                                    : "—"}
                                </td>

                                <td>{entry.created_at_formatted}</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                        </div>
                    )}
                    </div>
                </div>
                </section>
    
            
            
            
            
            
            }




        </main>












    )




}


export default VaultPage