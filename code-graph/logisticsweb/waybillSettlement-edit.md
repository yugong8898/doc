# 结算处理 - 调整结算信息页（edit.vue）

## 概述

结算处理模块的核心编辑页，用于对单条运单的结算信息进行调整和提交。支持查看（read）和编辑（edit）两种模式，集成了费用明细编辑、付款方式管理、风控预警、亏吨货损确认、抹零处理等完整结算业务流程。

---

## 文件结构

```
src/views/userBase/waybillSettlement/
├── edit.vue                        ← 本文件（调整结算信息页）
├── read.vue                        （查看页）
├── index.vue                       （结算列表页）
└── components/
    ├── CostMessageDetails.vue      费用明细子组件
    ├── PaymentMethodPanel.vue      付款方式子组件（C147.9新增）
    ├── EditMessageDetails.vue      操作记录子组件
    ├── loseDialog.vue              亏吨确认弹窗
    ├── examResult.vue              预审结果组件
    ├── warnTable.vue               运单状态警告弹窗
    └── editLoadWeight.vue          修改装卸重量弹窗
```

---

## 核心逻辑

### 1. 页面初始化（mounted）

```
getCompanyRoundMode()    → 获取金额取整/舍入方式（用于运费计算）
loadStatusOption()       → 加载枚举字典（运单状态、结算类型、开户行等）
getDetails()             → 加载运单详情、费用明细、结算信息
getZeroByBusId()         → 获取当前运单抹零方式
getPartPay()             → 获取分次支付数据（预付/回单付/到付初始值）
```

### 2. 运费计算联动

`formModel.unitRice`（单价）或 `formModel.settlementQuantity`（结算数量）变化时，通过 `watch` 自动重算 `transportCost`：

```
transportCost = unitRice × settlementQuantity（取整方式由 roundingMode 决定）
```

`once` 标志位控制首次渲染不触发计算。特殊逻辑：POW 开头订单且 supplyType === '300' 时，`once` 为 true，不自动重算。

### 3. 保存/提交主流程

```
handleSave / handleSubmit
  └── changeWaybillStatus(status, type)
        ├── CostMessageDetails.commit()         费用明细校验
        ├── validateOilGasCost()                油气费校验（司机运费 ≥ 实付油气费）
        ├── validatePaymentEquation()           付款等式校验（小计 = 预付 + 回单付 + 到付）
        ├── validateReceiptPayRatio()           回单付比例校验（调接口）
        ├── 抹零处理（zeroByBusIdMode）
        │     ├── diffAmount < 0 → 追加应付抹零费项 + 弹窗确认
        │     ├── diffAmount > 0 → 追加应收抹零费项 + 弹窗确认
        │     └── diffAmount = 0 → 直接进入 beforeChangeWaybill
        └── beforeChangeWaybill()
              └── formRef.validate()
                    └── checkOrder()            运单状态检查
                          └── riskManagement()  风控测算
```

### 4. 风控处理流程

```
riskManagement()
  ├── postData(busStatus)           先保存数据
  ├── getWaybillRiskInfoList()      风控测算（传入 settlementWeight、receivableTotalCost）
  ├── 有中高风险 && 不允许通过
  │     └── 打开 RiskWarningDialog 弹窗
  └── 无风险 / 允许通过
        └── postSubmitAfterRiskPass()
              ├── save  → postData('310') → 成功跳转
              └── submit → postData('320') → 成功跳转
```

风控弹窗回调：
- `handleCloseRiskDialog`：关闭弹窗，不做任何操作
- `handleSubmitRiskDialog`：判断 allowPass，允许则调 `postSubmitAfterRiskPass`
- `updateRiskWarning`：更新页面风控展示信息

### 5. 付款方式联动（C147.9）

三个字段：`advancePayment`（预付款）、`receiptPayment`（回单付）、`cashOnDelivery`（到付）

等式约束：`小计 = 预付款 + 回单付 + 到付`

- 小计变化（`onSubtotalChange`）：重算到付；若到付为负，只标红不清空回单付
- 回单付变化（`onReceiptPaymentChange`）：重算到付；若到付为负，标红并将回单付清为 0

### 6. 亏吨货损处理

```
cargoCompensationConfirmFlag:
  '0' → 不处理
  '1' → 待处理 → 进页面自动弹 loseDialog
  '2' → 已确认 → 可点击 btnTodialog 再次查看
  '3' → 未超吨
```

