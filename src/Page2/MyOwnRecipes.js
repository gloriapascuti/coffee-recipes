// src/Page2/MyOwnRecipes.js
import React from 'react';
import { useCoffee } from '../CoffeeContext';

export default function MyOwnRecipes({ showMine, onToggle }) {
    const { userId } = useCoffee();
    return (
        <label style={{ display: 'block', margin: '1em 0' }}>
            <input
                type="checkbox"
                checked={showMine}
                onChange={e => onToggle(e.target.checked)}
                style={{ marginRight: '0.5em' }}
            />
            Show only my recipes (user #{userId})
        </label>
    );
}
