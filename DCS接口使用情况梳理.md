# DCS 接口使用情况梳理文档

## 文档说明

本文档梳理 `wlyd-app-consigner`（移动端）和 `logisticsweb`（PC端）两个项目中所有 **DCS 相关接口**的使用情况。

**梳理范围**：只包含 URL 中包含 `/dcs/` 或 `/gateway/dcs/` 的接口

**梳理内容**：
- ✅ 实际接口 URL
- ✅ 页面路径
- ✅ 具体调用时机（按钮点击、生命周期等）

---

## 通用接口规范说明

### 响应数据结构（logisticsweb 项目）

根据 `src/utils/request.js` 的响应拦截器处理逻辑，所有接口的响应数据遵循以下规范：

#### 标准响应格式

**成功响应**：

```json
{
  "succeed": true,
  "model": [...],
  "total": 100
}
```

或

```json
{
  "succ": true,
  "model": [...],
  "total": 100
}
```

**失败响应**：

```json
{
  "succeed": false,
  "errCode": "BPLA0111",
  "errMsg": "错误描述信息"
}
```

或

```json
{
  "succeed": false,
  "code": "BPLA0111",
  "message": "错误描述信息"
}
```

#### 通用字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `succeed` / `succ` | Boolean | 请求是否成功（true: 成功, false: 失败） |
| `model` | Any | 业务数据，可以是对象、数组、字符串等 |
| `total` | Number | 分页查询时的总记录数（非分页接口可能没有此字段） |
| `errCode` / `code` | String | 业务错误码，失败时返回 |
| `errMsg` / `message` | String | 错误描述信息，失败时返回 |

#### 响应拦截器处理规则

**POST 请求**：
- 拦截器判断 `succeed` 或 `succ` 字段：
  - `true` → 返回 `response.data`（Promise resolve）
  - `false` → 根据 `errCode`/`code` 处理错误（Promise reject）
- 前端代码直接拿到的是 `response.data`

**GET 请求**：
- 不做成功失败判断，直接返回 `response.data`
- 通常用于导出、文件下载等场景

**特殊配置**：
- `custom.fullResponse: true` → 返回完整的 axios response 对象（包含 headers、status 等）
- `custom.toast: false` → 失败时不自动弹出错误提示

#### 常见错误码

| 错误码 | 说明 | 处理方式 |
|--------|------|---------|
| `100006` | Token 失效（白名单） | 自动退出登录，跳转登录页 |
| `ACOM0009` | Token 失效 | 自动退出登录，跳转登录页 |
| `UC_A1_0014` | 令牌非法 | 自动退出登录，跳转登录页 |
| `BPLA0111` | 已注册大宗，未注册3PL | 跳转3PL注册页 |
| `90001` | 发票登记相关错误 | 不拦截，返回原始数据 |

#### HTTP 状态码处理

| HTTP 状态码 | 错误提示 |
|------------|---------|
| 304 | 静默处理，不提示错误 |
| 403 | 您暂无权限访问该内容，请检查权限后重试 |
| 404 | 尊敬的用户，系统升级维护中，请您稍后重试 |
| 408 | 请求等待超时啦，检查下网络再重新试试吧 |
| 500-505 | 尊敬的用户，系统升级维护中，请您稍后重试 |
| 其他 | 操作失败，未知的网络错误，请稍后重试 |

#### 使用示例

**标准 POST 请求**：

```javascript
import { findZeroByBusId } from '@/api/userBase.waybillSettlement'

// 前端拿到的是 response.data
const [err, datas] = await findZeroByBusId(params)
  .then(datas => [null, datas])
  .catch(err => [err, null])

if (datas) {
  // 成功处理
  console.log(datas.model) // 业务数据
  console.log(datas.total) // 总数（如果有）
} else if (err) {
  // 错误处理（拦截器已自动提示，这里可做额外处理）
  console.error(err)
}
```

