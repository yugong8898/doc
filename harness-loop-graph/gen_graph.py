#!/usr/bin/env python3
"""生成 WLYD Harness Loop Graph（Style 1 Flat Icon）。

布局：左侧 Graph 图谱 → 中央 5 节点闭环 → 右侧 Harness 驾驶舱 → 底部 Reflow 回流。
"""

OUT = '/Users/limengxiao/workspace/wlyd/docs/harness-loop-graph/harness-loop-graph.svg'

lines = []
A = lines.append

A('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 900" width="1280" height="900">')
A('  <style>')
A("    text { font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif; }")
A('  </style>')
A('  <defs>')
for cid, c in [('blue', '#2563eb'), ('orange', '#ea580c'), ('green', '#16a34a'), ('purple', '#9333ea')]:
    A('    <marker id="a-%s" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">' % cid)
    A('      <polygon points="0 0, 10 3.5, 0 7" fill="%s"/>' % c)
    A('    </marker>')
A('  </defs>')
A('  <rect width="1280" height="900" fill="#ffffff"/>')

# ---------- Title ----------
A('  <text x="40" y="46" font-size="20" font-weight="600" fill="#111827">WLYD Harness Loop Graph · 提效与质量闭环</text>')
A('  <text x="40" y="72" font-size="12" fill="#6b7280">Graph 决定改哪里 → Harness 机器验证结果 → Loop 负责回流与回退 · 对应 wlyd-workflow 阶段 0-6</text>')

# ---------- Graph container (left) ----------
A('  <rect x="40" y="110" width="300" height="330" rx="8" ry="8" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6,4"/>')
A('  <text x="56" y="138" font-size="13" font-weight="600" fill="#111827">Graph · 影响范围图谱（已具备）</text>')
graph_items = [
    ('.repoWiki/kb 逐文件索引', ['6000+ 文档 · L0-L5 分层']),
    ('maps/ 目录树快照', ['7 个项目 · 按服务拆分']),
    ('.sync-state.json 锚点', ['git 驱动增量发现变更']),
    ('gen_repo_wiki / gen_views', ['脚本重生成 + 回收漂移']),
]
gy = 156
for label, subs in graph_items:
    A('  <rect x="64" y="%d" width="252" height="58" rx="8" ry="8" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>' % gy)
    A('  <text x="78" y="%d" font-size="12" font-weight="600" fill="#1e3a8a">%s</text>' % (gy + 23, label))
    for i, s in enumerate(subs):
        A('  <text x="78" y="%d" font-size="10" fill="#6b7280">%s</text>' % (gy + 40 + i * 14, s))
    gy += 66

# ---------- Loop nodes (center) ----------
nodes = [
    (130, '① Retrieve · 检索上下文', '查库优先：kb 索引 → maps → 源码', '#eff6ff', '#2563eb', '#1e3a8a'),
    (235, '② Plan · 接单确认 + 改动清单', '横向搜索 9 宫格 · R-* 编号 · 待确认项', '#eff6ff', '#2563eb', '#1e3a8a'),
    (340, '③ Act · 最小改动执行', '旧逻辑注释保留 · 逐文件 ESLint', '#eff6ff', '#2563eb', '#1e3a8a'),
    (445, '④ Verify · 机器门禁', 'quick-verify / ESLint / tsc · exit≠0 不放行', '#fff7ed', '#ea580c', '#9a3412'),
    (550, '⑤ Learn · 回流沉淀', '坑点 / 规则 / CHANGELOG + 锚点回写', '#f0fdf4', '#16a34a', '#166534'),
]
for y, label, sub, fill, stroke, tfill in nodes:
    A('  <rect x="470" y="%d" width="340" height="64" rx="8" ry="8" fill="%s" stroke="%s" stroke-width="1.5"/>' % (y, fill, stroke))
    A('  <text x="640" y="%d" font-size="14" font-weight="600" fill="%s" text-anchor="middle">%s</text>' % (y + 27, tfill, label))
    A('  <text x="640" y="%d" font-size="11" fill="#6b7280" text-anchor="middle">%s</text>' % (y + 49, sub))

