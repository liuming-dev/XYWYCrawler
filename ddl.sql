drop table if exists q_reply_2;
drop table if exists q_reply;
drop table if exists q_info;

create table q_info
(
	q_url varchar(52) not null,
	q_title varchar(30) not null,
	q_body varchar(1000) not null,
	q_datetime datetime not null,
	u_name varchar(20),
	u_sex char(1),
	u_age varchar(8),
	keshi1 varchar(10),
	keshi2 varchar(10),
	run_date date not null,
	run_number tinyint unsigned not null,
	primary key (q_url,run_date)
);


create table q_reply
(
	q_url varchar(52) not null,
	reply_id varchar(60) not null,
	doctor_url varchar(50) not null,
	reply_body varchar(1000) not null,
	reply_datetime datetime not null,
	pu_index smallint unsigned not null,
	accepted tinyint unsigned not null default '0',
	run_date date not null,
	run_number tinyint unsigned not null,
	primary key (reply_id,run_date)
);


create table q_reply_2
(
	reply_id varchar(60) not null,
	reply2_id varchar(63) not null,
	reply_body varchar(500) not null,
	who_reply tinyint unsigned not null,
	reply_datetime datetime not null,
	run_date date not null,
	run_number tinyint unsigned not null,
	primary key(reply2_id,run_date)
);
