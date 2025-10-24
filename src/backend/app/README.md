```markdown
# Sistema de Torniquete UTB - Demo (React + TailwindCSS)

Descripción:
Esta aplicación es una implementación de demostración (sin backend) que replica los mockups del "Sistema de Torniquete UTB" solicitados. Incluye:

- Módulo Operador (verificación de accesos simulada)
- Módulo Administrador (gestión de usuarios, registros, reportes y configuraciones)
- Diseño con React (Vite) + TailwindCSS
- Estado y datos simulados mediante JSON local y localStorage
- Responsive básico: sidebar que se oculta en pantallas pequeñas

Estructura principal:
src/
 ┣ components/ (Header, Sidebar, UserCard, AccessTable)
 ┣ pages/ (Login, OperatorView, AdminDashboard, UsersPage, AccessPage, ReportsPage, SettingsPage)
 ┣ data/ (users.json, accesses.json)
 ┣ assets/ (logoutb.png placeholder)
 ┗ index.css, main.jsx, App.jsx

Cómo ejecutar:
1. Instalar dependencias:
   npm install

2. Ejecutar en modo desarrollo:
   npm run dev

3. Abrir en el navegador:
   http://localhost:5173

Notas:
- Todos los datos son de ejemplo y se guardan en localStorage para persistencia entre recargas.
- El logo proporcionado es un placeholder SVG (archivo llamado logoutb.png) para la demo.
- Para integrar con la API real del repositorio Steindevlop reemplazar las llamadas/lectura de los archivos JSON por llamadas fetch/axios a esa API.
```