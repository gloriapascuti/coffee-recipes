import React, { useState } from 'react';
import styles from './styles/Prediction.module.css';

const API_URL = 'http://127.0.0.1:8000/api';

function authHeaders() {
    const accessToken = localStorage.getItem("access_token");
    const headers = {
        "Content-Type": "application/json"
    };
    if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`;
    }
    return headers;
}

export default function Prediction({ consumedCoffees }) {
    const [period, setPeriod] = useState('week');
    const [systolic, setSystolic] = useState('');
    const [diastolic, setDiastolic] = useState('');
    const [pulse, setPulse] = useState('');
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleGeneratePrediction = async () => {
        try {
            setLoading(true);
            setError(null);

            const requestBody = { period };
            if (systolic && diastolic) {
                requestBody.systolic = parseInt(systolic);
                requestBody.diastolic = parseInt(diastolic);
                if (pulse) {
                    requestBody.pulse = parseInt(pulse);
                }
            }

            const response = await fetch(`${API_URL}/prediction/`, {
                method: 'POST',
                headers: authHeaders(),
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to generate prediction');
            }

            const data = await response.json();
            setPrediction(data);
        } catch (err) {
            setError(err.message);
            console.error('Error generating prediction:', err);
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (category) => {
        switch (category) {
            case 'low':
                return '#4caf50';
            case 'moderate':
                return '#ff9800';
            case 'high':
                return '#f44336';
            default:
                return '#757575';
        }
    };

    const getRiskLabel = (category) => {
        switch (category) {
            case 'low':
                return 'Low Risk';
            case 'moderate':
                return 'Moderate Risk';
            case 'high':
                return 'High Risk';
            default:
                return 'Unknown';
        }
    };

    return (
        <div className={styles.container}>
            <h2 className={styles.title}>Generate Heart Disease Risk Prediction</h2>
            
            <div className={styles.formSection}>
                <div className={styles.periodSelector}>
                    <label>Prediction Period:</label>
                    <div className={styles.radioGroup}>
                        <label>
                            <input
                                type="radio"
                                value="week"
                                checked={period === 'week'}
                                onChange={(e) => setPeriod(e.target.value)}
                            />
                            Week
                        </label>
                        <label>
                            <input
                                type="radio"
                                value="month"
                                checked={period === 'month'}
                                onChange={(e) => setPeriod(e.target.value)}
                            />
                            Month
                        </label>
                        <label>
                            <input
                                type="radio"
                                value="year"
                                checked={period === 'year'}
                                onChange={(e) => setPeriod(e.target.value)}
                            />
                            Year
                        </label>
                    </div>
                </div>

                <div className={styles.bpSection}>
                    <h3>Optional: Blood Pressure (for this prediction)</h3>
                    <p className={styles.helpText}>
                        You can optionally provide your current blood pressure reading.
                        If not provided, the system will use your most recent entry.
                    </p>
                    <div className={styles.bpInputs}>
                        <div className={styles.inputGroup}>
                            <label>Systolic (Big Number):</label>
                            <input
                                type="number"
                                value={systolic}
                                onChange={(e) => setSystolic(e.target.value)}
                                placeholder="e.g., 120"
                                min="70"
                                max="250"
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Diastolic (Small Number):</label>
                            <input
                                type="number"
                                value={diastolic}
                                onChange={(e) => setDiastolic(e.target.value)}
                                placeholder="e.g., 80"
                                min="40"
                                max="150"
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Pulse (Optional):</label>
                            <input
                                type="number"
                                value={pulse}
                                onChange={(e) => setPulse(e.target.value)}
                                placeholder="e.g., 72"
                                min="30"
                                max="200"
                            />
                        </div>
                    </div>
                </div>

                <button
                    className={styles.generateButton}
                    onClick={handleGeneratePrediction}
                    disabled={loading}
                >
                    {loading ? 'Generating...' : 'Generate Prediction'}
                </button>
            </div>

            {error && (
                <div className={styles.error}>
                    {error}
                </div>
            )}

            {prediction && (
                <div className={styles.results}>
                    <div
                        className={styles.riskCard}
                        style={{ borderColor: getRiskColor(prediction.risk_category) }}
                    >
                        <div className={styles.riskHeader}>
                            <h3>Your Heart Disease Risk</h3>
                            <span
                                className={styles.riskBadge}
                                style={{ backgroundColor: getRiskColor(prediction.risk_category) }}
                            >
                                {getRiskLabel(prediction.risk_category)}
                            </span>
                        </div>
                        <div className={styles.riskPercentage}>
                            {prediction.risk_percentage}%
                        </div>
                        <p className={styles.periodInfo}>
                            Based on your coffee consumption over the last {prediction.period}
                        </p>
                    </div>

                    <div className={styles.statsSection}>
                        <h4>Caffeine Statistics</h4>
                        <div className={styles.statsGrid}>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Total Caffeine:</span>
                                <span className={styles.statValue}>
                                    {prediction.caffeine_stats.total_mg} mg
                                </span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Avg Daily Caffeine:</span>
                                <span className={styles.statValue}>
                                    {prediction.caffeine_stats.avg_daily_mg} mg/day
                                </span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Number of Coffees:</span>
                                <span className={styles.statValue}>
                                    {prediction.caffeine_stats.num_coffees}
                                </span>
                            </div>
                        </div>
                    </div>

                    {prediction.used_bp && (
                        <div className={styles.bpInfo}>
                            <h4>Blood Pressure Used:</h4>
                            <p>
                                {prediction.used_bp.systolic}/{prediction.used_bp.diastolic}
                                {prediction.used_bp.pulse && ` (Pulse: ${prediction.used_bp.pulse})`}
                            </p>
                        </div>
                    )}

                    {prediction.missing_fields && prediction.missing_fields.length > 0 && (
                        <div className={styles.warning}>
                            <h4>⚠️ Missing Information</h4>
                            <p>To improve prediction accuracy, please complete your health profile:</p>
                            <ul>
                                {prediction.missing_fields.map((field, idx) => (
                                    <li key={idx}>{field}</li>
                                ))}
                            </ul>
                            <a href="/settings" className={styles.settingsLink}>
                                Go to Settings to complete your profile
                            </a>
                        </div>
                    )}

                    <div className={styles.disclaimer}>
                        <p>
                            <strong>Disclaimer:</strong> This prediction is for informational purposes only
                            and is not a substitute for professional medical advice. Please consult with
                            your healthcare provider for accurate health assessments.
                        </p>
                        {prediction.note && (
                            <p className={styles.note}>{prediction.note}</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
