import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalProductos: 0,
    totalSaldo: 0,
    totalTransacciones: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [productosRes, transaccionesRes] = await Promise.all([
          api.get('/productos'),
          api.get('/transacciones?limit=1')
        ]);

        const productos = productosRes.data;
        const totalSaldo = productos.reduce((sum, p) => sum + parseFloat(p.saldo || 0), 0);

        setStats({
          totalProductos: productos.length,
          totalSaldo,
          totalTransacciones: transaccionesRes.data.length
        });
      } catch (error) {
        console.error('Error al cargar estadísticas:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div className="dashboard-loading">Cargando...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Bienvenido, {user?.nombre} {user?.apellido}</h1>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">💳</div>
          <div className="stat-info">
            <h3>Productos Bancarios</h3>
            <p className="stat-value">{stats.totalProductos}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-info">
            <h3>Saldo Total</h3>
            <p className="stat-value">${stats.totalSaldo.toLocaleString('es-CO', { minimumFractionDigits: 2 })}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <h3>Transacciones</h3>
            <p className="stat-value">{stats.totalTransacciones}</p>
          </div>
        </div>
      </div>
      <div className="dashboard-info">
        <h2>Información del Sistema</h2>
        <p>Rol: <strong>{user?.tipo_usuario === 'admin' ? 'Administrador' : 'Cliente'}</strong></p>
        <p>2FA: <strong>{user?.two_factor_enabled ? 'Habilitado' : 'Deshabilitado'}</strong></p>
      </div>
    </div>
  );
};

export default Dashboard;


