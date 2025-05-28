import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';
import styles from './styles/Login.module.css';

function TwoFactorSettings() {
    const { user, authenticatedFetch } = useCoffee();
    const [is2FAEnabled, setIs2FAEnabled] = useState(false);
    const [showSetup, setShowSetup] = useState(false);
    const [showEmailInput, setShowEmailInput] = useState(false);
    const [showQRCode, setShowQRCode] = useState(false);
    const [qrCode, setQrCode] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    const [email, setEmail] = useState('');
    const [error, setError] = useState(null);

    useEffect(() => {
        if (user) {
            setIs2FAEnabled(user.twofa);
        }
    }, [user]);

    const handleEnable2FA = () => {
        setShowSetup(true);
        setShowEmailInput(true);
        setError(null);
    };

    const handleEmailSubmit = async () => {
        if (!email) {
            alert('Please enter an email address');
            return;
        }

        try {
            const response = await authenticatedFetch('http://127.0.0.1:8000/api/users/setup-2fa/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Failed to setup 2FA');
            }

            const data = await response.json();
            setQrCode(data.qr_code);
            setShowEmailInput(false);
            setShowQRCode(true);
        } catch (err) {
            alert(err.message || 'Failed to setup 2FA');
            setError(err.message || 'Failed to setup 2FA');
        }
    };

    const handleVerify2FA = async () => {
        if (!verificationCode) {
            alert('Please enter the 6-digit code');
            return;
        }

        try {
            const response = await authenticatedFetch('http://127.0.0.1:8000/api/users/verify-2fa-setup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code: verificationCode })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Invalid verification code');
            }

            // Successfully enabled 2FA
            setIs2FAEnabled(true);
            setShowSetup(false);
            setShowQRCode(false);
            setVerificationCode('');
            setEmail('');
            setError(null);
            
            // Update user object
            if (user) {
                user.twofa = true;
            }
        } catch (err) {
            // Show popup error and clear input as required
            alert(err.message || 'Invalid verification code');
            setError(err.message || 'Invalid verification code');
            setVerificationCode(''); // Clear the input as required
        }
    };

    const handleDisable2FA = async () => {
        try {
            const response = await authenticatedFetch('http://127.0.0.1:8000/api/users/disable-2fa/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Failed to disable 2FA');
            }

            setIs2FAEnabled(false);
            setError(null);
            
            // Update user object
            if (user) {
                user.twofa = false;
            }
        } catch (err) {
            alert(err.message || 'Failed to disable 2FA');
            setError(err.message || 'Failed to disable 2FA');
        }
    };

    const handleCancel = () => {
        setShowSetup(false);
        setShowEmailInput(false);
        setShowQRCode(false);
        setVerificationCode('');
        setEmail('');
        setError(null);
    };

    return (
        <div style={{ maxWidth: '400px', margin: '20px auto', fontFamily: 'Georgia' }}>
            <h2>Two-Factor Authentication</h2>
            {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}

            {!is2FAEnabled ? (
                !showSetup ? (
                    <div>
                        <p>Two-factor authentication is not enabled.</p>
                        <button
                            className={styles.loginButton}
                            onClick={handleEnable2FA}
                        >
                            Enable 2FA
                        </button>
                    </div>
                ) : showEmailInput ? (
                    <div>
                        <p>Enter your email address to set up 2FA:</p>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            required
                            style={{ marginBottom: '10px', width: '100%' }}
                        />
                        <br/>
                        <button
                            className={styles.loginButton}
                            onClick={handleEmailSubmit}
                        >
                            Continue
                        </button>
                        <button
                            className={styles.loginButton}
                            onClick={handleCancel}
                            style={{ marginLeft: '10px' }}
                        >
                            Cancel
                        </button>
                    </div>
                ) : showQRCode ? (
                    <div>
                        <p>Scan this QR code with your authenticator app:</p>
                        {qrCode && (
                            <img
                                src={`data:image/png;base64,${qrCode}`}
                                alt="QR Code"
                                style={{ marginBottom: '20px', display: 'block' }}
                            />
                        )}
                        <p>Enter the 6-digit code from your authenticator app:</p>
                        <input
                            type="text"
                            value={verificationCode}
                            onChange={(e) => setVerificationCode(e.target.value)}
                            placeholder="Enter 6-digit code"
                            maxLength={6}
                            pattern="[0-9]{6}"
                            required
                            style={{ marginBottom: '10px' }}
                        />
                        <br/>
                        <button
                            className={styles.loginButton}
                            onClick={handleVerify2FA}
                        >
                            Verify
                        </button>
                        <button
                            className={styles.loginButton}
                            onClick={handleCancel}
                            style={{ marginLeft: '10px' }}
                        >
                            Cancel
                        </button>
                    </div>
                ) : null
            ) : (
                <div>
                    <p>Two-factor authentication is enabled.</p>
                    <button
                        className={styles.loginButton}
                        onClick={handleDisable2FA}
                    >
                        Disable 2FA
                    </button>
                </div>
            )}
        </div>
    );
}

export default TwoFactorSettings; 