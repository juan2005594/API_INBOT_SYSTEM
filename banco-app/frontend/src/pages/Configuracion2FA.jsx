import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './Configuracion2FA.css';

const Configuracion2FA = () => {
  const { user } = useAuth();
  const [qrCode, setQrCode] = useState(null);
  const [secret, setSecret] = useState('');
  const [verificationToken, setVerificationToken] = useState('');
  const [enabled, setEnabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user?.two_factor_enabled) {
      setEnabled(true);
    }
  }, [user]);

  const handleSetup2FA = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.get('/auth/setup-2fa');
      setQrCode(response.data.qrCode);
      setSecret(response.data.secret);
      setEnabled(response.data.enabled);
    } catch (err) {
      setError(err.response?.data?.error || 'Error al configurar 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify2FA = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await api.post('/auth/verify-2fa', { token: verificationToken });
      setSuccess('2FA habilitado exitosamente');
      setEnabled(true);
      setVerificationToken('');
    } catch (err) {
      setError(err.response?.data?.error || 'Error al verificar código 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!window.confirm('¿Estás seguro de que deseas deshabilitar 2FA?')) {
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await api.post('/auth/disable-2fa');
      setSuccess('2FA deshabilitado exitosamente');
      setEnabled(false);
      setQrCode(null);
      setSecret('');
    } catch (err) {
      setError(err.response?.data?.error || 'Error al deshabilitar 2FA');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="config-2fa-page">
      <h1>Configuración de Autenticación de Dos Factores (2FA)</h1>

      <div className="config-2fa-card">
        <div className="status-section">
          <h2>Estado Actual</h2>
          <div className={`status-badge ${enabled ? 'enabled' : 'disabled'}`}>
            {enabled ? '✓ 2FA Habilitado' : '✗ 2FA Deshabilitado'}
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        {!enabled && !qrCode && (
          <div className="setup-section">
            <h3>Configurar 2FA</h3>
            <p>
              La autenticación de dos factores añade una capa adicional de seguridad a tu cuenta.
              Necesitarás una aplicación de autenticación como Google Authenticator o Authy.
            </p>
            <button
              onClick={handleSetup2FA}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Configurando...' : 'Configurar 2FA'}
            </button>
          </div>
        )}

        {qrCode && !enabled && (
          <div className="verification-section">
            <h3>Escanea el Código QR</h3>
            <p>Usa tu aplicación de autenticación para escanear este código:</p>
            <div className="qr-container">
              <img src={qrCode} alt="QR Code para 2FA" />
            </div>
            <p className="secret-text">
              <strong>O ingresa este código manualmente:</strong>
              <code>{secret}</code>
            </p>
            <form onSubmit={handleVerify2FA}>
              <div className="form-group">
                <label>Código de Verificación (6 dígitos)</label>
                <input
                  type="text"
                  value={verificationToken}
                  onChange={(e) => setVerificationToken(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  maxLength="6"
                  required
                />
              </div>
              <button type="submit" disabled={loading || verificationToken.length !== 6} className="btn-primary">
                {loading ? 'Verificando...' : 'Verificar y Habilitar 2FA'}
              </button>
            </form>
          </div>
        )}

        {enabled && (
          <div className="disable-section">
            <h3>Deshabilitar 2FA</h3>
            <p>Si deseas deshabilitar la autenticación de dos factores, puedes hacerlo aquí.</p>
            <button
              onClick={handleDisable2FA}
              disabled={loading}
              className="btn-danger"
            >
              {loading ? 'Deshabilitando...' : 'Deshabilitar 2FA'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Configuracion2FA;

