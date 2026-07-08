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

下方汇总表格（`summaryTable`）的数据源，独立于 `params.model`。

#### 行结构

```js
{
  costName: '运费差价' | '货物保障服务金额' | '油气优惠',
  confirmMoney: Number,   // 金额
  confirmRemark: String,  // 运费差价行存差价率（数字），油气优惠行存「油气实际使用 xxx 元」
  companyType: Number     // 仅运费差价行有，用于模板 v-mask-star 遮蔽判断
}
```

#### 行构成与下标

| 行 | 下标 | 显示条件 |
|---|---|---|
| 运费差价 | `[0]` | `companyType !== 1` 时加入 |
| 货物保障服务金额 | `[1]` 或 `[0]`（B1时） | 始终加入，由 computed `tableNewList` 按 `premiumBuyerType === '10'` 过滤显示 |
| 油气优惠 | 末尾 | 后端返回有效油气数据，或全流程运单（`fullProcessFlag === 10`） |

> `companyType === 1`（B1承运商）时，运费差价行不加入 `newList`，货物保障服务金额下标变为 `[0]`。

#### 初始化时机（两处，结果后者覆盖前者）

**1. `mounted()`**：组件挂载时首次构建。注意此处**未处理全流程（fullProcessFlag）**，货物保障服务直接取 `premiumAmount`，不强制为 0。

**2. `detailObj` watch — 完整重建分支**：条件为 `newList.length === 0` 或 `type !== 'edit'`（首次加载 / 查看模式）。此分支**会处理全流程**：`fullProcessFlag === 10` 时货物保障服务强制为 0。

两处均在 `$nextTick` 内执行，`mounted` 触发后 watch 几乎立刻跟进并覆盖，`mounted` 的结果为**过渡态**，最终以 watch 为准。

| 场景 | 全流程货物保障服务金额 |
|---|---|
| `mounted` | 取 `premiumAmount`，不强制为 0 |
| `detailObj` watch 完整重建 | 强制为 `0` |

#### 更新时机（三处）

**1. `detailObj` watch — 保护分支**

条件：`newList.length > 0 && type === 'edit'`（编辑模式且已初始化）

只更新油气优惠行，不动运费差价和货物保障服务，防止保存刷新 `detailObj` 时覆盖用户已调整的差价：

```
油气数据有效 && 油气行不存在 → push 油气行
油气数据有效 && 油气行已存在 → 不动（优先保留接口已更新的值）
油气数据无效 && 油气行存在  → splice 移除
```

**2. `countMoney()`**

`subtotal` watch 在编辑模式下触发 → 重新计算运费差价，直接写 `newList[0]`：

```js
this.$set(this.newList[0], 'confirmMoney', serviceRateMoney)
this.$set(this.newList[0], 'confirmRemark', rate)  // 差价率
```

⚠️ 硬编码下标 `[0]`，`companyType === 1` 时 `newList[0]` 是货物保障服务行，存在写错位置的风险（实际业务中 B1 不会触发差价计算，但需注意）。

**3. `updateOilGasDiscountIfNeeded()`**

确认金额失焦 / 抹零计算后触发，调用 `calculateOilRebate` 接口，用返回的 `rebateAmount` 更新油气优惠行：

```js
this.$set(this.newList[oilGasIndex], 'confirmMoney', discountAmount)
```

#### 消费路径

```
newList
  └── computed: tableNewList（按 premiumBuyerType 过滤货物保障服务行）
        └── summaryTable :data
              └── summariesFn() 汇总行
                    合计 = subtotal + Σ(newList.confirmMoney)，其中油气优惠取负
```

父组件 `edit.vue` 也通过 ref 直接读取：

```js
this.$refs.CostMessageDetails.newList[0]?.confirmRemark  // 读取当前差价率
```

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

`confirmRemark` 列（费用备注）的汇总行有特殊逻辑：
- 有 `partPayData` 时，展示分次支付信息（预付 / 到付 / 回单付）
- `premiumBuyerType === '20'`（货主购买货物保障）时，额外展示含司机购买金额的提示文案
- 分次支付类型：`'10'`=预付，`'20'`=回单付，`'30'`=到付（到付固定展示"除预付和回单付以外未付运费"）

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

### 10. 固定扣款行（F10101 / F10102）

