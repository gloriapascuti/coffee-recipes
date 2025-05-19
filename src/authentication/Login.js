// src/authentication/Login.js
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

export default function Login() {
    const history = useHistory();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError]       = useState(null);

    const handleSubmit = async e => {
        e.preventDefault();
        setError(null);

        try {
            const resp = await fetch('http://127.0.0.1:8000/api/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            if (resp.status === 301) {
                // Follow redirect if backend misconfigured
                const redirectedResp = await fetch('http://127.0.0.1:8000/api/login/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                });
                if (!redirectedResp.ok) {
                    const text = await redirectedResp.text();
                    throw new Error(text || redirectedResp.status);
                }
                const body = await redirectedResp.json();
                localStorage.setItem('token', body.token);
                localStorage.setItem('user_id', String(body.user_id));
                history.push('/app');
                return;
            }
            if (!resp.ok) {
                let msg = 'Login failed.';
                try {
                    const data = await resp.json();
                    if (data && data.non_field_errors) {
                        msg = data.non_field_errors.join(' ');
                    } else if (data && data.detail) {
                        msg = data.detail;
                    } else if (resp.status === 400) {
                        msg = 'Invalid username or password.';
                    } else if (resp.status === 500) {
                        msg = 'Server error. Please try again later.';
                    }
                } catch (e) {
                    if (resp.status === 400) {
                        msg = 'Invalid username or password.';
                    } else if (resp.status === 500) {
                        msg = 'Server error. Please try again later.';
                    }
                }
                throw new Error(msg);
            }
            const body = await resp.json();
            localStorage.setItem('token', body.token);
            localStorage.setItem('user_id', String(body.user_id));
            history.push('/app');
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '100px auto' }}>
            <h2>Login</h2>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Username</label><br/>
                    <input value={username}
                           onChange={e => setUsername(e.target.value)}
                           required />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Password</label><br/>
                    <input type="password"
                           value={password}
                           onChange={e => setPassword(e.target.value)}
                           required />
                </div>
                <button type="submit" style={{ marginTop: '20px' }}>Login</button>
            </form>
        </div>
    );
}
