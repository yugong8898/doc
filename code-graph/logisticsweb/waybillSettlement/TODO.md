# 司机对账 & 运单结算 — 可执行优化 TODO LIST

> 原则：每一步独立可验证，做完一步测一遍再做下一步。不要同时改多个文件。
>
> 状态标记：⬜ 待执行 / 🔄 进行中 / ✅ 已完成

---

## 第一阶段：BUG 修复（最高优先级，影响用户）

### DC-B1 — `driverChecking/add.format.js`：`$total` 直接操作响应式数组

**问题**：`$total()` 在方法内直接 `pop()` 和 `push()` 操作 `bmsBusinessCostList`，每次调用都修改同一个数组，重复调用会导致小计/合计行叠加。

**处理文件**：`add.format.js`

**操作**：在 `$total` 方法开头用 `specialRowType` 过滤掉已有的汇总行，再追加，避免重复：
```js
// 先移除已有的特殊行（小计/运费差价/货物保障/油气优惠/合计等）
this.reseponse.model.bmsBusinessCostList = this.reseponse.model.bmsBusinessCostList.filter(
  item => !item.specialRowType
)
```

**影响范围**：`add.vue` 的费用表格展示（read / verify / check 三种 action）

**验证**：
- [ ] 进入详情页，费用表格只有一行小计、一行合计，不重复
- [ ] 切换 tab 或刷新后小计行不叠加
- [ ] read / verify / check 三种 action 均正常

**状态**：⬜

---

### DC-B2 — `driverChecking/index.format.js`：`codeFormat` 找不到匹配项时返回 undefined

**问题**：`codeFormat` 方法在 switch 没有匹配到任何 case 时，直接走到底，`options` 未定义就执行 `options?.find(...)`，返回 `undefined`，调用方拿到 `undefined` 渲染成空白。

**处理文件**：`index.format.js`

**操作**：在方法末尾加兜底 return：
```js
// 方法末尾，find 之前
const option = options?.find(item => item.code === (Number.isNaN(+code) ? code : +code))
return option ? option.text : '--'  // 改：原来是 undefined，现在兜底返回 '--'
```

**影响范围**：列表页所有通过 `codeFormat` 格式化的列（运输类型、状态、柜型、货运类型、车辆类型）

**验证**：
- [ ] 列表中运输类型/柜型等列无空白单元格，无匹配时显示 `--`

**状态**：⬜

---

## 第二阶段：P0 清理（随手可做，各项独立互不影响）

### DC-1 — `driverChecking/add.format.js`：删除 `$otherKuiTonsRatio` 中废弃注释

**问题**：方法内 `return` 后跟着一大段注释掉的旧计算逻辑（约 8 行），已由后端字段 `kuiTonsSituationVO.lossType` 替代。

**处理文件**：`add.format.js`

**操作**：确认 `kuiTonsSituationVO.lossType` 已稳定上线后，删除 `return` 后的注释块。

**影响范围**：仅文件可读性，无业务影响

**验证**：
- [ ] 文件语法正常，亏涨吨情况列展示不变

**状态**：⬜

---

### DC-2 — `driverChecking/add.format.js`：删除 `$all` 方法末尾废弃注释

**问题**：`$all` 方法体只有一行 `return parsePrice(row.amountsPayable)`，但后面跟着一行注释掉的旧计算逻辑，已由后端字段 `amountsPayable` 替代。

**处理文件**：`add.format.js`

**操作**：删除注释行。

**影响范围**：仅文件可读性，无业务影响

**验证**：
- [ ] 文件语法正常

**状态**：⬜

---

### DC-3 — `driverChecking/index.conf.js`：删除整段 `buttonAct` 注释

**问题**：`index.conf.js` 中 `buttonAct` 整段被注释掉（费用说明、导出、对账确认、下载对账单四个按钮），无废弃说明。经确认按钮已迁移到 `index.vue` 模板的 `#bar` slot 里直接写。

**处理文件**：`index.conf.js`

**操作**：删除整段 `buttonAct` 注释（约 8 行）。

**影响范围**：仅文件可读性，无业务影响

**验证**：
- [ ] 列表页顶部按钮区域展示正常（费用说明、导出、批量确认、批量不通过）

**状态**：⬜

---

### DC-4 — `driverChecking/add.format.js`：合并重复的 `formatTableFilse` / `formatResultFilse`

**问题**：两个方法实现完全相同（都是把 attachmentName/attachmentUrl 映射为 name/url），名字略有不同，调用方各自引用其中一个。

**处理文件**：`add.format.js`

**操作**：
1. 保留 `formatTableFilse`，改名为 `formatAttachmentList`
2. 删除 `formatResultFilse`
3. 搜索 `add.vue` 中所有调用 `formatResultFilse` 的地方，替换为 `formatAttachmentList`

**影响范围**：`add.vue` 中附件列展示

**验证**：
- [ ] verify / check / read 三种 action 下附件列正常显示

**状态**：⬜

