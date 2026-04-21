-- AI小商 - 课表扩展数据库脚本
-- MySQL 8.0
-- 运行: mysql -u root -p < timetable_extension.sql

USE ai_xiaoshang;

-- ============================================
-- 课程AI洞察表
-- ============================================
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
  `generated_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程AI洞察表';

-- ============================================
-- 课程提醒表
-- ============================================
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
  FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_remind_time` (`user_id`, `remind_time`, `is_sent`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程提醒表';