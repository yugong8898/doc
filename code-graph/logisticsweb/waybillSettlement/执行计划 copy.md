# 运单结算模块 — 可执行优化计划

> 原则：每个单元独立可测、改完即验、不影响其他模块。
> 来源整合自：优化方案.md + 业务维度优化方案.md

---

## 模块地图（先搞清楚在改什么）

```
waybillSettlement/
├── index.vue              列表页
├── edit.vue               调整结算页（核心，1846行，问题最集中）
├── read.vue               查看结算页（与 edit.vue 大量重复）
└── components/
    ├── CostMessageDetails.vue   费用明细
    ├── SettlementInfo.vue       结算信息表单
    ├── RiskWarningDialog.vue    风控弹窗
    ├── AnchorNav.vue            锚点导航
    └── add.conf.js              只有一个按钮配置（极小文件）
```

---

## 第一层：模块划分（大块）

edit.vue 里堆了 7 个业务模块，优先级和风险完全不同：

| 模块 | 当前位置 | 问题严重度 | 独立性 |
|------|---------|-----------|--------|
| A 保存/提交流程 | edit.vue methods | ⚠️ 有 3 个真实 bug | 高，只改 edit.vue |
| B 费用明细初始化 | CostMessageDetails.vue | ⚠️ 有 2 个潜在 bug | 高，只改该组件 |
| C 风控弹窗通信 | edit.vue + RiskWarningDialog | 可维护性差 | 中，涉及 2 个文件 |
| D 运单信息重复代码 | edit.vue + read.vue | 维护成本高 | 低，体量大需排期 |
| E 魔法数字常量化 | 散落 5 个文件 | 可读性差 | 高，新建文件不影响旧逻辑 |
| F 废代码清理 | edit.vue / read.vue | 低风险噪声 | 极高，随手可做 |

---

## 第二层：执行顺序（按人的操作逻辑排）

### 第 0 步 — 随手清理（不需要测试，30分钟内）

**做什么**：删掉确认没用的代码，降低后续阅读噪声。

| # | 文件 | 操作 |
|---|------|------|
| F1 | `read.vue` | 死条件 `:class` 改为静态 `class="blue pointer"` |
| F2 | `edit.vue` | 注释掉的 import（ImgPreview / LoseAndRiseViewText 等）确认废弃后删除 |
| F3 | `components/add.conf.js` | 只有一个按钮配置，内联到使用方，删除该文件 |

**收益**：减少阅读干扰，后续改动不会被这些"残留"误导。
**风险**：极低，纯删无用代码。
**验证**：页面正常打开即可。

---

### 第 1 步 — 建常量文件（不改任何业务逻辑，1小时内）

**做什么**：把散落在 5 个文件里的魔法数字集中到一个 `constants.js`，后续各模块按需引入。

**新建文件**：`src/views/userBase/waybillSettlement/constants.js`

```js
// 结算单状态
export const BUS_STATUS = {
  CHECK_FAILED:   '120',  // 审核不通过
  AFFIRM_BACK:    '210',  // 对账退回
  PENDING:        '300',  // 待处理
  SAVED:          '310',  // 已保存
  SETTLED:        '320',  // 结算通过
  PENDING_REVIEW: '330',  // 待预审
  REVIEW_FAILED:  '340'   // 预审不通过
}

export const EDITABLE_STATUS = ['120', '210', '300', '310', '340']

export const SETTLEMENT_FLAG = { NORMAL: '0', TRANSFER: '1', STOPPED: '2' }

export const ZERO_ORDER_NUMBER = { RECEIVABLE: 101, PAYABLE: 102 }

export const FIXED_DEDUCTION_CODE = { BY_RATIO: 'F10102', BY_AMOUNT: 'F10101' }

export const RISK_LEVEL = { LOW: '200', MIDDLE: '300', HIGH: '400' }

export const COST_TYPE = { PAYABLE: '200', OTHER_PAYABLE: '600' }
```

**先只在 `index.vue` 里引入并替换 `handleSelectable` 里的状态列表**，其他文件下次触碰时再迁移。

**收益**：状态值含义一眼可见，不再需要翻文档。
**风险**：极低，只新增文件 + 替换字面量，行为完全不变。
**验证**：`index.vue` 列表页，操作按钮显示/隐藏逻辑正常。

---

### 第 2 步 — 修复费用明细初始化（B 模块，仅改 CostMessageDetails.vue）

**做什么**：消除 `mounted` 和 `detailObj watch` 的双重初始化，修复两个 bug。

**修复的 bug**：
1. `mounted` 与 watch 对全流程运单的 `premiumAmount` 处理不一致，可能导致金额展示错误
2. `countMoney` 硬编码 `newList[0]`，`companyType=1` 时下标对应的是货物保障服务行而非运费差价行，会写错位置

**改动点**：
- 删除 `mounted` 里的 `newList` 初始化（约 50 行）
- `detailObj watch` 作为唯一入口，提取 `_buildNewList` / `_updateOilGasOnly` 两个方法
- `countMoney` 改为按 `costName` 查找目标行，不再用硬编码下标

**收益**：减少约 50 行重复代码，行为可预测，消除两个潜在展示 bug。
**风险**：中，需完整测试费用明细的展示场景。
**验证重点**：
```
□ 进页面：运费差价 / 货物保障 / 油气优惠三行正常展示
□ 全流程运单：货物保障服务金额显示 0
□ companyType=1（B1）：newList 只有货物保障服务行，无运费差价行
□ 修改确认金额：运费差价行联动更新
□ 保存后刷新：newList 正确重建，不残留旧值
```

