# 结算处理 - 查看结算信息页（read.vue）

## 概述

结算处理模块的只读查看页，用于展示单条运单的完整结算信息。页面结构与 `edit.vue` 高度一致，所有字段均为只读状态，无保存/提交流程，适用于核对已处理结算数据。

结算信息区块同样使用 `SettlementInfo.vue` 组件，通过 `:readonly="true"` 和 `:show-edit-actions="false"` 控制全只读展示。

---

## 文件结构

```
src/views/userBase/waybillSettlement/
├── read.vue                        ← 本文件（查看结算信息页）
├── edit.vue                        （调整结算信息页，详见 waybillSettlement-edit.md）
├── index.vue                       （结算列表页）
└── components/
    ├── SettlementInfo.vue          结算信息区块组件（readonly 模式）
    ├── CostMessageDetails.vue      费用明细只读展示
    ├── EditMessageDetails.vue      操作记录子组件
    ├── examResult.vue              预审结果组件
    └── AnchorNav.vue               顶部锚点导航
```

---

## 页面锚点结构

```
anchorWaybillInfo     → 运单信息（运单表格）
anchorSettlementInfo  → 结算信息（SettlementInfo 组件）
anchorCostDetail      → 费用明细（CostMessageDetails 组件）
anchorRiskWarning     → 风控预警（条件显示，有中高风险时插入）
anchorExamResult      → 预审结果
anchorOperationRecord → 操作记录
```

`anchorNavList` 计算属性根据 `showRiskWarning` 动态插入风控锚点，与 `edit.vue` 逻辑完全一致。

---

## 核心逻辑

### 1. 页面初始化（mounted）

```
getCompanyRoundMode()    → 获取金额取整方式（传给 CostMessageDetails 用于展示格式化）
loadStatusOption()       → 加载枚举字典
getDetails()             → 加载运单详情、费用明细、结算信息
getPartPay()             → 获取分次支付数据（仅用于展示）
```

> read.vue 不调用 `getZeroByBusId`，因为只读模式不需要抹零处理。

### 2. 与 SettlementInfo 组件的通信

read.vue 使用 `:readonly="true"` 和 `:show-edit-actions="false"` 将 SettlementInfo 切入全只读模式，不监听任何事件：

```html
<SettlementInfo
  :readonly="true"
  :show-edit-actions="false"
  :form-model="formModel"
  :detail="detail"
  :dictionary="dictionary"
  :bind-card-info="bindCardInfo"
  :new-company-off-line-datas="newCompanyOffLineDatas"
  :split-main-info="splitMainInfo"
  :split-info="splitInfo"
  :btn-loading="btnLoading"
  :waybill-id="$route.query.waybillId"
  :show-down-btn="controlBtn.btnDownload"
/>
```

### 3. getDetails 数据处理

流程与 `edit.vue` 基本一致，主要差异：

- `formModel.accountName` 直接赋值为 `detail.accountName`（文本，不经过绑卡/结算主体下拉逻辑）
- 不调用 `checkMemberStatus` / `checkBindingCardInfo`（无需校验绑卡）
- 不调用 `findOneByWaybillId`（无亏吨货损确认弹窗）
- 费用明细 `busCost` 统一用 `parsePrice` 格式化展示（不保留 toFixed(2) 编辑态）
- 风控数据通过 `queryWaybillRiskInfoList` 获取后赋给 `highMidWaybillListPage`，仅用于页面内 `RiskWarning` 组件展示

`kuiTonsSituationVO` 和 `lsdsGoodsDeductible` 从 `detail` 同步到 `formModel`，供 `SettlementInfo` 读取：

```js
this.formModel.kuiTonsSituationVO = this.detail.kuiTonsSituationVO || null
this.formModel.lsdsGoodsDeductible = this.detail.lsdsGoodsDeductible || null
```

### 4. 图片预览

装车净重、卸车净重、运单签收信息三列均可点击，调用 `handleLookImg` 获取附件后通过 `el-image-x` 组件弹出预览：

```
handleLookImg(scope, btnType)
  → getAttachmentsByWaybillId({ waybillId, wabillStatus, operAttachmentType, transportType })
  → 组装 imgList + imgListUrl
  → $refs.previewRef.clickHandler()
```

图片预览顶部标题通过 `el-image-x` 的 `#slot-html` slot 展示当前图片名称（`urlTxt`），切换图片时 `prevLoadImg` / `nextLoadImg` 回调更新标题。

### 5. 操作记录

与 `edit.vue` 完全一致：仅展示 2024-02-01 之后创建的运单的操作记录，分页通过 `handleCurrentChange` 驱动。

---

## 与 edit.vue 的差异对照

