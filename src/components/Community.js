import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';
import { useHistory } from 'react-router-dom';
import styles from './styles/Community.module.css';

const Community = () => {
    const { user } = useCoffee();
    const [challenges, setChallenges] = useState([]);
    const [notifications, setNotifications] = useState([]);
    const [availableUsers, setAvailableUsers] = useState([]);
    const [activeTab, setActiveTab] = useState('challenges');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Challenge creation form
    const [newChallenge, setNewChallenge] = useState({
        challenged_username: '',
        coffee_type: ''
    });

    // Recipe submission form
    const [recipeForm, setRecipeForm] = useState({
        name: '',
        origin: { name: '' },
        description: ''
    });

    const [selectedChallenge, setSelectedChallenge] = useState(null);

    useEffect(() => {
        console.log('Community component mounted');
        console.log('Current user:', user);
        console.log('Access token in localStorage:', localStorage.getItem('access_token'));
        
        fetchChallenges();
        fetchNotifications();
        fetchAvailableUsers();
    }, []);

    const fetchChallenges = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/challenges/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setChallenges(data);
            }
        } catch (error) {
            console.error('Error fetching challenges:', error);
        }
    };

    const fetchNotifications = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/notifications/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setNotifications(data);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    };

    const fetchAvailableUsers = async () => {
        try {
            console.log('Fetching available users...');
            const token = localStorage.getItem('access_token');
            console.log('Token exists:', !!token);
            
            const response = await fetch('http://127.0.0.1:8000/api/available-users/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Available users data:', data);
                setAvailableUsers(data);
            } else {
                const errorText = await response.text();
                console.error('Error response:', errorText);
            }
        } catch (error) {
            console.error('Error fetching available users:', error);
        }
    };

    const handleCreateChallenge = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const response = await fetch('http://127.0.0.1:8000/api/challenges/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(newChallenge)
            });

            if (response.ok) {
                setSuccess('Challenge created successfully!');
                setNewChallenge({ challenged_username: '', coffee_type: '' });
                fetchChallenges();
                fetchAvailableUsers();
            } else {
                const data = await response.json();
                setError(data.error || 'Failed to create challenge');
            }
        } catch (error) {
            setError('Error creating challenge');
        } finally {
            setLoading(false);
        }
    };

    const handleRespondToChallenge = async (challengeId, response) => {
        try {
            const result = await fetch(`http://127.0.0.1:8000/api/challenges/${challengeId}/respond/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({ response })
            });

            if (result.ok) {
                setSuccess(`Challenge ${response}ed successfully!`);
                fetchChallenges();
                fetchNotifications();
                fetchAvailableUsers();
            } else {
                const data = await result.json();
                setError(data.error || `Failed to ${response} challenge`);
            }
        } catch (error) {
            setError(`Error ${response}ing challenge`);
        }
    };

    const handleSubmitRecipe = async (e) => {
        e.preventDefault();
        if (!selectedChallenge) return;

        setLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/challenges/${selectedChallenge}/submit-recipe/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(recipeForm)
            });

            if (response.ok) {
                setSuccess('Recipe submitted successfully!');
                setRecipeForm({ name: '', origin: { name: '' }, description: '' });
                setSelectedChallenge(null);
                fetchChallenges();
            } else {
                const data = await response.json();
                setError(data.error || 'Failed to submit recipe');
            }
        } catch (error) {
            setError('Error submitting recipe');
        } finally {
            setLoading(false);
        }
    };

    const handleVote = async (challengeId, votedFor) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/challenges/${challengeId}/vote/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({ voted_for: votedFor })
            });

            if (response.ok) {
                setSuccess('Vote cast successfully!');
                fetchChallenges();
            } else {
                const data = await response.json();
                setError(data.error || 'Failed to vote');
            }
        } catch (error) {
            setError('Error voting');
        }
    };

    const markNotificationAsRead = async (notificationId) => {
        try {
            await fetch(`http://127.0.0.1:8000/api/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            fetchNotifications();
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'pending': return '#ffa500';
            case 'accepted': return '#8faa54';
            case 'declined': return '#f44336';
            case 'voting': return '#8B4513';
            case 'completed': return '#D2691E';
            default: return '#666';
        }
    };

    const renderChallengeCard = (challenge) => (
        <div key={challenge.id} className={styles.challengeCard}>
            <div className={styles.challengeHeader}>
                <h3>{challenge.challenger.username} vs {challenge.challenged.username}</h3>
                <span 
                    className={styles.status}
                    style={{ backgroundColor: getStatusColor(challenge.status) }}
                >
                    {challenge.status.toUpperCase()}
                </span>
            </div>
            <p><strong>Coffee Type:</strong> {challenge.coffee_type}</p>
            <p><strong>Created:</strong> {new Date(challenge.created_at).toLocaleDateString()}</p>
            
            {challenge.status === 'pending' && challenge.challenged.username === user?.username && (
                <div className={styles.challengeActions}>
                    <button 
                        onClick={() => handleRespondToChallenge(challenge.id, 'accept')}
                        className={styles.acceptButton}
                    >
                        Accept
                    </button>
                    <button 
                        onClick={() => handleRespondToChallenge(challenge.id, 'decline')}
                        className={styles.declineButton}
                    >
                        Decline
                    </button>
                </div>
            )}

            {challenge.status === 'accepted' && 
             (challenge.challenger.username === user?.username || challenge.challenged.username === user?.username) && (
                <div className={styles.challengeActions}>
                    <button 
                        onClick={() => setSelectedChallenge(challenge.id)}
                        className={styles.submitButton}
                    >
                        Submit Recipe
                    </button>
                </div>
            )}

            {challenge.status === 'voting' && (
                <div>
                    <h4>Recipes:</h4>
                    <div className={styles.recipesContainer}>
                        {challenge.recipes.map(recipe => (
                            <div key={recipe.id} className={styles.recipeCard}>
                                <h5>{recipe.name}</h5>
                                <p><strong>By:</strong> {recipe.user.username}</p>
                                <p><strong>Origin:</strong> {recipe.origin.name}</p>
                                <p>{recipe.description}</p>
                                
                                {challenge.can_vote && (
                                    <button 
                                        onClick={() => handleVote(challenge.id, recipe.user.username)}
                                        className={styles.voteButton}
                                    >
                                        Vote for this recipe
                                    </button>
                                )}
                                
                                {challenge.user_vote === recipe.user.username && (
                                    <span className={styles.votedIndicator}>✓ You voted for this</span>
                                )}
                            </div>
                        ))}
                    </div>
                    <div className={styles.voteStats}>
                        <p><strong>Votes:</strong> {challenge.challenger.username}: {challenge.challenger_votes} | 
                           {challenge.challenged.username}: {challenge.challenged_votes}</p>
                    </div>
                </div>
            )}

            {challenge.status === 'completed' && (
                <div className={styles.winnerSection}>
                    <h4>🏆 Winner: {challenge.winner.username}</h4>
                    <p>This recipe has been added to the community favorites!</p>
                </div>
            )}
        </div>
    );

    const history = useHistory();

    return (
        <div className={styles.container}>
            <button 
                onClick={() => history.goBack()} 
                className={styles.backButton}
            >
                ← Back
            </button>
            <h1 className={styles.title}>Coffee Community</h1>
            
            {error && <div className={styles.error}>{error}</div>}
            {success && <div className={styles.success}>{success}</div>}

            <div className={styles.tabs}>
                <button 
                    className={`${styles.tab} ${activeTab === 'challenges' ? styles.activeTab : ''}`}
                    onClick={() => setActiveTab('challenges')}
                >
                    Challenges
                </button>
                <button 
                    className={`${styles.tab} ${activeTab === 'notifications' ? styles.activeTab : ''}`}
                    onClick={() => setActiveTab('notifications')}
                >
                    Notifications ({notifications.filter(n => !n.is_read).length})
                </button>
                <button 
                    className={`${styles.tab} ${activeTab === 'create' ? styles.activeTab : ''}`}
                    onClick={() => setActiveTab('create')}
                >
                    Create Challenge
                </button>
            </div>

            {activeTab === 'challenges' && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Community Challenges</h2>
                    <div className={styles.challengesList}>
                        {challenges.length > 0 ? (
                            challenges.map(renderChallengeCard)
                        ) : (
                            <p>No challenges yet. Create the first one!</p>
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'notifications' && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Notifications</h2>
                    <div className={styles.notificationsList}>
                        {notifications.length > 0 ? (
                            notifications.map(notification => {
                                const isWin = notification.notification_type === 'challenge_won';
                                const isLose = notification.notification_type === 'challenge_lost';
                                const getNotificationClass = () => {
                                    let classes = styles.notificationCard;
                                    if (isWin) classes += ` ${styles.winNotification}`;
                                    else if (isLose) classes += ` ${styles.loseNotification}`;
                                    else classes += ` ${notification.is_read ? styles.read : styles.unread}`;
                                    return classes;
                                };
                                
                                return (
                                    <div 
                                        key={notification.id} 
                                        className={getNotificationClass()}
                                        onClick={() => markNotificationAsRead(notification.id)}
                                    >
                                        <p>{notification.message}</p>
                                        <small>{new Date(notification.created_at).toLocaleString()}</small>
                                    </div>
                                );
                            })
                        ) : (
                            <p>No notifications</p>
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'create' && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Create New Challenge</h2>
                    <form onSubmit={handleCreateChallenge} className={styles.challengeForm}>
                        <div className={styles.formGroup}>
                            <label>Challenge User:</label>
                            <select
                                value={newChallenge.challenged_username}
                                onChange={(e) => setNewChallenge({...newChallenge, challenged_username: e.target.value})}
                                required
                            >
                                <option value="">Select a user</option>
                                {availableUsers.map(user => (
                                    <option key={user.id} value={user.username}>
                                        {user.username}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className={styles.formGroup}>
                            <label>Coffee Type:</label>
                            <input
                                type="text"
                                value={newChallenge.coffee_type}
                                onChange={(e) => setNewChallenge({...newChallenge, coffee_type: e.target.value})}
                                placeholder="e.g., Filter coffee, Espresso, Cappuccino"
                                required
                            />
                        </div>
                        <button type="submit" disabled={loading} className={styles.submitButton}>
                            {loading ? 'Creating...' : 'Create Challenge'}
                        </button>
                    </form>
                </div>
            )}

            {selectedChallenge && (
                <div className={styles.modal}>
                    <div className={styles.modalContent}>
                        <h3>Submit Your Recipe</h3>
                        <form onSubmit={handleSubmitRecipe}>
                            <div className={styles.formGroup}>
                                <label>Recipe Name:</label>
                                <input
                                    type="text"
                                    value={recipeForm.name}
                                    onChange={(e) => setRecipeForm({...recipeForm, name: e.target.value})}
                                    required
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label>Origin:</label>
                                <input
                                    type="text"
                                    value={recipeForm.origin.name}
                                    onChange={(e) => setRecipeForm({...recipeForm, origin: { name: e.target.value }})}
                                    required
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label>Description:</label>
                                <textarea
                                    value={recipeForm.description}
                                    onChange={(e) => setRecipeForm({...recipeForm, description: e.target.value})}
                                    rows="4"
                                    required
                                />
                            </div>
                            <div className={styles.modalActions}>
                                <button type="submit" disabled={loading} className={styles.submitButton}>
                                    {loading ? 'Submitting...' : 'Submit Recipe'}
                                </button>
                                <button 
                                    type="button" 
                                    onClick={() => setSelectedChallenge(null)}
                                    className={styles.cancelButton}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Community; 