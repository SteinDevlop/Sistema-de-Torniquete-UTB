# 📡 Guía de Integración ESP32 - Reconocimiento Facial

## 🎯 Resumen
Esta guía explica cómo enviar embeddings faciales (vectores de 128 dimensiones) desde un ESP32 al backend del Sistema de Torniquete UTB para verificación de acceso.

---

## 🔄 Flujo de Trabajo

```
ESP32 → Captura Imagen → Extrae Embedding (128 valores) → HTTP POST → Backend → Respuesta
```

---

## 📤 Formato del Endpoint

### **POST** `/acceso/camara`

**URL Completa:** `http://<IP_SERVIDOR>:8000/acceso/camara`

**Content-Type:** `application/x-www-form-urlencoded` o `application/json`

### Parámetros:

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `dispositivo_id` | string | ✅ Sí | ID único del ESP32 (ej: "ESP32_001") |
| `vector` | string | ✅ Sí | Embedding facial de 128 decimales |
| `fecha` | string | ⚪ No | Timestamp de captura (ISO 8601) |

---

## 📊 Formato del Vector Facial

El embedding debe ser un **string JSON** con 128 valores decimales (float):

### Ejemplo:
```json
"[0.123, -0.456, 0.789, 0.234, -0.567, ..., 0.891]"
```

### Características:
- **Longitud:** Exactamente 128 valores
- **Tipo:** Números decimales (float32)
- **Formato:** Array JSON como string
- **Normalización:** Preferiblemente normalizado (norma L2 = 1)

---

## 🔌 Ejemplo de Petición HTTP

### **Opción 1: Form Data (Recomendado para ESP32)**

```http
POST /acceso/camara HTTP/1.1
Host: 192.168.1.100:8000
Content-Type: application/x-www-form-urlencoded

dispositivo_id=ESP32_001&vector=[0.123,-0.456,0.789,...]&fecha=2025-10-19T10:30:00
```

### **Opción 2: JSON**

```http
POST /acceso/camara HTTP/1.1
Host: 192.168.1.100:8000
Content-Type: application/json

{
    "dispositivo_id": "ESP32_001",
    "vector": "[0.123, -0.456, 0.789, 0.234, -0.567, ...]",
    "fecha": "2025-10-19T10:30:00"
}
```

---

## 📥 Respuesta del Servidor

### **Acceso Concedido** (200 OK):
```json
{
    "status": true,
    "medio": "camara",
    "usuario_id": 42,
    "mensaje": "Acceso concedido"
}
```

### **Acceso Denegado** (200 OK):
```json
{
    "status": false,
    "medio": "camara",
    "usuario_id": null,
    "mensaje": "Acceso denegado"
}
```

### **Error de Validación** (422 Unprocessable Entity):
```json
{
    "detail": "El embedding facial debe tener 128 dimensiones, recibido: 64"
}
```

---

## 💻 Código Ejemplo para ESP32 (Arduino/C++)

### **Usando HTTPClient (WiFi)**

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "TU_WIFI";
const char* password = "TU_PASSWORD";
const char* serverUrl = "http://192.168.1.100:8000/acceso/camara";

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi conectado");
}

bool verificarAcceso(float* embedding, int size) {
    if (size != 128) {
        Serial.println("Error: El embedding debe tener 128 valores");
        return false;
    }
    
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    // Construir el vector como string JSON
    String vectorStr = "[";
    for (int i = 0; i < size; i++) {
        vectorStr += String(embedding[i], 6); // 6 decimales de precisión
        if (i < size - 1) vectorStr += ",";
    }
    vectorStr += "]";
    
    // Construir el payload
    String payload = "dispositivo_id=ESP32_001&vector=" + vectorStr;
    
    // Enviar petición
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode == 200) {
        String response = http.getString();
        
        // Parsear JSON
        DynamicJsonDocument doc(512);
        deserializeJson(doc, response);
        
        bool status = doc["status"];
        int userId = doc["usuario_id"];
        String mensaje = doc["mensaje"];
        
        Serial.println("Respuesta: " + mensaje);
        Serial.println("Usuario ID: " + String(userId));
        
        http.end();
        return status;
    } else {
        Serial.println("Error HTTP: " + String(httpResponseCode));
        http.end();
        return false;
    }
}

void loop() {
    // Ejemplo: embedding de prueba (128 valores)
    float embedding[128];
    for (int i = 0; i < 128; i++) {
        embedding[i] = random(-1000, 1000) / 1000.0; // Valores entre -1 y 1
    }
    
    bool accesoConcedido = verificarAcceso(embedding, 128);
    
    if (accesoConcedido) {
        Serial.println("✅ ACCESO CONCEDIDO - Abrir torniquete");
        // Activar relé, servo, etc.
    } else {
        Serial.println("❌ ACCESO DENEGADO");
    }
    
    delay(5000); // Esperar 5 segundos
}
```

---

## 🧠 Generación del Embedding en ESP32

### **Opción 1: Modelo TensorFlow Lite Micro**
```cpp
#include <TensorFlowLite_ESP32.h>
#include "esp32-camera.h"

