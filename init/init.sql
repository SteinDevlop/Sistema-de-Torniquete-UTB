CREATE TABLE Usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    cargo TEXT,
    estado BOOLEAN DEFAULT 1,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
)

CREATE TABLE Biometria (
    id_biometria INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    vector_facial TEXT,
    facial_hash TEXT,
    huella_hash TEXT,
    template_huella TEXT,
    rfid_tag TEXT,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
)

CREATE TABLE Operarios (
    id_operario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_operario TEXT NOT NULL,
    usuario_sistema TEXT UNIQUE NOT NULL,
    contraseña_hash TEXT NOT NULL,
    activo BOOLEAN DEFAULT 1
)

CREATE TABLE Torniquetes (
    id_torniquete INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    ubicacion TEXT,
    estado BOOLEAN DEFAULT 1
)

CREATE TABLE Registros (
    id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_torniquete INTEGER NOT NULL,
    id_operario INTEGER,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_acceso TEXT,
    imagen_capturada TEXT,
    resultado BOOLEAN,
    observaciones TEXT,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_torniquete) REFERENCES Torniquetes(id_torniquete) ON DELETE CASCADE,
    FOREIGN KEY (id_operario) REFERENCES Operarios(id_operario) ON DELETE SET NULL
)


CREATE TABLE RegistrosInvalidos (
    id_invalido INTEGER PRIMARY KEY AUTOINCREMENT,
    id_registro INTEGER NOT NULL,
    motivo TEXT,
    fecha_invalido DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_registro) REFERENCES Registros(id_registro) ON DELETE CASCADE
)

CREATE TABLE HistorialEstadoUsuario (
    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    estado_anterior BOOLEAN,
    estado_nuevo BOOLEAN,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
)