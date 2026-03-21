# 闪光时刻 (GlowMoment) — 后端 API 接口文档

> **版本**: v1.0  
> **Base URL**: `http://<host>:<port>`  
> **日期**: 2026-03-19  
> **说明**: 本文档涵盖"闪光时刻"App 所有前端功能所需的后端接口。前端使用 `Authorization: Bearer <token>` 进行鉴权，JSON 字段命名统一使用 **snake_case**。

---

## 目录

1. [通用约定](#1-通用约定)
2. [认证模块](#2-认证模块)
3. [成功日记模块](#3-成功日记模块)
4. [美德践行模块](#4-美德践行模块)
5. [愿景板模块](#5-愿景板模块)
6. [用户信息模块](#6-用户信息模块)
7. [枚举值参考](#7-枚举值参考)
8. [错误码参考](#8-错误码参考)

---

## 1. 通用约定

### 1.1 请求格式

| 项目 | 说明 |
|------|------|
| Content-Type | `application/json` |
| Accept | `application/json` |
| 鉴权 | 除登录/注册外，所有接口须携带 `Authorization: Bearer <token>` |
| 字段命名 | 请求体与响应体统一使用 **snake_case** |
| 日期格式 | `yyyy-MM-dd`（如 `2026-03-19`） |
| 分页 | 使用 `page`（从 1 开始）和 `page_size`（默认 20） |

### 1.2 统一响应包装

所有接口返回统一格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 业务状态码，200 表示成功 |
| message | string | 提示信息，失败时返回错误原因 |
| data | object / array / null | 业务数据，无数据时为 null |

### 1.3 错误响应示例

```json
{
  "code": 401,
  "message": "登录已过期，请重新登录",
  "data": null
}
```

---

## 2. 认证模块

> 前缀: `/api/auth`

### 2.1 用户注册

**已对接** — 前端当前使用中。

```
POST /api/auth/regist
```

**请求体:**

```json
{
  "username": "string, 必填, 用户名",
  "password": "string, 必填, 密码(≥6位)",
  "header":   "string, 可选, 头像URL"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "header": ""
  }
}
```

**失败响应:**

```json
{
  "code": 400,
  "message": "用户名已存在",
  "data": null
}
```

---

### 2.2 用户登录

**已对接** — 前端当前使用中。

```
POST /api/auth/login
```

**请求体:**

```json
{
  "username": "string, 必填",
  "password": "string, 必填"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "zhangsan",
      "header": "https://example.com/avatar.png"
    }
  }
}
```

**失败响应:**

```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "data": null
}
```

---

### 2.3 发送短信验证码

**待对接** — 前端代码已写好，后端需实现。

```
POST /api/auth/sms/send
```

**请求体:**

```json
{
  "phone": "string, 必填, 手机号"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": null
}
```

---

### 2.4 短信验证码登录

**待对接** — 前端代码已写好，后端需实现。

```
POST /api/auth/login/sms
```

**请求体:**

```json
{
  "phone": "string, 必填",
  "code":  "string, 必填, 短信验证码"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "zhangsan",
      "header": ""
    }
  }
}
```

> **注**: 前端旧代码期望返回 `{ "token": "...", "phone": "..." }`，建议统一使用新的包装格式。

---

### 2.5 重置密码

**待对接** — 前端代码已写好，后端需实现。

```
POST /api/auth/password/reset
```

**请求体:**

```json
{
  "phone":        "string, 必填",
  "code":         "string, 必填, 短信验证码",
  "new_password": "string, 必填, 新密码(≥6位)"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "密码重置成功",
  "data": null
}
```

---

## 3. 成功日记模块

> 前缀: `/api/diary`  
> 鉴权: 所有接口需要 Bearer Token

### 3.1 数据模型: DiaryEntry

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识，后端生成 |
| date | string | 日期 `yyyy-MM-dd` |
| content | string | 日记内容（5~500字符） |
| category | string | 分类枚举，见[枚举值](#71-日记--愿景分类-diarycategorydata) |
| mood_icon | string | 心情图标名称，见[枚举值](#73-心情图标-moodicon) |
| created_at | string | 创建时间 ISO8601（可选，前端暂不展示） |
| updated_at | string | 更新时间 ISO8601（可选，前端暂不展示） |

---

### 3.2 获取日记列表

```
GET /api/diary/entries
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 按日期筛选 `yyyy-MM-dd` |
| category | string | 否 | 按分类筛选 `WORK` / `HEALTH` / ... |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页条数，默认 20 |

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 42,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": "d-uuid-001",
        "date": "2026-03-19",
        "content": "早起给自己做了一顿丰盛的早餐。",
        "category": "DAILY",
        "mood_icon": "Sun"
      }
    ]
  }
}
```

---

### 3.3 获取单条日记

```
GET /api/diary/entries/{id}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "d-uuid-001",
    "date": "2026-03-19",
    "content": "早起给自己做了一顿丰盛的早餐。",
    "category": "DAILY",
    "mood_icon": "Sun"
  }
}
```

---

### 3.4 创建日记

```
POST /api/diary/entries
```

**请求体:**

```json
{
  "date":      "2026-03-19",
  "content":   "早起给自己做了一顿丰盛的早餐。",
  "category":  "DAILY",
  "mood_icon": "Sun"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": "d-uuid-001",
    "date": "2026-03-19",
    "content": "早起给自己做了一顿丰盛的早餐。",
    "category": "DAILY",
    "mood_icon": "Sun"
  }
}
```

---

### 3.5 更新日记

```
PUT /api/diary/entries/{id}
```

**请求体:**

```json
{
  "date":      "2026-03-19",
  "content":   "更新后的日记内容",
  "category":  "GROWTH",
  "mood_icon": "Zap"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": "d-uuid-001",
    "date": "2026-03-19",
    "content": "更新后的日记内容",
    "category": "GROWTH",
    "mood_icon": "Zap"
  }
}
```

---

### 3.6 删除日记

```
DELETE /api/diary/entries/{id}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 3.7 获取日记统计

```
GET /api/diary/stats
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | 否 | 统计起始日期 |
| end_date | string | 否 | 统计结束日期 |
| category | string | 否 | 按分类统计 |

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_count": 42,
    "this_week_count": 5,
    "top_category": "DAILY",
    "streak_days": 7,
    "category_distribution": [
      { "category": "DAILY",        "count": 15, "label": "日常微光" },
      { "category": "WORK",         "count": 10, "label": "职业成就" },
      { "category": "GROWTH",       "count": 8,  "label": "个人成长" },
      { "category": "HEALTH",       "count": 5,  "label": "身体健康" },
      { "category": "RELATIONSHIP", "count": 4,  "label": "人际关系" }
    ]
  }
}
```

---

### 3.8 获取日历有记录日期

用于日历页标记哪些天有记录（小狗贴纸）。

```
GET /api/diary/calendar
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| year | int | 是 | 年份 |
| month | int | 是 | 月份 (1-12) |

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "year": 2026,
    "month": 3,
    "recorded_dates": ["2026-03-01", "2026-03-05", "2026-03-19"]
  }
}
```

---

### 3.9 获取高光时刻（首页用）

首页展示最近的成功日记高光。

```
GET /api/diary/highlights
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | 否 | 返回条数，默认 3 |

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "d-uuid-001",
      "date": "2026-03-19",
      "display_date": "今天",
      "content": "早起给自己做了一顿丰盛的早餐。",
      "category": "DAILY",
      "category_label": "日常微光",
      "category_color": "#FFF2D1",
      "mood_icon": "Sun"
    }
  ]
}
```

---

## 4. 美德践行模块

> 前缀: `/api/virtue`  
> 鉴权: 所有接口需要 Bearer Token

### 4.1 数据模型: VirtueDefinition

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识 |
| type | string | 美德类型枚举，见[枚举值](#72-美德类型-virtuetypedata) |
| name | string | 中文名称 |
| quote | string | 名言金句 |
| guidelines | string[] | 践行指南列表 |
| icon_name | string | 图标名称 |

### 4.2 数据模型: VirtuePracticeLog

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识，后端生成 |
| date | string | 日期 `yyyy-MM-dd` |
| virtue_type | string | 美德类型枚举 |
| is_completed | bool | 是否已完成践行 |
| reflection | string | 践行感悟（可为空） |

---

### 4.3 获取所有美德定义

```
GET /api/virtue/definitions
```

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "virtue-friendly",
      "type": "FRIENDLY",
      "name": "友好亲和",
      "quote": "最美好的事情莫过于温和待人。",
      "guidelines": [
        "祝愿他人生活幸福",
        "不伤害他人，不介入纷争",
        "谦虚尊重他人，我不必永远正确"
      ],
      "icon_name": "Smile"
    }
  ]
}
```

---

### 4.4 获取今日美德

根据日期返回当日应践行的美德（按天轮换）。

```
GET /api/virtue/today
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期，默认今天 |

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "definition": {
      "id": "virtue-friendly",
      "type": "FRIENDLY",
      "name": "友好亲和",
      "quote": "最美好的事情莫过于温和待人。",
      "guidelines": ["祝愿他人生活幸福", "..."],
      "icon_name": "Smile"
    },
    "practice_log": {
      "id": "log-2026-03-19-FRIENDLY",
      "date": "2026-03-19",
      "virtue_type": "FRIENDLY",
      "is_completed": false,
      "reflection": ""
    }
  }
}
```

---

### 4.5 获取践行记录列表

```
GET /api/virtue/logs
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 按日期筛选 |
| virtue_type | string | 否 | 按美德类型筛选 |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页条数，默认 20 |

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 30,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": "log-uuid-001",
        "date": "2026-03-19",
        "virtue_type": "FRIENDLY",
        "is_completed": true,
        "reflection": "今天也有意识地践行了「友好亲和」，从小事做起。"
      }
    ]
  }
}
```

---

### 4.6 提交/更新践行记录

```
POST /api/virtue/logs
```

**请求体:**

```json
{
  "date":         "2026-03-19",
  "virtue_type":  "FRIENDLY",
  "is_completed": true,
  "reflection":   "今天微笑面对每个人，感觉很好。"
}
```

> 同一天同一美德类型的记录做 upsert（存在则更新，不存在则创建）。

**成功响应:**

```json
{
  "code": 200,
  "message": "保存成功",
  "data": {
    "id": "log-uuid-001",
    "date": "2026-03-19",
    "virtue_type": "FRIENDLY",
    "is_completed": true,
    "reflection": "今天微笑面对每个人，感觉很好。"
  }
}
```

---

### 4.7 获取美德成长统计

```
GET /api/virtue/stats
```

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_practices": 30,
    "virtues_covered": 5,
    "streak_days": 7,
    "type_distribution": [
      { "virtue_type": "FRIENDLY",    "count": 8, "name": "友好亲和" },
      { "virtue_type": "RESPONSIBLE", "count": 6, "name": "勇于承担" },
      { "virtue_type": "KIND",        "count": 5, "name": "善待他人" },
      { "virtue_type": "HELPFUL",     "count": 4, "name": "帮助给予" },
      { "virtue_type": "GRATEFUL",    "count": 3, "name": "感恩之心" },
      { "virtue_type": "LEARNING",    "count": 2, "name": "勤学不辍" },
      { "virtue_type": "RELIABLE",    "count": 2, "name": "值得信赖" }
    ]
  }
}
```

---

## 5. 愿景板模块

> 前缀: `/api/vision`  
> 鉴权: 所有接口需要 Bearer Token

### 5.1 数据模型: VisionItem

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识，后端生成 |
| category | string | 分类枚举，见[枚举值](#71-日记--愿景分类-diarycategorydata) |
| title | string | 愿景标题 |
| description | string | 愿景描述 |
| image_url | string | 图片 URL |
| target_date | string | 目标日期 `yyyy-MM-dd`（可为空） |

---

### 5.2 获取愿景列表

```
GET /api/vision/items
```

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 按分类筛选 |

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "v-uuid-001",
      "category": "WORK",
      "title": "成为更好的自己",
      "description": "在职业上持续精进，做有价值的事。",
      "image_url": "https://example.com/image.png",
      "target_date": "2026-12-31"
    }
  ]
}
```

---

### 5.3 获取单个愿景

```
GET /api/vision/items/{id}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "v-uuid-001",
    "category": "WORK",
    "title": "成为更好的自己",
    "description": "在职业上持续精进，做有价值的事。",
    "image_url": "https://example.com/image.png",
    "target_date": "2026-12-31"
  }
}
```

---

### 5.4 创建愿景

```
POST /api/vision/items
```

**请求体:**

```json
{
  "category":    "WORK",
  "title":       "成为更好的自己",
  "description": "在职业上持续精进，做有价值的事。",
  "image_url":   "https://example.com/image.png",
  "target_date": "2026-12-31"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": "v-uuid-001",
    "category": "WORK",
    "title": "成为更好的自己",
    "description": "在职业上持续精进，做有价值的事。",
    "image_url": "https://example.com/image.png",
    "target_date": "2026-12-31"
  }
}
```

---

### 5.5 更新愿景

```
PUT /api/vision/items/{id}
```

**请求体:**

```json
{
  "category":    "GROWTH",
  "title":       "更新后的标题",
  "description": "更新后的描述",
  "image_url":   "https://example.com/new-image.png",
  "target_date": "2027-06-30"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": "v-uuid-001",
    "category": "GROWTH",
    "title": "更新后的标题",
    "description": "更新后的描述",
    "image_url": "https://example.com/new-image.png",
    "target_date": "2027-06-30"
  }
}
```

---

### 5.6 删除愿景

```
DELETE /api/vision/items/{id}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 5.7 上传图片

愿景编辑器支持从相册选图，需要图片上传接口。

```
POST /api/upload/image
```

**请求格式**: `multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| file | binary | 图片文件 (JPEG/PNG)，建议限制 5MB |
| type | string | 用途标识: `vision` / `avatar` |

**成功响应:**

```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "url": "https://cdn.example.com/uploads/2026/03/image-uuid.png"
  }
}
```

---

## 6. 用户信息模块

> 前缀: `/api/user`  
> 鉴权: 所有接口需要 Bearer Token

### 6.1 获取当前用户信息

```
GET /api/user/profile
```

**成功响应:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "header": "https://example.com/avatar.png"
  }
}
```

---

### 6.2 更新用户信息

```
PUT /api/user/profile
```

**请求体:**

```json
{
  "username": "zhangsan_new",
  "header":   "https://example.com/new-avatar.png"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "username": "zhangsan_new",
    "header": "https://example.com/new-avatar.png"
  }
}
```

---

### 6.3 修改密码

```
POST /api/user/change-password
```

**请求体:**

```json
{
  "old_password": "string, 必填",
  "new_password": "string, 必填, ≥6位"
}
```

**成功响应:**

```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