`costCode` 为特殊编码的行，确认金额不允许用户直接编辑，由系统自动计算：

| costCode | 含义 | 确认金额来源 |
|---|---|---|
| `F10102` | 固定扣款（按比例） | `computed: updBusCostComputed` = 运费 × `item1`（系数） |
| `F10101` | 固定扣款（按固定金额） | 绑定 `busCost`（原金额），不跟随用户输入变化 |

两者的 `el-input` 均设置了 `:disabled="true"`，通过 `syncFixedDeductionAmounts()` 在以下时机同步写入 `updBusCost`：
- `transportCost` 变化后
- `updBusCostInput` 输入时
- `updBusCostBlur` 失焦后
- `handleGetSummaries` 汇总计算时

### 11. transportCost watch

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
2. **`newList` 重建保护**：编辑模式且已初始化后，`detailObj` watch 只更新油气优惠行，不重建整个 `newList`，防止覆盖用户已调整的运费差价。`countMoney` 硬编码操作 `newList[0]`，B1（`companyType === 1`）场景需注意下标错位风险
3. **油气优惠不依赖规则配置**：只要后端返回有效 `oilAmount` 数据即展示，属于历史数据概念
4. **`commit()` 返回值**：返回整理好的数组（成功）或 `'1'`/`'2'`（失败），父组件需判断类型
5. **全流程运单（`fullProcessFlag === 10`）**：油气优惠强制为 0，下方汇总额外展示全流程运费差价行

---

## 重构参考：完整内部状态梳理

### data 字段一览

| 字段 | 初始值 | 用途 | 备注 |
|---|---|---|---|
| `type` | `''` | 页面模式，`'read'` 或 `'edit'`，从路由 `query.type` 读取 | 控制全组件的只读/编辑态 |
| `busBillId` | `''` | 当前结算单 ID，从 `params.busBillId` 读取 | 提交时写入每行数据 |
| `newList` | `[]` | 下方汇总表的数据行（运费差价/货物保障/油气优惠） | 见 newList 章节 |
| `subtotal` | `0` | 上方表格确认金额小计，由 `handleGetSummaries` 写入 | 父组件通过 ref 读取 |
| `total` | `0` | 声明了但**从未被赋值使用**，废弃字段 | ⚠️ 重构可删除 |
| `searchOptions` | `[]` | 费用项目下拉选项，按需加载（每次 focus 时拉取） | 全组件共享，多行同时操作可能串数据 |
| `selectLoading` | `false` | 费用项目下拉的加载状态 | |
| `fileList` | `[]` | 附件弹窗中当前显示的文件列表 | 打开弹窗时从对应行 `attachmentList` 映射 |
| `activeIndex` | `0` | 当前操作附件的行下标 | 上传/删除附件时定位到正确的行 |
| `upLoading` | `false` | 附件上传中的 loading 状态 | |
| `show.dialog` | `false` | 附件弹窗显隐 | |
| `imgList` | `[]` | 图片预览时的附件对象数组（含 url/name） | 传给 `el-image-x` |
| `imgListTableUrl` | `[]` | 图片预览时的 url 字符串数组 | 传给 `el-image-x` 的 `preview-src-list` |
| `initialIndex` | `0` | 图片预览初始下标 | 声明了但未实际使用，预览由 `clickHandler` 控制 |
| `maxIndex` | `9999` | 图片预览 z-index | 旧方案遗留，当前用 `el-image-x` 不需要此值 |
| `dialogImgVisible` | `false` | 旧图片预览弹窗的显隐 | ⚠️ 旧方案遗留，`el-image-x` 已替代，但此字段仍被 `handleLookImg` 写入 |
| `formRules` | 见代码 | 表单校验规则（costType/updBusCost/codeAndNames） | 仅用于 `el-form` 的 rules prop，实际行级校验用 `formItemRules()` |
| `serviceRateMoney` | 未声明 | 运费差价金额，在 `countMoney()` 中直接赋值到 `this` | ⚠️ 未在 data 中声明，为隐式属性，非响应式 |
| `delZeroTxt` | `''` | 删除抹零行时的操作备注文案 | 传给 `updateByBusId` 接口 |
| `addLose` | `''` | `addTableRow` 调用时传入的 flag，存在 data 上 | 逻辑意义不明确，重构时可改为局部变量 |
| `arr` | `[]` | 声明了但**从未使用**，废弃字段 | ⚠️ 重构可删除 |
| `nowIcon` | `''` | 声明了但**从未使用**，废弃字段 | ⚠️ 重构可删除 |
| `tableLoading` | `false` | 下方汇总表的 loading，全流程运费计算时展示 | |

