import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';
import Prediction from './Prediction';
import styles from './styles/ConsumedCoffees.module.css';

const API_URL = 'http://127.0.0.1:8000/api';

export default function ConsumedCoffees() {
    const { coffees, authenticatedFetch, userId, addCoffee, fetchData } = useCoffee();
    const [consumedCoffees, setConsumedCoffees] = useState({
        today: [],
        yesterday: [],
        last_7_days: [],
        last_month: [],
        all: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [activeTab, setActiveTab] = useState('today');
    const [showCustomForm, setShowCustomForm] = useState(false);
    const [customFormData, setCustomFormData] = useState({
        name: '',
        origin: '',
        description: '',
        inputType: 'grams', // 'grams' or 'caffeine'
        grams: '',
        caffeine_mg: '',
        coffee_type: ''
    });
    const [calculatedCaffeine, setCalculatedCaffeine] = useState(null);
    const [myRecipes, setMyRecipes] = useState([]);

    useEffect(() => {
        fetchConsumedCoffees();
        fetchMyRecipes();
    }, []);

    // Refresh my recipes when userId changes or when coffees are updated
    useEffect(() => {
        if (userId && authenticatedFetch) {
            fetchMyRecipes();
        }
    }, [userId, coffees.length]);

    const fetchMyRecipes = async () => {
        if (!userId || !authenticatedFetch) return;
        
        try {
            const response = await authenticatedFetch(`${API_URL}/my-recipes/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const recipes = await response.json();
                setMyRecipes(recipes);
            }
        } catch (err) {
            console.error('Error fetching my recipes:', err);
        }
    };

    const fetchConsumedCoffees = async () => {
        try {
            setLoading(true);
            const response = await authenticatedFetch(`${API_URL}/consumed/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch consumed coffees' }));
                throw new Error(errorData.detail || errorData.error || 'Failed to fetch consumed coffees');
            }

            const data = await response.json();
            setConsumedCoffees(data);
            setError(null);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching consumed coffees:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddConsumed = async (coffeeId) => {
        try {
            const response = await authenticatedFetch(`${API_URL}/consumed/${coffeeId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to add consumed coffee' }));
                throw new Error(errorData.detail || errorData.error || 'Failed to add consumed coffee');
            }

            // Refresh the list
            await fetchConsumedCoffees();
            setSuccess('Coffee added successfully!');
            setTimeout(() => setSuccess(null), 3000); // Clear success after 3 seconds
        } catch (err) {
            console.error('Error adding consumed coffee:', err);
            setError(err.message || 'Failed to add coffee. Please try again.');
            setTimeout(() => setError(null), 5000); // Clear error after 5 seconds
        }
    };

    const handleRemoveConsumed = async (consumedId) => {
        try {
            const response = await authenticatedFetch(`${API_URL}/consumed/remove/${consumedId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to remove consumed coffee');
            }

            // Refresh the list
            fetchConsumedCoffees();
        } catch (err) {
            console.error('Error removing consumed coffee:', err);
            setError(err.message || 'Failed to remove coffee. Please try again.');
            setTimeout(() => setError(null), 5000);
        }
    };

    const handleAddToRecipeList = async (consumedCoffee) => {
        try {
            // Check if coffee is already in the user's recipe list
            const coffee = consumedCoffee.coffee;
            
            // Check if this coffee already exists in user's recipes
            const existingCoffee = coffees.find(c => 
                c.name === coffee.name && 
                c.user === userId &&
                c.origin?.name === coffee.origin?.name
            );
            
            if (existingCoffee) {
                setSuccess('This recipe is already in your recipe list!');
                setTimeout(() => setSuccess(null), 3000);
                return;
            }
            
            // Add the coffee to user's recipe list
            await addCoffee({
                name: coffee.name,
                origin: coffee.origin?.name || coffee.origin,
                description: coffee.description || ''
            });
            
            // Refresh data to show updated list
            if (fetchData) {
                await fetchData();
            }
            
            // Refresh my recipes to update the button visibility
            await fetchMyRecipes();
            
            setSuccess('Recipe added to your recipe list!');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            console.error('Error adding to recipe list:', err);
            setError(err.message || 'Failed to add recipe to your list. Please try again.');
            setTimeout(() => setError(null), 5000);
        }
    };

    const calculateCaffeineFromGrams = (grams, coffeeType) => {
        // Formula: Caffeine (mg) = 1000 x D x G x R x B
        // D = dose in grams, G = 0.012 (1.2%), R = 1.15, B = brew method factor
        const G = 0.012; // 1.2% green coffee caffeine
        const R = 1.15;  // Roast adjustment factor
        
        // Determine brew method factor
        const coffeeTypeLower = (coffeeType || '').toLowerCase();
        let B = 0.85; // Default
        
        if (coffeeTypeLower.includes('cold brew')) {
            B = 1.0;
        } else if (coffeeTypeLower.includes('filter') || coffeeTypeLower.includes('v60') || coffeeTypeLower.includes('pour over')) {
            B = 0.9;
        } else if (coffeeTypeLower.includes('espresso') || coffeeTypeLower.includes('mocha') || 
                   coffeeTypeLower.includes('cappuccino') || coffeeTypeLower.includes('latte') ||
                   coffeeTypeLower.includes('americano') || coffeeTypeLower.includes('macchiato')) {
            B = 0.8;
        }
        
        const caffeine = 1000 * parseFloat(grams) * G * R * B;
        return Math.round(caffeine * 10) / 10; // Round to 1 decimal place
    };

    const handleCustomFormChange = (e) => {
        const { name, value } = e.target;
        setCustomFormData(prev => {
            const updated = { ...prev, [name]: value };
            
            // Auto-calculate caffeine if grams and coffee type are provided
            if (name === 'grams' || name === 'coffee_type' || name === 'name') {
                if (updated.inputType === 'grams' && updated.grams && (updated.coffee_type || updated.name)) {
                    const coffeeType = updated.coffee_type || updated.name;
                    const calculated = calculateCaffeineFromGrams(updated.grams, coffeeType);
                    setCalculatedCaffeine(calculated);
                } else {
                    setCalculatedCaffeine(null);
                }
            }
            
            return updated;
        });
    };

    const handleInputTypeChange = (e) => {
        setCustomFormData(prev => ({ ...prev, inputType: e.target.value, grams: '', caffeine_mg: '' }));
        setCalculatedCaffeine(null);
    };

    const handleCustomFormSubmit = async (e) => {
        e.preventDefault();
        
        if (!customFormData.name || !customFormData.origin) {
            setError('Name and origin are required');
            setTimeout(() => setError(null), 5000);
            return;
        }
        
        if (customFormData.inputType === 'grams' && !customFormData.grams) {
            setError('Please enter grams of coffee beans');
            setTimeout(() => setError(null), 5000);
            return;
        }
        
        if (customFormData.inputType === 'caffeine' && !customFormData.caffeine_mg) {
            setError('Please enter caffeine content in mg');
            setTimeout(() => setError(null), 5000);
            return;
        }
        
        try {
            const payload = {
                name: customFormData.name,
                origin: customFormData.origin,
                description: customFormData.description || '',
                coffee_type: customFormData.coffee_type || customFormData.name
            };
            
            if (customFormData.inputType === 'grams') {
                payload.grams = parseFloat(customFormData.grams);
            } else {
                payload.caffeine_mg = parseFloat(customFormData.caffeine_mg);
            }
            
            const response = await authenticatedFetch(`${API_URL}/consumed/custom/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to add custom coffee' }));
                throw new Error(errorData.detail || errorData.error || 'Failed to add custom coffee');
            }
            
            // Reset form
            setCustomFormData({
                name: '',
                origin: '',
                description: '',
                inputType: 'grams',
                grams: '',
                caffeine_mg: '',
                coffee_type: ''
            });
            setCalculatedCaffeine(null);
            setShowCustomForm(false);
            
            // Refresh the list
            await fetchConsumedCoffees();
            setSuccess('Custom coffee added successfully!');
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            console.error('Error adding custom coffee:', err);
            setError(err.message || 'Failed to add custom coffee. Please try again.');
            setTimeout(() => setError(null), 5000);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const isRecipeInMyList = (coffee) => {
        // Check if this coffee already exists in user's recipe list
        return myRecipes.some(recipe => {
            const recipeUserId = typeof recipe.user === 'object' ? recipe.user.id : recipe.user;
            const coffeeUserId = typeof coffee.user === 'object' ? coffee.user.id : coffee.user;
            return recipe.name === coffee.name && 
                   recipeUserId === userId &&
                   coffeeUserId === userId &&
                   (recipe.origin?.name === coffee.origin?.name || 
                    (typeof recipe.origin === 'string' && recipe.origin === coffee.origin?.name));
        });
    };

    const renderCoffeeList = (coffeeList) => {
        if (coffeeList.length === 0) {
            return <div className={styles.emptyMessage}>No coffees consumed in this period</div>;
        }

        return (
            <div className={styles.coffeeList}>
                {coffeeList.map((consumed) => {
                    // Check if this is a custom recipe (created by the current user)
                    const isCustomRecipe = consumed.coffee.user === userId;
                    // Check if recipe is already in user's recipe list
                    const alreadyInList = isRecipeInMyList(consumed.coffee);
                    
                    return (
                        <div key={consumed.id} className={styles.coffeeCard}>
                            <div className={styles.coffeeInfo}>
                                <h3>{consumed.coffee.name}</h3>
                                <p className={styles.coffeeOrigin}>{consumed.coffee.origin.name}</p>
                                <p className={styles.coffeeDescription}>{consumed.coffee.description}</p>
                                <p className={styles.caffeineInfo}>
                                    Caffeine: ~{consumed.coffee.caffeine_mg || 95}mg
                                </p>
                                <p className={styles.consumedTime}>
                                    Consumed: {formatDate(consumed.consumed_at)}
                                </p>
                            </div>
                            <div className={styles.cardActions}>
                                {isCustomRecipe && !alreadyInList && (
                                    <button
                                        className={styles.addToRecipeButton}
                                        onClick={() => handleAddToRecipeList(consumed)}
                                        title="Add to My Recipes"
                                    >
                                        Add to Recipe List
                                    </button>
                                )}
                                <button
                                    className={styles.removeButton}
                                    onClick={() => handleRemoveConsumed(consumed.id)}
                                >
                                    Remove
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>
        );
    };

    const getCurrentList = () => {
        switch (activeTab) {
            case 'today':
                return consumedCoffees.today;
            case 'yesterday':
                return consumedCoffees.yesterday;
            case 'last_7_days':
                return consumedCoffees.last_7_days;
            case 'last_month':
                return consumedCoffees.last_month;
            default:
                return [];
        }
    };

    if (loading) {
        return <div className={styles.loading}>Loading consumed coffees...</div>;
    }

    return (
        <div className={styles.container}>
            <div className={styles.section}>
                <h2 className={styles.sectionTitle}>My Consumed Coffees</h2>
                
                <div className={styles.tabs}>
                    <button
                        className={`${styles.tab} ${activeTab === 'today' ? styles.activeTab : ''}`}
                        onClick={() => setActiveTab('today')}
                    >
                        Today ({consumedCoffees.today.length})
                    </button>
                    <button
                        className={`${styles.tab} ${activeTab === 'yesterday' ? styles.activeTab : ''}`}
                        onClick={() => setActiveTab('yesterday')}
                    >
                        Yesterday ({consumedCoffees.yesterday.length})
                    </button>
                    <button
                        className={`${styles.tab} ${activeTab === 'last_7_days' ? styles.activeTab : ''}`}
                        onClick={() => setActiveTab('last_7_days')}
                    >
                        Last 7 Days ({consumedCoffees.last_7_days.length})
                    </button>
                    <button
                        className={`${styles.tab} ${activeTab === 'last_month' ? styles.activeTab : ''}`}
                        onClick={() => setActiveTab('last_month')}
                    >
                        Last Month ({consumedCoffees.last_month.length})
                    </button>
                </div>

                {error && <div className={styles.error}>{error}</div>}
                {success && <div className={styles.success}>{success}</div>}

                {renderCoffeeList(getCurrentList())}
            </div>

            <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Add Coffee from Recipes</h2>
                <div className={styles.addCoffeeSection}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <p className={styles.helpText} style={{ margin: 0 }}>
                            Select a coffee recipe below to add it to your consumed list:
                        </p>
                        <button
                            className={styles.addButton}
                            onClick={() => setShowCustomForm(!showCustomForm)}
                            style={{ width: 'auto', padding: '0.5rem 1rem' }}
                        >
                            {showCustomForm ? 'Cancel' : '+ Add Custom Recipe'}
                        </button>
                    </div>
                    
                    {showCustomForm && (
                        <div className={styles.customForm}>
                            <h3 style={{ marginBottom: '1rem', color: '#333' }}>Add Custom Recipe</h3>
                            <form onSubmit={handleCustomFormSubmit}>
                                <div className={styles.formGroup}>
                                    <label>Recipe Name *</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={customFormData.name}
                                        onChange={handleCustomFormChange}
                                        required
                                        placeholder="e.g., My Custom Cold Brew"
                                    />
                                </div>
                                
                                <div className={styles.formGroup}>
                                    <label>Origin *</label>
                                    <input
                                        type="text"
                                        name="origin"
                                        value={customFormData.origin}
                                        onChange={handleCustomFormChange}
                                        required
                                        placeholder="e.g., Colombia"
                                    />
                                </div>
                                
                                <div className={styles.formGroup}>
                                    <label>Description</label>
                                    <textarea
                                        name="description"
                                        value={customFormData.description}
                                        onChange={handleCustomFormChange}
                                        placeholder="Optional description"
                                        rows="3"
                                    />
                                </div>
                                
                                <div className={styles.formGroup}>
                                    <label>Caffeine Input Method *</label>
                                    <select
                                        name="inputType"
                                        value={customFormData.inputType}
                                        onChange={handleInputTypeChange}
                                    >
                                        <option value="grams">Calculate from grams of coffee beans</option>
                                        <option value="caffeine">Enter caffeine directly (mg)</option>
                                    </select>
                                </div>
                                
                                {customFormData.inputType === 'grams' ? (
                                    <>
                                        <div className={styles.formGroup}>
                                            <label>Coffee Type (for brew method calculation)</label>
                                            <select
                                                name="coffee_type"
                                                value={customFormData.coffee_type}
                                                onChange={handleCustomFormChange}
                                            >
                                                <option value="">Auto-detect from name</option>
                                                <option value="Cold Brew">Cold Brew</option>
                                                <option value="Filter">Filter/V60</option>
                                                <option value="Espresso">Espresso</option>
                                                <option value="Mocha">Mocha</option>
                                                <option value="Cappuccino">Cappuccino</option>
                                                <option value="Latte">Latte</option>
                                                <option value="Americano">Americano</option>
                                            </select>
                                        </div>
                                        
                                        <div className={styles.formGroup}>
                                            <label>Grams of Coffee Beans *</label>
                                            <input
                                                type="number"
                                                name="grams"
                                                value={customFormData.grams}
                                                onChange={handleCustomFormChange}
                                                required
                                                min="0"
                                                step="0.1"
                                                placeholder="e.g., 20"
                                            />
                                            {calculatedCaffeine && (
                                                <p style={{ marginTop: '0.5rem', color: '#8B4513', fontSize: '0.9rem' }}>
                                                    Calculated caffeine: ~{calculatedCaffeine}mg
                                                </p>
                                            )}
                                        </div>
                                    </>
                                ) : (
                                    <div className={styles.formGroup}>
                                        <label>Caffeine Content (mg) *</label>
                                        <input
                                            type="number"
                                            name="caffeine_mg"
                                            value={customFormData.caffeine_mg}
                                            onChange={handleCustomFormChange}
                                            required
                                            min="0"
                                            step="0.1"
                                            placeholder="e.g., 185"
                                        />
                                    </div>
                                )}
                                
                                <div className={styles.formActions}>
                                    <button type="submit" className={styles.submitButton}>
                                        Add to Consumed
                                    </button>
                                    <button
                                        type="button"
                                        className={styles.cancelButton}
                                        onClick={() => {
                                            setShowCustomForm(false);
                                            setCustomFormData({
                                                name: '',
                                                origin: '',
                                                description: '',
                                                inputType: 'grams',
                                                grams: '',
                                                caffeine_mg: '',
                                                coffee_type: ''
                                            });
                                            setCalculatedCaffeine(null);
                                        }}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}
                    
                    {!showCustomForm && (
                        <div className={styles.recipeGrid}>
                            {coffees.slice(0, 20).map((coffee) => (
                                <div key={coffee.id} className={styles.recipeCard}>
                                    <h4>{coffee.name}</h4>
                                    <p className={styles.recipeOrigin}>{coffee.origin.name}</p>
                                    <button
                                        className={styles.addButton}
                                        onClick={() => handleAddConsumed(coffee.id)}
                                    >
                                        + Add to Consumed
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <Prediction consumedCoffees={consumedCoffees} />
        </div>
    );
}
