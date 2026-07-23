# 技术雷达关注主题与关键词

## 目录

- [一、主题分组](#一主题分组)
- [二、关键词清单](#二关键词清单)
- [三、优先级规则](#三优先级规则)
- [四、WLYD 适配判断维度](#四wlyd-适配判断维度)

## 一、主题分组

| 主题 | 关注点 | 优先级 |
|------|--------|--------|
| 前端工程化 | 构建、依赖、质量、自动化、CI、包管理 | 高 |
| Vue2 老项目维护 | Vue2 存量系统、Element UI、兼容性、迁移策略 | 高 |
| Vue3 | Composition API、生态迁移、组件库、性能 | 中 |
| React | React 生态、状态管理、工程实践、架构演进 | 中 |
| AI Coding | Cursor、Copilot、Claude Code、CodeBuddy、Qoder、AI Review | 高 |
| Agent / Prompt / Spec | Agent 工作流、Prompt 工程、规格驱动开发、Spec Kit | 高 |
| 知识库 / 文档 / 图谱 | Obsidian、代码知识图谱、文档自动生成、依赖图 | 高 |
| 前端埋点 | 事件采集、数据治理、无埋点、埋点校验 | 中 |
| 前端监控 / 可观测性 | 错误监控、性能监控、日志、Tracing、Session Replay | 高 |
| 测试 / 质量 / 安全 | E2E、单测、Lint、依赖安全、SAST | 中 |
| 开发工具链 | IDE、CLI、调试、依赖分析、自动化脚本 | 高 |

## 二、关键词清单

### 前端工程化

- frontend engineering
- web engineering
- Vite
- Rsbuild
- Rspack
- Webpack
- pnpm
- monorepo
- module federation
- micro frontend
- lint staged
- eslint
- dependency analysis

### Vue2 老项目维护

- Vue 2 maintenance
- Vue 2 migration
- Element UI
- Vue 2 legacy
- vue2 composition api
- sass migration
- node-sass dart-sass

### Vue3

- Vue 3
- Composition API
- Pinia
- Element Plus
- VueUse
- Vue Vapor
- Vue performance

### React

- React
- React Compiler
- Next.js
- React Server Components
- Zustand
- TanStack Query
- React performance

### AI Coding

- AI coding
- Cursor
- GitHub Copilot
- Claude Code
- Devin
- Code review agent
- AI code review
- AI pair programming

### Agent / Prompt / Spec

- AI Agent
- coding agent
- prompt engineering
- spec driven development
- OpenSpec
- spec-kit
- requirements engineering
- software design docs

### 知识库 / 文档 / 图谱

- Obsidian
- knowledge graph
- code graph
- Graphify
- madge
- dependency graph
- architecture diagram
- documentation automation

### 前端埋点

- frontend analytics
- web analytics
- tracking plan
- event tracking
- auto tracking
- analytics governance
- data quality

### 前端监控 / 可观测性

- frontend monitoring
- observability
- Sentry
- Datadog RUM
- OpenTelemetry frontend
- session replay
- web vitals
- error tracking
- performance monitoring

### 测试 / 质量 / 安全

- Playwright
- Cypress
- Vitest
- Jest
- visual regression
- dependency security
- supply chain security
- SAST frontend

### 开发工具链

- developer tools
- CLI tools
- dev workflow
- VS Code extension
- Cursor rules
- code search
- static analysis

## 三、优先级规则

高优先级内容满足任一条件即可进入精选候选：

1. 能直接改善 WLYD 当前 Vue2 + Element UI 项目维护效率。
2. 能降低需求分析、影响范围评估、代码审查、提测清单的遗漏概率。
3. 能补充 `.repoWiki/`、Skills、Prompts 或 AI 协作流程。
4. 能提升前端监控、埋点、错误定位、性能排查能力。
5. 工具轻量，能局部试用，不要求大规模重构。

中优先级内容仅在质量较高时保留：

1. Vue3 / React 新特性。
2. 行业趋势解读。
3. 大厂实践但需要改造后才能落地的方案。

低优先级内容一般不进入每日精选：

1. 纯概念介绍。
2. 与前端无直接关系。
3. 需要大规模平台化投入的重型工具。

## 四、WLYD 适配判断维度

每条信息进入文档时，应尽量判断：

- 是否适用于 Vue2 / Element UI / uni-app 存量项目。
- 是否能服务当前多子项目知识库和 AI 工作流。
- 是否能用小成本先试点。
- 是否会引入额外维护负担。
- 是否需要后端、测试、运维配合。
- 是否有明确来源、示例或官方文档。

---

**文档版本**: v1.0  
**最后更新**: 2026年07月  
**整理人**: 王新骏