> ⚠️ 废弃字段汇总：`total`、`arr`、`nowIcon`、`dialogImgVisible`（逻辑上已被替代但未清理）、`serviceRateMoney`（未声明为响应式）。

### computed 一览

| 名称 | 依赖 | 返回值 | 备注 |
|---|---|---|---|
| `updBusCostComputed` | `params.model`（运费行 + F10102 行） | 固定比例扣款确认金额 = 运费 `updBusCost` × `item1`（系数） | 绑定到 F10102 行的 `el-input`，只读展示 |
| `uploadFormData` | 无 | `{ businessType: WAYBILL_SETTLEMENT_INFORMATION }` | 附件上传时的附加表单字段 |
| `fylxTypeObj` | `dictionary.params` | 费用类型枚举的 `{ enumCode: name }` 映射对象 | 用于只读模式下显示费用类型文案 |
| `fylxTypeOption` | `dictionary.items` | 费用类型枚举数组 | 用于编辑模式下费用类型下拉选项，过滤 `enable !== '2'` 的项 |
| `gxType` | `dictionary.params` | 关系类型枚举映射 | 声明了但**模板和 methods 中均未使用**，⚠️ 废弃 |
| `tableNewList` | `newList`、`detailObj.premiumBuyerType` | 过滤后的 `newList` | `premiumBuyerType !== '10'` 时过滤掉货物保障服务金额行 |

### watch 一览

| 监听目标 | 选项 | 触发时机 | 主要副作用 | 注意点 |
|---|---|---|---|---|
| `transportCost` | `deep` | 父组件运费变化时 | 更新 `params.model` 中 `orderNumber < 11` 且非豁免编码行的 `busCost`/`updBusCost`；调用 `syncFixedDeductionAmounts()` | 豁免编码：`A97200 A10111 A10210 F10101 F10102` |
| `detailObj` | `deep` | 运单详情对象任意字段变化时 | **分支一**（编辑模式且 newList 已有数据）：只更新油气优惠行；**分支二**（首次/查看模式）：完整重建 `newList` | 两个分支通过 `newList.length > 0 && type === 'edit'` 区分；全部在 `$nextTick` 内执行 |
| `subtotal` | `deep` | 小计金额变化时（由 `handleGetSummaries` 写入） | 编辑模式且有差价率时：调用 `countMoney()` 重新计算运费差价 | 查看模式下不触发 `countMoney`，避免覆盖后端已有数据 |

### methods 一览（上：计算类 / 数据处理类）

| 方法 | 入参 | 返回值 | 职责 | 被谁调用 |
|---|---|---|---|---|
| `syncFixedDeductionAmounts()` | 无 | 无 | 同步 F10102（按比例）和 F10101（按固定金额）行的 `updBusCost` | `transportCost` watch、`updBusCostInput`、`updBusCostBlur`、`handleGetSummaries` |
| `formatService(num, n, type)` | 数值、保留位数、取整方式(0/1/4) | 处理后的数值 | 自定义取整，封装 ceil/floor/round | `count()` |
| `count(Amount, Rate)` | 小计金额、差价率 | 合计金额（含取整） | 计算 `小计 / (1 - 差价率%)` | `countMoney()` |
| `getBit(value, n)` | 数值、截取小数位数 | 截取后的数值 | 截断（非四舍五入）小数，避免浮点误差 | `count()` |
| `countMoney(cost, rate)` | 小计、差价率 | 无（直接修改 `newList[0]`） | 计算运费差价，写入 `newList[0].confirmMoney`，emit `newServiceCharge`，触发全流程运费计算 | `subtotal` watch、父组件 ref 直接调用 |
| `doCalculateFullProcessFreight()` | 无（读 `detailObj` + `subtotal`） | 无（emit `updateDetail`） | 防抖 300ms，调用接口计算全流程运费差价，结果回传父组件 | `countMoney()`，仅 `type=edit && fullProcessFlag=10` 时生效 |
| `handleGetSummaries(param)` | el-table 的 param 对象 | sums 数组（JSX 元素） | 上方表格汇总行：计算小计（写 `subtotal`）、原金额汇总、分次支付备注 | el-table `summary-method` |
| `summariesFn(param)` | el-table 的 param 对象 | sums 数组（JSX 元素） | 下方汇总表格汇总行：计算合计、展示全流程差价/应付运费/差价率/上下游公司名 | el-table `summary-method` |
| `updBusCostInput(index, row)` | 行下标、行数据 | 无 | 输入时清洗非法字符、限制长度、同步 F10101/F10102、触发抹零计算 | 模板 `@input` |
| `updBusCostBlur(index, row)` | 行下标、行数据 | 无（async） | 失焦时格式化为两位小数、同步固定扣款、触发油气返利重新计算 | 模板 `@blur` |
| `dealZeroModeFn()` | 无 | 无 | 按 `zeroByBusIdMode` 规则计算抹零差值，插入/更新/删除 orderNumber 101/102 行；完成后触发油气返利更新 | `updBusCostInput`、父组件 ref 调用 |
| `updateOilGasDiscountIfNeeded()` | 无 | 无（async） | 有油气费时调用 `calculateOilRebate` 接口，更新 `newList` 中油气优惠行的金额 | `updBusCostBlur`、`dealZeroModeFn` |

