# 金融影像智能相似度检测系统

## API 接口说明与后续开发预留

**文档用途**：统一记录当前已实现接口、前端 Mock 数据和后续数据库接口预留，供后端开发、前后端联调及 Mock 替换使用。

**状态定义**：

- **已实现**：当前 Flask 后端已有真实路由，且前端已使用。
- **Mock**：前端以本地模拟数据完成展示，真实后端接口尚未开发。
- **待开发**：功能和建议接口契约已确定，当前不存在后端实现。
- **待确认**：用途已确定，但具体路径、参数、返回字段或认证方式仍需后端确认。

> 说明：本文中“建议路径”和“建议字段”均不是现有后端接口，不得据此当作真实接口调用或创建虚假接口。

## 一、当前已有真实接口

### 1. 登录

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 用户登录并返回当前前端保存的用户信息。 |
| 请求方式 | `POST` |
| 接口路径 | `/api/login` |
| 认证方式 | 无需认证。接口返回 token；前端后续请求会在本地存在 token 时附带 `Authorization: Bearer <token>`。当前后端未校验该 token。 |
| 请求参数 | JSON：`username`（字符串，可为空）、`password`（字符串）。 |
| 请求示例 | `{ "username": "operator", "password": "***" }` |
| 返回数据 | `code`、`message`、`data.username`、`data.token`。 |
| 当前状态 | **已实现** |
| 前端调用位置 | `frontend/src/api/index.js` 的 `login()`，由 `LoginRegister.vue` 使用。 |
| 备注 | 当前认证实现为演示逻辑，正式鉴权规则需后端后续确认。 |

### 2. 注册

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 注册或返回已有用户的登录信息。 |
| 请求方式 / 路径 | `POST /api/register` |
| 认证方式 | 无需认证；正式认证机制**待确认**。 |
| 请求参数 | JSON：`username`、`password`。 |
| 返回数据 | `code`、`message`、`data.username`、`data.token`。 |
| 当前状态 | **已实现** |
| 前端调用位置 | `frontend/src/api/index.js` 的 `register()`。 |
| 备注 | 当前为演示账户逻辑，不代表正式用户库。 |

### 3. 用户信息

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 获取当前用户信息。 |
| 请求方式 / 路径 | `GET /api/user/info` |
| 认证方式 | 后端读取可选 `Authorization: Bearer <token>`，但实际按可选查询参数 `username` 返回信息；正式鉴权规则**待确认**。 |
| 请求参数 | 查询参数：`username`（可选）。 |
| 返回数据 | `code`、`data.username`。 |
| 当前状态 | **已实现**（前端页面未接入） |
| 前端调用位置 | 当前 `src/api` 未封装调用。 |

### 4. 文件夹上传

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 上传金融业务影像文件夹，并保留浏览器提交的相对目录结构。 |
| 请求方式 | `POST` |
| 接口路径 | `/api/upload/folder` |
| 认证方式 | 前端请求拦截器可附带 Bearer token；后端未强制校验。可选 `X-Session-Id` 用于复用上传会话。 |
| 请求参数 | `multipart/form-data`：新客户端传递 `folder_name`（上传文件夹顶层名称）和重复字段 `files`（每个文件名携带相对路径）。旧客户端可暂不传 `folder_name`。 |
| 请求示例 | `folder_name=TASK_20260810_001`，`files=@TASK_20260810_001/面签照片/face_signing.jpg`（多个 `files` 字段）。 |
| 返回数据 | `code`、`message`、`data.session_id`、`total_files`、`subdirs`、`image_count`、`images`（最多 50 个图片路径）。 |
| 当前状态 | **已实现** |
| 前端调用位置 | `FolderUpload.vue` 直接请求 `/api/upload/folder`；`src/api/index.js` 同时保留 `uploadFolder()` 封装。 |
| 备注 | 新上传保存为 `backend/uploads/tasks/{folder_name}/`，并保留中文分类子目录和原始相对层级。`folder_name` 只能是合法单层目录名；同名任务返回 `409` 且不会覆盖已有文件。旧客户端未传该字段时仍沿用原会话目录和覆盖行为。 |

