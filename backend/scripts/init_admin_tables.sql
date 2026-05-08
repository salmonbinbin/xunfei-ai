-- ============================================
-- AI小商 管理端数据库初始化脚本
-- ============================================

-- 创建 admins 表
CREATE TABLE IF NOT EXISTS admins (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '管理员ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '管理员用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码（bcrypt哈希）',
    nickname VARCHAR(100) NOT NULL COMMENT '昵称',
    role VARCHAR(20) DEFAULT 'super_admin' COMMENT '角色：super_admin/auditor',
    status ENUM('active', 'disabled') DEFAULT 'active' COMMENT '状态',
    last_login DATETIME COMMENT '最后登录时间',
    login_count INT DEFAULT 0 COMMENT '登录次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted TINYINT DEFAULT 0 COMMENT '软删除标记',
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';

-- 创建 admin_logs 表
CREATE TABLE IF NOT EXISTS admin_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    admin_id INT NOT NULL COMMENT '管理员ID',
    admin_name VARCHAR(100) NOT NULL COMMENT '管理员昵称（冗余）',
    action VARCHAR(100) NOT NULL COMMENT '操作类型',
    action_text VARCHAR(200) COMMENT '操作描述',
    target_type VARCHAR(50) COMMENT '操作对象类型',
    target_id INT COMMENT '操作对象ID',
    detail TEXT COMMENT '详细信息（JSON）',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent TEXT COMMENT '浏览器信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_admin_id (admin_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员操作日志表';

-- 创建 user_logs 表
CREATE TABLE IF NOT EXISTS user_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id INT NOT NULL COMMENT '用户ID',
    user_type ENUM('student', 'teacher') NOT NULL COMMENT '用户类型',
    action VARCHAR(100) NOT NULL COMMENT '操作类型',
    module VARCHAR(50) NOT NULL COMMENT '功能模块',
    duration_ms INT DEFAULT 0 COMMENT '操作耗时（毫秒）',
    success TINYINT DEFAULT 1 COMMENT '是否成功：1成功 0失败',
    error_msg TEXT COMMENT '错误信息',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_module (module),
    INDEX idx_created_at (created_at),
    INDEX idx_user_type (user_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户操作日志表';

-- 创建 api_logs 表
CREATE TABLE IF NOT EXISTS api_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    api_name VARCHAR(50) NOT NULL COMMENT 'API名称',
    api_type ENUM('xfyun', 'other') DEFAULT 'xfyun' COMMENT 'API类型',
    call_type ENUM('success', 'fail', 'retry') NOT NULL COMMENT '调用结果',
    error_code VARCHAR(50) COMMENT '错误码',
    error_msg TEXT COMMENT '错误信息',
    response_time_ms INT COMMENT '响应时间（毫秒）',
    request_params JSON COMMENT '请求参数（脱敏）',
    user_id INT COMMENT '关联用户ID',
    user_type ENUM('student', 'teacher', 'admin', 'anonymous') COMMENT '用户类型',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '调用时间',
    INDEX idx_api_name (api_name),
    INDEX idx_call_type (call_type),
    INDEX idx_created_at (created_at),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API调用日志表';

-- 创建 login_logs 表
CREATE TABLE IF NOT EXISTS login_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id INT NOT NULL COMMENT '用户ID',
    user_type ENUM('student', 'teacher') NOT NULL COMMENT '用户类型',
    login_method ENUM('phone', 'wechat', 'admin') NOT NULL COMMENT '登录方式',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent TEXT COMMENT '浏览器信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    INDEX idx_user_id (user_id),
    INDEX idx_user_type (user_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';

-- 插入默认管理员（密码：123456）
-- bcrypt hash for '123456': $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4bFdKNKrC4AxqJGe
INSERT INTO admins (username, password, nickname, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4bFdKNKrC4AxqJGe', '超级管理员', 'super_admin')
ON DUPLICATE KEY UPDATE username = username;

SELECT '管理端数据库表创建完成' AS result;
SELECT CONCAT('默认管理员: admin / 123456') AS admin_note;