import { useEffect, useState } from "react";
import "./App.css";

function App() {
	const API_BASE_URL = "http://127.0.0.1:8001";

	const [token, setToken] = useState(
	  () => sessionStorage.getItem("fraud_token") || ""
	);

	const [username, setUsername] = useState(
	  () => sessionStorage.getItem("fraud_username") || ""
	);

	const [loginUsername, setLoginUsername] = useState("");
	const [loginPassword, setLoginPassword] = useState("");
	const [loginError, setLoginError] = useState("");
	const [loginLoading, setLoginLoading] = useState(false);
	const [formData, setFormData] = useState({
	  transaction_amount: "",
	  transactions_last_10min: "",
	  time_since_last_transaction: "",
	  time_since_unit: "minutes",
	  device_is_new: "",
	  location_is_unusual: "",
	  ip_is_unusual: "",
	  is_unusual_time: "",
	  account_age_days: "",
	  account_age_unit: "days",
   });

  const [result, setResult] = useState(null);
  const [lastEvent, setLastEvent] = useState(null);
  const [aiInvestigation, setAiInvestigation] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");

  const [summary, setSummary] = useState({
    total_assessments: 0,
    low_risk: 0,
    medium_risk: 0,
    high_risk: 0,
  });

  const [assessments, setAssessments] = useState([]);

const handleLogin = async (event) => {
  event.preventDefault();

  setLoginError("");
  setLoginLoading(true);

  try {
    const body = new URLSearchParams();

    body.append("username", loginUsername);
    body.append("password", loginPassword);

    const response = await fetch(
      `${API_BASE_URL}/api/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/x-www-form-urlencoded",
        },
        body,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(
        () => null
      );

      throw new Error(
        errorData?.detail ||
          "Invalid username or password"
      );
    }

    const data = await response.json();

    sessionStorage.setItem(
      "fraud_token",
      data.access_token
    );

    sessionStorage.setItem(
      "fraud_username",
      data.username
    );

    setToken(data.access_token);
    setUsername(data.username);

    setLoginUsername("");
    setLoginPassword("");

  } catch (error) {
    console.error("Login failed:", error);

    setLoginError(
      error.message ||
        "Unable to sign in."
    );
  } finally {
    setLoginLoading(false);
  }
};

const handleLogout = () => {
  sessionStorage.removeItem("fraud_token");
  sessionStorage.removeItem("fraud_username");

  setToken("");
  setUsername("");
};

const authenticatedFetch = async (
  path,
  options = {}
) => {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (response.status === 401) {
    handleLogout();

    throw new Error(
      "Your session has expired. Please log in again."
    );
  }

  return response;
};

  const loadDashboardData = async () => {
  try {
		const [summaryResponse, assessmentsResponse] =
		  await Promise.all([
			authenticatedFetch(
			  "/api/dashboard/summary"
			),
			authenticatedFetch(
			  "/api/assessments?limit=20"
			),
		  ]);

    if (!summaryResponse.ok || !assessmentsResponse.ok) {
      throw new Error("Failed to load dashboard data");
    }

    const summaryData = await summaryResponse.json();
    const assessmentsData =
      await assessmentsResponse.json();

    setSummary(summaryData);
    setAssessments(assessmentsData);

  } catch (error) {
    console.error(
      "Dashboard data loading failed:",
      error
    );
  }
};

useEffect(() => {
  if (!token) {
    return;
  }

  loadDashboardData();
}, [token]);
   const handleChange = (event) => {
	  const { name, value } = event.target;

	  setFormData((previous) => ({
		...previous,
		[name]: value,
	  }));
	};


	const handleSubmit = async (event) => {
	  event.preventDefault();

	  const requiredFields = [
		formData.transaction_amount,
		formData.transactions_last_10min,
		formData.time_since_last_transaction,
		formData.account_age_days,
		formData.device_is_new,
		formData.location_is_unusual,
		formData.ip_is_unusual,
		formData.is_unusual_time,
	  ];

	  if (requiredFields.some((value) => value === "")) {
		setResult({
		  fraud_probability: null,
		  risk_band: "INCOMPLETE",
		  decision: "INPUT REQUIRED",
		  reasons: [
			"Please complete all event fields before running the fraud check."
		  ],
		});

		return;
	  }


	  // Convert user-friendly time to minutes
	  let timeInMinutes = Number(
		formData.time_since_last_transaction
	  );

	  if (formData.time_since_unit === "hours") {
		timeInMinutes *= 60;
	  }

	  if (formData.time_since_unit === "days") {
		timeInMinutes *= 1440;
	  }


	  // Convert account age to days
	  let accountAgeInDays = Number(
		formData.account_age_days
	  );

	  if (formData.account_age_unit === "years") {
		accountAgeInDays *= 365;
	  }


	  try {
		  const eventPayload = {
			  transaction_amount: Number(
				formData.transaction_amount
			  ),
			  transactions_last_10min: Number(
				formData.transactions_last_10min
			  ),
			  time_since_last_transaction:
				timeInMinutes,
			  device_is_new: Number(
				formData.device_is_new
			  ),
			  location_is_unusual: Number(
				formData.location_is_unusual
			  ),
			  ip_is_unusual: Number(
				formData.ip_is_unusual
			  ),
			  is_unusual_time: Number(
				formData.is_unusual_time
			  ),
			  account_age_days:
				Math.round(accountAgeInDays),
			};

			
		const response = await authenticatedFetch(
			"/api/fraud/check",
			{
			method: "POST",
			headers: {
			  "Content-Type": "application/json",
			},

			body: JSON.stringify(eventPayload),
		  }
		);


		if (!response.ok) {
		  throw new Error(
			`API request failed with status ${response.status}`
		  );
		}


		const data = await response.json();

		setResult(data);
		setLastEvent(eventPayload);
		setAiInvestigation(null);
		setAiError("");

		await loadDashboardData();

	  } catch (error) {
		console.error(
		  "Fraud check failed:",
		  error
		);

		setResult({
		  fraud_probability: null,
		  risk_band: "ERROR",
		  decision: "API ERROR",
		  reasons: [
			"Unable to connect to the fraud detection backend."
		  ],
		});
	  }
	};


const handleSimulate = async () => {
  try {
    const response = await authenticatedFetch(
      "/api/fraud/simulate",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        `Simulation request failed with status ${response.status}`
      );
    }

    const data = await response.json();

    setResult(data);

    if (data.event) {
      setLastEvent(data.event);
    }

    setAiInvestigation(null);
    setAiError("");

    await loadDashboardData();

  } catch (error) {
    console.error(
      "Simulation failed:",
      error
    );

    setResult({
      fraud_probability: null,
      risk_band: "ERROR",
      decision: "SIMULATION ERROR",
      reasons: [
        "Unable to generate a simulated incoming transaction."
      ],
    });
  }
};
	
	const handleAiInvestigation = async () => {
  if (!lastEvent) {
    setAiError(
      "Run a fraud assessment before requesting an AI investigation."
    );
    return;
  }

  setAiLoading(true);
  setAiError("");
  setAiInvestigation(null);

  try {
    const response = await authenticatedFetch(
      "/api/fraud/investigate",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(lastEvent),
      }
    );

    if (!response.ok) {
      const errorData =
        await response.json().catch(() => null);

      throw new Error(
        errorData?.detail ||
          `AI investigation failed with status ${response.status}`
      );
    }

    const data = await response.json();

    setAiInvestigation(data.ai_investigation);

  } catch (error) {
    console.error(
      "AI investigation failed:",
      error
    );

    setAiError(
      error.message ||
        "Unable to generate the AI investigation."
    );
  } finally {
    setAiLoading(false);
  }
};

if (!token) {
  return (
    <div className="login-page">

      <div className="login-card">

        <div className="login-brand">
          <h1>FraudSense</h1>

          <p>
            Real-Time Digital Lending
            Risk Intelligence
          </p>
        </div>

        <form onSubmit={handleLogin}>

          <div className="login-field">
            <label>Username</label>

            <input
              type="text"
              value={loginUsername}
              onChange={(event) =>
                setLoginUsername(
                  event.target.value
                )
              }
              placeholder="Enter username"
              required
            />
          </div>

          <div className="login-field">
            <label>Password</label>

            <input
              type="password"
              value={loginPassword}
              onChange={(event) =>
                setLoginPassword(
                  event.target.value
                )
              }
              placeholder="Enter password"
              required
            />
          </div>

          {loginError && (
            <div className="login-error">
              {loginError}
            </div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={loginLoading}
          >
            {loginLoading
              ? "Signing in..."
              : "Sign In"}
          </button>

        </form>

      </div>

    </div>
  );
}

return (
  <div className="app">

      {/* Header */}
      <header className="topbar">
        <div>
         <h1>FraudSense</h1>
	<p>Real-Time Digital Lending Risk Intelligence</p>
        </div>

        <div className="system-status">
			<span className="status-dot"></span>

			<div>
				<strong>System Online</strong>
				<small>API • ML • Database</small>
			</div>
		</div>
		<button
			type="button"
			className="logout-button"
			onClick={handleLogout}
		   >
		    Sign Out
		   </button>
      </header>

      {/* Dashboard summary */}
		<section className="summary-grid">

		  <div className="summary-card">
			<span>Total Assessments</span>
			<strong>{summary.total_assessments}</strong>
		  </div>

		  <div className="summary-card low">
			<span>Low Risk</span>
			<strong>{summary.low_risk}</strong>
		  </div>

		  <div className="summary-card medium">
			<span>Medium Risk</span>
			<strong>{summary.medium_risk}</strong>
		  </div>

		  <div className="summary-card high">
			<span>High Risk</span>
			<strong>{summary.high_risk}</strong>
		  </div>

		</section>

      {/* Main content */}
      <main className="dashboard-grid">

        {/* Fraud check form */}
        <section className="panel">

          <div className="panel-header">
            <h2>Real-Time Fraud Check</h2>
            <p>Submit a fresh digital-lending event for analysis.</p>
          </div>

          <form onSubmit={handleSubmit}>

			  <div className="form-grid">

				{/* Transaction amount */}
				<div className="form-group">
				  <label>Transaction Amount</label>

				  <input
					type="number"
					name="transaction_amount"
					value={formData.transaction_amount}
					onChange={handleChange}
					placeholder="Max ₹5,00,000"
					min="0"
					max="500000"
					step="0.01"
					required
				  />
				</div>


				{/* Transactions in last 10 minutes */}
				<div className="form-group">
				  <label>Transactions / 10 min</label>

				  <input
					type="number"
					name="transactions_last_10min"
					value={formData.transactions_last_10min}
					onChange={handleChange}
					min="0"
					max="10"
					required
				  />
				</div>


				{/* Time since previous event */}
				<div className="form-group">
				  <label>Time Since Previous Event</label>

				  <div className="unit-input-group">

					<input
					  type="number"
					  name="time_since_last_transaction"
					  value={formData.time_since_last_transaction}
					  onChange={handleChange}
					  placeholder="Enter time"
					  min="0.1"
					  step="0.1"
					  required
					/>

					<select
					  name="time_since_unit"
					  value={formData.time_since_unit}
					  onChange={handleChange}
					>
					  <option value="minutes">Minutes</option>
					  <option value="hours">Hours</option>
					  <option value="days">Days</option>
					</select>

				  </div>
				</div>


				{/* Account age */}
				<div className="form-group">
				  <label>Account Age</label>

				  <div className="unit-input-group">

					<input
					  type="number"
					  name="account_age_days"
					  value={formData.account_age_days}
					  onChange={handleChange}
					  placeholder="Max 50 years"
					  min="1"
					  max={
						  formData.account_age_unit === "years"
							? "50"
							: "18250"
						}
					  step="0.1"
					  required
					/>

					<select
					  name="account_age_unit"
					  value={formData.account_age_unit}
					  onChange={handleChange}
					>
					  <option value="days">Days</option>
					  <option value="years">Years</option>
					</select>

				  </div>
				</div>

			  </div>


			  {/* Behavioral signals */}
			  <div className="signal-grid">

				{/* New device */}
				<label className="signal-control">
				  <span>New Device</span>

				  <select
					name="device_is_new"
					value={formData.device_is_new}
					onChange={handleChange}
					required
				  >
					<option value="" disabled hidden></option>
					<option value={0}>No</option>
					<option value={1}>Yes</option>
				  </select>
				</label>


				{/* Unusual location */}
				<label className="signal-control">
				  <span>Unusual Location</span>

				  <select
					name="location_is_unusual"
					value={formData.location_is_unusual}
					onChange={handleChange}
					required
				  >
					<option value="" disabled hidden></option>
					<option value={0}>No</option>
					<option value={1}>Yes</option>
				  </select>
				</label>


				{/* Unusual IP */}
				<label className="signal-control">
				  <span>Unusual IP / Network</span>

				  <select
					name="ip_is_unusual"
					value={formData.ip_is_unusual}
					onChange={handleChange}
					required
				  >
					<option value="" disabled hidden></option>
					<option value={0}>No</option>
					<option value={1}>Yes</option>
				  </select>
				</label>


				{/* Unusual time */}
				<label className="signal-control">
				  <span>Unusual Time</span>

				  <select
					name="is_unusual_time"
					value={formData.is_unusual_time}
					onChange={handleChange}
					required
				  >
					<option value="" disabled hidden></option>
					<option value={0}>No</option>
					<option value={1}>Yes</option>
				  </select>
				</label>

			  </div>


			  {/* Submit button */}
			  <div className="action-buttons">

				<button
					type="submit"
					className="check-button"
				>
					Check Fraud Risk
				</button>

				<button
					type="button"
					className="simulate-button"
					onClick={handleSimulate}
				>
					⚡ Simulate Incoming Transaction
				</button>

			  </div>

			</form>

        </section>

        {/* Result */}
{/* Result */}
	<section className="panel result-panel">

	  <div className="panel-header">
		<h2>Latest Assessment</h2>
		<p>Real-time model assessment</p>
	  </div>

	  {!result ? (
		<div className="empty-result">
		  <div className="empty-icon">✓</div>

		  <h3>Ready for analysis</h3>

		  <p>
			Submit a digital-lending event to generate
			a fraud-risk assessment.
		  </p>
		</div>
	  ) : (
		<div className="result-content">

		  {/* Fraud probability */}
		  <div className="result-score">
			<span>FRAUD PROBABILITY</span>

			<strong>
			  {result.fraud_probability === null
				? "--"
				: `${(
					result.fraud_probability * 100
				  ).toFixed(1)}%`}
			</strong>
		  </div>

		  {/* Risk band */}
		  <div className="result-row">
			<span>Risk Band</span>

			<strong
			  className={
				result.risk_band === "HIGH"
				  ? "assessment-high"
				  : result.risk_band === "MEDIUM"
				  ? "assessment-medium"
				  : result.risk_band === "LOW"
				  ? "assessment-low"
				  : ""
			  }
			>
			  {result.risk_band}
			</strong>
		  </div>

		  {/* Explanation */}
		  {result.reasons &&
			result.reasons.length > 0 && (
			  <div className="reasons-section">

				<h3>WHY WAS THIS FLAGGED?</h3>

				<ul>
				  {result.reasons.map(
					(reason, index) => (
					  <li key={index}>
						{reason}
					  </li>
					)
				  )}
				</ul>

			  </div>
			)}
	
		  {/* Decision */}
		  <div className="result-row decision-row">
			<span>Decision</span>

			<strong
			  className={
				result.decision === "BLOCK"
				  ? "decision-block-large"
				  : result.decision === "REVIEW"
				  ? "decision-review"
				  : result.decision === "APPROVE"
				  ? "decision-approve"
				  : ""
			  }
			>
			  {result.decision}
			</strong>
		  </div>

		</div>
	  )}
	</section>

      </main>
	  
	  {/* AI Investigation */}
<section className="panel ai-investigation-panel">

  <div className="panel-header">
    <h2>AI Investigation</h2>
    <p>
      Evidence-based investigation summary generated from the
      model assessment and fraud knowledge base.
    </p>
  </div>

  <div className="ai-investigation-content">

    <button
      type="button"
      className="ai-investigation-button"
      onClick={handleAiInvestigation}
      disabled={!lastEvent || aiLoading}
    >
      {aiLoading
        ? "Generating AI Investigation..."
        : "Generate AI Investigation"}
    </button>

    {aiError && (
      <div className="ai-investigation-error">
        {aiError}
      </div>
    )}

    {aiInvestigation && (
      <div className="ai-investigation-result">
        <pre>
          {aiInvestigation}
        </pre>
      </div>
    )}

  </div>

</section>


      {/* Recent assessments */}
      <section className="panel recent-panel">

        <div className="panel-header">
          <h2>Recent Assessments</h2>
          <p>Latest fraud assessments recorded by the system.</p>
        </div>

        <div className="table-wrapper">

          <table>

            <thead>
              <tr>
                <th>ID</th>
                <th>Amount</th>
                <th>Probability</th>
                <th>Risk</th>
                <th>Decision</th>
              </tr>
            </thead>

			<tbody>

			  {assessments.length === 0 ? (
				<tr>
				  <td colSpan="5">
					<div className="recent-empty">
						No assessments recorded yet.
					</div>
				</td>
				</tr>
			  ) : (
				assessments.map((assessment) => (
				  <tr key={assessment.id}>

					<td>#{assessment.id}</td>

					<td>
					  {Number(
						assessment.transaction_amount
					  ).toFixed(2)}
					</td>

					<td>
					  {(
						assessment.fraud_probability * 100
					  ).toFixed(1)}%
					</td>

					<td>
					  <span
						className={
						  assessment.risk_band === "HIGH"
							? "badge high-badge"
							: assessment.risk_band === "MEDIUM"
							? "badge medium-badge"
							: "badge low-badge"
						}
					  >
						{assessment.risk_band}
					  </span>
					</td>

					<td>
					  {assessment.decision}
					</td>

				  </tr>
				))
			  )}

			</tbody>

          </table>

        </div>

      </section>

    </div>
  );
}

export default App;