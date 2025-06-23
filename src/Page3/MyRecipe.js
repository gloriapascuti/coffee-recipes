import styles from './styles/MyRecipe.module.css'
import React, { useState, useContext, useEffect } from 'react';
import { useHistory } from "react-router-dom";
import { CoffeeContext } from '../CoffeeContext';

const MyRecipe = () => {
    const history = useHistory();
    const { coffees, user, editCoffee, deleteCoffee, addCoffee, favorites, removeFromFavorites } = useContext(CoffeeContext);
    const [showMyRecipes, setShowMyRecipes] = useState(false);
    const [showRecipeBuilder, setShowRecipeBuilder] = useState(false);
    const [showFavorites, setShowFavorites] = useState(false);
    const [editingCoffee, setEditingCoffee] = useState(null);
    const [editInput, setEditInput] = useState({
        id: null,
        name: "",
        origin: "",
        description: ""
    });
    
    // Add recipe form state
    const [name, setName] = useState("");
    const [origin, setOrigin] = useState("");
    const [description, setDescription] = useState("");
    
    // Filter coffees by current user
    const userCoffees = coffees.filter(coffee => coffee.user === user?.id);
    
    // Check if user is authenticated
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            history.push('/login');
        }
    }, [history]);
    
    const handleShowRecipes = () => {
        setShowMyRecipes(true);
    };
    
    const handleShowRecipeBuilder = () => {
        setShowRecipeBuilder(true);
    };

    const handleShowFavorites = () => {
        setShowFavorites(true);
    };
    
    const handleBackToCards = () => {
        setShowMyRecipes(false);
        setShowRecipeBuilder(false);
        setShowFavorites(false);
        setEditingCoffee(null); // Clear any editing state when going back
    };

    const handleEdit = (coffee) => {
        setEditingCoffee(coffee.id);
        setEditInput({
            id: coffee.id,
            name: coffee.name,
            origin: coffee.origin.name,
            description: coffee.description
        });
    };

    const handleSaveEdit = async () => {
        try {
            await editCoffee(editInput.id, editInput);
            setEditingCoffee(null);
        } catch (error) {
            console.error('Error updating coffee:', error);
            alert('Failed to update recipe. Please try again.');
        }
    };

    const handleCancelEdit = () => {
        setEditingCoffee(null);
        setEditInput({
            id: null,
            name: "",
            origin: "",
            description: ""
        });
    };

    const handleDelete = async (id, coffeeName) => {
        if (window.confirm(`Are you sure you want to delete "${coffeeName}"? This action cannot be undone.`)) {
            try {
                await deleteCoffee(id);
            } catch (error) {
                console.error('Error deleting coffee:', error);
                alert('Failed to delete recipe. Please try again.');
            }
        }
    };

    const addItem = async () => {
        if (!name || !origin || !description) {
            alert("Please fill in all fields.");
            return;
        }

        try {
            const newItem = { name, origin, description };
            await addCoffee(newItem);
            setName(""); 
            setOrigin(""); 
            setDescription(""); // Clear inputs
            alert("Recipe added successfully!");
        } catch (error) {
            alert("Failed to add coffee recipe. Please try again.");
            console.error("Error adding coffee:", error);
        }
    };

    // Recipe Builder View
    if (showRecipeBuilder) {
        return (
            <div className={styles.container}>
                <div className={styles.content}>
                    <div className={styles.recipeHeader}>
                        <button onClick={handleBackToCards} className={styles.backButton}>
                            ← Back to Overview
                        </button>
                        <h2 className={styles.recipeTitle}>Recipe Builder</h2>
                        <p className={styles.recipeSubtitle}>
                            Create and add your own coffee recipes to your collection
                        </p>
                    </div>
                    
                    <div className={styles.formSection}>
                        <div className={styles.inputGroup}>
                            <label className={styles.subtitle}>Name</label>
                            <input
                                type="text"
                                placeholder="Enter coffee name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className={styles.input}
                            />
                        </div>

                        <div className={styles.inputGroup}>
                            <label className={styles.subtitle}>Origin</label>
                            <input
                                type="text"
                                placeholder="Where is it from?"
                                value={origin}
                                onChange={(e) => setOrigin(e.target.value)}
                                className={styles.input}
                            />
                        </div>

                        <div className={styles.inputGroup}>
                            <label className={styles.subtitle}>Method used/Instructions</label>
                            <textarea
                                placeholder="Describe the preparation"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className={styles.textarea}
                                rows="4"
                            />
                        </div>

                        <button className={styles.addButton} onClick={addItem}>Add recipe</button>
                    </div>
                </div>
            </div>
        );
    }

    // Favorites View
    if (showFavorites) {
        return (
            <div className={styles.container}>
                <div className={styles.content}>
                    <div className={styles.recipeHeader}>
                        <button onClick={handleBackToCards} className={styles.backButton}>
                            ← Back to Overview
                        </button>
                        <h2 className={styles.recipeTitle}>Your Favorite Recipes</h2>
                        <p className={styles.recipeSubtitle}>
                            You have {favorites.length} favorite recipe{favorites.length !== 1 ? 's' : ''}
                        </p>
                    </div>
                    
                    <div className={styles.recipeGrid}>
                        {favorites.length === 0 ? (
                            <div className={styles.emptyState}>
                                <h3>No favorites yet!</h3>
                                <p>Browse recipes on Page 2 and click the heart icon to add them to your favorites.</p>
                            </div>
                        ) : (
                            favorites.map(coffee => (
                                <div key={coffee.id} className={styles.recipeCard}>
                                    <div className={styles.recipeCardHeader}>
                                        <h3 className={styles.recipeName}>{coffee.name}</h3>
                                        <span className={styles.recipeOrigin}>{coffee.origin?.name || 'Unknown Origin'}</span>
                                        <button 
                                            onClick={() => removeFromFavorites(coffee.id)} 
                                            className={styles.removeFavoriteButton}
                                            title="Remove from favorites"
                                        >
                                            🤎
                                        </button>
                                    </div>
                                    <p className={styles.recipeDescription}>
                                        {coffee.description || 'No description available'}
                                    </p>
                                    <div className={styles.recipeFooter}>
                                        <span className={styles.recipeDate}>
                                            Added to favorites
                                        </span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        );
    }

    if (showMyRecipes) {
        return (
            <div className={styles.container}>
                <div className={styles.content}>
                    <div className={styles.recipeHeader}>
                        <button onClick={handleBackToCards} className={styles.backButton}>
                            ← Back to Overview
                        </button>
                        <h2 className={styles.recipeTitle}>Your Recipe Collection</h2>
                        <p className={styles.recipeSubtitle}>
                            You have {userCoffees.length} recipe{userCoffees.length !== 1 ? 's' : ''} in your collection
                        </p>
                    </div>
                    
                    <div className={styles.recipeGrid}>
                        {userCoffees.length === 0 ? (
                            <div className={styles.emptyState}>
                                <h3>No recipes yet!</h3>
                                <p>Use the Recipe Builder to create your first coffee recipe.</p>
                            </div>
                        ) : (
                            userCoffees.map(coffee => (
                                <div key={coffee.id} className={styles.recipeCard}>
                                    {editingCoffee === coffee.id ? (
                                        <div className={styles.editForm}>
                                            <div className={styles.editField}>
                                                <label>Recipe Name:</label>
                                                <input 
                                                    type="text" 
                                                    value={editInput.name} 
                                                    onChange={(e) => setEditInput({ ...editInput, name: e.target.value })}
                                                    className={styles.editInput}
                                                />
                                            </div>
                                            <div className={styles.editField}>
                                                <label>Origin:</label>
                                                <input 
                                                    type="text" 
                                                    value={editInput.origin} 
                                                    onChange={(e) => setEditInput({ ...editInput, origin: e.target.value })}
                                                    className={styles.editInput}
                                                />
                                            </div>
                                            <div className={styles.editField}>
                                                <label>Description:</label>
                                                <textarea 
                                                    value={editInput.description} 
                                                    onChange={(e) => setEditInput({ ...editInput, description: e.target.value })}
                                                    className={styles.editTextarea}
                                                    rows="4"
                                                />
                                            </div>
                                            <div className={styles.editActions}>
                                                <button onClick={handleSaveEdit} className={styles.saveButton}>
                                                    Save Changes
                                                </button>
                                                <button onClick={handleCancelEdit} className={styles.cancelButton}>
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <>
                                            <div className={styles.recipeCardHeader}>
                                                <h3 className={styles.recipeName}>{coffee.name}</h3>
                                                <span className={styles.recipeOrigin}>{coffee.origin?.name || 'Unknown Origin'}</span>
                                            </div>
                                            <p className={styles.recipeDescription}>
                                                {coffee.description || 'No description available'}
                                            </p>
                                            <div className={styles.recipeFooter}>
                                                <span className={styles.recipeDate}>
                                                    Created: {new Date(coffee.created_at || Date.now()).toLocaleDateString()}
                                                </span>
                                                <div className={styles.recipeActions}>
                                                    <button 
                                                        onClick={() => handleEdit(coffee)} 
                                                        className={styles.editButton}
                                                    >
                                                        Edit
                                                    </button>
                                                    <button 
                                                        onClick={() => handleDelete(coffee.id, coffee.name)} 
                                                        className={styles.deleteButton}
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.placeholder}>
                    <div className={styles.placeholderCard} onClick={handleShowRecipes}>
                        <h3>Your Recipe Collection</h3>
                        <p>View and manage your personal coffee recipe library. Edit, delete, and organize your brewing methods.</p>
                        <div className={styles.recipeCount}>
                            {userCoffees.length} recipe{userCoffees.length !== 1 ? 's' : ''}
                        </div>
                        <div className={styles.clickHint}>Click to view →</div>
                    </div>
                    
                    <div className={styles.placeholderCard} onClick={handleShowRecipeBuilder}>
                        <h3>Recipe Builder</h3>
                        <p>Create new coffee recipes with our intuitive form. Document your brewing process, ingredients, and tasting notes.</p>
                        <div className={styles.clickHint}>Click to start →</div>
                    </div>
                    
                    <div className={styles.placeholderCard} onClick={handleShowFavorites}>
                        <h3>Favorite Recipes</h3>
                        <p>Your personal collection of favorite coffee recipes from the community. Easily access your most loved brewing methods.</p>
                        <div className={styles.recipeCount}>
                            {favorites.length} favorite{favorites.length !== 1 ? 's' : ''}
                        </div>
                        <div className={styles.clickHint}>Click to view →</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default MyRecipe