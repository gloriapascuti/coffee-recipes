const API_URL = 'http://127.0.0.1:8000/api'; // Correct backend API base URL

export const login = async (username, password) => {
  try {
    const response = await fetch(`${API_URL}/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    // JWT returns access and refresh tokens
    return {
      access: data.access,
      refresh: data.refresh,
      user_id: data.user_id, // If backend includes this
      username: data.username // If backend includes this
    };

  } catch (error) {
    console.error('Error during login:', error);
    throw error;
  }
};

export const refreshToken = async (refreshToken) => {
  try {
    const response = await fetch(`${API_URL}/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Could not refresh token');
    }

    const data = await response.json();
    return data.access; // JWT refresh returns just the new access token

  } catch (error) {
    console.error('Error during token refresh:', error);
    throw error;
  }
};

export const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
};

export const getProfile = async () => {
  try {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await fetch(`${API_URL}/users/profile/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch profile' }));
      throw new Error(errorData.detail || `Failed to fetch profile (${response.status})`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching profile:', error);
    throw error;
  }
};

export const updateProfile = async (profileData) => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_URL}/users/profile/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });

    const data = await response.json();

    if (!response.ok) {
      // Throw the actual error data for validation errors
      const error = new Error('Failed to update profile');
      error.validationErrors = data;
      throw error;
    }

    return data;
  } catch (error) {
    console.error('Error updating profile:', error);
    throw error;
  }
};