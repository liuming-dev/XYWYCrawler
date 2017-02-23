DROP TABLE IF EXISTS 2016_q_reply_2;
DROP TABLE IF EXISTS 2016_q_reply;
DROP TABLE IF EXISTS 2016_q_info;

CREATE TABLE 2016_q_info
(
  q_url      VARCHAR(52)   NOT NULL,
  q_title    VARCHAR(30)   NOT NULL,
  q_body     VARCHAR(1000) NOT NULL,
  q_datetime DATETIME      NOT NULL,
  u_name     VARCHAR(20),
  u_sex      char(1),
  u_age      VARCHAR(8),
  keshi1     VARCHAR(10),
  keshi2     VARCHAR(10),
  run_date   DATE          NOT NULL,
  PRIMARY KEY (q_url)
);


CREATE TABLE 2016_q_reply
(
  q_url          VARCHAR(52)       NOT NULL,
  reply_id       VARCHAR(60)       NOT NULL,
  doctor_url     VARCHAR(50)       NOT NULL,
  reply_body     VARCHAR(1000)     NOT NULL,
  reply_datetime DATETIME          NOT NULL,
  pu_index       SMALLINT UNSIGNED NOT NULL,
  accepted       TINYINT UNSIGNED  NOT NULL DEFAULT '0',
  run_date       DATE              NOT NULL,
  PRIMARY KEY (reply_id)
);


CREATE TABLE 2016_q_reply_2
(
  reply_id       VARCHAR(60)      NOT NULL,
  reply2_id      VARCHAR(63)      NOT NULL,
  reply_body     VARCHAR(500)     NOT NULL,
  who_reply      TINYINT UNSIGNED NOT NULL,
  reply_datetime DATETIME         NOT NULL,
  run_date       DATE             NOT NULL,
  PRIMARY KEY (reply2_id)
);