### 5. 上传会话信息

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 查询某个上传会话的文件清单和子目录。 |
| 请求方式 / 路径 | `GET /api/upload/session/{session_id}` |
| 认证方式 | **待确认**；当前后端未强制校验。 |
| 请求参数 | 路径参数：`session_id`。 |
| 返回数据 | `code`、`data.session_id`、`total_files`、`subdirs`、`files`。 |
| 当前状态 | **已实现**（前端页面未接入） |
| 前端调用位置 | 当前未封装调用。 |

### 6. 上传文件访问

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 访问某上传会话中的业务影像。 |
| 请求方式 / 路径 | `GET /api/file/{session_id}/{filepath}` |
| 认证方式 | **待确认**；当前后端未强制校验。 |
| 请求参数 | 路径参数：`session_id`、`filepath`。 |
| 返回数据 | 文件二进制内容，图片以对应 MIME 类型返回。 |
| 当前状态 | **已实现** |
| 前端调用位置 | `src/api/index.js` 的 `getFileUrl()`，由筛选和相似度结果组件用于预览。 |

### 7. 面签照片筛选

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 对上传会话中的图片执行本地 YOLO 人物检测，筛选待相似度比对的面签照片。 |
| 请求方式 | `POST` |
| 接口路径 | `/api/classify` |
| 认证方式 | 前端可附带 Bearer token；后端未强制校验。 |
| 请求参数 | JSON：`session_id`（必填）。 |
| 请求示例 | `{ "session_id": "session-uuid" }` |
| 返回数据 | `code`、`message`、`data.total_images`、`person_detected`、`face_signing_images`、`all_images`、`loan_dirs`、`metrics`。面签图片项包含 `image_id`、`file_path`、`loan_id`、`filename`、`image_type`、`person_confidence`。 |
| 当前状态 | **已实现** |
| 前端调用位置 | `src/api/index.js` 的 `runClassify()`，由 `ClassifyResults.vue` 调用。 |
| 备注 | 使用项目本地 YOLO 权重；不是第三方 AI API。 |

### 8. 面签筛选服务状态

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 查询本地面签筛选服务的模型路径和运行设备状态。 |
| 请求方式 / 路径 | `GET /api/classify/status` |
| 认证方式 | **待确认**；当前后端未强制校验。 |
| 请求参数 | 无。 |
| 返回数据 | `code`、`message`、`data.status`、`model`、`model_path_exists`、`device`、`conf_threshold`、`person_class_id`。 |
| 当前状态 | **已实现**（前端页面未接入） |
| 前端调用位置 | 当前未封装调用。 |

### 9. 相似度检测与可疑交易检索

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 对筛选出的面签照片执行本地特征提取、相似度计算、相似组构建和可疑交易识别。 |
| 请求方式 | `POST` |
| 接口路径 | `/api/similarity/detect` |
| 认证方式 | 前端可附带 Bearer token；后端未强制校验。 |
| 请求参数 | 两种真实模式：1）`session_id`、`face_images`、`threshold`；2）`folder_path`、`threshold`。当前检测页使用模式 1。 |
| 请求示例 | `{ "session_id": "session-uuid", "face_images": [{ "image_id": "IMG_00001", "file_path": "loan_001/face_signing.jpg", "loan_id": "loan_001" }], "threshold": 0.90 }` |
| 返回数据 | `code`、`message`、`data.total_images`、`threshold`、`similar_pairs_count`、`groups_count`、`similar_groups`、`suspicious_pairs`、`output_dir`。相似组含 `group_id`、`images`、`count`、`avg_similarity`、`max_similarity`；相似对含 `image_1`、`image_2`、`file_path_1`、`file_path_2`、`similarity`。 |
| 当前状态 | **已实现** |
| 前端调用位置 | `src/api/index.js` 的 `runSimilarity()`，由 `SimilaritySearch.vue` 调用。 |
| 备注 | 特征提取、相似度计算和可疑交易检索没有独立接口，均由本接口完成；真实计算至少需要两张面签照片。 |

