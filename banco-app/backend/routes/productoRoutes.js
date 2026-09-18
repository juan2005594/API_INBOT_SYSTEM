import express from 'express';
import {
  crearProducto,
  obtenerProductos,
  obtenerProducto,
  verificarSaldo
} from '../controllers/productoController.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();

router.use(authenticateToken);

router.post('/', crearProducto);
router.get('/', obtenerProductos);
router.get('/:id', obtenerProducto);
router.get('/:id/saldo', verificarSaldo);

export default router;