- `findOneByWaybillId` 获取货损确认详情
- `updateBmsWaybillPoolKuitonsAndWaybillCost` 提交货损确认
- 若运单不存在亏吨但 flag 为 1/2，弹提示"亏吨货损变为0"

### 7. 修改装卸重量

- 按钮：已上报（`regulatoryReportingStatus === '4'`）或结算通过（`busStatus === '320'`）时隐藏
- `handleConfirmEditLoadWeight`：调 `updateWeight` 接口，传 waybillId + versionCode；若已确认货损且重量有变化，给出提示

---

## 依赖关系

### 引用组件

| 组件 | 路径 | 作用 |
|------|------|------|
| `CostMessageDetails` | `./components/CostMessageDetails` | 费用明细展示与编辑 |
| `PaymentMethodPanel` | `./components/PaymentMethodPanel.vue` | 付款方式（预付/回单付/到付） |
| `EditMessageDetails` | `./components/EditMessageDetails` | 操作记录列表 |
| `LoseDialog` | `./components/loseDialog` | 亏吨货损确认弹窗 |
| `ExamResult` | `./components/examResult` | 预审结果展示 |
| `warnTable` | `./components/warnTable` | 运单状态异常警告 |
| `EditLoadWeight` | `./components/editLoadWeight` | 修改装卸净重/毛重 |
| `RiskWarning` | `@/components/Risk/riskWarning` | 页面内风控预警展示 |
| `RiskWarningDialog` | `@/components/Risk/riskWarningDialog` | 风控预警弹窗 |
| `LoseAndRiseViewText` | `@/components/LoseAndRise/viewText.vue` | 亏涨吨情况文本展示 |

### 引用 Mixins

| Mixin | 路径 | 提供能力 |
|-------|------|---------|
| `endOfCalculation` | `@/mixins/endOfCalculation.js` | 金额取整（`roundingMode`、`fomatFloatRoundMode`、`BNumber`、`getCompanyRoundMode`） |
| `unitTool` | `@/mixins/unitTool.js` | 结算单位换算（`exGetUnitName`、`exValidatorWeight`、`exGetgoodsQuantity` 等） |
| `getTrackTimes` | `@/mixins/getTrackTimes.js` | 获取跟踪时间相关 |

### 调用 API

| 接口函数 | 模块 | 说明 |
|---------|------|------|
| `postWaybillDetails` | `userBase.waybillSettlement` | 获取运单结算详情（含费用明细） |
| `postSaveWaybill` | `userBase.waybillSettlement` | 保存/提交结算数据（310/320） |
| `updateBmsWaybillPoolKuitonsAndWaybillCost` | `userBase.waybillSettlement` | 确认亏吨货损 |
| `findOneByWaybillId` | `userBase.waybillSettlement` | 查询货损确认详情 |
| `findZeroByBusId` | `userBase.waybillSettlement` | 获取抹零方式 |
| `dcsOperationRecordPagingexport` | `userBase.waybillSettlement` | 操作记录分页 |
| `checkBindingCard` | `userBase.waybillSettlement` | 检查绑卡状态 |
| `updateWeight` | `userBase.waybillSettlement` | 修改装卸重量 |
| `getShipperName` | `userBase.supplymanagement` | 结算主体下拉列表 |
| `getAttachmentsByWaybillId` | `userBase.transport` | 获取装卸/签收附件 |
| `checkOrderStatus` | `userBase.logisticsPlan` | 运单状态校验 |
| `checkMemberStatus` | `views/userBase/mainstay/api/bankcard` | 检查开户状态 |
| `getPartPay` | `userBase.driverSupplymanagement` | 获取分次支付数据 |
| `receiptPayCheck` | `userBase.driverSupplymanagement` | 回单付比例校验 |
| `getWaybillRiskInfoList` | `@/components/Risk/riskTools` | 风控测算 |
| `queryWaybillRiskInfoList` | `@/components/Risk/riskTools` | 查询风控结果（进页面时） |

### provide 注入（供子组件使用）

| key | 说明 |
|-----|------|
| `bmsWaybillDetail` | 当前运单详情（响应式函数形式） |
| `updateRiskWarning` | 更新风控信息回调 |
| `handleCloseRiskDialog` | 风控弹窗关闭回调 |
| `handleSubmitRiskDialog` | 风控弹窗确认回调 |
| `handleGetTrack` | 获取跟踪信息回调（来自 getTrackTimes mixin） |

