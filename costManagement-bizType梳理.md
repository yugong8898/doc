# costManagement 模块 bizType 梳理

## 概述

`costManagement` 模块中的 `bizType` 主要用于两个场景：
1. **导出功能**：传递给 `/exp/export-data` 接口，标识导出的业务类型
2. **操作日志查询**：传递给 `/log/operation-record/query` 接口，标识日志业务类型

---

## 一、导出类 bizType

### 1.1 服务费结算相关导出

| bizType 值 | 常量名 | 使用位置 | 对应业务 |
|-----------|--------|---------|---------|
| `4pl-export-service-cost-statement` | `EXPORT_BIZ_SERVICE_COST_STATEMENT` | `generateStatement/index.vue`<br>`billStatement/detail.vue` | 导出服务费对账单明细（运单级别） |
| `4pl-export-common-statement` | `EXPORT_BIZ_COMMON_STATEMENT` | `billStatement/detail.vue` | 导出对账单基本信息 |
| `4pl-service-cost-statement-detail-export` | - | `billStatement/index.vue` | 对账单列表页批量导出（最多100个对账单的明细） |

#### 1.1.1 服务费对账单明细导出

**常量定义：**

```246:248:platformweb/src/views/costManagement/serviceFeeSettlement/generateStatement/index.vue
/** 对账明细 / 服务费明细导出 */
const EXPORT_BIZ_SERVICE_COST_STATEMENT = '4pl-export-service-cost-statement'
const EXPORT_COLUMNS_SERVICE_COST = [
```

```63:65:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/detail.vue
/** 对账明细 / 服务费明细导出 */
const EXPORT_BIZ_SERVICE_COST_STATEMENT = '4pl-export-service-cost-statement'
const EXPORT_COLUMNS_SERVICE_COST = [
```

**导出字段：**
- `waybillId` - 运单号
- `networkMainBodyName` - 网络货运主体
- `level1CompanyName` - 业务归属一级公司
- `level2CompanyName` - 业务归属二级公司
- `shipperPaidAmount` - 托运人实付运费
- `driverPaidAmount` - 实付司机运费
- `customerCostDiffRate` - 客户成本差价率
- `freightFeeDiffRate` - 运费差价率
- `otherFeeDiscountRate` - 油气优惠
- `serviceFeeAmount` - 服务费金额
- `reason` - 原因
- `shipperCompanyName` - 托运企业
- `waybillCreateTime` - 运单创建时间
- `invoiceTime` - 运单开票时间
- `paySuccessTime` - 运单支付成功时间

**使用示例：**

```437:442:platformweb/src/views/costManagement/serviceFeeSettlement/generateStatement/index.vue
handleExportDetailRows() {
  const stmtNo = (this.stmtNo || '').trim()

  this.submitStatementExport({
    userExportColumnList: EXPORT_COLUMNS_SERVICE_COST,
    bizType: EXPORT_BIZ_SERVICE_COST_STATEMENT,
```

```565:570:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/detail.vue
handleExportDetailRows() {
  const stmtNo = (this.getRouteStmtNo() || this.baseInfo.billNo || '').trim()
  if (!stmtNo) {
    this.$message.warning('缺少对账单号')
    return
  }
  this.submitStatementExport({
    userExportColumnList: EXPORT_COLUMNS_SERVICE_COST,
    bizType: EXPORT_BIZ_SERVICE_COST_STATEMENT,
```

#### 1.1.2 对账单基本信息导出

**常量定义：**

```57:59:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/detail.vue
/** 对账单基本信息导出（/exp/export-data） */
const EXPORT_BIZ_COMMON_STATEMENT = '4pl-export-common-statement'
const EXPORT_COLUMNS_COMMON_STATEMENT = [
```

**导出字段：**
- `stmtNo` - 对账单号
- `stmtStatus` - 对账状态
- `totalCount` - 总运单数
- `totalAmount` - 总金额
- `networkMainBodyName` - 网络货运主体
- `level1CompanyName` - 业务归属一级公司
- `level2CompanyName` - 业务归属二级公司
- `beginTime` - 开始时间
- `endTime` - 结束时间
- `remark` - 备注
- `paySerialNo` - 付款流水号
- `paySuccessTime` - 付款成功时间
- `auditRemark` - 审核备注
- `createTime` - 创建时间

**使用示例：**

