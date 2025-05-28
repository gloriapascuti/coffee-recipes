import React, { useEffect, useState } from "react";
import styles from './styles/RUD.module.css';


const InfiniteScroll = ({data, loading, handleDelete, handleEdit, handleSaveEdit,
                            editingCoffee, editInput, setEditInput, getBackgroundColor, loadMoreData
    }) => {
    const [displayData, setDisplayData] = useState([]);

    useEffect(() => {
        setDisplayData(data);
    }, [data]);

    const handleScroll = () => {
        const { scrollTop, clientHeight, scrollHeight } = document.documentElement;

        if (scrollTop + clientHeight >= scrollHeight - 10 && !loading) {
            loadMoreData();
        }
    };

    useEffect(() => {
        // window.addEventListener('scroll', handleScroll);

        // return () => {
        //     window.removeEventListener('scroll', handleScroll);
        // };
    }, [loading]);

    return (
        <div className={styles.scrollContainer}>
            {displayData && displayData.map((coffee, index) => (
                <li key={index} className={styles.customerQuote} style={{ backgroundColor: getBackgroundColor(coffee.name) }}>
                    {editingCoffee === coffee.id ? (
                        <div>
                            <input type="text" value={editInput.name} onChange={(e) => setEditInput({ ...editInput, name: e.target.value })} />
                            <input type="text" value={editInput.origin} onChange={(e) => setEditInput({ ...editInput, origin: e.target.value })} />
                            <input type="text" value={editInput.description} onChange={(e) => setEditInput({ ...editInput, description: e.target.value })} />
                            <button onClick={handleSaveEdit} className={styles.button}>Save</button>
                        </div>
                    ) : (
                        <>
                            <div className={styles.aTerrificPiece}>{coffee.name}</div>
                            <div className={styles.nameParent}>
                                {/*<div className={styles.name}>{coffee.origin}</div>*/}
                                <div className={styles.name}>{coffee.origin.name}</div>
                                <div className={styles.description}>{coffee.description}</div>
                            </div>
                            <button className={styles.button} onClick={() => handleEdit(coffee)}>Edit</button>
                            <button className={styles.deleteButton} onClick={() => handleDelete(coffee.id)}>Delete</button>
                        </>
                    )}
                </li>
            ))}
            {loading && <p>loading...</p>}
        </div>
    );
};

export default InfiniteScroll;