import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import './DashboardPage.css'

function DashboardPage() {
    url = '/api/dashboard'
    response = await fetch(
        url,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
        }
    )



    return (
        <section class="dashboard-section">
            <div class="container">
                <div class="dashboard-header">
                    <div>
                        <h1>Hello, user</h1>
                        <p>Session active — API connected</p>
                    </div>

                    <form onSubmit={Функцию сюда для logout} method="post">
                        <button id="dashboard-logout" class="dashboard-logout" type="submit">Log out</button>
                    </form>
                </div>

                <div class="dashboard-block">
                    {% set pinned_backups = backups | selectattr('pinned') | list %}

                    {% if pinned_backups %}
                        <h2>Pinned Backups</h2>
                        <table class="dashboard-table">
                            <thead>
                                <tr>
                                    <th>name</th>
                                    <th>date</th>
                                    <th>rows</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for backup in backups if backup.pinned %}
                                <tr>
                                    <td>
                                        <NavLink to="{{ url_for('user_backup', backup_id=backup.id) }}" class="backup-name">
                                            {{ backup.name }}
                                        </NavLink>
                                    </td>
                                    <td>{{ backup.created_at_formatted }}</td>
                                    <td>{{ backup.rows }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% endif %}

                    <div class="backups-header">
                        <h2>Backups</h2>

                        <div class="sort-links">
                            <span class="sort-label">Sort by:</span>

                            <NavLink
                                to='/dashboard?sort_by=created_at'
                                class="sort-link"
                            >
                                Date
                            </NavLink>
                            

                            <NavLink
                                to="/dashboard?sort_by=name"
                                class="sort-link"
                            >
                                Name
                            </NavLink>

                            <NavLink
                                to="/dashboard?sort_by=rows"
                                class="sort-link"
                            >
                                Rows
                            </NavLink>
                        </div>
                    </div>

                    <table class="dashboard-table">
                        <thead>
                            <tr>
                                <th>name</th>
                                <th>date</th>
                                <th>rows</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for backup in backups if not backup.pinned %}
                            <tr>
                                <td>
                                    <NavLink href="{{ url_for('user_backup', backup_id=backup.id) }}" class="backup-name">
                                        {{ backup.name }}
                                    </NavLink>
                                </td>
                                <td>{{ backup.created_at_formatted }}</td>
                                <td>{{ backup.rows }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    )
}


export default DashboardPage