```547:557:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/detail.vue
handleExportBasicInfo() {
  const stmtNo = (this.getRouteStmtNo() || this.baseInfo.billNo || '').trim()
  if (!stmtNo) {
    this.$message.warning('缺少对账单号')
    return
  }
  this.submitStatementExport({
    userExportColumnList: EXPORT_COLUMNS_COMMON_STATEMENT,
    bizType: EXPORT_BIZ_COMMON_STATEMENT,
    filterModel: {
      stmtNo,
```

#### 1.1.3 对账单列表批量导出

**使用位置：** `billStatement/index.vue`

**使用示例：**

```591:607:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/index.vue
exportBefore() {
  return new Promise((resolve, reject) => {
    if (this.total > 100) {
      this.$message.error('导出失败，最多可导出100个对账单的明细，请缩小范围')
      reject(new Error('导出数量超过限制'))
      return
    }

    if (this.total === 0) {
      this.$message.warning('暂无数据可导出')
      reject(new Error('暂无数据'))
      return
    }

    // ... 省略中间代码 ...

    this.exportTableParams = {
      bizType: '4pl-service-cost-statement-detail-export',
```

**限制条件：**
- 最多可导出 100 个对账单的明细
- 无数据时禁止导出

### 1.2 客户成本差价率导出

| bizType 值 | 使用位置 | 对应业务 |
|-----------|---------|---------|
| `4pl-cust-cost-diff-query` | `customerCostDiffRate.vue` | 客户成本差价率查询与导出 |

**使用示例：**

```228:231:platformweb/src/views/costManagement/customerCostDiffRate.vue
exportTableParams: {
  bizType: '4pl-cust-cost-diff-query',
  filterModel: {}
},
```

```553:556:platformweb/src/views/costManagement/customerCostDiffRate.vue
this.exportTableParams = {
  bizType: '4pl-cust-cost-diff-query',
  filterModel: { ...this.buildQueryFilterModel() }
}
```

---

## 二、操作日志查询类 bizType

### 2.1 服务费运单日志

| bizType 值 | 常量名 | 使用位置 | 对应业务 |
|-----------|--------|---------|---------|
| `lsc_service_cost` | `SERVICE_COST_LOG_BIZ_TYPE` | `generateStatement/components/index.vue`<br>`billStatement/components/index.vue` | 查询运单级别的服务费操作日志 |

**常量定义：**

```248:248:platformweb/src/views/costManagement/serviceFeeSettlement/generateStatement/components/index.vue
const SERVICE_COST_LOG_BIZ_TYPE = 'lsc_service_cost'
```

```248:248:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/components/index.vue
const SERVICE_COST_LOG_BIZ_TYPE = 'lsc_service_cost'
```

**使用示例：**

```588:595:platformweb/src/views/costManagement/serviceFeeSettlement/generateStatement/components/index.vue
loadOperationRecords() {
  this.logLoading = true
  return operationRecordQuery({
    currentPage: 1,
    pageLength: 1000,
    countTotal: true,
    filterModel: {
      bizId: this.activeObj.waybillNo,
      bizType: SERVICE_COST_LOG_BIZ_TYPE
```

**说明：**
- `bizId` 传入运单号 (`waybillNo`)
- 查询该运单的所有服务费相关操作记录（如调整服务费金额等）

### 2.2 对账单操作记录

| bizType 值 | 常量名 | 使用位置 | 对应业务 |
|-----------|--------|---------|---------|
| `lsc_common_statement` | `STATEMENT_OP_RECORD_BIZ_TYPE` | `billStatement/detail.vue` | 查询对账单级别的操作记录 |

**常量定义：**

```37:37:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/detail.vue
const STATEMENT_OP_RECORD_BIZ_TYPE = 'lsc_common_statement'
```

**使用示例：**

```829:841:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/detail.vue
async loadOperateRecords(page) {
  const stmtNo = (this.getRouteStmtNo() || this.baseInfo.billNo || '').trim()
  if (!stmtNo) {
    this.operateRecords = []
    this.operateRecordPage.total = 0
    this.remarkExpanded = {}
    this.remarkShowExpand = {}
    return
  }
  if (page) this.operateRecordPage.currentPage = page
  this.operateRecordLoading = true
  try {
    const data = await operationRecordQuery({
      currentPage: this.operateRecordPage.currentPage,
      pageLength: this.operateRecordPage.pageSize,
      countTotal: true,
      filterModel: {
        bizId: stmtNo,
        bizType: STATEMENT_OP_RECORD_BIZ_TYPE
```

**说明：**
- `bizId` 传入对账单号 (`stmtNo`)
- 查询该对账单的所有操作记录（如创建、提交、审核、驳回、取消等）

---

## 三、列表展示字段 bizType

