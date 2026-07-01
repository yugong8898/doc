# Cursor MCP Plugins 使用指南

## 📋 已安装插件清单

### 1. GitKraken (GitLens Extension) ✅ 可用

**状态**: 正常运行

**核心功能**:

#### Git 操作工具
- `git_status` - 查看工作区状态
- `git_add_or_commit` - 添加和提交代码
- `git_branch` - 分支管理
- `git_checkout` - 切换分支/标签
- `git_fetch` / `git_pull` / `git_push` - 远程同步
- `git_stash` - 暂存工作进度
- `git_log_or_diff` - 查看提交历史和差异
- `git_blame` - 查看代码责任人
- `git_graph` - 可视化分支图
- `git_worktree` - 工作树管理

#### 代码协作工具
- `pull_request_*` - PR 创建、查看、评审
- `issues_*` - Issue 管理、创建、评论
- `gitlens_commit_composer` - 智能提交信息生成
- `gitlens_launchpad` - 启动工作流
- `gitlens_start_work` / `gitlens_start_review` - 开始工作/评审

#### 仓库工具
- `repository_get_file_content` - 获取远程文件内容
- `gitkraken_workspace_list` - 工作区列表

**使用场景**:
- Git 操作自动化（查看状态、提交代码、分支管理）
- 代码审查和 PR 管理
- Issue 跟踪和协作
- 生成符合规范的 commit 信息（配合 `.cursorrules` 规则）

---

### 2. Notion Workspace ⚠️ 需要认证

**状态**: 未认证，需要授权才能使用

**预期功能**:
- 读取 Notion 页面和数据库
- 创建和更新 Notion 文档
- 查询和管理工作空间内容
- 同步项目文档
- 与团队协作

**使用场景**:
- 同步项目文档到 Notion
- 从 Notion 读取需求和任务
- 自动化文档管理和更新
- 项目知识库管理

**激活方式**: 
```
需要在 Cursor 中调用 mcp_auth 工具进行 OAuth 认证
```

---

### 3. Figma ⚠️ 需要认证

**状态**: 未认证，需要授权才能使用

**预期功能**:
- 读取 Figma 设计稿
- 获取设计规范（颜色、字体、间距）
- 导出设计资源
- 查看组件和样式
- 设计系统同步

**使用场景**:
- 根据 Figma 设计稿生成代码
- 同步设计系统到代码
- 自动化 UI 开发流程
- 提取设计 Token（颜色、字体等）

**激活方式**: 
```
需要在 Cursor 中调用 mcp_auth 工具进行 OAuth 认证
```

---

### 4. Datadog ❌ 错误状态

**状态**: 服务错误，无法正常使用

**预期功能**:
- 查询应用性能指标
- 监控日志和错误
- 查看服务健康状态
- 分析性能数据
- 告警信息查询

**使用场景**:
- 排查生产环境问题
- 性能优化分析
- 监控告警查询
- 日志分析和调试

**问题**: 该服务当前处于错误状态

**解决方案**: 
```
在 Cursor 设置中检查 MCP 服务器状态
可能需要重新配置或更新服务器连接信息
```

---

## 🎯 使用优先级建议

### 立即可用（推荐）
1. **GitKraken** - 完全可用，功能强大
   - 配合 WLYD 项目的 Git 提交规范使用
   - 自动生成符合格式的 commit 信息
   - 简化分支管理和代码审查流程

### 值得激活
2. **Notion** - 文档管理利器
   - 适合团队知识库管理
   - 需求文档同步
   - 项目文档自动化

3. **Figma** - 前端开发加速器
   - UI 开发自动化
   - 设计规范同步
   - 组件代码生成

### 待修复
4. **Datadog** - 生产环境监控
   - 修复连接问题后非常有用
   - 适合排查线上问题

---

## 💡 与 WLYD 项目的结合建议

### 1. GitKraken + Commit 规范

根据 `.cursorrules` 中的规则，使用 GitKraken 自动生成符合规范的提交信息：

**提交类型**：
```
feat: 新功能
fix: 修复 bug
refactor: 重构代码
style: 样式调整
docs: 文档更新
perf: 性能优化
test: 测试相关
chore: 构建/工具相关
```

**使用方式**：
```
让 AI 使用 gitlens_commit_composer 工具
自动分析改动并生成规范的提交信息
```

### 2. GitKraken + 代码审查流程

**标准工作流**：
```
1. git_status - 查看当前改动
2. git_add_or_commit - 暂存和提交代码
3. git_push - 推送到远程仓库
4. pull_request_create - 创建 PR
5. gitlens_start_review - 发起代码审查
```

### 3. Notion + 文档规范

