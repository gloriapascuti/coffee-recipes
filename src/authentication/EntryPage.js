import React, { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { useCoffee } from '../CoffeeContext';

const btnStyle = {
    backgroundColor: 'black',
    color: 'white',
    padding: '10px 12px',
    border: 'none',
    borderRadius: '5px',
    fontSize: '16px',
    cursor: 'pointer',
    fontFamily: 'Georgia',
    marginLeft: '5px'
};

export default function EntryPage() {
    const history = useHistory();
    const { user } = useCoffee();

    // Redirect to app if user is already authenticated
    useEffect(() => {
        if (user) {
            history.push('/app');
        }
    }, [user, history]);

    // Don't render anything if user is authenticated (will be redirected)
    if (user) {
        return null;
    }

    return (
        <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: 'Georgia' }}>
            <h1>Welcome to the coffee recipe website ☕️</h1>
            <div style={{ marginTop: '30px' }}>
                <button style={btnStyle} onClick={() => history.push('/login')}>
                    Login
                </button>
                <button style={btnStyle} onClick={() => history.push('/register')}>
                    Register
                </button>
            </div>
        </div>
    );
}
