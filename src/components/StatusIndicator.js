import React from 'react';
import { useCoffee } from '../CoffeeContext';

const StatusIndicator = () => {
    const { isOnline, isServerOnline, isOfflineMode } = useCoffee();

    const getStatusMessage = () => {
        if (!isOnline) {
            return {
                message: 'Offline',
                className: 'status-offline'
            };
        }
        if (!isServerOnline) {
            return {
                message: 'Server Unavailable',
                className: 'status-server-offline'
            };
        }
        if (isOfflineMode) {
            return {
                message: 'Working Offline',
                className: 'status-offline-mode'
            };
        }
        return {
            message: 'Online',
            className: 'status-online'
        };
    };

    const status = getStatusMessage();

    return (
        <div className={`status-indicator ${status.className}`}>
            <div className="status-dot"></div>
            <span className="status-text">{status.message}</span>
        </div>
    );
};

export default StatusIndicator; 