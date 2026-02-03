import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useCoffee } from '../CoffeeContext';

export default function UserNotification() {
    const [notification, setNotification] = useState(null);
    const [loading, setLoading] = useState(true);
    const { user, accessToken } = useCoffee();

    useEffect(() => {
        if (user && accessToken) {
            axios
                .get('http://127.0.0.1:8000/api/users/notification-status/', {
                    headers: { Authorization: `Bearer ${accessToken}` }
                })
                .then(response => {
                    if (response.data.status !== 'normal') {
                        setNotification(response.data);
                    }
                    setLoading(false);
                })
                .catch(error => {
                    console.error('Error fetching notification status:', error);
                    setLoading(false);
                });
        } else {
            setLoading(false);
        }
    }, [user, accessToken]);

    if (loading || !notification) {
        return null;
    }

    const getNotificationStyle = () => {
        if (notification.status === 'banned') {
            return {
                backgroundColor: '#ffcccb',
                color: '#8b0000',
                border: '2px solid #8b0000',
                fontWeight: 'bold'
            };
        } else if (notification.status === 'high_risk') {
            return {
                backgroundColor: '#f8d7da',
                color: '#721c24',
                border: '2px solid #dc3545',
                fontWeight: 'bold'
            };
        } else if (notification.status === 'under_investigation') {
            return {
                backgroundColor: '#fff3cd',
                color: '#856404',
                border: '2px solid #ffc107',
                fontWeight: 'bold'
            };
        }
        return {};
    };

    return (
        <div style={{
            ...getNotificationStyle(),
            padding: '15px 25px',
            margin: '10px 0 20px 0',
            borderRadius: '8px',
            textAlign: 'center',
            fontSize: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
            {notification.status === 'banned' && '🚫'}
            {notification.status === 'high_risk' && '🔴'}
            {notification.status === 'under_investigation' && '⚠️'}
            <strong>{notification.message}</strong>
        </div>
    );
} 