import React, { useState, useEffect } from 'react';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement, Filler } from 'chart.js';
import { useCoffee } from '../CoffeeContext';
import styles from './styles/PredictionCharts.module.css';

const API_URL = 'http://127.0.0.1:8000/api';

ChartJS.register(
    CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
    ArcElement, PointElement, LineElement, Filler
);

export default function PredictionCharts({ prediction, period, consumedCoffees }) {
    const { authenticatedFetch } = useCoffee();
    const [caffeineHistory, setCaffeineHistory] = useState(null);
    const [bpHistory, setBpHistory] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchChartData();
    }, [period]);

    const fetchChartData = async () => {
        try {
            setLoading(true);
            
            // Fetch consumed coffees for the period to build daily caffeine chart
            const now = new Date();
            let daysBack = 7;
            if (period === 'month') daysBack = 30;
            else if (period === 'year') daysBack = 365;
            
            const startDate = new Date(now);
            startDate.setDate(startDate.getDate() - daysBack);
            
            // Group consumed coffees by date
            // consumedCoffees can have structure: {today: [], yesterday: [], last_7_days: [], last_month: [], all: []}
            const allConsumed = consumedCoffees?.all || 
                               consumedCoffees?.last_7_days || 
                               consumedCoffees?.last_month || 
                               [];
            
            if (allConsumed.length > 0) {
                const dailyCaffeine = {};
                allConsumed.forEach(consumed => {
                    const consumedDate = new Date(consumed.consumed_at);
                    if (consumedDate >= startDate) {
                        const date = consumedDate.toLocaleDateString();
                        if (!dailyCaffeine[date]) {
                            dailyCaffeine[date] = 0;
                        }
                        dailyCaffeine[date] += consumed.coffee?.caffeine_mg || 95;
                    }
                });
                
                const sortedDates = Object.keys(dailyCaffeine).sort((a, b) => 
                    new Date(a) - new Date(b)
                );
                
                setCaffeineHistory({
                    labels: sortedDates,
                    values: sortedDates.map(date => dailyCaffeine[date])
                });
            }
            
            // Fetch BP history
            try {
                const bpResponse = await authenticatedFetch(`${API_URL}/blood-pressure/list/`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (bpResponse.ok) {
                    const contentType = bpResponse.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        const bpData = await bpResponse.json();
                        const recentBp = bpData
                            .filter(entry => new Date(entry.measured_at) >= startDate)
                            .sort((a, b) => new Date(a.measured_at) - new Date(b.measured_at))
                            .slice(-30); // Last 30 readings
                        
                        setBpHistory(recentBp);
                    }
                }
            } catch (bpError) {
                console.warn('Could not fetch BP history for charts:', bpError);
                // Non-critical, continue without BP chart
            }
        } catch (error) {
            console.error('Error fetching chart data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (!prediction) return null;

    // Chart 1: Daily Caffeine Consumption Trend
    const dailyCaffeineData = caffeineHistory ? {
        labels: caffeineHistory.labels.map(date => {
            const d = new Date(date);
            return `${d.getMonth() + 1}/${d.getDate()}`;
        }),
        datasets: [{
            label: 'Daily Caffeine (mg)',
            data: caffeineHistory.values,
            borderColor: '#8B4513',
            backgroundColor: 'rgba(139, 69, 19, 0.1)',
            fill: true,
            tension: 0.4,
            borderWidth: 2
        }, {
            label: 'Safe Limit (400mg)',
            data: new Array(caffeineHistory.values.length).fill(400),
            borderColor: '#4caf50',
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 0
        }]
    } : null;

    // Chart 2: Caffeine vs Safe Limits
    const safeLimitData = {
        labels: ['Your Average', 'Recommended Max'],
        datasets: [{
            label: 'Caffeine (mg/day)',
            data: [
                prediction.caffeine_stats.avg_daily_mg,
                400 // FDA recommended safe limit
            ],
            backgroundColor: [
                prediction.caffeine_stats.avg_daily_mg > 400 ? '#f44336' : '#8B4513',
                '#4caf50'
            ],
            borderColor: [
                prediction.caffeine_stats.avg_daily_mg > 400 ? '#d32f2f' : '#6B3410',
                '#2e7d32'
            ],
            borderWidth: 2
        }]
    };

    // Chart 3: Coffee Types Distribution (if we have consumed coffees data)
    const allConsumed = consumedCoffees?.all || 
                       consumedCoffees?.last_7_days || 
                       consumedCoffees?.last_month || 
                       [];
    
    const coffeeTypesData = allConsumed.length > 0 ? (() => {
        const typeCounts = {};
        allConsumed.forEach(consumed => {
            const type = consumed.coffee?.name || 'Unknown';
            if (!typeCounts[type]) {
                typeCounts[type] = { count: 0, caffeine: 0 };
            }
            typeCounts[type].count++;
            typeCounts[type].caffeine += consumed.coffee?.caffeine_mg || 95;
        });
        
        const sortedTypes = Object.entries(typeCounts)
            .sort((a, b) => b[1].caffeine - a[1].caffeine)
            .slice(0, 8); // Top 8 types
        
        return {
            labels: sortedTypes.map(([type]) => type),
            datasets: [{
                label: 'Caffeine Contribution (mg)',
                data: sortedTypes.map(([, data]) => data.caffeine),
                backgroundColor: [
                    '#8B4513', '#A0522D', '#CD853F', '#D2691E',
                    '#DEB887', '#F4A460', '#D2B48C', '#BC8F8F'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        };
    })() : null;

    // Chart 4: Risk Factors Breakdown (if we have health profile data)
    const riskFactorsData = prediction.risk_factors ? {
        labels: Object.keys(prediction.risk_factors),
        datasets: [{
            label: 'Risk Contribution (%)',
            data: Object.values(prediction.risk_factors),
            backgroundColor: [
                '#8B4513', '#A0522D', '#CD853F', '#D2691E',
                '#DEB887', '#F4A460'
            ],
            borderColor: '#fff',
            borderWidth: 2
        }]
    } : null;

    // Chart 5: Blood Pressure Trend
    const bpTrendData = bpHistory && bpHistory.length > 0 ? {
        labels: bpHistory.map(entry => {
            const d = new Date(entry.measured_at);
            return `${d.getMonth() + 1}/${d.getDate()}`;
        }),
        datasets: [
            {
                label: 'Systolic',
                data: bpHistory.map(entry => entry.systolic),
                borderColor: '#f44336',
                backgroundColor: 'rgba(244, 67, 54, 0.1)',
                fill: false,
                tension: 0.4,
                borderWidth: 2
            },
            {
                label: 'Diastolic',
                data: bpHistory.map(entry => entry.diastolic),
                borderColor: '#ff9800',
                backgroundColor: 'rgba(255, 152, 0, 0.1)',
                fill: false,
                tension: 0.4,
                borderWidth: 2
            },
            {
                label: 'Normal Range (120/80)',
                data: new Array(bpHistory.length).fill(120),
                borderColor: '#4caf50',
                borderDash: [5, 5],
                borderWidth: 1,
                pointRadius: 0
            }
        ]
    } : null;

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        family: 'Georgia, serif',
                        size: 12
                    }
                }
            },
            title: {
                display: true,
                font: {
                    family: 'Georgia, serif',
                    size: 16,
                    weight: 'bold'
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        family: 'Georgia, serif'
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        family: 'Georgia, serif'
                    }
                }
            }
        }
    };

    if (loading) {
        return <div className={styles.loading}>Loading charts...</div>;
    }

    return (
        <div className={styles.chartsContainer}>
            <h3 className={styles.sectionTitle}>Prediction Analytics</h3>
            
            <div className={styles.chartsGrid}>
                {/* Daily Caffeine Trend */}
                {dailyCaffeineData && (
                    <div className={styles.chartCard}>
                        <h4>Daily Caffeine Consumption Trend</h4>
                        <div className={styles.chartWrapper}>
                            <Line 
                                data={dailyCaffeineData} 
                                options={{
                                    ...chartOptions,
                                    plugins: {
                                        ...chartOptions.plugins,
                                        title: {
                                            ...chartOptions.plugins.title,
                                            text: 'Daily Caffeine Intake Over Time'
                                        }
                                    }
                                }}
                            />
                        </div>
                        <p className={styles.chartNote}>
                            Green dashed line shows the recommended daily limit (400mg)
                        </p>
                    </div>
                )}

                {/* Caffeine vs Safe Limits */}
                <div className={styles.chartCard}>
                    <h4>Caffeine vs Safe Limits</h4>
                    <div className={styles.chartWrapper}>
                        <Bar 
                            data={safeLimitData} 
                            options={{
                                ...chartOptions,
                                plugins: {
                                    ...chartOptions.plugins,
                                    title: {
                                        ...chartOptions.plugins.title,
                                        text: 'Your Average vs Recommended Maximum'
                                    }
                                }
                            }}
                        />
                    </div>
                    <p className={styles.chartNote}>
                        {prediction.caffeine_stats.avg_daily_mg > 400 
                            ? '⚠️ Your average exceeds the recommended safe limit'
                            : '✓ Your average is within safe limits'}
                    </p>
                </div>

                {/* Coffee Types Distribution */}
                {coffeeTypesData && (
                    <div className={styles.chartCard}>
                        <h4>Top Coffee Types by Caffeine</h4>
                        <div className={styles.chartWrapper}>
                            <Doughnut 
                                data={coffeeTypesData} 
                                options={{
                                    ...chartOptions,
                                    plugins: {
                                        ...chartOptions.plugins,
                                        title: {
                                            ...chartOptions.plugins.title,
                                            text: 'Caffeine Contribution by Coffee Type'
                                        }
                                    }
                                }}
                            />
                        </div>
                        <p className={styles.chartNote}>
                            Shows which coffee types contribute most to your total caffeine intake
                        </p>
                    </div>
                )}

                {/* Blood Pressure Trend */}
                {bpTrendData && (
                    <div className={styles.chartCard}>
                        <h4>Blood Pressure Trend</h4>
                        <div className={styles.chartWrapper}>
                            <Line 
                                data={bpTrendData} 
                                options={{
                                    ...chartOptions,
                                    plugins: {
                                        ...chartOptions.plugins,
                                        title: {
                                            ...chartOptions.plugins.title,
                                            text: 'Blood Pressure Over Time'
                                        }
                                    }
                                }}
                            />
                        </div>
                        <p className={styles.chartNote}>
                            Track your blood pressure changes over time
                        </p>
                    </div>
                )}

                {/* Risk Factors Breakdown (if available) */}
                {riskFactorsData && (
                    <div className={styles.chartCard}>
                        <h4>Risk Factors Contribution</h4>
                        <div className={styles.chartWrapper}>
                            <Pie 
                                data={riskFactorsData} 
                                options={{
                                    ...chartOptions,
                                    plugins: {
                                        ...chartOptions.plugins,
                                        title: {
                                            ...chartOptions.plugins.title,
                                            text: 'What Contributes to Your Risk'
                                        }
                                    }
                                }}
                            />
                        </div>
                        <p className={styles.chartNote}>
                            Breakdown of factors contributing to your heart disease risk
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
