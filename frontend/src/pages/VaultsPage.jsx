import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import './DasboardPage.css'

function VaultsPage() {
    const SORT_BY = Object.freeze({
        NAME: "name",
        ENTRIES: "entries",
        CREATED_AT: "created_at"
    })
    const [sorting, SetSort] = useState(SORT_BY.CREATED_AT)
    const [vaults, SetVaults] = useState([])
    const [error, SetError] = useState('')
    const [message, SetMessage] = useState('')
    const [username, SetUsername] = useState('')
    
    let user_data = {}
    let pinned = []
    let no_pinned = []

    useEffect(() => {
        async function get_user_data() {
            const url = "/web/me"
            const response = await fetch(
                url,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
            if (response.ok) {
                const response_data = await response.json()
                if (response_data["ok"]) {
                    user_data = response_data["data"]
                    SetUsername(response_data["data"]["username"])
                } else {
                    return
                }
            } else {
                return
            }
    
        }
        get_user_data()
    }, [])

    useEffect(() => {
        async function get_vaults(sort_by = SORT_BY.CREATED_AT) {
            const url = `/web/vaults?sort_by=${sort_by}`
            const response = await fetch(
                url,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    },
                }
            )
            const contentType = response.headers.get('content-type')
            
            if (response.ok) {
                const response_data = await response.json()
                const vaults = response_data['vaults']
                return vaults
            
                 
            } else if (contentType && contentType.includes('application/json')) {
                const response_data = await response.json()
                const response_error = response_data['detail'] || "No detail from server"
                SetError(response_error)
                if (response.status === 401) {
                    document.location.href = '/login'
                }

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
        async function loadVaults(sort_by = SORT_BY.CREATED_AT) {
            const vaults = await get_vaults(sort_by)
            console.log(vaults)
            SetVaults(vaults)
        }
        loadVaults(sorting)
    }, [sorting])



    if (vaults) {
        pinned = vaults.filter(v => v.pinned)
        no_pinned = vaults.filter(v => !v.pinned)
    }

    return (
        <section className="dashboard-section">
            <div className="container">
                <div className="dashboard-header">
                    <div>
                        {username && 
                            <h1>Hello, {username}</h1>
                        }
                        {!username && 
                            <h1>Hello, User</h1>
                        }
                        <p>Session active — API connected</p>
                    </div>
                </div>

                { error &&
                    <div className="form-error">{error}</div>
                }


                { pinned.length > 0 && 
                <div className="dashboard-block">
                    <div>
                        <h2>Pinned Backups</h2>
                        <table className="dashboard-table">
                            <thead>
                                <tr>
                                    <th>name</th>
                                    <th>date</th>
                                    <th>entries</th>
                                </tr>
                            </thead>
                            <tbody>
                                { pinned.map(vault => (
                                    <tr key={vault.id}>
                                    <td>
                                        <NavLink to={`/vaults/${backup.id}`} className="backup-name">
                                            { vault.name }
                                        </NavLink>
                                    </td>
                                    <td>{ vault.created_at_formatted }</td>
                                    <td>{ vault.entries }</td>
                                </tr>
                                )) }
                            </tbody>
                        </table>
                    </div>
                </div>
                    }

                { no_pinned.length > 0 &&
                <div className="dashboard-block">
                    <div className="sort-links">
                        <span className="sort-label">Sort by:</span>

                        <button
                            type="button"
                            className={`sort-link ${sorting === SORT_BY.CREATED_AT ? 'sort-link-active' : ''}`}
                            onClick={() => {SetSort(SORT_BY.CREATED_AT)}}
                        >
                            Date
                        </button>

                        <button
                            type="button"
                            className={`sort-link ${sorting === SORT_BY.NAME ? 'sort-link-active' : ''}`}
                            onClick={() => {SetSort(SORT_BY.NAME)}}
                        >
                            Name
                        </button>

                        <button
                            type="button"
                            className={`sort-link ${sorting === SORT_BY.ENTRIES ? 'sort-link-active' : ''}`}
                            onClick={() => {SetSort(SORT_BY.ENTRIES)}}
                        >
                            Entries
                        </button>
                    </div>

                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th>name</th>
                                <th>date</th>
                                <th>entries</th>
                            </tr>
                        </thead>
                        <tbody>
                            { no_pinned.map(vault =>

                                <tr key={vault.id}>
                                    <td>
                                        <NavLink to={`/vaults/${vault.id}`} className="backup-name">
                                            { vault.name }
                                        </NavLink>
                                    </td>
                                    <td>{ vault.created_at_formatted }</td>
                                    <td>{ vault.entries }</td>
                                </tr>
                                ) 
                            }
                        </tbody>
                    </table>
                    </div>  }
                </div>
        </section>
    )
}


export default VaultsPage