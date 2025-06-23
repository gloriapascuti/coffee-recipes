import React from 'react';
import { BrowserRouter as Router, Switch, Route, Redirect } from 'react-router-dom';
import { CoffeeProvider } from './CoffeeContext';
import StatusIndicator from './components/StatusIndicator';
import UserNotification from './components/UserNotification';
import Header from './Page1/Header';
import Generalities from './Page1/Generalities';
import CoffeeTypes from './Page1/CoffeeTypes';
import AddCoffee from './Page1/AddCoffee';
import GrindingBeans from './Page1/GrindingBeans';
import Cards from './Page1/Cards';
import BrewingAndSyrups from './Page1/BrewingAndSyrups';

import RUD from './Page2/RUD';
import FileUploader from './Page2/FileUploader';

import NavigationFooter from './Page1/NavigationFooter';
import EntryPage from './authentication/EntryPage';
import Login from './authentication/Login';
import Register from './authentication/Register';
import PrivateRoute from './authentication/PrivateRoute';
import UserSettings from './authentication/UserSettings';
import Profile from './authentication/Profile';
import Recommendations from './Page3/Recommendations';
import MyRecipe from './Page3/MyRecipe';
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
                    
                    {/* Page 1 Route */}
                    <PrivateRoute
                        path="/page1"
                        component={() => (
                            <>
                                <Header/>
                                <Generalities/>
                                <CoffeeTypes/>
                                <AddCoffee/>
                                <GrindingBeans/>
                                <Cards/>
                                <BrewingAndSyrups/>
                                <NavigationFooter/>
                            </>
                        )}
                    />
                    
                    {/* Page 2 Route */}
                    <PrivateRoute
                        path="/page2"
                        component={() => (
                            <>
                                <Header/>
                                <RUD/>
                                <FileUploader/>
                                <NavigationFooter/>
                            </>
                        )}
                    />
                    
                    {/* Page 3 Route */}
                    <PrivateRoute
                        path="/page3"
                        component={() => (
                            <>
                                <Header/>
                                <MyRecipe/>
                                <NavigationFooter/>
                            </>
                        )}
                    />
                    
                    {/* Legacy route - redirect to page1 */}
                    <PrivateRoute
                        path="/app"
                        component={() => <Redirect to="/page1" />}
                    />
                    
                    <PrivateRoute path="/settings" component={() => (
                        <>
                            <UserNotification />
                            <UserSettings />
                        </>
                    )} />
                    <PrivateRoute path="/profile" component={Profile} />
                    <PrivateRoute path="/recommendations" component={Recommendations} />
                    <Redirect to="/" />
                </Switch>
            </CoffeeProvider>
        </Router>
    );
}

export default App;
