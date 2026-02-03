// // CoffeeContext.js
//
// import React, { createContext, useState, useEffect, useContext } from "react";
// import { useNetworkStatus } from "./customHooks/useNetworkStatus";
// import { OfflineService } from "./services/offlineService";
//
// export const CoffeeContext = createContext();
//
// export const useCoffee = () => {
//     const ctx = useContext(CoffeeContext);
//     if (!ctx) throw new Error("useCoffee must be used within a CoffeeProvider");
//     return ctx;
// };
//
// // Note trailing slash so Django doesn't redirect your POST/PUT with a 301
// // const baseUrl = "http://127.0.0.1:8000/coffee/";
// const baseUrl = "http://127.0.0.1:8000/api/coffee/";
//
// // Helper to build headers with JSON + optional Token
// function buildHeaders() {
//     const headers = { "Content-Type": "application/json" };
//     const token = localStorage.getItem("token");
//     if (token) headers["Authorization"] = `Token ${token}`;
//     return headers;
// }
//
// export const CoffeeProvider = ({ children }) => {
//     const [coffees, setCoffees] = useState([]);
//     const { isOnline, isServerOnline } = useNetworkStatus();
//     const [isOfflineMode, setIsOfflineMode] = useState(false);
//     const [isSyncing, setIsSyncing] = useState(false);
//
//     // On connectivity changes, either fetch from server or load cache
//     useEffect(() => {
//         if (!isOnline || !isServerOnline) {
//             setIsOfflineMode(true);
//             setCoffees(OfflineService.getLocalCoffees());
//         } else {
//             setIsOfflineMode(false);
//             fetchData();
//             if (!isSyncing) {
//                 setIsSyncing(true);
//                 OfflineService.processPendingOperations({
//                     addCoffee,
//                     editCoffee,
//                     deleteCoffee,
//                 }).finally(() => {
//                     setIsSyncing(false);
//                     fetchData();
//                 });
//             }
//         }
//     }, [isOnline, isServerOnline]);
//
//     // FETCH list
//     const fetchData = async () => {
//         try {
//             const resp = await fetch(baseUrl, {
//                 headers: buildHeaders(),
//             });
//             if (!resp.ok) throw new Error(resp.status);
//             const json = await resp.json();
//
//             // If paginated: unwrap `.results`, else expect array
//             const list = Array.isArray(json)
//                 ? json
//                 : Array.isArray(json.results)
//                     ? json.results
//                     : [];
//
//             setCoffees(list);
//             OfflineService.saveLocalCoffees(list);
//         } catch (err) {
//             console.error("Error fetching coffees:", err);
//             if (!isOnline || !isServerOnline) {
//                 setCoffees(OfflineService.getLocalCoffees());
//             }
//         }
//     };
//
//     // CREATE
//     async function addCoffee(coffee) {
//         if (!isOnline || !isServerOnline) {
//             const temp = { ...coffee, id: Date.now() };
//             setCoffees((c) => [temp, ...c]);
//             OfflineService.saveLocalCoffees([temp, ...coffees]);
//             OfflineService.savePendingOperation({ type: "ADD", data: coffee });
//             return temp;
//         }
//
//         const payload = {
//             name: coffee.name,
//             origin: { name: coffee.origin },
//             description: coffee.description,
//         };
//
//         const resp = await fetch(baseUrl, {
//             method: "POST",
//             headers: buildHeaders(),
//             body: JSON.stringify(payload),
//         });
//         if (!resp.ok) {
//             const body = await resp.text();
//             console.error("Server error adding coffee:", body);
//             throw new Error(`Add failed: ${resp.status}`);
//         }
//         const created = await resp.json();
//         setCoffees((c) => [created, ...c]);
//         OfflineService.saveLocalCoffees([created, ...coffees]);
//         return created;
//     }
//
//     // UPDATE
//     async function editCoffee(id, upd) {
//         if (!isOnline || !isServerOnline) {
//             setCoffees((c) => c.map((x) => (x.id === id ? { ...x, ...upd } : x)));
//             OfflineService.saveLocalCoffees(coffees);
//             OfflineService.savePendingOperation({ type: "EDIT", id, data: upd });
//             return upd;
//         }
//
//         const payload = {
//             name: upd.name,
//             origin: { name: upd.origin },
//             description: upd.description,
//         };
//
//         const resp = await fetch(`${baseUrl}${id}/`, {
//             method: "PUT",
//             headers: buildHeaders(),
//             body: JSON.stringify(payload),
//         });
//         if (!resp.ok) {
//             const body = await resp.text();
//             console.error("Server error updating coffee:", body);
//             throw new Error(`Update failed: ${resp.status}`);
//         }
//         const saved = await resp.json();
//         setCoffees((c) => c.map((x) => (x.id === id ? saved : x)));
//         OfflineService.saveLocalCoffees(coffees);
//         return saved;
//     }
//
//     // DELETE
//     async function deleteCoffee(id) {
//         if (!isOnline || !isServerOnline) {
//             setCoffees((c) => c.filter((x) => x.id !== id));
//             OfflineService.saveLocalCoffees(coffees);
//             OfflineService.savePendingOperation({ type: "DELETE", id });
//             return;
//         }
//
//         const resp = await fetch(`${baseUrl}${id}/`, {
//             method: "DELETE",
//             headers: buildHeaders(),
//         });
//         if (!resp.ok) throw new Error(`Delete failed: ${resp.status}`);
//         setCoffees((c) => c.filter((x) => x.id !== id));
//         OfflineService.saveLocalCoffees(coffees);
//     }
//
//     return (
//         <CoffeeContext.Provider
//             value={{
//                 coffees,
//                 addCoffee,
//                 editCoffee,
//                 deleteCoffee,
//                 isOfflineMode,
//                 isOnline,
//                 isServerOnline,
//                 isSyncing,
//             }}
//         >
//             {children}
//         </CoffeeContext.Provider>
//     );
// };

