import './static_pages.css'

function ProductPage() {
  return (
    <main className="product-content">
      <section className="page-intro">
        <div className="container">
          <p>Product</p>
          <h1>What is Pas CLI</h1>
          <p>
            Pas CLI is a command-line password manager designed for developers and
            technical users who prefer working in the terminal. It stores credentials
            in a locally encrypted vault, protected by a master password that never
            leaves your device.
          </p>
          <p>
            The tool supports an optional FastAPI backend for account-based vault
            backup sync — useful when you work across multiple machines. The backend
            is self-hosted and open source.
          </p>
        </div>
      </section>

      <section>
        <div className="container">
          <h2>Who it is for</h2>
          <p>
            Pas CLI is built for developers, students, and technical users who are
            comfortable in the terminal and prefer minimal, scriptable tooling.
          </p>
          <ul>
            <li>Developers managing credentials for multiple projects and services.</li>
            <li>Students learning secure credential handling.</li>
            <li>Technical users who want a CLI-native workflow without a SaaS dependency.</li>
            <li>Anyone who wants self-hosted backup control.</li>
          </ul>
        </div>
      </section>

      <section>
        <div className="container">
          <h2>Architecture</h2>
          <p>
            The project is split into two independent components that can be used
            together or separately.
          </p>

          <h3>CLI Client</h3>
          <p>
            A Python command-line tool for local vault operations. Runs entirely on
            your machine. Handles add, search, copy, edit, delete, export, import,
            password generation, and session management. Does not require the backend
            to function.
          </p>

          <h3>FastAPI Backend</h3>
          <p>
            An optional REST API server for user registration, JWT authentication,
            and vault backup management. Stores encrypted vault snapshots per user.
            Enables multi-machine restore via <code>pas api download</code>.
          </p>
        </div>
      </section>

      <section>
        <div className="container">
          <h2>CLI commands</h2>
          <p>The CLI provides a complete set of local vault operations:</p>
          <ul>
            <li>Add, edit, and delete password entries.</li>
            <li>Search entries by name, username, or note.</li>
            <li>Copy passwords directly to clipboard.</li>
            <li>Generate strong passwords with configurable length.</li>
            <li>Export and import vault as JSON.</li>
            <li>Change master password.</li>
            <li>Reset session tokens.</li>
            <li>Manage API connection config.</li>
          </ul>
        </div>
      </section>

      <section>
        <div className="container">
          <h2>Backend capabilities</h2>
          <p>The FastAPI backend handles authentication and backup operations:</p>
          <ul>
            <li>User registration and login.</li>
            <li>JWT access and refresh token issuance.</li>
            <li>Upload and download vault backup snapshots.</li>
            <li>List and delete existing backups.</li>
            <li>Protected routes that require valid JWT.</li>
          </ul>
        </div>
      </section>

      <section>
        <div className="container">
          <h2>Technology stack</h2>
          <table>
            <tbody>
              <tr>
                <th>CLI</th>
                <td>Python</td>
              </tr>
              <tr>
                <th>Backend</th>
                <td>Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic · Docker · pytest</td>
              </tr>
            </tbody>
          </table>
          <p>The source code, README, and installation instructions are available on GitHub.</p>
        </div>
      </section>
    </main>
  )
}

export default ProductPage