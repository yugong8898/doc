# 🚀 GitLens Superpowers 快速上手指南

## ✅ 安装状态
GitLens Superpowers 已通过 MCP 成功集成到您的 Cursor IDE 中！

## 📋 可用工具清单（30+ 个）

### 🔧 基础 Git 操作
- ✅ `git_status` - 查看仓库状态
- ✅ `git_branch` - 分支管理
- ✅ `git_checkout` - 切换分支  
- ✅ `git_add_or_commit` - 添加和提交
- ✅ `git_push` / `git_pull` / `git_fetch` - 代码同步
- ✅ `git_stash` - 暂存工作区
- ✅ `git_worktree` - 多工作区管理

### 🔍 代码审查工具
- ✅ `git_blame` - 查看代码作者（谁写的这行代码）
- ✅ `git_log_or_diff` - 提交历史和差异对比
- ✅ `git_graph` - 可视化分支图

### 🚀 智能工作流
- ✅ `gitlens_launchpad` - 智能工作面板（今日任务）
- ✅ `gitlens_commit_composer` - AI 生成提交信息
- ✅ `gitlens_start_work` - 开始新任务
- ✅ `gitlens_start_review` - 开始代码审查

### 📋 Issue 管理
- ✅ `issues_assigned_to_me` - 我的 Issue
- ✅ `issues_create` - 创建 Issue
- ✅ `issues_get_detail` - Issue 详情
- ✅ `issues_add_comment` - 添加评论

### 🔀 Pull Request 管理
- ✅ `pull_request_assigned_to_me` - 我的 PR
- ✅ `pull_request_create` - 创建 PR
- ✅ `pull_request_create_review` - 创建审查
- ✅ `pull_request_get_detail` - PR 详情
- ✅ `pull_request_get_comments` - PR 评论

## 🎯 常见使用场景

### 场景 1️⃣：快速查看某个文件的修改历史

**使用 Cursor IDE：**
1. 打开文件（例如 `waybillSettlement/edit.vue`）
2. 每行代码左侧会自动显示作者和时间
3. 鼠标悬停查看详细提交信息
4. 点击可查看完整的提交详情

**效果：**
```
303 │ <div v-if="!isInMicroApp">           👤 王新骏 4小时前
304 │   <div class="credit-account">        👤 王新骏 4小时前
305 │     <!-- ... -->                       👤 李明 2天前
```

### 场景 2️⃣：理解复杂的分支合并历史

**命令面板操作：**
1. `Cmd+Shift+P`
2. 输入 `GitLens: Show Commit Graph`
3. 可视化查看所有分支和合并关系

**或者使用侧边栏：**
- 点击左侧 GitLens 图标
- 选择 "Commits" 或 "Branches"
- 交互式查看提交历史

### 场景 3️⃣：代码审查前的快速检查

**步骤：**
1. 打开 `gitlens_launchpad`（智能工作面板）
2. 查看待处理的 PR 列表
3. 点击某个 PR 开始审查
4. 逐行查看改动和添加评论

### 场景 4️⃣：追踪 Bug 来源

**当发现 Bug 时：**
1. 定位到有问题的代码行
2. 使用 `git_blame` 查看是谁、什么时候修改的
3. 鼠标悬停查看完整的提交信息
4. 点击查看该提交的完整改动
5. 理解修改的上下文

### 场景 5️⃣：创建 Pull Request

**传统方式 vs GitLens：**

❌ **传统方式：**
```bash
git push
# 打开浏览器
# 进入 GitLab/GitHub
# 填写 PR 表单
# 分配审查者
```

✅ **GitLens 方式：**
1. `Cmd+Shift+P`
2. 输入 `GitLens: Create Pull Request`
3. 自动填充信息，一键创建
4. 无需离开 IDE！

## 💡 实用技巧

### 技巧 1：查看文件的完整修改历史
- 右键点击文件
- 选择 "GitLens: Show File History"
- 时间线形式展示所有修改

