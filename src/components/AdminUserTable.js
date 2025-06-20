// // src/components/AdminUserTable.js
// import React, { useEffect, useState } from 'react';
// import axios from 'axios';
//
// export default function AdminUserTable() {
//     const [users, setUsers] = useState([]);
//     const userId = localStorage.getItem('user_id');
//
//     // always invoke your hook in the same place
//     useEffect(() => {
//         if (userId === '1') {
//             const token = localStorage.getItem('token');
//             axios
//                 .get('http://127.0.0.1:8000/api/users/', {
//                     headers: { Authorization: `Token ${token}` }
//                 })
//                 .then(res => setUsers(res.data))
//                 .catch(console.error);
//         }
//     }, [userId]);
//
//     // only render the table for admin (id === "1")
//     if (userId !== '1') {
//         return null;
//     }
//
//     return (
//         <div style={{ margin: '2rem' }}>
//             <h2>All Registered Users</h2>
//             <table border="1" cellPadding="8">
//                 <thead>
//                 <tr>
//                     <th>ID</th>
//                     <th>Username</th>
//                     <th>Email</th>
//                     <th>Last Login</th>
//                     <th>Date Joined</th>
//                 </tr>
//                 </thead>
//                 <tbody>
//                 {users.map(u => (
//                     <tr key={u.id}>
//                         <td>{u.id}</td>
//                         <td>{u.username}</td>
//                         <td>{u.email}</td>
//                         <td>{u.last_login}</td>
//                         <td>{u.date_joined}</td>
//                     </tr>
//                 ))}
//                 </tbody>
//             </table>
//         </div>
//     );
// }


// src/components/AdminUserTable.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useCoffee } from '../CoffeeContext';

