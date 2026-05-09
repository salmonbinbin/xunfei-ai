-- 初始化日志表
-- 运行方式: mysql -u root -p ai_xiaoshang < init_logs_table.sql

-- 1. 登录日志表
CREATE TABLE IF NOT EXISTS `login_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `user_type` ENUM('student', 'teacher') NOT NULL COMMENT '用户类型',
    `login_method` ENUM('phone', 'wechat', 'admin') NOT NULL COMMENT '登录方式',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `user_agent` TEXT COMMENT '浏览器信息',
    `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_user_type` (`user_type`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';

-- 2. API调用日志表
CREATE TABLE IF NOT EXISTS `api_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    `api_name` VARCHAR(50) NOT NULL COMMENT 'API名称',
    `api_type` ENUM('xfyun', 'other') DEFAULT 'xfyun' COMMENT 'API类型',
    `call_type` ENUM('success', 'fail', 'retry') NOT NULL COMMENT '调用结果',
    `error_code` VARCHAR(50) COMMENT '错误码',
    `error_msg` TEXT COMMENT '错误信息',
    `response_time_ms` INT COMMENT '响应时间（毫秒）',
    `request_params` TEXT COMMENT '请求参数（脱敏）',
    `user_id` INT COMMENT '关联用户ID',
    `user_type` ENUM('student', 'teacher', 'admin', 'anonymous') COMMENT '用户类型',
    `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '调用时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_api_name` (`api_name`),
    INDEX `idx_call_type` (`call_type`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API调用日志表';

-- 3. 用户操作日志表
CREATE TABLE IF NOT EXISTS `user_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `user_type` ENUM('student', 'teacher') NOT NULL COMMENT '用户类型',
    `action` VARCHAR(100) NOT NULL COMMENT '操作类型',
    `module` VARCHAR(50) NOT NULL COMMENT '功能模块',
    `duration_ms` INT DEFAULT 0 COMMENT '操作耗时（毫秒）',
    `success` TINYINT(1) DEFAULT 1 COMMENT '是否成功：1成功 0失败',
    `error_msg` TEXT COMMENT '错误信息',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_user_type` (`user_type`),
    INDEX `idx_action` (`action`),
    INDEX `idx_module` (`module`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户操作日志表';

SELECT 'Log tables created successfully!' AS status;