**使用 fullResponse**：

```javascript
import { getTobValue } from '@/api/userBase.orderSettlement'

// fullResponse: true 时返回 [error, response]
getTobValue({ busId: orderId }).then(res => {
  // res = [null, { data: {...}, headers: {...}, status: 200 }]
  if (res && res[1]?.data?.value === 20) {
    // 处理 TOB 订单
  }
})
```

**关闭自动提示**：

```javascript
export function someApi(params) {
  return request({
    url: '/some/api',
    method: 'post',
    data: params,
    custom: {
      toast: false  // 失败时不自动弹提示
    }
  })
}
```

---

# 一、wlyd-app-consigner 项目（移动端 uni-app）

## 接口清单

共 **1 个** DCS 接口：

| 序号 | 实际接口 URL | 功能 |
|------|-------------|------|
| 1 | `/dcs/bussProcessing/findByBusId` | 抹零配置查询 |

---

## 接口详情：抹零配置查询

### 基本信息

- **实际接口 URL**: `/dcs/bussProcessing/findByBusId`
- **请求方式**: `GET`
- **API 定义文件**: `api/waybillSettlement.js`

```javascript
export function findZeroByBusId(payload) {
  return http.get(`/dcs/bussProcessing/findByBusId`, { params: payload })
}
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| busId | String | 是 | 运单号 |
| busType | String | 是 | 业务类型，固定值 '10' (运单) |

### 响应参数

**响应结构**:

```json
{
  "succeed": true,
  "data": {
    "model": [
      {
        "id": "string",
        "value": "string"
      }
    ]
  }
}
```

**字段说明**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| succeed | Boolean | 请求是否成功 |
| data.model | Array | 抹零配置数组（实际业务只取第一项） |
| data.model[0].id | String | 抹零配置ID，删除抹零配置时需要传入此参数作为 `waybillZeroId` |
| data.model[0].value | String | 抹零模式枚举值，参见下方说明 |

**抹零模式枚举（data.model[0].value）**:

| 枚举值 | 说明 | 计算方式 |
|--------|------|---------|
| '0' | 不抹零 | 保持原金额不变 |
| '1' | 小数抹零 | 向下取整到个位（去掉小数部分） |
| '2' | 个位抹零 | 向下取整到十位（去掉个位和小数） |
| '3' | 小数四舍五入 | 四舍五入到个位 |
| '4' | 个位智能抹零 | 个位<5取0，个位>=5取5 |

**响应示例**:

```json
{
  "succeed": true,
  "data": {
    "model": [
      {
        "id": "1234567890",
        "value": "1"
      }
    ]
  }
}
```

**字段使用说明**:

1. **id 字段**：在删除抹零配置时使用

```javascript
// 删除抹零配置时的请求参数（调用 updateByBusId 接口）
const params = {
  waybillZeroId: this.zeroModeObj.id,  // 使用返回的 id
  waybillZeroType: '10',
  zeroOperationRemark: this.delZeroTxt,
  busId: this.waybillId,
  waybillValue: '0'
}
```

2. **value 字段**：控制金额抹零计算逻辑

```javascript
// 前端使用示例
this.zeroByBusIdMode = res.data.model[0].value || '0'  // 默认不抹零
this.zeroModeObj = res.data.model[0]  // 保存完整对象供后续使用
```

### 使用详情

#### 页面 1：运单结算调整页面

**页面路径**: `settlementPages/waybillSettlement/adjust.vue`

**调用时机**: 
- **生命周期**: `onLoad` 
- **调用方法**: `getZeroByBusId()`
- **调用位置**: 页面加载时自动调用

**调用代码**:

```javascript
async onLoad(option) {
  // 获取金额取整方式（结算）
  await this.getCompanyRoundMode([this.waybillId], '11')
  // 加载必要的字典数据
  await this.loadNecessaryEnums()
  await this.loadZeroTypeObj()
  // 获取详情和抹零配置
  await Promise.all([this.getDetails(), this.loadCostEnums()])
  await this.getRecordPaging()
  await this.loadPartPay()
  this.loading = false
}

