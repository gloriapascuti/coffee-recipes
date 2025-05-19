import styles from './styles/NavigationFooter.module.css';


const NavigationFooter = () => {
    return (
        <div className={styles.navigationFooter}>
            <div className={styles.items}>
                <div className={styles.topic}>Topic</div>
                <div className={styles.page}>Page</div>
                <div className={styles.page}>Page</div>
                <div className={styles.page}>Page</div>
            </div>
            <div className={styles.items1}>
                <div className={styles.topic}>Topic</div>
                <div className={styles.page}>Page</div>
                <div className={styles.page}>Page</div>
                <div className={styles.page}>Page</div>
            </div>
            <div className={styles.items2}>
                <div className={styles.topic}>Topic</div>
                <div className={styles.page}>Page</div>
                <div className={styles.page}>Page</div>
                <div className={styles.page}>Page</div>
            </div>
            <div className={styles.siteName}>Coffee-website</div>
            <div className={styles.socialIcons}>
                <img className={styles.buttonsIcon} />
                <img className={styles.buttonsIcon} />
                <img className={styles.buttonsIcon} />
                <img className={styles.buttonsIcon} />
            </div>
            <div className={styles.divider} />
        </div>);
};

export default NavigationFooter;
