# 结算处理 - 调整结算信息页（adjust.vue）

## 概述

货主 App（`wlyd-app-consigner`）结算模块的核心编辑页，功能对标 PC 端 `edit.vue`。  
支持运单结算信息的查看与调整：单价/结算数量/结算重量编辑、费用明细管理、亏吨货损确认、抹零处理、风控测算、保存/提交预审。

---

## 文件结构

```
settlementPages/waybillSettlement/
├── adjust.vue       ← 本文件（调整结算信息页）
├── read.vue         （查看结算信息页）
├── index.vue        （结算列表页）
├── editAdjust.vue   （修改装卸重量页）
└── risk.js          （风控工具函数）
```

---

## 页面入口

| 参数 | 说明 |
|------|------|
| `waybillPoolId` | 结算池 ID，必填，用于查询详情 |
| `waybillId` | 运单号，必填，用于分次支付/抹零/风控等接口 |
| `riskLevel` | 初始风控等级（`0/200/300/400`），可选 |

---

## 核心流程

### 1. 初始化（onLoad）

```
getCompanyRoundMode([waybillId], '11')   → 获取金额取整方式（结算）
loadNecessaryEnums()                     → 加载字典（开户行 khh、结算重量类型 jszl、费用类型 fylx）
loadZeroTypeObj()                        → 加载抹零方式字典（yxzdmlfs）
getDetails()  ┐
loadCostEnums()┘  并行执行
getRecordPaging()                        → 加载操作记录
loadPartPay()                            → 加载分次支付信息（预付/回单付/到付文本）
uni.$on('editAdjust', getDetails)        → 监听 editAdjust 事件（从修改装卸重量页返回后刷新）
```

### 2. 详情加载（getDetails）

```
postWaybillDetails({ waybillPoolId })
  └── initFormModel()      → 表单字段赋值（单价/重量/结算主体/委托转账等）
        ├── getZeroByBusId()        → 查询抹零配置
        └── checkBindingCardInfo()  → 网络货运查询绑卡信息（freightType === '2'）
  └── initCostList()       → 费用明细初始化（含抹零费项处理）
  └── initDamageForm()     → 货损表单初始化
  └── 货损确认处理
        ├── cargoCompensationConfirmFlag === '1' 或 '2'
        │     └── findOneByWaybillId() → 获取货损详情
        │           └── flag === '1' → 自动弹出货损确认弹窗
        └── 其他 → 跳过
  └── getRiskDetails()     → 查询最新风控结果并更新 riskLevel
```

### 3. 运费计算联动

单价或结算数量变化时触发 `calcTransportCost()`：

```
transportCost = unitRice × settlementQuantity
（取整方式由 endOfCalculation mixin 的 fomatFloatRoundMode 决定）
```

`watch subtotalConfirm` → `countMoney(subtotalConfirm, taxRate)` → 重算运费差价 `serviceCharge`：

```
total = subtotalConfirm / (1 - taxRate/100) + premiumAmount
serviceCharge = total - subtotalConfirm - premiumAmount
```

### 4. 保存/提交主流程

```
handleSave / handleSubmit
  └── changeWaybillStatus()
        ├── validateForm()               表单校验（单价/结算数量/重量/费用项/货损确认）
        ├── validateOilGasCost()         司机运费 ≥ 实付油气费
        └── checkZeroRounding()
              ├── diffAmount = 0 → checkOrder()
              └── diffAmount ≠ 0 → 弹窗确认抹零
                    └── applyZeroRoundingItem(diffAmount) → checkOrder()

checkOrder()
  └── checkOrderStatus({ waybillIds })
        ├── 有状态问题 → showWModal 警告
        └── 无问题 → riskManagement()
```

### 5. 风控处理流程

```
riskManagement()
  ├── postSaveWaybill(params, busStatus=当前状态)   先保存
  ├── getWaybillRiskInfoList([waybillDetail])       风控测算
  │     传入：settlementWeight、receivableTotalCost
  ├── 有中高风险 && allowPass !== '100'
  │     ├── uni.setStorageSync('riskWarningData', ...)  缓存风控数据
  │     └── uni.navigateTo('/settlementPages/riskwarning/index?fromAdjust=1&submitType=save|submit')
  └── 无风险 / 允许通过
        └── postSubmitAfterRiskPass()
              ├── save   → postSaveWaybill(busStatus='310') → 成功返回上页
              └── submit → postSaveWaybill(busStatus='320') → 成功返回上页
```