### 10. 相似度阈值扫描

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 计算多个固定相似度阈值下的相似对和相似组统计。 |
| 请求方式 / 路径 | `POST /api/similarity/threshold-scan` |
| 认证方式 | **待确认**；当前后端未强制校验。 |
| 请求参数 | JSON：`folder_path` 或 `session_id` 二选一。 |
| 返回数据 | `code`、`message`、`data.input_folder`、`total_images`、`scan`；`scan` 项含 `threshold`、`similar_pairs`、`groups`。 |
| 当前状态 | **已实现**（前端页面未接入） |
| 前端调用位置 | `src/api/index.js` 的 `runThresholdScan()`；当前页面未调用。 |

### 11. 关联业务影像检索

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 在识别到相似面签照片后，获取指定贷款目录的关联业务影像。 |
| 请求方式 / 路径 | `GET /api/similarity/related/{session_id}/{loan_id}` |
| 认证方式 | 前端可附带 Bearer token；后端未强制校验。 |
| 请求参数 | 路径参数：`session_id`、`loan_id`。 |
| 返回数据 | `code`、`data.loan_id`、`files`；每项包含 `filename`、`file_path`、`image_type`、`label`、`loan_id`。 |
| 当前状态 | **已实现** |
| 前端调用位置 | `src/api/index.js` 的 `getRelatedFiles()`，由 `SimilaritySearch.vue` 调用。 |
| 备注 | 当前项目的“可疑交易检索结果”由相似度检测结果和此关联资料检索共同构成。 |

### 12. 服务健康检查

| 项目 | 说明 |
| --- | --- |
| 接口用途 | 检查后端服务以及本地 YOLO、CLIP、LoRA、Projection 权重文件是否存在。 |
| 请求方式 / 路径 | `GET /api/health` |
| 认证方式 | 无。 |
| 请求参数 | 无。 |
| 返回数据 | `code`、`message`、`data.models.yolo`、`clip`、`lora`、`projection`。 |
| 当前状态 | **已实现** |
| 前端调用位置 | `src/api/index.js` 的 `healthCheck()`；当前页面未调用。 |

## 二、智能影像检测接口链路

```text
智能影像检测页面
  -> POST /api/upload/folder                 文件夹上传
  -> POST /api/classify                      面签照片筛选
  -> POST /api/similarity/detect             特征提取、相似度计算、可疑交易识别
  -> GET  /api/similarity/related/{...}      关联业务影像检索
  -> GET  /api/file/{...}                    图片预览
```

检测结果、任务概要和风险统计当前由上述真实接口返回的相似度数据在前端展示；当前没有独立的“检测结果 API”或“风险统计 API”。

## 三、当前 Mock 数据

### 历史检测任务与详情（前端 Mock）

| 项目 | 说明 |
| --- | --- |
| 数据访问方法 | `getDetectionTasks()`、`getDetectionTask(taskId)` |
| 代码位置 | `frontend/src/api/tasks.js` |
| Mock 数据位置 | `frontend/src/mock/tasks.js` |
| 当前状态 | **Mock** |
| 用途 | `/tasks` 的筛选、分页、任务列表与 `/tasks/:id` 的详情展示。 |
| 请求方式 / 路径 | 当前不发起 HTTP 请求。未来建议分别为 `GET /api/history/tasks`、`GET /api/history/tasks/{taskId}`。 |
| 当前字段 | `taskId`、`createdAt`、`detectedAt`、`duration`、`similarity`、`riskLevel`、`status`，以及详情中的影像、筛选、相似度、风险统计和异常影像。 |
| 备注 | Mock 仅用于前端展示与交互。报告生成和重新检测不调用虚假后端接口。 |

