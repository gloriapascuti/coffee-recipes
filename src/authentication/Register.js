// src/authentication/Register.js
import styles from './styles/Register.module.css'
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

export default function Register() {
    const history = useHistory();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [address, setAddress] = useState('');
    const [error, setError] = useState(null);

    const handleSubmit = async e => {
        e.preventDefault();
        setError(null);

        if (password !== password2) {
            setError('Passwords do not match');
            return;
        }

        try {
            const resp = await fetch('http://127.0.0.1:8000/api/users/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    username, 
                    email, 
                    password,
                    password2,
                    phone_number: phoneNumber,
                    address
                }),
            });
            
            if (!resp.ok) {
                const json = await resp.json();
                const msg = json.username || json.email || json.password || JSON.stringify(json);
                throw new Error(msg);
            }
            
            const body = await resp.json();
            // Store the JWT tokens and user data
            localStorage.setItem('access_token', body.access);
            localStorage.setItem('refresh_token', body.refresh);
            localStorage.setItem('user_id', String(body.user_id));
            localStorage.setItem('username', body.username);
            localStorage.setItem('user_2fa', body.twofa);
            
            // Redirect to app since user is now logged in
            history.push('/app');
        } catch (err) {
            setError('Registration failed: ' + err.message);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '100px auto', fontFamily: 'Georgia' }}>
            <h2>Register</h2>
            {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Username</label><br/>
                    <input 
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        required 
                    />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Email</label><br/>
                    <input 
                        type="email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        required 
                    />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>First Name</label><br/>
                    <input 
                        value={firstName}
                        onChange={e => setFirstName(e.target.value)}
                        required 
                    />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Last Name</label><br/>
                    <input 
                        value={lastName}
                        onChange={e => setLastName(e.target.value)}
                        required 
                    />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Password</label><br/>
                    <input 
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        required 
                    />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Confirm Password</label><br/>
                    <input 
                        type="password"
                        value={password2}
                        onChange={e => setPassword2(e.target.value)}
                        required 
                    />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Phone Number (optional)</label><br/>
                    <input 
                        type="tel"
                        value={phoneNumber}
                        onChange={e => setPhoneNumber(e.target.value)}
                    />
                </div>
                <div style={{ marginTop: '10px' }}>
                    <label>Address (optional)</label><br/>
                    <textarea 
                        value={address}
                        onChange={e => setAddress(e.target.value)}
                        rows={3}
                        style={{ width: '100%', resize: 'vertical' }}
                    />
                </div>
                <button type="submit" className={styles.registerButton} style={{ marginTop: '15px' }}>
                    Register
                </button>
            </form>
        </div>
    );
}
