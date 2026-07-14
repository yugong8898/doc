# 账户流水模块（turnover）

## 概述

`turnover` 目录下包含三个账户流水列表页面，分别对应不同角色视角的账户流水查询：

| 文件 | 功能 | 角色视角 |
|------|------|---------|
| `3pl.vue` | 3PL（网络货运经营主体）流水列表 | 3PL 自己查看所有关联主体的流水 |
| `mainstay.vue` | 主体流水列表 | 网络货运主体查看自己的流水 |
| `credit.vue` | 授信流水列表 | 主体维度查看授信打款流水 |

---

## 文件结构

```
logisticsweb/src/views/userBase/mainstay/
├── turnover/
│   ├── 3pl.vue           # 3PL账户流水列表（主文件）
│   ├── mainstay.vue      # 主体账户流水列表
│   └── credit.vue        # 授信流水列表
├── api/
│   ├── index.js          # 3PL侧接口（流水、充值、提现、授信等）
│   └── mainstay.js       # 主体侧接口（主体流水、授信打款等）
├── components/
│   └── Dialog/
│       ├── 3pl/
│       │   ├── recharge.vue          # 充值详情弹窗
│       │   ├── withdrawalDetial.vue  # 提现详情弹窗
│       │   └── creditDetial.vue      # 授信详情弹窗
│       ├── cbs/
│       │   └── cbs.vue               # CBS银行回单选择弹窗（授信打款用）
│       └── freezeDetial.vue          # 冻结详情弹窗（credit.vue 复用）
└── utils/
    └── codeList.js       # 金额格式化等工具方法
```

---

## 核心逻辑

### 1. 3PL 流水列表（3pl.vue）

**职责**：3PL 视角查询所有关联网络货运主体的账户流水。

**筛选条件**：
- 网络货运经营主体（subjectName）
- 账户类型（accountType）：现金账户 `0` / 授信账户 `1`
- 类型（businessType）：一级分类，依赖账户类型动态加载
- 用途（businessTypeSubset）：二级分类，依赖一级分类联动
- 申请编号（applyCode）
- 流水号（cbsFlowMeter）
- 交易时间（createDate）：日期范围，默认加载最近 30 天（来自 `pickerOptionsLimit` mixin）
- 所属组织（orgIdList）：组织树多选，支持微应用和独立应用两种 orgId 字段（`bizId` / `orgId`）

**初始化流程**：
```
activatedMethods()
  ├── fetchOrganizationList()   # 获取当前用户有权限的组织列表，存入 copyOrgIdList
  ├── getDictionary()           # 加载一级分类字典（账户类型为空时不请求）
  └── getData()                 # 加载流水列表
```

**组织 ID 兜底逻辑**：
- `orgIdList` 为空时，自动传入 `copyOrgIdList`（当前用户所有组织），避免无权限数据越权
- 微应用环境下使用 `bizId` 字段，独立应用使用 `orgId` 字段（`isMicroApp()` 判断）

**字典联动**：
- 账户类型切换 → 调用 `getDictionaryEnumerationList` 刷新一级分类，清空二级分类和已选值
- 一级分类切换 → 从已加载的 `dictionaryList[].secondLevels` 中取二级分类，不再请求接口

**查看详情（showDetialNow）**：

仅 `['充值', '提现', '还款', '授信']` 类型支持查看详情，其余弹提示不跳转。

额外屏蔽以下组合（特殊业务流水）：
- `businessTypeCode === 'B001'` 且 `businessTypeSubsetCode === 'C012'`
- `businessTypeCode === 'B003'` 且 `businessTypeSubsetCode === 'C013'`

弹窗路由规则（基于 `accountType` 和 `ohterType`）：

| accountType | ohterType | 弹窗 |
|------------|-----------|------|
| 0（现金） | 0 | `recharge.vue`（充值详情） |
| 0（现金） | 非0 | `withdrawalDetial.vue`（提现详情） |
| 1（授信） | 0 | `creditDetial.vue`（授信详情） |
| 1（授信） | 非0 | `withdrawalDetial.vue`（提现详情） |

**表格列**：序号、网络货运经营主体、申请编号、流水号、账户类型、类型、用途、金额(元)、余额(元)、交易时间、摘要、所属组织、操作

**导出**：使用通用 `ExportBtn` 组件，`bizType` 为 `3pl-accountFlowMeterPageList`

---

