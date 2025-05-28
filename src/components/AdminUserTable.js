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
    const { user, accessToken } = useCoffee();

    // Debug logging
    console.log('AdminUserTable - Current user:', user);
    console.log('AdminUserTable - Is special admin:', user?.is_special_admin);

    useEffect(() => {
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
    }, [user, accessToken]);

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
                    <th>Last Login</th>
                    <th>Date Joined</th>
                </tr>
                </thead>
                <tbody>
                {users.map(u => (
                    <tr key={u.id} style={{ 
                        backgroundColor: u.is_suspicious ? '#ffebee' : (u.is_special_admin ? '#e8f5e8' : 'white'),
                        borderBottom: '1px solid #ddd',
                        color: u.is_suspicious ? '#d32f2f' : 'inherit'
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
                                color: u.is_active ? 'green' : 'red',
                                fontWeight: 'bold'
                            }}>
                                {u.is_active ? 'Active' : 'Inactive'}
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
                            {u.is_suspicious && (
                                <div style={{ 
                                    color: '#d32f2f',
                                    fontWeight: 'bold',
                                    marginBottom: '4px',
                                    fontSize: '0.9em'
                                }}>
                                    ⚠️ SUSPICIOUS ACTIVITY
                                </div>
                            )}
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
                    <li><span style={{ color: '#ffebee', backgroundColor: '#ffebee', padding: '2px 4px' }}>Red background</span>: Users with suspicious activity (5+ consecutive deletes)</li>
                    <li>Bold username: Superuser privileges</li>
                    <li>Operations column shows recent coffee operations (ADD/EDIT/DELETE)</li>
                    <li>⚠️ Warning icon indicates suspicious deletion patterns</li>
                </ul>
            </div>
        </div>
    );
}
