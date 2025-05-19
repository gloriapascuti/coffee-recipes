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

export default function AdminUserTable() {
    const [users, setUsers] = useState([]);
    const userId = localStorage.getItem('user_id');

    useEffect(() => {
        if (userId === '1') {
            const token = localStorage.getItem('token');
            axios
                .get('http://127.0.0.1:8000/api/users/', {
                    headers: { Authorization: `Token ${token}` }
                })
                .then(res => {
                    setUsers(res.data);
                    console.log('AdminUserTable users:', res.data);
                })
                .catch(console.error);
        }
    }, [userId]);

    // Only render for the admin user (id === '1')
    if (userId !== '1') {
        return null;
    }

    const formatDate = isoString =>
        isoString ? new Date(isoString).toLocaleString() : '';

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
