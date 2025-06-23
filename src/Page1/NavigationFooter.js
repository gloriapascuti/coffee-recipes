import styles from './styles/NavigationFooter.module.css';

const NavigationFooter = () => {
    return (
        <div className={styles.navigationFooter}>
            <div className={styles.footerContent}>
                <div className={styles.leftSection}>
                    <div className={styles.siteName}>Coffee-website</div>
                    <div className={styles.socialIcons}>
                        <div className={styles.socialIcon}>📘</div>
                        <div className={styles.socialIcon}>🐦</div>
                        <div className={styles.socialIcon}>📷</div>
                        <div className={styles.socialIcon}>💼</div>
                    </div>
                </div>
                <div className={styles.rightSection}>
                    <div className={styles.footerColumn}>
                        <div className={styles.topic}>Explore</div>
                        <div className={styles.page}>Coffee Types</div>
                        <div className={styles.page}>Brewing Methods</div>
                        <div className={styles.page}>Recipes</div>
                    </div>
                    <div className={styles.footerColumn}>
                        <div className={styles.topic}>Community</div>
                        <div className={styles.page}>Share Recipes</div>
                        <div className={styles.page}>Reviews</div>
                        <div className={styles.page}>Forums</div>
                    </div>
                    <div className={styles.footerColumn}>
                        <div className={styles.topic}>Support</div>
                        <div className={styles.page}>Help Center</div>
                        <div className={styles.page}>Contact Us</div>
                        <div className={styles.page}>FAQ</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default NavigationFooter;
