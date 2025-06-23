import React, { useEffect, useState, useContext } from "react";
import { CoffeeContext } from '../CoffeeContext';
import styles from './styles/RUD.module.css';

const InfiniteScroll = ({data, loading, getBackgroundColor, loadMoreData}) => {
    const [displayData, setDisplayData] = useState([]);
    const { addToFavorites, removeFromFavorites, isFavorite } = useContext(CoffeeContext);

    useEffect(() => {
        setDisplayData(data);
    }, [data]);

    const handleScroll = () => {
        const { scrollTop, clientHeight, scrollHeight } = document.documentElement;

        if (scrollTop + clientHeight >= scrollHeight - 10 && !loading) {
            loadMoreData();
        }
    };

    useEffect(() => {
        // window.addEventListener('scroll', handleScroll);

        // return () => {
        //     window.removeEventListener('scroll', handleScroll);
        // };
    }, [loading]);

    const handleFavoriteClick = (coffee, event) => {
        event.stopPropagation(); // Prevent any parent click handlers
        
        if (isFavorite(coffee.id)) {
            removeFromFavorites(coffee.id);
        } else {
            addToFavorites(coffee);
        }
    };

    const handleLikeClick = async (coffee, event) => {
        event.stopPropagation(); // Prevent any parent click handlers
        
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            alert('Please log in to like recipes');
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/like/${coffee.id}/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                
                // Update the coffee in displayData with new like count and status
                setDisplayData(prevData => 
                    prevData.map(c => 
                        c.id === coffee.id 
                            ? { ...c, likes_count: data.likes_count, is_liked: data.liked }
                            : c
                    )
                );
            } else {
                console.error('Failed to toggle like');
            }
        } catch (error) {
            console.error('Error toggling like:', error);
        }
    };

    return (
        <div className={styles.scrollContainer}>
            {displayData && displayData.map((coffee, index) => (
                <li key={index} className={styles.customerQuote} style={{ backgroundColor: getBackgroundColor(coffee.name) }}>
                    <div className={styles.recipeHeader}>
                        <div className={styles.aTerrificPiece}>{coffee.name}</div>
                        <div className={styles.actionButtons}>
                            <button 
                                className={`${styles.likeButton} ${coffee.is_liked ? styles.likeActive : ''}`}
                                onClick={(e) => handleLikeClick(coffee, e)}
                                title={coffee.is_liked ? "Unlike this recipe" : "Like this recipe"}
                            >
                                {coffee.is_liked ? '❤️' : '🤍'} {coffee.likes_count || 0}
                            </button>
                            <button 
                                className={`${styles.favoriteButton} ${isFavorite(coffee.id) ? styles.favoriteActive : ''}`}
                                onClick={(e) => handleFavoriteClick(coffee, e)}
                                title={isFavorite(coffee.id) ? "Remove from favorites" : "Add to favorites"}
                            >
                                {isFavorite(coffee.id) ? '🤎' : '🤍'}
                            </button>
                        </div>
                    </div>
                    <div className={styles.nameParent}>
                        <div className={styles.name}>{coffee.origin.name}</div>
                        <div className={styles.description}>{coffee.description}</div>
                    </div>
                </li>
            ))}
            {loading && <p>loading...</p>}
        </div>
    );
};

export default InfiniteScroll;