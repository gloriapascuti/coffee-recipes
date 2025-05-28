import React, { useState, useEffect } from 'react';
import { useCoffee } from '../CoffeeContext';

const TwoFactorAuth = () => {
    const [qrCodeUrl, setQrCodeUrl] = useState('');
    const [isEnabled, setIsEnabled] = useState(false);
    const [verificationCode, setVerificationCode] = useState('');
    const [setupEmail, setSetupEmail] = useState('');
    const [showSetupVerification, setShowSetupVerification] = useState(false);
    const { authenticatedFetch, accessToken, user, loginUser } = useCoffee();

    // Function to fetch the current 2FA status
    const fetch2FAStatus = async () => {
        if (!accessToken) return; // Don't fetch if not authenticated
        try {
            // Assuming your backend has an endpoint to get user details including 2FA status
            const response = await authenticatedFetch('/api/users/me/');
            setIsEnabled(response.is_2fa_enabled); // Assuming the user object includes is_2fa_enabled
        } catch (error) {
            console.error('Error fetching 2FA status:', error);
        }
    };

    // Fetch status on component mount and when access token changes
    useEffect(() => {
        fetch2FAStatus();
    }, [accessToken]); // Rerun when access token changes

    const setup2FA = async () => {
        try {
            console.log('Access Token before setup fetch:', accessToken); // Keep this log for now
             // Ensure email is provided for setup
            if (!setupEmail) {
                alert('Please enter your email address.');
                return;
            }
            // Call the backend endpoint to initiate 2FA setup (generate secret and QR code)
            const response = await authenticatedFetch(
                'http://127.0.0.1:8000/api/users/setup-2fa/',
                {
                    method: 'POST',
                    // Send email to associate with QR code (backend uses user.email, but sending explicitly might be good for clarity/future flexibility)
                    body: JSON.stringify({ email: setupEmail }),
                    headers: {
                         'Content-Type': 'application/json'
                    }
                }
            );
            setQrCodeUrl(response.qr_code_url);
            // We don't set isEnabled here, it's set after verification
            setShowSetupVerification(true); // Show the verification input after QR code is displayed
        } catch (error) {
            console.error('Error setting up 2FA:', error);
            alert('Error setting up 2FA. Please try again.');
        }
    };

    const verify2FASetup = async () => {
        try {
             console.log('Access Token before setup verification fetch:', accessToken); // Keep this log
             // Call the backend endpoint to verify the code and enable 2FA
            const response = await authenticatedFetch(
                'http://127.0.0.1:8000/api/users/verify-2fa-setup/',
                {
                    method: 'POST',
                    body: JSON.stringify({ code: verificationCode }),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );
            if (response.status === 'success') {
                alert('2FA enabled successfully!');
                setIsEnabled(true); // Update frontend state
                setShowSetupVerification(false); // Hide setup verification section
                setVerificationCode(''); // Clear the input
            } else {
                alert('Invalid verification code.');
                 setVerificationCode(''); // Clear the input
            }
        } catch (error) {
            console.error('Error verifying 2FA setup:', error);
            alert('Error verifying 2FA. Please try again.');
             setVerificationCode(''); // Clear the input on error
        }
    };

    const disable2FA = async () => {
        try {
             console.log('Access Token before disable fetch:', accessToken); // Keep this log
            // Call the backend endpoint to disable 2FA
            const response = await authenticatedFetch(
                'http://127.0.0.1:8000/api/users/disable-2fa/',
                {
                    method: 'POST',
                }
            );
            if (response.status === 'success') {
                alert('2FA disabled successfully!');
                setIsEnabled(false); // Update frontend state
                setQrCodeUrl(''); // Clear QR code and secret
                setSetupEmail('');
                setVerificationCode('');
                setShowSetupVerification(false);
            } else {
                 // This case might indicate an issue on the backend even if status is not 'success'
                 alert('Failed to disable 2FA.');
                 console.error('Unexpected response during 2FA disable:', response);
            }
        } catch (error) {
            console.error('Error disabling 2FA:', error);
            alert('Error disabling 2FA. Please try again.');
        }
    };

    return (
        <div>
            <h2>Two-Factor Authentication</h2>
            {isEnabled ? (
                // If 2FA is enabled, show disable button
                <button onClick={disable2FA}>Disable 2FA</button>
            ) : (
                // If 2FA is not enabled, show enable button and setup flow
                <div>
                    {!showSetupVerification ? (
                        // Show email input and Enable button initially
                        <>
                            <p>Enter your email to set up 2FA:</p>
                            <input
                                type="email"
                                placeholder="Enter email"
                                value={setupEmail}
                                onChange={(e) => setSetupEmail(e.target.value)}
                                required
                            />
                            <button onClick={setup2FA}>Enable 2FA</button>
                        </>
                    ) : (
                        // Show QR code and verification input after setup initiated
                        <div>
                            <p>Scan the QR code with Google Authenticator:</p>
                            {qrCodeUrl && <img src={qrCodeUrl} alt="QR Code" />} {/* Only show img if qrCodeUrl exists */}
                            <input
                                type="text"
                                placeholder="Enter 6-digit code"
                                value={verificationCode}
                                onChange={(e) => setVerificationCode(e.target.value)}
                            />
                            <button onClick={verify2FASetup}>Verify Setup</button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default TwoFactorAuth; 