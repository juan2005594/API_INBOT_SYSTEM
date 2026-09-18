import speakeasy from 'speakeasy';
import QRCode from 'qrcode';

/**
 * Genera un secreto para 2FA
 */
export const generateSecret = (email) => {
  return speakeasy.generateSecret({
    name: `Banco App (${email})`,
    issuer: 'Banco App',
    length: 32
  });
};

/**
 * Genera un código QR para escanear con Google Authenticator
 */
export const generateQRCode = async (secret) => {
  try {
    const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);
    return qrCodeUrl;
  } catch (error) {
    throw new Error('Error al generar código QR: ' + error.message);
  }
};

/**
 * Verifica un token 2FA
 */
export const verifyToken = (token, secret) => {
  return speakeasy.totp.verify({
    secret: secret,
    encoding: 'base32',
    token: token,
    window: 2 // Permite tokens de los últimos 2 períodos (60 segundos cada uno)
  });
};

/**
 * Genera un token temporal para verificación
 */
export const generateToken = (secret) => {
  return speakeasy.totp({
    secret: secret,
    encoding: 'base32'
  });
};


