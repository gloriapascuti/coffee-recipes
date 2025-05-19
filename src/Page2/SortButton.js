// SortButton.js
import React from "react";
import styles from './styles/RUD.module.css';

const SortButton = ({ isAscending, onToggleSort }) => {
    return (
        <button
            className={styles.sortButton}
            onClick={onToggleSort}
        >
            Sort {isAscending ? "↓" : "↑"}
        </button>
    );
};

export default SortButton;
