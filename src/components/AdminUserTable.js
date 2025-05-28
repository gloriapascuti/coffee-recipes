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
    const { user, accessToken } = useCoffee();

    // Debug logging
    console.log('AdminUserTable - Current user:', user);
    console.log('AdminUserTable - Current access token:', accessToken);

    useEffect(() => {
        console.log('AdminUserTable useEffect - user:', user);
        if (user && user.id === 1) {
            console.log('AdminUserTable - Making API request with token:', accessToken);
            axios
                .get('http://127.0.0.1:8000/api/users/', {
                    headers: { Authorization: `Bearer ${accessToken}` }
                })
                .then(res => {
                    console.log('AdminUserTable - API response:', res.data);
                    setUsers(res.data);
                })
                .catch(error => {
                    console.error('Error fetching users:', error);
                    if (error.response) {
                        console.error('Error response:', error.response.data);
                        console.error('Error status:', error.response.status);
                    }
                });
        } else {
            console.log('AdminUserTable - Not admin user, skipping API request');
        }
    }, [user, accessToken]);

    // Debug logging for render condition
    console.log('AdminUserTable - Rendering check, user:', user, 'should render:', user && user.id === 1);

    // Only render for the admin user (id === 1)
    if (!user || user.id !== 1) {
        return null;
    }

    return (
        <div style={{ margin: '2rem' }}>
            <h2>All Registered Users</h2>
            <table border="1" cellPadding="8">
                <thead>
                <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Last Login</th>
                    <th>Date Joined</th>
                    <th>Operations</th>
                </tr>
                </thead>
                <tbody>
                {users.map(u => {
                    const deleteCount = u.operations ? u.operations.filter(op => op.operation === 'delete').length : 0;
                    const isSuspicious = deleteCount >= 5;
                    const lastLogin = u.last_login ? u.last_login : u.date_joined;
                    return (
                        <tr key={u.id} style={isSuspicious ? { backgroundColor: 'red', color: 'white' } : {}}>
                            <td>{u.username}</td>
                            <td>{u.email}</td>
                            <td>{lastLogin ? new Date(lastLogin).toLocaleString() : ''}</td>
                            <td>{u.date_joined ? new Date(u.date_joined).toLocaleString() : ''}</td>
                            <td>
                                {u.operations && u.operations.length > 0 ? (
                                    <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                                        {u.operations.map((op, idx) => (
                                            <li key={idx}>
                                                <span style={{ fontWeight: op.operation === 'delete' ? 'bold' : 'normal' }}>{op.operation}</span>
                                                {' '}<span style={{ color: '#888', fontSize: '0.9em' }}>{op.timestamp ? new Date(op.timestamp).toLocaleString() : ''}</span>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <span>No operations</span>
                                )}
                                {isSuspicious && <span style={{ marginLeft: '1em', fontWeight: 'bold' }}>suspicious activity</span>}
                            </td>
                        </tr>
                    );
                })}
                </tbody>
            </table>
        </div>
    );
}