### 历史面签照片查询（前端 Mock）

| 项目 | 说明 |
| --- | --- |
| 数据访问方法 | `getHistoricalInterviewPhotos()` |
| 代码位置 | `frontend/src/api/history.js` |
| Mock 数据位置 | `frontend/src/mock/historyInterviewPhotos.js` |
| 当前状态 | **Mock** |
| 用途 | 检测页展示“历史面签照片预览（MOCK）”。 |
| 请求方式 / 路径 | 当前不发起 HTTP 请求。未来建议为 `GET /api/history/interview-photos`。 |
| 支持参数 | 当前 Mock 支持 `page`、`pageSize`；未来参数见下一节。 |
| 返回字段 | `code`、`message`、`mock`、`data.total`、`page`、`pageSize`、`records`；记录字段为 `photoId`、`businessId`、`loanId`、`photoType`、`imageUrl`、`imagePath`、`captureTime`。 |
| 备注 | 数据明确标记为 MOCK，不参与本地模型输入、相似度、风险统计或可疑交易结果。正式接口接入时只替换数据访问层，页面结构不应大改。 |

## 四、后续待开发接口

除“历史图片访问”外，下列接口状态均为 **待开发**。认证方式建议 `Authorization: Bearer <token>`，但所有正式认证规则均为**待后端确认**。

### 1. 历史检测任务

- 建议接口：`GET /api/history/tasks`
- 用途：查询历史检测任务列表。
- 建议参数：`page`、`pageSize`、`taskId`、`startTime`、`endTime`、`status`、`riskLevel`。
- 建议返回记录：`taskId`、`createdAt`、`similarity`、`riskLevel`、`status`。
- 前端状态：当前已有 **Mock** 数据访问层；正式后端接口仍为 **待开发**。

### 2. 历史检测任务详情

- 建议接口：`GET /api/history/tasks/{taskId}`
- 用途：获取指定检测任务详情。
- 建议参数：路径参数 `taskId`。
- 建议返回：任务编号、创建时间、检测时间、检测耗时、相似度、风险等级、状态、影像统计、面签筛选统计、相似度统计、风险统计、异常影像。
- 前端状态：当前已有 **Mock** 数据访问层；正式后端接口仍为 **待开发**。

### 3. 历史面签照片

- 建议接口：`GET /api/history/interview-photos`
- 用途：查询历史面签照片。
- 建议参数：`page`、`pageSize`、`businessId`、`loanId`、`customerId`、`startTime`、`endTime`、`keyword`。
- 建议返回：`photoId`、`businessId`、`loanId`、`photoType`、`imageUrl`、`imagePath`、`captureTime`，以及分页字段 `total`、`page`、`pageSize`。
- 前端状态：已有 **Mock** 数据访问层；正式后端接口仍为 **待开发**。

### 4. 历史相似度检测记录

- 建议接口：`GET /api/history/similarity`
- 用途：查询历史相似度检测结果。
- 建议参数：`page`、`pageSize`、`taskId`、`similarityMin`、`similarityMax`、`startTime`、`endTime`。
- 建议返回：`taskId`、`imageId`、`imageName`、`similarImageId`、`similarImageName`、`similarity`、`riskLevel`、`createdAt`。
- 前端状态：未接入。

### 5. 风险案件

- 建议接口：`GET /api/risk/cases`
- 用途：查询风险案件。
- 建议参数：`page`、`pageSize`、`riskLevel`、`status`、`startTime`、`endTime`、`keyword`。
- 建议返回：`caseId`、`taskId`、`riskLevel`、`similarity`、`status`、`createdAt`、`description`。
- 前端状态：当前已有 **Mock** 数据访问层；正式后端接口仍为 **待开发**。

