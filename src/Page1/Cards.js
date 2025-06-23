import React, { useState, useEffect } from 'react';
import styles from './styles/Cards.module.css';

const Cards = () => {
    const [popularRecipes, setPopularRecipes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPopularRecipes();
    }, []);

    const fetchPopularRecipes = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/most-popular/');
            if (response.ok) {
                const data = await response.json();
                setPopularRecipes(data);
            } else {
                console.error('Failed to fetch popular recipes');
            }
        } catch (error) {
            console.error('Error fetching popular recipes:', error);
        } finally {
            setLoading(false);
        }
    };

    const getCardClassName = (index) => {
        switch (index) {
            case 0: return styles.customerQuote;
            case 1: return styles.customerQuote1;
            case 2: return styles.customerQuote2;
            default: return styles.customerQuote;
        }
    };

    const truncateDescription = (description, maxLength = 120) => {
        if (description.length <= maxLength) return description;
        return description.substring(0, maxLength) + '...';
    };

    if (loading) {
        return (
            <div className={styles.container}>
                <div className={styles.content}>
                    <div className={styles.Title}>Most Popular Recipes</div>
                    <div className={styles.cards}>
                        <div className={styles.loadingMessage}>Loading popular recipes...</div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.Title}>Most Popular Recipes</div>
                <div className={styles.cards}>
                    {popularRecipes.map((recipe, index) => (
                        <div key={recipe.id} className={getCardClassName(index)}>
                            <div className={styles.aTerrificPiece}>
                                "{truncateDescription(recipe.description)}"
                            </div>
                            <div className={styles.avatar}>
                                <div className={styles.avatarIcon}></div>
                                <div className={styles.nameParent}>
                                    <div className={styles.name}>{recipe.name}</div>
                                    <div className={styles.description}>
                                        {recipe.origin?.name || 'Unknown Origin'} • {recipe.likes_count || 0} likes
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
};

export default Cards;
