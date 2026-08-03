import { useState, useEffect } from "react"
import { NavLink, useParams } from 'react-router-dom'
import './BackupPage.css'



function BackupPage() {
    const params = useParams()
    const backup_id = Number(params.backup_id)
    const [new_name, setNewName] = useState('')
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')
    const [backup, setBackup] = useState(null)

    async function get_backup() {
        setError("")
        if (Number.isNaN(backup_id) || !Number.isInteger(backup_id)) {
            setError('Wrong id of backup')
            return
        }

        const url = `/web/backups/${backup_id}`
        const response = await fetch(
            url,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )
        const contentType = response.headers.get('content-type')
        if (response.ok) {
            const response_data = await response.json()
            if (response_data['backup']) {
                return response_data['backup']
            } else {
                setError('No backup data')
            }
        } else  if (contentType.includes("application/json")) {
            const response_data = await response.json()
            const server_error = response_data['detail']
            setError(server_error)
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, "text/html")
            const nginx_error = nginx_document.title.slice(4)
            setError(nginx_error) 
        }
    }

    async function load_backup() {
        const backup = await get_backup()
        if (backup) {
            setBackup(backup)
        }
    }

    useEffect(() => {
        load_backup()
    }, [])

    async function change_pin(e) {
        e.preventDefault()
        
        setError("")
        setMessage("")

        const url = `/web/backups/${backup_id}/change-pin`
        const response = await fetch(
            url,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )

        const contentType = response.headers.get('content-type')
        if (response.ok) {
            const response_data = await response.json()
            setMessage(response_data['detail'])
            load_backup()
        } else  if (contentType.includes("application/json")) {
            const response_data = await response.json()
            const server_error = response_data['detail']
            setError(server_error)
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, "text/html")
            const nginx_error = nginx_document.title.slice(4)
            setError(nginx_error) 
        }
    }

    function validate_name() {
        const clear_new_name = new_name.trim()
        let error = '' 
        if (! clear_new_name) {
            error = "New name can not be empty"
        } else if (clear_new_name.length > 20) {
            error = 'New name is too long'
        }
        return {
            "new_name": clear_new_name,
            "error": error 
        }
    }

    async function change_name(e) {
        e.preventDefault()

        setError("")
        setMessage("")

        const validate_data = validate_name()
        if (validate_data['error']) {
            setError(validate_data['error'])
            return
        }

        const url = `/web/backups/${backup_id}`
        const response = await fetch(
            url,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(validate_data['new_name'])
            }
        )

        const contentType = response.headers.get('content-type')
        if (response.ok) {
            const response_data = await response.json()
            setMessage(response_data['detail'])
            load_backup()
        } else  if (contentType.includes("application/json")) {
            const response_data = await response.json()
            const server_error = response_data['detail']
            setError(server_error)
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, "text/html")
            const nginx_error = nginx_document.title.slice(4)
            setError(nginx_error) 
        }
    }

    // async function download_backup(e) {
    //     e.preventDefault()

    //     setError("")
    //     setMessage("")

    //     const url = `/web/backups/${backup_id}`
    //     const response = await fetch(
    //         url,
    //         {
    //             method: "POST",
    //             headers: {
    //                 "Content-Type": "application/json"
    //             },
    //             body: JSON.stringify({
    //                 "backup_id": backup_id
    //             })
    //         }
    //     )

    //     const contentType = response.headers.get('content-type')
    //     if (response.ok) {
    //         const response_data = await response.blob()
    //         setMessage("Your backup was successfully downloaded")
    //         document.location.href = '/dashboard'
    //     } else  if (contentType.includes("application/json")) {
    //         const response_data = await response.json()
    //         const server_error = response_data['detail']
    //         setError(server_error)
    //     } else {
    //         const text = await response.text()
    //         const parser = new DOMParser()
    //         const nginx_document = parser.parseFromString(text, "text/html")
    //         const nginx_error = nginx_document.title.slice(4)
    //         setError(nginx_error) 
    //     }
    // }

    async function delete_backup(e) {
        e.preventDefault()

        setError("")
        setMessage("")

        const confirmed = window.confirm('Delete this backup? This action cannot be undone.')
        if (! confirmed) {return}

        const url = `/web/backups/${backup_id}`
        const response = await fetch(
            url,
            {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json"
                },
            }
        )

        const contentType = response.headers.get('content-type')
        if (response.ok) {
            const response_data = await response.json()
            setMessage(response_data['detail'])
            document.location.href = '/dashboard'
        } else  if (contentType.includes("application/json")) {
            const response_data = await response.json()
            const server_error = response_data['detail']
            setError(server_error)
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, "text/html")
            const nginx_error = nginx_document.title.slice(4)
            setError(nginx_error) 
        }
    }


    return (
<section className="dashboard-section user-backup-page">
    
    
    <div className="container">
        { message &&
        <div className="success-message">
            {message}
        </div>}
    
        { error &&
        <div className="form-error">
            {error}
        </div>}
        
        {backup && 
        <div>

        <div className="dashboard-header">
            <div>
                <NavLink to="/dashboard" className="backup-back-link">← Back to dashboard</NavLink>
                <h1>{backup["name"]}</h1>
                <p>
                    Backup ID: {backup['id']}
                     · Created: { backup['created_at_formatted'] }
                     · Rows: {backup['rows']}
                </p>
            </div>
        </div>
        
        <div className="dashboard-block">
            { backup['pinned'] && 
                <div>
                    <h2>Unpin backup</h2>
                    <p>Remove this backup from pinned items so it no longer stays highlighted in your list.</p>
                </div>
            } 
            { ! backup['pinned'] && 
                <div>
                    <h2>Pin backup</h2>
                    <p>Pin this backup to keep it highlighted and easier to find in your backups list.</p>
                </div>
            }

            
            <form onSubmit={change_pin} method="post">
                <button type="submit" className="dashboard-button primary-button">
                    { backup['pinned'] && 'Unpin' }
                    { ! backup['pinned'] && 'Pin' }
                </button>
            </form>
        </div>

        <div className="dashboard-block">
            <h2>Download backup</h2>
            <p>Download this backup from the server to your local machine.</p>

            <form action={`/web/backups/${backup_id}/download`} method="post">
                <button type="submit" className="dashboard-button primary-button">
                    Download
                </button>
            </form>
        </div>

        <div className="dashboard-block">
            <h2>Rename backup</h2>
            <p>Change the display name of this backup.</p>

            <form onSubmit={change_name} method="post" className="dashboard-form">
                <div className="form-group">
                    <label htmlFor="new_name">New backup name</label>
                    <input
                        type="text"
                        id="new_name"
                        name="new_name"
                        value={new_name}
                        placeholder="Enter new backup name"
                        onChange={event => {setNewName(event.target.value)}}
                        required
                        />
                </div>

                <button type="submit" className="dashboard-button">
                    Rename
                </button>
            </form>
        </div>



        <div className="dashboard-block danger-block">
            <h2>Delete backup</h2>
            <p>This action permanently deletes the backup from the server.</p>

            <form
                onSubmit={delete_backup}
                method="post"
                >
                <button type="submit" className="dashboard-button danger-button">
                    Delete
                </button>
            </form>
        </div>
        </div>
    }
    </div>
</section>
    )
}



export default BackupPage