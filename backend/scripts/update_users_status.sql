-- 为users表添加status和disable_reason字段
-- 修改时间：2026-05-09

-- 添加status字段（如果不存在）
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active' COMMENT '账号状态：active=正常，disabled=禁用';

-- 添加disable_reason字段（如果不存在）
ALTER TABLE users ADD COLUMN disable_reason TEXT COMMENT '禁用原因';

-- 更新现有用户为active状态
UPDATE users SET status = 'active' WHERE status IS NULL OR status = '';

-- 更新admin_logs的action_text
UPDATE admin_logs SET action_text = '禁用用户' WHERE action = 'user.disable';
UPDATE admin_logs SET action_text = '启用用户' WHERE action = 'user.enable';