### 2. 主体流水列表（mainstay.vue）

**职责**：网络货运主体视角查询自己的账户流水（不含组织筛选，显示企业名称）。

**与 3pl.vue 的差异**：

| 维度 | 3pl.vue | mainstay.vue |
|------|---------|-------------|
| 主体筛选 | 有（subjectName） | 无（固定为当前主体） |
| 组织筛选 | 有（orgIdList） | 无 |
| 余额列 | 有（tradeAfterMoney） | 无 |
| 企业名称列 | 无 | 有（companyName） |
| 查询接口 | `get3plFLowMeterPageList` | `getSubjectFLowMeterPageList` |
| 导出 bizType | `3pl-accountFlowMeterPageList` | `3pl-subjectFLowMeterPageList` |
| 组织列 | 有 | 有 |

**查看详情逻辑**：与 `3pl.vue` 基本一致，但无特殊 businessTypeCode 屏蔽判断。

**时间初始化**：同样使用 `pickerOptionsLimit` mixin，默认最近 30 天。

---

### 3. 授信流水列表（credit.vue）

**职责**：主体维度查看授信打款流水（CBS 银行打款记录），与普通现金/授信流水完全独立。

**筛选条件**：
- 金额范围（startApplyMoney / endApplyMoney）
- 时间段（createdStartDate / createdEndDate）：独立的两个日期选择器，带互斥禁用逻辑

**时间选择器互斥禁用**：
- 选择开始时间后，结束时间不可选早于开始时间的日期
- 选择结束时间后，开始时间不可选晚于结束时间的日期
- 通过 `watch` 动态设置 `startTimeOptions.disabledDate` / `endTimeOptions.disabledDate`

**数据汇总**：页面顶部展示授信已打款金额和未打款金额（来自 `creditMoney` 对象，但当前代码中 `creditMoney` 默认值固定为 `{ done: '0', todo: '0' }`，未见接口写入，疑似待完善）。

**新增打款功能**（controlBtn.newPaymentBtn 权限控制）：
1. 点击"新增打款"，弹出 `cbs.vue`（CBS银行回单选择弹窗）
2. 用户选择回单后，回调 `saveSubjectRemitNow`
3. 将 CBS 回单字段映射为后端保存参数，调用 `saveSubjectRemit` 接口
4. 保存成功后关闭弹窗并刷新列表

**表格列**：序号、流水号(cbsSerialNumber)、户名(付款)、付款账号、开户银行(付款)、户名(收款)、收款账号、开户银行(收款)、金额(元)、交易时间

---

## 依赖关系图

```
turnover/3pl.vue
  ├── api/index.js
  │   ├── get3plFLowMeterPageList        # 列表查询
  │   ├── get3plFLowMeterExcel           # 导出（已通过 ExportBtn 替代，旧方法保留）
  │   └── getDictionaryEnumerationList   # 类型/用途字典
  ├── components/Dialog/3pl/
  │   ├── recharge.vue        # 充值详情弹窗
  │   ├── withdrawalDetial.vue # 提现/还款详情弹窗
  │   └── creditDetial.vue    # 授信详情弹窗
  ├── components/ExportBtn/indexNew.vue  # 通用导出按钮
  ├── components/OrganizationTree/index.vue # 组织树选择器
  ├── api/fetchOrgList.js     # 获取组织列表
  ├── utils/useMainProps.js   # isMicroApp() 判断
  └── mixins/pickerOptionLimit.js  # 日期默认30天、92天限制

turnover/mainstay.vue
  ├── api/mainstay.js
  │   ├── getSubjectFLowMeterPageList    # 列表查询
  │   └── getSubjectFLowMeterExcel       # 导出（已通过 ExportBtn 替代）
  ├── api/index.js
  │   └── getDictionaryEnumerationList   # 类型/用途字典
  ├── components/Dialog/3pl/             # 与 3pl.vue 共用同一套弹窗
  ├── components/ExportBtn/indexNew.vue
  └── mixins/pickerOptionLimit.js

turnover/credit.vue
  ├── api/mainstay.js
  │   ├── getSubjectRemitPageList        # 授信打款列表查询
  │   ├── getSubjectCreditAccountPageList # 授信账户列表（用于 companyList）
  │   └── saveSubjectRemit               # 新增授信打款
  ├── components/Dialog/freezeDetial.vue # 查看详情弹窗（已注释，暂无实际作用）
  ├── components/Dialog/cbs/cbs.vue      # CBS银行回单弹窗
  └── utils/codeList.js                  # moneyFormat 金额格式化
```