---

### DC-5 — `driverChecking/add.format.js`：合并 `codeFormat` 中 `reviewResult` / `rReviewResult` 重复 case

**问题**：`codeFormat` 的 switch 里 `reviewResult` 和 `rReviewResult` 两个 case 返回完全相同的数组 `[{code:10,'通过'},{code:20,'不通过'}]`，重复定义。

**处理文件**：`add.format.js`

**操作**：将两个 case 合并，利用 fall through：
```js
case 'reviewResult':
case 'rReviewResult':
  options = [{ code: 10, text: '通过' }, { code: 20, text: '不通过' }]
  break
```

**影响范围**：`add.vue` 操作记录表格中审核结果列格式化

**验证**：
- [ ] 审核结果列正常显示"通过"/"不通过"

**状态**：⬜

---

### DC-6 — `driverChecking/index.format.js`：合并 `getTransportName` 中 case 1/2/3

**问题**：`getTransportName` 的 switch 里 case 1、case 2、case 3 三个分支都返回 `'highway'`，可以合并。（`add.format.js` 里也有相同的重复，一并处理。）

**处理文件**：`index.format.js`、`add.format.js`

**操作**：
```js
case 1:
case 2:
case 3:
  return 'highway'
```

**影响范围**：仅代码可读性，运输类型名称映射结果不变

**验证**：
- [ ] 公路运单跳转详情页路由正常

**状态**：⬜

---

## 第三阶段：新建常量文件（建完再逐文件替换）

### DC-CONST-1 — 新建 `driverChecking/constants.js`

**问题**：`busStatus`、`freightType`、`costType` 等状态值裸写在多个文件里，含义不明。

**处理文件**：新建 `src/views/userBase/driverChecking/constants.js`

**操作**：创建文件，内容如下：
```js
// 账单状态
export const BUS_STATUS = {
  PENDING_VERIFY:  100,  // 待核对
  PENDING_CHECK:   110,  // 待审核
  PROCESSING:      115,  // 处理中
  CHECK_FAILED:    120,  // 审核不通过
  CHECK_PASSED:    130,  // 审核通过
  PENDING_AFFIRM:  200,  // 待对账
  AFFIRM_BACK:     210,  // 对账退回
  AFFIRM_PASSED:   220   // 对账通过
}

// 批量确认有效状态
export const BATCH_AFFIRM_VALID_STATUS = ['110', '130', '200']

// 批量不通过有效状态
export const BATCH_DIS_PASS_VALID_STATUS = ['110']

// 费用类型（应付/其他应付）
export const COST_TYPE = { PAYABLE: '200', OTHER_PAYABLE: '600' }

// 货运类型
export const FREIGHT_TYPE = { TRADITIONAL: '1', NETWORK: '2' }

// 操作 action 类型
export const ACTION_MODE = { READ: 'read', VERIFY: 'verify', CHECK: 'check' }
```

**影响范围**：仅新增文件，无业务影响

**验证**：
- [ ] 文件可被正常 import，无语法错误

**状态**：⬜

---

### DC-CONST-2 — `driverChecking/index.format.js` 引入常量

**依赖**：DC-CONST-1 完成后执行

**处理文件**：`index.format.js`

**操作**：
1. 顶部引入 `import { BUS_STATUS } from './constants'`
2. `$action` 方法的 switch/case 里将裸数字替换为常量，或改为 `ACTION_MAP` 对象映射：
```js
const ACTION_MAP = {
  [BUS_STATUS.PENDING_VERIFY]: { read: true, verify: true, check: false, giveBack: false, bill: false, affirm: false },
  [BUS_STATUS.PENDING_CHECK]:  { read: true, verify: false, check: true, ... },
  // ...
}
return (ACTION_MAP[+row.busStatus] || { read: false, ... })[action]
```

**影响范围**：列表页操作按钮显示逻辑

**验证**：
- [ ] 各状态下查看/核对/审核/退回/推送/对账确认按钮显示正确

**状态**：⬜

---

### DC-CONST-3 — `driverChecking/index.vue` 引入常量

**依赖**：DC-CONST-1 完成后执行

**处理文件**：`index.vue`

**操作**：
1. 顶部引入 `import { BATCH_AFFIRM_VALID_STATUS, BATCH_DIS_PASS_VALID_STATUS } from './constants'`
2. `batchAffirm` 方法里的 `['110', '130', '200']` 替换为 `BATCH_AFFIRM_VALID_STATUS`
3. `handleBatchDisPass` / `batchDisPassFn` 里的 `['110']` 替换为 `BATCH_DIS_PASS_VALID_STATUS`

**影响范围**：批量确认、批量不通过按钮逻辑

**验证**：
- [ ] 批量确认：只有待审核/审核通过/待对账的运单参与
- [ ] 批量不通过：只有待审核的运单参与
- [ ] 部分符合时弹出提示，全部不符合时显示全部不符合提示

**状态**：⬜

---