// 查询抹零配置
async getZeroByBusId() {
  try {
    const res = await findZeroByBusId({
      busId: this.waybillId,
      busType: '10'
    })
    if (res.data?.model?.[0]) {
      this.zeroByBusIdMode = res.data.model[0].value || '0'
      this.zeroModeObj = res.data.model[0]
    }
  } catch (e) {
    console.error('查询抹零配置失败:', e)
  }
}
```

**业务场景**:
- 页面加载时自动查询运单的抹零配置
- 用于保存/提交时的金额抹零处理
- 抹零配置影响最终应付金额的计算

**相关按钮操作**:
- **保存按钮**: 点击 → `handleSave()` → `changeWaybillStatus()` → 应用抹零配置
- **提交预审按钮**: 点击 → `handleSubmit()` → `changeWaybillStatus()` → 应用抹零配置

**抹零方式说明**:
- `0`: 不抹零
- `1`: 小数抹零（向下取整到个位）
- `2`: 个位抹零（向下取整到十位）
- `3`: 小数四舍五入到个位
- `4`: 个位智能抹零（个位<5取0，个位>=5取5）

**抹零处理流程**:
1. 页面加载时查询抹零配置
2. 用户修改费用明细时，实时计算应付金额
3. 点击保存/提交时，根据抹零配置计算抹零金额
4. 弹窗确认抹零金额
5. 确认后追加抹零费项（应收抹零或应付抹零）
6. 提交完整数据到后端

---

# 二、logisticsweb 项目（PC 端 Vue.js）

## 接口清单

共 **4 个** DCS 接口：

| 序号 | 实际接口 URL | 功能 |
|------|-------------|------|
| 1 | `/gateway/dcs/bussProcessing/findByBusId` | 抹零配置查询 |
| 2 | `/gateway/dcs/reporting/getValue` | 订单 TOB 标识查询 |
| 3 | `/gateway/dcs/roundingMode/get` | 金额取整方式查询（旧接口） |
| 4 | `/gateway/dcs/commonFile/downloadAnyFile` | 通用文件下载 |

---

## 接口 1：抹零配置查询

### 基本信息

- **实际接口 URL**: `/gateway/dcs/bussProcessing/findByBusId`
- **请求方式**: `GET`
- **API 定义文件**: `src/api/userBase.waybillSettlement.js`

```javascript
export function findZeroByBusId(params) {
  return request({
    url: dcsUrl + '/bussProcessing/findByBusId',  // dcsUrl = '/gateway/dcs'
    method: 'get',
    params
  })
}
```

> **注意**：PC 端当前实际调用的接口已改为 `bmsUrl + '/index/dcsToSearch'`（POST 方式），原 DCS 直连地址已注释，功能等同。

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| busId | String | 是 | 运单号（`waybillId`） |
| busType | String | 是 | 业务类型，固定值 '10' (运单) |

### 响应参数

**响应结构**:

```json
{
  "succeed": true,
  "model": [
    {
      "id": "string",
      "value": "string"
    }
  ]
}
```

**字段说明**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| succeed | Boolean | 请求是否成功 |
| model | Array | 抹零配置数组（实际业务只取第一项） |
| model[0].id | String | 抹零配置ID，删除抹零配置时需要传入此参数作为 `waybillZeroId` |
| model[0].value | String | 抹零模式枚举值，参见下方说明 |

**抹零模式枚举（model[0].value）**:

| 枚举值 | 说明 | 计算方式 |
|--------|------|---------|
| '0' | 不抹零 | 保持原金额不变 |
| '1' | 小数抹零 | 向下取整到个位（去掉小数部分） |
| '2' | 个位抹零 | 向下取整到十位（去掉个位和小数） |
| '3' | 小数四舍五入 | 四舍五入到个位 |
| '4' | 个位智能抹零 | 个位<5取0，个位>=5取5 |

**响应示例**:

```json
{
  "succeed": true,
  "model": [
    {
      "id": "1234567890",
      "value": "1"
    }
  ]
}
```

**字段使用说明**:

1. **id 字段**：在删除抹零配置时使用

```javascript
// 删除抹零配置时的请求参数（调用 updateByBusId 接口）
const params = {
  waybillZeroId: this.zeroModeObj.id,  // 使用返回的 id
  waybillZeroType: '10',
  zeroOperationRemark: this.delZeroTxt,
  busId: this.$route.query.waybillId,
  waybillValue: '0'
}
```

2. **value 字段**：控制费用明细的金额抹零计算逻辑，若接口未返回则默认取 `'0'`（不抹零）

```javascript
// 前端使用示例（edit.vue）
this.zeroByBusIdMode = datas.model?.[0]?.value || '0'
this.zeroModeObj = datas.model[0]
```

### 使用详情

#### 页面 1：运单结算处理-编辑页面

**页面路径**: `src/views/userBase/waybillSettlement/edit.vue`

**调用时机**: 
- **生命周期**: `mounted` 或 `created`
- **调用方法**: `findZeroByBusId`

**业务场景**:
- 编辑运单结算信息时查询抹零配置
- 用于费用计算和抹零处理
- 与移动端功能类似

---

#### 页面 2：运单结算处理-查看页面

**页面路径**: `src/views/userBase/waybillSettlement/read.vue`

**调用时机**: 
- **生命周期**: `mounted` 或 `created`
- **调用方法**: `findZeroByBusId`

**业务场景**:
- 只读模式查看抹零配置
- 展示抹零计算结果

---

## 接口 2：订单 TOB 标识查询

### 基本信息

- **实际接口 URL**: `bmsUrl + '/index/orderReporting'`
- **请求方式**: `POST`
- **API 定义文件**: `src/api/userBase.orderSettlement.js`
- **状态**: ⚠️ 接口地址已变更，原 DCS 地址已注释

```javascript
export const getTobValue = (data) => {
  return betterRequest({
    // url: dcsUrl + '/reporting/getValue',  // 旧地址已注释
    url: bmsUrl + '/index/orderReporting',
    method: 'post',
    params: data,
    custom: {
      fullResponse: true  // 返回完整响应（包含 headers 等）
    }
  })
}
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| busId | String | 是 | 订单ID（订单号，如 `POY2024051300000001`） |

