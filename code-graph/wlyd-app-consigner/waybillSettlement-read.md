# 结算处理 - 查看结算信息页（read.vue）

## 概述

货主 App（`wlyd-app-consigner`）结算模块的只读查看页，对标 PC 端 `read.vue`。  
以纯展示模式呈现运单的结算信息、费用明细、分次支付备注、合计金额，以及风控预警入口。无任何编辑或提交操作。

---

## 文件结构

```
settlementPages/waybillSettlement/
├── adjust.vue       （调整结算信息页）
├── read.vue         ← 本文件（查看结算信息页）
├── index.vue        （结算列表页）
├── editAdjust.vue   （修改装卸重量页）
└── risk.js          （风控工具函数）
```

---

## 页面入口

| 参数 | 说明 |
|------|------|
| `waybillPoolId` | 结算池 ID，必填，用于查询详情 |
| `waybillId` | 运单号，用于查询分次支付信息 |
| `riskLevel` | 初始风控等级（`0/200/300/400`），可选 |

---

## 核心流程

### 1. 初始化（onLoad）

```
loadNecessaryEnums()   → 加载字典（开户行 khh、费用类型 fylx）
getDetails()           → 加载运单详情，初始化 formModel 和 costList
getRecordPaging()      → 加载操作记录（2024-02-01 后的运单才加载）
loadPartPay()          → 加载分次支付信息（预付/回单付/到付文本）
loading = false        → 隐藏骨架屏，渲染实际内容
```

### 2. 详情加载（getDetails）

```
postWaybillDetails({ waybillPoolId })
  └── initFormModel()    → 表单字段赋值（单价/重量/结算主体/银行卡/委托转账等）
  └── initCostList()     → 费用明细格式化（原金额/调整金额/确认金额/费用类型文本）
```

### 3. 分次支付（loadPartPay）

```
getPartPay({ busBillId: waybillId })
  └── type === '10' → partPayPreText     预付文本（"预付：自定义金额 xx 元" 或 "预付：无"）
  └── type === '20' → partPayReceiptText 回单付文本（"回单付：自定义金额 xx 元" 或 "回单付：无"）
到付固定展示：到付：除预付和回单付以外未付运费
```

---

## 数据展示结构

### 结算信息区块

| 字段 | 数据来源 | 说明 |
|------|---------|------|
| 单价 | `formModel.unitRice` | 含计价单位（元/吨、元/柜、元/车） |
| 结算数量 | `formModel.settlementQuantity` | 含计价单位 |
| 结算重量 | `formModel.settlementWeight` | 仅 `settlementType !== '10'` 时展示 |
| 运费 | `formModel.transportCost` | |
| 结算重量类型 | `formModel.settlementWeightType` | 字典 `settlementWeightTypeMap` 映射 |
| 装货净重 | `formModel.loadWeight` | 克→吨（÷1000） |
| 卸货净重 | `formModel.unloadWeight` | 克→吨（÷1000） |
| 下单净重 | `formModel.transportWeight` | 克→吨（÷1000） |
| 结算主体 | `formModel.accountName` | |
| 收款人开户行 | `formModel.openBankName` | 字典 `bankMap` 映射（`khh`） |
| 收款银行卡号 | `formModel.bankAccount` | |
| 亏涨吨情况 | `kuiTonsText`（computed） | 非 transportType 4/5 时展示；含免赔系数 |
| 货源别名 | `formModel.orderAlias` | |
| 运单别名 | `formModel.waybillAlias` | |
| 备注 | `formModel.remark` | |

### 费用信息区块

| 字段 | 数据来源 | 说明 |
|------|---------|------|
| 费用类型 | `item.costTypeText` | 字典 `costTypeMap` 映射（`fylx`） |
| 费用项目 | `item.costName` | |
| 原金额 | `item.busCostOriginal` | 负数时红色标注 |
| 调整金额 | `item.updBusCostDiff` | 负数时红色标注 |
| 确认金额 | `item.updBusCost` | |
| 费用备注 | `item.confirmRemark` | |
| 小计 | `subtotalOriginal` / `subtotalConfirm`（computed） | 应付(200,600) - 应收(100,500) |
| 分次支付备注 | `partPayPreText` / 固定到付文本 / `partPayReceiptText` | 有 partPayData 时展示 |
| 运费差价 | `detail.serviceCharge` | 含差价率 |
| 货物保障服务 | `detail.listPremiumAmount` | |
| 货物保障服务购买方 | `detail.premiumBuyer` | |
| 合计 | `totalAmount`（computed） | |

