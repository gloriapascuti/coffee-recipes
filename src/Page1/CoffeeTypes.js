import styles from './styles/CoffeeTypes.module.css'

const CoffeeTypes = () => {
    return (

        <div>
            <div className={styles.Title}>Types of Coffee</div>
            <div style={{display: "flex", gap: "50px"}}>
                <div className={styles.container_image1}>
                    <div>
                        <img className={styles.imageIcon1}/>
                        <div className={styles.subheading}>Espresso Machine</div>
                        <div className={styles.bodyTextFor}>{`Most popular way to make coffee (espresso, cappuccino, latte, flat white)`}</div>
                    </div>
                </div>
                <div className={styles.container_image2}>
                    <img className={styles.imageIcon2}/>
                    <div className={styles.subheading}>Aero-press</div>
                    <div className={styles.bodyTextFor}>{`Manual coffeemaker, a hybrid of immersion dripper and filter brewing`}</div>
                </div>
                <div className={styles.container_image3}>
                    <img className={styles.imageIcon3}/>
                    <div className={styles.subheading}>French-press</div>
                    <div className={styles.bodyTextFor}>{`Coffee brewer by saturating coffee ground in hot water then applying 
                    manual pressure to force the hot water through coffee to the bottom of the pot`}</div>
                </div>
            </div>
        </div>


    )
}

export default  CoffeeTypes