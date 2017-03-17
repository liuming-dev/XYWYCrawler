DROP TABLE IF EXISTS f_all_doctor_info;
DROP TABLE IF EXISTS f_evaluation_4_doctor;
DROP TABLE IF EXISTS f_evaluation_text_4_doctor;
DROP TABLE IF EXISTS f_service_info;

CREATE TABLE IF NOT EXISTS f_all_doctor_info
(
  url                VARCHAR(100) NOT NULL,
  d_name             VARCHAR(30),
  d_rank             VARCHAR(10),
  d_hosp             VARCHAR(50),
  medals             VARCHAR(80),
  send_word          VARCHAR(100),
  week_service       VARCHAR(30),
  month_service      VARCHAR(30),
  old_week_service   VARCHAR(30),
  old_month_service  VARCHAR(30),
  help_family_count  VARCHAR(10),
  help_patient_count VARCHAR(10),
  good_at            VARCHAR(500),
  introduction       VARCHAR(1000),
  honor              VARCHAR(500),
  PRIMARY KEY (url)
);


CREATE TABLE IF NOT EXISTS f_evaluation_4_doctor
(
  url         VARCHAR(100) NOT NULL,
  total_score DECIMAL(5, 2),
  ysgm        INT,
  nxxz        INT,
  mshc        INT,
  ysyb        INT,
  fcmy        INT,
  zy          INT,
  hybz        INT,
  bgxx        INT,
  PRIMARY KEY (url)
);


CREATE TABLE IF NOT EXISTS f_evaluation_text_4_doctor
(
  url        VARCHAR(100) NOT NULL,
  u_name     VARCHAR(30),
  eval_atti  VARCHAR(10),
  eval_score VARCHAR(10),
  eval_text  VARCHAR(500),
  eval_time  DATETIME,
  PRIMARY KEY (url)
);

CREATE TABLE IF NOT EXISTS f_service_info
(
  url            VARCHAR(100) NOT NULL,
  u_name         VARCHAR(20),
  service_type   TINYINT UNSIGNED,
  service_count  INT UNSIGNED,
  service_price  VARCHAR(30),
  service_status VARCHAR(10),
  service_time   DATETIME,
  PRIMARY KEY (url)
);
