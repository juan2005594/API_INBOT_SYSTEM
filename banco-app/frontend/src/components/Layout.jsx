import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>🏦 Banco App</h1>
        </div>
        <div className="navbar-menu">
          <Link to="/" className="nav-link">Dashboard</Link>
          {user?.tipo_usuario === 'admin' && (
            <Link to="/clientes" className="nav-link">Clientes</Link>
          )}
          <Link to="/productos" className="nav-link">Productos</Link>
          <Link to="/transacciones" className="nav-link">Transacciones</Link>
          <Link to="/configuracion-2fa" className="nav-link">2FA</Link>
          <div className="user-info">
            <span>{user?.nombre} {user?.apellido}</span>
            <button onClick={handleLogout} className="logout-btn">Salir</button>
          </div>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;


