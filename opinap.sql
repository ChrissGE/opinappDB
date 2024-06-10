use opinapp;

DROP TABLE IF EXISTS map_global_scorings;
DROP TABLE IF EXISTS global_scorings_value;
DROP TABLE IF EXISTS traces;
DROP TABLE IF EXISTS answer;
DROP TABLE IF EXISTS scoring_per_map_review;
DROP TABLE IF EXISTS scorings_value;
DROP TABLE IF EXISTS scorings;
DROP TABLE IF EXISTS mapTextReward;
DROP TABLE IF EXISTS mapTextQuestions;
DROP TABLE IF EXISTS mapTextMenu;
DROP TABLE IF EXISTS texts;
DROP TABLE IF EXISTS languages;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS question_condition;
DROP TABLE IF EXISTS mapQuestions;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS questionaryMenu;
DROP TABLE IF EXISTS questionaries;
DROP TABLE IF EXISTS ticket;
DROP TABLE IF EXISTS rewards;
DROP TABLE IF EXISTS company;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    email VARCHAR(50) PRIMARY KEY,
    username VARCHAR(25),
    gender ENUM('Male', 'Female', 'Other'),
    birth_date DATE,
    points INT
);

CREATE TABLE company (
    company_code VARCHAR(20) PRIMARY KEY,
    company_name VARCHAR(50),
    address TEXT,
    coords VARCHAR(50),
    image_company LONGBLOB,
    email VARCHAR(50)
);

CREATE TABLE rewards (
    id_reward INT AUTO_INCREMENT PRIMARY KEY,
    rewards_price INT,
    company_code VARCHAR(20),
    stock INT,
    image_reward LONGBLOB,
    FOREIGN KEY(company_code) REFERENCES company(company_code)
);

CREATE TABLE ticket (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    id_reward INT,
    email VARCHAR(50),
    FOREIGN KEY(id_reward) REFERENCES rewards(id_reward),
    FOREIGN KEY(email) REFERENCES users(email)
);

CREATE TABLE questionaries (
    id_questionary INT AUTO_INCREMENT PRIMARY KEY,
    questionary_name VARCHAR(100),
    points_reward INT,
    company_code VARCHAR(20),
    FOREIGN KEY(company_code) REFERENCES company(company_code)
);

CREATE TABLE questionaryMenu (
    id_questionaryMenu INT AUTO_INCREMENT PRIMARY KEY,
    id_questionary INT,
    FOREIGN KEY(id_questionary) REFERENCES questionaries(id_questionary)
);

CREATE TABLE questions (
    id_questions INT AUTO_INCREMENT PRIMARY KEY,
    question_type ENUM('Text', 'Yes and no'),
    text VARCHAR(255)
);

CREATE TABLE mapQuestions(
    id_questions INT,
    id_questionaryMenu INT,
    PRIMARY key(id_questions,id_questionaryMenu),
    FOREIGN KEY(id_questions) REFERENCES questions(id_questions),
    FOREIGN KEY(id_questionaryMenu) REFERENCES questionaryMenu(id_questionaryMenu)
);

CREATE TABLE question_condition (
    id_questions INT,
    id_questionaryMenu INT,
    answer_value INT,
    score_value DECIMAL(10,2),
    PRIMARY KEY(id_questions, id_questionaryMenu),
    FOREIGN KEY(id_questions,id_questionaryMenu) REFERENCES mapQuestions(id_questions,id_questionaryMenu)
);

CREATE TABLE reviews (
    id_review INT AUTO_INCREMENT PRIMARY KEY,
    id_questionary INT,
    email VARCHAR(50),
    insert_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(id_questionary) REFERENCES questionaries(id_questionary),
    FOREIGN KEY(email) REFERENCES users(email)
);

CREATE TABLE languages(
id_language INT AUTO_INCREMENT PRIMARY KEY,
name_language VARCHAR(50)
);

CREATE TABLE texts(
    id_text INT AUTO_INCREMENT PRIMARY KEY,
    text VARCHAR(200),
    id_language INT,
    FOREIGN KEY(id_language) REFERENCES languages(id_language)
);
CREATE TABLE mapTextQuestions(
    id_text INT,
    id_questions INT,
    PRIMARY key(id_text,id_questions),
    FOREIGN KEY(id_text) REFERENCES texts(id_text),
    FOREIGN KEY(id_questions) REFERENCES questions(id_questions)
);

CREATE TABLE mapTextReward(
    id_text INT,
    id_reward INT,
    PRIMARY key(id_text,id_reward),
    FOREIGN KEY(id_text) REFERENCES texts(id_text),
    FOREIGN KEY(id_reward) REFERENCES rewards(id_reward)
);
CREATE TABLE mapTextMenu(
    id_text INT,
    id_questionaryMenu INT,
    PRIMARY key(id_text,id_questionaryMenu),
    FOREIGN KEY(id_text) REFERENCES texts(id_text),
    FOREIGN KEY(id_questionaryMenu) REFERENCES questionaryMenu(id_questionaryMenu)
);
CREATE TABLE answer (
    id_answer INT AUTO_INCREMENT PRIMARY KEY,
    id_questions INT,
    id_questionaryMenu INT,
    id_review INT,
    text VARCHAR(255),
    binary_answer INT,
    FOREIGN KEY(id_questions,id_questionaryMenu) REFERENCES mapQuestions(id_questions,id_questionaryMenu),
    FOREIGN KEY(id_review) REFERENCES reviews(id_review)
);

CREATE TABLE scorings (
    id_scoring INT AUTO_INCREMENT PRIMARY KEY,
    scoring_name VARCHAR(160),
    id_questionaryMenu INT,
    FOREIGN KEY(id_questionaryMenu) REFERENCES questionaryMenu(id_questionaryMenu)
);

CREATE TABLE scorings_value(
    id_scoring_value INT AUTO_INCREMENT PRIMARY KEY,
    id_scoring INT,
    mark DECIMAL(10,2),
    FOREIGN KEY(id_scoring) REFERENCES scorings(id_scoring)
);

CREATE TABLE scoring_per_map_review (
    id_scoring_per_review INT AUTO_INCREMENT PRIMARY KEY,
    id_review INT,
    id_questionaryMenu INT,
    mark DECIMAL(10,2),
    FOREIGN KEY(id_review) REFERENCES reviews(id_review),
    FOREIGN KEY(id_questionaryMenu) REFERENCES questionaryMenu(id_questionaryMenu)
);

CREATE TABLE traces(
    company_code VARCHAR(20) PRIMARY KEY,
    FOREIGN KEY(company_code) REFERENCES company(company_code)
);

CREATE TABLE global_scorings_value(
    id_global_scoring_value INT AUTO_INCREMENT PRIMARY KEY,
    company_code VARCHAR(20),
    mark DECIMAL(10,2),
    FOREIGN KEY(company_code) REFERENCES company(company_code)
);

CREATE TABLE map_global_scorings(
    company_code VARCHAR(20),
    id_scoring INT,
    percentage DECIMAL(10,2),
    PRIMARY KEY(company_code,id_scoring),
    FOREIGN KEY(company_code) REFERENCES company(company_code),
    FOREIGN KEY(id_scoring) REFERENCES scorings(id_scoring)
);
