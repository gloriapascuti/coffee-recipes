import styles from './styles/Header.module.css'
import React from "react";
import { useCoffee } from '../CoffeeContext';
import { useHistory, Link, useLocation } from 'react-router-dom';

const Header = () => {
    const { user, logoutUser } = useCoffee();
    const history = useHistory();
    const location = useLocation();

    const handleLogout = () => {
        logoutUser();
        history.push('/');
    };

    const getCurrentPage = () => {
        const path = location.pathname;
        if (path.includes('/page1')) return 1;
        if (path.includes('/page2')) return 2;
        return 1; // default to page 1
    };

    const getPageContent = () => {
        const path = location.pathname;
        if (path.includes('/page1')) {
            return {
                title: "Why anyone should love coffee",
                description: "this is a short history that will totally convince anyone that coffee is the best drink"
            };
        } else if (path.includes('/page2')) {
            return {
                title: "All recipes",
                description: "Explore our collection of coffee recipes, statistics, and brewing methods"
            };
        }
        return {
            title: "Why anyone should love coffee",
            description: "this is a short history that will totally convince anyone that coffee is the best drink"
        };
    };

    const currentPage = getCurrentPage();
    const pageContent = getPageContent();

    return (
        <div className={styles.headerContainer}>
            <div className={styles.navigationSection}>
                <div className={styles.header}>
                    <div className={styles.items}>
                        <Link 
                            to="/page1" 
                            className={`${styles.page} ${currentPage === 1 ? styles.activePage : ''}`}
                        >
                            Page 1
                        </Link>
                        <Link 
                            to="/page2" 
                            className={`${styles.page} ${currentPage === 2 ? styles.activePage : ''}`}
                        >
                            Page 2
                        </Link>
                        <Link to="/recommendations" className={styles.recommendationsButton}>
                            Recommendations
                        </Link>
                        <Link to="/community" className={styles.communityButton}>
                            Community
                        </Link>
                    </div>
                    {user && (
                        <div className={styles.userActions}>
                            <Link to="/profile" className={styles.profileButton}>
                                Profile
                            </Link>
                            <Link to="/settings" className={styles.settingsButton}>
                                Settings
                            </Link>
                            <button onClick={handleLogout} className={styles.logoutButton}>
                                Logout
                            </button>
                        </div>
                    )}
                </div>
                <div className={styles.siteTitle}>Coffee-website</div>
            </div>
            <div className={styles.contentSection}>
                <div className={styles.Title}>{pageContent.title}</div>
                <div className={styles.descriptionTitle}>{pageContent.description}</div>
            </div>
        </div>
    )
}

export default Header