### 5.1 风险案件详情与处理（前端 Mock）

| 项目 | 说明 |
| --- | --- |
| 数据访问方法 | `getRiskCase()`、`updateRiskCaseStatus()` |
| 代码位置 | `frontend/src/api/cases.js` |
| Mock 数据位置 | `frontend/src/mock/cases.js` |
| 当前状态 | **Mock** |
| 用途 | `/cases` 筛选与列表、`/cases/:id` 详情、待核查到核查中及确认/排除状态切换。 |
| 当前请求方式 | 不发起 HTTP 请求；处理操作只更新浏览器运行期 Mock 数据。 |
| 图片来源 | `frontend/public/mock/cases/` 中的 Mock 图片；不调用后端图片接口。 |
| 备注 | 相似度、风险原因和图片均为 Mock 演示数据，不是实时检测或后端案件数据。 |

#### 后续风险案件接口建议

- `GET /api/risk/cases`：列表查询；建议参数 `page`、`pageSize`、`caseId`、`businessId`、`riskLevel`、`status`、`startTime`、`endTime`。
- `GET /api/risk/cases/{caseId}`：查询案件详情；建议返回案件编号、风险等级、案件状态、业务 A/B、相似度、风险原因、发现时间和处理状态。
- `POST /api/risk/cases/{caseId}/review`：开始核查，建议更新为“核查中”。
- `POST /api/risk/cases/{caseId}/confirm`：确认风险，建议更新为“已确认”。
- `POST /api/risk/cases/{caseId}/dismiss`：标记正常，建议更新为“已排除”。
- 上述均为 **待开发** 建议接口，认证建议 Bearer Token，具体规则**待后端确认**。

### 6. 检测统计

- 建议接口：`GET /api/statistics/detection`
- 用途：获取首页或数据分析页的检测统计。
- 建议返回：`totalTasks`、`completedTasks`、`failedTasks`、`highRiskCount`、`mediumRiskCount`、`lowRiskCount`、`averageSimilarity`、`highSimilarityCount`。
- 前端状态：未接入。

### 6.1 影像检测数据分析（前端 Mock）

| 项目 | 说明 |
| --- | --- |
| 数据访问方法 | `getAnalyticsStatistics(range)` |
| 代码位置 | `frontend/src/api/analytics.js`、`frontend/src/services/statistics.js` |
| 稳定基础数据 | `frontend/src/mock/analytics.js`（按检测任务 ID 维护影像分类统计） |
| 当前状态 | **Mock** |
| 用途 | `/analytics` 根据今日、近 7 日、近 30 日、近 90 日聚合检测趋势、风险趋势、相似度分布、影像分类和风险分布。 |
| 数据来源 | 检测任务使用 `mock/tasks.js`，风险案件使用 `mock/cases.js`；与首页相同的统计服务派生。 |
| 备注 | 不生成随机数据，不调用后端接口。 |

#### 后续影像检测数据分析接口建议

- `GET /api/statistics/analytics`
- 建议参数：`startDate`、`endDate`。
- 建议返回：`detectionTrend`、`riskTrend`、`similarityDistribution`、`imageCategoryDistribution`、`riskDistribution`。
- 建议结构：`{ "code": 200, "data": { "detectionTrend": [], "riskTrend": [], "similarityDistribution": [], "imageCategoryDistribution": [], "riskDistribution": [] } }`。
- 当前状态：**待开发**；认证建议 Bearer Token，具体规则**待后端确认**。

### 7. 报告生成

- 建议接口：`POST /api/reports/generate`
- 用途：为指定任务生成报告。
- 建议参数：`taskId`、`reportType`。
- 建议返回：`reportId`、`status`、`downloadUrl`、`createdAt`。
- 前端状态：未接入。

### 8. 重新检测

