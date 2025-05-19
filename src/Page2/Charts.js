import React, { useContext } from "react";
import { Line, Pie, Bar } from "react-chartjs-2";
import { CoffeeContext } from "../CoffeeContext";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from 'chart.js';
import styles from './styles/RUD.module.css';

ChartJS.register(
    CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
    ArcElement, PointElement, LineElement
);

function Charts() {
    const { coffees } = useContext(CoffeeContext);

    // const origins = [...new Set(coffees.map(coffee => coffee.origin))];
    const origins = [...new Set(coffees.map(coffee => coffee.origin.name))];

    // const originsData = origins.map(origin =>
    //     coffees.filter(coffee => coffee.origin === origin).length
    const originsData = origins.map(originName =>
        coffees.filter(coffee => coffee.origin.name === originName).length
    );

    const originsChartData = {
        labels: origins,
        datasets: [{
            label: 'Coffees by Origin',
            data: originsData,
            backgroundColor: ['burlywood', 'saddlebrown', 'bisque', 'peru', 'sienna'],
            borderColor: ['burlywood', 'saddlebrown', 'bisque', 'peru', 'sienna'],
            borderWidth: 1
        }]
    };

    const coffeeNames = [...new Set(coffees.map(coffee => coffee.name))];
    const nameCountData = coffeeNames.map(name =>
        coffees.filter(coffee => coffee.name === name).length
    );

    const namesChartData = {
        labels: coffeeNames,
        datasets: [{
            label: 'Coffees by Name',
            data: nameCountData,
            backgroundColor: 'tan',
            borderColor: 'tan',
            borderWidth: 1
        }]
    };

    const nameToOriginRatioData = coffeeNames.map(name => {
        const countByName = coffees.filter(coffee => coffee.name === name).length;
        const countByOrigin = coffees.filter(coffee => coffee.origin === coffees.find(coffee => coffee.name === name).origin).length;
        return (countByName / countByOrigin).toFixed(2);
    });

    const namesToOriginRatioChartData = {
        labels: coffeeNames,
        datasets: [{
            label: 'Coffee Name to Origin Ratio',
            data: nameToOriginRatioData,
            backgroundColor: 'peru',
            borderColor: 'peru',
            borderWidth: 1
        }]
    };

    return (
        <div className={styles.chartWrapper}>
            <div className={styles.chartContainer}>
                <Pie data={originsChartData} />
            </div>
            <div className={styles.chartContainer}>
                <Bar data={namesChartData} />
            </div>
            <div className={styles.chartContainer}>
                <Line data={namesToOriginRatioChartData} />
            </div>
        </div>
    );
}

export default Charts;