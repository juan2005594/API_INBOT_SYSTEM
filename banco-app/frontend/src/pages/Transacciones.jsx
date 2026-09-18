import { useState, useEffect } from 'react';
import api from '../services/api';
import './Transacciones.css';

const Transacciones = () => {
  const [transacciones, setTransacciones] = useState([]);
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [tipoTransaccion, setTipoTransaccion] = useState('consignacion');
  const [formData, setFormData] = useState({
    producto_id: '',
    monto: '',
    descripcion: ''
  });
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTransacciones();
    fetchProductos();
  }, []);

  const fetchTransacciones = async () => {
    try {
      const response = await api.get('/transacciones');
      setTransacciones(response.data);
    } catch (error) {
      console.error('Error al obtener transacciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProductos = async () => {
    try {
      const response = await api.get('/productos');
      setProductos(response.data);
    } catch (error) {
      console.error('Error al obtener productos:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const endpoint = tipoTransaccion === 'consignacion' ? '/transacciones/consignacion' : '/transacciones/retiro';
      await api.post(endpoint, formData);
      setShowForm(false);
      setFormData({ producto_id: '', monto: '', descripcion: '' });
      fetchTransacciones();
      fetchProductos();
    } catch (err) {
      setError(err.response?.data?.error || 'Error al realizar transacción');
    }
  };

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  return (
    <div className="transacciones-page">
      <div className="page-header">
        <h1>Transacciones Bancarias</h1>
        <div className="header-buttons">
          <button
            onClick={() => {
              setTipoTransaccion('consignacion');
              setShowForm(!showForm);
            }}
            className="btn-success"
          >
            {showForm && tipoTransaccion === 'consignacion' ? 'Cancelar' : 'Consignar'}
          </button>
          <button
            onClick={() => {
              setTipoTransaccion('retiro');
              setShowForm(!showForm);
            }}
            className="btn-danger"
          >
            {showForm && tipoTransaccion === 'retiro' ? 'Cancelar' : 'Retirar'}
          </button>
        </div>
      </div>

      {showForm && (
        <form className="transaccion-form" onSubmit={handleSubmit}>
          <h2>{tipoTransaccion === 'consignacion' ? 'Realizar Consignación' : 'Realizar Retiro'}</h2>
          {error && <div className="error-message">{error}</div>}
          <div className="form-group">
            <label>Producto Bancario *</label>
            <select
              value={formData.producto_id}
              onChange={(e) => setFormData({ ...formData, producto_id: e.target.value })}
              required
            >
              <option value="">Seleccione un producto</option>
              {productos.map((producto) => (
                <option key={producto.id} value={producto.id}>
                  {producto.numero_producto} - ${parseFloat(producto.saldo).toLocaleString('es-CO', { minimumFractionDigits: 2 })}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Monto *</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={formData.monto}
              onChange={(e) => setFormData({ ...formData, monto: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Descripción</label>
            <input
              type="text"
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              placeholder="Descripción de la transacción"
            />
          </div>
          <button type="submit" className="btn-primary">
            {tipoTransaccion === 'consignacion' ? 'Consignar' : 'Retirar'}
          </button>
        </form>
      )}

      <div className="transacciones-list">
        <h2>Historial de Transacciones</h2>
        {transacciones.length === 0 ? (
          <div className="empty-state">No hay transacciones registradas</div>
        ) : (
          <table className="transacciones-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Monto</th>
                <th>Saldo Anterior</th>
                <th>Saldo Nuevo</th>
                <th>Descripción</th>
              </tr>
            </thead>
            <tbody>
              {transacciones.map((transaccion) => (
                <tr key={transaccion.id}>
                  <td>{new Date(transaccion.fecha_transaccion).toLocaleString('es-CO')}</td>
                  <td>
                    <span className={`badge badge-${transaccion.tipo_transaccion}`}>
                      {transaccion.tipo_transaccion === 'consignacion' ? 'Consignación' : 'Retiro'}
                    </span>
                  </td>
                  <td className={transaccion.tipo_transaccion === 'consignacion' ? 'positive' : 'negative'}>
                    {transaccion.tipo_transaccion === 'consignacion' ? '+' : '-'}
                    ${parseFloat(transaccion.monto).toLocaleString('es-CO', { minimumFractionDigits: 2 })}
                  </td>
                  <td>${parseFloat(transaccion.saldo_anterior).toLocaleString('es-CO', { minimumFractionDigits: 2 })}</td>
                  <td>${parseFloat(transaccion.saldo_nuevo).toLocaleString('es-CO', { minimumFractionDigits: 2 })}</td>
                  <td>{transaccion.descripcion || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Transacciones;