- 建议接口：`POST /api/tasks/{taskId}/retry`
- 用途：重新提交指定检测任务。
- 建议参数：路径参数或 JSON 中的 `taskId`，最终方式**待后端确认**。
- 建议返回：`newTaskId`、`status`、`createdAt`。
- 前端状态：未接入。

### 9. 历史图片访问

- 建议接口：`GET /api/images/{photoId}`，或由历史面签接口返回受权限控制的 `imageUrl`。
- 用途：按照片标识访问历史面签图片。
- 当前状态：**待确认**。
- 待确认事项：正式图片授权、有效期、下载/预览权限和最终 URL 规则。
- 约束：正式系统优先返回受权限控制的 `imageUrl`，不直接暴露服务器物理 `imagePath`。

## 五、页面—接口对应关系

| 页面或功能 | 当前数据来源 / 后续接口 |
| --- | --- |
| 智能影像检测 | `POST /api/upload/folder` → `POST /api/classify` → `POST /api/similarity/detect` → `GET /api/similarity/related/{session_id}/{loan_id}` |
| 上传与结果图片预览 | `GET /api/file/{session_id}/{filepath}` |
| 历史面签照片预览 | 当前 `getHistoricalInterviewPhotos()` Mock；后续 `GET /api/history/interview-photos` |
| 检测任务 | 当前 `getDetectionTasks()` Mock；后续 `GET /api/history/tasks` |
| 检测任务详情 | 当前 `getDetectionTask(taskId)` Mock；后续 `GET /api/history/tasks/{taskId}` |
| 历史相似度 | 后续 `GET /api/history/similarity` |
| 风险案件 | 后续 `GET /api/risk/cases` |
| 风险案件中心 | 当前 `getRiskCases()` / `getRiskCase()` Mock；后续风险案件列表、详情与处理接口 |
| 影像检测数据分析 | 当前 `getAnalyticsStatistics()` Mock；后续 `GET /api/statistics/analytics` |
| 检测统计 | 后续 `GET /api/statistics/detection` |
| 检测报告 | 后续 `POST /api/reports/generate` |
| 重新检测 | 后续 `POST /api/tasks/{taskId}/retry` |

## 六、后续接口开发优先级

| 优先级 | 接口 |
| --- | --- |
| P0 | 历史检测任务、历史检测任务详情 |
| P1 | 历史面签照片、历史相似度检测 |
| P2 | 风险案件、检测统计 |
| P3 | 检测报告、重新检测 |

## 七、数据库字段设计参考

以下仅为数据库设计参考，不代表当前项目已创建数据库或数据表。

### 检测任务

`task_id`、`created_at`、`completed_at`、`duration`、`similarity`、`risk_level`、`status`

### 面签照片

`photo_id`、`business_id`、`loan_id`、`image_url`、`capture_time`

### 检测结果

`result_id`、`task_id`、`photo_id`、`similar_photo_id`、`similarity`、`risk_level`、`created_at`

## 八、联调约束

1. 后端实现历史接口后，先确认正式路径、认证、分页、错误码和图片授权规则，再替换 `src/api` 数据访问层。
2. 页面组件不得把 Mock 数据当作真实检测结果，也不得直接调用本文中的待开发路径。
3. 不得为满足文档而虚构接口、修改模型权重或改变上传、筛选、相似度检测和关联资料检索流程。检测结果持久化使用第九节说明的项目内 SQLite 实现。

## 九、统一检测结果数据源（已实现）

智能影像检测完成后，后端会将真实任务、相似度明细和风险案件保存到 `backend/detection_results.sqlite3`。该文件使用 Python 标准库 `sqlite3`，不依赖外部数据库服务；模型、模型权重和现有检测请求结构均未改变。

数据形成链路：

```text
POST /api/upload/folder → detection_tasks（检测中）
POST /api/classify → 更新影像与面签统计
POST /api/similarity/detect → 保存相似度明细、生成风险案件、任务完成
```

### 1. 获取历史检测任务