---

## 7. 枚举值参考

### 7.1 日记 / 愿景分类 (DiaryCategoryData)

| 值 | 中文名称 | 说明 |
|----|----------|------|
| `WORK` | 职业成就 | 工作与职业相关 |
| `HEALTH` | 身体健康 | 运动、饮食、睡眠 |
| `RELATIONSHIP` | 人际关系 | 家人、朋友、社交 |
| `GROWTH` | 个人成长 | 学习、阅读、技能 |
| `DAILY` | 日常微光 | 生活中的小确幸 |

### 7.2 美德类型 (VirtueTypeData)

| 值 | 中文名称 | 图标 |
|----|----------|------|
| `FRIENDLY` | 友好亲和 | Smile |
| `RESPONSIBLE` | 勇于承担 | ShieldCheck |
| `KIND` | 善待他人 | HeartHandshake |
| `HELPFUL` | 帮助给予 | HandHelping |
| `GRATEFUL` | 感恩之心 | Grape |
| `LEARNING` | 勤学不辍 | BookOpen |
| `RELIABLE` | 值得信赖 | Award |

### 7.3 心情图标 (MoodIcon)

日记条目关联的心情图标名称（前端使用 Lucide 图标库）:

| 值 | 说明 |
|----|------|
| `Sun` | 阳光、日常 |
| `Zap` | 活力、能量 |
| `Activity` | 运动、活跃 |
| `MessageSquareHeart` | 交流、关爱 |
| `Heart` | 心爱、温暖 |
| `Star` | 优秀、闪亮 |
| `BookOpen` | 阅读、学习 |
| `Briefcase` | 工作 |
| `Users` | 人际 |

