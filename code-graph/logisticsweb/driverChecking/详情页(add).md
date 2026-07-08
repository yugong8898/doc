# 司机对账 - 详情页（add.vue）

## 概述

详情页路由：`/userBase/driverChecking/:action/:id`，通过 `$route.params.action` 区分三种模式，复用同一组件。

```
/userBase/driverChecking/read/:id    → 查看
/userBase/driverChecking/verify/:id  → 核对（可编辑确认金额）
/userBase/driverChecking/check/:id   → 审核（填写审核结果）
```

---

## 一、三种模式对比

| 维度 | read（查看） | verify（核对） | check（审核） |
|------|------------|--------------|-------------|
| 费用表确认金额列 | 只读展示 | **可编辑 el-input** | 只读展示 |
| 费用表备注列 | 只读 | **可编辑** | 只读 |
| 审核结果表单 | 不显示 | 不显示 | **显示且可填** |
| 保存按钮 | 隐藏 | 显示（需权限 `save`） | 隐藏 |
| 提交审核按钮 | 隐藏 | 显示（需权限 `commit`） | 隐藏 |
| 确定按钮 | 隐藏 | 隐藏 | 显示（需权限 `confirm`） |
| 返回按钮 | 显示 | 显示 | 显示 |
| 特殊汇总行 | 显示（网货） | 不显示 | 显示（网货） |

---

## 二、页面初始化（mounted）

```
loadStatusOption()         加载枚举字典（运输类型、开户行、费用类型、车辆类型等）
getPartPay()               获取分次付款数据（预付/回单付/到付）
getDetail()
  → constManagement.driverChecking.getDetail(request)
  → 按 transportType + settlementType 动态替换 formList[9~11]
  → 处理 bmsBusinessCostList：补空小计行、格式化金额（busCost / updBusCost）
  → fetchOilGasConfig()    获取油气返利配置（决定油气优惠行是否显示）
  → $total()               计算并追加特殊汇总行（仅 action !== 'verify' 且网货）
  → getRecord()            加载操作记录（仅 createDate >= 2024-02-01 的运单）
```

---

## 三、运单信息区（formList）

布局固定 4 列一行，默认 6 行（24 个字段）；无委托转账时（`splitFlag !== '10'`）删除最后 2 项改为 5 行。

### 3.1 字段列表

| prop | label | 说明 |
|------|-------|------|
| `waybillId` | 运单号 | 蓝色可点击，跳转运单详情 |
| `payeeNames` | 结算主体 | 蓝色可点击，调 `getSettlementDetail()` |
| `sendCarDate` | 派车日期 | `formatToDate().format('yyyy-MM-dd HH:mm')` |
| `zcsj` | 装货时间 | 同上 |
| `receiptDate` | 回单日期 | 同上 |
| `transportType` | 运输类型 | `codeFormat('transportType', val)` |
| `$startEnd` | 出发地-目的地 | `$startEnd(sendAddrShorthand, receiveAddrShorthand)` |
| `busNumber` | 车牌号/船名航次/铁路运单号 | 铁路/水运直接展示；公路蓝色跳转车辆监控；微应用内不跳转 |
| `dcCarrierCompanyName` | 司机 | 直接展示 |
| `goodsName` | 货物明细 | `renderRowInfo(model)` |
| `settlementWeight` | 结算重量（吨） | `exValidatorWeight()`；按结算类型动态替换 label/prop |
| `settlementQuantity` | 结算数量（吨） | `exValidatorWeight()`；按结算类型动态替换 |
| `unitRice` | 单价(元/吨) | `parsePrice()`；按结算类型动态替换 label |
| `lsdsGoodsDeductibleTxt` | 亏吨免赔 | type=text；label 含单位后缀 |
| `loadWeight` | 装货净重（吨） | 蓝色可点击 → `handleLookImg(model, '1')` 查看附件照片 |
| `unloadWeight` | 卸货净重（吨） | 蓝色可点击 → `handleLookImg(model, '2')` |
| `$otherKuiTonsRatio` | 亏涨吨情况 | 四种展示状态，见下方说明 |
| `orderAlias` | 货源别名 | tooltip 长文本（超 20 字截断） |
| `waybillAlias` | 运单别名 | 同上 |
| `goodsRemark` | 备注 | 同上 |
| `splitCollectionInfo` | 委托转账主体 | `splitFlag='10'` 时显示；名称/账号（脱敏可切换）/支付渠道 |
| `splitType` | 委托转账规则 | `splitFlag='10'` 时显示；颜色：`renewTimes>0` 红色，`splitType='10'` 黑色，否则橙色 |
| `preExamTime` | 预审通过时间 | `formatToDate().format('yyyy-MM-dd HH:mm')` |

### 3.2 结算类型（settlementType）动态替换规则

`getDetail` 内处理 `formList[9~11]`（结算重量/结算数量/单价字段）：

| settlementType | 替换内容 |
|---------------|---------|
| `10`（吨） | 默认不替换，label 含"吨" |
| `20`（柜） | 结算数量→"（柜）"，单价→"（元/柜）"，增加柜型/数量字段 |
| `30`（车） | 结算数量→"（车）"，单价→"（元/车）"，增加柜型/数量字段 |
| 方（体积） | 结算重量保留，结算数量→"（方）"，单价→"（元/方）" |

### 3.3 亏涨吨情况（`$otherKuiTonsRatio`）四种表现

| 表现 | 出现条件 |
|------|---------|
| 未设置亏吨免赔 | `otherKuiTonsRatioShow=true` 但 `lsdsGoodsDeductible.enable !== 1` |
| 空白 | 免赔已开启，但 `loadWeight`/`unloadWeight` 缺值、`transportType=1/2` 或 `kuiTonsSituationVO.lossType` 无值 |
| 亏吨/涨吨 XX 千克 | 免赔已开启，`kuiTonsSituationVO` 有有效 `lossType`/`lossNumber` |
| 正常 | 同上，`lossType` 为"正常"，不标红 |

