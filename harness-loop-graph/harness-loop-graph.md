# WLYD Harness Loop Graph · 提效与质量闭环

> Graph 决定改哪里 → Harness 机器验证结果 → Loop 负责回流与回退 · 对应 `wlyd-workflow` 阶段 0-6
>
> 渲染方式：IDE 装 Mermaid 插件直接预览；也可贴入 `mermaid.live`、或放进 Obsidian 任意 `.md`。

## 图

```mermaid
flowchart TB

    %% ================= Graph：影响范围图谱 =================
    subgraph GRAPH["Graph · 影响范围图谱（已具备）"]
        direction TB
        G1[".repoWiki/kb 逐文件索引<br/>6000+ 文档 · L0-L5 分层"]
        G2["maps/ 目录树快照<br/>7 个项目 · 按服务拆分"]
        G3[".sync-state.json 锚点<br/>git 驱动增量发现变更"]
        G4["gen_repo_wiki / gen_views<br/>脚本重生成 + 回收漂移"]
    end

    %% ================= Harness：验证驾驶舱 =================
    subgraph HARNESS["Harness · 验证驾驶舱"]
        direction TB
        H1["quick-verify.sh（已有）<br/>git 状态 · console.log · 大文件"]
        H2["ESLint（唯一机器 gate）<br/>改动后必跑，error 清零"]
        H3["tsc --noEmit（待接）<br/>企服线 es-web / es-ops-platform"]
        H4["影响范围 + 规则脚本（待建）<br/>多端矩阵 · 禁用深层选择器 · BNumber 金额"]
    end

    GATE{{"阶段出口 exit-code 门禁<br/>现状：AI 自述 → 建议：脚本判定"}}

    %% ================= Reflow：回流沉淀 =================
    subgraph REFLOW["Reflow · 回流沉淀"]
        direction TB
        R1["known-pitfalls.md<br/>13 类高频坑 · 编码前必检索"]
        R2["rules SSOT（三端镜像）<br/>接单确认 · 完成自检 · 横向搜索"]
        R3[".repoWiki 回流<br/>CHANGELOG + 锚点回写"]
        R4["自动回流（待建）<br/>commit 钩子抽取候选坑点"]
    end

    %% ================= Loop：五节点闭环 =================
    RET["① Retrieve · 检索上下文<br/>查库优先：kb 索引 → maps → 源码"]
    PLAN["② Plan · 接单确认 + 改动清单<br/>横向搜索 9 宫格 · R-* 编号 · 待确认项"]
    ACT["③ Act · 最小改动执行<br/>旧逻辑注释保留 · 逐文件 ESLint"]
    VER["④ Verify · 机器门禁<br/>quick-verify / ESLint / tsc · exit≠0 不放行"]
    LRN["⑤ Learn · 回流沉淀<br/>坑点 / 规则 / CHANGELOG + 锚点回写"]

    %% ================= 主流程 =================
    RET --> PLAN --> ACT --> VER --> LRN

    %% ================= 循环 / 回退 / 读写 =================
    LRN ==>|"下一轮循环 · 阶段 N → N+1"| RET
    VER -.->|"验证失败 → 修复 / 回退 ②"| PLAN
    G1 -->|"知识读取（查库检索）"| RET
    VER -->|"调用验证"| GATE
    GATE -.-> HARNESS
    LRN -.->|"回流写回"| REFLOW
    REFLOW -.->|"更新索引 / 写回锚点"| GRAPH

    %% ================= 痛点 =================
    PAIN["⚠ 当前痛点：三者未接通<br/>① Graph 未接阶段1：改需求仍全仓读码<br/>② Harness 非门禁：验证通过靠 AI 自述<br/>③ Loop 静默死亡：C161 卡 2 个月无提醒<br/>④ 回流靠人喊：教训不自动进 rules / 坑点"]

    classDef blue fill:#eff6ff,stroke:#2563eb,color:#1e3a8a
    classDef orange fill:#fff7ed,stroke:#ea580c,color:#9a3412
    classDef green fill:#f0fdf4,stroke:#16a34a,color:#166534
    classDef gray fill:#f9fafb,stroke:#d1d5db,color:#111827
    classDef pain fill:#fef2f2,stroke:#dc2626,color:#991b1b

    class RET,PLAN,ACT blue
    class VER,GATE orange
    class LRN,R1,R2,R3,R4 green
    class G1,G2,G3,G4,H1,H2,H3,H4 gray
    class PAIN pain
```

## 图例

- **蓝色实线**：主流程 ① → ⑤（Retrieve → Plan → Act → Verify → Learn）
- **橙色实线**：控制 / 触发 —— ④ Verify 调用 Harness 门禁
- **绿色实线**：知识读取 —— Graph 汇入 ① Retrieve（先查库再读码）
- **绿色虚线**：知识写回 —— ⑤ Learn → Reflow → Graph，形成闭环
- **紫色粗箭头**：下一轮循环（阶段 N → N+1）
- **紫色虚线**：验证失败 → 修复 / 回退到 ② Plan

---

**文档版本**：v1.0
**最后更新**：2026年09月
**整理人**：王新骏