### 响应参数

**响应结构**:

```json
[
  null,
  {
    "data": {
      "busId": "string",
      "value": 10 | 20
    }
  }
]
```

**字段说明**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| [0] | null | 错误信息（成功时为 null） |
| [1].data | Object | 响应数据对象 |
| [1].data.busId | String | 订单ID（与请求参数一致） |
| [1].data.value | Number | TOB 标识枚举值 |

**TOB 标识枚举（value）**:

| 枚举值 | 说明 | 业务处理 |
|--------|------|---------|
| `10` | 非 TOB 订单 | 使用普通分页查询运单列表 |
| `20` | TOB 订单 | 使用 TOB 专用接口查询运单列表 |

**响应示例**:

```json
[
  null,
  {
    "data": {
      "busId": "POY2024051300000001",
      "value": 20
    }
  }
]
```

**字段使用说明**:

1. **判断是否为 TOB 订单**：

```javascript
getTobValue({ busId: orderId }).then(res => {
  // res 格式：[error, response]
  if (res && res[1]?.data?.value === 20) {
    this.isTob = true
    // TOB 订单：调用专用接口 getSignWaybillList
    this.getTobDetailsList(orderId)
    this.getUnTransferNum(orderId)
  } else {
    this.isTob = false
    // 非 TOB 订单：调用普通接口 postGetWaybill
    this.postGetWaybill()
  }
})
```

