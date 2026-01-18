-- 数据库表结构DDL脚本
-- 生成时间: 2026-01-18
-- 适用于MySQL数据库


CREATE TABLE interest_tag (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	category VARCHAR(50), 
	description VARCHAR(200), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (name)
)




CREATE TABLE user (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	openid VARCHAR(100), 
	nickname VARCHAR(50) NOT NULL, 
	avatar VARCHAR(200), 
	gender INTEGER, 
	phone VARCHAR(20), 
	password_hash VARCHAR(255), 
	real_name VARCHAR(50), 
	id_card VARCHAR(20), 
	bio TEXT, 
	singing_style VARCHAR(100), 
	credit_score INTEGER, 
	is_verified BOOL, 
	`role` VARCHAR(20), 
	merchant_application_status VARCHAR(20), 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (openid), 
	UNIQUE (phone)
)




CREATE TABLE activity (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	title VARCHAR(100) NOT NULL, 
	description TEXT NOT NULL, 
	activity_type VARCHAR(50), 
	location VARCHAR(100) NOT NULL, 
	longitude FLOAT, 
	latitude FLOAT, 
	start_time DATETIME NOT NULL, 
	end_time DATETIME NOT NULL, 
	registration_deadline DATETIME, 
	refund_deadline DATETIME, 
	organizer_id INTEGER NOT NULL, 
	current_participants INTEGER, 
	max_participants INTEGER NOT NULL, 
	room_type VARCHAR(50), 
	music_style VARCHAR(100), 
	accept_beginners BOOL, 
	accept_microphone_king BOOL, 
	cost_type VARCHAR(50), 
	estimated_cost_per_person FLOAT, 
	total_cost FLOAT, 
	deposit_amount FLOAT, 
	status VARCHAR(50), 
	is_published BOOL, 
	requirements TEXT, 
	cover_image_url VARCHAR(255), 
	images TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organizer_id) REFERENCES user (id)
)




CREATE TABLE user_tag (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	tag_id INTEGER NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	FOREIGN KEY(tag_id) REFERENCES interest_tag (id)
)




CREATE TABLE activity_tag (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	activity_id INTEGER NOT NULL, 
	tag_id INTEGER NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(activity_id) REFERENCES activity (id), 
	FOREIGN KEY(tag_id) REFERENCES interest_tag (id)
)




CREATE TABLE enrollment (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	activity_id INTEGER NOT NULL, 
	status VARCHAR(50), 
	message TEXT, 
	cost_paid FLOAT, 
	deposit_paid FLOAT, 
	deposit_transferred BOOL, 
	cancel_time DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	FOREIGN KEY(activity_id) REFERENCES activity (id)
)




CREATE TABLE review (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	from_user_id INTEGER NOT NULL, 
	to_user_id INTEGER NOT NULL, 
	activity_id INTEGER NOT NULL, 
	rating INTEGER NOT NULL, 
	comment TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(from_user_id) REFERENCES user (id), 
	FOREIGN KEY(to_user_id) REFERENCES user (id), 
	FOREIGN KEY(activity_id) REFERENCES activity (id)
)



