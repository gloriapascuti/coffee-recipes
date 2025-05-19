import styles from './styles/Syrup.module.css'

const Syrup = () => {
    const links = [
        'https://i.pinimg.com/736x/ff/55/0f/ff550f17c7db2c534980123c84d46bb3.jpg',
        'https://i.pinimg.com/736x/77/05/3d/77053d5cf82b4b5704c87be6a07da6ec.jpg',
        'https://i.pinimg.com/736x/ce/29/2a/ce292a8f96f1d8611316a7e2056511d5.jpg',
    ]

    return (
        <div>
            <div className={styles.title}>
                Coffee is often liked with syrup
            </div>
            <div className={styles.container}>
                {
                    links.map((link, index) => (
                        <img key={index} src={link} className={styles.image} />
                    ))
                }
            </div>
            <div className={styles.textContainer}>
                <div>vanilla</div>
                <div>caramel</div>
                <div>salted caramel</div>
            </div>
        </div>
    )
}

export default Syrup