2. **TOB 订单特殊处理**：
   - 运单列表不支持分页（`v-if="+waybillTotal > 5 && !isTob"`）
   - 提交对账时弹窗二次确认未完成运单数
   - 运单数据通过 `getSignWaybillList` 获取

### 使用详情

#### 页面：订单结算处理-调整结算信息弹窗

**页面路径**: `src/components/SettlementProcessingDialog/order.vue`

**调用时机**: 
- **生命周期**: `mounted` → `getDetails()`
- **调用方法**: `getTobValue(id)`
- **调用位置**: 订单详情加载后，根据订单类型判断

**调用代码**:

```javascript
async getDetails() {
  // ... 获取订单详情
  const { subOrderIds = '' } = this.detail
  
  // 判断是否需要查询 TOB 标识
  // 1. subOrderIds 以 POY 或 POC 开头
  const isPoyOrPoc = subOrderIds.startsWith('POY') || subOrderIds.startsWith('POC')
  // 2. 不包含逗号（TOB 业务单一，只能派一个单子）
  const isTobOrder = isPoyOrPoc && !subOrderIds.includes(',')
  
  if (isTobOrder) {
    this.getTobValue(subOrderIds)
  }
}
```

**业务场景**:
- 判断订单是否为 TOB（To Business）订单
- 根据 TOB 标识决定运单列表查询方式和结算流程
- TOB 订单特性：
  - 业务单一，只能派一个运单
  - 运单列表不支持分页
  - 提交对账时需要二次确认未完成运单数
  - 一笔运单仅可发起一次对账

**TOB 订单提交确认逻辑**:

```javascript
showWarningMsg() {
  const unFinish = this.isTob && this.unTransferNum
  const txtA = `一笔运单仅可发起一次对账，您尚有${this.unTransferNum}单运单未完成，发起后未完成运单无法进行对账，是否确定提交本次对账？`
  const txtB = '一笔运单仅可发起一次对账，是否确定提交本次对账？'
  const msg = unFinish ? txtA : txtB
  
  this.$confirm(msg, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    this.changeOrderStatus('320', 'submit')
  })
}
```

**注意事项**:
- ⚠️ 接口已从 DCS 服务迁移到 BMS 服务（`/index/orderReporting`）
- ⚠️ 使用 `betterRequest` 封装，返回完整响应（数组格式 `[error, response]`）
- ⚠️ 只有订单号以 `POY` 或 `POC` 开头且不含逗号时才查询 TOB 标识
- ⚠️ TOB 订单和非 TOB 订单的运单查询接口不同

---

## 接口 3：金额取整方式查询（旧接口）

### 基本信息

- **实际接口 URL**: `/gateway/dcs/roundingMode/get`
- **请求方式**: `GET`
- **API 定义文件**: `src/api/userBase.driverSupplymanagement.js`
- **状态**: ⚠️ 已废弃，建议使用新接口