---

## 数据流转

```
路由参数（waybillPoolId / waybillId / type / riskLevel）
  ↓
getDetails()  →  detail（运单主信息）
                 responseRecordList（费用明细列表）
                 formModel（表单绑定数据）
  ↓
用户修改单价/结算数量  →  watch 联动重算 transportCost
用户修改费用明细       →  CostMessageDetails 内部管理
用户修改回单付        →  onReceiptPaymentChange → 重算到付
  ↓
保存/提交按钮
  → 多重校验（费用/油气/付款等式/回单付比例）
  → 抹零处理
  → checkOrder → riskManagement
  → postData(status) → 成功后跳回列表
```

---

## 表单字段说明

| 字段 | 说明 | 是否可编辑 |
|------|------|-----------|
| `unitRice` | 单价 | edit 模式可编辑 |
| `settlementQuantity` | 结算数量 | 非柜/车类型可编辑 |
| `settlementWeight` | 结算重量(吨) | 非吨结算时展示，可编辑 |
| `transportCost` | 运费(元) | 自动计算，不可编辑 |
| `loadWeight / loadRoughGoodsWeight` | 装货净重/毛重 | 不可直接编辑，通过弹窗修改 |
| `unloadWeight / unloadRoughGoodsWeight` | 卸货净重/毛重 | 不可直接编辑，通过弹窗修改 |
| `settlementWeightType` | 结算重量类型 | 只读 |
| `accountName` | 结算主体 | 只读（disabled） |
| `openBank / bankAccount` | 收款开户行/卡号 | 只读 |
| `advancePayment` | 预付款 | 只读（来自 getDetails） |
| `receiptPayment` | 回单付 | PaymentMethodPanel 内可编辑 |
| `cashOnDelivery` | 到付 | 联动计算，PaymentMethodPanel 内展示 |
| `waybillAlias` | 运单别名 | 可编辑，最多100字 |
| `orderAlias` | 货源别名 | 只读 |
| `remark` | 备注 | 可编辑，最多200字 |

---

## 运单类型与条件处理

| transportType | 说明 | 特殊逻辑 |
|--------------|------|---------|
| 1/2/3/6 | 公路系列 | 结算主体用下拉选择；司机字段取 `linkmanName` |
| 4/5 | 铁路/水运 | 结算主体用 input 只读；`busNumber` 不可点击跳转监控 |

`settlementType` 影响：
- `10`（吨）：结算数量不禁用；结算重量 = 结算数量；展示"结算方式:现付"
- `20`（柜）：结算数量禁用；展示柜型/柜号/封条号列
- `30`（车）：结算数量禁用

---

## 按钮权限控制

通过路由 meta 初始化，存入 `controlBtn`：

| 字段 | 说明 |
|------|------|
| `btnSave` | 是否显示保存按钮 |
| `btnSubmit` | 是否显示提交按钮 |
| `btnDownload` | 是否允许下载附件 |
| `btnLookDetail` | 是否允许查看运单详情 |

---

## 注意事项

1. **versionCode**：修改重量时必须传，用于乐观锁并发控制，从 `getDetails` 返回值中获取并缓存在 `this.versionCode`
2. **once 标志位**：防止 `watch` 在初始化时误触发运费重算，`updBusCostInput` 调用后置为 false
3. **抹零差价**：`diffAmount` 由 `processNumber` 计算，前端自动追加费项（orderNumber 101/102）并弹窗二次确认
4. **风控测算时机**：保存和提交都会先调保存接口、再进行风控测算，风控通过后才真正调用提交接口
5. **货损弹窗**：flag = '1' 时进页面自动弹出，保存/提交前校验 `updateLoseFlag` 是否已确认；flag = '2' 时用户可手动再次打开
6. **isInMicroApp**：微应用内查看运单详情/跟踪信息使用 `gotoWaybillDetail`，否则 `window.open` 新标签页跳转

---

## 相关文档

- [CostMessageDetails 组件](./CostMessageDetails组件.md)
- [useMainProps 工具模块](./useMainProps工具模块.md)

---

**文档版本**: v1.0  
**最后更新**: 2025-07  
