import React from 'react';
import { Route, Redirect } from 'react-router-dom';
import { useCoffee } from '../CoffeeContext';

function PrivateRoute({ component: Component, ...rest }) {
  const { user } = useCoffee();

  return (
    <Route
      {...rest}
      render={(props) =>
        user ? (
          <Component {...props} />
        ) : (
          <Redirect to="/" />
        )
      }
    />
  );
}

export default PrivateRoute; 