### DC-CONST-4 — `driverChecking/add.format.js` 引入常量

**依赖**：DC-CONST-1 完成后执行

**处理文件**：`add.format.js`

**操作**：
1. 引入 `import { COST_TYPE, ACTION_MODE } from './constants'`
2. `$total` 里 `['200', '600'].includes(...)` 替换为 `[COST_TYPE.PAYABLE, COST_TYPE.OTHER_PAYABLE].includes(...)`
3. `$total` 里 `this.$route.params.action === 'check' || this.$route.params.action === 'read'` 替换为常量

**影响范围**：费用表格汇总行计算逻辑

**验证**：
- [ ] check / read action 下小计/合计行金额正确

**状态**：⬜

---

## 第四阶段：P1 重构（触碰该文件时顺手做）

### DC-P1-1 — `add.format.js`：提取 `$total` 的汇总行构建为子方法

**问题**：`$total` 方法体约 80 行，直接操作响应式数组，各种特殊行（小计/运费差价/货物保障/油气优惠/合计）混在一起，难以维护。

**处理文件**：`add.format.js`

**操作**：提取以下子方法，`$total` 改为依次调用：
```js
_calcSubtotal(list)          // → { costName, $adjustCost }，纯计算，不操作数组
_appendSubtotalRow(data)     // 追加小计行
_appendFreightDiffRow()      // 追加运费差价行（companyType !== 1）
_appendInsuranceRow()        // 追加货物保障服务行（premiumBuyerType === '10'）
_appendOilDiscountRow()      // 追加油气优惠行
_appendTotalRow()            // 追加合计行（companyType !== 1）
_appendFullProcessRows()     // 追加全流程专属行（fpDiff / shipperPay / carrierPay）
```

**影响范围**：`add.vue` 费用表格展示（read / verify / check）

**验证**：
- [ ] 普通运单：小计行 + 合计行正常
- [ ] 全流程运单：油气优惠行 + fpDiff行 + shipperPay/carrierPay行正常
- [ ] companyType=1（B1公司）：不显示运费差价行和合计行

**状态**：⬜

---

### DC-P1-2 — `add.format.js`：`$total` 改为先清理特殊行再追加

**依赖**：DC-B1 已修复

**处理文件**：`add.format.js`

**操作**：在 `$total` 最开始过滤掉已有的特殊行，保证幂等：
```js
this.reseponse.model.bmsBusinessCostList = this.reseponse.model.bmsBusinessCostList.filter(
  item => !item.specialRowType
)
```

**影响范围**：同 DC-B1

**验证**：同 DC-B1

**状态**：⬜

---

## 第五阶段：P2 专项（最大体量，单独排期）

### DC-P2-1 — 新建 `components/DriverCheckingCostTable.vue`

**问题**：`add.vue` 费用表格模板内联在父组件里，`edit.vue` 与 `read.vue` 共用场景无法复用。

**处理文件**：新建 `driverChecking/components/DriverCheckingCostTable.vue`

**操作**：
1. 将 `add.vue` 中费用表格相关模板（`conf.table` 对应的 el-table 部分）剪切到新组件
2. 定义 props：
   - `action`：String（read / verify / check）
   - `costList`：Array（bmsBusinessCostList）
   - `partPayData`：Object（分次付款数据）
   - `showStar`：Boolean（是否打星）
   - `dictionary`：Object（枚举字典）
3. 定义 emits：
   - `cost-change`（确认金额变更）
   - `files-change`（附件变更）

**影响范围**：`add.vue` 费用表格展示

**验证**：
- [ ] read action：表格只读，所有列正常展示
- [ ] verify action：确认金额列可编辑，附件可上传
- [ ] check action：表格只读，显示审核结果

**状态**：⬜

---

### DC-P2-2 — `add.vue` 引入 `DriverCheckingCostTable` 组件

**依赖**：DC-P2-1 完成后执行

**处理文件**：`add.vue`

**操作**：
1. 引入并注册 `DriverCheckingCostTable` 组件
2. 用 `<DriverCheckingCostTable>` 替换内联表格，传入对应 props
3. 监听 emits，更新父组件数据

**影响范围**：`add.vue` 整体结构

**验证**：
- [ ] read / verify / check 三种 action 模式均正常
- [ ] 保存和提交审核流程不受影响

**状态**：⬜

---

## 执行顺序

```
立即（真实 bug）：DC-B1 → DC-B2
空余（清理废代码）：DC-1 → DC-2 → DC-3 → DC-4 → DC-5 → DC-6
建常量文件：DC-CONST-1
按文件逐步引入：DC-CONST-2 → DC-CONST-3 → DC-CONST-4
触碰 add.format.js 时：DC-P1-1 → DC-P1-2
专项排期：DC-P2-1 → DC-P2-2
```

> 运单结算模块重构计划见：[REFACTOR.md](./REFACTOR.md)

---

**文档版本**: v2.0（司机对账专项）
**最后更新**: 2026年07月
**整理人**: 王新骏
