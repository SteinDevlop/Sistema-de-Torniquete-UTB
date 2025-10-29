# Casos de Prueba para API de Acceso

Este documento proporciona casos de prueba prácticos para probar el endpoint de reconocimiento facial.

## 🧪 Tests Automatizados

Los tests automatizados están en: `src/backend/app/tests/test_access_service.py`

Para ejecutarlos:
```bash
cd src
$env:PYTHONPATH = '.'
..\venv\Scripts\python.exe -m pytest backend\app\tests\test_access_service.py -v -s
```

---

## 📝 Casos de Prueba Manuales

### ✅ Caso 1: Crear Usuario con Embedding Facial

**Endpoint:** `POST /biometria/create`

**Request (Form Data):**
```bash
curl -X 'POST' \
  'http://localhost:8000/biometria/create' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'id_usuario=999&vector_facial=ALY8P4vIUj8HuTQ/z2ORPRlw2T64Jy49alKlPtqFWz9FFiY+nh1dP9kwSz9w/Ig9o9e5PtRzGj+rA5A+aMnfPuxvCj+Hi4Q+8Mm/PoJGqz16qmQ/MkJzPwLifj+unWw/tMIEP+aMZj/AGr8++d4aP4ZgJD9PWPA+ilodPyJdET5S/II+3A7PPjnFqz65Ivs+lWWuPluVBz+oFyM8CertPquJpz5ysV8/DxN5P/RmHD/dUbA+DE6jPuYpCj5z6zM/fxEjPoitIz/foWI/H/ZsP3RnDz+/WYA+db58Pp3xKz8651A/FjFIP+2kDD7wwIM+jY5zP3FGZj9PI2s/d6p4P3bpaD9NmdU7TIUSP7lR2D4E3jQ/Mzl+P8uhST+WjYo+EOiGPaMUVT8HcG8/eUgXPhAcUT8JY8w+PgIZPzRsyz5YGcg+pL+nPZjqMT8q4m8/raYZP/HFoj0duJQ+85AMPkZBQD1qFOo9fHlIP0G3ED7trWQ/sUBPPyk/gD44iwk/VxRbPu97Rj/u0io/H75OP8WShjz5E3Y/MHZZPyPIMD9ZqDo/ZGssP8Ucbj+U4T0/z+8qP5gsKT7i2AY+q3cKPxTkQT70f409IqpQOrKnfj9P5mI/yeBBPydwAT8u9cw97LkXP2NTWj/PIT4/xGkmP/4d2jy4MGU/oUwjPwkOVD8=&rfid_tag=RFID999&fecha_actualizacion=2025-10-20T20:00:00'
```

**Respuesta Esperada:**
```json
{
  "operation": "create",
  "success": true,
  "data": {
    "id_biometria": null,
    "id_usuario": 999,
    "vector_facial": "ALY8P4vIUj8HuTQ...",
    "facial_hash": "a3f2b1c4",
    "huella_hash": null,
    "rfid_tag": "RFID999",
    "fecha_actualizacion": "2025-10-20T20:00:00",
    "template_huella": null
  },
  "message": "Biometria creada correctamente."
}
```

---

### ✅ Caso 2: Acceso Exitoso con Embedding Correcto

**Endpoint:** `POST /acceso/camara`

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/acceso/camara?dispositivo_id=torniquete1&vector=ALY8P4vIUj8HuTQ/z2ORPRlw2T64Jy49alKlPtqFWz9FFiY+nh1dP9kwSz9w/Ig9o9e5PtRzGj+rA5A+aMnfPuxvCj+Hi4Q+8Mm/PoJGqz16qmQ/MkJzPwLifj+unWw/tMIEP+aMZj/AGr8++d4aP4ZgJD9PWPA+ilodPyJdET5S/II+3A7PPjnFqz65Ivs+lWWuPluVBz+oFyM8CertPquJpz5ysV8/DxN5P/RmHD/dUbA+DE6jPuYpCj5z6zM/fxEjPoitIz/foWI/H/ZsP3RnDz+/WYA+db58Pp3xKz8651A/FjFIP+2kDD7wwIM+jY5zP3FGZj9PI2s/d6p4P3bpaD9NmdU7TIUSP7lR2D4E3jQ/Mzl+P8uhST+WjYo+EOiGPaMUVT8HcG8/eUgXPhAcUT8JY8w+PgIZPzRsyz5YGcg+pL+nPZjqMT8q4m8/raYZP/HFoj0duJQ+85AMPkZBQD1qFOo9fHlIP0G3ED7trWQ/sUBPPyk/gD44iwk/VxRbPu97Rj/u0io/H75OP8WShjz5E3Y/MHZZPyPIMD9ZqDo/ZGssP8Ucbj+U4T0/z+8qP5gsKT7i2AY+q3cKPxTkQT70f409IqpQOrKnfj9P5mI/yeBBPydwAT8u9cw97LkXP2NTWj/PIT4/xGkmP/4d2jy4MGU/oUwjPwkOVD8=&fecha=2025-10-20T20:01:00' \
  -H 'accept: application/json' \
  -d ''
