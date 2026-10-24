---
name: unit-test
description: 为「RAG 知识库问答系统」代码创建单元测试、运行测试并生成测试报告
---

# 单元测试

本技能用于为代码**创建单元测试**、**执行测试**、并**输出测试报告**。

## 测试环境

- 后端（Python）：测试工具 pytest。若未安装：`cd backend && .venv/Scripts/python -m pip install pytest`。
- 运行命令：`cd backend && .venv/Scripts/python -m pytest -v`。
- 测试文件命名：`test_*.py`，放在 `backend/tests/` 目录下。
- 前端（Vue）：如需测前端组件，可用 Vitest（`cd frontend && npm test`），当前项目暂未配置。

## 执行步骤

1. **确定测试对象**：优先测「纯函数」——不依赖数据库、不依赖网络、输入确定输出就确定的函数。
   - 后端可测：`app/security.py` 里的 `hash_password` / `verify_password`（密码哈希），`app/rag/chain.py` 里的 `format_context` / `build_messages` 等纯函数。
   - 不要直接测：需要真实 API Key 的 LLM/嵌入调用、真实 Chroma 检索、真实 SQLite 数据库读写（这些需要 mock 或集成测试，超出单元测试范围）。
2. **创建测试文件**：用 pytest 的 `test_` 函数 + `assert` 编写用例。
3. **运行测试**：执行 `cd backend && .venv/Scripts/python -m pytest -v`，等待结果。
4. **输出测试报告**：用中文汇报——共几个测试文件、共几个用例、通过/失败几个；失败时逐个说明失败项名称、原因，并给修复建议。

## 注意事项

- 只测「纯函数」。不要试图测需要联网、需要真实 API Key、或真实数据库/向量库的逻辑。
- 如果某个逻辑「藏」在路由函数里难以测试，先把它抽取成独立纯函数再测。
- 运行测试一般不需要关闭沙箱；若因环境报错再尝试关闭沙箱。
