import './static_pages.css'

function HowItWorksPage() {
  return (
    <main>
      <section className="page-intro">
        <div className="container">
          <p>How It Works</p>
          <h1>Pas CLI is designed to be straightforward.</h1>
          <p>
            You can be up and running with a local vault in under two minutes, and
            optionally add API backup sync when you need it.
          </p>
        </div>
      </section>

      <section className="steps-section">
        <div className="container">
          <div className="step">
            <p>01</p>
            <h2>Clone and install</h2>
            <p>
              Clone the repository and run the setup script. This installs the CLI
              and sets up your initial configuration.
            </p>
            <pre>
              <code>{`git clone https://github.com/Scroll07/password_manager.git
cd password_manager
./realise.sh`}</code>
            </pre>
          </div>

          <div className="step">
            <p>02</p>
            <p>
              Optional but recommended for backup sync. Register an account on your
              self-hosted backend instance. This generates your JWT credentials.
            </p>
            <pre><code>pas api register</code></pre>
          </div>

          <div className="step">
            <p>03</p>
            <p>
              Add a password entry to your local vault. Use <code>--gen</code> to
              auto-generate a strong password, or <code>-p</code> to set one manually.
            </p>
            <pre>
              <code>{`pas add github -u myuser --gen

pas add github -u myuser -p mypassword --note "personal account"`}</code>
            </pre>
          </div>

          <div className="step">
            <p>04</p>
            <p>
              Use the CLI to look up credentials, copy passwords to clipboard, edit
              entries, or delete ones you no longer need.
            </p>
            <pre>
              <code>{`pas find gmail.com
pas copy github
pas edit 1 -p newpass
pas del github`}</code>
            </pre>
          </div>

          <div className="step">
            <p>05</p>
            <p>
              Export your vault to a local JSON file for manual backups, or upload a
              snapshot to the API for cloud-accessible restore.
            </p>
            <pre>
              <code>{`pas export backup.json
pas api upload`}</code>
            </pre>
          </div>

          <div className="step">
            <p>06</p>
            <p>
              On a new machine, clone the repo, install Pas CLI, log in to the API,
              and download your vault backup. Your credentials are available
              immediately.
            </p>
            <pre>
              <code>{`pas api login
pas api download`}</code>
            </pre>
          </div>
        </div>
      </section>

      <section className="page-note">
        <div className="container">
          <p>
            Need the full command reference? The docs page has complete tables for
            all CLI and API commands plus backend endpoint documentation.
          </p>
          <a href="https://github.com/Scroll07/password_manager" target="_blank" rel="noopener noreferrer">
            View on GitHub
          </a>
        </div>
      </section>
    </main>
  )
}

export default HowItWorksPage