# ---------- Harness container (right) ----------
A('  <rect x="860" y="140" width="380" height="285" rx="8" ry="8" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6,4"/>')
A('  <text x="876" y="166" font-size="13" font-weight="600" fill="#111827">Harness · 验证驾驶舱</text>')
harness_items = [
    ('quick-verify.sh（已有）', 'git 状态 · console.log · 大文件'),
    ('ESLint（唯一机器 gate）', '改动后必跑，error 清零'),
    ('tsc --noEmit（待接）', '企服线 es-web / es-ops-platform'),
    ('影响范围 + 规则脚本（待建）', '多端矩阵 · /deep/ · BNumber 金额'),
]
hy = 180
for label, sub in harness_items:
    A('  <rect x="880" y="%d" width="340" height="56" rx="8" ry="8" fill="#f9fafb" stroke="#d1d5db" stroke-width="1.5"/>' % hy)
    A('  <text x="894" y="%d" font-size="12" font-weight="600" fill="#111827">%s</text>' % (hy + 22, label))
    A('  <text x="894" y="%d" font-size="10" fill="#6b7280">%s</text>' % (hy + 38, sub))
    hy += 60
# 门禁节点独立于容器外，保证 Verify 的水平箭头不穿越容器矩形
A('  <rect x="880" y="445" width="340" height="64" rx="8" ry="8" fill="#fff7ed" stroke="#ea580c" stroke-width="2"/>')
A('  <text x="1050" y="472" font-size="14" font-weight="600" fill="#9a3412" text-anchor="middle">阶段出口 exit-code 门禁</text>')
A('  <text x="1050" y="494" font-size="11" fill="#6b7280" text-anchor="middle">现状：AI 自述 → 建议：脚本判定</text>')

# ---------- Reflow band (bottom) ----------
A('  <rect x="40" y="660" width="780" height="160" rx="8" ry="8" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6,4"/>')
A('  <text x="56" y="688" font-size="13" font-weight="600" fill="#111827">Reflow · 回流沉淀（写回后闭环回 Graph）</text>')
reflow_items = [
    ('known-pitfalls.md', ['13 类高频坑', '编码前必检索']),
    ('rules SSOT（三端镜像）', ['接单确认 · 完成自检', '横向搜索 · 旧逻辑注释保留']),
    ('.repoWiki 回流', ['CHANGELOG + 锚点回写', '抽样验证 + 回收漂移']),
    ('自动回流（待建）', ['commit 钩子抽取候选坑点', '不再依赖人工喊话']),
]
rx = 62
for label, subs in reflow_items:
    A('  <rect x="%d" y="706" width="178" height="94" rx="8" ry="8" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>' % rx)
    A('  <text x="%d" y="730" font-size="12" font-weight="600" fill="#166534">%s</text>' % (rx + 14, label))
    for i, s in enumerate(subs):
        A('  <text x="%d" y="%d" font-size="10" fill="#6b7280">%s</text>' % (rx + 14, 748 + i * 14, s))
    rx += 192

# ---------- Pain callout ----------
A('  <rect x="860" y="530" width="380" height="140" rx="8" ry="8" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>')
A('  <text x="876" y="558" font-size="13" font-weight="600" fill="#991b1b">当前痛点：三者未接通</text>')
pains = [
    '① Graph 未接阶段1：改需求仍全仓读码',
    '② Harness 非门禁：验证通过靠 AI 自述',
    '③ Loop 静默死亡：C161 卡 2 个月无提醒',
    '④ 回流靠人喊：教训不自动进 rules/坑点',
]
py = 584
for p in pains:
    A('  <text x="876" y="%d" font-size="11" fill="#7f1d1d">%s</text>' % (py, p))
    py += 24

