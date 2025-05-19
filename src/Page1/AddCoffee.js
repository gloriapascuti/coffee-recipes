import React, {useContext, useState, useEffect} from "react";
import { useHistory } from "react-router-dom";
import styles from "./styles/AddCoffee.module.css";
import {CoffeeContext} from "../CoffeeContext";

const AddCoffee = () => {
    const history = useHistory();
    const [name, setName] = useState("");
    const [origin, setOrigin] = useState("");
    const [description, setDescription] = useState("");

    // const {items, setItems} = useContext(CoffeeContext);

    const {coffees, addCoffee} = useContext(CoffeeContext)

    // Check if user is authenticated
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            history.push('/login');
        }
    }, [history]);

    const addItem = async () => {
        if (!name || !origin || !description) {
            alert("Please fill in all fields.");
            return;
        }

        try {
            const newItem = { name, origin, description };
            await addCoffee(newItem);
            setName(""); 
            setOrigin(""); 
            setDescription(""); // Clear inputs
        } catch (error) {
            alert("Failed to add coffee recipe. Please try again.");
            console.error("Error adding coffee:", error);
        }
    };

    return (
        <div style={{gap: "50px"}}>
            <div className={styles.Title}>Add your own recipe</div>
            {/*<div className={styles.pageContainer}>*/}
            {/*<div style={{display: "flex", padding: "50px", gap: "80px"}}>*/}
                <div style={{display: "flex", padding: "50px", gap: "100px"}}>
                    {/* Form Section */}
                    {/*<div className={styles.formContainer}>*/}
                    <div style={{display: "flex", gap: "60", flexDirection: "column", width: "50%", justifyContent: "center"}}>
                        <div className={styles.inputGroup}>
                            <label className={styles.subtitle}>Name</label>
                            <input
                                type="text"
                                placeholder="Enter coffee name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                            />
                        </div>

                        <div className={styles.inputGroup}>
                            <label className={styles.subtitle}>Origin</label>
                            <input
                                type="text"
                                placeholder="Where is it from?"
                                value={origin}
                                onChange={(e) => setOrigin(e.target.value)}
                            />
                        </div>

                        <div className={styles.inputGroup}>
                            <label className={styles.subtitle}>Method used/Instructions</label>
                            <input
                                type="text"
                                placeholder="Describe the preparation"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                            />
                        </div>

                        <button className={styles.addButton} onClick={addItem}>Add recipe</button>

                        {/* Display added items */}
                        {/*<ul className={styles.itemsList}>*/}
                        {/*    {coffees.map((item, index) => (*/}
                        {/*        <li key={index}>*/}
                        {/*            <strong>{item.name}</strong> ({item.origin}) - {item.description}*/}
                        {/*        </li>*/}
                        {/*    ))}*/}
                        {/*</ul>*/}
                    </div>

                    {/* Image Section */}
                    <div className={styles.imageContainer}>
                        <img className={styles.coffeeImage}/>
                    </div>
                </div>
            </div>
        // </div>

    );
};

export default AddCoffee;