---

### 第 3 步 — 拍平保存/提交流程（A 模块，仅改 edit.vue）

**做什么**：把 5 级调用链改成一个平铺的 `_executeFlow`，同时修复 3 个真实 bug。

**修复的 bug**：
1. 抹零弹窗取消后，已 push 进 `costNewList` 的抹零行没有清理，下次提交会重复计入
2. `riskManagement` 开头的防重 `if (this.btnLoading) return` 是死代码（进来之前 loading 已被重置为 false），永远不会触发
3. `handleSubmitRiskDialog` 里 `riskResult = null` 从未赋值，导致更详细的失败原因永远不展示

**目标结构**：
```
handleSave()   → _executeFlow('save')
handleSubmit() → _executeFlow('submit')

_executeFlow(action):
  1. 费用明细校验
  2. 货损确认校验
  3. 油气费校验
  4. 抹零处理（含弹窗，取消时清理已追加的行）
  5. 表单校验
  6. 运单状态校验（接口）
  7. 预保存（必须在风控前）
  8. 风控测算
  9. 正式提交
```

> 注意：步骤 7（预保存）不能和步骤 9 合并，风控接口依赖后端已固化的费用数据。

**收益**：新增/删除一个校验步骤只改 `_executeFlow` 里一行；`btnLoading` 重置统一到一处；消除 `.then()` 和 `async/await` 混用。
**风险**：中高，提交流程是核心链路，需完整回归。
**验证重点**：
```
□ 保存（310）：费用校验 → 油气校验 → 表单校验 → 接口，成功跳回列表
□ 提交（320）：全部校验 → 预保存 → 风控 → 正式提交
□ 任一校验失败：流程中止，loading 重置，可重试
□ 抹零弹窗取消：costNewList 不含抹零行，可重新保存
□ 低风险：跳过弹窗直接提交
□ 中高风险：弹窗 → 确认提交 or 展示失败原因
□ 风控接口报错：提示错误，loading 重置
```

---

### 第 4 步 — 风控弹窗通信方式改为 emit（C 模块，改 edit.vue + RiskWarningDialog.vue）

**做什么**：把 `provide/inject` 反向调用改成标准的 `$emit`。

**现状**：子组件通过 `inject` 拿到父组件方法并直接调用，数据流是向上的，追踪触发路径要跨文件找 inject 调用点。

**目标**：
```html
<RiskWarningDialog
  :visible.sync="riskWarningDialogVisible"
  @close="handleCloseRiskDialog"
  @submit="handleSubmitRiskDialog"
  @update="updateRiskWarning"
/>
```

**改动前需确认**：`RiskWarningDialog` 是否在其他地方（如 `index.vue`）也有使用，改动前要检查兼容性。

**收益**：数据流清晰，追踪路径从"跨文件 inject"缩短为"模板事件监听"。
**风险**：中，涉及公共组件，需确认使用方范围。
**验证重点**：
```
□ 中高风险弹窗正常弹出
□ 点击关闭：弹窗关闭，不提交
□ 点击确认且 allowPass='100'：继续提交
□ 点击确认且 allowPass 非 '100'：展示失败提示
□ index.vue 等其他使用方不受影响
```

---

### 第 5 步 — 提取共用逻辑（D 模块，体量最大，需单独排期）

**做什么**：消除 `edit.vue` 和 `read.vue` 约 430 行完全相同的代码。

**新建文件**：
- `useWaybillDetail.js`（mixin）：迁入 `getDetails` / `handleLookImg` / `getRecordPaging` / `loadStatusOption` / `handleViewCarInfo`
- `components/WaybillInfoTable.vue`：剥离运单信息表格模板

**改后文件体量预估**：

| 文件 | 当前 | 改后 |
|------|------|------|
| `edit.vue` | 1846 行 | ~900 行 |
| `read.vue` | ~1200 行 | ~400 行 |
| 新增 `useWaybillDetail.js` | — | ~200 行 |
| 新增 `WaybillInfoTable.vue` | — | ~180 行 |

**顺带修复**：`once` 标志位在 `$nextTick` 里重置不稳定的问题（改为所有异步步骤完成后再置 false）。

**收益**：接口字段变更从"同步两个文件"变为"改一处"。
**风险**：高，涉及核心数据加载方法，需完整回归两个页面。
**验证重点**：
```
□ edit.vue：详情回填正常，结算主体 / 银行卡 / 风控展示正确
□ read.vue：所有字段只读展示正常
□ 操作记录：createDate < 2024-02-01 时不加载
□ 运单信息表格：运单号跳转 / 附件查看 / 车辆监控均正常
□ 柜型柜数列（settlementType='20'）正确显示 / 隐藏
□ 两边 handleLookImg 均可正常弹出附件预览
```

---

## 汇总：执行顺序一览

```
第 0 步  废代码清理         随手，30min       极低风险
第 1 步  建 constants.js    1h，先只改 index  极低风险
第 2 步  CostMessageDetails 0.5d             中风险，独立可测
第 3 步  保存/提交流程拍平   1d               中高风险，核心链路
第 4 步  风控弹窗改 emit     0.5d             中风险，需确认使用方
第 5 步  提取共用逻辑        2d，单独排期      高风险，需完整回归
```

**不建议同时推进多个步骤**，每步完成后完整测试一遍再启动下一步。

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
