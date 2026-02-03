import React from 'react';
import { useHistory } from 'react-router-dom';
import TwoFactorSettings from './TwoFactorSettings';
import HealthProfile from './HealthProfile';
import AdminUserTable from '../components/AdminUserTable';
import UserNotification from '../components/UserNotification';
import styles from './styles/Login.module.css';

const UserSettings = () => {
    const history = useHistory();

    return (
        <div style={{ maxWidth: '1200px', margin: '20px auto', fontFamily: 'Georgia' }}>
            <button 
                onClick={() => history.goBack()} 
                className={styles.backButton}
            >
                ← Back
            </button>
            <h1>User Settings</h1>
            
            {/* User notification for investigation status */}
            <UserNotification />
            
            <div style={{ marginTop: '20px' }}>
                <TwoFactorSettings />
            </div>
            
            <div style={{ marginTop: '40px' }}>
                <HealthProfile />
            </div>
            
            {/* Admin User Table - only visible to special admin users */}
            <AdminUserTable />
        </div>
    );
};

export default UserSettings; 