### 模板列渲染规则（上方表格 recordList）

| 列 | 只读条件 | 可编辑条件 | 特殊规则 |
|---|---|---|---|
| 费用类型 | `type==='read'` 或 `orderNumber<=10` | 其他情况显示下拉 | 抹零行（101/102）下拉 disabled；选项过滤 `enable==='2'` 的禁用项 |
| 费用项目 | `orderNumber<=10` 或 `type==='read'` | 其他情况显示下拉 | 抹零行（101/102）下拉 disabled；focus 时按 costType 动态拉取选项（`searchOptions` 共享） |
| 原金额 | 始终只读 | — | `orderNumber<=10` 时负数标红；其他行 `style="display:black"`（⚠️ 疑似笔误，应为 `block`） |
| 调整金额 | 始终只读 | — | `updBusCost - busCost < 0` 时标红 |
| 确认金额 | `type !== 'edit'` | `type === 'edit'` | F10102 行绑定 `updBusCostComputed`（只读 computed）；F10101 行绑定 `busCost`（原金额）；抹零行（101/102）disabled；其他行正常输入 |
| 费用备注（编辑） | 抹零行（101/102）或 F10101/F10102 行 disabled | 其他行可输入 | `v-if="type==='edit'"` 时显示此列 |
| 费用备注（只读） | 始终只读，`show-overflow-tooltip` | — | `v-if="type!=='edit'"` 时显示此列 |
| 附件 | 始终只读 | — | 有附件时显示「查看附件」蓝色链接；无附件不显示 |
| 操作人 | 始终只读 | — | 优先 `updateName`，fallback `createName` |
| 操作时间 | 始终只读 | — | 格式化为 `yyyy-MM-dd HH:mm` |
| 操作 | `v-if="type==='edit'"` 才显示 | — | 「上传附件」始终显示；「删除」按钮：`orderNumber>10` 或 `costCode` 为 A10111/A10210/F10102/F10101 时显示；「新增」按钮：仅最后一行且总行数 < 20 时显示 |

**模板列渲染规则（下方表格 summaryTable）**

| 列 | 渲染逻辑 |
|---|---|
| 费用项目 | 直接显示 `costName` |
| 确认金额 | 运费差价行：`v-mask-star` 脱敏，`companyType===1` 时不显示；油气优惠行：全流程时显示 0，否则显示 `-金额`（负数展示）；其他行正常显示 |
| 费用备注 | 油气优惠行：直接显示 `confirmRemark`（油气实际使用 x 元）；运费差价行：显示「差价率：x %」并 `v-mask-star`；其他行不显示 |
| 其余列 | 全为空占位列，与上方表格对齐 |

### methods 一览（下：交互类 / 附件类 / 对外接口）

