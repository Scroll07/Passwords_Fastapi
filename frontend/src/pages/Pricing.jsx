import './static_pages.css'

function PricingPage() {
  return (
    <main>
      <section className="page-intro">
        <div className="container">
          <p>Pricing</p>
          <h1>Local and Sync are both available today.</h1>
          <p>
            Local stays free, while Sync is a paid plan for backup and restore
            across machines. Team features are currently in development.
          </p>
        </div>
      </section>

      <section className="pricing-table-section">
        <div className="container">
          <table className="pricing-table">
            <thead>
              <tr>
                <th></th>
                <th>Local</th>
                <th>Sync</th>
                <th>Team</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Encrypted local vault</td><td>✓</td><td>✓</td><td className='unavailable'>—</td></tr>
              <tr><td>All CLI commands</td><td>✓</td><td>✓</td><td className='unavailable'>—</td></tr>
              <tr><td>Password generation</td><td>✓</td><td>✓</td><td className='unavailable'>—</td></tr>
              <tr><td>JSON export / import</td><td>✓</td><td>✓</td><td className='unavailable'>—</td></tr>
              <tr><td>API backup sync</td><td className='unavailable'>—</td><td>✓</td><td className='unavailable'>—</td></tr>
              <tr><td>Multi-machine restore</td><td className='unavailable'>—</td><td>✓</td><td className='unavailable'>—</td></tr>
              <tr><td>Shared vault</td><td className='unavailable'>—</td><td className='unavailable'>—</td><td className='unavailable'>—</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="pricing-plans">
        <div className="container">
          <div className="plan-card">
            <h2>Local</h2>
            <p>Full CLI functionality, local vault only. No account required.</p>
          </div>
          <div className="plan-card">
            <h2>Sync</h2>
            <p>Local features plus API account for cross-machine backup sync.</p>
          </div>
          <div className="plan-card">
            <h2>Team</h2>
            <p>Planned for teams who need shared vault management and access control.</p>
          </div>
        </div>
      </section>

      <section className="page-note">
        <div className="container">
          <p>
            Pas CLI is open source. You can self-host the backend with no usage
            limits or licensing fees. See the repository for Docker setup
            instructions.
          </p>
          <a href="https://github.com/Scroll07/password_manager" target="_blank" rel="noopener noreferrer">
            View on GitHub →
          </a>
        </div>
      </section>
    </main>
  )
}

export default PricingPage