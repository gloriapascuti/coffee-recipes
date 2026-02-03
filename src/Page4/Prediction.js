import React, { useState } from 'react';
import { useCoffee } from '../CoffeeContext';
import PredictionCharts from './PredictionCharts';
import styles from './styles/Prediction.module.css';

const API_URL = 'http://127.0.0.1:8000/api';

export default function Prediction({ consumedCoffees }) {
    const { authenticatedFetch } = useCoffee();
    const [period, setPeriod] = useState('week');
    const [systolic, setSystolic] = useState('');
    const [diastolic, setDiastolic] = useState('');
    const [pulse, setPulse] = useState('');
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showAnalysis, setShowAnalysis] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [validationErrors, setValidationErrors] = useState({});
    const [lastPrediction, setLastPrediction] = useState(null);

    const validateInputs = () => {
        const errors = {};
        
        // Validate blood pressure if provided
        if (systolic || diastolic) {
            if (!systolic) {
                errors.systolic = 'Systolic is required when diastolic is provided';
            } else {
                const sys = parseInt(systolic);
                if (isNaN(sys) || sys < 70 || sys > 250) {
                    errors.systolic = 'Systolic must be between 70 and 250';
                }
            }
            
            if (!diastolic) {
                errors.diastolic = 'Diastolic is required when systolic is provided';
            } else {
                const dia = parseInt(diastolic);
                if (isNaN(dia) || dia < 40 || dia > 150) {
                    errors.diastolic = 'Diastolic must be between 40 and 150';
                }
            }
            
            // Validate that systolic > diastolic
            if (systolic && diastolic) {
                const sys = parseInt(systolic);
                const dia = parseInt(diastolic);
                if (!isNaN(sys) && !isNaN(dia) && sys <= dia) {
                    errors.systolic = 'Systolic must be greater than diastolic';
                }
            }
            
            if (pulse) {
                const pulseVal = parseInt(pulse);
                if (isNaN(pulseVal) || pulseVal < 30 || pulseVal > 200) {
                    errors.pulse = 'Pulse must be between 30 and 200';
                }
            }
        }
        
        setValidationErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleGeneratePrediction = async () => {
        // Validate inputs first
        if (!validateInputs()) {
            setError('Please fix the validation errors before generating a prediction.');
            return;
        }

        try {
            setLoading(true);
            setError(null);
            setValidationErrors({});

            const requestBody = { period };
            if (systolic && diastolic) {
                requestBody.systolic = parseInt(systolic);
                requestBody.diastolic = parseInt(diastolic);
                if (pulse) {
                    requestBody.pulse = parseInt(pulse);
                }
            }

            const response = await authenticatedFetch(`${API_URL}/prediction/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                // Check if response is JSON or HTML
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || errorData.detail || `Failed to generate prediction (${response.status})`);
                } else {
                    // Response is HTML (likely an error page)
                    const text = await response.text();
                    throw new Error(`Server error (${response.status}). Please check if the backend is running correctly.`);
                }
            }

            const data = await response.json();
            setLastPrediction(prediction); // Store previous prediction for comparison
            setPrediction(data);
        } catch (err) {
            // Handle JSON parsing errors more gracefully
            if (err.message.includes('JSON') || err.message.includes('<!DOCTYPE')) {
                setError('Server returned an error. Please check if the backend is running and try again.');
            } else {
                setError(err.message);
            }
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

    const generateMedicalAnalysis = () => {
        if (!prediction) return;

        const analysisText = [];
        
        // Risk Overview
        analysisText.push(`## Risk Assessment Summary`);
        analysisText.push(`\nYour heart disease risk is **${prediction.risk_percentage}%** over the ${prediction.period} period, which is classified as **${getRiskLabel(prediction.risk_category)}**.`);
        
        // Caffeine Analysis
        const avgDaily = prediction.caffeine_stats.avg_daily_mg;
        const totalCaffeine = prediction.caffeine_stats.total_mg;
        const numCoffees = prediction.caffeine_stats.num_coffees;
        
        analysisText.push(`\n## Caffeine Consumption Analysis`);
        analysisText.push(`\nOver the past ${prediction.period}, you consumed **${numCoffees} coffees**, totaling **${totalCaffeine.toFixed(0)}mg** of caffeine.`);
        analysisText.push(`Your average daily caffeine intake is **${avgDaily.toFixed(0)}mg per day**.`);
        
        if (avgDaily > 400) {
            analysisText.push(`\n⚠️ **Warning**: Your average daily caffeine intake (${avgDaily.toFixed(0)}mg) exceeds the FDA-recommended safe limit of 400mg per day. High caffeine consumption can contribute to increased heart rate, elevated blood pressure, and may increase cardiovascular risk over time.`);
        } else if (avgDaily > 300) {
            analysisText.push(`\n⚠️ **Caution**: Your average daily caffeine intake (${avgDaily.toFixed(0)}mg) is approaching the recommended limit of 400mg per day. Consider monitoring your consumption to stay within safe limits.`);
        } else {
            analysisText.push(`\n✓ Your average daily caffeine intake is within the generally accepted safe range (under 400mg per day).`);
        }
        
        // Blood Pressure Analysis
        if (prediction.used_bp) {
            const bp = prediction.used_bp;
            analysisText.push(`\n## Blood Pressure Assessment`);
            analysisText.push(`\nYour current blood pressure reading is **${bp.systolic}/${bp.diastolic}${bp.pulse ? ` (Pulse: ${bp.pulse})` : ''}**.`);
            
            if (bp.systolic >= 140 || bp.diastolic >= 90) {
                analysisText.push(`\n⚠️ **High Blood Pressure**: Your readings indicate Stage 2 Hypertension. This is a significant risk factor for heart disease and requires medical attention. Combined with caffeine intake, this increases your cardiovascular risk.`);
            } else if (bp.systolic >= 130 || bp.diastolic >= 85) {
                analysisText.push(`\n⚠️ **Elevated Blood Pressure**: Your readings are above normal (ideal is below 120/80). This, combined with caffeine consumption, may contribute to increased cardiovascular risk.`);
            } else {
                analysisText.push(`\n✓ Your blood pressure is within a normal range. However, caffeine can temporarily increase blood pressure, so it's important to monitor regularly.`);
            }
        }
        
        // Risk Factors Breakdown
        if (prediction.risk_factors && Object.keys(prediction.risk_factors).length > 0) {
            analysisText.push(`\n## Risk Factors Contribution`);
            analysisText.push(`\nThe following factors contribute to your heart disease risk:`);
            
            const sortedFactors = Object.entries(prediction.risk_factors)
                .sort((a, b) => b[1] - a[1]);
            
            sortedFactors.forEach(([factor, percentage]) => {
                analysisText.push(`\n- **${factor}**: ${percentage}% of your risk profile`);
            });
        }
        
        // Recommendations
        analysisText.push(`\n## Recommendations`);
        
        if (avgDaily > 400) {
            analysisText.push(`\n- **Reduce Caffeine Intake**: Aim to reduce your daily caffeine consumption to below 400mg. Consider switching some coffees to decaffeinated options or smaller servings.`);
        }
        
        if (prediction.used_bp && (prediction.used_bp.systolic >= 130 || prediction.used_bp.diastolic >= 85)) {
            analysisText.push(`\n- **Blood Pressure Management**: Your blood pressure readings suggest you should consult with a healthcare provider. Lifestyle modifications including reducing caffeine, regular exercise, and dietary changes may help.`);
        }
        
        if (prediction.missing_fields && prediction.missing_fields.length > 0) {
            analysisText.push(`\n- **Complete Health Profile**: To improve prediction accuracy, please complete your health profile with: ${prediction.missing_fields.join(', ')}.`);
        }
        
        analysisText.push(`\n- **Regular Monitoring**: Continue tracking your coffee consumption and blood pressure regularly to monitor trends over time.`);
        analysisText.push(`\n- **Medical Consultation**: This analysis is for informational purposes only. Please consult with a healthcare provider for personalized medical advice and risk assessment.`);
        
        // Period-specific insights
        if (period === 'week') {
            analysisText.push(`\n## Weekly Pattern Insights`);
            analysisText.push(`\nThis analysis is based on your consumption over the past week. Short-term patterns can fluctuate, so consider generating monthly or yearly predictions for a more comprehensive view of your long-term risk.`);
        } else if (period === 'month') {
            analysisText.push(`\n## Monthly Pattern Insights`);
            analysisText.push(`\nThis analysis reflects your consumption patterns over the past month, providing a more stable view of your habits and their impact on cardiovascular health.`);
        } else {
            analysisText.push(`\n## Yearly Pattern Insights`);
            analysisText.push(`\nThis analysis covers a full year of data, offering the most comprehensive view of your long-term caffeine consumption patterns and their cumulative impact on heart disease risk.`);
        }
        
        return analysisText.join('\n');
    };

    const handleShowAnalysis = () => {
        if (!showAnalysis) {
            const analysisText = generateMedicalAnalysis();
            setAnalysis(analysisText);
        }
        setShowAnalysis(!showAnalysis);
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
                            <label>
                                Systolic (Big Number):
                                <span className={styles.tooltip} title="The top number in a blood pressure reading, measuring pressure when the heart beats"> ℹ️</span>
                            </label>
                            <input
                                type="number"
                                value={systolic}
                                onChange={(e) => {
                                    setSystolic(e.target.value);
                                    if (validationErrors.systolic) {
                                        const newErrors = {...validationErrors};
                                        delete newErrors.systolic;
                                        setValidationErrors(newErrors);
                                    }
                                }}
                                placeholder="e.g., 120"
                                min="70"
                                max="250"
                                className={validationErrors.systolic ? styles.inputError : ''}
                            />
                            {validationErrors.systolic && (
                                <span className={styles.errorText}>{validationErrors.systolic}</span>
                            )}
                        </div>
                        <div className={styles.inputGroup}>
                            <label>
                                Diastolic (Small Number):
                                <span className={styles.tooltip} title="The bottom number in a blood pressure reading, measuring pressure when the heart rests"> ℹ️</span>
                            </label>
                            <input
                                type="number"
                                value={diastolic}
                                onChange={(e) => {
                                    setDiastolic(e.target.value);
                                    if (validationErrors.diastolic) {
                                        const newErrors = {...validationErrors};
                                        delete newErrors.diastolic;
                                        setValidationErrors(newErrors);
                                    }
                                }}
                                placeholder="e.g., 80"
                                min="40"
                                max="150"
                                className={validationErrors.diastolic ? styles.inputError : ''}
                            />
                            {validationErrors.diastolic && (
                                <span className={styles.errorText}>{validationErrors.diastolic}</span>
                            )}
                        </div>
                        <div className={styles.inputGroup}>
                            <label>
                                Pulse (Optional):
                                <span className={styles.tooltip} title="Your heart rate in beats per minute"> ℹ️</span>
                            </label>
                            <input
                                type="number"
                                value={pulse}
                                onChange={(e) => {
                                    setPulse(e.target.value);
                                    if (validationErrors.pulse) {
                                        const newErrors = {...validationErrors};
                                        delete newErrors.pulse;
                                        setValidationErrors(newErrors);
                                    }
                                }}
                                placeholder="e.g., 72"
                                min="30"
                                max="200"
                                className={validationErrors.pulse ? styles.inputError : ''}
                            />
                            {validationErrors.pulse && (
                                <span className={styles.errorText}>{validationErrors.pulse}</span>
                            )}
                        </div>
                    </div>
                </div>

                <button
                    className={styles.generateButton}
                    onClick={handleGeneratePrediction}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <span className={styles.spinner}></span>
                            Generating Prediction...
                        </>
                    ) : (
                        'Generate Prediction'
                    )}
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
                            {lastPrediction && (
                                <span className={styles.trendIndicator}>
                                    {prediction.risk_percentage > lastPrediction.risk_percentage ? (
                                        <span className={styles.trendUp} title="Risk increased"> ↗️</span>
                                    ) : prediction.risk_percentage < lastPrediction.risk_percentage ? (
                                        <span className={styles.trendDown} title="Risk decreased"> ↘️</span>
                                    ) : (
                                        <span className={styles.trendSame} title="Risk unchanged"> →</span>
                                    )}
                                </span>
                            )}
                        </div>
                        <p className={styles.periodInfo}>
                            Based on your coffee consumption over the last {prediction.period}
                        </p>
                        {lastPrediction && (
                            <p className={styles.comparisonInfo}>
                                Previous: {lastPrediction.risk_percentage}% ({lastPrediction.period})
                            </p>
                        )}
                    </div>

                    {/* AI Medical Analysis Button */}
                    <div className={styles.analysisSection}>
                        <button
                            className={styles.analysisButton}
                            onClick={handleShowAnalysis}
                        >
                            {showAnalysis ? '▼ Hide' : '▶ Show'} AI Medical Analysis
                        </button>
                        
                        {showAnalysis && analysis && (
                            <div className={styles.analysisContent}>
                                <div className={styles.analysisText}>
                                    {analysis.split('\n').map((line, index) => {
                                        if (line.startsWith('## ')) {
                                            return <h4 key={index} className={styles.analysisHeading}>{line.replace('## ', '')}</h4>;
                                        } else if (line.startsWith('**') && line.endsWith('**')) {
                                            return <strong key={index} className={styles.analysisBold}>{line.replace(/\*\*/g, '')}</strong>;
                                        } else if (line.startsWith('- **')) {
                                            const parts = line.match(/\*\*(.*?)\*\*: (.*)/);
                                            return (
                                                <div key={index} className={styles.analysisListItem}>
                                                    <strong>{parts[1]}:</strong> {parts[2]}
                                                </div>
                                            );
                                        } else if (line.trim() === '') {
                                            return <br key={index} />;
                                        } else {
                                            // Handle inline bold text
                                            const parts = line.split(/(\*\*.*?\*\*)/g);
                                            return (
                                                <p key={index} className={styles.analysisParagraph}>
                                                    {parts.map((part, pIndex) => {
                                                        if (part.startsWith('**') && part.endsWith('**')) {
                                                            return <strong key={pIndex}>{part.replace(/\*\*/g, '')}</strong>;
                                                        }
                                                        return <span key={pIndex}>{part}</span>;
                                                    })}
                                                </p>
                                            );
                                        }
                                    })}
                                </div>
                            </div>
                        )}
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

            {/* Prediction Charts */}
            {prediction && (
                <PredictionCharts 
                    prediction={prediction} 
                    period={period}
                    consumedCoffees={consumedCoffees}
                />
            )}
        </div>
    );
}