// Cargar modelo FaceNet cuantizado
const unsigned char model_tflite[] = {...};

float* extraerEmbedding(camera_fb_t* fb) {
    // 1. Preprocesar imagen (resize, normalizar)
    // 2. Ejecutar inferencia con modelo TFLite
    // 3. Retornar vector de 128 floats
    static float embedding[128];
    // ... lógica de inferencia ...
    return embedding;
}
```

### **Opción 2: Procesamiento Externo (Raspberry Pi/PC)**
- ESP32 captura imagen y la envía a un procesador más potente
- El procesador extrae el embedding y lo devuelve al ESP32
- ESP32 envía el embedding al backend

---

## 🔐 Registrar Nuevos Usuarios

### Endpoint: `POST /biometria/create`

```http
POST /biometria/create HTTP/1.1
Host: 192.168.1.100:8000
Content-Type: application/x-www-form-urlencoded

id_usuario=42&vector_facial=[0.123,-0.456,...]
```

El backend automáticamente:
1. Calcula el `facial_hash` (SHA256 de los primeros 8 caracteres)
2. Almacena el embedding en la BD
3. Lo indexa para búsquedas rápidas

---

## ⚙️ Configuración del Umbral

El umbral de similitud se configura en:
```python
# backend/app/logic/verification.py
# Línea ~277
UMBRAL = 0.70  # Valor entre 0 y 1
```

### Recomendaciones:
- **0.60-0.65:** Más permisivo (puede tener falsos positivos)
- **0.70-0.75:** **Balanceado** ⭐ (recomendado)
- **0.80-0.85:** Muy estricto (puede rechazar usuarios válidos)

---

## 🧪 Pruebas con cURL

### Crear usuario de prueba:
```bash
curl -X POST "http://localhost:8000/biometria/create" \
  -F "id_usuario=1" \
  -F "vector_facial=[0.1,0.2,0.3,...,0.128]"
```

### Verificar acceso:
```bash
curl -X POST "http://localhost:8000/acceso/camara" \
  -F "dispositivo_id=TEST_001" \
  -F "vector=[0.1,0.2,0.3,...,0.128]"
```

---

## 📊 Diagrama de Comparación

```
Embedding Capturado (ESP32)          Embeddings Almacenados (BD)
         ↓                                      ↓
   [128 valores]                          [Usuario 1: 128 valores]
         ↓                                 [Usuario 2: 128 valores]
   Normalizar L2                          [Usuario N: 128 valores]
         ↓                                      ↓
   Calcular Hash                          Filtrar por facial_hash
    (SHA256[:8])                               similar
         ↓                                      ↓
   "a3f7b2e1"  ────────────────────→  Candidatos: [Usuario 1, 42]
                                                   ↓
                                          Comparar Similitud Coseno
                                                   ↓
                                          Score > 0.70 → ACCESO ✅
                                          Score < 0.70 → DENEGADO ❌
```

---

## 🐛 Troubleshooting

### Error: "El embedding debe tener 128 dimensiones"
- Verificar que el vector tenga exactamente 128 valores
- Revisar la serialización JSON

### Error: "No se encontraron candidatos"
- No hay usuarios registrados con vector_facial en la BD
- Registrar usuarios con `/biometria/create`

### Siempre devuelve "Acceso denegado"
- Verificar umbral de similitud (podría ser muy alto)
- Confirmar que el embedding es del mismo modelo
- Revisar normalización del vector

### Timeout de conexión
- Verificar que el servidor esté corriendo en `0.0.0.0:8000`
- Comprobar firewall/red local

---

## 📚 Referencias

- **Modelo recomendado:** FaceNet (128-d embeddings)
- **Librería Python:** `facenet-pytorch`, `deepface`
- **ESP32 TFLite:** https://github.com/espressif/tflite-micro-esp-examples

---

## ✅ Checklist de Implementación

- [ ] ESP32 conectado a WiFi
- [ ] Modelo de reconocimiento facial cargado
- [ ] Endpoint `/acceso/camara` probado con cURL
- [ ] Usuarios registrados en BD con `vector_facial`
- [ ] Umbral ajustado según precisión deseada
- [ ] Logs del backend monitoreados
- [ ] Integración con actuador del torniquete

---

**¡Listo!** 🎉 El sistema de reconocimiento facial está completamente operativo.
