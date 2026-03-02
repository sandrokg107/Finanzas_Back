# 📄 Sistema de Comprobantes de Pago

## ✨ Nuevas Funcionalidades Implementadas

### 1. Modal de Registro de Pago

Al hacer clic en **"Pagar"** en cualquier cuota pendiente, se abre un modal moderno con:

#### Campos del Modal:

- **Método de Pago** (Requerido):
  - Efectivo
  - Tarjeta de Débito
  - Tarjeta de Crédito
  - Transferencia Bancaria
  - Yape
  - Plin
  - Otro

- **Comprobante** (Opcional):
  - Permite subir archivo PDF, PNG, JPG o JPEG
  - Tamaño máximo: 5MB
  - Vista previa en tiempo real para imágenes
  - Icono de PDF para archivos PDF

### 2. Visualización de Comprobantes

- Botón **"Ver"** con ícono de descarga para pagos con comprobante
- Descarga automática del archivo con el nombre original
- Compatible con PDF e imágenes

### 3. Backend - Nuevos Endpoints

#### POST `/debts/payments/{payment_id}/mark-paid`

Marca una cuota como pagada.

```json
{
  "payment_method": "Transferencia Bancaria",
  "paid_date": "2026-02-17" // Opcional, por defecto fecha actual
}
```

**Respuesta:**

```json
{
  "message": "Cuota marcada como pagada",
  "was_late": false,
  "paid_date": "2026-02-17"
}
```

#### POST `/debts/payments/{payment_id}/upload-voucher`

Sube un comprobante de pago (multipart/form-data).

**Parámetros:**

- `file`: Archivo PDF, PNG, JPG o JPEG (máx 5MB)

**Respuesta:**

```json
{
  "message": "Comprobante subido exitosamente",
  "filename": "comprobante-pago.pdf",
  "voucher_id": 123
}
```

#### GET `/debts/payments/{payment_id}/download-voucher`

Descarga el comprobante de pago.

**Respuesta:** Archivo binario (FileResponse)

#### DELETE `/debts/payments/{payment_id}/delete-voucher`

Elimina el comprobante de pago del sistema.

**Respuesta:** 204 No Content

---

## 🗄️ Cambios en Base de Datos

### Tabla `debt_payments`

Nuevas columnas agregadas:

```sql
ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);
ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS voucher_filename VARCHAR(255);
ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS voucher_path VARCHAR(512);
```

---

## 📁 Estructura de Archivos

### Backend

```
backend/
├── app/
│   ├── models/
│   │   └── debt_payment.py          # ✨ Actualizado con nuevos campos
│   ├── routers/
│   │   └── debts.py                  # ✨ Nuevos endpoints de comprobantes
│   └── schemas.py                    # ✨ DebtPaymentResponse actualizado
├── uploads/
│   └── vouchers/                     # 🆕 Directorio para comprobantes
└── scripts/
    └── migrate_payment_voucher.py    # 🆕 Script de migración
```

### Frontend

```
frontend/
└── src/
    └── pages/
        └── Debts.jsx                 # ✨ Modal de pago y visualización
```

---

## 🚀 Flujo de Uso

### Registrar un Pago:

1. Ir a la sección "Mis Deudas"
2. Expandir el cronograma de pagos de una deuda
3. Hacer clic en **"Pagar"** en una cuota pendiente
4. Seleccionar método de pago (obligatorio)
5. (Opcional) Subir comprobante PDF o imagen
6. Hacer clic en **"Confirmar Pago"**

### Ver/Descargar Comprobante:

1. En el cronograma de pagos, buscar pagos marcados con ✅
2. Si el pago tiene comprobante, aparece botón **"Ver"** 📥
3. Hacer clic para descargar el archivo

---

## 🎨 Características de Diseño

### Modal de Pago:

- ✅ Diseño glassmorphism consistente
- ✅ Animaciones suaves (fade-in, slide-in)
- ✅ Vista previa de imágenes en tiempo real
- ✅ Validación de archivos (tipo y tamaño)
- ✅ Botones con gradientes y efectos hover
- ✅ Responsive para móvil y desktop

### Visualización:

- ✅ Botón de descarga con ícono
- ✅ Sombras y efectos hover
- ✅ Integrado en tabla de cronograma

---

## 🔒 Seguridad

- ✅ Validación de tipo de archivo (solo PDF, PNG, JPG, JPEG)
- ✅ Límite de tamaño (5MB máximo)
- ✅ Nombres únicos generados con UUID
- ✅ Validación de permisos (solo el usuario dueño puede subir/descargar)
- ✅ Almacenamiento seguro en directorio `uploads/vouchers/`

---

## 📦 Dependencias Nuevas

### Backend

```txt
python-multipart==0.0.9
```

Instalación:

```bash
pip install python-multipart==0.0.9
```

### Frontend

No requiere dependencias adicionales (usa Axios existente).

---

## 🧪 Testing

### Probar Subida de Comprobante:

```bash
curl -X POST "http://localhost:8000/api/v1/debts/payments/1/upload-voucher" \
  -H "Authorization: Bearer {token}" \
  -F "file=@comprobante.pdf"
```

### Probar Descarga:

```bash
curl -X GET "http://localhost:8000/api/v1/debts/payments/1/download-voucher" \
  -H "Authorization: Bearer {token}" \
  --output comprobante_descargado.pdf
```

---

## 🐛 Solución de Problemas

### Error: "Tipo de archivo no permitido"

- ✅ Asegúrate de subir solo PDF, PNG, JPG o JPEG
- ✅ Verifica que el archivo no esté corrupto

### Error: "El archivo no debe superar 5MB"

- ✅ Comprime la imagen antes de subirla
- ✅ Convierte PDF a versión optimizada

### Error: "No hay comprobante para este pago"

- ✅ Verifica que el pago esté marcado como "Pagado"
- ✅ Confirma que se haya subido un comprobante previamente

### No aparece botón "Ver"

- ✅ El pago debe estar marcado como pagado
- ✅ Debe tener un comprobante asociado
- ✅ Refresca la página

---

## 📝 Notas Técnicas

### Almacenamiento:

- Los archivos se guardan en: `backend/uploads/vouchers/`
- Nombres únicos: `{uuid}.{extensión}`
- Metadata en base de datos:
  - `voucher_filename`: Nombre original del archivo
  - `voucher_path`: Ruta completa del archivo guardado

### Formato de Respuestas:

- Todos los endpoints siguen estándar REST
- Errores devuelven HTTPException con detail
- FileResponse para descarga con media_type correcto

---

## ✅ Checklist de Implementación

- [x] Modelo DebtPayment actualizado
- [x] Migración de base de datos ejecutada
- [x] Endpoints backend creados y testeados
- [x] Schemas actualizados
- [x] Modal de pago en frontend
- [x] Visualización de comprobantes
- [x] Validación de archivos
- [x] Directorio uploads creado
- [x] Dependencias instaladas
- [x] Documentación completa

---

## 🎯 Próximas Mejoras (Futuras)

- [ ] Miniatura de preview en cronograma
- [ ] Visor de PDF integrado (sin descarga)
- [ ] Eliminación de comprobantes desde UI
- [ ] Historial de comprobantes por deuda
- [ ] Notificaciones al subir comprobante
- [ ] Compresión automática de imágenes grandes
