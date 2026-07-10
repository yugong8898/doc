# 司机对账模块 — 可执行优化 TODO

> 模块路径：`src/views/userBase/driverChecking/`
> 状态：⬜ 待执行 / 🔄 进行中 / ✅ 已完成

---

## 功能一：列表页

涉及文件：`index.vue` / `index.format.js` / `index.conf.js`

### BUG

#### DC-INDEX-B1 | `index.format.js` | codeFormat 无兜底返回值

**问题**：switch 没有命中任何 case 时 `options` 未定义，`options?.find()` 返回 `undefined`，列表单元格渲染为空白。

**操作**：
```js
const option = options?.find(item => item.code === (Number.isNaN(+code) ? code : +code))
return option ? option.text : '--'
```

**影响范围**：列表页所有通过 codeFormat 格式化的列（运输类型、账单状态、柜型、货运类型、车辆类型）

**验证**：
- [ ] 无匹配时显示 `--` 而非空白

**状态**：⬜

---

### P0 清理（随手可做，各项独立）

#### DC-INDEX-1 | `index.conf.js` | 删除 buttonAct 整段废弃注释

**问题**：buttonAct（费用说明、导出、对账确认、下载对账单）已整段注释，按钮已迁移至 `index.vue` 的 `#bar` slot 直接写，注释无废弃说明。

**操作**：删除 `// buttonAct: { ... }` 整段注释（约 10 行）

**影响范围**：仅可读性，无业务影响

**验证**：
- [ ] 列表页顶部按钮区域展示正常（费用说明 / 导出 / 批量确认 / 批量不通过）

**状态**：⬜

---

#### DC-INDEX-2 | `index.format.js` | 合并 getTransportName 重复 case 1/2/3

**问题**：case 1、2、3 三个分支都 `return 'highway'`，逻辑完全相同。

**操作**：
```js
case 1:
case 2:
case 3:
  return 'highway'
```

**影响范围**：仅可读性

**验证**：
- [ ] 公路运单跳转详情页路由正常

**状态**：⬜

---

### P1 重构（触碰该文件时顺手做）

#### DC-INDEX-P1-1 | `index.format.js` | $action switch/case 改为对象映射

**问题**：$action 用 switch/case 列出所有状态约 40 行，新增/修改某状态需全文搜索，容易遗漏。

**依赖**：DC-INDEX-P2-1 建完 constants.js 后执行

**操作**：
```js
const ACTION_MAP = {
  100: { read: true,  verify: true,  check: false, giveBack: false, bill: false, affirm: false },
  110: { read: true,  verify: false, check: true,  giveBack: false, bill: false, affirm: false },
  115: { read: true,  verify: false, check: false, giveBack: false, bill: false, affirm: false },
  120: { read: true,  verify: false, check: false, giveBack: false, bill: false, affirm: false },
  130: { read: true,  verify: false, check: false, giveBack: true,  bill: true,  affirm: false },
  200: { read: true,  verify: false, check: false, giveBack: true,  bill: false, affirm: true  },
  210: { read: true,  verify: false, check: false, giveBack: false, bill: false, affirm: false },
  220: { read: true,  verify: false, check: false, giveBack: false, bill: false, affirm: false },
}
const DEFAULT_CTRL = { read: false, verify: false, check: false, giveBack: false, bill: false, affirm: false }
return (ACTION_MAP[+row.busStatus] || DEFAULT_CTRL)[action]
```

**影响范围**：列表页每行操作按钮显示逻辑

**验证**：
- [ ] 待核对(100)：查看 + 核对
- [ ] 待审核(110)：查看 + 审核
- [ ] 审核通过(130)：查看 + 退回 + 推送
- [ ] 待对账(200)：查看 + 退回 + 对账确认
- [ ] 对账退回(210) / 审核不通过(120)：只显示查看

**状态**：⬜

---

### P2 专项（单独排期）

#### DC-INDEX-P2-1 | 新建 `constants.js` + `index.vue` 引入常量

**问题**：`batchAffirm` 里 `['110','130','200']`、`handleBatchDisPass` 里 `['110']` 均为裸字符串，含义不明。

**处理文件**：新建 `driverChecking/constants.js`，修改 `index.vue`

