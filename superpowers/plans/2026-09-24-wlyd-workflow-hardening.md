# WLYD Workflow Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` (recommended) or `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `wlyd-workflow` 从依赖全局临时状态与暂存区的流程，升级为以需求目录为工作区、可在未暂存改动上验证、且能阻止“审查后变更未复审”漏检的闭环流程。

**Architecture:** 需求 PRD 目录成为唯一工作区，`workflow-state.md` 保存允许改动清单和阶段 4 的差异指纹。`quick-verify.sh` 接收显式 diff 范围和文件白名单，仅读取 Git 工作区并对实际受检文件执行静态检查。Skill、角色 Prompt 和当前规范文档共享同一套七阶段、复审失效与验证命令表述。

**Tech Stack:** Bash、Git、ESLint、Markdown、Cursor/Qoder/CodeBuddy/Trae 项目配置。

## Global Constraints

- 不修改 REQ-170 的既有需求产物、不修改业务代码、不自动 `git add`、不自动提交。
- `.md/temp/` 仅可作为一次性草稿区；不得再读写其下的 `workflow-state.md`。
- 以 `.cursor/skills/wlyd-workflow/` 为 Skill 唯一物理源；四端的 `skills` 软链应自动复用同一版本。
- 测试先行：先让回归用例针对当前脚本失败，再实现脚本，再运行同一用例转绿。
- 文档更新保留可追溯性，使用项目约定的目录、版本、日期与整理人信息。

## 目录

1. 建立可重复的脚本回归测试
2. 改造非暂存范围验证脚本
3. 加固 Workflow 状态与阶段门禁
4. 同步角色 Prompt 与当前规范文档
5. 执行压力场景与四端交付验证

---

## Task 1: 建立可重复的脚本回归测试

**Files:**
- Create: `.md/scripts/test-quick-verify.sh`
- Test target: `.md/scripts/quick-verify.sh`

- [ ] **Step 1: 写入失败基线测试，不改生产脚本。**

  测试脚本在 `mktemp -d` 创建独立 Git fixture，在其中复制当前 `quick-verify.sh`，通过可控的 `PATH` 注入 `npx` 替身，避免下载依赖或依赖真实 ESLint 配置。每个断言捕获退出码、输出和暂存区快照。

  覆盖以下可观察行为：

  1. 空的 `--scope unstaged` 必须非零退出，不能显示“通过”。
  2. 未暂存 Vue 文件中新加 `console.log` 时，`--scope unstaged` 必须失败，证明不再只看暂存区。
  3. `--allow-files src/a.vue` 与实际改动 `src/b.vue` 不一致时必须失败，并列出越界文件。
  4. `--files src/a.vue` 只允许选择改动集中的目标文件；不存在或不在当前 diff 中的文件必须失败。
  5. ESLint 调用必须带 `--no-ignore`；替身把完整参数写入日志，测试断言该参数存在。
  6. 执行前后 `git diff --cached --name-only` 字节一致，证明验证脚本没有暂存或写入 Git 索引。

- [ ] **Step 2: 先执行红灯。**

  Run: `bash .md/scripts/test-quick-verify.sh`

  Expected: 当前脚本至少因不支持 `--scope` / `--allow-files`、且空暂存 diff 误报通过而失败。保存失败摘要，仅作为改造依据，不修改 fixture 外的工作区。

## Task 2: 改造非暂存范围验证脚本

**Files:**
- Modify: `.md/scripts/quick-verify.sh`
- Test: `.md/scripts/test-quick-verify.sh`

- [ ] **Step 1: 实现参数与安全边界。**

  支持以下命令契约：

  ```bash
  bash .md/scripts/quick-verify.sh --scope unstaged
  bash .md/scripts/quick-verify.sh --scope staged
  bash .md/scripts/quick-verify.sh --scope both
  bash .md/scripts/quick-verify.sh --scope unstaged --files path/a.vue,path/b.ts
  bash .md/scripts/quick-verify.sh --scope unstaged --allow-files path/a.vue,path/b.ts
  ```

  默认 `--scope both`。使用 `git diff --name-only -z` 与 Bash 数组收集文件，保留含空格路径；`both` 去重。拒绝未知参数、空参数、未变化文件和不在所选 diff 范围内的 `--files` 项。`--allow-files` 对完整选中 diff 做集合比较，发现范围漂移时退出非零并打印越界路径。

