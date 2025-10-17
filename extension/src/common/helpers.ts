/**
 * Helper files shared across the project
 */
export const API_BASE_URL = 'http://localhost:8000/api/v1';

export const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString();
};

export const apiRequest = async (url: string, options: RequestInit = {}) => {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (err) {
    // Re-throw for the main error handler to deal with
    throw err;
  }
};