```javascript
export function RoundModeBybizld(id) {
  return request({
    url: dcsUrl + '/roundingMode/get?bizId=' + id,  // dcsUrl = '/gateway/dcs'
    method: 'get'
  })
}
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| bizId | String | 是 | 业务单据ID（运单号、货源号等） |

### 使用详情

#### 页面：司机货源管理页面

**页面路径**: `src/views/userBase/driverSupplymanagement/*`

**调用时机**: 
- **业务逻辑**: 司机货源发布时
- **调用方法**: `RoundModeBybizld`

**业务场景**:
- 查询金额取整方式
- 用于运费、保费计算时的金额取整

**替代方案**:
- 新接口 1: `getCompanyRoundMode(id)` - 根据公司 ID 查询（推荐）
- 新接口 2: `getRoundingMode(data)` - 批量查询运单取整方式
- 新接口 3: `getRoundModeBybizlds(data)` - 批量查询（BMS 服务）

**注意事项**:
- ⚠️ 此接口为旧版接口，代码中已有注释说明
- 建议使用新接口以获得更好的性能和更完整的功能

---

## 接口 4：通用文件下载

### 基本信息

- **实际接口 URL**: `/gateway/dcs/commonFile/downloadAnyFile`
- **请求方式**: `GET`
- **API 定义文件**: `src/api/userBase.collectTicket.js`

```javascript
export function previewStatementFile(receiptNo, fileName) {
  const path = `bill/billReceiptInvoiceStatement/${receiptNo}/${fileName}`
  return `${dcsUrl}/commonFile/downloadAnyFile?path=${encodeURIComponent(path)}`
  // 返回完整 URL: /gateway/dcs/commonFile/downloadAnyFile?path=...
}
```

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | String | 是 | 文件路径（需要 URL 编码） |

### 使用详情

#### 页面：收票管理页面

**页面路径**: `src/views/userBase/collectTicket/*`

**调用时机**: 
- **用户操作**: 点击预览/下载对账单文件按钮
- **调用方法**: `previewStatementFile`

**业务场景**:
- 预览对账单文件
- 下载对账单附件
- 查看收票相关的文档

**文件路径格式**:

```
bill/billReceiptInvoiceStatement/{receiptNo}/{fileName}
```

**使用示例**:

```javascript
// 预览对账单文件
const url = previewStatementFile('REC202401010001', 'statement.pdf')
// 返回: /gateway/dcs/commonFile/downloadAnyFile?path=bill%2FbillReceiptInvoiceStatement%2FREC202401010001%2Fstatement.pdf
```

**相关接口**:
- `getStatementFileList(receiptNo)` - 查询对账单附件列表
- `deleteStatementFile(data)` - 删除对账单文件
- `uploadStatement(data)` - 上传对账单文件

**注意事项**:
- 文件路径必须进行 URL 编码（使用 `encodeURIComponent`）
- 返回的是完整的 URL 字符串，可直接用于下载或预览
- 主要用于收票管理模块的对账单文件处理

---

## 配置说明

### wlyd-app-consigner 配置

接口直接使用相对路径，无需配置：
- `/dcs/bussProcessing/findByBusId`

### logisticsweb 配置

**配置文件**: `src/config/index.js`

```javascript
export default {
  dcsUrl: '/gateway/dcs',
  // ... 其他配置
}
```

---

## 项目对比总结

| 对比项 | wlyd-app-consigner (移动端) | logisticsweb (PC 端) |
|--------|---------------------------|---------------------|
| 项目类型 | uni-app | Vue.js |
| DCS 接口数量 | 1 个 | 4 个 |
| URL 前缀 | `/dcs/` | `/gateway/dcs/` |
| 抹零配置 | ✅ | ✅ |
| TOB 标识 | ❌ | ✅ |
| 金额取整（旧） | ❌ | ✅ |
| 文件下载 | ❌ | ✅ |
| 业务范围 | 运单结算 | 运单结算、订单结算、司机货源、收票管理 |

---

## 总结

### 接口总览

**wlyd-app-consigner 项目**：1 个 DCS 接口
- `/dcs/bussProcessing/findByBusId` - 抹零配置查询

**logisticsweb 项目**：4 个 DCS 接口
- `/gateway/dcs/bussProcessing/findByBusId` - 抹零配置查询
- `/gateway/dcs/reporting/getValue` - 订单 TOB 标识查询
- `/gateway/dcs/roundingMode/get` - 金额取整方式查询（旧接口）
- `/gateway/dcs/commonFile/downloadAnyFile` - 通用文件下载

**总计**：5 个 DCS 接口

---

## 更新记录

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|----------|--------|
| 2026-05-30 | v1.0 | 最终版本：只包含 `/dcs/` 或 `/gateway/dcs/` 的接口 | 王新骏 |
