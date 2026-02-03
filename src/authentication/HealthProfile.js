import React, { useState, useEffect } from 'react';
import styles from './styles/HealthProfile.module.css';

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

export default function HealthProfile() {
    const [profile, setProfile] = useState({
        sex: '',
        date_of_birth: '',
        height_cm: '',
        weight_kg: '',
        has_family_history_chd: false,
        num_relatives_chd: 0,
        family_history_details: '',
        has_hypertension: false,
        has_diabetes: false,
        has_high_cholesterol: false,
        has_obesity: false,
        is_smoker: false,
        activity_level: '',
        other_health_issues: ''
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);
    const [bpEntries, setBpEntries] = useState([]);
    const [showBpForm, setShowBpForm] = useState(false);
    const [newBp, setNewBp] = useState({
        systolic: '',
        diastolic: '',
        pulse: ''
    });

    useEffect(() => {
        fetchHealthProfile();
        fetchBloodPressure();
    }, []);

    const fetchHealthProfile = async () => {
        try {
            const response = await fetch(`${API_URL}/health-profile/`, {
                method: 'GET',
                headers: authHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                // Format date for input field
                if (data.date_of_birth) {
                    data.date_of_birth = data.date_of_birth.split('T')[0];
                }
                setProfile(data);
            }
        } catch (err) {
            console.error('Error fetching health profile:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchBloodPressure = async () => {
        try {
            const response = await fetch(`${API_URL}/blood-pressure/list/`, {
                method: 'GET',
                headers: authHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                setBpEntries(data);
            }
        } catch (err) {
            console.error('Error fetching blood pressure:', err);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setProfile(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            setMessage(null);

            const response = await fetch(`${API_URL}/health-profile/`, {
                method: 'PUT',
                headers: authHeaders(),
                body: JSON.stringify(profile)
            });

            if (response.ok) {
                setMessage({ type: 'success', text: 'Health profile saved successfully!' });
            } else {
                const errorData = await response.json();
                setMessage({ type: 'error', text: errorData.error || 'Failed to save health profile' });
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Error saving health profile' });
            console.error('Error saving health profile:', err);
        } finally {
            setSaving(false);
        }
    };

    const handleAddBp = async () => {
        try {
            const response = await fetch(`${API_URL}/blood-pressure/`, {
                method: 'POST',
                headers: authHeaders(),
                body: JSON.stringify(newBp)
            });

            if (response.ok) {
                setMessage({ type: 'success', text: 'Blood pressure entry added!' });
                setNewBp({ systolic: '', diastolic: '', pulse: '' });
                setShowBpForm(false);
                fetchBloodPressure();
            } else {
                const errorData = await response.json();
                setMessage({ type: 'error', text: errorData.error || 'Failed to add blood pressure' });
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Error adding blood pressure' });
            console.error('Error adding blood pressure:', err);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return <div className={styles.loading}>Loading health profile...</div>;
    }

    return (
        <div className={styles.container}>
            <h2 className={styles.title}>Health Profile</h2>
            <p className={styles.description}>
                Complete your health profile to get more accurate heart disease risk predictions.
            </p>

            {message && (
                <div className={`${styles.message} ${styles[message.type]}`}>
                    {message.text}
                </div>
            )}

            <div className={styles.section}>
                <h3>Demographics</h3>
                <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                        <label>Sex</label>
                        <select name="sex" value={profile.sex} onChange={handleChange}>
                            <option value="">Select...</option>
                            <option value="M">Male</option>
                            <option value="F">Female</option>
                            <option value="O">Other</option>
                        </select>
                    </div>
                    <div className={styles.formGroup}>
                        <label>Date of Birth</label>
                        <input
                            type="date"
                            name="date_of_birth"
                            value={profile.date_of_birth}
                            onChange={handleChange}
                        />
                    </div>
                </div>
            </div>

            <div className={styles.section}>
                <h3>Physical Measurements</h3>
                <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                        <label>Height (cm)</label>
                        <input
                            type="number"
                            name="height_cm"
                            value={profile.height_cm}
                            onChange={handleChange}
                            min="50"
                            max="250"
                        />
                    </div>
                    <div className={styles.formGroup}>
                        <label>Weight (kg)</label>
                        <input
                            type="number"
                            name="weight_kg"
                            value={profile.weight_kg}
                            onChange={handleChange}
                            min="20"
                            max="300"
                        />
                    </div>
                </div>
                {profile.height_cm && profile.weight_kg && (
                    <div className={styles.bmiInfo}>
                        <strong>BMI:</strong> {((profile.weight_kg / ((profile.height_cm / 100) ** 2)).toFixed(1))}
                    </div>
                )}
            </div>

            <div className={styles.section}>
                <h3>Family History</h3>
                <div className={styles.formGroup}>
                    <label>
                        <input
                            type="checkbox"
                            name="has_family_history_chd"
                            checked={profile.has_family_history_chd}
                            onChange={handleChange}
                        />
                        Family history of coronary heart disease
                    </label>
                </div>
                {profile.has_family_history_chd && (
                    <>
                        <div className={styles.formGroup}>
                            <label>Number of relatives with CHD</label>
                            <input
                                type="number"
                                name="num_relatives_chd"
                                value={profile.num_relatives_chd}
                                onChange={handleChange}
                                min="0"
                                max="10"
                            />
                        </div>
                        <div className={styles.formGroup}>
                            <label>Details</label>
                            <textarea
                                name="family_history_details"
                                value={profile.family_history_details}
                                onChange={handleChange}
                                rows="3"
                                placeholder="e.g., Father had heart attack at age 55"
                            />
                        </div>
                    </>
                )}
            </div>

            <div className={styles.section}>
                <h3>Medical Conditions</h3>
                <div className={styles.checkboxGroup}>
                    <label>
                        <input
                            type="checkbox"
                            name="has_hypertension"
                            checked={profile.has_hypertension}
                            onChange={handleChange}
                        />
                        Hypertension (High Blood Pressure)
                    </label>
                    <label>
                        <input
                            type="checkbox"
                            name="has_diabetes"
                            checked={profile.has_diabetes}
                            onChange={handleChange}
                        />
                        Diabetes
                    </label>
                    <label>
                        <input
                            type="checkbox"
                            name="has_high_cholesterol"
                            checked={profile.has_high_cholesterol}
                            onChange={handleChange}
                        />
                        High Cholesterol
                    </label>
                    <label>
                        <input
                            type="checkbox"
                            name="has_obesity"
                            checked={profile.has_obesity}
                            onChange={handleChange}
                        />
                        Obesity
                    </label>
                </div>
            </div>

            <div className={styles.section}>
                <h3>Lifestyle</h3>
                <div className={styles.formGroup}>
                    <label>
                        <input
                            type="checkbox"
                            name="is_smoker"
                            checked={profile.is_smoker}
                            onChange={handleChange}
                        />
                        Smoker
                    </label>
                </div>
                <div className={styles.formGroup}>
                    <label>Activity Level</label>
                    <select name="activity_level" value={profile.activity_level} onChange={handleChange}>
                        <option value="">Select...</option>
                        <option value="sedentary">Sedentary</option>
                        <option value="light">Light</option>
                        <option value="moderate">Moderate</option>
                        <option value="active">Active</option>
                        <option value="very_active">Very Active</option>
                    </select>
                </div>
            </div>

            <div className={styles.section}>
                <h3>Other Health Issues</h3>
                <div className={styles.formGroup}>
                    <textarea
                        name="other_health_issues"
                        value={profile.other_health_issues}
                        onChange={handleChange}
                        rows="4"
                        placeholder="List any other relevant health conditions or concerns"
                    />
                </div>
            </div>

            <div className={styles.section}>
                <h3>Blood Pressure Log</h3>
                <button
                    className={styles.addBpButton}
                    onClick={() => setShowBpForm(!showBpForm)}
                >
                    {showBpForm ? 'Cancel' : '+ Add Blood Pressure Reading'}
                </button>

                {showBpForm && (
                    <div className={styles.bpForm}>
                        <div className={styles.formGrid}>
                            <div className={styles.formGroup}>
                                <label>Systolic (Big Number)</label>
                                <input
                                    type="number"
                                    value={newBp.systolic}
                                    onChange={(e) => setNewBp({ ...newBp, systolic: e.target.value })}
                                    min="70"
                                    max="250"
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label>Diastolic (Small Number)</label>
                                <input
                                    type="number"
                                    value={newBp.diastolic}
                                    onChange={(e) => setNewBp({ ...newBp, diastolic: e.target.value })}
                                    min="40"
                                    max="150"
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label>Pulse (Optional)</label>
                                <input
                                    type="number"
                                    value={newBp.pulse}
                                    onChange={(e) => setNewBp({ ...newBp, pulse: e.target.value })}
                                    min="30"
                                    max="200"
                                />
                            </div>
                        </div>
                        <button className={styles.saveBpButton} onClick={handleAddBp}>
                            Save Reading
                        </button>
                    </div>
                )}

                {bpEntries.length > 0 && (
                    <div className={styles.bpList}>
                        <h4>Recent Readings</h4>
                        {bpEntries.slice(0, 5).map((entry) => (
                            <div key={entry.id} className={styles.bpEntry}>
                                <span className={styles.bpValue}>
                                    {entry.systolic}/{entry.diastolic}
                                    {entry.pulse && ` (Pulse: ${entry.pulse})`}
                                </span>
                                <span className={styles.bpDate}>{formatDate(entry.measured_at)}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <button
                className={styles.saveButton}
                onClick={handleSave}
                disabled={saving}
            >
                {saving ? 'Saving...' : 'Save Health Profile'}
            </button>
        </div>
    );
}
