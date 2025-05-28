import React from 'react';
import TwoFactorSettings from './TwoFactorSettings';
import AdminUserTable from '../components/AdminUserTable';
import styles from './styles/Login.module.css';

const UserSettings = () => {
    return (
        <div style={{ maxWidth: '1200px', margin: '20px auto', fontFamily: 'Georgia' }}>
            <h1>User Settings</h1>
            <div style={{ marginTop: '20px' }}>
                <TwoFactorSettings />
            </div>
            
            {/* Admin User Table - only visible to special admin users */}
            <AdminUserTable />
        </div>
    );
};

export default UserSettings; 