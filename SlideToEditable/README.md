# SlideToEditable

将交互式 HTML 幻灯片转换为 **PDF** 或 **PPTX** 文件。

- **PDF**：完整保留 HTML 的样式、背景、布局，文字可选择复制
- **PPTX**：截图保留完整视觉样式作为背景，上层叠加可编辑文本框，文字可复制修改

## 功能特性

- Web 界面：上传 HTML 文件，选择格式和语言，一键转换
- PDF 转换：使用 Playwright 完整渲染 HTML（含 JS 动态内容），自动切换语言、隐藏干扰元素
- PPTX 转换：Playwright 截图保留样式 + BeautifulSoup 提取文字叠加可编辑文本框
- 多语言支持：自动识别并切换 `.content-{lang}` 语言内容块
- 支持 JS 导航式幻灯片（`display:none` / `.active` 切换）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 3. 启动服务

```bash
python app.py
```

或

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 4. 打开浏览器

访问 [http://localhost:8000](http://localhost:8000)

## HTML 幻灯片格式要求

源 HTML 文件需满足以下结构：

- 每个幻灯片使用 `<div class="slide">` 包裹
- 多语言内容使用 `.content-{lang}` 类名标记（如 `.content-ru`、`.content-en`、`.content-zh`）
- 支持 JS 导航（`display:none` / `.active` 类切换）

示例：

```html
<div class="slide">
  <div class="content-ru active">
    <h1>Заголовок</h1>
    <p>Текст на русском</p>
  </div>
  <div class="content-en">
    <h1>Title</h1>
    <p>Text in English</p>
  </div>
  <button class="lang-btn" onclick="setLanguage('ru')">RU</button>
  <button class="lang-btn" onclick="setLanguage('en')">EN</button>
</div>
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 返回前端页面 |
| POST | `/convert` | 上传 HTML 并转换 |

### POST /convert

表单字段：

- `file`: HTML 文件（必填）
- `type`: 转换类型，`pdf` 或 `pptx`（必填）
- `lang`: 语言，`ru` / `en` / `zh`（默认 `ru`）

## 项目结构

```
SlideToEditable/
├── app.py              # FastAPI 主程序
├── requirements.txt    # 依赖清单
├── README.md           # 说明文档
├── static/
│   └── index.html      # 前端页面
├── uploads/            # 上传文件目录
└── outputs/            # 输出文件目录
```

## 技术栈

- **后端框架**: FastAPI
- **HTML 渲染与 PDF 生成**: Playwright (Chromium)
- **PPTX 生成**: python-pptx + Playwright 截图
- **HTML 解析**: BeautifulSoup4 + lxml
- **前端**: 原生 HTML + CSS + JavaScript