export default function AdminUserTable() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [actionLoading, setActionLoading] = useState({});
    const { user, accessToken } = useCoffee();

    // Debug logging
    console.log('AdminUserTable - Current user:', user);
    console.log('AdminUserTable - Is special admin:', user?.is_special_admin);

    const fetchUsers = () => {
        if (user && user.is_special_admin) {
            setLoading(true);
            setError(null);
            console.log('AdminUserTable - Making API request to admin/users/ endpoint');
            
            axios
                .get('http://127.0.0.1:8000/api/users/admin/users/', {
                    headers: { Authorization: `Bearer ${accessToken}` }
                })
                .then(res => {
                    console.log('AdminUserTable - API response:', res.data);
                    setUsers(res.data.results || res.data);
                    setLoading(false);
                })
                .catch(error => {
                    console.error('Error fetching users:', error);
                    setError(error.response?.data?.error || 'Failed to fetch users');
                    setLoading(false);
                });
        }
    };

    useEffect(() => {
        fetchUsers();
    }, [user, accessToken]);

    const handleVerifyUser = async (userId) => {
        setActionLoading(prev => ({ ...prev, [`verify_${userId}`]: true }));
        
        try {
            await axios.post(
                `http://127.0.0.1:8000/api/users/admin/verify-user/${userId}/`,
                {},
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );
            
            // Refresh the users list
            fetchUsers();
            alert('User activity verified successfully!');
        } catch (error) {
            console.error('Error verifying user:', error);
            alert(error.response?.data?.error || 'Failed to verify user');
        } finally {
            setActionLoading(prev => ({ ...prev, [`verify_${userId}`]: false }));
        }
    };

    const handleBanUser = async (userId) => {
        if (!window.confirm('Are you sure you want to ban this user? This action cannot be undone.')) {
            return;
        }

        setActionLoading(prev => ({ ...prev, [`ban_${userId}`]: true }));
        
        try {
            await axios.post(
                `http://127.0.0.1:8000/api/users/admin/ban-user/${userId}/`,
                {},
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );
            
            // Refresh the users list
            fetchUsers();
            alert('User has been banned successfully!');
        } catch (error) {
            console.error('Error banning user:', error);
            alert(error.response?.data?.error || 'Failed to ban user');
        } finally {
            setActionLoading(prev => ({ ...prev, [`ban_${userId}`]: false }));
        }
    };

    // Only render for special admin users
    if (!user || !user.is_special_admin) {
        return null;
    }

    if (loading) {
        return (
            <div style={{ margin: '2rem' }}>
                <h2>Admin User Management</h2>
                <p>Loading users...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ margin: '2rem' }}>
                <h2>Admin User Management</h2>
                <p style={{ color: 'red' }}>Error: {error}</p>
            </div>
        );
    }

    return (
        <div style={{ margin: '2rem' }}>
            <h2>Admin User Management</h2>
            <p style={{ color: '#666', marginBottom: '1rem' }}>
                Special Admin Access - MacBook Owner: {user.first_name} {user.last_name}
            </p>
            
            <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse', width: '100%' }}>
                <thead style={{ backgroundColor: '#f5f5f5' }}>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Name</th>
                    <th>Status</th>
                    <th>2FA</th>
                    <th>Operations</th>
                    <th>Suspicious Activity</th>
                    <th>Actions</th>
                    <th>Last Login</th>
                    <th>Date Joined</th>
                </tr>
                </thead>
                <tbody>
                {users.map(u => (
                    <tr key={u.id} style={{ 
                        backgroundColor: u.is_banned ? '#ffcccb' : (u.is_suspicious ? '#ffebee' : (u.is_special_admin ? '#e8f5e8' : 'white')),
                        borderBottom: '1px solid #ddd',
                        color: u.is_banned ? '#8b0000' : (u.is_suspicious ? '#d32f2f' : 'inherit')
                    }}>
                        <td>{u.id}</td>
                        <td style={{ fontWeight: u.is_superuser ? 'bold' : 'normal' }}>
                            {u.username}
                            {u.is_superuser && <span style={{ color: '#007bff', fontSize: '0.8em' }}> (Super)</span>}
                        </td>
                        <td>{u.email}</td>
                        <td>{u.first_name} {u.last_name}</td>
                        <td>
                            <span style={{ 
                                color: u.is_banned ? '#8b0000' : (u.is_active ? 'green' : 'red'),
                                fontWeight: 'bold'
                            }}>
                                {u.is_banned ? 'BANNED' : (u.is_active ? 'Active' : 'Inactive')}
                            </span>
                            {u.is_staff && <span style={{ color: '#007bff', fontSize: '0.8em' }}> (Staff)</span>}
                        </td>
                        <td>
                            <span style={{ 
                                color: u.is_2fa_enabled ? 'green' : '#999',
                                fontWeight: u.is_2fa_enabled ? 'bold' : 'normal'
                            }}>
                                {u.is_2fa_enabled ? '✓ Enabled' : '✗ Disabled'}
                            </span>
                        </td>
                        <td style={{ maxWidth: '200px', fontSize: '0.8em' }}>
                            {u.operations && u.operations.length > 0 ? (
                                <div style={{ maxHeight: '100px', overflowY: 'auto' }}>
                                    {u.operations.map((op, index) => (
                                        <div key={index} style={{ 
                                            marginBottom: '2px',
                                            padding: '2px 4px',
                                            backgroundColor: op.operation_type === 'delete' ? '#ffebee' : '#f5f5f5',
                                            borderRadius: '2px',
                                            fontSize: '0.75em'
                                        }}>
                                            <strong style={{ 
                                                color: op.operation_type === 'add' ? 'green' : 
                                                       op.operation_type === 'edit' ? 'orange' : 'red'
                                            }}>
                                                {op.operation_type.toUpperCase()}
                                            </strong>: {op.coffee_name || `Coffee #${op.coffee_id}`}
                                            <br />
                                            <span style={{ color: '#666' }}>
                                                {new Date(op.timestamp).toLocaleString()}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <span style={{ color: '#999' }}>No operations</span>
                            )}
                        </td>
                        <td style={{ fontSize: '0.8em', maxWidth: '150px' }}>
                            {u.is_banned ? (
                                <div style={{ color: '#8b0000', fontWeight: 'bold' }}>
                                    🚫 BANNED
                                </div>
                            ) : u.is_suspicious ? (
                                <div>
                                    <div style={{ 
                                        color: '#d32f2f',
                                        fontWeight: 'bold',
                                        marginBottom: '4px',
                                        fontSize: '0.9em'
                                    }}>
                                        ⚠️ SUSPICIOUS
                                    </div>
                                    <div style={{ fontSize: '0.75em', color: '#666' }}>
                                        Count: {u.suspicious_activity_count || 0}
                                    </div>
                                    {u.last_suspicious_check_date && (
                                        <div style={{ fontSize: '0.7em', color: '#999' }}>
                                            Last checked: {new Date(u.last_suspicious_check_date).toLocaleDateString()}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <span style={{ color: '#999', fontSize: '0.8em' }}>Normal</span>
                            )}
                        </td>
                        <td style={{ fontSize: '0.8em', minWidth: '120px' }}>
                            {!u.is_banned && u.is_suspicious && (
                                <div>
                                    <button
                                        onClick={() => handleVerifyUser(u.id)}
                                        disabled={actionLoading[`verify_${u.id}`]}
                                        style={{
                                            backgroundColor: '#4CAF50',
                                            color: 'white',
                                            border: 'none',
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontSize: '0.75em',
                                            marginBottom: '4px',
                                            width: '100%'
                                        }}
                                    >
                                        {actionLoading[`verify_${u.id}`] ? 'Verifying...' : 'Verify Activity'}
                                    </button>
                                    {(u.suspicious_activity_count >= 3) && (
                                        <button
                                            onClick={() => handleBanUser(u.id)}
                                            disabled={actionLoading[`ban_${u.id}`]}
                                            style={{
                                                backgroundColor: '#f44336',
                                                color: 'white',
                                                border: 'none',
                                                padding: '4px 8px',
                                                borderRadius: '4px',
                                                cursor: 'pointer',
                                                fontSize: '0.75em',
                                                width: '100%'
                                            }}
                                        >
                                            {actionLoading[`ban_${u.id}`] ? 'Banning...' : 'BAN USER'}
                                        </button>
                                    )}
                                </div>
                            )}
                            {u.is_banned && (
                                <span style={{ color: '#8b0000', fontSize: '0.7em' }}>No actions available</span>
                            )}
                            {!u.is_suspicious && !u.is_banned && (
                                <span style={{ color: '#999', fontSize: '0.7em' }}>No actions needed</span>
                            )}
                        </td>
                        <td>{u.last_login ? new Date(u.last_login).toLocaleString() : 'Never'}</td>
                        <td>{new Date(u.date_joined).toLocaleString()}</td>
                    </tr>
                ))}
                </tbody>
            </table>
            
            <div style={{ marginTop: '1rem', fontSize: '0.9em', color: '#666' }}>
                <p><strong>Legend:</strong></p>
                <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
                    <li>Green background: Special Admin users</li>
                    <li><span style={{ backgroundColor: '#ffebee', padding: '2px 4px' }}>Light red background</span>: Users with suspicious activity</li>
                    <li><span style={{ backgroundColor: '#ffcccb', padding: '2px 4px' }}>Dark red background</span>: Banned users</li>
                    <li>Bold username: Superuser privileges</li>
                    <li>Operations column shows recent coffee operations (ADD/EDIT/DELETE)</li>
                    <li>⚠️ Warning icon indicates suspicious deletion patterns</li>
                    <li>🚫 Ban icon indicates permanently banned users</li>
                    <li>BAN USER button appears after 3 suspicious activity incidents</li>
                </ul>
            </div>
        </div>
    );
}