### 技巧 2：对比两个分支的差异
- 右键点击分支
- 选择 "Compare with..."
- 选择要对比的分支
- 查看文件级别的差异

### 技巧 3：快速切换工作上下文（Worktrees）
- 使用 `git_worktree` 工具
- 创建独立的工作区
- 同时处理多个任务（主开发 + 紧急修复）

### 技巧 4：搜索提交历史
- `Cmd+Shift+P`
- 输入 `GitLens: Search Commits`
- 按关键词、作者、时间搜索

### 技巧 5：使用 AI 生成提交信息
- 暂存改动后
- 使用 `gitlens_commit_composer`
- AI 自动分析改动并生成规范的提交信息

## 🎨 IDE 界面集成

### 侧边栏面板
点击 Cursor 左侧的 **GitLens 图标**，可以看到：
- 📊 **Commits** - 提交历史
- 🌿 **Branches** - 分支列表
- 📁 **File History** - 文件历史
- 🔖 **Tags** - 标签列表
- 👥 **Contributors** - 贡献者统计
- 🚀 **Launchpad** - 智能工作面板

### 编辑器内联显示
- 每行代码旁显示最后修改者和时间
- 鼠标悬停显示完整提交信息
- 点击快速导航到提交详情

### 状态栏信息
- 当前分支名称
- 同步状态（领先/落后多少提交）
- 快速切换分支

## 📚 进阶学习

### 推荐阅读项目中的文档：
1. `docs/superpowers-team-collaboration.md` - 团队协作实战
2. `docs/superpowers-demo-code-review.md` - 代码审查演示

### 官方资源：
- GitLens 文档: https://help.gitkraken.com/gitlens/
- 视频教程: https://www.youtube.com/gitkraken

## ⚡️ 效率提升统计

根据项目文档的实战测试：

| 任务 | 传统方式 | GitLens | 提升 |
|------|---------|---------|------|
| 理解分支结构 | 10分钟 | 30秒 | **95%** |
| 检查代码冲突 | 5分钟 | 20秒 | **93%** |
| 追踪团队进度 | 15分钟 | 1分钟 | **93%** |
| 创建 PR | 3分钟 | 30秒 | **83%** |
| 切换工作上下文 | 5分钟 | 1分钟 | **80%** |

**平均效率提升：88%+** 🚀

## 🎓 最佳实践

### 每日工作流
```
早上：
1. 打开 GitLens Launchpad 查看任务
2. 同步最新代码（git_pull）
3. 检查待审查的 PR

开发中：
4. 实时查看文件修改历史
5. 使用 git_blame 了解代码来源
6. 定期提交并推送

下班前：
7. 创建 PR 并分配审查者
8. 查看明日待办
```

### 代码审查清单
```
☑️ 查看提交历史是否清晰
☑️ 检查是否有合并冲突
☑️ 确认改动符合需求
☑️ 验证测试覆盖
☑️ 批准或请求修改
```

## 🆘 常见问题

### Q: 为什么我看不到 GitLens 侧边栏？
**A:** 点击 Cursor 左侧活动栏，找到 GitLens 图标（通常是一个分支图标）

### Q: 如何禁用/启用行内作者信息？
**A:** `Cmd+Shift+P` → `GitLens: Toggle Line Blame`

### Q: GitLens 工具调用超时怎么办？
**A:** 某些 GitLens 工具需要在 UI 中打开，直接使用 IDE 界面操作即可

### Q: 如何在不同项目间切换？
**A:** GitLens 会自动识别当前打开的 Git 仓库，切换项目文件夹即可

## 🎉 开始使用

**现在就试试吧！**

1. 打开 `logisticsweb/src/views/userBase/waybillSettlement/edit.vue`
2. 查看每行代码的作者信息
3. 鼠标悬停查看提交详情
4. 点击打开 GitLens 侧边栏探索更多功能

**Happy Coding with GitLens Superpowers!** 🚀
