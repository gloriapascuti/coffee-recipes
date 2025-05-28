import styles from './styles/Header.module.css'
import React from "react";
import { useCoffee } from '../CoffeeContext';
import { useHistory, Link } from 'react-router-dom';

const Header = () => {
    const { user, logoutUser } = useCoffee();
    const history = useHistory();

    const handleLogout = () => {
        logoutUser();
        history.push('/');
    };

    return (
        <div>
            <div>
                <div>
                    <div className={styles.header}>
                        <div className={styles.items}>
                            <div className={styles.page}>Page 1</div>
                            <div className={styles.page}>Page 2</div>
                            <div className={styles.page}>Page 3</div>
                        </div>
                        {user && (
                            <>
                                <Link to="/settings" className={styles.settingsButton}>
                                    Settings
                                </Link>
                                <button onClick={handleLogout} className={styles.logoutButton}>
                                    Logout
                                </button>
                            </>
                        )}
                    </div>
                    <div className={styles.siteTitle}>Coffee-website</div>
                </div>
                <div className={styles.Title}>Why anyone should love coffee</div>
            </div>
            <div className={styles.descriptionTitle}>this is a short history that will totally convince anyone that coffee is the best drink</div>
        </div>
    )
}

export default Header