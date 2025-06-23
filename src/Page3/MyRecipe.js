import styles from './styles/MyRecipe.module.css'
import React from 'react';

const MyRecipe = () => {
    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.placeholder}>
                    <div className={styles.placeholderCard}>
                        <h3>Your Recipe Collection</h3>
                        <p>Start building your personal coffee recipe library. Add custom brewing methods, notes, and share with the community.</p>
                    </div>
                    
                    <div className={styles.placeholderCard}>
                        <h3>Recipe Builder</h3>
                        <p>Use our intuitive recipe builder to document your brewing process, ingredients, and tasting notes.</p>
                    </div>
                    
                    <div className={styles.placeholderCard}>
                        <h3>Community Sharing</h3>
                        <p>Share your favorite recipes with other coffee enthusiasts and discover new brewing techniques.</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default MyRecipe