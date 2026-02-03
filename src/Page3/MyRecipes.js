import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';
import styles from './styles/MyRecipes.module.css';

const API_URL = 'http://127.0.0.1:8000/api';

function authHeaders() {
    const accessToken = localStorage.getItem("access_token");
    const headers = {
        "Content-Type": "application/json"
    };
    if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`;
    }
    return headers;
}

export default function MyRecipes() {
    const { 
        coffees, 
        userId, 
        addCoffee, 
        editCoffee, 
        deleteCoffee,
        favorites,
        addToFavorites,
        removeFromFavorites,
        isFavorite,
        fetchData,
        authenticatedFetch
    } = useCoffee();

    const [myRecipes, setMyRecipes] = useState([]);
    const [favoritesList, setFavoritesList] = useState([]);
    const [activeTab, setActiveTab] = useState('my-recipes'); // 'my-recipes' or 'favorites'
    const [showAddForm, setShowAddForm] = useState(false);
    const [showEditForm, setShowEditForm] = useState(false);
    const [editingCoffee, setEditingCoffee] = useState(null);
    const [message, setMessage] = useState(null);
    const [origins, setOrigins] = useState([]);

    const [formData, setFormData] = useState({
        name: '',
        origin: '',
        description: ''
    });

    useEffect(() => {
        // Fetch user's own recipes directly from API (including private ones)
        const fetchMyRecipes = async () => {
            if (userId && authenticatedFetch) {
                try {
                    // Use the dedicated endpoint that includes private recipes
                    const response = await authenticatedFetch(`${API_URL}/my-recipes/`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (response.ok) {
                        const userRecipes = await response.json();
                        setMyRecipes(userRecipes);
                    } else {
                        console.error('Failed to fetch my recipes:', response.status);
                        // Fallback to filtering from context coffees (may miss private recipes)
                        const userRecipes = coffees.filter(c => {
                            const coffeeUserId = typeof c.user === 'object' ? c.user.id : c.user;
                            return coffeeUserId === userId;
                        });
                        setMyRecipes(userRecipes);
                    }
                } catch (error) {
                    console.error('Error fetching my recipes:', error);
                    // Fallback to filtering from context coffees (may miss private recipes)
                    const userRecipes = coffees.filter(c => {
                        const coffeeUserId = typeof c.user === 'object' ? c.user.id : c.user;
                        return coffeeUserId === userId;
                    });
        setMyRecipes(userRecipes);
                }
            } else {
                // No user ID, use empty array
                setMyRecipes([]);
            }
        };
        
        fetchMyRecipes();
        
        // Get favorites list
        setFavoritesList(favorites);
        
        // Fetch origins
        fetchOrigins();
    }, [coffees, userId, favorites, authenticatedFetch]);

    const fetchOrigins = async () => {
        try {
            const response = await fetch(`${API_URL}/origins/`);
            if (response.ok) {
                const data = await response.json();
                setOrigins(data);
            }
        } catch (err) {
            console.error('Error fetching origins:', err);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAddRecipe = async (e) => {
        e.preventDefault();
        if (!formData.name || !formData.origin || !formData.description) {
            setMessage({ type: 'error', text: 'Please fill in all fields' });
            return;
        }

        try {
            // Check if recipe with same name already exists
            const existing = coffees.find(c => 
                c.name.toLowerCase() === formData.name.toLowerCase() && 
                c.user === userId
            );

            if (existing) {
                setMessage({ 
                    type: 'warning', 
                    text: `Recipe "${formData.name}" already exists! It was already added to the all recipes table.` 
                });
                setShowAddForm(false);
                setFormData({ name: '', origin: '', description: '' });
                return;
            }

            const newCoffee = {
                name: formData.name,
                origin: formData.origin,
                description: formData.description
            };

            await addCoffee(newCoffee);
            setMessage({ type: 'success', text: 'Recipe added successfully!' });
            setShowAddForm(false);
            setFormData({ name: '', origin: '', description: '' });
            
            // Refresh data
            if (fetchData) {
                fetchData();
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Failed to add recipe. Please try again.' });
            console.error('Error adding recipe:', err);
        }
    };

    const handleEditRecipe = async (e) => {
        e.preventDefault();
        if (!formData.name || !formData.origin || !formData.description) {
            setMessage({ type: 'error', text: 'Please fill in all fields' });
            return;
        }

        try {
            await editCoffee(editingCoffee.id, {
                name: formData.name,
                origin: formData.origin,
                description: formData.description
            });
            setMessage({ type: 'success', text: 'Recipe updated successfully!' });
            setShowEditForm(false);
            setEditingCoffee(null);
            setFormData({ name: '', origin: '', description: '' });
            
            // Refresh data
            if (fetchData) {
                fetchData();
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Failed to update recipe. Please try again.' });
            console.error('Error updating recipe:', err);
        }
    };

    const handleDeleteRecipe = async (id) => {
        if (!window.confirm('Are you sure you want to delete this recipe?')) {
            return;
        }

        try {
            await deleteCoffee(id);
            setMessage({ type: 'success', text: 'Recipe deleted successfully!' });
            
            // Refresh data
            if (fetchData) {
                fetchData();
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Failed to delete recipe. Please try again.' });
            console.error('Error deleting recipe:', err);
        }
    };

    const handleStartEdit = (coffee) => {
        setEditingCoffee(coffee);
        setFormData({
            name: coffee.name,
            origin: coffee.origin.name,
            description: coffee.description
        });
        setShowEditForm(true);
    };

    const handleCancel = () => {
        setShowAddForm(false);
        setShowEditForm(false);
        setEditingCoffee(null);
        setFormData({ name: '', origin: '', description: '' });
    };

    const handleToggleFavorite = (coffee) => {
        if (isFavorite(coffee.id)) {
            removeFromFavorites(coffee.id);
        } else {
            addToFavorites(coffee);
        }
    };

    const handleTogglePrivacy = async (coffee) => {
        try {
            const response = await authenticatedFetch(`${API_URL}/privacy/${coffee.id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to toggle privacy' }));
                const errorMessage = errorData.detail || errorData.error || 'Failed to toggle privacy';
                console.error('Privacy toggle error:', errorMessage, errorData);
                throw new Error(errorMessage);
            }

            const data = await response.json();
            
            // Refresh data to get updated privacy status
            if (fetchData) {
                await fetchData();
            }
            
            setMessage({ 
                type: 'success', 
                text: data.message || (data.is_private ? 'Recipe is now private' : 'Recipe is now public')
            });
        } catch (err) {
            console.error('Error toggling privacy:', err);
            setMessage({ 
                type: 'error', 
                text: err.message || 'Failed to update privacy. Please try again.' 
            });
        }
    };

    useEffect(() => {
        if (message) {
            const timer = setTimeout(() => setMessage(null), 5000);
            return () => clearTimeout(timer);
        }
    }, [message]);

    return (
        <div className={styles.container}>
            <h2 className={styles.title}>My Recipes & Favorites</h2>

            {message && (
                <div className={`${styles.message} ${styles[message.type]}`}>
                    {message.text}
                </div>
            )}

            <div className={styles.tabs}>
                <button
                    className={`${styles.tab} ${activeTab === 'my-recipes' ? styles.activeTab : ''}`}
                    onClick={() => setActiveTab('my-recipes')}
                >
                    My Recipes ({myRecipes.length})
                </button>
                <button
                    className={`${styles.tab} ${activeTab === 'favorites' ? styles.activeTab : ''}`}
                    onClick={() => setActiveTab('favorites')}
                >
                    Favorites ({favoritesList.length})
                </button>
            </div>

            {activeTab === 'my-recipes' && (
                <div className={styles.section}>
                    <div className={styles.header}>
                        <h3>My Recipes</h3>
                        <button
                            className={styles.addButton}
                            onClick={() => {
                                setShowAddForm(true);
                                setShowEditForm(false);
                                setFormData({ name: '', origin: '', description: '' });
                            }}
                        >
                            + Add New Recipe
                        </button>
                    </div>

                    {(showAddForm || showEditForm) && (
                        <div className={styles.formContainer}>
                            <h4>{showEditForm ? 'Edit Recipe' : 'Add New Recipe'}</h4>
                            <form onSubmit={showEditForm ? handleEditRecipe : handleAddRecipe}>
                                <div className={styles.formGroup}>
                                    <label>Recipe Name *</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        required
                                        placeholder="e.g., Espresso, Latte, Cold Brew"
                                    />
                                </div>
                                <div className={styles.formGroup}>
                                    <label>Origin *</label>
                                    <select
                                        name="origin"
                                        value={formData.origin}
                                        onChange={handleInputChange}
                                        required
                                    >
                                        <option value="">Select an origin...</option>
                                        {origins.map(origin => (
                                            <option key={origin.id} value={origin.name}>
                                                {origin.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className={styles.formGroup}>
                                    <label>Description *</label>
                                    <textarea
                                        name="description"
                                        value={formData.description}
                                        onChange={handleInputChange}
                                        required
                                        rows="4"
                                        placeholder="Describe your coffee recipe..."
                                    />
                                </div>
                                <div className={styles.formActions}>
                                    <button type="submit" className={styles.submitButton}>
                                        {showEditForm ? 'Update Recipe' : 'Add Recipe'}
                                    </button>
                                    <button
                                        type="button"
                                        className={styles.cancelButton}
                                        onClick={handleCancel}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div className={styles.recipesList}>
                        {myRecipes.length === 0 ? (
                            <div className={styles.emptyMessage}>
                                You haven't created any recipes yet. Click "Add New Recipe" to get started!
                            </div>
                        ) : (
                            myRecipes.map(coffee => (
                                <div key={coffee.id} className={styles.recipeCard}>
                                    <div className={styles.recipeHeader}>
                                        <h4>
                                            {coffee.name}
                                            {coffee.is_community_winner && (
                                                <span className={styles.star}> ⭐</span>
                                            )}
                                        </h4>
                                        <div className={styles.recipeActions}>
                                            <button
                                                className={styles.editButton}
                                                onClick={() => handleStartEdit(coffee)}
                                            >
                                                Edit
                                            </button>
                                            <button
                                                className={styles.deleteButton}
                                                onClick={() => handleDeleteRecipe(coffee.id)}
                                            >
                                                Delete
                                            </button>
                                            <button
                                                className={`${styles.privacyButton} ${coffee.is_private ? styles.privacyActive : ''}`}
                                                onClick={() => handleTogglePrivacy(coffee)}
                                                title={coffee.is_private ? "Make public (show in main recipe list)" : "Keep private (hide from main recipe list)"}
                                            >
                                                {coffee.is_private ? 'Private' : 'Public'}
                                            </button>
                                            <button
                                                className={`${styles.favoriteButton} ${isFavorite(coffee.id) ? styles.favoriteActive : ''}`}
                                                onClick={() => handleToggleFavorite(coffee)}
                                                title={isFavorite(coffee.id) ? "Remove from favorites" : "Add to favorites"}
                                            >
                                                {isFavorite(coffee.id) ? '🤎' : '🤍'}
                                            </button>
                                        </div>
                                    </div>
                                    <div className={styles.recipeInfo}>
                                        <div className={styles.origin}>Origin: {coffee.origin.name}</div>
                                        <div className={styles.description}>{coffee.description}</div>
                                        <div className={styles.meta}>
                                            {(coffee.likes_count || 0) > 0 && <span>Likes: {coffee.likes_count}</span>}
                                            <span>Caffeine: ~{coffee.caffeine_mg || 95}mg</span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'favorites' && (
                <div className={styles.section}>
                    <h3>My Favorites</h3>
                    <div className={styles.recipesList}>
                        {favoritesList.length === 0 ? (
                            <div className={styles.emptyMessage}>
                                You don't have any favorite recipes yet. Add recipes to your favorites from Page 2 or your recipe list!
                            </div>
                        ) : (
                            favoritesList.map(coffee => (
                                <div key={coffee.id} className={styles.recipeCard}>
                                    <div className={styles.recipeHeader}>
                                        <h4>
                                            {coffee.name}
                                            {coffee.is_community_winner && (
                                                <span className={styles.star}> ⭐</span>
                                            )}
                                        </h4>
                                        <div className={styles.recipeActions}>
                                            <button
                                                className={`${styles.favoriteButton} ${styles.favoriteActive}`}
                                                onClick={() => handleToggleFavorite(coffee)}
                                                title="Remove from favorites"
                                            >
                                                🤎
                                            </button>
                                        </div>
                                    </div>
                                    <div className={styles.recipeInfo}>
                                        <div className={styles.origin}>Origin: {coffee.origin?.name || 'Unknown'}</div>
                                        <div className={styles.description}>{coffee.description}</div>
                                        <div className={styles.meta}>
                                            {(coffee.likes_count || 0) > 0 && <span>Likes: {coffee.likes_count}</span>}
                                            <span>Caffeine: ~{coffee.caffeine_mg || 95}mg</span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