激活后可以：
- 自动在 Notion 中创建符合规范的文档
- 文档版本自动管理（v1.0, v1.1...）
- 自动添加文档信息（整理人：王新骏）

### 4. Figma + uni-app 开发

激活后可以：
- 根据 Figma 设计生成 uni-app 组件
- 自动适配 rpx 单位
- 生成符合条件编译规范的代码

---

## 🚀 快速开始

### 激活 Notion

1. 告诉 AI："帮我激活 Notion MCP 服务器"
2. AI 会调用 `mcp_auth` 工具
3. 在浏览器中完成 OAuth 授权
4. 返回 Cursor 即可使用

### 激活 Figma

1. 告诉 AI："帮我激活 Figma MCP 服务器"
2. AI 会调用 `mcp_auth` 工具
3. 在浏览器中完成 OAuth 授权
4. 返回 Cursor 即可使用

### 使用 GitKraken

直接使用，无需额外配置：

**示例指令**：
```
"查看当前仓库状态"
"帮我生成一个符合规范的 commit 信息"
"创建一个新分支 feature/xxx"
"推送到远程仓库"
"查看最近的提交历史"
```

---

## 📚 常见使用场景

### 场景1：规范化提交代码

**需求**: 修改了多个文件，需要规范提交

**操作流程**：
```
1. 告诉 AI："查看当前改动"
   → AI 调用 git_status

2. 告诉 AI："帮我生成 commit 信息"
   → AI 调用 gitlens_commit_composer
   → 自动分析改动，生成符合 feat:/fix: 等格式的信息

3. 告诉 AI："提交代码"
   → AI 调用 git_add_or_commit
```

### 场景2：创建 PR 并发起评审

**需求**: 功能开发完成，需要创建 PR

**操作流程**：
```
1. "推送代码到远程"
   → git_push

2. "创建 PR"
   → pull_request_create

3. "发起代码评审"
   → gitlens_start_review
```

### 场景3：查看代码历史

**需求**: 查看某个文件的修改历史

**操作流程**：
```
1. "查看 xxx.vue 的修改历史"
   → git_log_or_diff

2. "查看某行代码是谁写的"
   → git_blame
```

### 场景4：分支管理

**需求**: 创建新分支开发功能

**操作流程**：
```
1. "创建并切换到新分支 feature/xxx"
   → git_branch + git_checkout

2. 开发完成后："合并到主分支"
   → git_checkout + git_merge
```

---

## 🔧 高级技巧

### 1. 批量操作

**同时查看多个信息**：
```
"显示当前状态、最近提交和分支列表"
→ AI 会并行调用多个工具
```

### 2. 智能提交

**让 AI 分析改动类型**：
```
"根据我的改动生成合适的 commit 类型"
→ AI 会智能判断是 feat、fix 还是 refactor
```

### 3. 工作流自动化

**完整的开发流程**：
```
"帮我完成以下流程：
1. 查看改动
2. 生成 commit
3. 提交并推送
4. 创建 PR"

→ AI 会按顺序执行所有操作
```

---

## ⚠️ 注意事项

### Git 操作注意

1. **敏感操作确认**
   - 推送代码前会提示确认
   - 删除分支等危险操作会二次确认

2. **多人协作**
   - 推送前先拉取最新代码
   - 避免直接在主分支提交

3. **提交规范**
   - 严格遵守项目的 commit 格式
   - 提交信息要清晰描述改动

### 认证相关

1. **Token 安全**
   - OAuth Token 存储在本地
   - 定期检查授权状态

2. **权限控制**
   - 只授予必要的权限
   - 定期审查已授权的应用

---

## 🆘 故障排查

### GitKraken 无法使用

**问题**: 工具调用失败

**解决方案**：
```
1. 检查 MCP 服务器状态
2. 重启 Cursor
3. 检查仓库是否是 Git 仓库
```

### Notion/Figma 认证失败

**问题**: OAuth 认证无法完成

**解决方案**：
```
1. 检查网络连接
2. 确认账号权限
3. 清除浏览器缓存后重试
4. 检查 Cursor 设置中的 MCP 配置
```

### Datadog 连接错误

**问题**: 服务器状态显示错误

**解决方案**：
```
1. 检查 API Key 配置
2. 验证 Datadog 账号状态
3. 查看 Cursor 日志
4. 联系管理员检查服务器配置
```

---

## 📖 相关文档

- [GitLens 快速上手指南](./GitLens-快速上手指南.md)
- [Cursor Superpowers 完整指南](./superpowers-complete-guide.md)
- [项目 .cursorrules 规则](../.cursorrules)

---

**文档版本**: v1.0
**最后更新**: 2026年06月
**整理人**: 王新骏
