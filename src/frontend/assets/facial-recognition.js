import API_URL from './api_root.js';
    const API_ROOT = API_URL;
    let stream = null;
    let streamVerify = null;
    let capturedImageData = null;
    let capturedImageDataVerify = null;

    // Cambio de modo de verificación
    document.getElementById('modeCamera').addEventListener('change', () => {
      document.getElementById('cameraVerifyPanel').style.display = 'block';
      document.getElementById('fileVerifyPanel').style.display = 'none';
      document.getElementById('uploadedImageVerify').style.display = 'none';
      document.getElementById('videoVerify').style.display = 'block';
      document.getElementById('capturedImageVerify').style.display = 'none';
      document.getElementById('verifyResult').innerHTML = '';
    });

    document.getElementById('modeFile').addEventListener('change', () => {
      document.getElementById('cameraVerifyPanel').style.display = 'none';
      document.getElementById('fileVerifyPanel').style.display = 'block';
      document.getElementById('videoVerify').style.display = 'none';
      document.getElementById('capturedImageVerify').style.display = 'none';
      document.getElementById('uploadedImageVerify').style.display = 'none';
      document.getElementById('verifyResult').innerHTML = '';
      
      // Detener cámara si está activa
      if (streamVerify) {
        streamVerify.getTracks().forEach(track => track.stop());
        streamVerify = null;
      }
    });

    // Previsualizar imagen subida
    document.getElementById('fileInput').addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const img = document.getElementById('uploadedImageVerify');
          img.src = event.target.result;
          img.style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    });

    // REGISTRO - Abrir cámara
    document.getElementById('btnStartCamera').addEventListener('click', async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        document.getElementById('video').srcObject = stream;
        document.getElementById('btnStartCamera').style.display = 'none';
        document.getElementById('btnCapture').style.display = 'block';
        document.getElementById('capturedImage').style.display = 'none';
      } catch (e) {
        alert('Error al acceder a la cámara: ' + e.message);
      }
    });

    // REGISTRO - Capturar foto
    document.getElementById('btnCapture').addEventListener('click', () => {
      const video = document.getElementById('video');
      const canvas = document.getElementById('canvas');
      const img = document.getElementById('capturedImage');
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      capturedImageData = canvas.toDataURL('image/jpeg', 0.9);
      img.src = capturedImageData;
      img.style.display = 'block';
      video.style.display = 'none';
      
      // Detener cámara
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
      }
      
      document.getElementById('btnCapture').style.display = 'none';
      document.getElementById('btnRegister').style.display = 'block';
      document.getElementById('btnStartCamera').style.display = 'block';
      document.getElementById('btnStartCamera').textContent = '🔄 Tomar otra foto';
    });

    // REGISTRO - Registrar usuario
    document.getElementById('btnRegister').addEventListener('click', async () => {
      const userId = document.getElementById('regUserId').value;
      
      if (!userId) {
        document.getElementById('regResult').innerHTML = '<div class="result-error">⚠️ Ingresa un ID</div>';
        return;
      }
      if (!capturedImageData) {
        document.getElementById('regResult').innerHTML = '<div class="result-error">⚠️ Captura una foto primero</div>';
        return;
      }

      document.getElementById('regResult').innerHTML = '<div class="result-info">⏳ Procesando...</div>';

      try {
        const base64Clean = capturedImageData.split(',')[1];
        const form = new FormData();
        form.append('id_usuario', userId);
        form.append('imagen_facial', base64Clean);

        const res = await fetch(`${API_ROOT}/biometria/create`, {
          method: 'POST',
          body: form
        });

        const data = await res.json();
        
        if (res.ok && data.success) {
          document.getElementById('regResult').innerHTML = `
            <div class="result-success">
              <strong>✅ Usuario registrado</strong>
              <p class="mb-0">ID: ${userId}</p>
            </div>
          `;
          await refreshUsers();
        } else {
          document.getElementById('regResult').innerHTML = `
            <div class="result-error">
              <strong>❌ Error</strong>
              <p class="mb-0">${data.detail || data.message || 'Error'}</p>
            </div>
          `;
        }
      } catch (e) {
        document.getElementById('regResult').innerHTML = `<div class="result-error">❌ ${e.message}</div>`;
      }
    });

    // VERIFICACIÓN - Abrir cámara
    document.getElementById('btnStartCameraVerify').addEventListener('click', async () => {
      try {
        streamVerify = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        document.getElementById('videoVerify').srcObject = streamVerify;
        document.getElementById('btnStartCameraVerify').style.display = 'none';
        document.getElementById('btnCaptureVerify').style.display = 'block';
        document.getElementById('capturedImageVerify').style.display = 'none';
        document.getElementById('videoVerify').style.display = 'block';
      } catch (e) {
        alert('Error al acceder a la cámara: ' + e.message);
      }
    });

    // VERIFICACIÓN - Capturar foto
    document.getElementById('btnCaptureVerify').addEventListener('click', () => {
      const video = document.getElementById('videoVerify');
      const canvas = document.getElementById('canvasVerify');
      const img = document.getElementById('capturedImageVerify');
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      capturedImageDataVerify = canvas.toDataURL('image/jpeg', 0.9);
      img.src = capturedImageDataVerify;
      img.style.display = 'block';
      video.style.display = 'none';
      
      if (streamVerify) {
        streamVerify.getTracks().forEach(track => track.stop());
        streamVerify = null;
      }
      
      document.getElementById('btnCaptureVerify').style.display = 'none';
      document.getElementById('btnVerify').style.display = 'block';
      document.getElementById('btnStartCameraVerify').style.display = 'block';
      document.getElementById('btnStartCameraVerify').textContent = '🔄 Tomar otra foto';
    });

    // VERIFICACIÓN - Verificar acceso con cámara
    document.getElementById('btnVerify').addEventListener('click', async () => {
      if (!capturedImageDataVerify) {
        document.getElementById('verifyResult').innerHTML = '<div class="result-error">⚠️ Captura una foto</div>';
        return;
      }

      document.getElementById('verifyResult').innerHTML = '<div class="result-info">⏳ Verificando...</div>';

      try {
        const base64Clean = capturedImageDataVerify.split(',')[1];
        const form = new FormData();
        form.append('dispositivo_id', 'web_test');
        form.append('imagen_facial', base64Clean);

        const res = await fetch(`${API_ROOT}/acceso/camara`, {
          method: 'POST',
          body: form
        });

        const data = await res.json();
        
        if (data.status === true) {
          let detallesHtml = '';
          if (data.detalles_verificacion) {
            const d = data.detalles_verificacion;
            detallesHtml = `
              <hr>
              <small>
                <strong>📊 Detalles de Verificación:</strong><br>
                • Candidatos evaluados: ${d.candidatos_evaluados || 0}<br>
                • Score obtenido: ${d.mejor_score ? (d.mejor_score * 100).toFixed(2) : '0.00'}%<br>
                • Umbral requerido: ${d.umbral_score ? (d.umbral_score * 100).toFixed(0) : '70'}%<br>
                • Distancia: ${d.mejor_distancia ? d.mejor_distancia.toFixed(4) : 'N/A'}
              </small>
            `;
            
            if (d.todos_scores && d.todos_scores.length > 0) {
              detallesHtml += '<br><br><strong>🏆 Top 5 Coincidencias:</strong><ul class="small mb-0">';
              d.todos_scores.slice(0, 5).forEach((s, i) => {
                detallesHtml += `<li>Usuario ${s.usuario_id}: ${s.porcentaje_similitud}% (${s.score.toFixed(4)})</li>`;
              });
              detallesHtml += '</ul>';
            }
          }
          
          document.getElementById('verifyResult').innerHTML = `
            <div class="result-success">
              <strong>✅ ACCESO CONCEDIDO</strong>
              <p class="mb-0">${data.mensaje}</p>
              <p class="mb-0">Usuario: <strong>${data.usuario_id}</strong></p>
              ${data.score ? `<p class="mb-0">Similitud: ${(data.score * 100).toFixed(1)}%</p>` : ''}
              ${detallesHtml}
            </div>
          `;
        } else {
          let detallesHtml = '';
          if (data.detalles_verificacion) {
            const d = data.detalles_verificacion;
            detallesHtml = `
              <hr>
              <small>
                <strong>📊 Detalles de Verificación:</strong><br>
                • Candidatos evaluados: ${d.candidatos_evaluados || 0}<br>
                • Mejor score: ${d.mejor_score ? (d.mejor_score * 100).toFixed(2) : '0.00'}%<br>
                • Umbral requerido: ${d.umbral_score ? (d.umbral_score * 100).toFixed(0) : '70'}%<br>
                • Distancia: ${d.mejor_distancia ? d.mejor_distancia.toFixed(4) : 'N/A'}<br>
                <span class="text-danger">⚠️ Score insuficiente para conceder acceso</span>
              </small>
            `;
            
            if (d.todos_scores && d.todos_scores.length > 0) {
              detallesHtml += '<br><br><strong>🏆 Top 5 Coincidencias:</strong><ul class="small mb-0">';
              d.todos_scores.slice(0, 5).forEach((s, i) => {
                detallesHtml += `<li>Usuario ${s.usuario_id}: ${s.porcentaje_similitud}% (${s.score.toFixed(4)})</li>`;
              });
              detallesHtml += '</ul>';
            }
          }
          
          document.getElementById('verifyResult').innerHTML = `
            <div class="result-error">
              <strong>❌ ACCESO DENEGADO</strong>
              <p class="mb-0">${data.mensaje}</p>
              ${detallesHtml}
            </div>
          `;
        }
      } catch (e) {
        document.getElementById('verifyResult').innerHTML = `<div class="result-error">❌ ${e.message}</div>`;
      }
    });

    // VERIFICACIÓN - Verificar acceso con archivo
    document.getElementById('btnVerifyFile').addEventListener('click', async () => {
      const fileInput = document.getElementById('fileInput');
      
      if (!fileInput.files || fileInput.files.length === 0) {
        document.getElementById('verifyResult').innerHTML = '<div class="result-error">⚠️ Selecciona una imagen primero</div>';
        return;
      }

      document.getElementById('verifyResult').innerHTML = '<div class="result-info">⏳ Verificando...</div>';

      try {
        const file = fileInput.files[0];
        const reader = new FileReader();
        
        reader.onload = async (e) => {
          const base64Data = e.target.result;
          const base64Clean = base64Data.split(',')[1];
          
          const form = new FormData();
          form.append('dispositivo_id', 'web_test');
          form.append('imagen_facial', base64Clean);

          const res = await fetch(`${API_ROOT}/acceso/camara`, {
            method: 'POST',
            body: form
          });

          const data = await res.json();
          
          if (data.status === true) {
            let detallesHtml = '';
            if (data.detalles_verificacion) {
              const d = data.detalles_verificacion;
              detallesHtml = `
                <hr>
                <small>
                  <strong>📊 Detalles de Verificación:</strong><br>
                  • Candidatos evaluados: ${d.candidatos_evaluados || 0}<br>
                  • Score obtenido: ${d.mejor_score ? (d.mejor_score * 100).toFixed(2) : '0.00'}%<br>
                  • Umbral requerido: ${d.umbral_score ? (d.umbral_score * 100).toFixed(0) : '70'}%<br>
                  • Distancia: ${d.mejor_distancia ? d.mejor_distancia.toFixed(4) : 'N/A'}
                </small>
              `;
              
              if (d.todos_scores && d.todos_scores.length > 0) {
                detallesHtml += '<br><br><strong>🏆 Top 5 Coincidencias:</strong><ul class="small mb-0">';
                d.todos_scores.slice(0, 5).forEach((s, i) => {
                  detallesHtml += `<li>Usuario ${s.usuario_id}: ${s.porcentaje_similitud}% (${s.score.toFixed(4)})</li>`;
                });
                detallesHtml += '</ul>';
              }
            }
            
            document.getElementById('verifyResult').innerHTML = `
              <div class="result-success">
                <strong>✅ ACCESO CONCEDIDO</strong>
                <p class="mb-0">${data.mensaje}</p>
                <p class="mb-0">Usuario: <strong>${data.usuario_id}</strong></p>
                ${data.score ? `<p class="mb-0">Similitud: ${(data.score * 100).toFixed(1)}%</p>` : ''}
                ${detallesHtml}
              </div>
            `;
          } else {
            let detallesHtml = '';
            if (data.detalles_verificacion) {
              const d = data.detalles_verificacion;
              detallesHtml = `
                <hr>
                <small>
                  <strong>📊 Detalles de Verificación:</strong><br>
                  • Candidatos evaluados: ${d.candidatos_evaluados || 0}<br>
                  • Mejor score: ${d.mejor_score ? (d.mejor_score * 100).toFixed(2) : '0.00'}%<br>
                  • Umbral requerido: ${d.umbral_score ? (d.umbral_score * 100).toFixed(0) : '70'}%<br>
                  • Distancia: ${d.mejor_distancia ? d.mejor_distancia.toFixed(4) : 'N/A'}<br>
                  <span class="text-danger">⚠️ Score insuficiente para conceder acceso</span>
                </small>
              `;
              
              if (d.todos_scores && d.todos_scores.length > 0) {
                detallesHtml += '<br><br><strong>🏆 Top 5 Coincidencias:</strong><ul class="small mb-0">';
                d.todos_scores.slice(0, 5).forEach((s, i) => {
                  detallesHtml += `<li>Usuario ${s.usuario_id}: ${s.porcentaje_similitud}% (${s.score.toFixed(4)})</li>`;
                });
                detallesHtml += '</ul>';
              }
            }
            
            document.getElementById('verifyResult').innerHTML = `
              <div class="result-error">
                <strong>❌ ACCESO DENEGADO</strong>
                <p class="mb-0">${data.mensaje}</p>
                ${detallesHtml}
              </div>
            `;
          }
        };
        
        reader.readAsDataURL(file);
      } catch (e) {
        document.getElementById('verifyResult').innerHTML = `<div class="result-error">❌ ${e.message}</div>`;
      }
    });

    // Lista de usuarios
    document.getElementById('btnRefresh').addEventListener('click', refreshUsers);

    async function refreshUsers() {
      const list = document.getElementById('usersList');
      list.innerHTML = '<p class="text-muted">Cargando...</p>';
      
      try {
        const res = await fetch(`${API_ROOT}/biometria/all`);
        const items = await res.json();
        
        if (!items || items.length === 0) {
          list.innerHTML = '<p class="text-muted">No hay usuarios</p>';
          return;
        }

        let html = '<div class="list-group">';
        items.forEach(it => {
          html += `
            <div class="list-group-item">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-1">Usuario ${it.id_usuario}</h6>
                  <small class="text-muted">ID: ${it.id_biometria} | Hash: ${it.facial_hash || 'N/A'}</small>
                </div>
                <button class="btn btn-danger btn-sm" onclick="deleteUser(${it.id_biometria})">🗑️</button>
              </div>
            </div>
          `;
        });
        html += '</div>';
        list.innerHTML = html;
      } catch (e) {
        list.innerHTML = `<p class="text-danger">Error: ${e.message}</p>`;
      }
    }

    async function deleteUser(bioId) {
      if (!confirm('¿Eliminar?')) return;
      
      try {
        const form = new FormData();
        form.append('id_biometria', bioId);
        
        const res = await fetch(`${API_ROOT}/biometria/delete`, {
          method: 'POST',
          body: form
        });
        
        const data = await res.json();
        if (data.success) {
          await refreshUsers();
        }
      } catch (e) {
        alert('Error: ' + e.message);
      }
    }

    refreshUsers();