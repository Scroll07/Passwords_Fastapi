import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { useNotification } from '../hooks/useNotification.js'
import './DashboardPage.css'


function DashboardPage() {
    const SORT_BY = Object.freeze({
        NAME: "name",
        ROWS: "rows",
        CREATED_AT: "created_at"
    })
    const [backups, SetBackups] = useState([])
    const [sorting, SetSort] = useState(SORT_BY.CREATED_AT)
    const [error, SetError] = useState('')
    const [username, SetUsername] = useState('')
    
    const [
        error,
        message,
        showError,
        showMessage
    ] = useNotification()

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


    async function logout(e) {
        e.preventDefault()
        
        const url = '/web/logout'
        const response = await fetch (
            url,
            {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )
        const contentType = response.headers.get('content-type') 
        
        if (response.ok) {
            document.location.href = '/login'
            return

        } else if (contentType && contentType.includes('application/json')){
            const response_data = await response.json()
            const response_error = response_data['detail'] || "No detail from server"
            await show_error(response_error)
            return
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, 'text/html') 
            const nginx_error = nginx_document.title.slice(4)
            await show_error(nginx_error)
            return
        }

    }
    
    useEffect(() => {
        async function get_backups(sort_by = SORT_BY.CREATED_AT) {
            const url = `/web/backups?sort_by=${sort_by}`
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
                const backups = response_data['backups']
                return backups
            
                 
            } else if (contentType && contentType.includes('application/json')) {
                const response_data = await response.json()
                const response_error = response_data['detail'] || "No detail from server"
                await show_error(response_error)
                if (response.status === 401) {
                    document.location.href = '/login'
                }

                return

            } else {
                const text = await response.text()
                const parser = new DOMParser()
                const nginx_document = parser.parseFromString(text, 'text/html') 
                const nginx_error = nginx_document.title.slice(4)
                await show_error(nginx_error)
                return
            }
        }
        async function loadBackups(sort_by = SORT_BY.CREATED_AT) {
            const backups = await get_backups(sort_by)
            console.log(backups)
            SetBackups(backups)
        }
        loadBackups(sorting)
    }, [sorting])


    if (backups) {
        pinned = backups.filter(b => b.pinned)
        no_pinned = backups.filter(b => !b.pinned)
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

                    <form onSubmit={logout} method="post">
                        <button id="dashboard-logout" className="dashboard-logout" type="submit">Log out</button>
                    </form>
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
                                    <th>rows</th>
                                </tr>
                            </thead>
                            <tbody>
                                { pinned.map(backup => (
                                    <tr key={backup.id}>
                                    <td>
                                        <NavLink to={`/backups/${backup.id}`} className="backup-name">
                                            { backup.name }
                                        </NavLink>
                                    </td>
                                    <td>{ backup.created_at_formatted }</td>
                                    <td>{ backup.rows }</td>
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
                            className={`sort-link ${sorting === SORT_BY.ROWS ? 'sort-link-active' : ''}`}
                            onClick={() => {SetSort(SORT_BY.ROWS)}}
                        >
                            Rows
                        </button>
                    </div>

                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th>name</th>
                                <th>date</th>
                                <th>rows</th>
                            </tr>
                        </thead>
                        <tbody>
                            { no_pinned.map(backup =>

                                <tr key={backup.id}>
                                    <td>
                                        <NavLink to={`/backups/${backup.id}`} className="backup-name">
                                            { backup.name }
                                        </NavLink>
                                    </td>
                                    <td>{ backup.created_at_formatted }</td>
                                    <td>{ backup.rows }</td>
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


export default DashboardPage