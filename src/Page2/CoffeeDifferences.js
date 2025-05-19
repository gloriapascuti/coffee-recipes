import styles from './styles/CoffeeDifferences.module.css'

const CoffeeDifferences = () => {
    const links = [
        'https://i.pinimg.com/736x/f1/3b/65/f13b653fceab444e7c7985782a7e1578.jpg',
        'https://i.pinimg.com/736x/2a/46/75/2a467563694c291c864e747dd6be0444.jpg',
        'https://i.pinimg.com/736x/c4/cb/dd/c4cbdd755f3420bc6bf58841b8420cbe.jpg',
    ]
    return (
        <div>
            <div className={styles.container}>
                {
                    links.map((link, index) => (
                        <img key={index} src={link} className={styles.image} />
                    ))
                }

                {/*<img src={require('/Users/filip/Documents/gloria/UBB/facultate/Anul II/semester2/MPP/coffee-website/src/images/v60_2.png')} className={styles.image}/>*/}

                {/*<div className={styles.container_image1}>*/}
                {/*    <img src={require()} className={styles.image1}/>*/}
                {/*</div>*/}
                {/*<div className={styles.container_image2}>*/}
                {/*    <img className={styles.image2}/>*/}
                {/*</div>*/}
                {/*<div className={styles.container_image2}>*/}
                {/*    <img className={styles.image3}/>*/}
                {/*</div>*/}
            </div>
            <div className={styles.text} style={{fontFamily: "Georgia"}}>
                Brewing Methods:
                Drip Coffee (Filter Coffee), Espresso, French Press (Press Pot), Cold Brew, Pour Over (e.g., Chemex, V60)
            </div>
            <div className={styles.text} style={{fontFamily: "Georgia"}}>
                Coffee Drinks:
                Americano, Latte, Cappuccino, Mocha
            </div>
        </div>

    )
}

export default CoffeeDifferences