

function DocsPage() {
  return (
    <main>
      <section className="page-intro">
        <div className="container">
          <p>Documentation</p>
          <h1>Complete reference for installation, commands, and the backend API.</h1>
        </div>
      </section>

      <section className="docs-section">
        <div className="container">
          <div className="docs-block">
            <h2>Installation</h2>
            <p>Clone the repository and run the setup script. Python 3.8+ is required.</p>
            <pre>
              <code>{`git clone https://github.com/Scroll07/password_manager.git
cd password_manager
./realise.sh`}</code>
            </pre>
            <p>Register on the API (optional), then add your first entry:</p>
            <pre>
              <code>{`pas api register
pas add test -u test -p test --note test`}</code>
            </pre>
          </div>

          <div className="docs-table-block">
            <h2>CLI commands</h2>
            <p>All local vault operations. These work without an API account.</p>
            <table className="docs-table">
              <thead>
                <tr><th>Command</th><th>Description</th><th>Example</th></tr>
              </thead>
              <tbody>
                <tr><td><code>pas add</code></td><td>Add entry</td><td><code>pas add github -u user --gen</code></td></tr>
                <tr><td><code>pas list</code></td><td>List all entries</td><td><code>pas list</code></td></tr>
                <tr><td><code>pas get</code></td><td>Show entry detail</td><td><code>pas get github</code></td></tr>
                <tr><td><code>pas copy</code></td><td>Copy password to clipboard</td><td><code>pas copy 2</code></td></tr>
                <tr><td><code>pas edit</code></td><td>Edit entry</td><td><code>pas edit 1 -p newpass</code></td></tr>
                <tr><td><code>pas del</code></td><td>Delete entry</td><td><code>pas del github</code></td></tr>
                <tr><td><code>pas find</code></td><td>Search entries</td><td><code>pas find @gmail</code></td></tr>
                <tr><td><code>pas reset-session</code></td><td>Reset session token</td><td><code>pas reset-session</code></td></tr>
                <tr><td><code>pas export</code></td><td>Export vault to JSON</td><td><code>pas export backup.json</code></td></tr>
                <tr><td><code>pas import</code></td><td>Import vault from JSON</td><td><code>pas import backup.json</code></td></tr>
                <tr><td><code>pas change-master</code></td><td>Change master password</td><td><code>pas change-master</code></td></tr>
                <tr><td><code>pas create-key</code></td><td>Generate a password</td><td><code>pas create-key -l 32</code></td></tr>
                <tr><td><code>pas config</code></td><td>Configure API token</td><td><code>pas config --token</code></td></tr>
              </tbody>
            </table>
          </div>

          <div className="docs-table-block">
            <h2>API commands</h2>
            <p>Commands that interact with the FastAPI backend. Require a registered account.</p>
            <table className="docs-table">
              <thead>
                <tr><th>Command</th><th>Description</th></tr>
              </thead>
              <tbody>
                <tr><td><code>pas api register</code></td><td>Register a new account on the API</td></tr>
                <tr><td><code>pas api login</code></td><td>Log in and receive JWT tokens</td></tr>
                <tr><td><code>pas api upload</code></td><td>Upload vault backup to the API</td></tr>
                <tr><td><code>pas api download</code></td><td>Download vault backup from the API</td></tr>
                <tr><td><code>pas api delete</code></td><td>Delete a vault backup</td></tr>
              </tbody>
            </table>
          </div>

          <div className="docs-table-block">
            <h2>Backend API endpoints</h2>
            <p>
              REST endpoints exposed by the FastAPI backend. All <code>/backups</code>{' '}
              routes require a valid JWT access token in the Authorization header.
            </p>
            <table className="docs-table">
              <thead>
                <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
              </thead>
              <tbody>
                <tr><td><code>POST</code></td><td><code>/register</code></td><td>Register a new user</td></tr>
                <tr><td><code>POST</code></td><td><code>/login</code></td><td>Login and receive JWT tokens</td></tr>
                <tr><td><code>GET</code></td><td><code>/refresh</code></td><td>Refresh the access token</td></tr>
                <tr><td><code>GET</code></td><td><code>/backups</code></td><td>List all backups for the user</td></tr>
                <tr><td><code>POST</code></td><td><code>/backups/upload</code></td><td>Upload an encrypted vault backup</td></tr>
                <tr><td><code>POST</code></td><td><code>/backups/download</code></td><td>Download a vault backup</td></tr>
                <tr><td><code>DELETE</code></td><td><code>/backups/{'{id}'}</code></td><td>Delete a specific backup</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  )
}

export default DocsPage