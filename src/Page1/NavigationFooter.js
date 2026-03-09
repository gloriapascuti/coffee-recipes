import { Link } from 'react-router-dom';
import styles from './styles/NavigationFooter.module.css';

const NavigationFooter = () => {
    return (
        <footer className={styles.navigationFooter}>
            <div className={styles.footerInner}>

                {/* Top row: brand + columns */}
                <div className={styles.footerTop}>
                    <div className={styles.brand}>
                        <div className={styles.siteName}>Coffee&#8209;website</div>
                        <div className={styles.pageNav}>
                            <Link to="/page1" className={styles.pageCircle}>1</Link>
                            <Link to="/page2" className={styles.pageCircle}>2</Link>
                            <Link to="/page3" className={styles.pageCircle}>3</Link>
                            <Link to="/page4" className={styles.pageCircle}>4</Link>
                        </div>
                    </div>

                    <div className={styles.columns}>
                        <div className={styles.footerColumn}>
                            <span className={styles.topic}>Explore</span>
                            <Link to="/page1#generalities" className={styles.footerLink}>Coffee History</Link>
                            <Link to="/page1#coffee-types" className={styles.footerLink}>Coffee Types</Link>
                            <Link to="/page1#grinding-beans" className={styles.footerLink}>Grinding the Beans</Link>
                            <Link to="/page1#brewing-methods" className={styles.footerLink}>Brewing Methods</Link>
                            <Link to="/recommendations" className={styles.footerLink}>Recommendations</Link>
                        </div>

                        <div className={styles.footerColumn}>
                            <span className={styles.topic}>Community</span>
                            <Link to="/community" className={styles.footerLink}>Community Hub</Link>
                            <Link to="/page2#all-recipes" className={styles.footerLink}>Recipes</Link>
                            <Link to="/page3#favorites" className={styles.footerLink}>Favorites</Link>
                        </div>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className={styles.footerBottom}>
                    <span className={styles.copyright}>© {new Date().getFullYear()} Coffee&#8209;website. All rights reserved.</span>
                </div>

            </div>
        </footer>
    );
};

export default NavigationFooter;
