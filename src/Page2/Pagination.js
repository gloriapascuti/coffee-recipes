import React from "react";
import styles from './styles/RUD.module.css';

function Pagination({ currentPage, setCurrentPage, totalItems, itemsPerPage }) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    return (
        <div className={styles.pagination}>
            <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className={styles.pageButton}
            >
                Previous
            </button>
            <span>Page {currentPage} of {totalPages}</span>
            <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage >= totalPages}
                className={styles.pageButton}
            >
                Next
            </button>
        </div>
    );
}

export default Pagination;
