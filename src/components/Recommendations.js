import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';
import { useHistory } from 'react-router-dom';
import styles from './styles/Recommendations.module.css';

const Recommendations = () => {
    const { coffees, addCoffee } = useCoffee();
    const [selectedAttributes, setSelectedAttributes] = useState({
        origin: [],
        keywords: []
    });
    const [aiInput, setAiInput] = useState('');
    const [recommendations, setRecommendations] = useState([]);
    const [aiRecipe, setAiRecipe] = useState('');
    const [loading, setLoading] = useState(false);
    const [origins, setOrigins] = useState([]);
    const [saveLoading, setSaveLoading] = useState(false);
    const [saveMessage, setSaveMessage] = useState('');

    // Extract unique origins from coffees
    useEffect(() => {
        if (coffees && coffees.length > 0) {
            const uniqueOrigins = [...new Set(coffees.map(coffee => coffee.origin?.name).filter(Boolean))];
            setOrigins(uniqueOrigins);
        }
    }, [coffees]);

    const handleAttributeChange = (type, value) => {
        setSelectedAttributes(prev => ({
            ...prev,
            [type]: prev[type].includes(value) 
                ? prev[type].filter(item => item !== value)
                : [...prev[type], value]
        }));
    };

    const handleRecommend = () => {
        if (!coffees || coffees.length === 0) return;

        let filtered = coffees;

        // Filter by selected origins
        if (selectedAttributes.origin.length > 0) {
            filtered = filtered.filter(coffee => 
                selectedAttributes.origin.includes(coffee.origin?.name)
            );
        }

        // Enhanced filtering by keywords - search more thoroughly in descriptions
        if (selectedAttributes.keywords.length > 0) {
            filtered = filtered.filter(coffee => {
                const searchText = `${coffee.name} ${coffee.description}`.toLowerCase();
                
                return selectedAttributes.keywords.some(keyword => {
                    const keywordLower = keyword.toLowerCase();
                    
                    // Direct match
                    if (searchText.includes(keywordLower)) return true;
                    
                    // Related keyword matching for better description search
                    const keywordMappings = {
                        'strong': ['bold', 'intense', 'robust', 'powerful', 'full-bodied', 'dark'],
                        'mild': ['light', 'gentle', 'smooth', 'soft', 'delicate', 'subtle'],
                        'fruity': ['berry', 'citrus', 'apple', 'cherry', 'tropical', 'sweet'],
                        'bold': ['strong', 'intense', 'robust', 'dark', 'heavy'],
                        'smooth': ['creamy', 'silky', 'mellow', 'balanced', 'refined'],
                        'aromatic': ['fragrant', 'floral', 'perfumed', 'scented'],
                        'creamy': ['smooth', 'milky', 'rich', 'velvety', 'buttery'],
                        'dark': ['strong', 'bold', 'intense', 'roasted', 'deep'],
                        'light': ['mild', 'bright', 'clean', 'crisp', 'fresh'],
                        'sweet': ['honey', 'caramel', 'sugar', 'vanilla', 'chocolate']
                    };
                    
                    // Check if any related keywords are found in the description
                    const relatedKeywords = keywordMappings[keywordLower] || [];
                    return relatedKeywords.some(related => searchText.includes(related));
                });
            });
        }

        // Sort by relevance - coffees with more matching keywords come first
        if (selectedAttributes.keywords.length > 0) {
            filtered.sort((a, b) => {
                const aMatches = selectedAttributes.keywords.filter(keyword => {
                    const searchText = `${a.name} ${a.description}`.toLowerCase();
                    return searchText.includes(keyword.toLowerCase());
                }).length;
                
                const bMatches = selectedAttributes.keywords.filter(keyword => {
                    const searchText = `${b.name} ${b.description}`.toLowerCase();
                    return searchText.includes(keyword.toLowerCase());
                }).length;
                
                return bMatches - aMatches; // Sort by most matches first
            });
        }

        setRecommendations(filtered);
    };

    const handleAIGenerate = async () => {
        if (!aiInput.trim()) return;

        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/generate-ai-recipe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({
                    attributes: aiInput
                })
            });

            if (response.ok) {
                const data = await response.json();
                setAiRecipe(data.recipe);
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.error || 'Failed to generate recipe. Please try again.';
                console.error('Failed to generate AI recipe:', errorMessage);
                setAiRecipe(`Error: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Error generating AI recipe:', error);
            setAiRecipe(`Error generating recipe: ${error.message || 'Please try again.'}`);
        } finally {
            setLoading(false);
        }
    };

    const parseAIRecipe = (recipe) => {
        // Parse the AI recipe text to extract Name, Origin, and Description
        const lines = recipe.split('\n').filter(line => line.trim());
        
        let name = '';
        let origin = '';
        let description = '';
        
        for (const line of lines) {
            if (line.includes('**Name:**')) {
                name = line.replace('**Name:**', '').trim();
            } else if (line.includes('**Origin:**')) {
                origin = line.replace('**Origin:**', '').trim();
                // Extract just the region name (e.g., "Ethiopian Highlands" from "Ethiopian Highlands (Yirgacheffe region)")
                if (origin.includes('(')) {
                    origin = origin.split('(')[0].trim();
                }
            } else if (line.includes('**Description:**')) {
                description = line.replace('**Description:**', '').trim();
            }
        }
        
        return { name, origin, description };
    };

    const handleSaveToList = async () => {
        if (!aiRecipe) return;
        
        setSaveLoading(true);
        setSaveMessage('');
        
        try {
            const parsedRecipe = parseAIRecipe(aiRecipe);
            
            if (!parsedRecipe.name || !parsedRecipe.origin || !parsedRecipe.description) {
                throw new Error('Unable to parse recipe. Please check the format.');
            }
            
            await addCoffee(parsedRecipe);
            setSaveMessage('✓ Coffee recipe saved successfully!');
            
            // Clear the message after 3 seconds
            setTimeout(() => setSaveMessage(''), 3000);
            
        } catch (error) {
            console.error('Error saving coffee:', error);
            setSaveMessage('❌ Failed to save coffee recipe. Please try again.');
            
            // Clear the error message after 5 seconds
            setTimeout(() => setSaveMessage(''), 5000);
        } finally {
            setSaveLoading(false);
        }
    };

    const commonKeywords = ['strong', 'mild', 'fruity', 'bold', 'smooth', 'aromatic', 'creamy', 'dark', 'light', 'sweet'];

    const history = useHistory();

    return (
        <div className={styles.container}>
            <button 
                onClick={() => history.goBack()} 
                className={styles.backButton}
            >
                ← Back
            </button>
            <h1 className={styles.title}>Coffee Recommendations</h1>
            
            <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Find Coffee by Attributes</h2>
                
                {/* Origins */}
                <div className={styles.attributeGroup}>
                    <h3>Origins</h3>
                    <div className={styles.checkboxGroup}>
                        {origins.map(origin => (
                            <label key={origin} className={styles.checkbox}>
                                <input
                                    type="checkbox"
                                    checked={selectedAttributes.origin.includes(origin)}
                                    onChange={() => handleAttributeChange('origin', origin)}
                                />
                                {origin}
                            </label>
                        ))}
                    </div>
                </div>

                {/* Keywords */}
                <div className={styles.attributeGroup}>
                    <h3>Keywords</h3>
                    <div className={styles.checkboxGroup}>
                        {commonKeywords.map(keyword => (
                            <label key={keyword} className={styles.checkbox}>
                                <input
                                    type="checkbox"
                                    checked={selectedAttributes.keywords.includes(keyword)}
                                    onChange={() => handleAttributeChange('keywords', keyword)}
                                />
                                {keyword}
                            </label>
                        ))}
                    </div>
                </div>

                <button onClick={handleRecommend} className={styles.recommendButton}>
                    Recommend
                </button>

                {/* Recommendations Results */}
                {recommendations.length > 0 && (
                    <div className={styles.results}>
                        <h3>Recommended Coffees</h3>
                        <div className={styles.coffeeGrid}>
                            {recommendations.map(coffee => (
                                <div key={coffee.id} className={styles.coffeeCard}>
                                    <h4>
                                        {coffee.name}
                                        {coffee.is_community_winner && <span className={styles.communityWinnerStar}>⭐</span>}
                                    </h4>
                                    <p><strong>Origin:</strong> {coffee.origin?.name}</p>
                                    <p>{coffee.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Generate Recipe with AI</h2>
                <div className={styles.aiSection}>
                    <input
                        type="text"
                        value={aiInput}
                        onChange={(e) => setAiInput(e.target.value)}
                        placeholder="Enter attributes separated by commas (e.g. strong, fruity, espresso)"
                        className={styles.aiInput}
                    />
                    <button 
                        onClick={handleAIGenerate} 
                        disabled={loading}
                        className={styles.aiButton}
                    >
                        {loading ? 'Generating...' : 'Generate with AI'}
                    </button>
                </div>

                {aiRecipe && (
                    <div className={styles.aiResult}>
                        <h3>AI Generated Recipe</h3>
                        <div className={styles.recipeContent}>
                            {aiRecipe}
                        </div>
                        <div className={styles.saveSection}>
                            <button 
                                onClick={handleSaveToList}
                                disabled={saveLoading}
                                className={styles.saveButton}
                            >
                                {saveLoading ? 'Saving...' : 'Add to Coffee List'}
                            </button>
                            {saveMessage && (
                                <div className={styles.saveMessage}>
                                    {saveMessage}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Recommendations; 