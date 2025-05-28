// src/authentication/Login.js
import styles from './styles/Login.module.css'
import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';
import { useHistory } from 'react-router-dom';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError]       = useState(null);
    const { loginUser, user } = useCoffee();
    const history = useHistory();

    useEffect(() => {
        if (user) {
            history.push('/app');
        }
    }, [user, history]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            await loginUser(username, password);
            console.log('Login successful!');
        } catch (err) {
            setError(err.message);
        }
    };

    if (user) {
        return null;
    }

    return (
        <div style={{ maxWidth: '400px', margin: '100px auto', fontFamily: 'Georgia'}}>
            <h2>Login</h2>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="username">Username:</label><br/>
                    <input type="text"
                           id="username"
                           value={username}
                           onChange={(e) => setUsername(e.target.value)}
                           required />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label htmlFor="password">Password:</label><br/>
                    <input type="password"
                           id="password"
                           value={password}
                           onChange={(e) => setPassword(e.target.value)}
                           required />
                </div>
                <button type="submit" className={styles.loginButton}>Login</button>
            </form>
        </div>
    );
}

export default Login;
