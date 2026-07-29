# `/PlatformUmCompany/companyTreeList` 接口使用梳理

> 梳理范围：logisticsweb、platformweb、bdbl-admin 三个项目

## 目录

- [一、接口概述](#一接口概述)
- [二、logisticsweb 项目](#二logisticsweb-项目)
- [三、platformweb 项目](#三platformweb-项目)
- [四、bdbl-admin 项目](#四bdbl-admin-项目)
- [五、总结对照表](#五总结对照表)
- [六、替代接口说明](#六替代接口说明)
- [七、易混淆接口（排除项）](#七易混淆接口排除项)
- [八、触发机制与风险说明](#八触发机制与风险说明)

---

## 一、接口概述

- **接口路径**：`/PlatformUmCompany/companyTreeList`（用户原始描述 `/platform/PlatformUmCompany/companyTreeList`，其中 `/platform` 为各项目 baseUrl 前缀，后缀路径一致）
- **用途**：根据公司编码获取该公司下所有子集公司（树形结构，业务归属树）
- **原开发对接**：大藩-林枫
- **现状**：三个项目均已逐步引入新接口替代，但部分封装函数和调用链仍保留

---

## 二、logisticsweb 项目

### 2.1 接口封装定义（3 处）

| # | 文件 | 行号 | 函数名 | 状态 |
|---|------|------|--------|------|
| 1 | `src/api/login.js` | 140 | `getOrganizationTreeList` | 废弃（调用链已注释） |
| 2 | `src/api/WaybillData.js` | 34 | `companyTreeList` | ✅ **在用** |
| 3 | `src/api/businessOwnershipWaybill.js` | 8 | `companyTreeList` | 死代码（无调用方） |

三者 URL 均为 `config.baseUrllgiUser + '/PlatformUmCompany/companyTreeList'`。

### 2.2 调用链详情

#### ① `getOrganizationTreeList`（login.js）— 废弃

```
src/api/login.js:140  getOrganizationTreeList()
  ↓（已注释）
src/vuex/modules/app.js
  - import 已注释：// getOrganizationTreeList,
  - action 体已注释保留：// getChildCompany({ commit, state }, payload) { ... }
  ↓（已注释）
src/router/index.js:71         // store.dispatch('app/getChildCompany', {})
src/utils/useMainProps.js:292  // store.dispatch('app/getChildCompany', {})
```

- 替代方案：`fetchCompanyTreeList`（新接口），通过 `getChildCompanyTreeList` action 调用
- `src/layout/components/Header.vue:152` 仅在注释中提及旧逻辑，实际使用 `getChildCompanyTreeList`

#### ② `companyTreeList`（WaybillData.js）— ✅ 在用

```
src/api/WaybillData.js:34  companyTreeList(data, id)
  ↓
src/views/userBase/WaybillDataNew20260622/index.vue
  - 行 401：import { companyTreeList } from '@/api/WaybillData'
  - 行 532：activated() { ... this.getTree() }
  - 行 544：companyTreeList({}, `/${this.$store.state.app.userInfo.companyId}`).then(...)
```

- 用途：运单数据（新版 2026-06-22）页面获取企业树形列表，用于企业筛选
- **触发机制**：`activated()` 生命周期调用 `getTree()`，页面经 `AppMain.vue` 的 `<keep-alive>` 包裹（条件：`$route.path.includes('userBase')`），进入即触发，确证会发请求

#### ③ `companyTreeList`（businessOwnershipWaybill.js）— 死代码

- 定义了 `companyTreeList` 函数，但全项目无任何文件 import 调用
- `src/views/userBase/businessOwnershipWaybill/index.vue` 仅 import 了 `waybillSummaryBusinessBelongPage`、`dmsWaybillBusinessBelongExport`，未引用 `companyTreeList`

### 2.3 间接调用（已切换新接口，非目标接口）

以下文件通过 Vuex `app/getChildCompanyTreeList` action 调用 `fetchCompanyTreeList`（新接口），**不再使用** `/PlatformUmCompany/companyTreeList`：

| 文件 | 说明 |
|------|------|
| `src/components/CompanyTree/index.vue` | 公共企业树组件 |
| `src/layout/components/Header.vue` | 头部企业切换 |
| `src/router/index.js` | 路由前置守卫初始化 |
| `src/utils/useMainProps.js` | 主布局 props 初始化 |

---

## 三、platformweb 项目

### 3.1 接口封装定义（2 处）

| # | 文件 | 行号 | 函数名 | 状态 |
|---|------|------|--------|------|
| 1 | `src/views/infolook/api/public/WaybillData.js` | 46 | `companyTreeList` | 死代码（@deprecated，引用组件无页面使用） |
| 2 | `src/api/transaction/businessOwnershipWaybill.js` | 13 | `companyTreeList` | 死代码（@deprecated，无调用方） |

两者 URL 均为 `BASE_API + '/PlatformUmCompany/companyTreeList' + id`。

### 3.2 调用链详情

#### ① `companyTreeList`（infolook/api/public/WaybillData.js）— 死代码

```
src/views/infolook/api/public/WaybillData.js:46  companyTreeList(data, id)  // 标记 @deprecated
  ↓
src/components/Selectmore/selsectTree.vue:29
  - import { companyTreeList } from '@/views/infolook/api/public/WaybillData.js'
  - 行 68：companyTreeList({}, `/${2}`).then(...)
  ↓
（无页面引用该组件）
```

- **关键发现**：`@/components/Selectmore/selsectTree.vue` 虽内部调用了 `companyTreeList`，但全项目搜索 `Selectmore/selsectTree` **无任何页面引用**该组件
- **易混淆点（重要）**：`views/matching/waybill/components/selsectTree.vue` 和 `views/matching/dispatchWorkbench/dispatchWaybill/components/selsectTree.vue` 是**同名本地组件**，但它们使用的是 `getBusinessCompanyTree`（`@/api/matching/waybill`），**不是**目标接口。这两个本地组件分别被 `matching/waybill/road/index.vue`（import 路径 `'../components/selsectTree.vue'`）和 `matching/dispatchWorkbench/dispatchWaybill/index.vue`（import 路径 `'./components/selsectTree.vue'`）引用，但均与 `/PlatformUmCompany/companyTreeList` 无关

#### ② `companyTreeList`（transaction/businessOwnershipWaybill.js）— 死代码

- 标记 `@deprecated`，全项目无任何文件 import 该函数
- `src/views/transaction/businessOwnershipWaybill/` 下各文件 import 的是 `dmsWaybillBusinessBelongPaging`、`dmsWaybillBusinessBelongExport`、`queryFreightReminder` 等其他函数

### 3.3 间接调用（已切换新接口，非目标接口）

| 文件 | 说明 |
|------|------|
| `src/components/CompanyTree/index.vue` | 公共企业树组件，使用 `getChildCompanyTreeList` action |
| `src/vuex/modules/app.js` | `getChildCompanyTreeList` action 调用 `fetchCompanyTreeList`（新接口） |
| `src/api/system/login.js` | `fetchCompanyTreeList` 封装（新接口） |

---

## 四、bdbl-admin 项目

### 4.1 接口封装定义（1 处）

| # | 文件 | 行号 | 函数名 | 完整 URL | 状态 |
|---|------|------|--------|----------|------|
| 1 | `src/api/login.js` | 92 | `getOrganizationTreeList` | `baseUrl + '/PlatformUmCompany/companyTreeList'` | 废弃（触发点已注释） |

### 4.2 调用链详情

#### ① `getOrganizationTreeList`（login.js）— 废弃

```
src/api/login.js:92  getOrganizationTreeList(payload)
  ↓
src/vuex/modules/app.js
  - 行 1：import { getOrganizationTreeList } from '../../api/login'
  - 行 119：getChildCompany action 中调用 getOrganizationTreeList({ companyCode: state.companyId })
  ↓（已注释）
src/router/index.js:44  // store.dispatch('app/getChildCompany', {})
```

- import 未注释（仍引入），action 定义未注释（仍保留），但**唯一触发点** `router/index.js` 已注释
- 全项目搜索 `getChildCompany` 仅 `router/index.js`（注释）和 `app.js`（定义）两处，无其他调用方
- 结论：接口封装和 action 保留但**实际不会执行**

---

## 五、总结对照表

| 项目 | 文件 | 函数 | 状态 | 实际调用方 |
|------|------|------|------|-----------|
| logisticsweb | `src/api/WaybillData.js` | `companyTreeList` | ✅ **在用** | `WaybillDataNew20260622/index.vue` |
| logisticsweb | `src/api/login.js` | `getOrganizationTreeList` | 废弃 | 无（调用链全注释） |
| logisticsweb | `src/api/businessOwnershipWaybill.js` | `companyTreeList` | 死代码 | 无 |
| platformweb | `src/views/infolook/api/public/WaybillData.js` | `companyTreeList` | 死代码 | `Selectmore/selsectTree.vue`（但该组件无页面引用） |
| platformweb | `src/api/transaction/businessOwnershipWaybill.js` | `companyTreeList` | 死代码 | 无 |
| bdbl-admin | `src/api/login.js` | `getOrganizationTreeList` | 废弃 | 无（触发点已注释） |

### 真正在用的仅 1 处

- **logisticsweb** `src/views/userBase/WaybillDataNew20260622/index.vue` 通过 `src/api/WaybillData.js` 的 `companyTreeList` 函数调用

---

## 六、替代接口说明

三个项目均已引入新接口替代 `/PlatformUmCompany/companyTreeList`：

| 项目 | 新接口封装 | 新接口路径 | Vuex action |
|------|-----------|-----------|-------------|
| logisticsweb | `src/api/login.js` → `fetchCompanyTreeList` | `/plat-company/find-company-list-by-biz-company-id-for-cache` | `app/getChildCompanyTreeList` |
| platformweb | `src/api/system/login.js` → `fetchCompanyTreeList` | `/company/find-company-list-by-biz-company-id-for-cache` | `app/getChildCompanyTreeList` |
| bdbl-admin | 暂无（旧 action 未替换） | — | — |

新接口支持 `companyId` + `isNext`（0-当前/1-下一级）参数，支持 el-tree lazy 模式按节点加载子节点，并带内存缓存（Vuex `childCompanyTree`）。

> 注意：logisticsweb 的 `WaybillDataNew20260622/index.vue` 仍在用旧接口，尚未迁移到新接口。

---

## 七、易混淆接口（排除项）

以下同名 / 近名调用**不是**本接口，梳理时已排除，请勿混淆：

| 接口 / 函数 | 项目 | 实际路径 | 说明 |
|-------------|------|----------|------|
| `companyTreeListByCompanyId` | platformweb | `DMS_API + '/dpeq/companyTreeListByCompanyId'` | 完全不同的接口（`dpeq` 路径），由 `w-graph-table.vue` 调用 |
| `getCompanyTreeList` | platformweb | `/gateway/lmt-platform/company/company-tree-list` | `CostDiffRateManagement` 使用，新网关接口 |
| `fetchCompanyTreeList` | platformweb / logisticsweb | `/company/find-company-list-by-biz-company-id-for-cache`、`/plat-company/find-company-list-by-biz-company-id-for-cache` | **官方替代接口**，Vuex `getChildCompanyTreeList` 与 `CompanyTree` 组件使用 |
| `getChildCompanyTreeList`（vuex action） | platformweb / logisticsweb | 内部调用 `fetchCompanyTreeList` | 已迁移到新接口 |
| `getBusinessCompanyTree` | platformweb | `@/api/matching/waybill` | matching 目录下本地 `selsectTree.vue` 使用，与目标接口无关 |
| `agencyTreeList` | 三项目均有 | `/PlatformUmCompany/agencyTreeList` 等 | 代理公司树，非本接口 |

---

## 八、触发机制与风险说明

### 1. 活跃调用的触发机制

唯一在用的 logisticsweb `WaybillDataNew20260622/index.vue`：

- `getTree()` 写在 `activated()` 生命周期（第 532 行），而非 `created/mounted`
- 页面经 `AppMain.vue` 的 `<keep-alive>` 包裹（条件：`$route.meta.hierarchy !== 4 && $route.path.includes('userBase')`），进入即触发 `activated` → `getTree()` → **确定发请求**
- 风险：若该页面被移出 keep-alive 或路由路径不再包含 `userBase`，则首次进入也不会触发接口，业务归属树会为空

### 2. 废弃标记不一致

| 项目 | 文件 | 是否标注 @deprecated |
|------|------|---------------------|
| platformweb | `views/infolook/api/public/WaybillData.js` | ✅ 已标注 |
| platformweb | `api/transaction/businessOwnershipWaybill.js` | ✅ 已标注 |
| logisticsweb | `api/WaybillData.js` | ❌ 未标注（但在用） |
| logisticsweb | `api/login.js` | ❌ 未标注（已废弃） |
| logisticsweb | `api/businessOwnershipWaybill.js` | ❌ 未标注（死代码） |
| bdbl-admin | `api/login.js` | ❌ 未标注（已废弃） |

- 建议统一补充 `@deprecated` 标注（logisticsweb `WaybillData.js` 除外，因为仍在用），并在注释中指明替代接口，降低后续维护误用风险

### 3. 前缀差异

三项目 baseUrl 变量不同（platformweb `BASE_API`、logisticsweb `config.baseUrllgiUser`、bdbl-admin `baseUrl`），但请求路径后缀均为 `/PlatformUmCompany/companyTreeList`，最终打到同一后端 controller。

### 4. 下线建议

若计划下线 `/PlatformUmCompany/companyTreeList` 接口：
- 需先迁移上述 **1 处活跃调用**（logisticsweb `WaybillDataNew20260622`）到 `fetchCompanyTreeList`，否则该页面的业务归属树将失效
- 5 处死代码 / 废弃封装可评估清理（注意 bdbl-admin 的 `getOrganizationTreeList` 是「被注释关闭」而非纯死代码，清理前需确认产品无重新启用的计划）

---

**文档版本**: v2.0
**最后更新**: 2026年7月
**整理人**: 王新骏
