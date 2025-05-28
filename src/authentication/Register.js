// src/authentication/Register.js
import styles from './styles/Register.module.css'
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

export default function Register() {
    const history = useHistory();
    const [username, setUsername] = useState('');
    const [email, setEmail]       = useState('');
    const [password, setPassword] = useState('');
    const [error, setError]       = useState(null);

    const handleSubmit = async e => {
        e.preventDefault();
        setError(null);

        try {
            const resp = await fetch('http://127.0.0.1:8000/api/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password }),
            });
            if (!resp.ok) {
                const json = await resp.json();
                const msg  = json.username || json.email || JSON.stringify(json);
                throw new Error(msg);
            }
            const body = await resp.json();
            localStorage.setItem('token', body.token);
            localStorage.setItem('user_id', String(body.user_id));
            history.push('/login');
        } catch (err) {
            setError('Registration failed: ' + err.message);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '100px auto', fontFamily: 'Georgia'  }}>
            <h2>Register</h2>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Username</label><br/>
                    <input value={username}
                           onChange={e => setUsername(e.target.value)}
                           required />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Email</label><br/>
                    <input type="email"
                           value={email}
                           onChange={e => setEmail(e.target.value)}
                           required />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Password</label><br/>
                    <input type="password"
                           value={password}
                           onChange={e => setPassword(e.target.value)}
                           required />
                </div>
                <button type="submit" className={styles.registerButton}>Register</button>
            </form>
        </div>
    );
}
