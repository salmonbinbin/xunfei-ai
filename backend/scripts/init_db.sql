-- ============================================================
-- AI小商 - 数据库初始化脚本 (v3.0)
-- MySQL 8.0+
-- 运行: mysql -u root -p < init_db.sql
--
-- 此脚本是数据库唯一真源（Single Source of Truth）。
-- 所有表结构必须与此脚本和 app/models/ 中的模型保持一致。
-- 修改数据库结构时，请同步更新此文件和对应的模型文件。
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ai_xiaoshang
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE ai_xiaoshang;

-- ============================================================
-- 1. users - 用户表
-- 模型: app.models.user.User
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `openid` VARCHAR(64) COMMENT '微信openid',
  `unionid` VARCHAR(64) COMMENT '微信unionid',
  `nickname` VARCHAR(64) COMMENT '昵称',
  `phone` VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号（登录账号）',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码hash',
  `avatar_url` VARCHAR(500) COMMENT '头像URL',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '账号状态：active/disabled',
  `disable_reason` TEXT COMMENT '禁用原因',
  `role` ENUM('student', 'teacher', 'admin') DEFAULT 'student' COMMENT '角色',
  `last_login` DATETIME COMMENT '最后登录',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  INDEX `idx_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 2. student_profiles - 学生画像表
-- 模型: app.models.user.StudentProfile
-- ============================================================
CREATE TABLE IF NOT EXISTS `student_profiles` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL UNIQUE COMMENT '关联users',
  `major` VARCHAR(100) COMMENT '专业',
  `grade` TINYINT COMMENT '年级1-4',
  `class_name` VARCHAR(50) COMMENT '班级',
  `goal` VARCHAR(20) COMMENT '考研/考公/就业/出国/未定',
  `goal_detail` TEXT COMMENT '目标详细描述',
  `voice_prefer` TINYINT(1) DEFAULT 1 COMMENT '偏好语音',
  `emotion_mode` VARCHAR(20) DEFAULT 'normal' COMMENT 'normal/emotion',
  `gpa` DECIMAL(3,2) COMMENT '绩点',
  `completed_courses` JSON COMMENT '已修课程',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生画像表';

-- ============================================================
-- 3. teacher_profiles - 教师画像表
-- 模型: app.models.teacher_profile.TeacherProfile
-- ============================================================
CREATE TABLE IF NOT EXISTS `teacher_profiles` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  `user_id` INT NOT NULL UNIQUE COMMENT '关联users',
  `department` VARCHAR(100) COMMENT '院系',
  `office` VARCHAR(100) COMMENT '办公室',
  `title` VARCHAR(50) COMMENT '职称（教授/副教授/讲师）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师画像表';

-- ============================================================
-- 4. courses - 课程表
-- 模型: app.models.course.Course
-- ============================================================
CREATE TABLE IF NOT EXISTS `courses` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL COMMENT '关联users',
  `name` VARCHAR(100) NOT NULL COMMENT '课程名',
  `code` VARCHAR(20) COMMENT '课程代码',
  `credit` DECIMAL(3,1) COMMENT '学分',
  `category` VARCHAR(20) COMMENT '通识/专业/选修',
  `day_of_week` TINYINT NOT NULL COMMENT '周几1-7',
  `start_slot` TINYINT NOT NULL COMMENT '第几节',
  `end_slot` TINYINT NOT NULL COMMENT '第几节',
  `week_range` VARCHAR(20) DEFAULT '1-16周' COMMENT '周次',
  `location` VARCHAR(100) COMMENT '上课地点',
  `teacher` VARCHAR(50) COMMENT '教师',
  `ai_tip` VARCHAR(200) COMMENT 'AI学习建议',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '有效',
  `course_date` DATE COMMENT '课程日期（根据学期开始日期计算）',
  `source` VARCHAR(20) DEFAULT '手动' COMMENT '课程来源：手动/选课助手',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_day` (`user_id`, `day_of_week`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- ============================================================
-- 5. schedules - 日程表
-- 模型: app.models.schedule.Schedule
-- ============================================================
CREATE TABLE IF NOT EXISTS `schedules` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL COMMENT '关联users',
  `event` VARCHAR(200) NOT NULL COMMENT '日程内容',
  `event_type` VARCHAR(20) DEFAULT '日程' COMMENT '类型',
  `day_of_week` TINYINT COMMENT '周几',
  `time_desc` VARCHAR(50) COMMENT '时间描述',
  `location` VARCHAR(100) COMMENT '地点',
  `is_completed` TINYINT(1) DEFAULT 0 COMMENT '已完成',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_today` (`user_id`, `day_of_week`, `is_completed`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日程表';

-- ============================================================
-- 6. review_records - 录音回顾记录
-- 模型: app.models.review.ReviewRecord
-- ============================================================
CREATE TABLE IF NOT EXISTS `review_records` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL COMMENT '关联users',
  `record_type` VARCHAR(10) NOT NULL COMMENT '课程/会议',
  `title` VARCHAR(200) COMMENT '标题',
  `audio_url` VARCHAR(500) COMMENT '音频URL',
  `duration` INT COMMENT '时长(秒)',
  `language` VARCHAR(20) DEFAULT 'mandarin' COMMENT '语言',
  `status` VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/processing/completed/failed',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_status` (`user_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='录音回顾记录';

-- ============================================================
-- 7. transcriptions - 转写结果
-- 模型: app.models.review.Transcription
-- ============================================================
CREATE TABLE IF NOT EXISTS `transcriptions` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `record_id` INT NOT NULL UNIQUE COMMENT '关联review_records',
  `raw_text` LONGTEXT COMMENT '原始转写文字',
  `segments` JSON COMMENT '分段结果',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`record_id`) REFERENCES `review_records`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='转写结果';

-- ============================================================
-- 8. summaries - 总结结果
-- 模型: app.models.review.Summary
-- ============================================================
CREATE TABLE IF NOT EXISTS `summaries` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `record_id` INT NOT NULL UNIQUE COMMENT '关联review_records',
  `topic` VARCHAR(200) COMMENT '主题',
  `key_points` TEXT COMMENT '核心知识点（课程用）',
  `difficulties` TEXT COMMENT '重点难点（课程用）',
  `memorable_quote` VARCHAR(500) COMMENT '金句',
  `next_suggestion` TEXT COMMENT '预习建议（课程用）',
  `discussion_points` TEXT COMMENT '讨论要点（会议用）',
  `resolutions` TEXT COMMENT '决议（会议用）',
  `action_items` TEXT COMMENT '行动项（会议用）',
  `full_text` TEXT COMMENT '完整总结',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`record_id`) REFERENCES `review_records`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='总结结果';

-- ============================================================
-- 9. conversations - 对话会话
-- 模型: app.models.chat.Conversation
-- ============================================================
CREATE TABLE IF NOT EXISTS `conversations` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL COMMENT '关联users',
  `title` VARCHAR(200) COMMENT '会话标题',
  `category` VARCHAR(20) DEFAULT 'general' COMMENT '分类',
  `mode` VARCHAR(20) DEFAULT 'normal' COMMENT 'normal/emotion',
  `context_summary` TEXT COMMENT '上下文摘要',
  `message_count` INT DEFAULT 0 COMMENT '消息数',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_updated` (`user_id`, `updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话会话';

-- ============================================================
-- 10. messages - 消息记录
-- 模型: app.models.chat.Message
-- ============================================================
CREATE TABLE IF NOT EXISTS `messages` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `conv_id` INT NOT NULL COMMENT '关联conversations',
  `role` VARCHAR(10) NOT NULL COMMENT 'user/assistant',
  `content_type` VARCHAR(20) DEFAULT 'text' COMMENT 'text/voice',
  `content` TEXT COMMENT '消息内容',
  `audio_url` VARCHAR(500) COMMENT '语音URL',
  `sentiment` VARCHAR(20) COMMENT '情感分析结果',
  `tokens_used` INT COMMENT 'token消耗',
  `latency_ms` INT COMMENT '响应延迟',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`conv_id`) REFERENCES `conversations`(`id`) ON DELETE CASCADE,
  INDEX `idx_conv_time` (`conv_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息记录';

-- ============================================================
-- 11. knowledge_base - 知识库
-- 模型: app.models.knowledge.KnowledgeBase
-- ============================================================
CREATE TABLE IF NOT EXISTS `knowledge_base` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `category` VARCHAR(50) NOT NULL COMMENT '分类',
  `question` VARCHAR(500) COMMENT '问题',
  `answer` TEXT COMMENT '回答',
  `content` TEXT COMMENT '原始内容',
  `content_vector` TEXT COMMENT '向量',
  `source` VARCHAR(200) COMMENT '来源',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '有效',
  `views` INT DEFAULT 0 COMMENT '查询次数',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  INDEX `idx_category` (`category`),
  INDEX `idx_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库';

-- ============================================================
-- 12. admins - 管理员表
-- 模型: app.models.admin.Admin
-- 注：删除了旧的 admin_users 表，统一使用 admins
-- ============================================================
CREATE TABLE IF NOT EXISTS `admins` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '管理员ID',
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '管理员用户名',
  `password` VARCHAR(255) NOT NULL COMMENT '密码（bcrypt哈希）',
  `nickname` VARCHAR(100) NOT NULL COMMENT '昵称',
  `role` VARCHAR(20) DEFAULT 'super_admin' COMMENT '角色：super_admin/auditor',
  `status` ENUM('active', 'disabled') DEFAULT 'active' COMMENT '状态',
  `last_login` DATETIME COMMENT '最后登录时间',
  `login_count` INT DEFAULT 0 COMMENT '登录次数',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT DEFAULT 0 COMMENT '软删除标记',
  INDEX `idx_username` (`username`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';

-- ============================================================
-- 13. admin_logs - 管理员操作日志表
-- 模型: app.models.admin_log.AdminLog
-- 注：模型覆盖了 id 和 created_at 列
-- ============================================================
CREATE TABLE IF NOT EXISTS `admin_logs` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
  `admin_id` INT NOT NULL COMMENT '管理员ID',
  `admin_name` VARCHAR(100) NOT NULL COMMENT '管理员昵称（冗余）',
  `action` VARCHAR(100) NOT NULL COMMENT '操作类型',
  `action_text` VARCHAR(200) COMMENT '操作描述',
  `target_type` VARCHAR(50) COMMENT '操作对象类型',
  `target_id` INT COMMENT '操作对象ID',
  `detail` TEXT COMMENT '详细信息（JSON）',
  `ip_address` VARCHAR(50) COMMENT 'IP地址',
  `user_agent` TEXT COMMENT '浏览器信息',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`admin_id`) REFERENCES `admins`(`id`) ON DELETE CASCADE,
  INDEX `idx_admin_id` (`admin_id`),
  INDEX `idx_action` (`action`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员操作日志表';

-- ============================================================
-- 14. user_logs - 用户操作日志表
-- 模型: app.models.user_log.UserLog
-- 注：模型覆盖了 id 和 created_at 列
-- ============================================================
CREATE TABLE IF NOT EXISTS `user_logs` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `user_type` ENUM('student', 'teacher') NOT NULL COMMENT '用户类型',
  `action` VARCHAR(100) NOT NULL COMMENT '操作类型',
  `module` VARCHAR(50) NOT NULL COMMENT '功能模块',
  `duration_ms` INT DEFAULT 0 COMMENT '操作耗时（毫秒）',
  `success` TINYINT DEFAULT 1 COMMENT '是否成功：1成功 0失败',
  `error_msg` TEXT COMMENT '错误信息',
  `ip_address` VARCHAR(50) COMMENT 'IP地址',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_action` (`action`),
  INDEX `idx_module` (`module`),
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_user_type` (`user_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户操作日志表';

-- ============================================================
-- 15. api_logs - API调用日志表
-- 模型: app.models.user_log.ApiLog
-- 注：模型覆盖了 id 和 created_at 列；request_params 使用 TEXT 类型（与模型一致）
-- ============================================================
CREATE TABLE IF NOT EXISTS `api_logs` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
  `api_name` VARCHAR(50) NOT NULL COMMENT 'API名称',
  `api_type` ENUM('xfyun', 'other') DEFAULT 'xfyun' COMMENT 'API类型',
  `call_type` ENUM('success', 'fail', 'retry') NOT NULL COMMENT '调用结果',
  `error_code` VARCHAR(50) COMMENT '错误码',
  `error_msg` TEXT COMMENT '错误信息',
  `response_time_ms` INT COMMENT '响应时间（毫秒）',
  `request_params` TEXT COMMENT '请求参数（脱敏）',
  `user_id` INT COMMENT '关联用户ID',
  `user_type` ENUM('student', 'teacher', 'admin', 'anonymous') COMMENT '用户类型',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '调用时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT DEFAULT 0 COMMENT '软删除标记',
  INDEX `idx_api_name` (`api_name`),
  INDEX `idx_call_type` (`call_type`),
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API调用日志表';

-- ============================================================
-- 16. login_logs - 登录日志表
-- 模型: app.models.user_log.LoginLog
-- 注：模型覆盖了 id 和 created_at 列
-- ============================================================
CREATE TABLE IF NOT EXISTS `login_logs` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `user_type` ENUM('student', 'teacher') NOT NULL COMMENT '用户类型',
  `login_method` ENUM('phone', 'wechat', 'admin') NOT NULL COMMENT '登录方式',
  `ip_address` VARCHAR(50) COMMENT 'IP地址',
  `user_agent` TEXT COMMENT '浏览器信息',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_user_type` (`user_type`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';

-- ============================================================
-- 17. grade_records - 成绩记录表
-- 模型: app.models.grade.GradeRecord
-- ============================================================
CREATE TABLE IF NOT EXISTS `grade_records` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  `teacher_id` INT NOT NULL COMMENT '教师用户ID',
  `course_name` VARCHAR(200) NOT NULL COMMENT '课程名称',
  `semester` VARCHAR(50) COMMENT '学期（如2026春季）',
  `class_name` VARCHAR(100) COMMENT '班级名称',
  `file_path` VARCHAR(500) COMMENT '原始Excel路径',
  `weights` JSON COMMENT '成绩权重配置',
  `ai_report` TEXT COMMENT 'AI分析报告内容',
  `stats_data` JSON COMMENT '统计数据（分布、均分等）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`teacher_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_record_teacher` (`teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成绩记录表';

-- ============================================================
-- 18. grade_items - 成绩明细表
-- 模型: app.models.grade.GradeItem
-- 注：列名 ranking（与模型保持一致，不再使用旧名 rank）
-- ============================================================
CREATE TABLE IF NOT EXISTS `grade_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  `record_id` INT NOT NULL COMMENT '关联grade_records',
  `student_name` VARCHAR(100) NOT NULL COMMENT '学生姓名',
  `student_no` VARCHAR(50) COMMENT '学号',
  `usual_score` DECIMAL(5,2) COMMENT '平时分',
  `midterm_score` DECIMAL(5,2) COMMENT '期中分',
  `final_score` DECIMAL(5,2) COMMENT '期末分',
  `practice_score` DECIMAL(5,2) COMMENT '实验/实践分',
  `total_score` DECIMAL(5,2) COMMENT '总评',
  `ranking` INT COMMENT '排名',
  `status` ENUM('normal', 'absent', 'deferred') DEFAULT 'normal' COMMENT '考试状态',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`record_id`) REFERENCES `grade_records`(`id`) ON DELETE CASCADE,
  INDEX `idx_item_record` (`record_id`),
  INDEX `idx_item_rank` (`record_id`, `ranking`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成绩明细表';

-- ============================================================
-- 19. course_ai_insights - 课程AI洞察表
-- 模型: app.models.timetable.CourseAIInsight
-- ============================================================
CREATE TABLE IF NOT EXISTS `course_ai_insights` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `course_id` INT NOT NULL UNIQUE COMMENT '关联courses表',
  `course_summary` TEXT COMMENT 'AI生成的课程概述',
  `learning_tips` JSON COMMENT '分点学习建议',
  `preview_suggestion` TEXT COMMENT '课前预习建议',
  `review_suggestion` TEXT COMMENT '课后复习建议',
  `key_points` JSON COMMENT '核心知识点',
  `related_courses` JSON COMMENT '关联课程',
  `difficulty_level` VARCHAR(10) COMMENT 'easy/medium/hard',
  `importance` VARCHAR(10) COMMENT 'low/medium/high',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程AI洞察表';

-- ============================================================
-- 20. course_reminders - 课程提醒表
-- 模型: app.models.timetable.CourseReminder
-- ============================================================
CREATE TABLE IF NOT EXISTS `course_reminders` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `course_id` INT NOT NULL COMMENT '关联courses表',
  `user_id` INT NOT NULL COMMENT '关联users表',
  `remind_type` VARCHAR(20) DEFAULT 'class' COMMENT 'class/exam/assignment',
  `remind_time` DATETIME NOT NULL COMMENT '提醒时间',
  `minutes_before` INT DEFAULT 15 COMMENT '提前分钟数',
  `message` VARCHAR(500) COMMENT '提醒消息',
  `is_sent` TINYINT(1) DEFAULT 0 COMMENT '是否已发送',
  `is_completed` TINYINT(1) DEFAULT 0 COMMENT '是否已完成',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_remind_time` (`user_id`, `remind_time`, `is_sent`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程提醒表';

-- ============================================================
-- 21. course_catalog - 课程目录表（选课助手用）
-- 模型: app.models.course_catalog.CourseCatalog
-- ============================================================
CREATE TABLE IF NOT EXISTS `course_catalog` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL COMMENT '课程名称',
  `code` VARCHAR(20) COMMENT '课程代码',
  `credit` DECIMAL(3,1) DEFAULT 3.0 COMMENT '学分',
  `category` VARCHAR(20) NOT NULL COMMENT '必修/选修/跨专业',
  `teacher` VARCHAR(50) COMMENT '授课教师',
  `day_of_week` INT NOT NULL COMMENT '周几1-7',
  `start_slot` INT NOT NULL COMMENT '开始节次1-12',
  `end_slot` INT NOT NULL COMMENT '结束节次1-12',
  `location` VARCHAR(100) COMMENT '上课地点',
  `capacity` INT DEFAULT 100 COMMENT '课程容量',
  `enrolled` INT DEFAULT 0 COMMENT '已选人数',
  `rating` DECIMAL(2,1) DEFAULT 4.5 COMMENT '课程评分',
  `semester` VARCHAR(20) NOT NULL COMMENT '学期（如2024-1）',
  `target_goals` JSON COMMENT '适用目标',
  `prerequisites` JSON COMMENT '先修课程ID列表',
  `alternatives` JSON COMMENT '替代课程ID列表',
  `tags` JSON COMMENT '标签',
  `description` TEXT COMMENT '课程描述',
  `difficulty` VARCHAR(10) DEFAULT 'medium' COMMENT 'easy/medium/hard',
  `is_active` INT DEFAULT 1 COMMENT '是否启用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  INDEX `idx_catalog_name` (`name`),
  INDEX `idx_catalog_code` (`code`),
  INDEX `idx_catalog_semester` (`semester`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程目录表';

-- ============================================================
-- 22. translation_tasks - 翻译任务表
-- 模型: app.models.translation.TranslationTask
-- ============================================================
CREATE TABLE IF NOT EXISTS `translation_tasks` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `task_id` VARCHAR(64) NOT NULL UNIQUE COMMENT '任务ID',
  `user_id` INT NOT NULL COMMENT '关联users',
  `task_type` VARCHAR(20) NOT NULL COMMENT 'text/document',
  `source_lang` VARCHAR(10) NOT NULL COMMENT '源语言',
  `target_lang` VARCHAR(10) NOT NULL COMMENT '目标语言',
  `original_content` TEXT COMMENT '即时翻译的原文',
  `original_file_url` VARCHAR(500) COMMENT '文档翻译的原文件URL',
  `translated_content` TEXT COMMENT '翻译结果',
  `word_count` INT DEFAULT 0 COMMENT '词数统计',
  `status` VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/processing/completed/failed',
  `error_message` TEXT COMMENT '错误信息',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_task_id` (`task_id`),
  INDEX `idx_trans_user` (`user_id`),
  INDEX `idx_trans_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='翻译任务表';

-- ============================================================
-- 23. course_advisor_selections - 选课记录表（课程顾问用）
-- 模型: app.models.course_advisor.CourseSelection (如存在)
-- 存储学生通过选课助手确认的选课方案
-- ============================================================
CREATE TABLE IF NOT EXISTS `course_advisor_selections` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL COMMENT '关联users',
  `semester` VARCHAR(20) NOT NULL COMMENT '学期',
  `selected_courses` JSON NOT NULL COMMENT '选中的课程ID列表',
  `reasoning` TEXT COMMENT 'AI推荐理由',
  `status` VARCHAR(20) DEFAULT 'draft' COMMENT 'draft/confirmed/submitted',
  `confirmed_at` DATETIME COMMENT '确认时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_selection_user` (`user_id`),
  INDEX `idx_selection_semester` (`semester`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='选课记录表';

-- ============================================================
-- 24. lesson_plans - 教案表（教师端用）
-- 辅助模型（前端有教案生成功能但没有专门的模型，预留此表）
-- ============================================================
CREATE TABLE IF NOT EXISTS `lesson_plans` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `teacher_id` INT NOT NULL COMMENT '教师用户ID',
  `title` VARCHAR(200) NOT NULL COMMENT '教案标题',
  `course_name` VARCHAR(100) COMMENT '课程名称',
  `semester` VARCHAR(50) COMMENT '学期',
  `theme` VARCHAR(50) COMMENT 'PPT主题',
  `outline` JSON COMMENT '教学大纲',
  `ppt_sid` VARCHAR(100) COMMENT 'PPT生成任务SID',
  `ppt_status` VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/processing/completed/failed',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`teacher_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_plan_teacher` (`teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教案表';


-- ============================================================
-- 初始化种子数据
-- ============================================================

-- -----------------------------------------------------------
-- 默认管理员账号
-- 密码: 123456
-- -----------------------------------------------------------
INSERT INTO `admins` (`username`, `password`, `nickname`, `role`) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4bFdKNKrC4AxqJGe', '超级管理员', 'super_admin')
ON DUPLICATE KEY UPDATE username = username;

-- -----------------------------------------------------------
-- 测试用户账号（密码统一为：123456）
-- -----------------------------------------------------------
INSERT INTO `users` (`openid`, `unionid`, `nickname`, `phone`, `password_hash`, `role`) VALUES
('test_openid_1', 'test_unionid_1', '张三', '13800138001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0l8lCLsKaC3qK', 'student'),
('test_openid_2', 'test_unionid_2', '李四', '13800138002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0l8lCLsKaC3qK', 'student'),
('test_openid_3', 'test_unionid_3', '王五', '13800138003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0l8lCLsKaC3qK', 'student'),
('teacher_openid_1', 'teacher_unionid_1', '张教授', '13900139001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0l8lCLsKaC3qK', 'teacher');

-- -----------------------------------------------------------
-- 学生画像
-- -----------------------------------------------------------
INSERT INTO `student_profiles` (`user_id`, `major`, `grade`, `class_name`, `goal`, `goal_detail`, `voice_prefer`, `emotion_mode`, `gpa`) VALUES
(1, '计算机科学与技术', 3, '计科3班', '就业', '希望毕业后能进入互联网大厂工作，目前正在准备秋招', 1, 'normal', 3.75),
(2, '金融学', 2, '金融2班', '考研', '计划报考经济学研究生，需要提升数学和专业课成绩', 1, 'normal', 3.45),
(3, '会计学', 4, '会计1班', '出国', '准备申请澳洲商科硕士，正在准备雅思考试', 0, 'emotion', 3.60);

-- -----------------------------------------------------------
-- 教师画像
-- -----------------------------------------------------------
INSERT INTO `teacher_profiles` (`user_id`, `department`, `office`, `title`) VALUES
(4, '经济管理学院', '行政楼302', '教授');

-- -----------------------------------------------------------
-- 课程数据
-- -----------------------------------------------------------
INSERT INTO `courses` (`user_id`, `name`, `code`, `credit`, `category`, `day_of_week`, `start_slot`, `end_slot`, `week_range`, `location`, `teacher`, `ai_tip`, `source`) VALUES
(1, '数据结构与算法', 'CS301', 4.0, '专业', 1, 1, 3, '1-16周', '7教201', '张教授', '这门课是考研必考，建议多做练习题', '手动'),
(1, '操作系统', 'CS302', 3.5, '专业', 2, 3, 5, '1-16周', '7教301', '李老师', '操作系统概念抽象，多画图理解', '手动'),
(1, '计算机网络', 'CS303', 3.0, '专业', 3, 1, 2, '1-16周', '7教102', '王教授', '协议分层结构是重点', '手动'),
(1, '软件工程', 'CS304', 2.5, '专业', 4, 4, 5, '1-16周', '7教401', '刘老师', '注重实践项目经验', '手动'),
(1, '人工智能导论', 'CS305', 2.0, '选修', 5, 2, 3, '1-16周', '7教202', '陈教授', '了解AI基本概念和发展趋势', '手动'),
(2, '微观经济学', 'EC201', 3.0, '专业', 1, 2, 4, '1-16周', '5教101', '周教授', '供需曲线分析是基础', '手动'),
(2, '货币银行学', 'EC202', 3.0, '专业', 2, 1, 2, '1-16周', '5教203', '吴老师', '关注利率和货币政策', '手动'),
(2, '高等数学', 'MA101', 4.0, '通识', 3, 3, 5, '1-16周', '1教301', '高教授', '微积分是考研数学重点', '手动'),
(2, '统计学', 'EC203', 3.0, '专业', 4, 1, 3, '1-16周', '5教105', '郑老师', '假设检验和回归分析', '手动'),
(2, '金融英语', 'EC204', 2.0, '选修', 5, 4, 5, '1-16周', '5教202', '外教Tom', '提升专业英语能力', '手动'),
(3, '财务会计', 'AC301', 4.0, '专业', 1, 3, 5, '1-16周', '4教101', '赵教授', '会计准则变化要关注', '手动'),
(3, '审计学', 'AC302', 3.0, '专业', 2, 4, 5, '1-16周', '4教203', '钱老师', '审计流程和风险评估', '手动'),
(3, '财务管理', 'AC303', 3.5, '专业', 3, 1, 3, '1-16周', '4教102', '孙教授', '资本结构决策是重点', '手动'),
(3, '税法', 'AC304', 3.0, '专业', 4, 2, 4, '1-16周', '4教301', '周老师', '最新税收政策要留意', '手动'),
(3, '职业规划与发展', 'GE101', 1.0, '通识', 5, 3, 4, '1-16周', '3教101', '就业指导中心', '为求职面试做准备', '手动');

-- -----------------------------------------------------------
-- 日程数据
-- -----------------------------------------------------------
INSERT INTO `schedules` (`user_id`, `event`, `event_type`, `day_of_week`, `time_desc`, `location`) VALUES
(1, '考研数学模拟考试', '考试', 6, '09:00-11:00', '7教101'),
(1, '秋招宣讲会-腾讯', '宣讲', 3, '19:00-21:00', '图书馆报告厅'),
(2, '导师组会', '会议', 5, '14:00-16:00', '5教会议室'),
(3, '雅思口语模拟', '考试', 6, '14:00-16:00', '外语学院');

-- -----------------------------------------------------------
-- 录音回顾 + 转写 + 总结数据
-- -----------------------------------------------------------
INSERT INTO `review_records` (`user_id`, `record_type`, `title`, `duration`, `language`, `status`) VALUES
(1, '课程', '数据结构与算法-图论部分', 3600, 'mandarin', 'completed'),
(1, '课程', '操作系统-进程与线程', 2700, 'mandarin', 'completed'),
(2, '课程', '微观经济学-市场结构', 3000, 'mandarin', 'completed'),
(3, '会议', '秋招简历指导', 1800, 'mandarin', 'completed');

INSERT INTO `transcriptions` (`record_id`, `raw_text`) VALUES
(1, '今天我们来讲图论部分。图是一种非常重要的数据结构...'),
(2, '进程是程序的一次执行，线程是CPU调度的基本单位...'),
(3, '这节课我们讨论四种市场结构：完全竞争、垄断竞争、寡头和垄断...'),
(4, '简历最重要的是突出项目经验和技能点...');

INSERT INTO `summaries` (`record_id`, `topic`, `key_points`, `difficulties`, `memorable_quote`, `next_suggestion`) VALUES
(1, '图论基础', '图的定义、遍历算法、最短路径', '迪杰斯特拉算法的正确性证明', '图是描述现实世界关系的有力工具', '预习网络流算法'),
(2, '进程与线程', '进程概念、线程概念、进程间通信', '死锁的条件和处理', '并发是现代计算的基础', '复习pv操作'),
(3, '市场结构分析', '四种市场结构特征、效率比较', '寡头市场的博弈分析', '市场结构影响企业定价策略', '做习题巩固'),
(4, '简历撰写技巧', 'STAR法则、项目描述技巧', '如何量化工作成果', '简历是求职的第一张名片', '完善个人项目展示');

-- -----------------------------------------------------------
-- FAQ知识库
-- -----------------------------------------------------------
INSERT INTO `knowledge_base` (`category`, `question`, `answer`, `source`) VALUES
('faq', '图书馆开放时间？', '周一至周五 8:00-22:00，周六周日 9:00-21:00，节假日另行通知。', '广州商学院官网'),
('faq', '如何申请调课？', '联系任课教师说明原因，填写调课申请表，由教务处审批。一般需要提前3个工作日申请。', '教务处'),
('faq', '9教是指哪栋楼？', '9教是9号教学楼，位于学校东门附近，主要用于经济管理学院教学，设施齐全。', '校园导航'),
('faq', '教务处在哪里？', '教务处位于行政楼3楼，电话：020-82876123，工作时间：周一至周五 8:30-17:30。', '校园导航'),
('faq', '如何办理成绩单？', '登录教务系统在线申请，或到教务处前台办理，需要学生证和身份证人工办理。', '教务处'),
('faq', '学校食堂有哪些？', '学校有第一食堂（靠近宿舍区）、第二食堂（靠近教学区）、清真食堂，满足不同口味需求。', '后勤服务'),
('faq', '如何申请奖学金？', '每学期末申请，包括学业奖学金、单项奖学金等。成绩排名前30%有机会，具体看辅导员通知。', '学生处'),
('faq', '体育馆开放时间？', '羽毛球馆：周一至周日 9:00-21:00；篮球场：全天开放；游泳馆：夏季 14:00-20:00。', '体育部'),
('faq', '如何预约自习室？', '可通过图书馆公众号预约，或到图书馆前台登记。期末周建议提前预约。', '图书馆'),
('faq', '学生卡丢了怎么办？', '第一时间到校园卡管理中心（行政楼1楼）挂失，可办理新卡。补卡费用20元。', '校园卡中心'),
('faq', '快递在哪里取？', '校内快递点：菜鸟驿站（近东门）、京东派（近南门），营业时间 9:00-21:00。', '后勤服务'),
('faq', '如何申请勤工俭学？', '登录学生事务系统申请，或关注学院发布的勤工俭学岗位信息，面试通过后即可上岗。', '学生处'),
('faq', '心理咨询中心在哪里？', '心理咨询中心位于学生活动中心2楼，需要提前电话预约：020-82876099。', '心理咨询中心'),
('faq', '如何参加社团活动？', '每学期初有社团招新（百团大战），也可通过学校团委公众号了解社团动态并报名。', '团委'),
('faq', '毕业需要修满多少学分？', '本科毕业一般需要修满160-180学分，具体视专业培养方案而定，请咨询辅导员。', '教务处');

-- ============================================================
-- 初始化完成
-- ============================================================
SELECT 'AI小商 数据库初始化完成 (v3.0)' AS status;
SELECT CONCAT('共创建 ', COUNT(*), ' 张表') AS table_count
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'ai_xiaoshang';
SELECT '默认管理员: admin / 123456' AS admin_account;
SELECT '测试用户密码均为: 123456' AS test_accounts;