---

## 计算属性（computed）

| 属性 | 说明 |
|------|------|
| `noticeTitle` | 根据 `busStatus` 映射业务状态文字（展示在顶部通知栏） |
| `getWaningStatus(riskLevel)` | 风控等级对应的 class 和文本 |
| `kuiTonsText` | 亏涨吨情况描述。开启免赔时展示 `lossType + lossNumber + 免赔系数`；未开启时展示 `lossNumber + (未设置亏吨免赔)` |
| `settlementMethod` | 结算方式（先付/到付/回单付），映射 `detail.settlement` |
| `splitMainInfo` | 委托转账主体（名称/脱敏卡号/渠道名称），`splitFlag === '10'` 时有效 |
| `splitInfo` | 委托转账规则（全额运费 / 元/车 / 单价单位） |
| `subtotalOriginal` | 费用小计原金额（BigNumber 精确计算） |
| `subtotalConfirm` | 费用小计确认金额（BigNumber 精确计算） |
| `shouldShowOilGas` | 是否展示油气优惠行（oilAmount > 0 且 oilDiscountAmount ≠ -1） |
| `oilGasDiscountAmount` | 油气优惠金额（取自 `detail` 或 `bmsWaybillPoolExt`） |
| `totalAmount` | 合计 = subtotalConfirm + serviceCharge + premiumAmount - oilGasDiscountAmount |

---

## 页面交互

| 操作 | 说明 |
|------|------|
| 跟踪信息 | `handleTrackInfo()` → 跳转 `/minePages/mine/enRoute/enRoute?waybillId=...` |
| 风控预警 | `handleRiskDetail()` → 低风险不跳转；中高风险跳转 `/settlementPages/riskDetail/index?waybillId=...&riskLevel=...&isView=1` |

---

## 依赖关系

### 引用 Mixins

| Mixin | 路径 | 提供能力 |
|-------|------|---------|
| `unitTool` | `@/mixins/unitTool.js` | `exGetUnitName`、`exGetUnitPerFixName`、`exGetgoodsQuantity`、`bigNumberWeight` |
| `getCurrentEnv` | `@/mixins/getCurrentEnv.js` | `currentEnv`（控制导航栏是否渲染） |

### 调用 API（`@/api/waybillSettlement`）

| 接口函数 | URL | 说明 |
|---------|-----|------|
| `postWaybillDetails` | `/bms/BmsWaybillPool/viewDetailPool` | 获取运单结算详情（含费用明细） |
| `dcsOperationRecordPagingexport` | `/bms/OperationRecord/dcsOperationRecordPaging` | 操作记录分页 |
| `getPartPay` | `/bms/bmsNetworkFreightPayment/queryReceiptPayStatus` | 分次支付信息（预付/回单付） |

### Store

| Action | 说明 |
|--------|------|
| `common/getDirctionaryIds` | 批量获取字典（`khh` 开户行、`fylx` 费用类型） |

---

## 与 adjust.vue 的主要差异

| 维度 | read.vue | adjust.vue |
|------|---------|------------|
| 页面性质 | 纯只读查看 | 可编辑调整 |
| 结算信息 | 全部静态文本展示 | 单价/结算数量/结算重量可编辑 |
| 费用明细 | 静态展示，无操作按钮 | 可新增/删除/编辑费用项 |
| 底部按钮 | 无 | 保存 + 提交预审 |
| 货损弹窗 | 无 | 有（`u-popup` 含表单校验） |
| 装卸重量修改 | 无 | 标题栏有"修改装卸货净重"入口 |
| 抹零处理 | 无 | 有（`dealZeroModeFn`，实时监测） |
| 风控测算 | 无（仅展示初始 riskLevel） | 保存/提交前调用 `getWaybillRiskInfoList` |
| 油气优惠 | 展示 `detail` 返回的静态值 | 费用确认金额 blur 时实时调接口重算 |
| 运费差价 | 展示 `detail.serviceCharge` | 小计变化时联动重算（`countMoney`） |
| 字典加载 | `khh` + `fylx` | `khh` + `jszl` + `fylx` + `yxzdmlfs` + `fyx` |
| 操作记录 | 加载并保留在 `editItems`（模板中未渲染） | 同左 |
| 委托转账 | 展示（`splitFlag === '10'` 时） | 同左（只读展示，不可编辑） |
