CREATE DATABASE IF NOT EXISTS `fastapi_demo`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `fastapi_demo`;

CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) DEFAULT NULL,
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_username` (`username`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO `users` (`username`, `email`, `password_hash`, `full_name`, `is_active`) VALUES
    (
        'admin',
        'admin@example.com',
        'pbkdf2_sha256$100000$adminsalt$8ab9ebe5a0c116bdfb6ab37f8728e5fde23814a12ba552a73805b3aefc707cfc',
        'Administrator',
        TRUE
    ),
    (
        'testuser',
        'test@example.com',
        'pbkdf2_sha256$100000$testsalt$0ed5971b19e07285b1e884f98f7b609da489de096535daf645c62d017fb206f3',
        'Test User',
        TRUE
    );
