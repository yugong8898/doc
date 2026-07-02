# CostMessageDetails 费用明细组件

## 概述

`CostMessageDetails` 是运单结算模块的**费用明细核心组件**，负责展示和编辑运单的各类费用项目。支持查看（`read`）和编辑（`edit`）两种模式，包含费用项的增删改、附件上传、抹零计算、油气优惠计算、运费差价计算等完整业务逻辑。

---

## 文件结构

```
waybillSettlement/
└── components/
    ├── CostMessageDetails.vue   ← 本组件
    └── add.conf.js              ← mixin，提供附件弹窗按钮配置
```

---

## 核心数据结构

### params.model（费用明细行）

费用表格的数据源，每行结构如下：

| 字段 | 说明 |
|---|---|
| `costType` | 费用类型（枚举：100=应收，200=应付，600=其他应付） |
| `costCode` | 费用编码（如 A10110=货损，A10111，A10210） |
| `costName` | 费用名称 |
| `busCost` | 原金额 |
| `updBusCost` | 确认金额（可编辑） |
| `confirmRemark` | 费用备注 |
| `orderNumber` | 排序号，≤10 为系统默认项（不可删除费用类型），101/102 为抹零项 |
| `attachmentList` | 附件列表 |
| `addLose` | 是否为货损行（`'1'`） |

### newList（汇总区附加行）

下方汇总表格的数据，独立于 `params.model`，包含：

| 行 | 显示条件 |
|---|---|
| 运费差价 | `companyType !== 1` 时显示 |
| 货物保障服务金额 | `premiumBuyerType === '10'` 时展示（computed `tableNewList` 过滤） |
| 油气优惠 | 后端返回有效油气数据时展示 |

---

## 两张表格的关系

```
┌─────────────────────────────────────────┐
│  上方表格（el-table#recordList）         │
│  数据源：params.model                   │
│  展示：费用明细行（可增删改）            │
│  汇总行：handleGetSummaries()           │
│  → 显示「小计」（updBusCost 汇总）      │
└─────────────────────────────────────────┘
           ↓ subtotal（小计值向下传递）
┌─────────────────────────────────────────┐
│  下方表格（el-table#summaryTable）       │
│  数据源：tableNewList（newList 过滤后）  │
│  展示：运费差价、货物保障服务、油气优惠  │
│  汇总行：summariesFn()                  │
│  → 显示「合计」、全流程运费差价、       │
│       客户应付运费 / 应付承运商运费      │
└─────────────────────────────────────────┘
```

---

## 核心逻辑

### 1. 模式控制（type）

`type` 从路由参数 `this.$route.query.type` 获取，值为 `'read'` 或 `'edit'`。

- `read`：所有输入禁用，操作列隐藏，附件为「查看附件」模式
- `edit`：可编辑确认金额、备注，可新增/删除行，可上传附件

### 2. orderNumber 的特殊含义

```
orderNumber ≤ 10    → 系统默认费用项，费用类型和费用项目不可编辑
orderNumber = 101   → 抹零行（应收方向，costType='100'）
orderNumber = 102   → 抹零行（应付方向，costType='200'）
orderNumber > 10    → 用户自定义新增行，可删除，可选费用类型
```

### 3. 小计计算（handleGetSummaries）

遍历 `params.model`：
- `costType` 为 `'200'` 或 `'600'`（应付/其他应付）→ **加**
- 其他（应收）→ **减**

结果赋给 `this.subtotal`，同时渲染动态金额单位图标。

### 4. 合计计算（summariesFn）

```
合计 = subtotal（小计）+ 运费差价 + 货物保障服务金额 - 油气优惠
```

- 油气优惠作为**负数**扣减，`confirmMoney === -1` 时按 0 处理
- 全流程运单额外展示：全流程运费差价、差价率、客户应付/应付承运商运费

### 5. 运费差价计算（countMoney）

```
合计 = 小计 / (1 - 差价率%) + 货物保障服务金额
运费差价 = 合计 - 小计 - 货物保障服务金额
```

- 取整方式由 `roundingMode` prop 控制（0=向上，1=向下，4=四舍五入）
- 结果写入 `newList[0].confirmMoney`，并通过 `$emit('newServiceCharge')` 通知父组件

### 6. 抹零计算（dealZeroModeFn）

- 遍历 `params.model`，按应收/应付方向汇总确认金额
- 调用 `processNumber()` 按 `zeroByBusIdMode` 规则处理抹零
- 差值 > 0 → 插入 `orderNumber: 101`（应收抹零行）
- 差值 < 0 → 插入 `orderNumber: 102`（应付抹零行）
- 删除抹零行时调用 `updateByBusId` 接口将抹零方式置为不抹零

### 7. 油气优惠逻辑

#### 展示条件
后端返回以下数据即展示（不依赖当前规则配置，属于历史数据展示）：
```
oilAmount > 0
&& oilDiscountAmount !== -1
```

全流程运单（`fullProcessFlag === 10`）强制展示，油气优惠金额固定为 0。