---

## 8. 错误码参考

| HTTP 状态码 | 业务 code | 说明 |
|-------------|-----------|------|
| 200 | 200 | 成功 |
| 400 | 400 | 请求参数错误（字段缺失、格式不对） |
| 401 | 401 | 未登录 / Token 过期 |
| 403 | 403 | 无权限 |
| 404 | 404 | 资源不存在 |
| 409 | 409 | 冲突（如用户名已存在） |
| 500 | 500 | 服务器内部错误 |

---

## 附录: 接口清单总览

| # | 方法 | 路径 | 说明 | 状态 |
|---|------|------|------|------|
| 1 | POST | `/api/auth/regist` | 用户注册 | **已对接** |
| 2 | POST | `/api/auth/login` | 用户名密码登录 | **已对接** |
| 3 | POST | `/api/auth/sms/send` | 发送短信验证码 | 待对接 |
| 4 | POST | `/api/auth/login/sms` | 短信验证码登录 | 待对接 |
| 5 | POST | `/api/auth/password/reset` | 重置密码 | 待对接 |
| 6 | GET | `/api/diary/entries` | 获取日记列表 | **待开发** |
| 7 | GET | `/api/diary/entries/{id}` | 获取单条日记 | **待开发** |
| 8 | POST | `/api/diary/entries` | 创建日记 | **待开发** |
| 9 | PUT | `/api/diary/entries/{id}` | 更新日记 | **待开发** |
| 10 | DELETE | `/api/diary/entries/{id}` | 删除日记 | **待开发** |
| 11 | GET | `/api/diary/stats` | 日记统计 | **待开发** |
| 12 | GET | `/api/diary/calendar` | 日历记录日期 | **待开发** |
| 13 | GET | `/api/diary/highlights` | 首页高光时刻 | **待开发** |
| 14 | GET | `/api/virtue/definitions` | 美德定义列表 | **待开发** |
| 15 | GET | `/api/virtue/today` | 今日美德 | **待开发** |
| 16 | GET | `/api/virtue/logs` | 践行记录列表 | **待开发** |
| 17 | POST | `/api/virtue/logs` | 提交践行记录 | **待开发** |
| 18 | GET | `/api/virtue/stats` | 美德成长统计 | **待开发** |
| 19 | GET | `/api/vision/items` | 愿景列表 | **待开发** |
| 20 | GET | `/api/vision/items/{id}` | 获取单个愿景 | **待开发** |
| 21 | POST | `/api/vision/items` | 创建愿景 | **待开发** |
| 22 | PUT | `/api/vision/items/{id}` | 更新愿景 | **待开发** |
| 23 | DELETE | `/api/vision/items/{id}` | 删除愿景 | **待开发** |
| 24 | POST | `/api/upload/image` | 图片上传 | **待开发** |
| 25 | GET | `/api/user/profile` | 获取用户信息 | **待开发** |
| 26 | PUT | `/api/user/profile` | 更新用户信息 | **待开发** |
| 27 | POST | `/api/user/change-password` | 修改密码 | **待开发** |

