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
                // Ensure we only show top 3 most liked recipes
                const top3 = data.slice(0, 3).sort((a, b) => (b.likes_count || 0) - (a.likes_count || 0));
                setPopularRecipes(top3);
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
                    {popularRecipes.length > 0 ? (
                        popularRecipes.map((recipe, index) => (
                            <div key={recipe.id} className={getCardClassName(index)}>
                                <div className={styles.aTerrificPiece}>
                                    "{truncateDescription(recipe.description)}"
                                </div>
                                <div className={styles.avatar}>
                                    <div className={styles.avatarIcon}></div>
                                    <div className={styles.nameParent}>
                                        <div className={styles.name}>{recipe.name}</div>
                                        <div className={styles.description}>
                                            {recipe.origin?.name || 'Unknown Origin'}{(recipe.likes_count || 0) > 0 && ` • ${recipe.likes_count} ${recipe.likes_count === 1 ? 'like' : 'likes'}`}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className={styles.noRecipesMessage}>No popular recipes available yet. Be the first to like a recipe!</div>
                    )}
                </div>
            </div>
        </div>
    )
};

export default Cards;