| 方法 | 入参 | 返回值 | 职责 | 被谁调用 |
|---|---|---|---|---|
| `handleResize()` | 无 | 无 | window resize 时调用上方表格 `doLayout()` | `window resize` 事件（mounted 注册，destroyed 销毁） |
| `formItemRules(prop, trigger)` | 字段名、触发方式 | validator 规则对象 | 动态生成行级表单校验规则 | 模板 `el-form-item :rules` |
| `costTypeChange(index)` | 行下标 | 无 | 费用类型变更时清空该行所有费用项目字段，`orderNumber` 重置为 `'11'` | 模板费用类型 `@change` |
| `handleSelect(val, index)` | 费用编码、行下标 | 无 | 选择费用项目后，将 `costCode/costName/asCostName/codeAndNames` 写入对应行 | 模板费用项目 `@change` |
| `getSearchList(row)` | 行数据 | 无 | 费用项目 focus 时，按 `costType` 拉取费用项目列表，填充 `searchOptions` | 模板费用项目 `@focus` |
| `mapObj(rule, to, from)` | 字段映射规则数组、目标对象、来源对象 | 目标对象或 null | 通用字段映射工具，按规则将 from 的字段复制到 to | `handleSelect`、`commit` |
| `handleLookImg(item)` | 行数据（含 `attachmentList`） | 无 | 点击「查看附件」时，组装图片数据并触发 `el-image-x` 预览 | 模板附件列 `@click` |
| `handleDialogClose()` | 无 | 无 | 旧图片弹窗关闭（已废弃，`el-image-x` 替代后未清理） | 旧 `ImgDialog` 组件回调 |
| `viewFiles(index, fileList)` | 行下标、附件列表 | 无 | 点击「上传附件」时，映射文件列表格式，打开附件弹窗 | 模板操作列「上传附件」按钮 |
| `fileRemove(file, fileList)` | 删除的文件、剩余列表 | 无 | 附件弹窗中删除文件时，同步从 `params.model[activeIndex].attachmentList` 移除 | Upload 组件 `@handleRemove` |
| `closeDialog()` | 无 | 无 | 关闭附件弹窗，重置 `activeIndex/fileList/show.dialog` | `add.conf.js` 中「返回」按钮 |
| `uploadSuccess({ response, file, fileList })` | 上传响应对象 | 无 | 上传成功后将新文件追加到 `params.model[activeIndex].attachmentList` | Upload 组件 `@handleSuccess` |
| `beforeUpload(val)` | 无 | 无 | 上传开始，设 `upLoading = true` | Upload 组件 `@beforeUpload` |
| `handleError()` | 无 | 无 | 上传失败，设 `upLoading = false` | Upload 组件 `@handleError` |
| `delTableRow(index)` | 行下标 | 无 | 删除行：普通行直接 splice；抹零行弹确认框后调 `updateByBusId` 接口再删，成功后 emit `updateZeroType` | 模板操作列「删除」按钮 |
| `getZeroDelStatus(index)` | 行下标 | 无 | 调用 `updateByBusId` 接口将抹零方式置为不抹零，成功后删除行并 emit | `delTableRow` |
| `addTableRow(formObj?, flag?)` | 可选：货损信息对象、货损 flag | 无 | 新增费用行（空行 / 货损首次 / 货损更新） | 模板「新增」按钮、父组件 ref（已注释） |
| `commit()` | 无 | 整理好的数组 或 `'1'`/`'2'` | 保存前校验（重复编码/填写完整/表单校验），整理数据格式并返回 | 父组件 `changeWaybillStatus` 中通过 ref 调用 |

---

### 父组件（edit.vue）对本组件的 ref 调用清单

| 调用位置 | 调用方式 | 触发场景 |
|---|---|---|
| `changeWaybillStatus()` | `this.$refs.CostMessageDetails.commit()` | 保存/提交前校验并获取整理好的费用数据 |
| `changeWaybillStatus()` | `this.$refs.CostMessageDetails?.subtotal` | 油气费校验时读取小计金额 |
| 运费金额变化回调 | `this.$refs.CostMessageDetails.newList[0]?.confirmRemark` | 读取当前差价率，传入 `countMoney()` |
| 运费金额变化回调 | `this.$refs.CostMessageDetails.countMoney(amount, rate)` | 重新计算运费差价（抹零后重算） |
| 费用明细数据加载后 | `this.$refs.CostMessageDetails.dealZeroModeFn()` | 初始化数据后立即执行抹零计算 |
| 抹零配置刷新后 | `this.$refs.CostMessageDetails.dealZeroModeFn()` | 重新获取抹零方式后重算 |
| 货损确认（已注释） | `this.$refs.CostMessageDetails.addTableRow(confirmInfo, flag)` | 货损确认后新增/更新货损行（当前已注释，未走此路径） |