风控页回调通过 `uni.setStorageSync('riskWarningData')` 传递参数，风控预警页读取后回调。

### 6. 抹零处理

```
zeroByBusIdMode:
  '0' → 不抹零
  '1' → 小数抹零（取整）
  '2' → 个位抹零（取整到十位）
  '3' → 小数四舍五入到个位
  '4' → 个<5取0，个≥5取5

applyZeroRoundingItem(diffAmount):
  diffAmount > 0 → 追加应收费项（orderNumber: 101，costType: '100'，costCode: 'A10102'）
  diffAmount < 0 → 追加应付费项（orderNumber: 102，costType: '200'，costCode: 'A10202'）

dealZeroModeFn():  实时监测 costList 变化，自动更新抹零费项金额
```

### 7. 亏吨货损处理

| `cargoCompensationConfirmFlag` | 行为 |
|---|---|
| `'1'` 待处理 | 进页面自动弹货损确认弹窗 |
| `'2'` 已确认 | 可点击"亏涨吨情况"行再次查看 |
| 其他 | 不处理 |

```
confirmDamagePopup()
  └── damageForm 表单验证（$refs.damageForm.validate）
        └── updateBmsWaybillPoolKuitonsAndWaybillCost(confirmInfo)
              └── 成功 → updateLoseFlag = true → 刷新详情
```

货损金额联动：`goodsLostValue` 或 `lossWeight` 变化时自动计算 `lossCast = price × (weight/1000)`

### 8. 油气优惠处理

```
updateOilGasDiscountIfNeeded()  （费用确认金额 blur 时触发）
  ├── 判断 oilAmount > 0
  ├── calculateOilRebate({ waybillNo, adjustedAmount: subtotalConfirm, needDetail: 'true' })
  └── 更新 oilGasDiscountAmount

totalAmount = subtotalConfirm + serviceCharge + premiumAmount - oilGasDiscountAmount
（oilGasDiscountAmount 为 -1 时按 0 处理）
```

### 9. 费用明细管理

- 默认费用项（`orderNumber ≤ 10`）：只读，不可删除
- `orderNumber` 为 101/102：抹零费项，禁止编辑和删除
- 新增费用项（`orderNumber > 10`，非 101/102）：可编辑费用类型/费用项目/确认金额，可删除
- 总数上限：20 条
- 费用类型选择器：从字典 `fylx` 加载
- 费用项目选择器：按选中的费用类型动态调用 `getCostProjectDropdown` 接口加载

---

## 计算属性（computed）

| 属性 | 说明 |
|------|------|
| `noticeTitle` | 根据 `busStatus` 映射业务状态文字 |
| `getAuthList` | 从 store 获取权限列表，控制保存/提交按钮显示 |
| `getWaningStatus(riskLevel)` | 返回风控等级对应的样式 class 和文本 |
| `kuiTonsText` | 亏涨吨情况描述（含免赔系数） |
| `splitMainInfo` | 委托转账主体信息展示（脱敏） |
| `splitInfo` | 委托转账规则展示 |
| `subtotalOriginal` | 费用小计原金额（应付 - 应收） |
| `subtotalConfirm` | 费用小计确认金额（应付 - 应收） |
| `shouldShowOilGas` | 是否展示油气优惠行 |
| `totalAmount` | 合计金额（小计 + 差价 + 保障服务 - 油气优惠） |

---

## 权限控制

| 常量 | 功能码 | 控制范围 |
|------|--------|---------|
| `SAVE_BTN_FUNCID` | `1663745633175` | 保存按钮（小程序端） |
| `SUBMIT_BTN_FUNCID` | `1663745593855` | 提交预审按钮 |

H5 端保存按钮固定显示（不走权限控制），小程序端通过 `getAuthList` 判断。

---

## 依赖关系

### 引用组件

| 组件 | 路径 | 作用 |
|------|------|------|
| `LoseAndRiseView` | `@/components/lose-and-rise/view.vue` | 亏涨吨信息展示 |
| `WModal` | `@/settlementPages/components/wModal.vue` | H5 自定义弹窗（替代 uni.showModal） |

### 引用 Mixins

