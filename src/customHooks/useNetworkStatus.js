import { useState, useEffect } from 'react';

export const useNetworkStatus = () => {
    const [isOnline, setIsOnline] = useState(navigator.onLine);
    const [isServerOnline, setIsServerOnline] = useState(true);

    useEffect(() => {
        const checkNetworkStatus = async () => {
            try {
                // Try to fetch a small resource to verify actual connectivity
                await fetch('https://www.google.com/favicon.ico', {
                    // method: 'HEAD',
                    method: 'GET',
                    mode: 'no-cors',
                    cache: 'no-cache'
                });
                setIsOnline(true);
            } catch (error) {
                setIsOnline(false);
            }
        };

        const checkServerStatus = async () => {
            if (!isOnline) {
                setIsServerOnline(false);
                return;
            }

            try {
                // const response = await fetch('http://127.0.0.1:8000/coffee', {
                //     method: 'HEAD',
                //     cache: 'no-cache'
                const response = await fetch('http://127.0.0.1:8000/api/healthcheck/', {
                    method: 'GET',
                    cache: 'no-cache'
                });
                if (response.status === 404) {
                    throw new Error('Endpoint /api/healthcheck/ not found (404)');
                }
                setIsServerOnline(response.ok);
            } catch (error) {
                setIsServerOnline(false);
            }
        };

        // Set up event listeners
        window.addEventListener('online', checkNetworkStatus);
        window.addEventListener('offline', checkNetworkStatus);

        // Initial checks
        checkNetworkStatus();
        checkServerStatus();

        // Set up intervals
        const networkCheckInterval = setInterval(checkNetworkStatus, 5000);
        const serverCheckInterval = setInterval(checkServerStatus, 30000);

        return () => {
            window.removeEventListener('online', checkNetworkStatus);
            window.removeEventListener('offline', checkNetworkStatus);
            clearInterval(networkCheckInterval);
            clearInterval(serverCheckInterval);
        };
    }, [isOnline]);

    return { isOnline, isServerOnline };
}; 