- [ ] **Step 2: 保留并收紧现有检查。**

  在选中的真实文件集上运行：新增 `console.log` 检查、500KB 大文件检查、`git diff --check`、改动统计和 ESLint。ESLint 调用必须为 `npx eslint --no-ignore -- <files...>`，让原本被 ignore 的目标也显式接受校验；配置缺失或 lint 错误均为失败，不能静默绿灯。输出必须展示 `scope`、受检文件和统计，便于写入阶段记录。

  禁止加入 `git add`、`git restore`、`git commit` 或任何修改索引/工作区的命令。

- [ ] **Step 3: 运行回归测试直到转绿。**

  Run: `bash .md/scripts/test-quick-verify.sh`

  Expected: 六类断言全部通过；失败消息能定位到参数、范围、console、lint 或索引副作用。

- [ ] **Step 4: 审查脚本可移植性与用户现有改动。**

  Run: `bash -n .md/scripts/quick-verify.sh && git diff --check -- .md/scripts/quick-verify.sh .md/scripts/test-quick-verify.sh`

  Expected: Bash 语法正确、无空白错误；不修改仓库中现有业务 diff。

## Task 3: 加固 Workflow 状态与阶段门禁

**Files:**
- Modify: `.cursor/skills/wlyd-workflow/SKILL.md`
- Modify: `.md/prompts/role-workflow.md`

- [ ] **Step 1: 先建立 Skill 行为压力基线。**

  使用 REQ-170 的已知问题构造两组只读情境，要求执行者仅按现有 Workflow 文本回答：

  - 需求目录已有 `workflow-state.md`，而 `.md/temp/workflow-state.md` 是 C161 的旧状态；
  - 阶段 4 审查完成后又修改了 Vue 模板，并且用户明确不允许暂存。

  记录旧文本是否仍会读取全局状态、要求 `git add` 或允许直接进入阶段 5；这些就是后续行为验收的红灯基线。

- [ ] **Step 2: 修改 Skill 的状态解析与状态模板。**

  将“需求 PRD 所在目录”明确为唯一工作区。新建流程先创建 `需求目录/workflow-state.md`；继续流程在用户给出需求编号/路径时只读取该目录。若用户只说“继续”，仅列出候选需求目录、要求用户选择，绝不自动沿用 `.md/temp/workflow-state.md`。

  状态模板新增：`工作区`、`阶段 3 允许改动文件`、`阶段 4 审查差异 SHA-256 指纹`、`复审失效原因`。历史全局状态仅作为人工可迁移来源：展示来源和目标，得到确认后复制为需求目录状态；不覆盖任何已有需求状态。

- [ ] **Step 3: 固化阶段 3/4/6 的验证与复审规则。**

  阶段 3 先把技术方案的最小文件集写入状态，再执行：

  ```bash
  bash .md/scripts/quick-verify.sh --scope unstaged --allow-files <方案文件清单>
  ```

  阶段 4 的审查记录必须保存完整 diff 的 SHA-256 指纹和实际受检文件。阶段 4 后如代码 diff 变化，立即将阶段 4 标记为失效，禁止进入阶段 5/6，必须重新审查并重跑门禁。只因补充文档、但没有业务代码 diff 变化时，须在状态中说明判定依据。

- [ ] **Step 4: 增加 Vue SFC 审查完整性规则。**

  审查范围必须包含原始完整 `template`，包括注释、`KeepAlive`、动态组件/动态插槽、条件分支和布局结构；不得只抽取“改动附近模板”。任何模板编译风险一律 P0，未确认前不能通过阶段 4。

- [ ] **Step 5: 将角色 Prompt 对齐为同一七阶段协议。**

  `role-workflow.md` 更新为 Skill 同步的阶段 0–6、状态目录、非暂存验证、最小文件集、diff 指纹和复审失效规则。删除“必须先 stage”的措辞；保留当前 Stall 检测和角色文件加载说明，但不再让它们引用全局临时状态。

