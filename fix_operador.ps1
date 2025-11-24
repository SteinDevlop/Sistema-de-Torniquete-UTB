# Script para arreglar operador.js automáticamente
# Ejecuta este script en PowerShell

$archivo = "src/frontend/assets/operador.js"

Write-Host "🔧 Arreglando operador.js..." -ForegroundColor Cyan

# 1. Backup
Copy-Item $archivo "$archivo.backup" -Force
Write-Host "✅ Backup creado: operador.js.backup" -ForegroundColor Green

# 2. Leer contenido
$contenido = Get-Content $archivo -Raw

# 3. Arreglar import -> const
$contenido = $contenido -replace 'import API_URL from ''\.\/api_root\.js'';', 'const API_URL = "http://localhost:8000";'

# 4. Agregar función ShowTab después de hideLoading
$showTabFunction = @'

        // Función para cambiar tabs
        function ShowTab(tabName) {
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            const tabButtons = document.querySelectorAll('.tab-button');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            const selectedTab = document.getElementById(tabName);
            if (selectedTab) selectedTab.classList.add('active');
            const selectedButton = document.querySelector(`[onclick="ShowTab('${tabName}')"]`);
            if (selectedButton) selectedButton.classList.add('active');
        }
'@

$contenido = $contenido -replace '(function hideLoading\(\) \{ document\.getElementById\("loadingOverlay"\)\.classList\.remove\("show"\); \})', "`$1$showTabFunction"

# 5. Guardar cambios
$contenido | Set-Content $archivo -NoNewline

Write-Host "✅ Archivo arreglado!" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora ejecuta: Ctrl + Shift + R en el navegador" -ForegroundColor Yellow
