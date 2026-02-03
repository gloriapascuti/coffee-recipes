import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Log the error details
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({
            error: error,
            errorInfo: errorInfo
        });
    }

    render() {
        if (this.state.hasError) {
            // Fallback UI
            return (
                <div style={{
                    padding: '2rem',
                    margin: '1rem',
                    border: '2px solid #f44336',
                    borderRadius: '8px',
                    backgroundColor: '#ffebee',
                    color: '#d32f2f',
                    textAlign: 'center'
                }}>
                    <h2>⚠️ Something went wrong</h2>
                    <p>An error occurred while rendering this component.</p>
                    {process.env.NODE_ENV === 'development' && (
                        <details style={{ 
                            marginTop: '1rem', 
                            textAlign: 'left',
                            backgroundColor: '#fff',
                            padding: '1rem',
                            borderRadius: '4px',
                            border: '1px solid #ddd'
                        }}>
                            <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                                Error Details (Development Only)
                            </summary>
                            <pre style={{ fontSize: '0.8em', marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
                                {this.state.error && this.state.error.toString()}
                                {this.state.errorInfo.componentStack}
                            </pre>
                        </details>
                    )}
                    <button 
                        onClick={() => window.location.reload()} 
                        style={{
                            marginTop: '1rem',
                            padding: '0.5rem 1rem',
                            backgroundColor: '#f44336',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        Reload Page
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary; 