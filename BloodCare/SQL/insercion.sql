
INSERT INTO rol (nombre_rol, descripcion) VALUES ('Administrador', 'Acceso completo al sistema');
INSERT INTO rol (nombre_rol, descripcion) VALUES ('Diplomado', 'Gestiona donantes, registros de donaciones y visualiza inventario');
INSERT INTO rol (nombre_rol, descripcion) VALUES ('Técnico', 'Control del inventario y rechazo de donaciones');
INSERT INTO rol (nombre_rol, descripcion) VALUES ('Microbiologo', 'Acceso a registros, inventarios y causas de rechazo');
INSERT INTO rol (nombre_rol, descripcion) VALUES ('Jefatura', 'Acceso al sistema, pero no puede crear usuarios');

--Usuarios--
-- Usuario Administrador
INSERT INTO usuario (id_usuario, nombre_usuario, correo, contrasena, estado, id_rol)
VALUES ('USR001', 'admin1', 'admin1@bloodcare.com', 'admin123', 'Activo', 1);

-- Usuario Diplomado
INSERT INTO usuario (id_usuario, nombre_usuario, correo, contrasena, estado, id_rol)
VALUES ('USR002', 'diplomado1', 'diplomado1@bloodcare.com', 'diplomado123', 'Activo', 2);

-- Usuario Técnico
INSERT INTO usuario (id_usuario, nombre_usuario, correo, contrasena, estado, id_rol)
VALUES ('USR003', 'tecnico1', 'tecnico1@bloodcare.com', 'tecnico123', 'Activo', 3);

-- Usuario Microbiologo
INSERT INTO usuario (id_usuario, nombre_usuario, correo, contrasena, estado, id_rol)
VALUES ('USR004', 'micro1', 'micro1@bloodcare.com', 'micro123', 'Activo', 4);

-- Usuario Jefatura
INSERT INTO usuario (id_usuario, nombre_usuario, correo, contrasena, estado, id_rol)
VALUES ('USR005', 'jefatura1', 'jefatura1@bloodcare.com', 'jefatura123', 'Activo', 5);

INSERT INTO tipo_sangre (tipo) VALUES ('A+');
INSERT INTO tipo_sangre (tipo) VALUES ('A-');
INSERT INTO tipo_sangre (tipo) VALUES ('B+');
INSERT INTO tipo_sangre (tipo) VALUES ('B-');
INSERT INTO tipo_sangre (tipo) VALUES ('O+');
INSERT INTO tipo_sangre (tipo) VALUES ('O-');
INSERT INTO tipo_sangre (tipo) VALUES ('AB+');
INSERT INTO tipo_sangre (tipo) VALUES ('AB-');

COMMIT;

--insercion de donantes
INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('101010101', 'Andrea', 'Mora Salazar', 'San José, Rohrmoser', TO_DATE('1991-04-15','YYYY-MM-DD'), 'F', '8888-1010', 'andrea.mora@example.com', 1);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('202020202', 'Luis', 'Cordero Jiménez', 'Cartago, El Guarco', TO_DATE('1989-06-22','YYYY-MM-DD'), 'M', '8899-2020', 'luis.cordero@example.com', 2);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('303030303', 'María José', 'Solís Vargas', 'Alajuela, San Rafael', TO_DATE('1993-12-09','YYYY-MM-DD'), 'F', '8700-3030', 'mariaj.solis@example.com', 3);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('404040404', 'Jorge', 'Rodríguez Álvarez', 'Heredia, Barva', TO_DATE('1990-01-30','YYYY-MM-DD'), 'M', '8711-4040', 'jorge.r@example.com', 4);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('505050505', 'Paola', 'Zúñiga Chacón', 'San José, Curridabat', TO_DATE('1987-10-18','YYYY-MM-DD'), 'F', '8722-5050', 'paola.z@example.com', 5);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('606060606', 'Carlos', 'Alpízar Marín', 'Puntarenas, Parrita', TO_DATE('1995-07-11','YYYY-MM-DD'), 'M', '8733-6060', 'carlos.alpizar@example.com', 6);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('707070707', 'Estefany', 'Guzmán Valverde', 'Guanacaste, Santa Cruz', TO_DATE('1992-03-26','YYYY-MM-DD'), 'F', '8744-7070', 'estefany.g@example.com', 7);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('808080808', 'José Miguel', 'Sánchez Rivera', 'Limón, Siquirres', TO_DATE('1988-09-14','YYYY-MM-DD'), 'M', '8755-8080', 'jose.sanchez@example.com', 8);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('909090909', 'Karina', 'Campos Rojas', 'San José, Desamparados', TO_DATE('1994-11-03','YYYY-MM-DD'), 'F', '8766-9090', 'karina.campos@example.com', 2);

