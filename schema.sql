-- ============================================================
-- 小狗钱钱 App 建表脚本（远程数据库 mydb）
-- ============================================================

USE `mydb`;

-- 已有 user 表，新增 nickname 字段（如已存在会忽略）
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'mydb' AND TABLE_NAME = 'user' AND COLUMN_NAME = 'nickname');
SET @sql = IF(@col_exists = 0,
  'ALTER TABLE `user` ADD COLUMN `nickname` VARCHAR(64) NOT NULL DEFAULT \'\' COMMENT \'用户昵称\' AFTER `password`',
  'SELECT \'nickname column already exists\'');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 已有 user 表，新增 created_at 字段
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'mydb' AND TABLE_NAME = 'user' AND COLUMN_NAME = 'created_at');
SET @sql = IF(@col_exists = 0,
  'ALTER TABLE `user` ADD COLUMN `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT \'创建时间\'',
  'SELECT \'created_at column already exists\'');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 已有 user 表，新增 updated_at 字段
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'mydb' AND TABLE_NAME = 'user' AND COLUMN_NAME = 'updated_at');
SET @sql = IF(@col_exists = 0,
  'ALTER TABLE `user` ADD COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT \'更新时间\'',
  'SELECT \'updated_at column already exists\'');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. 成功日记表
CREATE TABLE IF NOT EXISTS `diaries` (
  `id`         INT          NOT NULL AUTO_INCREMENT COMMENT '日记ID',
  `user_id`    INT          NOT NULL                COMMENT '用户ID',
  `content`    TEXT         NOT NULL                COMMENT '日记内容',
  `date`       VARCHAR(10)  NOT NULL                COMMENT '日期 yyyy-MM-dd',
  `category`   VARCHAR(32)  NOT NULL DEFAULT 'daily' COMMENT '分类',
  `mood_icon`  VARCHAR(64)           DEFAULT NULL   COMMENT '心情图标',
  `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_date` (`user_id`, `date`),
  KEY `idx_user_category` (`user_id`, `category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成功日记表';

-- 4. 美德践行表
CREATE TABLE IF NOT EXISTS `virtue_logs` (
  `id`           INT           NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id`      INT           NOT NULL                COMMENT '用户ID',
  `virtue_type`  VARCHAR(32)   NOT NULL                COMMENT '美德类型',
  `completed`    TINYINT(1)    NOT NULL DEFAULT 1      COMMENT '是否已践行 0=否 1=是',
  `reflection`   VARCHAR(2000)          DEFAULT NULL   COMMENT '践行感想',
  `date`         VARCHAR(10)   NOT NULL                COMMENT '日期 yyyy-MM-dd',
  `created_at`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_date` (`user_id`, `date`),
  UNIQUE KEY `uk_user_virtue_date` (`user_id`, `virtue_type`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='美德践行表';

-- 5. 愿景板表
CREATE TABLE IF NOT EXISTS `vision_items` (
  `id`          INT          NOT NULL AUTO_INCREMENT COMMENT '愿景ID',
  `user_id`     INT          NOT NULL                COMMENT '用户ID',
  `category`    VARCHAR(32)  NOT NULL DEFAULT 'growth' COMMENT '分类',
  `title`       VARCHAR(128)          DEFAULT NULL   COMMENT '标题',
  `description` VARCHAR(512)          DEFAULT NULL   COMMENT '描述',
  `image_url`   VARCHAR(512)          DEFAULT NULL   COMMENT '图片URL',
  `target_date` VARCHAR(32)           DEFAULT NULL   COMMENT '目标日期',
  `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_user_category` (`user_id`, `category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='愿景板表';
