import React, { useEffect, useState, useContext } from "react";
import { CoffeeContext } from '../CoffeeContext';
import styles from './styles/RUD.module.css';

const InfiniteScroll = ({data, loading, getBackgroundColor, loadMoreData}) => {
    const [displayData, setDisplayData] = useState([]);
    const [activeChallengeRecipeIds, setActiveChallengeRecipeIds] = useState(new Set());
    const { addToFavorites, removeFromFavorites, isFavorite } = useContext(CoffeeContext);

    useEffect(() => {
        setDisplayData(data);
    }, [data]);

    // Fetch active challenges to determine which recipes can be liked
    useEffect(() => {
        const fetchActiveChallenges = async () => {
            try {
                const accessToken = localStorage.getItem('access_token');
                const headers = {
                    'Content-Type': 'application/json'
                };
                if (accessToken) {
                    headers['Authorization'] = `Bearer ${accessToken}`;
                }

                const response = await fetch('http://127.0.0.1:8000/api/challenges/', {
                    headers
                });

                if (response.ok) {
                    const challenges = await response.json();
                    // Filter for active challenges (accepted, active, or voting status)
                    const activeChallenges = challenges.filter(
                        challenge => ['accepted', 'active', 'voting'].includes(challenge.status)
                    );
                    
                    // Collect recipe identifiers from active challenges
                    // Store user_id and recipe name for matching
                    const recipeIdentifiers = new Set();
                    activeChallenges.forEach(challenge => {
                        if (challenge.recipes && challenge.recipes.length > 0) {
                            challenge.recipes.forEach(recipe => {
                                // recipe.user is an object, get the ID
                                const userId = recipe.user?.id || recipe.user;
                                if (userId && recipe.name) {
                                    // Match by user ID and recipe name
                                    const recipeKey = `${userId}_${recipe.name}`;
                                    recipeIdentifiers.add(recipeKey);
                                }
                            });
                        } else {
                            // If no recipes submitted yet but challenge is active (accepted status),
                            // mark all recipes by participants that match the coffee_type
                            if (challenge.challenger && challenge.challenged && challenge.coffee_type) {
                                const challengerId = challenge.challenger?.id || challenge.challenger;
                                const challengedId = challenge.challenged?.id || challenge.challenged;
                                if (challengerId) {
                                    const challengerKey = `${challengerId}_${challenge.coffee_type.toLowerCase()}`;
                                    recipeIdentifiers.add(challengerKey);
                                }
                                if (challengedId) {
                                    const challengedKey = `${challengedId}_${challenge.coffee_type.toLowerCase()}`;
                                    recipeIdentifiers.add(challengedKey);
                                }
                            }
                        }
                    });
                    
                    setActiveChallengeRecipeIds(recipeIdentifiers);
                }
            } catch (error) {
                console.error('Error fetching active challenges:', error);
            }
        };

        fetchActiveChallenges();
        // Refresh challenge data every 30 seconds to catch new active challenges
        const interval = setInterval(fetchActiveChallenges, 30000);
        return () => clearInterval(interval);
    }, []);

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
                        <div className={styles.aTerrificPiece}>
                            {coffee.name}
                            {coffee.is_community_winner && <span className={styles.communityWinnerStar}>⭐</span>}
                        </div>
                        <div className={styles.actionButtons}>
                            {/* Show like button only if recipe is part of an active challenge */}
                            {(() => {
                                // Check if this coffee is part of an active challenge
                                // Match by user ID and coffee name
                                const recipeKey = `${coffee.user}_${coffee.name}`;
                                const isInActiveChallenge = activeChallengeRecipeIds.has(recipeKey);
                                
                                if (isInActiveChallenge) {
                                    return (
                                        <button 
                                            className={`${styles.likeButton} ${coffee.is_liked ? styles.likeActive : ''}`}
                                            onClick={(e) => handleLikeClick(coffee, e)}
                                            title={coffee.is_liked ? "Unlike this recipe" : "Like this recipe (Active Challenge)"}
                                        >
                                            {coffee.is_liked ? '❤️' : '🤍'}{(coffee.likes_count || 0) > 0 && ` ${coffee.likes_count}`}
                                        </button>
                                    );
                                }
                                return null;
                            })()}
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