| 项目 | 说明 |
| --- | --- |
| 请求方式 / 路径 | `GET /api/history/tasks` |
| 当前状态 | **已实现** |
| 认证方式 | 前端沿用 `Authorization: Bearer <token>`；后端权限校验待后续完善。 |
| 参数 | `page`、`pageSize`、`taskId`、`startTime`、`endTime`、`status`、`riskLevel`。 |
| 返回 | `total`、`page`、`pageSize`、`records`；记录包含 `taskId`、时间、相似度、风险等级、状态和影像统计。 |

### 2. 获取检测任务详情

| 项目 | 说明 |
| --- | --- |
| 请求方式 / 路径 | `GET /api/history/tasks/{taskId}` |
| 当前状态 | **已实现** |
| 返回 | 任务基本信息、影像统计、面签筛选统计、相似度统计、风险统计、异常影像及相似度明细。 |

### 3. 获取风险案件

| 项目 | 说明 |
| --- | --- |
| 请求方式 / 路径 | `GET /api/risk/cases` |
| 当前状态 | **已实现** |
| 参数 | `caseId`、`businessId`、`startTime`、`endTime`、`riskLevel`、`status`。 |
| 返回 | `caseId`、`taskId`、业务 A/B、面签图片相对路径、相似度、风险等级、规则化风险原因、发现时间和处理状态。 |

### 4. 风险案件详情与处理

| 操作 | 接口 | 当前状态 |
| --- | --- | --- |
| 查询详情 | `GET /api/risk/cases/{caseId}` | **已实现** |
| 开始核查 | `POST /api/risk/cases/{caseId}/review` | **已实现** |
| 确认风险 | `POST /api/risk/cases/{caseId}/confirm` | **已实现** |
| 标记正常 | `POST /api/risk/cases/{caseId}/dismiss` | **已实现** |

### 5. 获取影像检测分析统计

| 项目 | 说明 |
| --- | --- |
| 请求方式 / 路径 | `GET /api/statistics/analytics` |
| 当前状态 | **已实现** |
| 参数 | `startDate`、`endDate`；或传入 `all=true` 获取从最早检测任务创建日期至 `endDate`（默认今天）的全部历史统计。 |
| 返回 | `detectionTrend`、`riskTrend`、`similarityDistribution`、`imageCategoryDistribution`、`riskDistribution`、任务与案件摘要。 |

### 6. 前端数据源切换

默认真实数据模式下，任务、案件、分析、首页和操作日志请求上述接口。接口成功但无记录时，页面展示真实空状态或零值；接口失败时展示错误与重试，不回退 Mock。Mock 仅在显式设置 `VITE_DATA_SOURCE=mock` 时使用，不会写入 SQLite，也不会与真实统计混合。

如需固定使用演示数据，可设置：

```text
VITE_DATA_SOURCE=mock
```

### 7. 操作日志

| 项目 | 说明 |
| --- | --- |
| 请求方式 / 路径 | `GET /api/system/operation-logs` |
| 当前状态 | **已实现** |
| 认证方式 | 前端请求携带 `Authorization: Bearer <token>`；当前模拟认证以 Token 对应用户名作为日志操作者。 |
| 参数 | `page`（默认 1）、`pageSize`（默认 20，最大 100）。 |
| 返回 | `total`、`page`、`pageSize`、`records`；每项包含 `id`、`username`、`action`、`detail`、`type`、`occurredAt`。 |
| 空数据 | SQLite 中没有日志时返回 `records: []` 与 `total: 0`；系统管理页面显示“暂无操作日志”，不使用 Mock。 |

操作日志持久化在 `operation_logs` 表：`log_id`、`username`、`action`、`detail`、`type`、`occurred_at`。当前记录登录、上传影像、开始检测、完成检测、检测失败，以及案件开始核查、确认风险、标记为正常等成功业务操作；不记录密码、Token、绝对文件路径、影像内容或只读页面访问。
