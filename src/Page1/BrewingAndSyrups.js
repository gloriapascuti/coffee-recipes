import React from 'react';
import styles from './styles/BrewingAndSyrups.module.css';

const BrewingAndSyrups = () => {
    // Coffee brewing equipment images
    const brewingEquipmentLinks = [
        'https://i.pinimg.com/736x/f1/3b/65/f13b653fceab444e7c7985782a7e1578.jpg',
        'https://i.pinimg.com/736x/2a/46/75/2a467563694c291c864e747dd6be0444.jpg',
        'https://i.pinimg.com/736x/c4/cb/dd/c4cbdd755f3420bc6bf58841b8420cbe.jpg',
    ];

    // Syrup flavor images
    const syrupLinks = [
        'https://i.pinimg.com/736x/ff/55/0f/ff550f17c7db2c534980123c84d46bb3.jpg',
        'https://i.pinimg.com/736x/77/05/3d/77053d5cf82b4b5704c87be6a07da6ec.jpg',
        'https://i.pinimg.com/736x/ce/29/2a/ce292a8f96f1d8611316a7e2056511d5.jpg',
    ];

    const equipmentCaptions = [
        'Professional Espresso Machine',
        'Pour Over Coffee Setup',
        'French Press Collection'
    ];

    const syrupCaptions = [
        'Vanilla Syrup',
        'Caramel Syrup',
        'Hazelnut Syrup'
    ];

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.sectionTitle}>Coffee Equipment & Flavors</div>
                
                {/* Coffee Brewing Equipment Section */}
                <div className={styles.section}>
                    <div className={styles.sectionSubtitle}>Coffee Brewing Equipment</div>
                    <div className={styles.imagesGrid}>
                        {brewingEquipmentLinks.map((link, index) => (
                            <div key={index} className={styles.imageCard}>
                                <div 
                                    className={styles.equipmentImage}
                                    style={{ backgroundImage: `url(${link})` }}
                                ></div>
                                <div className={styles.imageCaption}>
                                    {equipmentCaptions[index]}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Syrup Flavors Section */}
                <div className={styles.section}>
                    <div className={styles.sectionSubtitle}>Popular Syrup Flavors</div>
                    <div className={styles.imagesGrid}>
                        {syrupLinks.map((link, index) => (
                            <div key={index} className={styles.imageCard}>
                                <div 
                                    className={styles.syrupImage}
                                    style={{ backgroundImage: `url(${link})` }}
                                ></div>
                                <div className={styles.imageCaption}>
                                    {syrupCaptions[index]}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BrewingAndSyrups; 