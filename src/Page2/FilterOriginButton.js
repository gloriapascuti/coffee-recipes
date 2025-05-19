// FilterOriginButton.js
import React, { useEffect, useState } from "react";
import styles from "./styles/RUD.module.css";

/**
 * Props:
 *  selectedOrigin: string  – the currently-selected origin name (or "")
 *  onFilter:       (origin: string) => void
 */
const FilterOriginButton = ({ selectedOrigin, onFilter }) => {
    const [origins, setOrigins] = useState([]);

    // 1) load the list of origins once on mount
    useEffect(() => {
        const fetchOrigins = async () => {
            try {
                // const res = await fetch("http://127.0.0.1:8000/origins/");
                const res = await fetch("http://127.0.0.1:8000/api/origins/");
                if (res.status === 404) {
                    throw new Error('Endpoint /api/origins/ not found (404)');
                }
                if (!res.ok) throw new Error(res.statusText);
                const data = await res.json();
                setOrigins(data);
            } catch (err) {
                console.error("Failed to fetch origins:", err);
            }
        };
        fetchOrigins();
    }, []);

    return (
        <select
            className={styles.sortButton /* or create a new .filterButton style */}
            value={selectedOrigin}
            onChange={(e) => onFilter(e.target.value)}
        >
            {/* default: show all coffees */}
            <option value="">All Origins</option>

            {/* one option per origin record */}
            {origins.map((o) => (
                <option key={o.id} value={o.name}>
                    {o.name}
                </option>
            ))}
        </select>
    );
};

export default FilterOriginButton;
