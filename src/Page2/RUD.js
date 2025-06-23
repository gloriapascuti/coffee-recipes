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

    // 1) WebSocket real-time updates
    useEffect(() => {
        const socket = new WebSocket(WS_URL);
        socket.onmessage = e => {
            const newCoffee = JSON.parse(e.data);
            setCoffees(prev => [newCoffee, ...prev]);
        };
        return () => socket.close();
    }, [setCoffees]);

    // 2) Filter pipeline
    useEffect(() => {
        let list = coffees;

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
