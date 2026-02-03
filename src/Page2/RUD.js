// src/Page2/RUD.js
import React, { useContext, useState, useEffect } from "react";
import { CoffeeContext } from "../CoffeeContext";
import Charts from "./Charts";
import SortButton from "./SortButton";
import FilterOriginButton from "./FilterOriginButton";
import InfiniteScroll from "./InfiniteScroll";
import MyOwnRecipes from "./MyOwnRecipes";
import styles from "./styles/RUD.module.css";
import AdminUserTable from "../components/AdminUserTable";

const WS_URL = "ws://localhost:8000/ws/coffee/";

export default function RUD() {
    const {
        coffees,
        userId,
        setCoffees,    // for websocket updates
    } = useContext(CoffeeContext);

    // toggle for "only mine"
    const [showMine, setShowMine] = useState(false);

    // search/filter/sort state
    const [input, setInput]             = useState("");
    const [selectedOrigin, setSelectedOrigin] = useState("");
    const [filteredCoffee, setFilteredCoffee] = useState([]);

    // sort
    const [isAscending, setIsAscending] = useState(true);

    // 1) WebSocket real-time updates (optional - only for real-time new coffee notifications)
    useEffect(() => {
        let socket = null;
        try {
            socket = new WebSocket(WS_URL);
            socket.onopen = () => {
                console.log("WebSocket connected for real-time updates");
            };
            socket.onmessage = e => {
                const newCoffee = JSON.parse(e.data);
                setCoffees(prev => [newCoffee, ...prev]);
            };
            socket.onerror = (error) => {
                // WebSocket is optional - silently fail if not available
                console.log("WebSocket not available (this is OK - recipes still load via REST API)");
            };
            socket.onclose = () => {
                console.log("WebSocket closed");
            };
        } catch (error) {
            // WebSocket connection failed - this is fine, recipes still work via REST API
            console.log("WebSocket connection failed (this is OK)");
        }
        return () => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, [setCoffees]);

    // 2) Filter pipeline
    useEffect(() => {
        console.log("RUD: coffees count:", coffees.length);
        let list = coffees;

        // Filter out ALL private recipes from main recipe list
        // Private recipes should only appear in "My Recipes" (Page 3), not in the main list
        list = list.filter(c => {
            const isPrivate = c.is_private === true || c.is_private === 1 || c.is_private === 'true';
            if (isPrivate) {
                console.log(`Filtering out private recipe from main list: ${c.name}`);
                return false;
            }
            return true; // Only show public recipes
        });

        // only mine?
        if (showMine) {
            list = list.filter(c => c.user === userId);
        }

        // name search
        if (input.trim()) {
            list = list.filter(c =>
                c.name.toLowerCase().includes(input.toLowerCase())
            );
        }

        // origin dropdown
        if (selectedOrigin) {
            list = list.filter(c => c.origin.name === selectedOrigin);
        }

        console.log("RUD: filtered count:", list.length);
        setFilteredCoffee(list);
    }, [coffees, showMine, input, selectedOrigin, userId]);

    // 3) helpers
    const getBackgroundColor = name => {
        const mostList   = ["Latte","Mocha","Irish Coffee","Vanilla Latte"];
        const mediumList = ["Flat White","Cappuccino","V60","Cold Brew"];
        const lowList    = ["Espresso","Americano","Macchiato"];
        if (mostList.includes(name))  return "sienna";
        if (mediumList.includes(name))return "tan";
        if (lowList.includes(name))   return "papayawhip";
        return "papayawhip";
    };

    // 4) sort
    const sorted = [...filteredCoffee].sort((a,b) =>
        isAscending
            ? a.name.localeCompare(b.name)
            : b.name.localeCompare(a.name)
    );

    return (
        <div>
            <Charts />

            <AdminUserTable />

            <div>
                <div className={styles.sectionTitle}>All recipes</div>

                {/* ↙︎ our new toggle */}
                {/*<MyOwnRecipes*/}
                {/*    showMine={showMine}*/}
                {/*    onToggle={setShowMine}*/}
                {/*/>*/}

                <div className={styles.searchBar}>
                    <input
                        type="text"
                        placeholder="Search coffee..."
                        value={input}
                        onChange={e => setInput(e.target.value)}
                    />
                    <SortButton
                        isAscending={isAscending}
                        onToggleSort={() => setIsAscending(!isAscending)}
                    />
                    <FilterOriginButton
                        selectedOrigin={selectedOrigin}
                        onFilter={setSelectedOrigin}
                    />
                </div>

                <ul className="mt-4">
                    <InfiniteScroll
                        data={sorted}
                        loading={false}
                        getBackgroundColor={getBackgroundColor}
                    />
                </ul>
            </div>
        </div>
    );
}