#### 实时更新（updateOilGasDiscountIfNeeded）
在「确认金额失焦」和「抹零计算」后触发：
1. 确认存在有效油气费（`oilAmount > 0`）
2. 取 `subtotal`（小计）作为 `adjustedAmount`
3. 调用 `calculateOilRebate` 接口
4. 用返回的 `rebateAmount` 更新 `newList` 中油气优惠行的 `confirmMoney`

### 8. 全流程运费计算（doCalculateFullProcessFreight）

仅在 `type === 'edit'` 且 `fullProcessFlag === 10` 时触发：
- 防抖 300ms
- 传入 `waybillId` + `receivableTotalCost`（即 `subtotal`）
- 返回结果通过 `$emit('updateDetail')` 更新父组件的 `detailObj`

### 9. detailObj watch 中的重建逻辑

| 场景 | 行为 |
|---|---|
| 首次加载 / 查看模式 | 完整重建 `newList`（运费差价、货物保障服务、油气优惠） |
| 编辑模式且 `newList` 已有数据 | **跳过重建**，只单独更新油气优惠行，避免覆盖用户调整后的运费差价 |

### 10. transportCost watch

当父组件传入 `transportCost` 变化时，自动更新 `params.model` 中 `orderNumber < 11` 且不是货损/其他杂费（`A97200/A10111/A10210`）的行的原金额和确认金额。

---

## Props 说明

| prop | 类型 | 说明 |
|---|---|---|
| `params` | Object | 包含 `model`（费用行数组）、`busBillId` |
| `dictionary` | Object | 枚举字典，含 `fylx`（费用类型）、`gx` 等 |
| `newUpdBusCost` | String | 新确认金额（外部传入） |
| `transportCost` | String | 运费，变更时同步更新费用行原金额 |
| `detailObj` | Object | 运单详情，含 `fullProcessFlag`、`companyType`、`oilAmount` 等 |
| `zeroModeObj` | Object | 当前抹零配置对象（含 `id`、`value`） |
| `zeroTypeObj` | Object | 抹零类型枚举 |
| `roundingMode` | Number | 差价取整方式（0/1/4） |
| `partPayData` | Array | 分次支付数据（预付/到付/回单付） |
| `zeroByBusIdMode` | String | 按运单的抹零方式 |

---

## Emits 事件

| 事件 | 触发时机 | 参数 |
|---|---|---|
| `newServiceCharge` | 运费差价重新计算后 | `serviceRateMoney`（差价金额） |
| `updateDetail` | 全流程运费计算接口返回后 | `res.model[0]`（更新后的详情） |
| `updateZeroType` | 删除抹零行成功后 | 无 |

---

## 对外方法（供父组件调用）

### `commit()`

执行保存/提交前的数据校验和整理：

1. 检查同费用类型下是否有重复费用编码 → 报错
2. 检查费用类型/费用项目是否填写完整 → 报错
3. 执行 `$refs.form.validate()` 表单校验
4. 整理数据格式（补全 `orderNumber`、`codeAndNames`、`busBillId` 等字段）
5. 校验通过返回整理后的数组，失败返回错误标记字符串

### `addTableRow(formObj?, flag?)`

外部（货损场景）调用新增费用行：
- 无参数：新增空白自定义行
- `formObj + flag=1`（首次货损）：新增货损行，金额为 `formObj.lossCast`
- `formObj + flag + 已有货损`：只更新现有货损行的确认金额

---

## 依赖关系

```
CostMessageDetails.vue
├── mixin: add.conf.js
├── api: userBase.waybillSettlement
│   ├── updateByBusId（删除抹零行）
│   └── doCalculateFullProcessFreight（全流程运费计算）
├── api: oilGasManage
│   └── calculateOilRebate（油气返利计算）
├── api: userBase.constManagement
│   └── constRecord.getConstNameList（费用项目列表）
├── components: PrimitivePage/buttons（附件弹窗按钮）
├── components: Upload（附件上传）
├── utils: workSpace.processNumber（抹零处理）
├── utils: func.debounce（防抖）
├── utils: commonUpload.BUSINESS_TYPE（附件业务类型）
└── config: enumeration（枚举常量 fylx、gx 等）
```

---

## 注意事项

1. **`orderNumber` 是关键控制字段**：决定行是否可编辑、可删除，以及抹零行的方向，不可随意修改
2. **`newList` 重建保护**：编辑模式下 `detailObj` watch 不重建 `newList`，防止覆盖用户已调整的运费差价
3. **油气优惠不依赖规则配置**：只要后端返回有效 `oilAmount` 数据即展示，属于历史数据概念
4. **`commit()` 返回值**：返回整理好的数组（成功）或 `'1'`/`'2'`（失败），父组件需判断类型
5. **全流程运单（`fullProcessFlag === 10`）**：油气优惠强制为 0，下方汇总额外展示全流程运费差价行

---

## 相关文档

- [logisticsweb 项目总览](./项目总览.md)

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