```

**Respuesta Esperada:**
```json
{
  "status": true,
  "medio": "camara",
  "usuario_id": 999,
  "mensaje": "Acceso concedido"
}
```

---

### ❌ Caso 3: Acceso Denegado con Embedding Incorrecto

**Endpoint:** `POST /acceso/camara`

**Request (con embedding diferente):**
```bash
curl -X 'POST' \
  'http://localhost:8000/acceso/camara?dispositivo_id=torniquete1&vector=DIFERENTES_BYTES_BASE64_AQUI&fecha=2025-10-20T20:01:00' \
  -H 'accept: application/json' \
  -d ''
```

**Respuesta Esperada:**
```json
{
  "status": false,
  "medio": "camara",
  "usuario_id": null,
  "mensaje": "Acceso denegado"
}
```

---

### ❌ Caso 4: Vector Malformado

**Endpoint:** `POST /acceso/camara`

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/acceso/camara?dispositivo_id=torniquete1&vector=string_invalido&fecha=2025-10-20T20:00:00' \
  -H 'accept: application/json' \
  -d ''
```

**Respuesta Esperada:**
```json
{
  "status": false,
  "medio": "camara",
  "usuario_id": null,
  "mensaje": "Acceso denegado"
}
```

---

### ⚠️ Caso 5: Sin Vector (Error de Validación)

**Endpoint:** `POST /acceso/camara`

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/acceso/camara?dispositivo_id=torniquete1&fecha=2025-10-20T20:00:00' \
  -H 'accept: application/json' \
  -d ''
```

**Respuesta Esperada (HTTP 422):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "vector"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

## 📊 Resumen de Resultados de Tests

Todos los tests automáticos pasaron exitosamente:

```
✅ test_crear_usuario_y_acceso_facial - PASSED
✅ test_acceso_denegado_embedding_incorrecto - PASSED
✅ test_acceso_vector_malformado - PASSED
✅ test_acceso_sin_vector - PASSED

4 passed in 1.18s
```

---

## 🔧 Generador de Embeddings de Prueba

Para generar embeddings de prueba, usa este script Python:

```python
import numpy as np
import base64

# Generar embedding aleatorio de 128 floats
embedding = np.random.rand(128).astype(np.float32)

# Convertir a Base64
embedding_b64 = base64.b64encode(embedding.tobytes()).decode()

print("Embedding Base64:")
print(embedding_b64)

print("\nPrimeros 10 valores:")
print(list(embedding[:10]))
```

---

## 📚 Documentación Adicional

- **[ESP32_INTEGRATION.md](./ESP32_INTEGRATION.md)** - Integración con ESP32
- **[RECONOCIMIENTO_FACIAL_COMPLETO.md](./RECONOCIMIENTO_FACIAL_COMPLETO.md)** - Detalles técnicos del reconocimiento facial
- **[README.md](./README.md)** - Instrucciones generales del proyecto

---

## 🎯 Notas Importantes

1. **Formato del Vector**: El embedding facial debe ser:
   - Base64 de un array numpy de 128 float32, **o**
   - String JSON con 128 números decimales: `"[0.123, 0.456, ...]"`

2. **Umbral de Similitud**: El sistema usa un umbral de 0.70 (configurable) para aceptar coincidencias faciales.

3. **Hash-Indexing**: El sistema usa hash parcial (SHA256[:8]) para optimizar la búsqueda de candidatos antes de comparar embeddings completos.

4. **Padding Base64**: El sistema corrige automáticamente el padding Base64 incorrecto (`=` al final).
