import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verificar si el token es válido obteniendo información del usuario
      // Por ahora, solo guardamos el token
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password, twoFactorToken = null) => {
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
        twoFactorToken
      });

      if (response.data.requiresTwoFactor) {
        return { requiresTwoFactor: true };
      }

      const { token: newToken, user: userData } = response.data;
      localStorage.setItem('token', newToken);
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      setToken(newToken);
      setUser(userData);
      return { success: true };
    } catch (error) {
      throw error.response?.data || { error: 'Error al iniciar sesión' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
  };

  const register = async (userData) => {
    try {
      await api.post('/auth/register', userData);
      return { success: true };
    } catch (error) {
      throw error.response?.data || { error: 'Error al registrar usuario' };
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};


