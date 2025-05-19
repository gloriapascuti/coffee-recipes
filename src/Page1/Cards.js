import styles from './styles/Cards.module.css';


const Cards = () => {
    return (
        <div>
            <div className={styles.Title}>Most Popular Recipes</div>
            <div className={styles.cards}>
                <div className={styles.customerQuote}>
                    <div className={styles.aTerrificPiece}>“creamy, smooth, and balanced; rich, but not acidic and have a mildly sweet flavouring from the milk”</div>
                    <div className={styles.avatar}>
                        <img className={styles.avatarIcon} />
                        <div className={styles.nameParent}>
                            <div className={styles.name}>Cappuccino</div>
                            <div className={styles.description}>1 shot of espresso with milk</div>
                        </div>
                    </div>
                </div>
                <div className={styles.customerQuote1}>
                    <div className={styles.aTerrificPiece}>“bold, with a dense and delightful aroma; it's consistent and heavy but ranging from light to full”</div>
                    <div className={styles.avatar}>
                        <img className={styles.avatarIcon} />
                        <div className={styles.nameParent}>
                            <div className={styles.name}>Espresso</div>
                            <div className={styles.description}>36ml of extraction, medium roast</div>
                        </div>
                    </div>
                </div>
                <div className={styles.customerQuote2}>
                    <div className={styles.aTerrificPiece}>“rich, with a deep coffee flavor, and this particular one has was slightly sweet on the tip of my tongue”</div>
                    <div className={styles.avatar}>
                        <img className={styles.avatarIcon}/>
                        <div className={styles.nameParent}>
                            <div className={styles.name}>Latte</div>
                            <div className={styles.description}>2 shots of espresso with milk</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
};

export default Cards;
