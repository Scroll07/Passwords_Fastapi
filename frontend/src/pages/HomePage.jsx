import { NavLink } from 'react-router-dom'
import './static_pages.css'

function HomePage() {
  return (
    <main className="home-page">
      <section className="hero">
        <div className="container">
          <p className="hero-badge">v1.2.0 — open source</p>
          <h1>Password management for the command line.</h1>
          <p className="hero-description">
            Pas CLI is a local-first password manager for developers.
            Store credentials in an encrypted vault on your machine,
            with optional API sync for cross-machine backup.
          </p>

          <div className="hero-actions">
            <a
              href="https://github.com/Scroll07/password_manager"
              target="_blank"
              rel="noopener noreferrer"
            >
              Get started
            </a>
            <NavLink to="/product">Read about the product</NavLink>
          </div>

          <div className="hero-code">
            <pre>
              <code>{`git clone https://github.com/Scroll07/password_manager
cd password_manager && ./realise.sh

pas add github -u myuser --gen
Entry added. Password generated (32 chars).

pas copy github
Password copied to clipboard.

pas api upload
Vault backed up to API.`}</code>
            </pre>
          </div>
        </div>
      </section>

      <section className="about-product">
        <div className="container">
          <h2>What Pas CLI does</h2>
          <p>
            Pas CLI is split into two parts. The CLI client handles all local vault
            operations — adding, searching, copying, and editing credentials —
            entirely on your machine.
          </p>
          <p>
            The FastAPI backend is optional and adds registration, login,
            and encrypted vault backup sync so you can restore your vault on another machine.
          </p>
          <p>
            The vault is encrypted and protected by a master password that never leaves your device.
          </p>
        </div>
      </section>

      <section className="commands">
        <div className="container">
          <h2>Common commands</h2>

          <table className="commands-table">
            <tbody>
              <tr>
                <td><code>pas add github -u user --gen</code></td>
                <td>Add an entry and auto-generate a password</td>
              </tr>
              <tr>
                <td><code>pas copy github</code></td>
                <td>Copy a password to clipboard</td>
              </tr>
              <tr>
                <td><code>pas find gmail.com</code></td>
                <td>Search entries by pattern</td>
              </tr>
              <tr>
                <td><code>pas export backup.json</code></td>
                <td>Export vault to a local JSON file</td>
              </tr>
              <tr>
                <td><code>pas api upload</code></td>
                <td>Back up vault to the API</td>
              </tr>
              <tr>
                <td><code>pas api download</code></td>
                <td>Restore vault from the API on a new machine</td>
              </tr>
            </tbody>
          </table>

          <NavLink className="text-link" to="/docs">
            View full command reference
          </NavLink>
        </div>
      </section>

      <section className="developer-note">
        <div className="container">
          <h2>Built by a developer, for developers</h2>
          <p>
            This is a real project built by a student developer.
            It is open source, documented, and actively maintained.
            If you prefer the terminal over GUI apps, Pas CLI is for you.
          </p>

          <div className="hero-actions">
            <a
              href="https://github.com/Scroll07/password_manager"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
            <NavLink to="/how_it_works">See how it works</NavLink>
          </div>
        </div>
      </section>
    </main>
  )
}

export default HomePage