> 重构注意：以上 ref 调用说明父组件对子组件有较强依赖，重构时需同步更新 `edit.vue` 中对应调用点。`newList[0]` 的硬编码下标读取差价率属于隐性耦合，重构时应改为具名 getter 或 emit 事件。

---

## 重构风险点清单

重构前必须逐条确认：

| # | 风险点 | 影响范围 | 建议处理 |
|---|---|---|---|
| 1 | `searchOptions` 全组件共享，多行同时 focus 会互相覆盖 | 费用项目下拉 | 重构时改为行级独立的 options 数据，或按当前聚焦行隔离 |
| 2 | `countMoney` 硬编码操作 `newList[0]`，B1（`companyType===1`）场景下 `[0]` 是货保行而非差价行 | 运费差价计算 | 重构时用 `find` 按 `costName` 定位行，不依赖下标 |
| 3 | `serviceRateMoney` 未在 `data` 中声明，为非响应式隐式属性 | 运费差价金额 | 重构时在 `data` 中补充声明 |
| 4 | `newList` 有两处初始化（`mounted` + `detailObj` watch），后者会覆盖前者，`mounted` 实际是过渡态；且 `mounted` 不处理全流程逻辑 | newList 初始化 | 重构时合并为单一初始化入口，统一处理全流程判断 |
| 5 | `detailObj` watch 保护分支中，油气行已存在时完全跳过更新（注释写"可能已接口更新过"），但 `detailObj.oilDiscountAmount` 有变化时实际上不会同步 | 油气优惠金额 | 重构时明确：油气金额来源只认接口返回，detailObj 变化时也应对比更新 |
| 6 | `commit()` 的返回值用字符串 `'1'`/`'2'` 表示失败，`undefined` 表示表单校验未通过，父组件需做多种类型判断 | 保存流程 | 重构时改为明确的 `{ valid, data, error }` 结构 |
| 7 | `commit()` 内用 `Map` 校验重复编码，逻辑写在 `forEach` 内嵌套 `for...of map`，存在提前 `return false` 但外层 `forEach` 仍继续执行的问题（`return false` 对 `forEach` 无效） | 重复费用项校验 | 重构时改用 `some` 或 `for...of` 可以 break 的循环 |
| 8 | `updBusCostInput` 中调用 `debounce(this.dealZeroModeFn(), 500)` 写法有误：`debounce()` 应包裹函数引用而非调用结果，实际上 `dealZeroModeFn` 每次都立即执行，debounce 无效 | 抹零计算频率 | 重构时改为 `this.debouncedDealZeroMode()` 提前在 `created` 中创建防抖函数 |
| 9 | `delTableRow` 删除行后再调 `dealZeroModeFn()`，但删除抹零行的逻辑走异步接口，接口成功后才 splice，此时 `dealZeroModeFn` 已经用旧数据算完了 | 删除抹零行后的重算 | 重构时将 `dealZeroModeFn` 移到 `getZeroDelStatus` 成功回调中 |
| 10 | 父组件通过 `ref` 直接读取 `newList[0].confirmRemark`（差价率）属于强耦合，父组件的逻辑依赖子组件内部数据结构 | edit.vue 与本组件的耦合 | 重构时改为子组件 emit 差价率变化事件，或提供明确的 `getDiffRate()` 方法 |
| 11 | 废弃字段未清理：`total`、`arr`、`nowIcon`、`gxType` computed、`dialogImgVisible`（被 `el-image-x` 替代后未移除）、`handleDialogClose`（旧回调） | 代码整洁度 | 重构时统一删除 |
| 12 | 原金额列有 `style="display:black"`（应为 `block`）的笔误 | 视觉无影响（inline 元素 display 值不合法时降级为 inline） | 重构时修正 |

---

## 相关文档

- [logisticsweb 项目总览](./项目总览.md)

---

**文档版本**: v2.0
**最后更新**: 2026年07月
**整理人**: 王新骏