**操作**：
```js
// constants.js
export const BUS_STATUS = {
  PENDING_VERIFY: 100,  // 待核对
  PENDING_CHECK:  110,  // 待审核
  PROCESSING:     115,  // 处理中
  CHECK_FAILED:   120,  // 审核不通过
  CHECK_PASSED:   130,  // 审核通过
  PENDING_AFFIRM: 200,  // 待对账
  AFFIRM_BACK:    210,  // 对账退回
  AFFIRM_PASSED:  220   // 对账通过
}
export const BATCH_AFFIRM_VALID_STATUS   = ['110', '130', '200']
export const BATCH_DIS_PASS_VALID_STATUS = ['110']
export const COST_TYPE    = { PAYABLE: '200', OTHER_PAYABLE: '600' }
export const FREIGHT_TYPE = { TRADITIONAL: '1', NETWORK: '2' }
export const ACTION_MODE  = { READ: 'read', VERIFY: 'verify', CHECK: 'check' }
```

`index.vue` 引入后替换 `batchAffirm` / `handleBatchDisPass` / `batchDisPassFn` 中的裸字符串。

**影响范围**：批量确认、批量不通过的过滤逻辑

**验证**：
- [ ] 批量确认：只有 110/130/200 状态参与
- [ ] 批量不通过：只有 110 状态参与
- [ ] 全部不符合 / 部分符合 提示弹窗正常

**状态**：⬜


---

## 功能二：详情页

涉及文件：`add.vue` / `add.format.js` / `add.conf.js`

### BUG

#### DC-ADD-B1 | `add.format.js` | $total 重复调用导致汇总行叠加

**问题**：`$total()` 先 `pop()` 一项再 `push()` 追加多行。若当前已有多个汇总行，`pop()` 只移除最后一行，重复调用时小计/合计行越积越多。

**操作**：方法开头先过滤所有已有特殊行，保证幂等：
```js
$total() {
  this.reseponse.model.bmsBusinessCostList = this.reseponse.model.bmsBusinessCostList.filter(
    item => !item.specialRowType
  )
  if (this.reseponse.model.bmsBusinessCostList.length < 2) return
  // ... 原有逻辑不变
}
```

**影响范围**：`add.vue` 费用表格（read / verify / check 三种 action）

**验证**：
- [ ] 进入详情页：小计/合计行各只有一行，不重复
- [ ] 切换 tab 返回后汇总行不叠加
- [ ] read / verify / check 三种 action 均正常

**状态**：⬜

---

### P0 清理

#### DC-ADD-1 | `add.format.js` | 删除 $otherKuiTonsRatio 中 return 后的废弃注释

**问题**：`return` 后跟着约 8 行注释掉的旧计算逻辑，已由后端 `kuiTonsSituationVO.lossType` 替代。

**操作**：删除 `return ...` 之后的注释块

**验证**：
- [ ] 亏涨吨情况列展示不变

**状态**：⬜

---

#### DC-ADD-2 | `add.format.js` | 删除 $all 末尾废弃注释

**问题**：`$all` 只有一行 return，后跟注释掉的旧多字段计算逻辑（已由后端 `amountsPayable` 替代）。

**操作**：删除该注释行（1 行）

**验证**：
- [ ] 文件语法正常

**状态**：⬜

---

#### DC-ADD-3 | `add.format.js` + `add.vue` | 合并重复方法 formatTableFilse / formatResultFilse

**问题**：两个方法实现完全相同（附件数组映射为 `{name, url}`），仅名字不同，调用方各自引用一个。

**操作**：
1. 保留 `formatTableFilse`，改名为 `formatAttachmentList`
2. 删除 `formatResultFilse`
3. `add.vue` 中所有 `formatResultFilse` 调用替换为 `formatAttachmentList`

执行前先确认调用点：
```bash
rg "formatResultFilse|formatTableFilse" src/views/userBase/driverChecking/
```

**影响范围**：`add.vue` 附件列展示

**验证**：
- [ ] verify / check / read 三种 action 下附件列正常展示

**状态**：⬜

---

#### DC-ADD-4 | `add.format.js` | 合并 codeFormat 中 reviewResult / rReviewResult 重复 case

**问题**：两个 case 返回完全相同的选项数组，重复定义。

**操作**：
```js
case 'reviewResult':
case 'rReviewResult':
  options = [{ code: 10, text: '通过' }, { code: 20, text: '不通过' }]
  break
```

**验证**：
- [ ] 操作记录表格审核结果列正常显示"通过"/"不通过"

