# 后端API端点列表

以下是后端实际实现的API端点列表，前端应使用这些端点与后端交互：

## 1. 用户相关 API

### 认证相关
- **用户注册**：`POST /api/users/register`
  - 请求体：`{"openid": "string", "nickname": "string", "avatar": "string", "gender": number}`
  - 响应：用户信息和访问令牌

- **用户登录**：`POST /api/users/login`
  - 请求体：`{"openid": "string"}`
  - 响应：用户信息和访问令牌

- **退出登录**：后端无专门的logout端点，前端只需删除本地存储的token即可

### 用户信息
- **获取当前用户信息**：`GET /api/users/me`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 响应：当前登录用户的详细信息

- **更新当前用户信息**：`PUT /api/users/me`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 请求体：`{"nickname": "string", "avatar": "string", "gender": number, "phone": "string", "bio": "string", "singing_style": "string"}`
  - 响应：更新后的用户信息

- **获取指定用户信息**：`GET /api/users/{user_id}`
  - 响应：指定用户的详细信息

### 商家申请
- **申请成为商家**：`POST /api/users/apply-merchant`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 响应：申请提交成功消息

- **获取商家申请列表**（管理员）：`GET /api/users/merchant-applications`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 需管理员权限
  - 响应：所有待审核的商家申请

- **审核商家申请**（管理员）：`PUT /api/users/merchant-applications/{user_id}`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 需管理员权限
  - 请求体：`{"status": "approved/rejected"}`
  - 响应：审核结果消息

## 2. 活动相关 API

### 活动管理
- **获取活动列表**：`GET /api/activities/`
  - 支持分页和筛选参数
  - 响应：活动列表及分页信息

- **创建活动**：`POST /api/activities/`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 请求体：包含活动所有必要信息的JSON对象
  - 响应：创建成功的活动信息

- **获取活动详情**：`GET /api/activities/{activity_id}`
  - 响应：指定活动的详细信息

- **更新活动**：`PUT /api/activities/{activity_id}`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 需活动组织者权限
  - 请求体：包含需要更新的活动信息的JSON对象
  - 响应：更新后的活动信息

- **删除活动**：`DELETE /api/activities/{activity_id}`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 需活动组织者权限
  - 响应：删除成功消息

### 用户相关活动
- **获取我创建的活动**：`GET /api/activities/my-organized`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 响应：当前用户创建的活动列表

- **获取我参与的活动**：`GET /api/activities/my-participated`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 响应：当前用户参与的活动列表

## 3. 报名相关 API

- **报名参加活动**：`POST /api/enrollments/`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 请求体：`{"activity_id": number, "message": "string"}`
  - 响应：报名成功信息

- **审核报名（同意）**：`PUT /api/enrollments/{enrollment_id}/approve`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 需活动组织者权限
  - 响应：审核结果消息

- **审核报名（拒绝）**：`PUT /api/enrollments/{enrollment_id}/reject`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 需活动组织者权限
  - 响应：审核结果消息

- **取消报名**：`DELETE /api/enrollments/{enrollment_id}`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 响应：取消成功信息

- **获取活动的报名列表**：`GET /api/enrollments/activity/{activity_id}`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 需活动组织者权限
  - 响应：指定活动的所有报名记录

- **获取我的报名记录**：`GET /api/enrollments/my`
  - 需认证：在请求头中添加 `Authorization: Bearer {token}`
  - 响应：当前用户的所有报名记录

## 4. 前端错误分析与修复建议

### 404错误（未找到端点）

| 前端调用的端点 | 错误 | 正确的端点 |
|----------------|------|------------|
| `GET /api/activities/joined` | 404 | `GET /api/activities/my-participated` |
| `GET /api/activities/history` | 404 | 后端未实现此端点，可使用 `GET /api/activities/my-participated` 或 `GET /api/activities/my-organized` 并在前端进行过滤 |
| `GET /api/users/stats` | 404 | 后端未实现此端点 |
| `POST /api/users/logout` | 404 | 后端无专门的logout端点，前端只需删除本地存储的token即可 |

### 401错误（未授权）

| 前端调用的端点 | 错误 | 原因与修复 |
|----------------|------|------------|
| `GET /api/activities/my-organized` | 401 | 缺少认证信息，需在请求头中添加 `Authorization: Bearer {token}` |

## 5. 认证说明

- 所有需要认证的端点都必须在请求头中添加 `Authorization: Bearer {token}`
- 登录/注册成功后，后端会返回 `access_token`，前端需将其存储在本地
- 退出登录时，前端只需删除本地存储的token即可
- 401错误表示缺少有效的认证信息，请检查：
  1. 是否已登录并获取了token
  2. token是否已过期
  3. 请求头中是否正确添加了Authorization字段