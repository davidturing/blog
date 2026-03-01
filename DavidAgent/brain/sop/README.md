# DavidAgent 双脑架构工程化SOP

## 目录结构
```
sop/
├── README.md               # 本SOP文档
├── environment_setup.py    # 环境初始化脚本
├── validate_physical_layer.py  # 物理层验证（数据落盘）
├── validate_logical_layer.py   # 逻辑层验证（API契约）
├── validate_cognitive_layer.py # 认知层验证（对抗性幻觉演练）
└── run_full_sop.py         # 完整SOP执行脚本
```

## 运行环境准备

### 1. 目录与存储初始化
- ✅ `skills/self-learning-agent/pageindex/knowledge/` 目录
- ✅ ChromaDB本地服务（可选）

### 2. 环境变量配置
```bash
# .env文件
GEMINI_API_KEY=your_gemini_api_key
DASHSCOPE_API_KEY=your_dashscope_api_key
```

### 3. OpenClaw框架集成
- Qwen作为主Agent实例运行
- Gemini封装为异步外部Tool
- 所有状态通过Blackboard内存对象共享

## 三层验证体系

### 第一层：物理层验证（数据落盘）
- 检查PageIndex目录是否生成新.md文件
- 验证双链语法`[[ ]]`存在
- 确保三元组格式符合规范

### 第二层：逻辑层验证（API契约）
- JSON Schema校验左脑输出
- 验证去噪能力（过滤无意义内容）
- 强类型接口保证系统稳定性

### 第三层：认知层验证（对抗性幻觉演练）
- 红蓝对抗：注入虚假信息
- 验证左脑纠错审查能力
- 确保免疫系统正常工作

## 执行流程

```bash
# 1. 环境初始化
python sop/environment_setup.py

# 2. 运行完整SOP验证
python sop/run_full_sop.py
```

成功标准：所有断言通过，无异常抛出。