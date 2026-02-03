import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';
import Prediction from './Prediction';
import styles from './styles/ConsumedCoffees.module.css';

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

export default function ConsumedCoffees() {
    const { coffees } = useCoffee();
    const [consumedCoffees, setConsumedCoffees] = useState({
        today: [],
        yesterday: [],
        last_7_days: [],
        last_month: [],
        all: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('today');

    useEffect(() => {
        fetchConsumedCoffees();
    }, []);

    const fetchConsumedCoffees = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/consumed/`, {
                method: 'GET',
                headers: authHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch consumed coffees');
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
            const response = await fetch(`${API_URL}/consumed/${coffeeId}/`, {
                method: 'POST',
                headers: authHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to add consumed coffee');
            }

            // Refresh the list
            fetchConsumedCoffees();
        } catch (err) {
            console.error('Error adding consumed coffee:', err);
            alert('Failed to add coffee. Please try again.');
        }
    };

    const handleRemoveConsumed = async (consumedId) => {
        try {
            const response = await fetch(`${API_URL}/consumed/remove/${consumedId}/`, {
                method: 'DELETE',
                headers: authHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to remove consumed coffee');
            }

            // Refresh the list
            fetchConsumedCoffees();
        } catch (err) {
            console.error('Error removing consumed coffee:', err);
            alert('Failed to remove coffee. Please try again.');
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

    const renderCoffeeList = (coffeeList) => {
        if (coffeeList.length === 0) {
            return <div className={styles.emptyMessage}>No coffees consumed in this period</div>;
        }

        return (
            <div className={styles.coffeeList}>
                {coffeeList.map((consumed) => (
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
                        <button
                            className={styles.removeButton}
                            onClick={() => handleRemoveConsumed(consumed.id)}
                        >
                            Remove
                        </button>
                    </div>
                ))}
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

                {renderCoffeeList(getCurrentList())}
            </div>

            <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Add Coffee from Recipes</h2>
                <div className={styles.addCoffeeSection}>
                    <p className={styles.helpText}>
                        Select a coffee recipe below to add it to your consumed list:
                    </p>
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
                </div>
            </div>

            <Prediction consumedCoffees={consumedCoffees} />
        </div>
    );
}
