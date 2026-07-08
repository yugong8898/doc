# 运单结算处理模块（waybillSettlement）总览 — App 端

## 概述

货主 App（`wlyd-app-consigner`）的运单结算处理模块，位于 `settlementPages/waybillSettlement/`，负责结算信息的查看与调整。功能对标 PC 端 `logisticsweb/src/views/userBase/waybillSettlement/`，但由于移动端交互限制，架构上做了相应简化。

---

## 文件结构

```
settlementPages/waybillSettlement/
├── index.vue        结算信息展示页（旧版，含运输信息/费用/收款人等，独立弹窗交互）
├── adjust.vue       调整结算信息页（新版，对标 PC edit.vue）
├── read.vue         查看结算信息页（新版，对标 PC read.vue）
├── editAdjust.vue   修改装卸货净重页
└── risk.js          风控工具函数（风险项定义 + 风控测算逻辑）
```

> `index.vue` 为早期版本，页面内内联所有逻辑，目前结算主流程已由 `adjust.vue` / `read.vue` 承接。

---

## 页面导航关系

```
结算列表（pages/settlement/settlement）
  ├── 调整结算信息 → settlementPages/waybillSettlement/adjust.vue
  │     └── 修改装卸货净重 → settlementPages/waybillSettlement/editAdjust.vue
  │           └── 保存后 uni.$emit('editAdjust') → adjust.vue 刷新详情
  ├── 查看结算信息 → settlementPages/waybillSettlement/read.vue
  └── 风控预警详情 → settlementPages/riskDetail/index
        ├── 从 adjust.vue 跳入（isView 无值）：可操作
        └── 从 read.vue 跳入（isView=1）：只读

adjust.vue 保存/提交 → 风控预警 → settlementPages/riskwarning/index?fromAdjust=1&submitType=save|submit
  └── 风控页确认后：根据 uni.getStorageSync('riskWarningData').btnTypeClicked 决定保存还是提交
```

---

## 三大页面说明

### adjust.vue — 调整结算信息页

**职责**：结算模块核心编辑页，支持调整单价/结算数量/结算重量/费用明细，含保存与提交预审流程。

**核心能力**：
- 单价/结算数量变化 → 实时重算运费（`calcTransportCost`）
- 小计变化 → 实时重算运费差价（`countMoney`，基于 `taxRate`）
- 费用确认金额 blur → 实时查询油气返利（`updateOilGasDiscountIfNeeded`）
- 完整的保存/提交链路：表单校验 → 油气费校验 → 抹零处理 → 运单状态检查 → 风控测算 → 提交
- 亏吨货损：`flag='1'` 时自动弹出确认弹窗，`flag='2'` 可点击行再次查看
- 费用明细管理：支持新增/删除，费用类型/项目按需动态加载

详细文档：[waybillSettlement-adjust.md](./waybillSettlement-adjust.md)

---

### read.vue — 查看结算信息页

**职责**：结算信息纯只读展示，结构与 `adjust.vue` 一致，所有字段均为静态文本。

**核心特点**：
- 无编辑、无保存/提交按钮
- 展示内容：结算信息、费用明细（原金额/调整金额/确认金额）、分次支付备注、运费差价、保障服务、合计
- 油气优惠：展示 `detail` 返回的静态值（不实时计算）
- 风控预警：展示初始 `riskLevel`，可点击跳转 `riskDetail`（isView=1 只读）

详细文档：[waybillSettlement-read.md](./waybillSettlement-read.md)

---

### editAdjust.vue — 修改装卸货净重页

**职责**：独立页面用于修改装卸货净重，保存后通过 `uni.$emit('editAdjust')` 通知 `adjust.vue` 刷新。

---

### risk.js — 风控工具函数

**职责**：集中管理风控相关逻辑，供 `adjust.vue` 调用。

**导出内容**：

| 导出项 | 说明 |
|--------|------|
| `SETTLE_RISK_WARNING_ITEMS` | 结算场景风险项配置（R10001/R100/R10006/R10012 等 12 个风控项） |
| `PRELIMINARY_RISK_WARNING_ITEMS` | 预审场景风险项配置（含额外的 R10014 车辆轨迹合规） |
| `getWaybillRiskInfoList(selectItems, queryFirst)` | 批量风控测算，返回包含 riskItems/allowPass/highRiskCount 等的 Promise |
| `riskCal(queryFirst, waybillInfo)` | 单运单风控计算（支持先查询再测算，或直接测算） |
| `orderByRiskSort(riskList)` | 按 riskSort 升序排列风控项 |
| `getValidRiskDealArr(arr)` | 过滤 ossKey 不为空的处理结果 |

**风控测算流程**：
```
getWaybillRiskInfoList(selectItems)
  └── riskCal(queryFirst, waybillInfo)
        ├── queryFirst=true → queryRisk()  先查历史风控结果
        └── 无历史结果 或 queryFirst=false → riskCalculate()  重新测算
              传入：settlementWeight、receivableTotalCost、paymentLimitVo 等
              返回：riskList（各风控项结果）+ highCount/middleCount/lowCount/allowPass
```

---

## 数据流转

