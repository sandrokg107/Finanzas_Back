# Mejoras al Sistema de Deudas

## Nuevas Funcionalidades

### 1. **Número Total de Cuotas**

Ahora puedes especificar exactamente cuántas cuotas tiene tu deuda (ej: 12 cuotas, 24 cuotas, etc.). El sistema calculará automáticamente el cronograma de pagos.

### 2. **Día del Mes de Pago**

Define en qué día del mes debes realizar cada pago (ej: día 12 de cada mes). El sistema generará los pagos siempre en ese día específico.

**Ejemplo:**

- Si eliges día 12: Pagarás el 12 de enero, 12 de febrero, 12 de marzo, etc.
- Si eliges día 31 en un mes que no tiene 31 días (como febrero), automáticamente se ajustará al último día del mes.

### 3. **Recordatorios de Pago**

Configura con cuántos días de anticipación quieres recibir recordatorios:

- **1 día antes**: Te avisará el día anterior
- **3 días antes**: Te avisará 3 días antes (recomendado)
- **5 días antes**: Te avisará 5 días antes
- **7 días antes**: Te avisará con una semana de anticipación

### 4. **Alertas Inteligentes**

En la parte superior de la página de Deudas verás un panel de alertas que muestra:

- **Pagos vencidos**: Resaltados en rojo con un ícono de alerta
- **Pagos próximos**: Según tus días de recordatorio configurados
- **Días restantes**: Cuenta regresiva hasta cada fecha de pago
- **Botón rápido**: "Pagar Ahora" directo desde las alertas

### 5. **Control de Fechas**

**Importante:**

- ✅ **Puedes pagar ANTES** de la fecha de vencimiento
- ✅ **Puedes pagar EN** la fecha de vencimiento
- ❌ **NO puedes registrar pagos DESPUÉS** de la fecha de vencimiento

Esto te ayuda a mantener un buen historial y evita pagos atrasados.

### 6. **Información Mejorada en Tarjetas**

Cada tarjeta de deuda ahora muestra:

- **Cuotas pendientes**: "X de Y pendientes" (ej: "5 de 12 pendientes")
- **Día de pago**: "Día 12 de cada mes"
- **Recordatorio**: "3 días antes"
- **Fechas**: Inicio y vencimiento final

## Cómo Usar

### Crear una Nueva Deuda

1. **Clic en "Nueva Deuda"**

2. **Llenar información básica:**
   - Acreedor (requerido)
   - Monto Total (requerido)

3. **Configurar plan de pagos:**
   - **Pago Mensual**: Cuánto pagarás cada mes
   - **Total de Cuotas**: Cuántas cuotas en total (ej: 12)
   - **Día de Pago**: Qué día del mes (ej: 12)
   - **Fecha Inicio**: Cuándo empieza el primer pago
   - **Fecha Vencimiento**: Cuándo termina la deuda (opcional si ya pusiste total de cuotas)
   - **Días de Anticipación**: Cuándo quieres que te recuerde (1, 3, 5 o 7 días)

4. **Descripción** (opcional): Notas adicionales

### Ejemplo Práctico

**Escenario:** Sacaste una laptop en 12 cuotas de S/ 200 cada una, empiezas a pagar el 12 de marzo

```
Acreedor: Tienda Electro
Monto Total: 2400
Pago Mensual: 200
Total de Cuotas: 12
Día de Pago: 12
Fecha Inicio: 2026-03-12
Días de Anticipación: 3 días antes
```

**Resultado:**

- El sistema generará automáticamente 12 pagos de S/ 200
- Cada uno el día 12 de cada mes
- Te recordará 3 días antes (el 9 de cada mes)
- Verás: "5 de 12 pendientes" conforme vayas pagando

## Instalación de Mejoras

### Backend

1. **Instalar nueva dependencia:**

```bash
pip install python-dateutil==2.9.0
```

2. **Ejecutar migración de base de datos:**

```bash
cd backend
python scripts/add_debt_improvements.py
```

3. **Reiniciar el servidor:**

```bash
uvicorn app.main:app --reload
```

### Frontend

No requiere cambios adicionales, solo actualizar el código.

## API Endpoints Nuevos

### Obtener Recordatorios

```http
GET /debts/reminders/upcoming
```

Devuelve todos los pagos que están próximos a vencer según los días de recordatorio configurados en cada deuda.

**Respuesta:**

```json
[
  {
    "debt_id": 1,
    "debt_creditor": "Tienda Electro",
    "payment_id": 5,
    "payment_amount": 200.0,
    "due_date": "2026-03-12",
    "days_until_due": 2,
    "is_overdue": false
  }
]
```

## Solución de Problemas

### "No puedo pagar después de la fecha"

Esto es intencional. Si necesitas registrar un pago atrasado, contacta al administrador del sistema.

### "El día 31 no aparece en febrero"

El sistema ajusta automáticamente al último día del mes (28 o 29 en febrero).

### "No veo las alertas"

Asegúrate de haber configurado:

1. Pago mensual
2. Fecha de inicio
3. Días de recordatorio

## Beneficios

✅ **Nunca olvides un pago**: Recordatorios automáticos
✅ **Control total**: Sabes exactamente cuántas cuotas te quedan
✅ **Organización**: Cada deuda en su día específico del mes
✅ **Historial limpio**: Evita pagos atrasados
✅ **Vista rápida**: Panel de alertas en la parte superior

---

**¿Preguntas o sugerencias?** Abre un issue en el repositorio.