## Task 4: 同步当前规范文档

**Files:**
- Modify: `docs/wlyd-workflow-upgrade/README.md`
- Modify: `docs/wlyd-workflow-upgrade/01-总体方案.md`
- Modify: `docs/wlyd-workflow-upgrade/02-7阶段流程设计.md`
- Modify: `docs/wlyd-workflow-upgrade/03-统一验证协议.md`
- Modify: `docs/wlyd-workflow-upgrade/05-变更回退机制.md`
- Modify: `docs/wlyd-workflow-upgrade/07-最终交付门禁.md`
- Modify: `docs/wlyd-workflow-upgrade/11-如何提升开发效率.md`
- Modify: `docs/wlyd-workflow-upgrade/12-开发实战SOP.md`

- [ ] **Step 1: 先检索当前规范性表述。**

  Run: `rg -n "\.md/temp/workflow-state|git add -A|git diff --cached|quick-verify" docs/wlyd-workflow-upgrade .md/prompts/role-workflow.md .cursor/skills/wlyd-workflow/SKILL.md`

  Expected: 按文件逐项分类为“当前规范”与“历史记录”。只更新当前规范文档；路线图、实施进度等历史记录保留其当时语义，必要时加“历史记录”说明，不伪造历史。

- [ ] **Step 2: 更新当前规范。**

  把需求目录工作区、状态字段、`--scope`/`--files`/`--allow-files`、真实受检文件输出、无暂存副作用、差异指纹与复审失效、完整 SFC 审查写入上述文档。更新目录链接、版本和页脚；不加入估时。

- [ ] **Step 3: 进行文档一致性检查。**

  Run: `rg -n "\.md/temp/workflow-state|git add -A && bash \.md/scripts/quick-verify\.sh|只扫描 `git diff --cached`" .cursor/skills/wlyd-workflow/SKILL.md .md/prompts/role-workflow.md docs/wlyd-workflow-upgrade`

  Expected: 当前规范文件不再出现已废弃流程；如历史文档仍保留旧命令，必须紧邻历史说明，不能被误解为现行规则。

## Task 5: 执行压力场景与四端交付验证

**Files:**
- Verify: `.cursor/skills/wlyd-workflow/SKILL.md`
- Verify symlinks: `.qoder/skills`, `.codebuddy/skills`, `.trae/skills`
- Verify: `.md/prompts/role-workflow.md`, `.trae/prompts`

- [ ] **Step 1: 重放两组 Workflow 压力情境。**

  对第 3 节相同情境执行修订后的 Workflow：必须选择需求目录状态、将旧全局状态视为待确认迁移源、使用 `--scope unstaged`，并在阶段 4 后代码变化时阻止阶段 5/6、要求重新审查。记录结果与基线对比。

- [ ] **Step 2: 验证软链和 Prompt 同步路径。**

  Run: `readlink .qoder/skills && readlink .codebuddy/skills && readlink .trae/skills && readlink .trae/prompts`

  Expected: 三个 Skill 目录都解析到 `.cursor/skills`，Trae Prompt 解析到 `.md/prompts`；因此本轮 Skill/Prompt 更新无需复制多份内容。

- [ ] **Step 3: 最终验证并报告边界。**

  Run:

  ```bash
  bash .md/scripts/test-quick-verify.sh
  bash -n .md/scripts/quick-verify.sh
  git diff --check -- .md/scripts/quick-verify.sh .md/scripts/test-quick-verify.sh \
    .cursor/skills/wlyd-workflow/SKILL.md .md/prompts/role-workflow.md docs/wlyd-workflow-upgrade
  ```

  Expected: 回归测试、语法检查、差异空白检查通过。最终报告列出变更文件、未改动的 REQ-170 历史产物、未执行的 `git add`/提交，以及若需在各 IDE 图形界面确认的手动项。

---

文档版本：v1.0  
更新日期：2026年09月  
整理人：王新骏
