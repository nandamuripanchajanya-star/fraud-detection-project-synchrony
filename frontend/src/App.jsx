import React, {
  useEffect,
  useState
} from "react";
import "./App.css";

function App() {
	const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL ||
	"http://127.0.0.1:8001";

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

   const [validationErrors, setValidationErrors] = useState({});

  const [result, setResult] = useState(null);
  const [lastEvent, setLastEvent] = useState(null);
  const [aiInvestigation, setAiInvestigation] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [fraudLoading, setFraudLoading] = useState(false);
  const [simulateLoading, setSimulateLoading] = useState(false);

  const [summary, setSummary] = useState({
    total_assessments: 0,
    low_risk: 0,
    medium_risk: 0,
    high_risk: 0,
  });

  const [assessments, setAssessments] = useState([]);
  const [expandedAssessmentId, setExpandedAssessmentId] = useState(null);
  const [expandedAssessment, setExpandedAssessment] = useState(null);
  const [expandedAssessmentLoading, setExpandedAssessmentLoading] = useState(false);
  const [expandedAiInvestigation, setExpandedAiInvestigation] = useState(null);
  const [expandedAiLoading, setExpandedAiLoading] = useState(false);
  const [expandedAiError, setExpandedAiError] = useState("");

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

const handleAssessmentClick = async (assessmentId) => {
  // Clicking the already-open row collapses it.
  if (expandedAssessmentId === assessmentId) {
    setExpandedAssessmentId(null);
    setExpandedAssessment(null);
    setExpandedAiInvestigation(null);
    setExpandedAiError("");
    return;
  }

  setExpandedAssessmentId(assessmentId);
  setExpandedAssessment(null);

  // Clear any previous historical AI result.
  setExpandedAiInvestigation(null);
  setExpandedAiError("");

  setExpandedAssessmentLoading(true);

  try {
    const response = await authenticatedFetch(
      `/api/assessments/${assessmentId}`
    );

    if (!response.ok) {
      throw new Error(
        `Failed to load assessment ${assessmentId}`
      );
    }

    const data = await response.json();

    setExpandedAssessment(data);
  } catch (error) {
    console.error(
      "Historical assessment loading failed:",
      error
    );

    setExpandedAssessment({
      error: "Unable to load assessment details."
    });
  } finally {
    setExpandedAssessmentLoading(false);
  }
};

const handleExpandedAiInvestigation = async () => {
  if (!expandedAssessment || expandedAssessment.error) {
    return;
  }

  setExpandedAiLoading(true);
  setExpandedAiError("");
  setExpandedAiInvestigation(null);

  try {
    // The historical assessment endpoint already gives us
    // the original transaction fields needed by /api/fraud/investigate.
    const historicalEvent = {
      transaction_amount: Number(
        expandedAssessment.transaction_amount
      ),
      transactions_last_10min: Number(
        expandedAssessment.transactions_last_10min
      ),
      time_since_last_transaction: Number(
        expandedAssessment.time_since_last_transaction
      ),
      device_is_new: Number(
        expandedAssessment.device_is_new
      ),
      location_is_unusual: Number(
        expandedAssessment.location_is_unusual
      ),
      ip_is_unusual: Number(
        expandedAssessment.ip_is_unusual
      ),
      is_unusual_time: Number(
        expandedAssessment.is_unusual_time
      ),
      account_age_days: Number(
        expandedAssessment.account_age_days
      ),
    };

    const response = await authenticatedFetch(
      "/api/fraud/investigate",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(historicalEvent),
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

    setExpandedAiInvestigation(
      data.ai_investigation
    );
  } catch (error) {
    console.error(
      "Historical AI investigation failed:",
      error
    );

    setExpandedAiError(
      "AI investigation is temporarily unavailable. " +
      "The historical fraud assessment remains valid."
    );
  } finally {
    setExpandedAiLoading(false);
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

  setFormData((previous) => {
    const next = {
      ...previous,
      [name]: value,
    };

    // If there is at least one transaction in the
    // last 10 minutes, previous-event time must use minutes.
    if (
      name === "transactions_last_10min" &&
      Number(value) > 0
    ) {
      next.time_since_unit = "minutes";
    }

    return next;
  });

  setValidationErrors((previous) => ({
    ...previous,
    [name]: "",
  }));

  // If transaction count changes the time rule,
  // clear any old time validation message.
  if (name === "transactions_last_10min") {
    setValidationErrors((previous) => ({
      ...previous,
      transactions_last_10min: "",
      time_since_last_transaction: "",
    }));
  }
};

	const validateForm = () => {
		const errors = {};
		const invalidFields = new Set();

		const amount = Number(formData.transaction_amount);
		const transactionsLast10Min = Number(
			formData.transactions_last_10min
		);
		const timeSinceLastTransaction = Number(
			formData.time_since_last_transaction
		);
		const accountAge = Number(
			formData.account_age_days
		);

		/* ---------------- Transaction amount ---------------- */

		if (formData.transaction_amount === "") {
			errors.transaction_amount = "Invalid amount";
			invalidFields.add("transaction_amount");
		} else if (
			!Number.isFinite(amount) ||
			amount < 1 ||
			amount > 500000
		) {
			errors.transaction_amount = "Invalid amount";
			invalidFields.add("transaction_amount");
		}

		/* ---------------- Transaction velocity ---------------- */

		if (formData.transactions_last_10min === "") {
			errors.transactions_last_10min =
			"Invalid transaction count";
			invalidFields.add("transactions_last_10min");
		} else if (
			!Number.isInteger(transactionsLast10Min) ||
			transactionsLast10Min < 0 ||
			transactionsLast10Min > 10
		) {
			errors.transactions_last_10min =
			"Invalid transaction count";
			invalidFields.add("transactions_last_10min");
		}

		/* ---------------- Time since previous event ---------------- */

		if (formData.time_since_last_transaction === "") {
		errors.time_since_last_transaction =
			"Invalid time";
		invalidFields.add("time_since_last_transaction");
		} else if (
		!Number.isInteger(timeSinceLastTransaction) ||
		timeSinceLastTransaction <= 0
		) {
		errors.time_since_last_transaction =
			"Invalid time";
		invalidFields.add("time_since_last_transaction");
		} else if (
		Number(formData.transactions_last_10min) > 0 &&
		(
			formData.time_since_unit !== "minutes" ||
			timeSinceLastTransaction > 10
		)
		) {
		errors.time_since_last_transaction =
			"Invalid time";
		invalidFields.add("time_since_last_transaction");
		}

		/* ---------------- Account age ---------------- */

		if (formData.account_age_days === "") {
		errors.account_age_days =
			"Invalid account age";
		invalidFields.add("account_age_days");
		} else {
		const accountAgeValid =
			Number.isInteger(accountAge) &&
			(
			formData.account_age_unit === "years"
				? accountAge >= 1 && accountAge <= 50
				: accountAge >= 1 && accountAge <= 18250
			);

		if (!accountAgeValid) {
			errors.account_age_days =
			"Invalid account age";
			invalidFields.add("account_age_days");
		}
		}

		/* ---------------- Behavioural selections ---------------- */

		const selectionFields = [
			{
			name: "device_is_new",
			label: "New Device",
			},
			{
			name: "location_is_unusual",
			label: "Unusual Location",
			},
			{
			name: "ip_is_unusual",
			label: "Unusual IP / Network",
			},
			{
			name: "is_unusual_time",
			label: "Unusual Time",
			},
		];

		selectionFields.forEach(({ name, label }) => {
			if (
			formData[name] !== "0" &&
			formData[name] !== "1"
			) {
			errors[name] = `Please select ${label}`;
			invalidFields.add(name);
			}
		});

		/*
		* Time since previous event must not exceed
		* the account age.
		*
		* Both values are converted to days before comparison.
		*/

		if (
			!invalidFields.has(
			"time_since_last_transaction"
			) &&
			!invalidFields.has("account_age_days")
		) {
			let timeInDays =
			timeSinceLastTransaction;

			if (formData.time_since_unit === "hours") {
			timeInDays /= 24;
			} else if (formData.time_since_unit === "minutes") {
			timeInDays /= 1440;
			} else if (formData.time_since_unit === "years") {
			timeInDays *= 365;
			}

			let accountAgeInDays = accountAge;

			if (formData.account_age_unit === "years") {
			accountAgeInDays *= 365;
			}

			if (timeInDays > accountAgeInDays) {
			errors.time_since_last_transaction =
				"Invalid time";
			invalidFields.add(
				"time_since_last_transaction"
			);
			}
		}

		return {
			errors,
			invalidFields,
		};
		};


	const handleSubmit = async (event) => {
event.preventDefault();

const { errors } = validateForm();

if (Object.keys(errors).length > 0) {
  setValidationErrors(errors);
  return;
}

setValidationErrors({});
setFraudLoading(true);

// Convert user-friendly time to minutes



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
	  } finally {
		setFraudLoading(false);
	  }
	};


const handleSimulate = async () => {
	setSimulateLoading(true);
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
  finally {
    setSimulateLoading(false);
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
       "AI investigation is temporarily unavailable. " +
       "The fraud assessment and decision above remain valid."
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
			<label
				htmlFor="login-username"
				className="login-label"
			>
				Username
			</label>

			<input
				id="login-username"
				type="text"
				value={loginUsername}
				onChange={(event) =>
				setLoginUsername(event.target.value)
				}
				placeholder="Username"
				required
				aria-required="true"
			/>
			</div>

          <div className="login-field">
			<label
				htmlFor="login-password"
				className="login-label"
			>
				Password
			</label>

			<input
				id="login-password"
				type="password"
				value={loginPassword}
				onChange={(event) =>
				setLoginPassword(event.target.value)
				}
				placeholder="Password"
				required
				aria-required="true"
			/>
			</div>

          {loginError && (
            <div
				className="login-error"
				role="alert"
				aria-live="assertive"
			>
  				{loginError}
			</div>
          )}

          <button
			type="submit"
			className="login-button"
			disabled={loginLoading}
		  >
			{loginLoading ? (
			  <span className="login-loading-content">
				<span
					className="login-spinner"
					aria-hidden="true"
				></span>
				Signing in...
			  </span>
			) : (
				"Sign In"
			)}
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
			<span
				className="status-dot"
				role="status"
				aria-label="System online: API, ML, and Database connected"
			/>

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

          <form
  onSubmit={handleSubmit}
  noValidate
>

			  	<div className="form-grid">

				{/* Transaction amount */}
				<div className="form-group">
					<label htmlFor="transaction-amount">
						Transaction Amount
					</label>

					<input
						id="transaction-amount"
						type="number"
						name="transaction_amount"
						value={formData.transaction_amount}
						onChange={handleChange}
						placeholder="Max ₹5,00,000"
						min="1"
						max="500000"
						step="0.01"
						required
						aria-required="true"
					/>

					{validationErrors.transaction_amount && (
						<div className="field-validation-error">
						<span className="validation-error-icon">
							!
						</span>
						{validationErrors.transaction_amount}
						</div>
					)}
					</div>


				{/* Transactions in last 10 minutes */}
				<div className="form-group">
				<label htmlFor="transactions-last-10min">
					Transactions / 10 min
				</label>

				<input
					id="transactions-last-10min"
					type="number"
					name="transactions_last_10min"
					value={formData.transactions_last_10min}
					onChange={handleChange}
					min="0"
					max="10"
					step="1"
					required
					aria-required="true"
				/>

				{validationErrors.transactions_last_10min && (
					<div className="field-validation-error">
					<span className="validation-error-icon">
						!
					</span>
					{validationErrors.transactions_last_10min}
					</div>
				)}
				</div>


				{/* Time since previous event */}
				<div className="form-group">
				<label htmlFor="time-since-previous">
					Time Since Previous Event
				</label>

				<div className="unit-input-group">
				<input
				id="time-since-previous"
				type="number"
				name="time_since_last_transaction"
				value={formData.time_since_last_transaction}
				onChange={handleChange}
				placeholder="Enter time"
				min="1"
				max={
					Number(formData.transactions_last_10min) > 0
					? "10"
					: undefined
				}
				step="1"
				required
				aria-required="true"
				/>

						<select
							id="time-since-unit"
							name="time_since_unit"
							value={formData.time_since_unit}
							onChange={handleChange}
							aria-label="Time unit for previous event"
							>
							<option value="minutes">Minutes</option>

							{Number(formData.transactions_last_10min) === 0 && (
								<>
								<option value="hours">Hours</option>
								<option value="days">Days</option>
								<option value="years">Years</option>
								</>
							)}
						</select>
				</div>

				{validationErrors.time_since_last_transaction && (
					<div className="field-validation-error">
					<span className="validation-error-icon">
						!
					</span>
					{validationErrors.time_since_last_transaction}
					</div>
				)}
				</div>


				{/* Account age */}
				<div className="form-group">
				<label htmlFor="account-age">
					Account Age
				</label>

				<div className="unit-input-group">
					<input
						id="account-age"
						aria-required="true"
						type="number"
						name="account_age_days"
						value={formData.account_age_days}
						onChange={handleChange}
						placeholder="Max 50 years"
						min={
							formData.account_age_unit === "years"
							? "1"
							: "1"
						}
						max={
							formData.account_age_unit === "years"
							? "50"
							: "18250"
						}
						step="1"
						required
						/>

					<select
					id="account-age-unit"
					name="account_age_unit"
					value={formData.account_age_unit}
					onChange={handleChange}
					aria-label="Account age unit"
					>
					<option value="days">Days</option>
					<option value="years">Years</option>
					</select>
				</div>

				{validationErrors.account_age_days && (
					<div className="field-validation-error">
					<span className="validation-error-icon">
						!
					</span>
					{validationErrors.account_age_days}
					</div>
				)}
				</div>
				</div>


			  {/* Behavioral signals */}
			  <div className="signal-grid">

				{/* New device */}
				<label className="signal-control">
					<span>New Device</span>

					<select
						id="new-device"
						name="device_is_new"
						value={formData.device_is_new}
						onChange={handleChange}
						required
						aria-required="true"
					>
						<option value="" disabled hidden></option>
						<option value="0">No</option>
						<option value="1">Yes</option>
					</select>

					{validationErrors.device_is_new && (
						<div className="field-validation-error">
						<span className="validation-error-icon">!</span>
						{validationErrors.device_is_new}
						</div>
					)}
					</label>


				{/* Unusual location */}
				<label className="signal-control">
				  <span>Unusual Location</span>

				  <select
				    id="unusual-location"
					name="location_is_unusual"
					value={formData.location_is_unusual}
					onChange={handleChange}
					required
					aria-required="true"
				  >
					{validationErrors.location_is_unusual && (
						<div className="field-validation-error">
							<span className="validation-error-icon">
							!
							</span>
							{validationErrors.location_is_unusual}
						</div>
						)}
					<option value="" disabled hidden></option>
					<option value="0">No</option>
					<option value="1">Yes</option>
				  </select>
				</label>


				{/* Unusual IP */}
				<label className="signal-control">
				  <span>Unusual IP / Network</span>

				  <select
				    id="unusual-ip"
					name="ip_is_unusual"
					value={formData.ip_is_unusual}
					onChange={handleChange}
					required
					aria-required="true"
				  >
					{validationErrors.ip_is_unusual && (
						<div className="field-validation-error">
							<span className="validation-error-icon">
							!
							</span>
							{validationErrors.ip_is_unusual}
						</div>
						)}
					<option value="" disabled hidden></option>
					<option value="0">No</option>
					<option value="1">Yes</option>
				  </select>
				</label>


				{/* Unusual time */}
				<label className="signal-control">
				  <span>Unusual Time</span>

				  <select
				    id="unusual-time"
					name="is_unusual_time"
					value={formData.is_unusual_time}
					onChange={handleChange}
					required
					aria-required="true"
				  >
					{validationErrors.is_unusual_time && (
						<div className="field-validation-error">
							<span className="validation-error-icon">
							!
							</span>
							{validationErrors.is_unusual_time}
						</div>
						)}
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
 					disabled={fraudLoading}
                    aria-label="Check fraud risk for the entered transaction"
                    aria-busy={fraudLoading}
            >
  					{fraudLoading ? "Analyzing..." : "Check Fraud Risk"}
			</button>

				<button
					type="button"
					className="simulate-button"
					onClick={handleSimulate}
					disabled={simulateLoading}
					aria-label="Simulate an incoming transaction"
					aria-busy={simulateLoading}
				>
					{simulateLoading
						? "Simulating..."
						: "⚡ Simulate Incoming Transaction"}
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
		<div
           className="result-content"
           aria-live="polite"
           aria-atomic="true"
        >

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
			  aria-label={`Risk band: ${result.risk_band}`}
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
		  <div className="reasons-section">

				<h3>WHY WAS THIS FLAGGED?</h3>

				<ul>
  					{result.reasons && result.reasons.length > 0 ? (
    					result.reasons.map((reason, index) => (
      						<li key={index}>{reason}</li>
    					))
  					) : (
    					<li>No major behavioral anomalies detected.</li>
  					)}
				</ul>
			  </div>
	
		  {/* Decision */}
		  <div className="result-row decision-row">
			<span>Decision</span>

			<strong
				aria-label={
					result.decision === "APPROVE"
					? "Decision: APPROVE. Normal transaction."
					: result.decision === "REVIEW"
					? "Decision: REVIEW. Manual verification recommended."
					: result.decision === "BLOCK"
					? "Decision: BLOCK. Transaction should be blocked."
					: `Decision: ${result.decision}`
				}
				title={
					result.decision === "APPROVE"
					? "Normal transaction"
					: result.decision === "REVIEW"
					? "Manual verification recommended"
					: result.decision === "BLOCK"
					? "Transaction should be blocked"
					: "Assessment decision"
				}
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
		aria-label="Generate AI investigation for the latest assessment"
		aria-disabled={!lastEvent || aiLoading}
	>
      {aiLoading
        ? "Generating AI Investigation..."
        : "Generate AI Investigation"}
    </button>

    {aiError && (
      <div
		className="ai-investigation-error"
		role="alert"
		aria-live="assertive"
	  >
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
                <th scope="col">ID</th>
				<th scope="col">Amount</th>
				<th scope="col">Probability</th>
				<th scope="col">Risk</th>
				<th scope="col">Decision</th>
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
					<React.Fragment key={assessment.id}>
						<tr
						className="assessment-clickable-row"
						onClick={() =>
							handleAssessmentClick(assessment.id)
						}
						tabIndex="0"
						role="button"
						aria-expanded={
							expandedAssessmentId === assessment.id
						}
						onKeyDown={(event) => {
							if (
							event.key === "Enter" ||
							event.key === " "
							) {
							event.preventDefault();
							handleAssessmentClick(assessment.id);
							}
						}}
						>
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
							<div className="assessment-decision-cell">
								<span>{assessment.decision}</span>

								<span
								className="assessment-expand-indicator"
								aria-hidden="true"
								>
								{expandedAssessmentId === assessment.id
									? "⌄"
									: ">"}
								</span>
							</div>
							</td>
						</tr>

						{expandedAssessmentId === assessment.id && (
						<tr className="assessment-expanded-row">
							<td colSpan="5">
							{expandedAssessmentLoading ? (
								<div className="assessment-expanded-loading">
								Loading assessment details...
								</div>
							) : expandedAssessment?.error ? (
								<div className="assessment-expanded-error">
								{expandedAssessment.error}
								</div>
							) : expandedAssessment ? (
								<div className="assessment-expanded-content">

								<div className="expanded-result-score">
									<span>FRAUD PROBABILITY</span>

									<strong>
									{(
										expandedAssessment.fraud_probability * 100
									).toFixed(1)}
									%
									</strong>
								</div>

								<div className="expanded-result-row">
									<span>Risk Band</span>

									<strong
									className={
										expandedAssessment.risk_band === "HIGH"
										? "assessment-high"
										: expandedAssessment.risk_band === "MEDIUM"
										? "assessment-medium"
										: expandedAssessment.risk_band === "LOW"
										? "assessment-low"
										: ""
									}
									>
									{expandedAssessment.risk_band}
									</strong>
								</div>

								<div className="expanded-reasons-section">
									<h3>WHY WAS THIS FLAGGED?</h3>

									<ul>
									{expandedAssessment.reasons &&
									expandedAssessment.reasons.length > 0 ? (
										expandedAssessment.reasons.map(
										(reason, index) => (
											<li key={index}>
											{reason}
											</li>
										)
										)
									) : (
										<li>
										No major behavioral anomalies detected.
										</li>
									)}
									</ul>
								</div>

								<div className="expanded-result-row expanded-decision-row">
									<span>Decision</span>

									<strong
									className={
										expandedAssessment.decision === "BLOCK"
										? "decision-block-large"
										: expandedAssessment.decision === "REVIEW"
										? "decision-review"
										: expandedAssessment.decision === "APPROVE"
										? "decision-approve"
										: ""
									}
									>
									{expandedAssessment.decision}
									</strong>
								</div>

								<div className="expanded-ai-section">
									<button
									type="button"
									className="expanded-ai-button"
									onClick={(event) => {
										event.stopPropagation();
										handleExpandedAiInvestigation();
									}}
									disabled={expandedAiLoading}
									aria-busy={expandedAiLoading}
									>
									{expandedAiLoading
										? "Generating AI Investigation..."
										: "Generate AI Investigation"}
									</button>

									{expandedAiError && (
									<div
										className="expanded-ai-error"
										role="alert"
										aria-live="assertive"
									>
										{expandedAiError}
									</div>
									)}

									{expandedAiInvestigation && (
									<div className="expanded-ai-result">
										<h3>AI INVESTIGATION</h3>

										<pre>
										{expandedAiInvestigation}
										</pre>
									</div>
									)}
								</div>

								</div>
							) : null}
							</td>
						</tr>
						)}
					</React.Fragment>
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