// import React from 'react';
// import './App.css';
// import Header from "./Page1/Header";
// import Generalities from "./Page1/Generalities";
// import CoffeeTypes from "./Page1/CoffeeTypes";
// import AddCoffee from "./Page1/AddCoffee";
// import GrindingBeans from "./Page1/GrindingBeans";
// import Cards from "./Page1/Cards";
// import ViewSection from "./Page1/ViewSection";
// import NavigationFooter from "./Page1/NavigationFooter";
// import RUD from "./Page2/RUD";
// import {CoffeeProvider} from "./CoffeeContext";
// import CoffeeDifferences from "./Page2/CoffeeDifferences";
// import Syrup from "./Page2/Syrup";
// import FileUploader from "./Page2/FileUploader";
// import StatusIndicator from './components/StatusIndicator';
// import './components/StatusIndicator.css';
//
// function App() {
//
//     return (
//     <div className="App">
//
//         <CoffeeProvider>
//             <StatusIndicator />
//             <Header/>
//             <Generalities/>
//             <CoffeeTypes/>
//             <AddCoffee/>
//             <GrindingBeans/>
//             <Cards/>
//             <ViewSection/>
//
//             <RUD/>
//             <FileUploader/>
//             <CoffeeDifferences/>
//             <Syrup/>
//             <NavigationFooter/>
//         </CoffeeProvider>
//     </div>
//   );
// }
//
// export default App;


import React from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import { CoffeeProvider } from './CoffeeContext';
import StatusIndicator from './components/StatusIndicator';
import Header from './Page1/Header';
import Generalities from './Page1/Generalities';
import CoffeeTypes from './Page1/CoffeeTypes';
import AddCoffee from './Page1/AddCoffee';
import GrindingBeans from './Page1/GrindingBeans';
import Cards from './Page1/Cards';
import ViewSection from './Page1/ViewSection';
import RUD from './Page2/RUD';
import FileUploader from './Page2/FileUploader';
import CoffeeDifferences from './Page2/CoffeeDifferences';
import Syrup from './Page2/Syrup';
import NavigationFooter from './Page1/NavigationFooter';
import EntryPage from './authentication/EntryPage';
import Login from './authentication/Login';
import Register from './authentication/Register';
import './App.css';
import './components/StatusIndicator.css';

function App() {
    return (
        <Router>
            <CoffeeProvider>
                <StatusIndicator />
                <Switch>
                    <Route exact path="/"       component={EntryPage} />
                    <Route       path="/login"    component={Login} />
                    <Route       path="/register" component={Register} />
                    <Route
                        path="/app"
                        render={() => (
                            <>
                                <Header/>
                                <Generalities/>
                                <CoffeeTypes/>
                                <AddCoffee/>
                                <GrindingBeans/>
                                <Cards/>
                                <ViewSection/>
                                <RUD/>
                                <FileUploader/>
                                <CoffeeDifferences/>
                                <Syrup/>
                                <NavigationFooter/>
                            </>
                        )}
                    />
                    <Redirect to="/" />
                </Switch>
            </CoffeeProvider>
        </Router>
    );
}

export default App;
