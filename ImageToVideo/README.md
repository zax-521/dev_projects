# Image to Video Demo

基于 FastAPI + OpenCV 的图片转视频 Web 应用。上传多张图片，一键生成视频，支持在线预览和下载。

## 功能特性

- **图片上传**：支持 PNG、JPG、WebP 格式，可多选或拖拽上传
- **参数可调**：每张图片时长、帧率(FPS)、输出格式(MP4/AVI)、过渡效果(淡入淡出)
- **视频生成**：自动统一图片尺寸，支持淡入淡出过渡效果
- **在线预览**：生成后可直接在浏览器播放和下载

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| Web 服务器 | Uvicorn |
| 视频处理 | OpenCV (cv2) |
| 数值计算 | NumPy |
| 前端 | 原生 HTML / CSS / JavaScript |

## 快速开始

### 1. 克隆项目

```bash
git clone <repo-url>
cd ImageToVideo
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python main.py
```

服务默认运行在 `http://localhost:8000`。

### 4. 使用

1. 浏览器打开 `http://localhost:8000`
2. 上传图片（可多选或拖拽）
3. 调整视频参数（时长、帧率、格式、过渡效果）
4. 点击"生成视频"
5. 在线预览或下载视频

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 返回前端页面 |
| POST | `/api/upload` | 上传图片文件 |
| POST | `/api/generate` | 根据上传的图片生成视频 |
| GET | `/api/download/{filename}` | 下载生成的视频文件 |

### POST /api/upload

上传图片文件，支持多张同时上传。

**参数**：`files` (multipart/form-data)

**响应示例**：
```json
{
  "session_id": "a1b2c3d4",
  "files": ["img1.png", "img2.png"],
  "count": 2
}
```

### POST /api/generate

根据上传的图片生成视频。

**参数** (form-data)：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| session_id | string | - | 上传图片后返回的会话 ID |
| fps | int | 24 | 视频帧率 |
| duration_per_image | float | 2.0 | 每张图片显示时长(秒) |
| output_format | string | mp4 | 输出格式 (mp4 / avi) |
| transition | string | none | 过渡效果 (none / fade) |

**响应示例**：
```json
{
  "video_url": "/api/download/video_a1b2c3d4_abc123.mp4",
  "filename": "video_a1b2c3d4_abc123.mp4"
}
```

## 项目结构

```
ImageToVideo/
├── main.py              # FastAPI 主应用，API 路由定义
├── video_processor.py   # 图片转视频核心逻辑（OpenCV）
├── requirements.txt     # Python 依赖清单
├── README.md            # 项目说明文档
├── static/
│   └── index.html       # 前端页面
├── uploads/             # 上传图片存储目录（自动创建）
└── outputs/             # 生成视频输出目录（自动创建）
```