**状态**：⬜

---

#### DC-ADD-5 | `add.format.js` | 合并 getTransportName 重复 case 1/2/3

**操作**：同 DC-INDEX-2，case 1/2/3 合并为 fall-through。

**验证**：
- [ ] 文件语法正常

**状态**：⬜

---

### P1 重构（触碰该文件时顺手做）

#### DC-ADD-P1-1 | `add.format.js` | 拆解 $total 为子方法

**问题**：`$total` 约 80 行，小计/运费差价/货物保障/油气优惠/合计/全流程专属行的构建逻辑全堆在一起，任何一种行的条件变化都要在 80 行中定位。

**依赖**：DC-ADD-B1 先完成

**操作**：提取子方法：
```
_calcSubtotal(list)       → 纯计算，返回 { costName, $adjustCost }，不操作数组
_appendSubtotalRow(data)  → 追加小计行
_appendFreightDiffRow()   → 运费差价行（companyType !== 1）
_appendInsuranceRow()     → 货物保障服务行（premiumBuyerType === '10'）
_appendOilDiscountRow()   → 油气优惠行
_appendTotalRow()         → 合计行（companyType !== 1）
_appendFullProcessRows()  → 全流程专属行（fpDiff / shipperPay / carrierPay）
```

`$total` 主体精简为：
```js
$total() {
  this.reseponse.model.bmsBusinessCostList =
    this.reseponse.model.bmsBusinessCostList.filter(item => !item.specialRowType)
  if (this.reseponse.model.bmsBusinessCostList.length < 2) return
  const data = this._calcSubtotal(this.reseponse.model.bmsBusinessCostList)
  this._appendSubtotalRow(data)
  if ((action === 'check' || action === 'read') && freightType === '2') {
    this._appendFreightDiffRow()
    this._appendInsuranceRow()
    this._appendOilDiscountRow()
    this._appendTotalRow()
    this._appendFullProcessRows()
  }
}
```

**影响范围**：`add.vue` 费用表格（read / verify / check）

**验证**：
- [ ] 普通运单：小计 + 合计行正常
- [ ] 全流程运单（fullProcessFlag=10）：油气优惠 + fpDiff + 应付/应收运费行正常
- [ ] companyType=1（B1）：不显示运费差价行和合计行

**状态**：⬜

---

### P2 专项（单独排期）

#### DC-ADD-P2-1 | 新建 `components/DriverCheckingCostTable.vue`

**问题**：`add.vue` 费用表格模板全部内联（约 200 行），read/verify/check 三种模式的条件判断混在一起，无法单独测试或复用。

**处理文件**：新建 `driverChecking/components/DriverCheckingCostTable.vue`

**操作**：
- 将 `add.vue` 中费用表格相关模板剪切到新组件
- Props：`action`（read/verify/check）、`costList`、`partPayData`、`showStar`、`dictionary`
- Emits：`cost-change`（确认金额变更）、`files-change`（附件变更）

**验证**：
- [ ] read：表格只读，所有列正常展示
- [ ] verify：确认金额可编辑，附件可上传，保存/提交审核正常
- [ ] check：只读，审核结果列正常

**状态**：⬜

---

#### DC-ADD-P2-2 | `add.vue` | 引入 DriverCheckingCostTable 组件

**依赖**：DC-ADD-P2-1 完成后执行

**操作**：引入注册组件，替换内联表格，监听 emits 更新父组件数据。

**验证**：
- [ ] read / verify / check 三种模式均正常
- [ ] 保存和提交审核流程不受影响

**状态**：⬜

---

## 执行顺序

```
立即（真实 bug）：
  DC-ADD-B1

随手清理（各项独立，不影响业务逻辑）：
  DC-INDEX-B1
  DC-INDEX-1  DC-INDEX-2
  DC-ADD-1  DC-ADD-2  DC-ADD-3  DC-ADD-4  DC-ADD-5

触碰该文件时顺手：
  DC-INDEX-P1-1（依赖 DC-INDEX-P2-1 先建常量）
  DC-ADD-P1-1（依赖 DC-ADD-B1 先完成）

专项排期：
  DC-INDEX-P2-1（建 constants.js，再逐步引入替换）
  DC-ADD-P2-1 → DC-ADD-P2-2
```

---

**文档版本**: v1.0 | **最后更新**: 2026年07月
