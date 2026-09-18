import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './Clientes.css';

const Clientes = () => {
  const { user } = useAuth();
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nombre: '',
    apellido: '',
    documento: '',
    telefono: '',
    fecha_nacimiento: '',
    direccion: '',
    ciudad: ''
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (user?.tipo_usuario === 'admin') {
      fetchClientes();
    } else {
      fetchMiInformacion();
    }
  }, [user]);

  const fetchClientes = async () => {
    try {
      const response = await api.get('/clientes');
      setClientes(response.data);
    } catch (error) {
      console.error('Error al obtener clientes:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMiInformacion = async () => {
    try {
      const response = await api.get('/clientes/mi-informacion');
      setClientes([response.data]);
    } catch (error) {
      console.error('Error al obtener información:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      await api.post('/clientes', formData);
      setShowForm(false);
      setFormData({
        email: '',
        password: '',
        nombre: '',
        apellido: '',
        documento: '',
        telefono: '',
        fecha_nacimiento: '',
        direccion: '',
        ciudad: ''
      });
      fetchClientes();
    } catch (err) {
      setError(err.response?.data?.error || 'Error al crear cliente');
    }
  };

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  return (
    <div className="clientes-page">
      <div className="page-header">
        <h1>Clientes Bancarios</h1>
        {user?.tipo_usuario === 'admin' && (
          <button onClick={() => setShowForm(!showForm)} className="btn-primary">
            {showForm ? 'Cancelar' : 'Crear Cliente'}
          </button>
        )}
      </div>

      {showForm && user?.tipo_usuario === 'admin' && (
        <form className="cliente-form" onSubmit={handleSubmit}>
          <h2>Nuevo Cliente</h2>
          {error && <div className="error-message">{error}</div>}
          <div className="form-row">
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Contraseña *</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Nombre *</label>
              <input
                type="text"
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Apellido *</label>
              <input
                type="text"
                value={formData.apellido}
                onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                required
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Documento *</label>
              <input
                type="text"
                value={formData.documento}
                onChange={(e) => setFormData({ ...formData, documento: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Teléfono</label>
              <input
                type="text"
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Fecha de Nacimiento</label>
              <input
                type="date"
                value={formData.fecha_nacimiento}
                onChange={(e) => setFormData({ ...formData, fecha_nacimiento: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Ciudad</label>
              <input
                type="text"
                value={formData.ciudad}
                onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
              />
            </div>
          </div>
          <div className="form-group">
            <label>Dirección</label>
            <input
              type="text"
              value={formData.direccion}
              onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
            />
          </div>
          <button type="submit" className="btn-primary">Crear Cliente</button>
        </form>
      )}

      <div className="clientes-list">
        {clientes.map((cliente) => (
          <div key={cliente.id} className="cliente-card">
            <h3>{cliente.nombre} {cliente.apellido}</h3>
            <div className="cliente-info">
              <p><strong>Email:</strong> {cliente.email}</p>
              <p><strong>Documento:</strong> {cliente.documento}</p>
              <p><strong>Teléfono:</strong> {cliente.telefono || 'N/A'}</p>
              <p><strong>Estado:</strong> {cliente.estado}</p>
              {cliente.ciudad && <p><strong>Ciudad:</strong> {cliente.ciudad}</p>}
            </div>
          </div>
        ))}
        {clientes.length === 0 && (
          <div className="empty-state">No hay clientes registrados</div>
        )}
      </div>
    </div>
  );
};

export default Clientes;


