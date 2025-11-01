-- ============================================
-- Script para verificar datos en todas las tablas
-- Sistema de Torniquete UTB
-- ============================================

-- Tabla: Usuarios
SELECT 'USUARIOS' as Tabla, COUNT(*) as Total FROM Usuarios;
SELECT * FROM Usuarios ORDER BY id_usuario DESC;

-- Tabla: Biometria
SELECT 'BIOMETRIA' as Tabla, COUNT(*) as Total FROM Biometria;
SELECT 
    id_biometria,
    id_usuario,
    CASE WHEN vector_facial IS NOT NULL THEN 'SÍ' ELSE 'NO' END as Tiene_Facial,
    CASE WHEN huella_hash IS NOT NULL THEN 'SÍ' ELSE 'NO' END as Tiene_Huella,
    rfid_tag,
    fecha_actualizacion
FROM Biometria 
ORDER BY id_biometria DESC;

-- Tabla: Torniquetes
SELECT 'TORNIQUETES' as Tabla, COUNT(*) as Total FROM Torniquetes;
SELECT * FROM Torniquetes ORDER BY id_torniquete DESC;

-- Tabla: Registros
SELECT 'REGISTROS' as Tabla, COUNT(*) as Total FROM Registros;
SELECT 
    id_registro,
    id_usuario,
    id_torniquete,
    tipo_acceso,
    fecha_hora,
    id_operario
FROM Registros 
ORDER BY fecha_hora DESC 
LIMIT 50;

-- Tabla: Registros Inválidos
SELECT 'REGISTROS_INVALIDOS' as Tabla, COUNT(*) as Total FROM Registros_Invalidos;
SELECT * FROM Registros_Invalidos ORDER BY fecha_hora DESC LIMIT 20;

-- Tabla: Operarios
SELECT 'OPERARIOS' as Tabla, COUNT(*) as Total FROM Operarios;
SELECT * FROM Operarios ORDER BY id_operario DESC;

-- Tabla: Historial Estado Usuario
SELECT 'HISTORIAL_ESTADO' as Tabla, COUNT(*) as Total FROM Historial_Estado_Usuario;
SELECT * FROM Historial_Estado_Usuario ORDER BY fecha_cambio DESC LIMIT 20;

-- ============================================
-- Resumen consolidado
-- ============================================
SELECT 
    'Usuarios' as Tabla, COUNT(*) as Total FROM Usuarios
UNION ALL
SELECT 'Biometria', COUNT(*) FROM Biometria
UNION ALL
SELECT 'Torniquetes', COUNT(*) FROM Torniquetes
UNION ALL
SELECT 'Registros', COUNT(*) FROM Registros
UNION ALL
SELECT 'Registros_Invalidos', COUNT(*) FROM Registros_Invalidos
UNION ALL
SELECT 'Operarios', COUNT(*) FROM Operarios
UNION ALL
SELECT 'Historial_Estado', COUNT(*) FROM Historial_Estado_Usuario;

-- ============================================
-- Verificar relaciones (usuarios con biometría)
-- ============================================
SELECT 
    u.id_usuario,
    u.nombre_completo,
    u.cargo,
    u.estado,
    CASE WHEN b.vector_facial IS NOT NULL THEN '✓' ELSE '✗' END as Facial,
    CASE WHEN b.huella_hash IS NOT NULL THEN '✓' ELSE '✗' END as Huella,
    b.rfid_tag,
    (SELECT COUNT(*) FROM Registros r WHERE r.id_usuario = u.id_usuario) as Total_Accesos
FROM Usuarios u
LEFT JOIN Biometria b ON u.id_usuario = b.id_usuario
ORDER BY u.id_usuario DESC;
