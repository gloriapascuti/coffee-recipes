import styles from './styles/GrindingBeans.module.css'

const GrindingBeans = () => {
    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.Title}>Grinding the beans</div>
                <div className={styles.grindingGrid}>
                    <div className={styles.grindingCard}>
                        <div className={styles.image1}></div>
                        <div className={styles.subheading}>Why is grinding important?</div>
                        <div className={styles.bodyTextFor}>
                            Each coffee particle has an amount of extractable mass (the taste). As you soak it in hot water, the structure softens and the water extracts the taste extracts the taste. However this takes time. The longer the particle, the longer it takes to extract the taste near the middle.
                        </div>
                    </div>
                    <div className={styles.grindingCard}>
                        <div className={styles.image2}></div>
                        <div className={styles.subheading}>The extraction</div>
                        <div className={styles.bodyTextFor}>
                            Different taste compounds extract at different rates
                        </div>
                    </div>
                    <div className={styles.grindingCard}>
                        <div className={styles.image3}></div>
                        <div className={styles.subheading}>Different roasts</div>
                        <div className={styles.bodyTextFor}>
                            Light roast: light brown color with a mild flavor, such as fruity or floral notes<br/><br/>
                            Medium roast: Balanced in flavor, acidity and aroma<br/><br/>
                            Dark roast: has a smoky, bitter flavor and less acidity
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default GrindingBeans

/*Each coffee particle has an amount of extratactable mass (the taste) locked inside a tight cellulose structure
(the 'wood' of the seed). As you soak it in hot water, the structure softens and the water extracts the taste.
However, this takes time. The larger the particle, the longer it takes to extract the taste near the middle.
To add to this, different taste compounds also extract at differing rates.*/