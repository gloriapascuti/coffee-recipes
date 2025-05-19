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
const COFFEE_URL = `${API_ROOT}/coffee/`;
const ORIGINS_URL= `${API_ROOT}/origins/`;
const UPLOAD_URL = `${API_ROOT}/upload/`;

function authHeaders() {
    const token = localStorage.getItem("token");
    return {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Token ${token}` } : {})
    };
}

export const CoffeeProvider = ({ children }) => {
    const [coffees, setCoffees]             = useState([]);
    const { isOnline, isServerOnline }      = useNetworkStatus();
    const [isOfflineMode, setIsOfflineMode] = useState(false);
    const [isSyncing, setIsSyncing]         = useState(false);
    const [pendingOperations, setPendingOperations] = useState([]);

    // read & expose current user ID
    const userId = Number(localStorage.getItem("user_id") || -1);

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

    // whenever connectivity changes...
    useEffect(() => {
        if (!isOnline || !isServerOnline) {
            setIsOfflineMode(true);
            const localCoffees = OfflineService.getLocalCoffees();
            setCoffees(localCoffees);
        } else {
            setIsOfflineMode(false);
            fetchData();
            if (!isSyncing) {
                setIsSyncing(true);
                OfflineService
                    .processPendingOperations({ addCoffee, editCoffee, deleteCoffee })
                    .finally(() => {
                        setIsSyncing(false);
                        fetchData();
                    });
            }
        }
    }, [isOnline, isServerOnline]);

    // GET list
    async function fetchData() {
        try {
            const resp = await fetch(COFFEE_URL, { headers: authHeaders() });
            if (!resp.ok) throw new Error(`Error ${resp.status}`);
            const data = await resp.json();
            setCoffees(data);
            OfflineService.saveLocalCoffees(data);
        } catch (err) {
            console.error("Error fetching coffees:", err);
            if (!isOnline || !isServerOnline) {
                setCoffees(OfflineService.getLocalCoffees());
            }
        }
    }

    // Log operation to backend
    async function logOperation(operation) {
        const token = localStorage.getItem('token');
        await fetch('http://127.0.0.1:8000/api/log-operation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`,
            },
            body: JSON.stringify({ operation }),
        });
    }

    // CREATE
    async function addCoffee(coffee) {
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

        const resp = await fetch(COFFEE_URL, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(payload)
        });
        if (!resp.ok) {
            const text = await resp.text();
            console.error("Server error adding coffee:", text);
            throw new Error(`Add failed: ${resp.status}`);
        }
        const created = await resp.json();
        const updatedCoffees = [created, ...coffees];
        setCoffees(updatedCoffees);
        OfflineService.saveLocalCoffees(updatedCoffees);
        await logOperation('add');
        return created;
    }

    // UPDATE
    async function editCoffee(id, upd) {
        if (!isOnline || !isServerOnline) {
            const updatedCoffees = coffees.map(x => x.id === id ? { ...x, ...upd } : x);
            setCoffees(updatedCoffees);
            OfflineService.saveLocalCoffees(updatedCoffees);
            const operation = { type: "EDIT", id, data: upd, timestamp: Date.now() };
            OfflineService.savePendingOperation(operation);
            setPendingOperations(prev => [...prev, operation]);
            return upd;
        }

        const resp = await fetch(`${COFFEE_URL}${id}/`, {
            method: "PUT",
            headers: authHeaders(),
            body: JSON.stringify({
                name: upd.name,
                origin: { name: upd.origin },
                description: upd.description
            })
        });
        if (!resp.ok) {
            const text = await resp.text();
            console.error("Server error updating coffee:", text);
            throw new Error(`Update failed: ${resp.status}`);
        }
        const saved = await resp.json();
        const updatedCoffees = coffees.map(x => x.id === id ? saved : x);
        setCoffees(updatedCoffees);
        OfflineService.saveLocalCoffees(updatedCoffees);
        await logOperation('edit');
        return saved;
    }

    // DELETE
    async function deleteCoffee(id) {
        if (!isOnline || !isServerOnline) {
            const updatedCoffees = coffees.filter(x => x.id !== id);
            setCoffees(updatedCoffees);
            OfflineService.saveLocalCoffees(updatedCoffees);
            const operation = { type: "DELETE", id, timestamp: Date.now() };
            OfflineService.savePendingOperation(operation);
            setPendingOperations(prev => [...prev, operation]);
            return;
        }

        const resp = await fetch(`${COFFEE_URL}${id}/`, {
            method: "DELETE",
            headers: authHeaders()
        });
        if (!resp.ok) {
            const text = await resp.text();
            console.error("Server error deleting coffee:", text);
            throw new Error(`Delete failed: ${resp.status}`);
        }
        const updatedCoffees = coffees.filter(x => x.id !== id);
        setCoffees(updatedCoffees);
        OfflineService.saveLocalCoffees(updatedCoffees);
        await logOperation('delete');
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
            pendingOperations
        }}>
            {children}
        </CoffeeContext.Provider>
    );
};
