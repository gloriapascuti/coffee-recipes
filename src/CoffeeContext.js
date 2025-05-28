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
import { login, refreshToken as callRefreshToken, logout } from "./services/authService"; // Alias refreshToken import

export const CoffeeContext = createContext();
export const useCoffee = () => {
    const ctx = useContext(CoffeeContext);
    if (!ctx) throw new Error("useCoffee must be used within CoffeeProvider");
    return ctx;
};

// your DRF URLs
const API_ROOT   = "http://127.0.0.1:8000/api";
const COFFEE_URL = `${API_ROOT}/`;
const ORIGINS_URL= `${API_ROOT}/origins/`;
const UPLOAD_URL = `${API_ROOT}/upload/`;

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

    // read & expose current user ID
    const userId = Number(localStorage.getItem("user_id") || -1);

    // Add authentication state
    const [user, setUser] = useState(null);
    const [accessToken, setAccessToken] = useState(null);
    const [refreshToken, setRefreshToken] = useState(null); // This is the state variable for the token string

    // Load tokens from localStorage on initial load
    useEffect(() => {
        const storedAccessToken = localStorage.getItem('access_token');
        const storedRefreshToken = localStorage.getItem('refresh_token');
        const storedUserId = localStorage.getItem('user_id');
        const storedUsername = localStorage.getItem('username');
        
        if (storedAccessToken && storedRefreshToken) {
            setAccessToken(storedAccessToken);
            setRefreshToken(storedRefreshToken);
            if (storedUserId && storedUsername) {
                setUser({ id: Number(storedUserId), username: storedUsername });
            }
        }
    }, []);

    // Add login function
    const loginUser = async (username, password) => {
        try {
            const data = await login(username, password);
            setAccessToken(data.access);
            setRefreshToken(data.refresh);
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            if (data.user_id) {
                localStorage.setItem('user_id', data.user_id);
            }
            if (data.username) {
                localStorage.setItem('username', data.username);
            }
            setUser({ id: Number(data.user_id), username: data.username });
            return data;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    // Add logout function
    const logoutUser = () => {
        logout(); // This will clear all tokens from localStorage
        setAccessToken(null);
        setRefreshToken(null);
        setUser(null);
        setCoffees([]); // Clear coffee data on logout
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
            
            if (isOnline && isServerOnline) {
                try {
                    const resp = await fetch(COFFEE_URL, { headers: authHeaders() });
                    if (!resp.ok) throw new Error(`Error ${resp.status}`);
                    const data = await resp.json();
                    setCoffees(data);
                    OfflineService.saveLocalCoffees(data);
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
            // Only fetch data if authenticated
            if (accessToken) {
                 fetchData();
                 if (!isSyncing) {
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
            } else {
                // Clear data if not authenticated
                setCoffees([]);
            }
        }
    }, [isOnline, isServerOnline, accessToken]); // Add accessToken as a dependency

    // FETCH list - Modify to only fetch if authenticated and handle token refresh
    const fetchData = async () => {
        if (!accessToken) return; // Don't fetch if not authenticated
        try {
            const resp = await fetch(COFFEE_URL, {
                headers: authHeaders(),
            });
            if (!resp.ok) {
                // Handle token expiration or invalid token
                if (resp.status === 401) {
                    console.log('Access token expired or invalid. Attempting to refresh...');
                    try {
                        const newAccessToken = await callRefreshToken(refreshToken);
                        setAccessToken(newAccessToken);
                        localStorage.setItem('access_token', newAccessToken);
                        // Retry the original request with the new token
                         fetchData(); // Simple retry: refetch all data
                    } catch (refreshError) {
                        console.error('Failed to refresh token:', refreshError);
                        logoutUser(); // Logout if refresh fails
                    }
                } else {
                     throw new Error(resp.status);
                }
            }
             const json = await resp.json();

            // If paginated: unwrap `.results`, else expect array
            const list = Array.isArray(json)
                ? json
                : Array.isArray(json.results)
                    ? json.results
                    : [];

            setCoffees(list);
            OfflineService.saveLocalCoffees(list);
        } catch (err) {
            console.error("Error fetching coffees:", err);
            if (!isOnline || !isServerOnline) {
                setCoffees(OfflineService.getLocalCoffees());
            }
        }
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
                const newAccessToken = await callRefreshToken(refreshToken);
                setAccessToken(newAccessToken);
                localStorage.setItem('access_token', newAccessToken);
                console.log('Token refreshed. Retrying original request...');

                const retryHeaders = new Headers(initialOptions.headers);
                retryHeaders.set('Authorization', `Bearer ${newAccessToken}`);

                const retryOptions = {
                    ...options,
                    headers: retryHeaders,
                };

                if (['POST', 'PUT', 'PATCH'].includes(options.method?.toUpperCase()) && options.body) {
                    retryOptions.body = options.body;
                }

                return fetch(url, retryOptions);
            } catch (refreshError) {
                console.error('Failed to refresh token:', refreshError);
                logoutUser();
                throw new Error('Authentication failed. Please log in again.');
            }
        }

        if (!response.ok) {
            const errorBody = await response.text();
            let errorDetail = `Request failed with status ${response.status}`;
            try {
                const jsonError = JSON.parse(errorBody);
                errorDetail = jsonError.detail || JSON.stringify(jsonError);
            } catch (e) {
                errorDetail = errorBody;
            }
            const error = new Error(errorDetail);
            error.response = response;
            throw error;
        }

        return response;
    };

    // CREATE - Use authenticatedFetch for token refresh retry
    async function addCoffee(coffee) {
         if (!accessToken) return; // Prevent adding if not authenticated
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
            const resp = await authenticatedFetch(COFFEE_URL, {
                method: "POST",
                body: JSON.stringify(payload)
            });

            const created = await resp.json();
            const updatedCoffees = [created, ...coffees];
            setCoffees(updatedCoffees);
            OfflineService.saveLocalCoffees(updatedCoffees);
            await logOperation('add');
            return created;
        } catch (error) {
            console.error('Error adding coffee:', error);
            throw error; // Re-throw the error after logging
        }
    }

    // UPDATE - Use authenticatedFetch for token refresh retry
    async function editCoffee(id, upd) {
        if (!accessToken) return; // Prevent editing if not authenticated
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
            const resp = await authenticatedFetch(`${COFFEE_URL}${id}/`, {
                method: "PUT",
                body: JSON.stringify({
                    name: upd.name,
                    origin: { name: upd.origin },
                    description: upd.description
                })
            });

            const saved = await resp.json();
            const updatedCoffees = coffees.map(x => x.id === id ? saved : x);
            setCoffees(updatedCoffees);
            OfflineService.saveLocalCoffees(updatedCoffees);
            await logOperation('edit');
            return saved;
        } catch (error) {
             console.error('Error updating coffee:', error);
             throw error; // Re-throw the error after logging
        }
    }

    // DELETE - Use authenticatedFetch for token refresh retry
    async function deleteCoffee(id) {
        if (!accessToken) return; // Prevent deletion if not authenticated
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
            const resp = await authenticatedFetch(`${COFFEE_URL}${id}/`, {
                method: "DELETE",
            });

            if (resp.status === 204) { // Handle 204 No Content for successful delete
                 const updatedCoffees = coffees.filter(x => x.id !== id);
                 setCoffees(updatedCoffees);
                 OfflineService.saveLocalCoffees(updatedCoffees);
                 await logOperation('delete');
                 return; // Return early for 204
            }
             // If not 204, and authenticatedFetch didn't throw for other errors, something unexpected happened
             // This part might need further refinement based on your backend's delete response
             const result = await resp.text(); // Read response body if not 204
             console.log('Delete response (not 204):', result);
             // Depending on backend, you might need to check result or status again

        } catch (error) {
             console.error('Error deleting coffee:', error);
             throw error; // Re-throw the error after logging
        }
    }

    // Log operation to backend - Use authenticatedFetch
    async function logOperation(operation) {
         if (!accessToken) return; // Prevent logging if not authenticated
        try {
            await authenticatedFetch('http://127.0.0.1:8000/api/log-operation/', {
                method: 'POST',
                body: JSON.stringify({ operation }),
            });
        } catch (error) {
             console.error('Error logging operation:', error);
             // Optionally, handle this error differently as it might not be critical
        }
    }

    return (
        <CoffeeContext.Provider value={{
            coffees,
            userId,
            addCoffee,
            editCoffee,
            deleteCoffee,
            isOfflineMode,
            isOnline,
            isServerOnline,
            isSyncing,
            pendingOperations,
            user,
            loginUser,
            logoutUser,
            accessToken,
        }}>
            {children}
        </CoffeeContext.Provider>
    );
};