---

## 数据库表建议

### users
```sql
CREATE TABLE users (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL COMMENT '加密存储',
    header      VARCHAR(500) DEFAULT '' COMMENT '头像URL',
    phone       VARCHAR(20)  DEFAULT '' COMMENT '手机号',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### diary_entries
```sql
CREATE TABLE diary_entries (
    id          VARCHAR(50)  PRIMARY KEY,
    user_id     BIGINT       NOT NULL,
    date        DATE         NOT NULL,
    content     TEXT         NOT NULL,
    category    VARCHAR(20)  NOT NULL COMMENT 'WORK/HEALTH/RELATIONSHIP/GROWTH/DAILY',
    mood_icon   VARCHAR(50)  NOT NULL DEFAULT 'Sun',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_date (user_id, date)
);
```

### virtue_practice_logs
```sql
CREATE TABLE virtue_practice_logs (
    id           VARCHAR(50)  PRIMARY KEY,
    user_id      BIGINT       NOT NULL,
    date         DATE         NOT NULL,
    virtue_type  VARCHAR(20)  NOT NULL COMMENT 'FRIENDLY/RESPONSIBLE/KIND/...',
    is_completed TINYINT(1)   NOT NULL DEFAULT 0,
    reflection   TEXT         DEFAULT '',
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_date_type (user_id, date, virtue_type)
);
```

### vision_items
```sql
CREATE TABLE vision_items (
    id          VARCHAR(50)  PRIMARY KEY,
    user_id     BIGINT       NOT NULL,
    category    VARCHAR(20)  NOT NULL COMMENT 'WORK/HEALTH/RELATIONSHIP/GROWTH/DAILY',
    title       VARCHAR(200) NOT NULL,
    description TEXT         DEFAULT '',
    image_url   VARCHAR(500) DEFAULT '',
    target_date DATE         DEFAULT NULL,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_category (user_id, category)
);
```
