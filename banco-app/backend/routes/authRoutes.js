import express from 'express';
import {
  register,
  login,
  setup2FA,
  verify2FA,
  disable2FA
} from '../controllers/authController.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();

router.post('/register', register);
router.post('/login', login);
router.get('/setup-2fa', authenticateToken, setup2FA);
router.post('/verify-2fa', authenticateToken, verify2FA);
router.post('/disable-2fa', authenticateToken, disable2FA);

export default router;


