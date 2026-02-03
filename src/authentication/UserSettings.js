import React from 'react';
import { useHistory } from 'react-router-dom';
import TwoFactorSettings from './TwoFactorSettings';
import HealthProfile from './HealthProfile';
import AdminUserTable from '../components/AdminUserTable';
import UserNotification from '../components/UserNotification';
import styles from './styles/UserSettings.module.css';

const UserSettings = () => {
    const history = useHistory();

    return (
        <div className={styles.container}>
            <button 
                onClick={() => history.goBack()} 
                className={styles.backButton}
            >
                ← Back
            </button>
            <h1 className={styles.title}>User Settings</h1>
            
            {/* User notification for investigation status */}
            <UserNotification />
            
            <div className={styles.section}>
                <TwoFactorSettings />
            </div>
            
            <div className={styles.section}>
                <HealthProfile />
            </div>
            
            {/* Admin User Table - only visible to special admin users */}
            <AdminUserTable />
        </div>
    );
};

export default UserSettings; 