// src/CoffeeContext.js
import React, { createContext, useState, useEffect, useContext } from "react";
import { useNetworkStatus } from "./customHooks/useNetworkStatus";
import { OfflineService } from "./services/offlineService";

export const CoffeeContext = createContext();
export const useCoffee = () => {
    const ctx = useContext(CoffeeContext);
    if (!ctx) throw new Error("useCoffee must be used within CoffeeProvider");
    return ctx;
};

// your DRF URLs
const API_ROOT   = "http://127.0.0.1:8000/api";
const COFFEE_URL = `${API_ROOT}/`;
const USERS_URL = `${API_ROOT}/users/`;

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

export const CoffeeProvider = ({ children }) => {
    const [coffees, setCoffees]             = useState([]);
    const { isOnline, isServerOnline }      = useNetworkStatus();
    const [isOfflineMode, setIsOfflineMode] = useState(false);
    const [isSyncing, setIsSyncing]         = useState(false);
    const [pendingOperations, setPendingOperations] = useState([]);
    const [favorites, setFavorites] = useState([]);

    // read & expose current user ID
    const userId = Number(localStorage.getItem("user_id") || -1);

    // Add authentication state
    const [user, setUser] = useState(null);
    const [accessToken, setAccessToken] = useState(null);
    const [refreshToken, setRefreshToken] = useState(null);

    // Load tokens from localStorage on initial load
    useEffect(() => {
        const storedAccessToken = localStorage.getItem('access_token');
        const storedRefreshToken = localStorage.getItem('refresh_token');
        const storedUserId = localStorage.getItem('user_id');
        const storedUsername = localStorage.getItem('username');
        const storedIsSpecialAdmin = localStorage.getItem('user_is_special_admin') === 'true';
        
        if (storedAccessToken && storedRefreshToken) {
            setAccessToken(storedAccessToken);
            setRefreshToken(storedRefreshToken);
            if (storedUserId && storedUsername) {
                setUser({ 
                    id: Number(storedUserId), 
                    username: storedUsername,
                    twofa: localStorage.getItem('user_2fa') === 'true',
                    is_special_admin: storedIsSpecialAdmin
                });
            }
        }
    }, []);

    // Simplified login function
    const loginUser = async (username, password, code = null) => {
        try {
            const payload = { username, password };
            if (code) {
                payload.code = code;
            }

            const response = await fetch(`${USERS_URL}token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Login failed');
            }

            if (data.requires_2fa) {
                return { require_2fa: true, email: data.email };
            }

            // Store tokens and user data
            setAccessToken(data.access);
            setRefreshToken(data.refresh);
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            localStorage.setItem('user_2fa', data.twofa);
            localStorage.setItem('user_is_special_admin', data.is_special_admin);
            
            setUser({
                id: data.user_id,
                username: data.username,
                twofa: data.twofa,
                is_special_admin: data.is_special_admin
            });

            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    };

    // Function to verify 2FA code during login
    const verify2FALogin = async (email, code) => {
        try {
            const response = await fetch(`${USERS_URL}verify-2fa-login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, code })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '2FA verification failed');
            }

            // Store tokens and user info after successful 2FA verification
            setAccessToken(data.access);
            setRefreshToken(data.refresh);
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('username', data.username);
            localStorage.setItem('user_2fa', data.twofa);
            localStorage.setItem('user_is_special_admin', data.is_special_admin);
            
            setUser({
                id: data.user_id,
                username: data.username,
                twofa: data.twofa,
                is_special_admin: data.is_special_admin
            });

            return data;
        } catch (error) {
            console.error('2FA login verification failed:', error);
            throw error;
        }
    };

    // Add logout function
    const logoutUser = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        localStorage.removeItem('user_2fa');
        localStorage.removeItem('user_is_special_admin');
        setAccessToken(null);
        setRefreshToken(null);
        setUser(null);
        setCoffees([]);
    };

    // Helper function to perform authenticated fetch with token refresh retry
    const authenticatedFetch = async (url, options = {}, retry = true) => {
        if (!accessToken) {
            throw new Error('No access token available');
        }

        const initialOptions = {
            ...options,
            headers: {
                ...authHeaders(),
                ...(options.headers || {}),
            },
        };

        const response = await fetch(url, initialOptions);

        if (response.status === 401 && retry) {
            console.log('401 Unauthorized. Attempting to refresh token...');
            try {
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }
                
                const refreshResponse = await fetch('http://127.0.0.1:8000/api/users/token/refresh/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ refresh: refreshToken })
                });

                if (!refreshResponse.ok) {
                    throw new Error('Token refresh failed');
                }

                const refreshData = await refreshResponse.json();
                const newAccessToken = refreshData.access;
                
                setAccessToken(newAccessToken);
                localStorage.setItem('access_token', newAccessToken);
                console.log('Token refreshed. Retrying original request...');

                const retryHeaders = new Headers(initialOptions.headers);
                retryHeaders.set('Authorization', `Bearer ${newAccessToken}`);

                const retryOptions = {
                    ...options,
                    headers: retryHeaders,
                };

                return fetch(url, retryOptions);
            } catch (refreshError) {
                console.error('Failed to refresh token:', refreshError);
                logoutUser();
                throw new Error('Authentication failed. Please log in again.');
            }
        }

        return response;
    };

    // Load initial data and pending operations
    useEffect(() => {
        const loadInitialData = async () => {
            const localCoffees = OfflineService.getLocalCoffees();
            const pendingOps = OfflineService.getPendingOperations();
            setPendingOperations(pendingOps);
            
            if (localCoffees.length > 0) {
                setCoffees(localCoffees);
            }
            
            if (isOnline && isServerOnline && accessToken) {
                try {
                    const resp = await fetch(COFFEE_URL, { headers: authHeaders() });
                    if (resp.ok) {
                        const data = await resp.json();
                        setCoffees(data);
                        OfflineService.saveLocalCoffees(data);
                    }
                } catch (error) {
                    console.error("Error fetching initial data:", error);
                }
            }
        };

        loadInitialData();
    }, []);

    // Effect to handle network status and data fetching
    useEffect(() => {
        if (!isOnline || !isServerOnline) {
            setIsOfflineMode(true);
            setCoffees(OfflineService.getLocalCoffees());
        } else {
            setIsOfflineMode(false);
            // Fetch data even without token (API allows read-only access)
            fetchData();
            if (accessToken && !isSyncing) {
                setIsSyncing(true);
                OfflineService.processPendingOperations({
                    addCoffee,
                    editCoffee,
                    deleteCoffee,
                }).finally(() => {
                    setIsSyncing(false);
                    fetchData();
                });
            }
        }
    }, [isOnline, isServerOnline, accessToken]);

    // FETCH list
    const fetchData = async () => {
        // Allow fetching even without token (API allows read-only access)
        try {
            const resp = await fetch(COFFEE_URL, {
                headers: authHeaders(),
            });
            console.log("Fetch response status:", resp.status, resp.ok);
            if (resp.ok) {
                const json = await resp.json();
                console.log("Fetched coffees count:", Array.isArray(json) ? json.length : (Array.isArray(json.results) ? json.results.length : 0));
                const list = Array.isArray(json) ? json : Array.isArray(json.results) ? json.results : [];
                console.log("Setting coffees, count:", list.length);
                setCoffees(list);
                OfflineService.saveLocalCoffees(list);
            } else {
                console.error("Fetch failed with status:", resp.status, await resp.text());
            }
        } catch (err) {
            console.error("Error fetching coffees:", err);
            if (!isOnline || !isServerOnline) {
                setCoffees(OfflineService.getLocalCoffees());
            }
        }
    };

    // CREATE
    async function addCoffee(coffee) {
        if (!accessToken) return;
        if (!isOnline || !isServerOnline) {
            const temp = { ...coffee, id: Date.now(), user: userId };
            const updatedCoffees = [temp, ...coffees];
            setCoffees(updatedCoffees);
            OfflineService.saveLocalCoffees(updatedCoffees);
            const operation = { type: "ADD", data: coffee, timestamp: Date.now() };
            OfflineService.savePendingOperation(operation);
            setPendingOperations(prev => [...prev, operation]);
            return temp;
        }

        const payload = {
            name: coffee.name,
            origin: { name: coffee.origin },
            description: coffee.description
        };

        try {
            const resp = await fetch(COFFEE_URL, {
                method: "POST",
                headers: authHeaders(),
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                const created = await resp.json();
                const updatedCoffees = [created, ...coffees];
                setCoffees(updatedCoffees);
                OfflineService.saveLocalCoffees(updatedCoffees);
                return created;
            }
        } catch (error) {
            console.error('Error adding coffee:', error);
            throw error;
        }
    }

    // UPDATE
    async function editCoffee(id, upd) {
        if (!accessToken) return;
        if (!isOnline || !isServerOnline) {
            const updatedCoffees = coffees.map(x => x.id === id ? { ...x, ...upd } : x);
            setCoffees(updatedCoffees);
            OfflineService.saveLocalCoffees(updatedCoffees);
            const operation = { type: "EDIT", id, data: upd, timestamp: Date.now() };
            OfflineService.savePendingOperation(operation);
            setPendingOperations(prev => [...prev, operation]);
            return upd;
        }

        try {
            const resp = await fetch(`${COFFEE_URL}${id}/`, {
                method: "PUT",
                headers: authHeaders(),
                body: JSON.stringify({
                    name: upd.name,
                    origin: { name: upd.origin },
                    description: upd.description
                })
            });

            if (resp.ok) {
                const saved = await resp.json();
                const updatedCoffees = coffees.map(x => x.id === id ? saved : x);
                setCoffees(updatedCoffees);
                OfflineService.saveLocalCoffees(updatedCoffees);
                return saved;
            }
        } catch (error) {
            console.error('Error updating coffee:', error);
            throw error;
        }
    }

    // DELETE
    async function deleteCoffee(id) {
        if (!accessToken) return;
        if (!isOnline || !isServerOnline) {
            const updatedCoffees = coffees.filter(x => x.id !== id);
            setCoffees(updatedCoffees);
            OfflineService.saveLocalCoffees(updatedCoffees);
            const operation = { type: "DELETE", id, timestamp: Date.now() };
            OfflineService.savePendingOperation(operation);
            setPendingOperations(prev => [...prev, operation]);
            return;
        }

        try {
            const resp = await fetch(`${COFFEE_URL}${id}/`, {
                method: "DELETE",
                headers: authHeaders(),
            });

            if (resp.status === 204 || resp.ok) {
                const updatedCoffees = coffees.filter(x => x.id !== id);
                setCoffees(updatedCoffees);
                OfflineService.saveLocalCoffees(updatedCoffees);
            }
        } catch (error) {
            console.error('Error deleting coffee:', error);
            throw error;
        }
    }

    // Load favorites from localStorage on mount
    useEffect(() => {
        const storedFavorites = localStorage.getItem(`favorites_${userId}`);
        if (storedFavorites) {
            setFavorites(JSON.parse(storedFavorites));
        }
    }, [userId]);

    // Save favorites to localStorage whenever favorites change
    useEffect(() => {
        if (userId && favorites.length >= 0) {
            localStorage.setItem(`favorites_${userId}`, JSON.stringify(favorites));
        }
    }, [favorites, userId]);

    // Add to favorites
    const addToFavorites = (coffee) => {
        const isAlreadyFavorite = favorites.some(fav => fav.id === coffee.id);
        if (!isAlreadyFavorite) {
            setFavorites(prev => [...prev, coffee]);
        }
    };

    // Remove from favorites
    const removeFromFavorites = (coffeeId) => {
        setFavorites(prev => prev.filter(fav => fav.id !== coffeeId));
    };

    // Check if coffee is favorite
    const isFavorite = (coffeeId) => {
        return favorites.some(fav => fav.id === coffeeId);
    };

    return (
        <CoffeeContext.Provider value={{
            coffees,
            userId,
            addCoffee,
            editCoffee,
            deleteCoffee,
            fetchData,
            isOfflineMode,
            isOnline,
            isServerOnline,
            isSyncing,
            pendingOperations,
            user,
            loginUser,
            logoutUser,
            accessToken,
            authenticatedFetch,
            verify2FALogin,
            favorites,
            addToFavorites,
            removeFromFavorites,
            isFavorite,
        }}>
            {children}
        </CoffeeContext.Provider>
    );
};
