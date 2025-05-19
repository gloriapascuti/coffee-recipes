import styles from './styles/Header2.module.css'
import React from "react";

const Header2 = () => {
    return (
        <div>
            <div>
                <div className={styles.header}>
                    <div className={styles.items}>
                        <div className={styles.page}>Page 1</div>
                        <div className={styles.page}>Page 2</div>
                        <div className={styles.page}>Page 3</div>
                    </div>
                </div>
                <div className={styles.siteTitle}>Coffee-website</div>
            </div>
            <div className={styles.Title}>All recipes</div>
        </div>



    )
}

export default Header2