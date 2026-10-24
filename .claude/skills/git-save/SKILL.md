---
name: git-save
description: 将改动存档并上传到 GitHub（git add + commit + push）
---

# 存档上传（git-save）

将当前改动存档并上传到 GitHub。

## 执行步骤

1. `git add -A` 暂存所有改动。
2. `git commit`：若用户已提供提交信息则使用；否则根据改动内容用中文写一句概括。
3. `git push origin main` 上传到 GitHub（联网操作，需要关闭沙箱）。
4. 用中文向用户汇报提交结果。

## 注意事项

- 提交信息用中文、简洁、概括本次改动的核心。
- push 需要联网，必要时关闭沙箱。
