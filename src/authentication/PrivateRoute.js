import React, { useEffect, useState } from 'react';
import { Route, Redirect } from 'react-router-dom';
import { useCoffee } from '../CoffeeContext';

function PrivateRoute({ component: Component, ...rest }) {
  const { user } = useCoffee();
  const [isChecking, setIsChecking] = useState(true);

  // Wait a moment for user to load from localStorage
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsChecking(false);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Check localStorage directly as fallback
  const hasToken = localStorage.getItem('access_token');
  const isAuthenticated = user || hasToken;

  return (
    <Route
      {...rest}
      render={(props) => {
        if (isChecking) {
          // Show nothing while checking (prevents flash)
          return null;
        }
        return isAuthenticated ? (
          <Component {...props} />
        ) : (
          <Redirect 
            to={{
              pathname: "/",
              state: { from: props.location }
            }} 
          />
        );
      }}
    />
  );
}

export default PrivateRoute; 