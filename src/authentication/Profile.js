import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import styles from './styles/Profile.module.css';
import { getProfile, updateProfile } from '../services/authService';

const Profile = () => {
    const history = useHistory();
    const [user, setUser] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        username: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        address: '',
        current_password: '',
        new_password: '',
        new_password_confirm: ''
    });
    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const userData = await getProfile();
            setUser(userData);
            setFormData({
                username: userData.username || '',
                first_name: userData.first_name || '',
                last_name: userData.last_name || '',
                phone_number: userData.phone_number || '',
                address: userData.address || '',
                current_password: '',
                new_password: '',
                new_password_confirm: ''
            });
        } catch (error) {
            console.error('Error fetching profile:', error);
            setMessage('Failed to load profile. Please try again.');
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear error for this field when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrors({});
        setMessage('');

        try {
            const submitData = {
                username: formData.username,
                first_name: formData.first_name,
                last_name: formData.last_name,
                phone_number: formData.phone_number,
                address: formData.address
            };

            // Only include password fields if they are filled
            if (formData.current_password && formData.new_password && formData.new_password_confirm) {
                submitData.current_password = formData.current_password;
                submitData.new_password = formData.new_password;
                submitData.new_password_confirm = formData.new_password_confirm;
            }

            const data = await updateProfile(submitData);
            setMessage('Profile updated successfully!');
            setUser(data.user);
            setIsEditing(false);
            // Clear password fields
            setFormData(prev => ({
                ...prev,
                current_password: '',
                new_password: '',
                new_password_confirm: ''
            }));
        } catch (error) {
            console.error('Error updating profile:', error);
            if (error.validationErrors) {
                // Handle API validation errors
                setErrors(error.validationErrors);
            } else {
                setMessage('An error occurred while updating your profile.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = () => {
        setIsEditing(false);
        setErrors({});
        setMessage('');
        // Reset form data to original user data
        if (user) {
            setFormData({
                username: user.username || '',
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                phone_number: user.phone_number || '',
                address: user.address || '',
                current_password: '',
                new_password: '',
                new_password_confirm: ''
            });
        }
    };

    if (!user) {
        return <div className={styles.loading}>Loading profile...</div>;
    }

    return (
        <div className={styles.profileContainer}>
            <div className={styles.profileCard}>
                <button 
                    onClick={() => history.goBack()} 
                    className={styles.backButton}
                >
                    ← Back
                </button>
                <h1 className={styles.title}>My Profile</h1>
                
                {message && (
                    <div className={styles.successMessage}>
                        {message}
                    </div>
                )}

                <div className={styles.profileInfo}>
                    <div className={styles.infoSection}>
                        <h3>Account Information</h3>
                        <div className={styles.infoRow}>
                            <span className={styles.label}>Email:</span>
                            <span className={styles.value}>{user.email}</span>
                        </div>
                        <div className={styles.infoRow}>
                            <span className={styles.label}>Member since:</span>
                            <span className={styles.value}>
                                {new Date(user.date_joined).toLocaleDateString()}
                            </span>
                        </div>
                        <div className={styles.infoRow}>
                            <span className={styles.label}>Last login:</span>
                            <span className={styles.value}>
                                {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                            </span>
                        </div>
                        <div className={styles.infoRow}>
                            <span className={styles.label}>Account Status:</span>
                            <span className={`${styles.value} ${user.is_profile_complete ? styles.complete : styles.incomplete}`}>
                                {user.is_profile_complete ? 'Complete' : 'Incomplete'}
                            </span>
                        </div>
                        {!user.is_profile_complete && (
                            <div className={styles.incompleteWarning}>
                                <strong>Account Incomplete</strong>
                                <p>Please fill in the following required fields:</p>
                                <ul>
                                    {user.missing_fields.map((field, index) => (
                                        <li key={index}>{field}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {!isEditing ? (
                        <div className={styles.infoSection}>
                            <h3>Personal Information</h3>
                            <div className={styles.infoRow}>
                                <span className={styles.label}>Username:</span>
                                <span className={styles.value}>{user.username}</span>
                            </div>
                            <div className={styles.infoRow}>
                                <span className={styles.label}>First Name:</span>
                                <span className={styles.value}>{user.first_name || 'Not set'}</span>
                            </div>
                            <div className={styles.infoRow}>
                                <span className={styles.label}>Last Name:</span>
                                <span className={styles.value}>{user.last_name || 'Not set'}</span>
                            </div>
                            <div className={styles.infoRow}>
                                <span className={styles.label}>Phone:</span>
                                <span className={styles.value}>{user.phone_number || 'Not set'}</span>
                            </div>
                            <div className={styles.infoRow}>
                                <span className={styles.label}>Address:</span>
                                <span className={styles.value}>{user.address || 'Not set'}</span>
                            </div>
                            <button 
                                className={styles.editButton}
                                onClick={() => setIsEditing(true)}
                            >
                                Edit Profile
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className={styles.editForm}>
                            <h3>Edit Personal Information</h3>
                            <p className={styles.requiredNote}>* Required fields</p>
                            
                            <div className={styles.formGroup}>
                                <label htmlFor="username">Username *</label>
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleInputChange}
                                    className={errors.username ? styles.errorInput : ''}
                                    required
                                />
                                {errors.username && <span className={styles.error}>{errors.username}</span>}
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="first_name">First Name *</label>
                                <input
                                    type="text"
                                    id="first_name"
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleInputChange}
                                    className={errors.first_name ? styles.errorInput : ''}
                                    required
                                />
                                {errors.first_name && <span className={styles.error}>{errors.first_name}</span>}
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="last_name">Last Name *</label>
                                <input
                                    type="text"
                                    id="last_name"
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleInputChange}
                                    className={errors.last_name ? styles.errorInput : ''}
                                    required
                                />
                                {errors.last_name && <span className={styles.error}>{errors.last_name}</span>}
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="phone_number">Phone Number *</label>
                                <input
                                    type="text"
                                    id="phone_number"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleInputChange}
                                    className={errors.phone_number ? styles.errorInput : ''}
                                    required
                                />
                                {errors.phone_number && <span className={styles.error}>{errors.phone_number}</span>}
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="address">Address *</label>
                                <textarea
                                    id="address"
                                    name="address"
                                    value={formData.address}
                                    onChange={handleInputChange}
                                    className={errors.address ? styles.errorInput : ''}
                                    rows="3"
                                    required
                                />
                                {errors.address && <span className={styles.error}>{errors.address}</span>}
                            </div>

                            <div className={styles.passwordSection}>
                                <h4>Change Password (optional)</h4>
                                <p className={styles.passwordNote}>Leave blank to keep current password</p>
                                
                                <div className={styles.formGroup}>
                                    <label htmlFor="current_password">Current Password</label>
                                    <input
                                        type="password"
                                        id="current_password"
                                        name="current_password"
                                        value={formData.current_password}
                                        onChange={handleInputChange}
                                        className={errors.current_password ? styles.errorInput : ''}
                                    />
                                    {errors.current_password && <span className={styles.error}>{errors.current_password}</span>}
                                </div>

                                <div className={styles.formGroup}>
                                    <label htmlFor="new_password">New Password</label>
                                    <input
                                        type="password"
                                        id="new_password"
                                        name="new_password"
                                        value={formData.new_password}
                                        onChange={handleInputChange}
                                        className={errors.new_password ? styles.errorInput : ''}
                                    />
                                    {errors.new_password && <span className={styles.error}>{errors.new_password}</span>}
                                </div>

                                <div className={styles.formGroup}>
                                    <label htmlFor="new_password_confirm">Confirm New Password</label>
                                    <input
                                        type="password"
                                        id="new_password_confirm"
                                        name="new_password_confirm"
                                        value={formData.new_password_confirm}
                                        onChange={handleInputChange}
                                        className={errors.new_password_confirm ? styles.errorInput : ''}
                                    />
                                    {errors.new_password_confirm && <span className={styles.error}>{errors.new_password_confirm}</span>}
                                </div>
                            </div>

                            <div className={styles.formButtons}>
                                <button 
                                    type="submit" 
                                    className={styles.saveButton}
                                    disabled={loading}
                                >
                                    {loading ? 'Saving...' : 'Save Changes'}
                                </button>
                                <button 
                                    type="button" 
                                    className={styles.cancelButton}
                                    onClick={handleCancel}
                                    disabled={loading}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Profile; 