import styles from './styles/Header.module.css'
import React from "react";

const Header = () => {
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