import styles from './styles/GrindingBeans.module.css'

const GrindingBeans = () => {
    return (
        <div>
            <div className={styles.Title}>Grinding the beans</div>
            <div style={{display: "flex", gap: "80px"}}>
                <div className={styles.container_image1}>
                    <img className={styles.image1}/>
                    <div className={styles.subheading}>Why is grinding important?</div>
                    <div className={styles.bodyTextFor}>Each coffee particle has an amount of extractable mass</div>
                    <div className={styles.bodyTextFor}>(the taste). As you soak it in hot water, the structure</div>
                    <div className={styles.bodyTextFor}>softens and the water extracts the taste extracts the</div>
                    <div className={styles.bodyTextFor}>taste. However this takes time. The longer the particle,</div>
                    <div className={styles.bodyTextFor}>the longer it takes to extract the taste near the middle</div>
                </div>
                <div className={styles.container_image2}>
                    <img className={styles.image2}/>
                    <div className={styles.subheading}>The extraction</div>
                    <div className={styles.bodyTextFor}>Different taste compounds</div>
                    <div className={styles.bodyTextFor}>extract at different rates</div>
                </div>
                <div className={styles.container_image3}>
                    <img className={styles.image3}/>
                    <div className={styles.subheading}>Different roasts</div>
                    <div className={styles.bodyTextFor}>Light roast: light brown color with a mild flavor,</div>
                    <div className={styles.bodyTextFor}>such as fruity or floral notes</div>
                    <div className={styles.bodyTextFor}>Medium roast: Balanced in flavor, acidity and aroma</div>
                    <div className={styles.bodyTextFor}>Dark roast: has a smoky, bitter flavor and less acidity</div>
                </div>
            </div>
        </div>
    )
}

export default GrindingBeans

/*Each coffee particle has an amount of extratactable mass (the taste) locked inside a tight cellulose structure
(the ‘wood’ of the seed). As you soak it in hot water, the structure softens and the water extracts the taste.
However, this takes time. The larger the particle, the longer it takes to extract the taste near the middle.
To add to this, different taste compounds also extract at differing rates.*/