```
路由入参：waybillPoolId + waybillId + riskLevel
  ↓
onLoad 初始化
  ├── getCompanyRoundMode()    金额取整方式（endOfCalculation mixin）
  ├── loadNecessaryEnums()     字典（khh / jszl / fylx）
  ├── loadZeroTypeObj()        抹零方式字典
  ├── getDetails() || loadCostEnums()    并行
  ├── getRecordPaging()        操作记录
  └── loadPartPay()            分次支付文本
  ↓
用户操作（adjust.vue）
  ├── 修改单价/结算数量 → calcTransportCost() → 运费更新
  ├── 小计变化 → countMoney() → serviceCharge 更新
  ├── 确认金额 blur → updateOilGasDiscountIfNeeded() → oilGasDiscountAmount 更新
  └── 修改费用项 → dealZeroModeFn() → 抹零费项实时更新
  ↓
保存/提交
  validateForm → validateOilGasCost → checkZeroRounding
  → checkOrder → riskManagement
      ├── postSaveWaybill(当前 busStatus)  先保存
      ├── 有中高风险 → 跳转 riskwarning/index（缓存风控数据）
      └── 无风险 → postSubmitAfterRiskPass → postSaveWaybill(310/320) → 返回上页
```

---

## 接口汇总（`@/api/waybillSettlement`）

| 接口函数 | URL | 使用页面 |
|---------|-----|---------|
| `postWaybillDetails` | `/bms/BmsWaybillPool/viewDetailPool` | adjust / read |
| `postSaveWaybill` | `/bms/BmsWaybillPool/adjustBillInformation` | adjust |
| `dcsOperationRecordPagingexport` | `/bms/OperationRecord/dcsOperationRecordPaging` | adjust / read |
| `updateBmsWaybillPoolKuitonsAndWaybillCost` | `/bms/BmsWaybillPoolKuitons/updateBmsWaybillPoolKuitonsAndWaybillCost` | adjust |
| `findOneByWaybillId` | `/bms/BmsWaybillPoolKuitons/findOneByWaybillId` | adjust |
| `findZeroByBusId` | `/bms/index/dcsToSearch` | adjust |
| `checkBindingCard` | `/bms/bmsWithdrawalRecord/checkBindingCard` | adjust |
| `getPartPay` | `/bms/bmsNetworkFreightPayment/queryReceiptPayStatus` | adjust / read |
| `checkOrderStatus` | `/woa/station/offerPlan/checkOrderStatus` | adjust |
| `getCostProjectDropdown` | `/bms/BmsCost/getdropDownData` | adjust |
| `calculateOilRebate` | `/oil/oilServiceInter/rebate/calculate` | adjust |
| `updateWeight` | `/bms/BmsWaybillPool/updateWeight` | editAdjust |

---

## Mixin 依赖

| Mixin | 路径 | 提供能力 |
|-------|------|---------|
| `unitTool` | `@/mixins/unitTool.js` | 计价单位换算（`exGetUnitName`、`bigNumberWeight`、`exGetgoodsQuantity` 等） |
| `endOfCalculation` | `@/mixins/endOfCalculation.js` | 金额取整（`roundingMode`、`fomatFloatRoundMode`、`getCompanyRoundMode`） |
| `getCurrentEnv` | `@/mixins/getCurrentEnv.js` | 当前运行环境（`currentEnv`，控制自定义导航栏渲染） |

---

## 与 PC 端的模块对应关系

| App 端 | PC 端 | 差异说明 |
|--------|-------|---------|
| `adjust.vue` | `edit.vue` | App 无独立付款方式面板；风控跳独立页；费用明细内联 |
| `read.vue` | `read.vue` | 基本一致，App 更精简 |
| `editAdjust.vue` | `editLoadWeight.vue`（弹窗） | PC 端为弹窗组件，App 端为独立页面 |
| `risk.js` | `@/components/Risk/riskTools.js` | App 端风控逻辑内聚到本目录 |
| `index.vue`（旧版） | `index.vue`（列表页） | App 旧版为纯展示，无列表筛选能力 |

---

## 业务状态码（busStatus）

| 值 | 含义 |
|----|------|
| 99 | 未回单 |
| 100 | 待核对 |
| 110 | 待审核 |
| 120 | 审核不通过 |
| 130 | 审核通过 |
| 200 | 待对账 |
| 210 | 对账退回 |
| 220 | 对账通过 |
| 300 | 待处理 |
| 310 | 已保存（保存操作写入值） |
| 320 | 结算通过（提交操作写入值） |
| 330 | 待预审 |
| 340 | 预审不通过 |

---

## 注意事项

1. **操作记录已加载但未渲染**：`adjust.vue` 和 `read.vue` 均有 `getRecordPaging()` 逻辑和 `editItems` 数据，但模板中未展示，保留了数据层以备后续扩展。
2. **风控数据缓存传递**：App 端风控弹窗改为独立页面，数据通过 `uni.setStorageSync('riskWarningData')` 传递，风控页读取后根据 `btnTypeClicked` 决定回调类型（save/submit）。
3. **H5 vs 小程序差异**：H5 端保存按钮固定显示，不走权限控制；小程序端通过 `getAuthList` 判断 `SAVE_BTN_FUNCID` 权限。H5 端弹窗使用自定义 `WModal` 组件代替 `uni.showModal`。
4. **全流程运单**：`listWaybillPoolAndTmsWaybill` 接口中硬编码 `fullProcessFlag=20`，App 端暂不展示全流程运单。
5. **结算重量单位**：接口传参时重量单位为克（kg），页面展示时统一除以 1000 转为吨；提交时 `settlementWeight` 需乘以 1000 转回克，保留 4 位小数。

---

## 相关文档

- [调整结算信息页（adjust.vue）](./waybillSettlement-adjust.md)
- [查看结算信息页（read.vue）](./waybillSettlement-read.md)
- [PC 端结算模块总览](../logisticsweb/waybillSettlement模块总览.md)
- [PC 端调整结算信息页（edit.vue）](../logisticsweb/waybillSettlement-edit.md)
- [PC 端费用明细组件（CostMessageDetails）](../logisticsweb/CostMessageDetails组件.md)
- [wlyd-app-consigner 项目总览](./项目总览.md)

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
