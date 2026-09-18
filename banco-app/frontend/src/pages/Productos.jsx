import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './Productos.css';

const Productos = () => {
  const { user } = useAuth();
  const [productos, setProductos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showSaldo, setShowSaldo] = useState(null);
  const [formData, setFormData] = useState({
    cliente_id: '',
    tipo_producto: 'cuenta_ahorros',
    saldo_inicial: 0
  });
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProductos();
    if (user?.tipo_usuario === 'admin') {
      fetchClientes();
    }
  }, [user]);

  const fetchClientes = async () => {
    try {
      const response = await api.get('/clientes');
      setClientes(response.data);
    } catch (error) {
      console.error('Error al obtener clientes:', error);
    }
  };

  const fetchProductos = async () => {
    try {
      const response = await api.get('/productos');
      setProductos(response.data);
    } catch (error) {
      console.error('Error al obtener productos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      await api.post('/productos', formData);
      setShowForm(false);
      setFormData({
        cliente_id: '',
        tipo_producto: 'cuenta_ahorros',
        saldo_inicial: 0
      });
      fetchProductos();
    } catch (err) {
      setError(err.response?.data?.error || 'Error al crear producto');
    }
  };

  const handleVerificarSaldo = async (productoId) => {
    try {
      const response = await api.get(`/productos/${productoId}/saldo`);
      setShowSaldo(response.data);
    } catch (error) {
      console.error('Error al verificar saldo:', error);
    }
  };

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  return (
    <div className="productos-page">
      <div className="page-header">
        <h1>Productos Bancarios</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? 'Cancelar' : 'Crear Producto'}
        </button>
      </div>

      {showForm && (
        <form className="producto-form" onSubmit={handleSubmit}>
          <h2>Nuevo Producto Bancario</h2>
          {error && <div className="error-message">{error}</div>}
          {user?.tipo_usuario === 'admin' && (
            <div className="form-group">
              <label>Cliente *</label>
              <select
                value={formData.cliente_id}
                onChange={(e) => setFormData({ ...formData, cliente_id: e.target.value })}
                required
              >
                <option value="">Seleccione un cliente</option>
                {clientes.map((cliente) => (
                  <option key={cliente.id} value={cliente.id}>
                    {cliente.nombre} {cliente.apellido} - {cliente.documento}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="form-group">
            <label>Tipo de Producto *</label>
            <select
              value={formData.tipo_producto}
              onChange={(e) => setFormData({ ...formData, tipo_producto: e.target.value })}
              required
            >
              <option value="cuenta_ahorros">Cuenta de Ahorros</option>
              <option value="cuenta_corriente">Cuenta Corriente</option>
              <option value="cdt">CDT</option>
              <option value="credito">Crédito</option>
            </select>
          </div>
          <div className="form-group">
            <label>Saldo Inicial</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.saldo_inicial}
              onChange={(e) => setFormData({ ...formData, saldo_inicial: parseFloat(e.target.value) || 0 })}
            />
          </div>
          <button type="submit" className="btn-primary">Crear Producto</button>
        </form>
      )}

      <div className="productos-list">
        {productos.map((producto) => (
          <div key={producto.id} className="producto-card">
            <div className="producto-header">
              <h3>{producto.numero_producto}</h3>
              <span className={`badge badge-${producto.estado}`}>{producto.estado}</span>
            </div>
            <div className="producto-info">
              <p><strong>Tipo:</strong> {producto.tipo_producto.replace('_', ' ').toUpperCase()}</p>
              <p><strong>Saldo:</strong> ${parseFloat(producto.saldo).toLocaleString('es-CO', { minimumFractionDigits: 2 })}</p>
              <p><strong>Fecha Apertura:</strong> {new Date(producto.fecha_apertura).toLocaleDateString('es-CO')}</p>
            </div>
            <button
              onClick={() => handleVerificarSaldo(producto.id)}
              className="btn-secondary"
            >
              Verificar Saldo
            </button>
          </div>
        ))}
        {productos.length === 0 && (
          <div className="empty-state">No hay productos bancarios registrados</div>
        )}
      </div>

      {showSaldo && (
        <div className="modal-overlay" onClick={() => setShowSaldo(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Saldo del Producto</h2>
            <div className="saldo-info">
              <p><strong>Número:</strong> {showSaldo.numero_producto}</p>
              <p><strong>Tipo:</strong> {showSaldo.tipo_producto.replace('_', ' ').toUpperCase()}</p>
              <p className="saldo-amount"><strong>Saldo Actual:</strong> ${parseFloat(showSaldo.saldo).toLocaleString('es-CO', { minimumFractionDigits: 2 })}</p>
              <p><strong>Estado:</strong> {showSaldo.estado}</p>
            </div>
            <button onClick={() => setShowSaldo(null)} className="btn-primary">Cerrar</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Productos;


