 
-- PAQUETE PARA DONACIÓN
CREATE OR REPLACE PACKAGE PAQ_DONACION AS
  PROCEDURE REGISTRAR_DONACION (
    p_id_donante IN VARCHAR2,
    p_id_centro IN NUMBER,
    p_fecha IN DATE,
    p_volumen_ml IN NUMBER,
    p_estado IN VARCHAR2,
    p_id_usuario IN VARCHAR2
  );
END PAQ_DONACION;
/

CREATE OR REPLACE PACKAGE BODY PAQ_DONACION AS
  PROCEDURE REGISTRAR_DONACION (
    p_id_donante IN VARCHAR2,
    p_id_centro IN NUMBER,
    p_fecha IN DATE,
    p_volumen_ml IN NUMBER,
    p_estado IN VARCHAR2,
    p_id_usuario IN VARCHAR2
  ) IS
  BEGIN
    INSERT INTO donacion (
      id_donante, id_centro, fecha, volumen_ml, estado, id_usuario_registra
    ) VALUES (
      p_id_donante, p_id_centro, p_fecha, p_volumen_ml, p_estado, p_id_usuario
    );
  END;
END PAQ_DONACION;
/

-- PAQUETE PARA RECHAZO
CREATE OR REPLACE PACKAGE PAQ_RECHAZO AS
  PROCEDURE REGISTRAR_RECHAZO (
    p_id_donacion IN NUMBER,
    p_id_causa IN NUMBER,
    p_observaciones IN VARCHAR2,
    p_usuario_registra IN VARCHAR2
  );
END PAQ_RECHAZO;
/

CREATE OR REPLACE PACKAGE BODY PAQ_RECHAZO AS
  PROCEDURE REGISTRAR_RECHAZO (
    p_id_donacion IN NUMBER,
    p_id_causa IN NUMBER,
    p_observaciones IN VARCHAR2,
    p_usuario_registra IN VARCHAR2
  ) IS
  BEGIN
    INSERT INTO rechazo (
      id_donacion, id_causa, observaciones, usuario_registra
    ) VALUES (
      p_id_donacion, p_id_causa, p_observaciones, p_usuario_registra
    );
  END;
END PAQ_RECHAZO;
/

SELECT object_name, object_type
FROM user_objects
WHERE object_name = 'PAQ_DONANTE';

GRANT EXECUTE ON PAQ_DONANTE TO ROL_TECNICO;


CREATE OR REPLACE PACKAGE PAQ_DONANTE AS
  PROCEDURE REGISTRAR_DONANTE (
    p_id_donante        IN VARCHAR2,
    p_nombre            IN VARCHAR2,
    p_apellido          IN VARCHAR2,
    p_direccion         IN VARCHAR2,
    p_fecha_nacimiento  IN DATE,
    p_sexo              IN VARCHAR2,
    p_telefono          IN VARCHAR2,
    p_correo            IN VARCHAR2,
    p_id_tipo_sangre    IN NUMBER
  );
END PAQ_DONANTE;
/

CREATE OR REPLACE PACKAGE BODY PAQ_DONANTE AS
  PROCEDURE REGISTRAR_DONANTE (
    p_id_donante        IN VARCHAR2,
    p_nombre            IN VARCHAR2,
    p_apellido          IN VARCHAR2,
    p_direccion         IN VARCHAR2,
    p_fecha_nacimiento  IN DATE,
    p_sexo              IN VARCHAR2,
    p_telefono          IN VARCHAR2,
    p_correo            IN VARCHAR2,
    p_id_tipo_sangre    IN NUMBER
  ) IS
  BEGIN
    INSERT INTO donante (
      id_donante, nombre, apellido, direccion,
      fecha_nacimiento, sexo, telefono, correo, id_tipo_sangre
    ) VALUES (
      p_id_donante, p_nombre, p_apellido, p_direccion,
      p_fecha_nacimiento, p_sexo, p_telefono, p_correo, p_id_tipo_sangre
    );
  END;
END PAQ_DONANTE;
/

CREATE OR REPLACE VIEW estadisticas AS
SELECT 
    t.tipo AS tipo_sangre,
    c.nombre AS componente,
    SUM(i.unidades_disponibles) AS total_unidades
FROM inventario i
JOIN tipo_sangre t ON i.id_tipo_sangre = t.id_tipo_sangre
JOIN componente_sanguineo c ON i.id_componente = c.id_componente
GROUP BY t.tipo, c.nombre;


CREATE ROLE ROL_TECNICO;
CREATE ROLE ROL_DIPLOMADO;
CREATE ROLE ROL_MICROBIOLOGO;
CREATE ROLE ROL_JEFATURA;
CREATE ROLE ROL_ADMIN_BD;


/* ASIGNAR ROLES*/
CREATE USER tecnico01 IDENTIFIED BY tecnico123;
GRANT CONNECT TO tecnico01;
GRANT ROL_TECNICO TO tecnico01;

CREATE USER diplomado01 IDENTIFIED BY diplo123;
GRANT CONNECT TO diplomado01;
GRANT ROL_DIPLOMADO TO diplomado01;

CREATE USER micro01 IDENTIFIED BY micro123;
GRANT CONNECT TO micro01;
GRANT ROL_MICROBIOLOGO TO micro01;

CREATE USER jefatura01 IDENTIFIED BY jefa123;
GRANT CONNECT TO jefatura01;
GRANT ROL_JEFATURA TO jefatura01;

CREATE USER adminbd IDENTIFIED BY admin123;
GRANT CONNECT, DBA TO adminbd;
GRANT ROL_ADMIN_BD TO adminbd;

/* ASIGNAR LOS PIVILEGIOS*/

--ROL_TECNICO
GRANT EXECUTE ON PAQ_DONANTE TO ROL_TECNICO;
GRANT EXECUTE ON PAQ_DONACION TO ROL_TECNICO;

-- ROL_DIPLOMADO
GRANT EXECUTE ON PAQ_DONANTE TO ROL_DIPLOMADO;
GRANT EXECUTE ON PAQ_DONACION TO ROL_DIPLOMADO;
GRANT EXECUTE ON PAQ_RECHAZO TO ROL_DIPLOMADO;
GRANT SELECT, INSERT, UPDATE ON inventario TO ROL_DIPLOMADO;

-- ROL_MICROBIOLOGO
GRANT EXECUTE ON PAQ_DONANTE TO ROL_MICROBIOLOGO;
GRANT EXECUTE ON PAQ_DONACION TO ROL_MICROBIOLOGO;
GRANT EXECUTE ON PAQ_RECHAZO TO ROL_MICROBIOLOGO;
GRANT SELECT, INSERT, UPDATE ON inventario TO ROL_MICROBIOLOGO;
GRANT SELECT ON estadisticas TO ROL_MICROBIOLOGO;

-- ROL_JEFATURA
GRANT EXECUTE ON PAQ_DONANTE TO ROL_JEFATURA;
GRANT EXECUTE ON PAQ_DONACION TO ROL_JEFATURA;
GRANT EXECUTE ON PAQ_RECHAZO TO ROL_JEFATURA;
GRANT SELECT, INSERT, UPDATE ON inventario TO ROL_JEFATURA;
GRANT SELECT ON estadisticas TO ROL_JEFATURA;
GRANT SELECT ON bitacora TO ROL_JEFATURA;

-- ROL_ADMIN_BD
GRANT ALL PRIVILEGES TO ROL_ADMIN_BD;