---

## 数据流转

### 3pl.vue / mainstay.vue 流水查询

```
页面挂载/activated
  → fetchOrganizationList（仅3pl.vue）获取组织权限列表
  → getDictionary 加载字典（账户类型选中时才请求）
  → getData → getSubjectFLowMeterPageList / get3plFLowMeterPageList
  → list / total 更新表格

账户类型变更
  → getDictionaryEnumerationList 刷新字典
  → businessType 清空 → dictionaryListSecond 清空 → businessTypeSubset 清空

一级分类变更
  → 从 dictionaryList[].secondLevels 中本地过滤二级分类
  → businessTypeSubset 清空
```

### credit.vue 新增打款

```
点击"新增打款"
  → showCBSDeital = true → cbs.vue 弹窗
  → 用户选择 CBS 回单 → 触发 callBack 事件
  → saveSubjectRemitNow(item, code) 字段映射
  → saveSubjectRemit(params) 接口调用
  → closeDialog(1) → getData() 刷新列表
```

---

## API 接口

### api/index.js（3PL 侧）

| 方法 | 接口路径 | 说明 |
|------|---------|------|
| `get3plFLowMeterPageList` | POST `/flowMeter/get3plFLowMeterPageList` | 3PL 流水列表分页 |
| `get3plFLowMeterExcel` | POST `/flowMeter/get3plFLowMeterExcel` | 3PL 流水导出（blob） |
| `getDictionaryEnumerationList` | POST `/flowMeter/getDictionaryEnumerationList` | 流水类型/用途字典 |

### api/mainstay.js（主体侧）

| 方法 | 接口路径 | 说明 |
|------|---------|------|
| `getSubjectFLowMeterPageList` | POST `/flowMeter/getSubjectFLowMeterPageList` | 主体流水列表分页 |
| `getSubjectFLowMeterExcel` | POST `/flowMeter/getSubjectFLowMeterExcel` | 主体流水导出（blob） |
| `getSubjectRemitPageList` | POST `/credit/getSubjectRemitPageList` | 授信打款流水列表 |
| `getSubjectCreditAccountPageList` | POST `/accountAmount/getSubjectCreditAccountPageList` | 主体授信账户列表 |
| `saveSubjectRemit` | POST `/subjectRemit/saveSubjectRemit` | 新增授信打款记录 |

---

## 状态管理

- `this.$store.state.app.controlBtn`：权限按钮控制（`exportBtn` 导出、`newPaymentBtn` 新增打款）
- `this.$store.state.app.userInfo.companyId`：当前用户所属公司 ID，兜底读 `sessionStorage.companyId`
- `this.$store.dispatch('app/getUserInfo')`：3pl.vue 中异步获取 companyId 用于组织列表查询

---

## 注意事项

1. **导出方式变更**：三个文件均保留了旧的 `getExcel()` 方法和被注释的导出按钮，实际导出已改为通用 `ExportBtn` 组件（`3pl.vue` 和 `mainstay.vue`），`credit.vue` 无导出功能。

2. **credit.vue 的 creditMoney**：页面展示"已打款/未打款金额"，但 `creditMoney` 对象当前未通过接口赋值（默认 `'0'`），疑似为待完善功能。

3. **时间范围限制**：`3pl.vue` 和 `mainstay.vue` 通过 `pickerOptionsLimit` mixin 限制日期选择范围，mixin 中的 `is_DEFAULT_DAYS_30: true` 控制默认展示最近 30 天。

4. **弹窗组件共用**：`3pl.vue` 和 `mainstay.vue` 共用 `components/Dialog/3pl/` 下的同一套弹窗组件（recharge / withdrawalDetial / creditDetial），传入 `appInfo` 和 `companyInfo` 区分上下文（mainstay.vue 中 `appInfo` 默认为空对象）。

5. **ohterType 字段拼写**：详情弹窗路由判断中使用 `row.ohterType`（非 `otherType`），为后端原始字段名，注意勿自行修正。

---

## 相关文档

- [账户流水优化需求](/Users/limengxiao/workspace/wlyd/.md/需求/【C111.1】账户流水优化.md)
- [mainstay 模块 API](../api/index.js)
- [pickerOptionLimit mixin](../../../../../../mixins/pickerOptionLimit.js)

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
