import styles from './styles/ViewSection.module.css';


const ViewSection = () => {
    return (
        <div className={styles.section}>
            <div className={styles.buttons}>
                <div className={styles.button}>
                    <div className={styles.view}>View</div>
                </div>
                <div className={styles.button1}>
                    <div className={styles.view}>View your recipes</div>
                </div>
            </div>
            <div className={styles.viewAllRecipes}>View recipes</div>
        </div>);
};

export default ViewSection;
