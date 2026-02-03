import React from 'react';
import styles from './styles/AddCoffee.module.css';

const AddCoffee = () => {
    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.ctaCard}>
                    <h2 className={styles.ctaTitle}>Discover Our Amazing Features</h2>
                    <div className={styles.featuresList}>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>☕</span>
                            <span>Create custom coffee recipes</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>🔍</span>
                            <span>Search through thousands of recipes</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>📊</span>
                            <span>View detailed coffee analytics</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>🎯</span>
                            <span>Filter by origin and preferences</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>🤖</span>
                            <span>AI-powered recipe recommendations</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>🔒</span>
                            <span>Secure user authentication</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>📤</span>
                            <span>Upload and download recipe instructions and videos</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>❤️</span>
                            <span>Make your own favorite list</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>🏥</span>
                            <span>ML-powered heart disease risk assessment</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>📈</span>
                            <span>Track coffee consumption and health predictions</span>
                        </div>
                        <div className={styles.feature}>
                            <span className={styles.featureIcon}>💊</span>
                            <span>Personalized health insights based on caffeine intake</span>
                        </div>
                    </div>
                </div>
                <div className={styles.imageContainer}>
                    <div className={styles.coffeeImage}></div>
                </div>
            </div>
        </div>
    );
};

export default AddCoffee;