| Mixin | 路径 | 提供能力 |
|-------|------|---------|
| `unitTool` | `@/mixins/unitTool.js` | 结算单位换算（`exGetUnitName`、`exGetUnitPerFixName`、`exGetgoodsQuantity`、`bigNumberWeight`） |
| `endOfCalculation` | `@/mixins/endOfCalculation.js` | 金额取整（`roundingMode`、`fomatFloatRoundMode`、`getCompanyRoundMode`、`countMoney`） |
| `getCurrentEnv` | `@/mixins/getCurrentEnv.js` | 获取当前运行环境（`currentEnv`，控制导航栏是否渲染） |

### 调用 API（`@/api/waybillSettlement`）

| 接口函数 | URL | 说明 |
|---------|-----|------|
| `postWaybillDetails` | `/bms/BmsWaybillPool/viewDetailPool` | 获取运单结算详情 |
| `postSaveWaybill` | `/bms/BmsWaybillPool/adjustBillInformation` | 保存/提交（310=保存，320=结算通过） |
| `dcsOperationRecordPagingexport` | `/bms/OperationRecord/dcsOperationRecordPaging` | 操作记录分页 |
| `updateBmsWaybillPoolKuitonsAndWaybillCost` | `/bms/BmsWaybillPoolKuitons/updateBmsWaybillPoolKuitonsAndWaybillCost` | 确认亏吨货损 |
| `findZeroByBusId` | `/bms/index/dcsToSearch` | 查询抹零配置 |
| `checkBindingCard` | `/bms/bmsWithdrawalRecord/checkBindingCard` | 网络货运绑卡信息查询 |
| `findOneByWaybillId` | `/bms/BmsWaybillPoolKuitons/findOneByWaybillId` | 查询货损确认详情 |
| `getPartPay` | `/bms/bmsNetworkFreightPayment/queryReceiptPayStatus` | 分次支付信息 |
| `checkOrderStatus` | `/woa/station/offerPlan/checkOrderStatus` | 检查运单在德邦平台的状态 |
| `getCostProjectDropdown` | `/bms/BmsCost/getdropDownData` | 费用项目下拉数据（按费用类型动态加载） |
| `calculateOilRebate` | `/oil/oilServiceInter/rebate/calculate` | 计算油气返利金额 |

### 调用 API（其他）

| 接口函数 | 模块路径 | 说明 |
|---------|---------|------|
| `queryWaybillRiskInfoList` | `@/api/risk` | 查询风控信息列表（用于页面初始化时更新 riskLevel） |
| `getWaybillRiskInfoList` | `./risk` | 风控测算（保存提交前调用） |

### Store

| Action/Getter | 说明 |
|--------------|------|
| `common/getDirctionaryIds` | 批量获取字典（`khh` 开户行、`jszl` 结算重量类型、`fylx` 费用类型、`yxzdmlfs` 抹零方式、`fyx` 费用项目） |
| `common/getAuthList` | 获取权限列表 |

---

## 页面间通信

| 方式 | 场景 |
|------|------|
| `uni.$on('editAdjust', getDetails)` | 从修改装卸重量页（editAdjust.vue）返回后刷新详情 |
| `uni.setStorageSync('riskWarningData', ...)` | 传递风控数据到风控预警页 |
| `uni.navigateTo('/settlementPages/riskwarning/index?fromAdjust=1&submitType=...')` | 跳转风控预警页 |
| `uni.navigateTo('/settlementPages/waybillSettlement/editAdjust?...')` | 跳转修改装卸重量页 |
| `uni.navigateTo('/minePages/mine/enRoute/enRoute?waybillId=...')` | 跳转跟踪信息页 |
| `uni.navigateTo('/settlementPages/riskDetail/index?...')` | 跳转风控预警详情页 |

---

## 与 PC 端 edit.vue 的主要差异

| 维度 | App（adjust.vue） | PC（edit.vue） |
|------|------------------|---------------|
| 费用明细 | 内联展示，直接在页面编辑 | 抽离为 `CostMessageDetails` 子组件 |
| 付款方式 | 无独立付款方式面板（仅展示分次支付备注） | 有 `PaymentMethodPanel` 子组件，含等式校验 |
| 风控弹窗 | 跳转独立页面（`riskwarning/index`） | 页面内弹窗（`RiskWarningDialog`） |
| 亏吨弹窗 | 页面内 `u-popup`，含表单校验 | 独立 `loseDialog` 组件 |
| 运单状态警告 | `showWModal`（H5 用自定义 WModal，其他用 uni.showModal） | 独立 `warnTable` 弹窗组件 |
| 操作记录 | 已加载但未在模板中渲染（保留了数据层逻辑） | 独立 `EditMessageDetails` 子组件 |
