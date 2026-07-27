import { useState, useEffect } from "react"
import { NavLink } from 'react-router-dom'
import './BackupPage.css'



function BackupPage(backup_id) {
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')
    const [backup, setBackup] = useState({})




    return (
<section class="dashboard-section user-backup-page">
        { message &&
        <div class="success-message">
            {message}
        </div>}
    
        { error &&
        <div class="error-message">
            {error}
        </div>}
    
    {backup && 
    
    <div class="container">
        
        <div class="dashboard-header">
            <div>
                <a href="{{ url_for('dashboard') }}" class="backup-back-link">← Back to dashboard</a>
                <h1>{backup["name"]}</h1>
                <p>
                    Backup ID: {backup['id']}
                    {/* !!!!!!!!!!!!!!!!! */}
                    {/* !!!!!!!!!!!!!!!!! */}
                    {/* Я ОСТАНОВИЛСЯ ЗДЕСЬ, ДОДЕЛАЙ ЭТУ СТРАНИЦУ */}
                    {/* !!!!!!!!!!!!!!!!! */}
                    {/* !!!!!!!!!!!!!!!!! */}


                    {}
                    {% if backup.created_at_formatted %} · Created: {{ backup.created_at_formatted }}{% endif %}
                    {% if backup.rows is not none %} · Rows: {{ backup.rows }}{% endif %}
                </p>
            </div>
        </div>
        
        <div class="dashboard-block">
            {% if backup.pinned %}
                <h2>Unpin backup</h2>
                <p>Remove this backup from pinned items so it no longer stays highlighted in your list.</p>
            {% else %}
                <h2>Pin backup</h2>
                <p>Pin this backup to keep it highlighted and easier to find in your backups list.</p>
            {% endif %}

            <form action="{{ url_for('web_change_pin', backup_id=backup.id) }}" method="post">
                <button type="submit" class="dashboard-button primary-button">
                    {% if backup.pinned %}
                        Unpin
                    {% else %}
                        Pin
                    {% endif %}
                </button>
            </form>
        </div>

        <div class="dashboard-block">
            <h2>Download backup</h2>
            <p>Download this backup from the server to your local machine.</p>

            <form action="{{ url_for('web_download_post', backup_id=backup.id) }}" method="post">
                <button type="submit" class="dashboard-button primary-button">
                    Download
                </button>
            </form>
        </div>

        <div class="dashboard-block">
            <h2>Rename backup</h2>
            <p>Change the display name of this backup.</p>

            <form action="{{ url_for('web_patch_backup', backup_id=backup.id) }}" method="post" class="dashboard-form">
                <div class="form-group">
                    <label for="new_name">New backup name</label>
                    <input
                        type="text"
                        id="new_name"
                        name="new_name"
                        value="{{ backup.name }}"
                        placeholder="Enter new backup name"
                        required
                        >
                </div>

                <button type="submit" class="dashboard-button">
                    Rename
                </button>
            </form>
        </div>



        <div class="dashboard-block danger-block">
            <h2>Delete backup</h2>
            <p>This action permanently deletes the backup from the server.</p>

            <form
                action="{{ url_for('web_delete_backup', backup_id=backup.id) }}"
                method="post"
                onsubmit="return confirm('Delete this backup? This action cannot be undone.');"
                >
                <button type="submit" class="dashboard-button danger-button">
                    Delete
                </button>
            </form>
        </div>
    </div>
    }
</section>
    )
}



export default BackupPage