# ---------- Legend ----------
A('  <text x="876" y="714" font-size="12" font-weight="600" fill="#111827">图例</text>')
legend = [
    ('blue', 'solid', '主流程 ① → ⑤'),
    ('orange', 'solid', '控制 / 触发（调用 Harness 门禁）'),
    ('green', 'solid', '知识读取（先查库再读码）'),
    ('green', 'dash', '知识写回（回流沉淀）'),
    ('purple', 'solid', '反馈回退 / 下一轮循环'),
]
ly = 740
for cid, kind, label in legend:
    color = {'blue': '#2563eb', 'orange': '#ea580c', 'green': '#16a34a', 'purple': '#9333ea'}[cid]
    dash = ' stroke-dasharray="5,3"' if kind == 'dash' else ''
    A('  <line x1="886" y1="%d" x2="926" y2="%d" stroke="%s" stroke-width="1.5"%s marker-end="url(#a-%s)"/>' % (ly, ly, color, dash, cid))
    A('  <text x="936" y="%d" font-size="12" fill="#6b7280">%s</text>' % (ly + 4, label))
    ly += 26

# ---------- Arrows ----------
A('  <line x1="640" y1="194" x2="640" y2="231" stroke="#2563eb" stroke-width="1.5" marker-end="url(#a-blue)"/>')
A('  <line x1="640" y1="299" x2="640" y2="336" stroke="#2563eb" stroke-width="1.5" marker-end="url(#a-blue)"/>')
A('  <line x1="640" y1="404" x2="640" y2="441" stroke="#2563eb" stroke-width="1.5" marker-end="url(#a-blue)"/>')
A('  <line x1="640" y1="509" x2="640" y2="546" stroke="#2563eb" stroke-width="1.5" marker-end="url(#a-blue)"/>')
A('  <path d="M470,582 C406,582 406,150 470,150" stroke="#9333ea" stroke-width="1.5" fill="none" marker-end="url(#a-purple)"/>')
A('  <path d="M470,470 C348,460 348,384 470,372" stroke="#9333ea" stroke-width="1.5" fill="none" stroke-dasharray="5,3" marker-end="url(#a-purple)"/>')
A('  <path d="M340,190 L395,190 L395,182 L470,182" stroke="#16a34a" stroke-width="1.5" fill="none" marker-end="url(#a-green)"/>')
A('  <path d="M810,477 L876,477" stroke="#ea580c" stroke-width="1.5" fill="none" marker-end="url(#a-orange)"/>')
A('  <path d="M640,614 L640,656" stroke="#16a34a" stroke-width="1.5" fill="none" stroke-dasharray="5,3" marker-end="url(#a-green)"/>')
A('  <path d="M320,660 L320,444" stroke="#16a34a" stroke-width="1.5" fill="none" stroke-dasharray="5,3" marker-end="url(#a-green)"/>')

# ---------- Arrow labels ----------
A('  <text x="452" y="330" font-size="11" fill="#7e22ce" text-anchor="middle" transform="rotate(-90 452 330)">下一轮循环 · 阶段 N → N+1</text>')
A('  <text x="374" y="424" font-size="10" fill="#7e22ce" text-anchor="middle" transform="rotate(-90 374 424)">验证失败 → 修复 / 回退 ②</text>')
A('  <text x="432" y="172" font-size="10" fill="#15803d" text-anchor="middle">查库检索</text>')
A('  <text x="841" y="469" font-size="10" fill="#9a3412" text-anchor="middle">调用验证</text>')
A('  <text x="652" y="640" font-size="10" fill="#15803d">回流写回</text>')
A('  <text x="330" y="548" font-size="10" fill="#15803d">更新索引 / 写回锚点</text>')
A('</svg>')

with open(OUT, 'w') as f:
    f.write('\n'.join(lines))
print('SVG generated:', len(lines), 'lines ->', OUT)
