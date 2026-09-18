import express from 'express';
import {
  crearCliente,
  obtenerClientes,
  obtenerCliente,
  obtenerMiInformacion
} from '../controllers/clienteController.js';
import { authenticateToken, requireAdmin } from '../middleware/auth.js';

const router = express.Router();

// Rutas que requieren autenticación
router.use(authenticateToken);

router.get('/mi-informacion', obtenerMiInformacion);
router.get('/:id', obtenerCliente);

// Rutas solo para admin
router.post('/', requireAdmin, crearCliente);
router.get('/', requireAdmin, obtenerClientes);

export default router;