INSERT INTO donante (id_donante, nombre, apellido, direccion, fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre)
VALUES ('111111111', 'Ricardo', 'Castillo Fallas', 'Alajuela, Grecia', TO_DATE('1996-05-20','YYYY-MM-DD'), 'M', '8777-1111', 'ricardo.castillo@example.com', 1);

---insercion de centros

-- Insertar centros de donación
INSERT INTO centro_donacion (nombre, ubicacion, tipo)
VALUES ('Hospital San Vicente de Paul', 'Heredia centro', 'Fijo');

INSERT INTO centro_donacion (nombre, ubicacion, tipo)
VALUES ('Empresa Cerveceria de Costa Rica', 'Heredia Centro, Heredia', 'Móvil');

INSERT INTO centro_donacion (nombre, ubicacion, tipo)
VALUES ('Campaña Universitaria', 'UCR Sede Rodrigo Facio', 'Campaña');


-- componente_sanguineo
INSERT INTO componente_sanguineo (nombre, descripcion) 
VALUES ('Glóbulos Rojos', 'Transportan oxígeno desde los pulmones al resto del cuerpo y dióxido de carbono de vuelta a los pulmones.');

INSERT INTO componente_sanguineo (nombre, descripcion) 
VALUES ('Plaquetas', 'Ayudan a la coagulación de la sangre deteniendo hemorragias en heridas o lesiones.');

INSERT INTO componente_sanguineo (nombre, descripcion) 
VALUES ('Plasma', 'Contiene proteínas y factores de coagulación, transporta nutrientes, hormonas y desechos.');


SELECT * FROM donacion;


--TRIGGERS
CREATE OR REPLACE TRIGGER trg_audit_donacion
AFTER INSERT ON donacion
FOR EACH ROW
BEGIN
  INSERT INTO bitacora (id_bitacora, tabla_afectada, accion, fecha, id_usuario)
  VALUES (bitacora_seq.NEXTVAL, 'DONACION', 'INSERCION', SYSDATE, :NEW.id_usuario_registra);
END;
/


CREATE OR REPLACE TRIGGER trg_valida_volumen
BEFORE INSERT ON donacion
FOR EACH ROW
BEGIN
  IF :NEW.volumen_ml < 350 THEN
    RAISE_APPLICATION_ERROR(-20001, 'El volumen mínimo permitido es de 350 ml.');
  END IF;
END;
/


CREATE OR REPLACE TRIGGER trg_bloquear_usuario_inactivo
BEFORE INSERT ON donacion
FOR EACH ROW
DECLARE
  estado_usuario VARCHAR2(10);
BEGIN
  SELECT estado INTO estado_usuario FROM usuario WHERE id_usuario = :NEW.id_usuario_registra;

  IF estado_usuario <> 'activo' THEN
    RAISE_APPLICATION_ERROR(-20002, 'El usuario no está activo y no puede registrar donaciones.');
  END IF;
END;
/


CREATE OR REPLACE TRIGGER trg_generar_componentes
AFTER INSERT ON donacion
FOR EACH ROW
WHEN (NEW.estado = 'aceptada')
BEGIN
  INSERT INTO donacion_componente (id_donacion_componente, id_donacion, id_componente, unidades)
  VALUES (donacion_comp_seq.NEXTVAL, :NEW.id_donacion, 1, 1);

  INSERT INTO donacion_componente (id_donacion_componente, id_donacion, id_componente, unidades)
  VALUES (donacion_comp_seq.NEXTVAL, :NEW.id_donacion, 2, 1);

  INSERT INTO donacion_componente (id_donacion_componente, id_donacion, id_componente, unidades)
  VALUES (donacion_comp_seq.NEXTVAL, :NEW.id_donacion, 3, 1);
END;
/


CREATE OR REPLACE TRIGGER trg_validar_fecha_donacion
BEFORE INSERT ON donacion
FOR EACH ROW
BEGIN
  IF :NEW.fecha > SYSDATE THEN
    RAISE_APPLICATION_ERROR(-20003, 'La fecha de la donación no puede ser futura.');
  END IF;
END;
/