---

## 四、费用信息区（bmsBusinessCostList）

使用 `primitive-table` 组件，列配置来自 `add.conf.js`。

### 4.1 表格列配置

| prop | label | verify 模式 | read/check 模式 |
|------|-------|-----------|----------------|
| `aa` | 序号 | 从 1 开始；最后一行"小计" | 同左；特殊行显示文字（小计/运费差价/合计等） |
| `costName` | 费用项目 | 只读；tooltip 含 `asCostName` | 同左 |
| `costType` | 费用类型 | `costType.count=true` 时显示数值，否则 `codeFormat` | 同左 |
| `busCost` | 原金额（元） | `parsePrice(parsePriceReduction(busCost))`；负数标红 | 同左 |
| `$adjustCost` | 确认金额（元） | **`el-input` 可编辑**；`@input` 触发 `updBusCostInput`；特殊行展示汇总值 | 只读文本；特殊行展示汇总值 |
| `updBusCost` | 调整金额（元） | **`el-input` 可编辑** | 只读；特殊行展示备注文案 |
| `confirmRemark` | 费用备注 | **`el-input` 可编辑** | 只读 |
| `$files` | 附件 | 展示附件列表 | 同左 |
| `updateName` | 操作人 | 直接显示 | 同左 |
| `updateDate` | 操作时间 | `formatToDate().format('yyyy-MM-dd HH:mm')` | 同左 |

### 4.2 特殊汇总行（仅 `action !== 'verify' && freightType === '2'`）

由 `add.format.js $total()` 在 `bmsBusinessCostList` 末尾追加，通过 `specialRowType` 字段标识。首列合并"序号+费用项目"两列（`spanMethod` 控制）。

| specialRowType | 显示文字 | 确认金额取值 | 显示条件 |
|----------------|---------|------------|---------|
| `subtotal` | 小计 | 前端累加计算 | 始终 |
| `freightDiff` | 运费差价 | `serviceCharge`（`v-mask-star` 脱敏） | `companyType !== 1` |
| `insurance` | 货物保障服务金额 | `premiumAmount`（全流程为 0） | `premiumBuyerType === '10'` |
| `oilDiscount` | 油气优惠 | `-oilDiscountAmount`（`-1` 时显示 `--`） | 有有效油气数据 或 全流程（金额强制为 0） |
| `total` | 合计 | 小计 + 差价 + 保障 - 油气 | `companyType !== 1` |
| `fpDiff` | 全流程运费差价 | `fpFreightDiffAmt` | `fullProcessFlag === 10` |
| `shipperPay` | 客户应付运费 | `payableFpFreight` | 全流程 `companyType === 2` |
| `carrierPay` | 应付承运商运费 | `payableFpFreight`（加粗） | 全流程 `companyType === 1` |

特殊行备注列额外内容：

| specialRowType | 备注列额外显示 |
|----------------|-------------|
| `subtotal` | 若 `premiumBuyerType === '20'` 追加"含司机购买货物保障服务金额 X 元" |
| `subtotal`（verify） | tooltip 展示付款方式（预付/到付/回单付）说明 |
| `oilDiscount` | "油气实际使用 X 元" |
| `fpDiff` | "差价率：X%" |
| `shipperPay` | "上游客户名称：XXX" |
| `carrierPay` | "承运商名称：XXX" |

---

## 五、付款方式（PaymentMethodPanel）

只读展示，数据来自 `getPartPay()` 接口：

| type | 说明 |
|------|------|
| `10` | 预付款 |
| `20` | 回单付 |
| `30` | 到付 |

---

## 六、操作流程

### 6.1 核对（verify）

```
保存（save）
  → form.validate()
  → constManagement.driverChecking.save(request)

提交审核（verify）
  → form.validate()
  → constManagement.driverChecking.verify(request)
  → 成功后 goBack()
```

### 6.2 审核（check）

```
确定（check）
  → form.validate()
  → constManagement.driverChecking.check(request)
    request 包含 bmsReview: { reviewResult, reviewRemark }
  → 成功后 goBack()
```

---

## 七、操作记录

`getRecord()` 调 `constManagement.recordNew` 接口，仅加载 `createDate >= 2024-02-01` 的运单的操作记录。分页通过 `handleCurrentChange` 驱动。

---

## 八、接口汇总

| 接口函数 | 说明 |
|---------|------|
| `constManagement.driverChecking.getDetail` | 获取详情（运单信息 + 费用列表） |
| `constManagement.driverChecking.save` | 保存（核对暂存） |
| `constManagement.driverChecking.verify` | 提交审核 |
| `constManagement.driverChecking.check` | 审核确定 |
| `constManagement.recordNew` | 操作记录 |
| `getAttachmentsByWaybillId` | 装/卸货附件图片 |
| `getPartPay` | 分次付款方式（type=10/20/30） |
| `queryDispatchRatio` | 油气返利配置 |

---

## 九、Mixin 依赖

| Mixin | 提供能力 |
|-------|---------|
| `add.conf.js` | `conf.formList`、`conf.table`（费用表格列）、`conf.buttons`、`conf.resultFormList` |
| `add.format.js` | `$total()`、`compuAdjustCost()`、`codeFormat()`、`spanMethod()`、`fetchOilGasConfig()`、`$startEnd()`、`$otherKuiTonsRatio()` |
| `unitTool.js` | `exGetgoodsQuantity()`、`exValidatorWeight()`、`parsePrice()`、`exGetUnitPerFixName()` |

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
