# 双脑引擎E2E验证方案

## 目录结构
```
test/
├── mock_x_post.txt          # 测试用高噪音推文数据
├── validate_dual_brain.py   # 主验证脚本
└── __init__.py             # Python包初始化
```

## 使用方法

### 1. 运行完整验证
```bash
cd DavidAgent/brain/test
python validate_dual_brain.py
```

### 2. 验证检查点说明

**阶段1：左脑蛋白质提取验证**
- ✅ JSON格式强制性：确保返回标准结构化数据
- ✅ 去噪能力：过滤情绪化废话，提取核心实体
- ✅ PageIndex固化：生成双链Markdown文件

**阶段2：黑板神经电信号验证**  
- ✅ 事件驱动：状态树正确更新

**阶段3：右脑米其林烹饪验证**
- ✅ 幻觉阻断：严格基于左脑提取的逻辑，不捏造信息
- ✅ Persona升维：生成带科技达人风格的连贯文章

## 日常开发使用场景

### 作为重构护城河
每次修改左脑Prompt或升级右脑模型后，运行验证脚本确保逻辑链条完整。

### 持续监控集成
可将此脚本集成到cron任务中，定时验证双脑引擎健康状态，异常时发送告警。

## 环境要求
- Python 3.8+
- 配置环境变量：
  - `GEMINI_API_KEY`
  - `DASHSCOPE_API_KEY`