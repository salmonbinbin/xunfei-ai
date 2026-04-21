-- AI小商 - 数据库初始化脚本
-- MySQL 8.0
-- 运行: mysql -u root -p < init_db.sql

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ai_xiaoshang
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE ai_xiaoshang;

-- ============================================
-- 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `openid` VARCHAR(64) COMMENT '微信openid',
  `unionid` VARCHAR(64) COMMENT '微信unionid',
  `nickname` VARCHAR(64) COMMENT '昵称',
  `phone` VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号（登录账号）',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码hash',
  `avatar_url` VARCHAR(500) COMMENT '头像URL',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '账号状态',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login` DATETIME COMMENT '最后登录',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  INDEX `idx_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 学生画像表
-- ============================================
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

-- ============================================
-- 课程表
-- ============================================
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
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_day` (`user_id`, `day_of_week`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- ============================================
-- 日程表
-- ============================================
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

-- ============================================
-- 录音回顾记录
-- ============================================
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

-- ============================================
-- 转写结果
-- ============================================
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

-- ============================================
-- 总结结果
-- ============================================
CREATE TABLE IF NOT EXISTS `summaries` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `record_id` INT NOT NULL UNIQUE COMMENT '关联review_records',
  `topic` VARCHAR(200) COMMENT '主题',
  `key_points` TEXT COMMENT '核心知识点',
  `difficulties` TEXT COMMENT '重点难点',
  `memorable_quote` VARCHAR(500) COMMENT '金句',
  `next_suggestion` TEXT COMMENT '预习建议',
  `full_text` TEXT COMMENT '完整总结',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  FOREIGN KEY (`record_id`) REFERENCES `review_records`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='总结结果';

-- ============================================
-- 对话会话
-- ============================================
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

-- ============================================
-- 消息记录
-- ============================================
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

-- ============================================
-- 知识库
-- ============================================
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

-- ============================================
-- 管理员
-- ============================================
CREATE TABLE IF NOT EXISTS `admin_users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
  `password_hash` VARCHAR(255) COMMENT '密码',
  `role` VARCHAR(20) DEFAULT 'admin' COMMENT '角色',
  `nickname` VARCHAR(50) COMMENT '昵称',
  `last_login` DATETIME COMMENT '最后登录',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '有效',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  INDEX `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';

-- ============================================
-- 初始化测试用户数据
-- 密码统一为：123456
-- bcrypt hash for "123456": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0l8lCLsKaC3qK
-- ============================================
INSERT INTO `users` (`openid`, `unionid`, `nickname`, `phone`, `password_hash`, `avatar_url`, `is_active`) VALUES
('test_openid_1', 'test_unionid_1', '张三', '13800138001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0l8lCLsKaC3qK', 'https://example.com/avatar1.jpg', 1),
('test_openid_2', 'test_unionid_2', '李四', '13800138002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0l8lCLsKaC3qK', 'https://example.com/avatar2.jpg', 1),
('test_openid_3', 'test_unionid_3', '王五', '13800138003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S0l8lCLsKaC3qK', 'https://example.com/avatar3.jpg', 1);

-- ============================================
-- 初始化学生画像数据
-- ============================================
INSERT INTO `student_profiles` (`user_id`, `major`, `grade`, `class_name`, `goal`, `goal_detail`, `voice_prefer`, `emotion_mode`, `gpa`) VALUES
(1, '计算机科学与技术', 3, '计科3班', '就业', '希望毕业后能进入互联网大厂工作，目前正在准备秋招', 1, 'normal', 3.75),
(2, '金融学', 2, '金融2班', '考研', '计划报考经济学研究生，需要提升数学和专业课成绩', 1, 'normal', 3.45),
(3, '会计学', 4, '会计1班', '出国', '准备申请澳洲商科硕士，正在准备雅思考试', 0, 'emotion', 3.60);

-- ============================================
-- 初始化课程数据（每个用户5门课程，覆盖周一到周五）
-- ============================================
-- 用户1的课程（计算机专业大三）
INSERT INTO `courses` (`user_id`, `name`, `code`, `credit`, `category`, `day_of_week`, `start_slot`, `end_slot`, `week_range`, `location`, `teacher`, `ai_tip`) VALUES
(1, '数据结构与算法', 'CS301', 4.0, '专业', 1, 1, 3, '1-16周', '7教201', '张教授', '这门课是考研必考，建议多做练习题'),
(1, '操作系统', 'CS302', 3.5, '专业', 2, 3, 5, '1-16周', '7教301', '李老师', '操作系统概念抽象，多画图理解'),
(1, '计算机网络', 'CS303', 3.0, '专业', 3, 1, 2, '1-16周', '7教102', '王教授', '协议分层结构是重点'),
(1, '软件工程', 'CS304', 2.5, '专业', 4, 4, 5, '1-16周', '7教401', '刘老师', '注重实践项目经验'),
(1, '人工智能导论', 'CS305', 2.0, '选修', 5, 2, 3, '1-16周', '7教202', '陈教授', '了解AI基本概念和发展趋势');

-- 用户2的课程（金融专业大二）
INSERT INTO `courses` (`user_id`, `name`, `code`, `credit`, `category`, `day_of_week`, `start_slot`, `end_slot`, `week_range`, `location`, `teacher`, `ai_tip`) VALUES
(2, '微观经济学', 'EC201', 3.0, '专业', 1, 2, 4, '1-16周', '5教101', '周教授', '供需曲线分析是基础'),
(2, '货币银行学', 'EC202', 3.0, '专业', 2, 1, 2, '1-16周', '5教203', '吴老师', '关注利率和货币政策'),
(2, '高等数学', 'MA101', 4.0, '通识', 3, 3, 5, '1-16周', '1教301', '高教授', '微积分是考研数学重点'),
(2, '统计学', 'EC203', 3.0, '专业', 4, 1, 3, '1-16周', '5教105', '郑老师', '假设检验和回归分析'),
(2, '金融英语', 'EC204', 2.0, '选修', 5, 4, 5, '1-16周', '5教202', '外教Tom', '提升专业英语能力');

-- 用户3的课程（会计专业大四）
INSERT INTO `courses` (`user_id`, `name`, `code`, `credit`, `category`, `day_of_week`, `start_slot`, `end_slot`, `week_range`, `location`, `teacher`, `ai_tip`) VALUES
(3, '财务会计', 'AC301', 4.0, '专业', 1, 3, 5, '1-16周', '4教101', '赵教授', '会计准则变化要关注'),
(3, '审计学', 'AC302', 3.0, '专业', 2, 4, 5, '1-16周', '4教203', '钱老师', '审计流程和风险评估'),
(3, '财务管理', 'AC303', 3.5, '专业', 3, 1, 3, '1-16周', '4教102', '孙教授', '资本结构决策是重点'),
(3, '税法', 'AC304', 3.0, '专业', 4, 2, 4, '1-16周', '4教301', '周老师', '最新税收政策要留意'),
(3, '职业规划与发展', 'GE101', 1.0, '通识', 5, 3, 4, '1-16周', '3教101', '就业指导中心', '为求职面试做准备');

-- ============================================
-- 初始化日程数据
-- ============================================
INSERT INTO `schedules` (`user_id`, `event`, `event_type`, `day_of_week`, `time_desc`, `location`) VALUES
(1, '考研数学模拟考试', '考试', 6, '09:00-11:00', '7教101'),
(1, '秋招宣讲会-腾讯', '宣讲', 3, '19:00-21:00', '图书馆报告厅'),
(2, '导师组会', '会议', 5, '14:00-16:00', '5教会议室'),
(3, '雅思口语模拟', '考试', 6, '14:00-16:00', '外语学院');

-- ============================================
-- 初始化录音回顾记录
-- ============================================
INSERT INTO `review_records` (`user_id`, `record_type`, `title`, `duration`, `language`, `status`) VALUES
(1, '课程', '数据结构与算法-图论部分', 3600, 'mandarin', 'completed'),
(1, '课程', '操作系统-进程与线程', 2700, 'mandarin', 'completed'),
(2, '课程', '微观经济学-市场结构', 3000, 'mandarin', 'completed'),
(3, '会议', '秋招简历指导', 1800, 'mandarin', 'completed');

-- ============================================
-- 初始化转写结果
-- ============================================
INSERT INTO `transcriptions` (`record_id`, `raw_text`) VALUES
(1, '今天我们来讲图论部分。图是一种非常重要的数据结构...'),
(2, '进程是程序的一次执行，线程是CPU调度的基本单位...'),
(3, '这节课我们讨论四种市场结构：完全竞争、垄断竞争、寡头和垄断...'),
(4, '简历最重要的是突出项目经验和技能点...');

-- ============================================
-- 初始化总结结果
-- ============================================
INSERT INTO `summaries` (`record_id`, `topic`, `key_points`, `difficulties`, `memorable_quote`, `next_suggestion`) VALUES
(1, '图论基础', '图的定义、遍历算法、最短路径', '迪杰斯特拉算法的正确性证明', '图是描述现实世界关系的有力工具', '预习网络流算法'),
(2, '进程与线程', '进程概念、线程概念、进程间通信', '死锁的条件和处理', '并发是现代计算的基础', '复习pv操作'),
(3, '市场结构分析', '四种市场结构特征、效率比较', '寡头市场的博弈分析', '市场结构影响企业定价策略', '做习题巩固'),
(4, '简历撰写技巧', 'STAR法则、项目描述技巧', '如何量化工作成果', '简历是求职的第一张名片', '完善个人项目展示');

-- ============================================
-- 初始化对话会话
-- ============================================
INSERT INTO `conversations` (`user_id`, `title`, `category`, `mode`, `message_count`) VALUES
(1, '数据结构学习咨询', 'study', 'normal', 5),
(1, '秋招求职指导', 'career', 'emotion', 8),
(2, '考研数学规划', 'study', 'normal', 3),
(3, '留学申请咨询', 'life', 'emotion', 6);

-- ============================================
-- 初始化消息记录
-- ============================================
INSERT INTO `messages` (`conv_id`, `role`, `content_type`, `content`, `sentiment`, `tokens_used`, `latency_ms`) VALUES
(1, 'user', 'text', '图论中迪杰斯特拉算法求最短路径的时间复杂度是多少？', 'neutral', 50, 230),
(1, 'assistant', 'text', '迪杰斯特拉算法的时间复杂度是O(V²)，如果使用优先级队列优化可以降到O(E log V)。', 'neutral', 120, 450),
(1, 'user', 'text', '那如果边权有负数呢？', 'neutral', 30, 180),
(1, 'assistant', 'text', '如果边权有负数，迪杰斯特拉算法就不适用了，需要使用Bellman-Ford算法。', 'neutral', 100, 380),
(1, 'user', 'voice', NULL, 'positive', 80, 520),
(2, 'user', 'text', '秋招应该什么时候开始准备？', 'anxious', 40, 200),
(2, 'assistant', 'text', '秋招一般从7月开始，建议提前1-2个月准备简历和刷题。保持好心态很重要！', 'empathetic', 150, 600),
(2, 'user', 'text', '我是计算机专业的，现在gap大吗？', 'worried', 35, 190),
(2, 'assistant', 'text', '计算机专业需求依然旺盛，但竞争也更加激烈。建议突出项目经验和算法能力。', 'encouraging', 180, 550),
(3, 'user', 'text', '考研数学怎么规划复习？', 'neutral', 45, 220),
(3, 'assistant', 'text', '建议分三轮复习：基础阶段过教材、强化阶段刷题、冲刺阶段做真题和模拟。', 'neutral', 130, 420),
(4, 'user', 'text', '申请澳洲商科硕士需要准备什么？', 'neutral', 50, 240),
(4, 'assistant', 'text', '需要准备：本科成绩单、雅思成绩、个人陈述、推荐信。商科一般需要GMAT。', 'neutral', 160, 480),
(4, 'user', 'text', '雅思要考到多少分？', 'neutral', 25, 150),
(4, 'assistant', 'text', '澳洲商科硕士一般要求雅思6.5（单项不低于6），部分名校要求7分。', 'neutral', 90, 350),
(4, 'user', 'text', '感谢学姐指导！', 'happy', 20, 120),
(4, 'assistant', 'text', '不客气！祝申请顺利，有问题随时来问。加油！', 'warm', 60, 280);

-- ============================================
-- 初始化FAQ知识库（10条以上关于广州商学院）
-- ============================================
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

-- ============================================
-- 初始化管理员账号
-- ============================================
-- 密码: admin123 (bcrypt hash)
INSERT INTO `admin_users` (`username`, `password_hash`, `role`, `nickname`) VALUES
('admin', '$2b$12$o7zXS6UrIBcO5.rP5gOVXeoIFmjkgCuYjA3O1XHPD8EBhnYdzQXPa', 'super_admin', '系统管理员');
