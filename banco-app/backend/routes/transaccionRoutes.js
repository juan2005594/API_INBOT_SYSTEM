import express from 'express';
import {
  realizarConsignacion,
  realizarRetiro,
  obtenerTransacciones
} from '../controllers/transaccionController.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();

router.use(authenticateToken);

router.post('/consignacion', realizarConsignacion);
router.post('/retiro', realizarRetiro);
router.get('/', obtenerTransacciones);

export default router;