以下 `bizType` 是**后端返回的字段**，直接展示在页面表格中，**不是前端传参**。

### 3.1 按运单列表

**位置：** `waybill/index.vue`

```177:177:platformweb/src/views/costManagement/serviceFeeSettlement/waybill/index.vue
<el-table-column prop="bizType" label="业务类型" width="160" align="center" show-overflow-tooltip />
```

**说明：** 展示每条运单对应的业务类型名称（如"默认业务"、"短倒业务"、"轻卡业务"等）

### 3.2 生成对账单页

**位置：** `generateStatement/index.vue`

```101:101:platformweb/src/views/costManagement/serviceFeeSettlement/generateStatement/index.vue
<el-table-column prop="bizType" label="业务类型" width="150" show-overflow-tooltip />
```

**说明：** 在生成对账单的运单明细列表中展示业务类型

### 3.3 对账单详情页

**位置：** `billStatement/detail.vue`

```170:170:platformweb/src/views/costManagement/serviceFeeSettlement/billStatement/detail.vue
<el-table-column prop="bizType" label="业务类型" width="160" show-overflow-tooltip />
```

**说明：** 在对账明细列表中展示每条运单的业务类型

### 3.4 服务费详情弹窗

**位置：** `waybill/components/serviceFeeDetailDialog.vue`

```21:21:platformweb/src/views/costManagement/serviceFeeSettlement/waybill/components/serviceFeeDetailDialog.vue
业务类型：{{ activeObj.bizTypeName || activeObj.bizType }}
```

**说明：** 优先展示 `bizTypeName`，降级使用 `bizType`

---

## 四、customerCostDiffRate 中的特殊用法

在 `customerCostDiffRate.vue` 中，`bizType` 有两层含义：

### 4.1 作为成本差价率类型标识

```406:406:platformweb/src/views/costManagement/customerCostDiffRate.vue
const bizType = row?.costDiffRateType
```

**说明：** 这里的 `bizType` 实际上是 `costDiffRateType`，用于标识成本差价率的配置类型

### 4.2 业务类型枚举映射

**定义位置：**

```203:208:platformweb/src/views/costManagement/customerCostDiffRate.vue
map: {
  10: '默认业务',
  20: '短倒业务',
  50: '轻卡业务'
},
```

**使用场景：**

```128:128:platformweb/src/views/costManagement/customerCostDiffRate.vue
{{ row.costDiffRateType === '3' ? map[item.bizType] : item.mainBodyName }}
```

**说明：**
- 当 `costDiffRateType === '3'` 时，按业务类型维度展示差价率配置
- 展示时通过 `map[item.bizType]` 将数字代码转换为中文名称
- 其他 `costDiffRateType` 值时，展示网货主体名称

### 4.3 业务类型枚举值

| 代码 | 业务类型 |
|-----|---------|
| `10` | 默认业务 |
| `20` | 短倒业务 |
| `50` | 轻卡业务 |

---

## 五、总结

### 5.1 bizType 分类汇总

| 分类 | 数量 | bizType 值 |
|------|------|-----------|
| 导出类 | 4 个 | `4pl-export-service-cost-statement`<br>`4pl-export-common-statement`<br>`4pl-service-cost-statement-detail-export`<br>`4pl-cust-cost-diff-query` |
| 日志查询类 | 2 个 | `lsc_service_cost`<br>`lsc_common_statement` |
| 展示字段 | N/A | 后端返回，直接展示 |

### 5.2 使用规范

1. **导出类 bizType**
   - 必须传递给 `/exp/export-data` 接口
   - 配合 `userExportColumnList` 指定导出字段
   - 配合 `filterModel` 传递筛选条件

2. **日志查询类 bizType**
   - 必须传递给 `/log/operation-record/query` 接口
   - 配合 `bizId` 指定业务主键（运单号或对账单号）
   - 用于查询该业务实体的操作记录

3. **展示字段 bizType**
   - 由后端返回，前端不传参
   - 直接绑定到表格列 `prop="bizType"`
   - 展示运单或对账单的业务类型

### 5.3 注意事项

1. 各 bizType 有固定的使用场景，**互不混用**
2. 导出类 bizType 以 `4pl-` 开头
3. 日志查询类 bizType 以 `lsc_` 开头
4. `customerCostDiffRate` 中的 `bizType` 含义特殊，实际指 `costDiffRateType`
5. 业务类型枚举值（10/20/50）仅在 `customerCostDiffRate` 模块使用

---

**文档版本**: v1.0

**最后更新**: 2026年06月

**整理人**: 王新骏
