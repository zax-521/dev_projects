# 测试题生成器

一个基于Python的智能测试题生成工具，支持从PDF、Word文档中提取内容并生成四种类型的测试题。

## 功能特点

- 📄 **多格式支持**: 支持PDF、DOC、DOCX、TXT格式文档
- 🧠 **智能生成**: 支持本地生成和DeepSeek AI生成两种模式
- 📝 **四种题型**: 选择题、排序题、配对题、解答题
- 📊 **详细导出**: 支持JSON和TXT格式导出
- 🔧 **灵活配置**: 可自定义题目类型、数量等参数

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用（本地生成）

```bash
# 生成所有四种题型，每种3题
python deepseek_test_generator.py 文档.pdf

# 只生成选择题和解答题
python deepseek_test_generator.py 文档.docx --types choice essay

# 指定输出文件名和题目数量
python deepseek_test_generator.py 文档.pdf --output my_test --num 5
```

### 使用DeepSeek AI生成

```bash
# 使用DeepSeek API生成更高质量的题目
python deepseek_test_generator.py 文档.pdf --use-deepseek --api-key YOUR_DEEPSEEK_API_KEY

# 或者设置环境变量
export DEEPSEEK_API_KEY=your_api_key
python deepseek_test_generator.py 文档.pdf --use-deepseek
```

### 参数说明

- `input_file`: 输入文件路径（必需）
- `--output, -o`: 输出文件名前缀（默认：output）
- `--types, -t`: 题目类型列表（默认：所有四种类型）
- `--num, -n`: 每种题型的数量（默认：3）
- `--use-deepseek`: 使用DeepSeek API生成题目
- `--api-key`: DeepSeek API密钥

## 支持的题型

1. **选择题 (choice)**
   - 基于文本内容的理解题
   - 4个选项，包含正确答案和解析

2. **排序题 (sorting)**
   - 将打乱的句子按逻辑顺序排列
   - 考察逻辑思维能力

3. **配对题 (matching)**
   - 概念与描述的匹配
   - 考察概念理解能力

4. **解答题 (essay)**
   - 开放式问题
   - 包含评分标准和字数要求

## 输出文件

程序会生成两个文件：

- `output.json`: 结构化JSON格式，包含完整题目数据和元数据
- `output.txt`: 可读性强的文本格式，适合打印或直接查看

## DeepSeek API配置

1. 获取DeepSeek API密钥：访问 https://platform.deepseek.com/
2. 设置API密钥：
   - 通过命令行参数：`--api-key YOUR_KEY`
   - 通过环境变量：`DEEPSEEK_API_KEY`

## 示例

```bash
# 从PDF文档生成测试题
python deepseek_test_generator.py sample.pdf --output exam --types choice sorting --num 4

# 使用DeepSeek生成高质量题目
python deepseek_test_generator.py lecture.docx --use-deepseek --api-key sk-xxx --num 5
```

## 文件结构

```
.
├── deepseek_test_generator.py  # 主程序（推荐使用）
├── test_generator.py           # 基础版本（支持OpenAI）
├── enhanced_test_generator.py  # 增强版本
├── config.py                   # 配置文件
├── requirements.txt            # 依赖列表
└── README.md                   # 说明文档
```

## 注意事项

1. 确保输入文档包含足够的内容（建议至少500字符）
2. 使用DeepSeek API需要网络连接和有效的API密钥
3. 程序会自动处理文档编码和格式问题
4. 生成的题目仅供参考，建议人工审核后使用

## 故障排除

- **文档提取失败**: 检查文件格式和权限
- **API调用失败**: 检查网络连接和API密钥
- **题目生成失败**: 尝试增加文本内容或使用本地模式
- **编码问题**: 程序会自动检测编码，如有问题可手动指定

## 许可证