| 维度 | edit.vue | read.vue |
|------|----------|----------|
| `SettlementInfo` 模式 | `readonly=false` `show-edit-actions=true` | `readonly=true` `show-edit-actions=false` |
| 结算主体赋值 | 含绑卡状态/手机号拼接 | 直接用 `detail.accountName` |
| 绑卡状态检查 | 调 `checkMemberStatus` + `checkBindingCardInfo` | 不调用 |
| 亏吨货损弹窗 | flag='1' 自动弹，支持手动再次打开 | 不弹 |
| 风控展示 | `RiskWarning`（页面内）+ `RiskWarningDialog`（弹窗） | 仅页面内 `RiskWarning` |
| 抹零处理 | 有（`getZeroByBusId`） | 无 |
| 修改装卸重量 | `EditLoadWeight` 弹窗（满足条件时显示） | 不显示修改按钮 |
| 底部按钮 | 取消 / 保存 / 提交 | 仅返回 |
| `getPartPay` 作用 | 联动付款方式计算 | 仅用于展示 |
| 费用 `busCost` 格式化 | `toFixed(2)` 编辑态 | `parsePrice` 展示态 |
| `once` 标志位 | 由 `updBusCostInput` 置为 false | 永远不会被置为 false（无编辑操作） |

---

## 依赖关系

### 引用组件

| 组件 | 路径 | 作用 |
|------|------|------|
| `SettlementInfo` | `./components/SettlementInfo` | 结算信息区块（readonly 模式） |
| `CostMessageDetails` | `./components/CostMessageDetails` | 费用明细只读展示 |
| `EditMessageDetails` | `./components/EditMessageDetails` | 操作记录列表 |
| `ExamResult` | `./components/examResult` | 预审结果展示 |
| `RiskWarning` | `@/components/Risk/riskWarning` | 页面内风控预警展示 |
| `AnchorNav` | `./components/AnchorNav` | 顶部锚点导航 |

### 引用 Mixins

| Mixin | 路径 | 提供能力 |
|-------|------|---------|
| `endOfCalculation` | `@/mixins/endOfCalculation.js` | 金额取整（`roundingMode`、`BNumber`、`getCompanyRoundMode`） |
| `unitTool` | `@/mixins/unitTool.js` | 结算单位换算（`exGetUnitName`、`exValidatorWeight` 等） |

### 调用 API

| 接口函数 | 模块 | 说明 |
|---------|------|------|
| `postWaybillDetails` | `userBase.waybillSettlement` | 获取运单结算详情（含费用明细） |
| `dcsOperationRecordPagingexport` | `userBase.waybillSettlement` | 操作记录分页 |
| `getNewFreightAmount` | `userBase.waybillSettlement` | 获取新运费金额（仅在 `updBusCostInput` 里调，read 模式实际不触发） |
| `getShipperName` | `userBase.supplymanagement` | 结算主体下拉（read 模式不调用，分支在 `type !== 'read'`） |
| `getAttachmentsByWaybillId` | `userBase.transport` | 获取装卸/签收附件 |
| `getPartPay` | `userBase.driverSupplymanagement` | 获取分次支付数据 |
| `queryWaybillRiskInfoList` | `@/components/Risk/riskTools` | 风控数据查询 |

---

## 数据流转

```
路由参数（waybillPoolId / waybillId / type='read' / riskLevel）
  ↓
getDetails()  →  detail（运单主信息）
                 responseRecordList（费用明细，busCost 用 parsePrice 格式化）
                 formModel（表单绑定数据，全部只读）
  ↓
SettlementInfo（readonly=true）→ 展示所有结算字段，无交互
CostMessageDetails             → 只读展示费用明细
RiskWarning（条件显示）        → 展示中高风险预警
ExamResult                     → 展示预审结果
EditMessageDetails             → 展示操作记录

点击运单号 → handleLook → window.open 运单详情页
点击装/卸重/签收 → handleLookImg → el-image-x 预览
点击返回 → handleClose → $router.back(-1)
```

---

## 注意事项

1. **`bindCardInfo` 初始值**：read.vue 中 `bindCardInfo` 初始化为 `{ isBindCard: true, payeePhone: '' }`，传给 `SettlementInfo` 仅用于展示，不影响只读逻辑
2. **`newCompanyOffLineDatas`**：read.vue 不走绑卡/结算主体下拉流程，但仍需初始化传入，避免 `SettlementInfo` 组件报错
3. **风控 `riskLevel`**：从路由 query 取，控制 `showRiskWarning` 是否展示风控区块和锚点
4. **`once` 标志位**：read.vue 中 `watch` 仍然存在（共享 `formModel`），但因为没有编辑操作，`once` 永远不会被置为 false，所以 watch 回调实际上不会执行计算
5. **isInMicroApp**：微应用内点击车牌号不跳转车辆监控（`v-if="!isInMicroApp"` 隐藏链接），点击运单号/跟踪信息使用 `gotoWaybillDetail`

---

## 相关文档

- [调整结算信息页](./waybillSettlement-edit.md)
- [CostMessageDetails 组件](./CostMessageDetails组件.md)

---

**文档版本**: v1.0
**最后更新**: 2025-07
