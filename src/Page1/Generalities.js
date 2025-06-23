import styles from './styles/Generalities.module.css'

const Generalities = () => {
    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.image}></div>
                <div className={styles.textContent}>
                    <div className={styles.talkAboutSpeciality}>
                        Coffee has created a vibrant and changing culture
                        throughout the world from its humble origins as a
                        discovery in the highlands of Ethiopia to its current global prominence.

                        During the 15th century, coffee's impact from Ethiopia spread to the Arabic world.
                        Qahveh Khaneh, or coffee shops, became well-liked gathering places for individuals to talk
                        about philosophy, politics, and business.
                        As a result of the success of these energetic institutions, coffeehouses began to pop up all
                        throughout the region, including in towns like Mecca, Cairo, and Istanbul.

                        In the 16th century, traders and merchants coming from the Middle East brought
                        the first known coffee plants to Europe.
                        In cities like London, Paris, and Vienna, coffee shops known as "penny universities"
                        developed and became hubs for writers, artists, and intellectuals.

                        Through Dutch and French traders, coffee predominantly reached the Americas in the 17th century.
                        These areas' favourable environment made it possible to grow and produce coffee on a vast scale.

                        Countries with booming coffee industries include Brazil, Colombia, and Costa Rica,
                        which transformed their economies and established thriving coffee cultures.
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Generalities