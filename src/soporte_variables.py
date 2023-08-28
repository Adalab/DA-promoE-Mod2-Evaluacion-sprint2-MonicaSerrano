query_paises = """
CREATE TABLE IF NOT EXISTS `paises` (
  `idestado` INT NOT NULL AUTO_INCREMENT,
  `nombre_pais` VARCHAR(45) NOT NULL,
  `nombre_provincia` VARCHAR(45) NOT NULL,
  `latitud` DECIMAL NOT NULL,
  `longitud` DECIMAL NOT NULL,
  PRIMARY KEY (`idestado`));"""

query_universidades = """
CREATE TABLE IF NOT EXISTS `universidades` (
  `iduniversidades` INT NOT NULL AUTO_INCREMENT,
  `nombre_universidad` VARCHAR(100) NOT NULL,
  `pagina_web` VARCHAR(100) NOT NULL,
  `paises_idestado` INT NOT NULL,
  PRIMARY KEY (`iduniversidades`),
  CONSTRAINT `fk_universidades_paises`
    FOREIGN KEY (`paises_idestado`)
    REFERENCES `paises` (`idestado`));"""

cambios = {'NV':'Nevada','VA':'Virginia', 'TX':'Texas','IN':'Indianapolis','CA':'California','NY':'New York', 'ND':'North Dakota', 'MI':'Michigan',
       'GA':'Georgia', 'New York, NY':'New York','Ciudad Autónoma de Buenos Aires':'Buenos Aires'}