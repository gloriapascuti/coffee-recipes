// src/authentication/Login.js
import styles from './styles/Login.module.css'
import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';
import { useHistory } from 'react-router-dom';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const { loginUser, verify2FALogin, user } = useCoffee();
    const history = useHistory();

    // State for 2FA flow
    const [show2FAInput, setShow2FAInput] = useState(false);
    const [twoFactorCode, setTwoFactorCode] = useState('');
    const [userEmail, setUserEmail] = useState('');

    useEffect(() => {
        if (user) {
            history.push('/app');
        }
    }, [user, history]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const response = await loginUser(username, password);
            
            if (response.require_2fa) {
                setShow2FAInput(true);
                setUserEmail(response.email);
            } else {
                // User logged in successfully without 2FA
                history.push('/app');
            }
        } catch (err) {
            // Show popup error
            alert(err.message || 'Invalid credentials');
            setError(err.message || 'Invalid credentials');
            setShow2FAInput(false);
            setTwoFactorCode('');
        }
    };

    const handle2FASubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            await verify2FALogin(userEmail, twoFactorCode);
            // User logged in successfully with 2FA
            history.push('/app');
        } catch (err) {
            // Show popup error and clear input
            alert(err.message || 'Invalid 2FA code');
            setError(err.message || 'Invalid 2FA code');
            setTwoFactorCode(''); // Clear the input as required
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '100px auto', fontFamily: 'Georgia' }}>
            <h2>Login</h2>
            {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}

            {!show2FAInput ? (
                <form onSubmit={handleLogin}>
                    <div>
                        <label htmlFor="username">Username:</label><br/>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div style={{ marginTop: '10px' }}>
                        <label htmlFor="password">Password:</label><br/>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className={styles.loginButton}>Login</button>
                </form>
            ) : (
                <div>
                    <p>Please enter the 6-digit code from your authenticator app:</p>
                    <form onSubmit={handle2FASubmit}>
                        <input
                            type="text"
                            value={twoFactorCode}
                            onChange={(e) => setTwoFactorCode(e.target.value)}
                            placeholder="Enter 6-digit code"
                            maxLength={6}
                            pattern="[0-9]{6}"
                            required
                            style={{ marginBottom: '10px' }}
                        />
                        <br/>
                        <button type="submit" className={styles.loginButton}>Verify</button>
                        <button
                            type="button"
                            onClick={() => {
                                setShow2FAInput(false);
                                setTwoFactorCode('');
                                setError(null);
                                setUserEmail('');
                            }}
                            className={styles.loginButton}
                            style={{ marginLeft: '10px' }}
                        >
                            Back
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}

export default Login;
