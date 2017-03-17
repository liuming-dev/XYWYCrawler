-- DROP TABLE IF EXISTS q_reply2;
-- DROP TABLE IF EXISTS q_reply1;
-- DROP TABLE IF EXISTS q_info;

CREATE TABLE IF NOT EXISTS q_info
(
  q_url      VARCHAR(100) NOT NULL,
  q_title    VARCHAR(100),
  q_body     VARCHAR(1500),
  q_datetime DATETIME,
  keshi1     VARCHAR(10),
  keshi2     VARCHAR(10),
  u_name     VARCHAR(30),
  u_sex      VARCHAR(10),
  u_age      VARCHAR(10),
  PRIMARY KEY (q_url)
);


CREATE TABLE IF NOT EXISTS q_reply1
(
  reply_id       VARCHAR(100) NOT NULL,
  doctor_url     VARCHAR(100),
  reply_body     VARCHAR(1500),
  reply_datetime DATETIME,
  pu_index       SMALLINT UNSIGNED,
  accepted       TINYINT UNSIGNED,
  PRIMARY KEY (reply_id)
);


CREATE TABLE IF NOT EXISTS q_reply2
(
  reply2_id       VARCHAR(100) NOT NULL,
  reply2_body     VARCHAR(1000),
  who_reply       TINYINT UNSIGNED,
  reply2_datetime DATETIME,
  PRIMARY KEY (reply2_id)
);
