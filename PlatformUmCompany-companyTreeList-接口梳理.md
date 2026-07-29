# `/PlatformUmCompany/companyTreeList` 接口使用梳理

## 目录

- [一、接口概述](#一接口概述)
- [二、梳理范围与方法](#二梳理范围与方法)
- [三、三项目调用总览](#三三项目调用总览)
- [四、各项目详细分析](#四各项目详细分析)
  - [4.1 platformweb](#41-platformweb)
  - [4.2 logisticsweb](#42-logisticsweb)
  - [4.3 bdbl-admin](#43-bdbl-admin)
- [五、易混淆接口（排除项，避免误判）](#五易混淆接口排除项避免误判)
- [六、触发机制与风险说明](#六触发机制与风险说明)
- [七、结论与建议](#七结论与建议)

---

## 一、接口概述

- **目标接口**：`/PlatformUmCompany/companyTreeList`（用户原始描述为 `/platform/PlatformUmCompany/companyTreeList`，其中 `/platform` 为各项目 baseUrl 前缀，后缀路径一致）
- **功能**：根据公司编码递归获取该公司下所有子集公司树（业务归属树）
- **现状**：该接口已被标记为 `@deprecated`，官方替代接口为 `fetchCompanyTreeList`（路径：`/company/find-company-list-by-biz-company-id-for-cache` 或 `/plat-company/...`），新组件 `CompanyTree` 与 Vuex `getChildCompanyTreeList` 已切换到新接口
- **梳理目的**：确认该接口在三个前端项目中是否仍被真实调用、哪些封装已是死代码

---

## 二、梳理范围与方法

| 项目 | 技术栈 | 源码路径 |
|------|--------|----------|
| platformweb | Vue2 + Element UI | `platformweb/src` |
| logisticsweb | Vue2 + Element UI | `logisticsweb/src` |
| bdbl-admin | Vue2 + Element UI | `bdbl-admin/src` |

**方法**：对三个项目 `src` 目录全量检索 `companyTreeList`、`PlatformUmCompany`、`getOrganizationTreeList` 等关键词，定位接口封装定义与所有 import/调用点，并逐层向上追溯触发时机（mounted / created / activated）与路由 keep-alive 包裹情况，区分「活跃调用」与「死代码 / 未启用」。

---

## 三、三项目调用总览

| 项目 | 封装函数 | 定义位置 | 实际请求路径 | 状态 | 真实调用方 |
|------|----------|----------|--------------|------|------------|
| platformweb | `companyTreeList` | `views/infolook/api/public/WaybillData.js` | `BASE_API + '/PlatformUmCompany/companyTreeList' + id` | **活跃** | `components/Selectmore/selsectTree.vue` → `matching/waybill/road` 等 |
| platformweb | `companyTreeList` | `views/transaction/businessOwnershipWaybill.js` | `BASE_API + '/PlatformUmCompany/companyTreeList' + id` | **死代码** | 无引用方 |
| logisticsweb | `companyTreeList` | `api/WaybillData.js` | `config.baseUrllgiUser + '/PlatformUmCompany/companyTreeList'` | **活跃** | `views/userBase/WaybillDataNew20260622/index.vue` |
| logisticsweb | `companyTreeList` | `api/businessOwnershipWaybill.js` | `config.baseUrllgiUser + '/PlatformUmCompany/companyTreeList'` | **死代码** | 无引用方 |
| logisticsweb | `getOrganizationTreeList` | `api/login.js` | `config.baseUrllgiUser + '/PlatformUmCompany/companyTreeList'` | **死代码（已注释）** | vuex 中 `getChildCompany` 注释未调用 |
| bdbl-admin | `getOrganizationTreeList` | `api/login.js` | `baseUrl + '/PlatformUmCompany/companyTreeList'` | **死代码（未启用）** | vuex `getChildCompany` 的 dispatch 被注释 |

> **结论速览**：三项目中真正仍在发请求的活跃调用点仅 **2 处**（platformweb 公路运单页、logisticsweb WaybillDataNew20260622 页）；另有 **4 处**封装为死代码 / 未启用，不会实际请求。

---

## 四、各项目详细分析

### 4.1 platformweb

#### 4.1.1 活跃调用（确证会发请求）

**封装定义**：`platformweb/src/views/infolook/api/public/WaybillData.js`

```44:55:platformweb/src/views/infolook/api/public/WaybillData.js
// 企业
// @deprecated 已废弃，请使用 fetchCompanyTreeList
export function companyTreeList(data, id) {
  return request({
    url: BASE_API + '/PlatformUmCompany/companyTreeList' + id
  })
}
```

**唯一真实调用方**：`platformweb/src/components/Selectmore/selsectTree.vue`（「业务归属」下拉树组件）

```67:68:platformweb/src/components/Selectmore/selsectTree.vue
getTree() {
  companyTreeList({}, `/${2}`).then(data => {
```

`selsectTree.vue` 被以下页面引用：
- `platformweb/src/views/matching/waybill/road/index.vue`（第 16、371、376 行）—— 撮合-公路运单页，业务归属筛选
- `platformweb/src/views/matching/dispatchWorkbench/dispatchWaybill/index.vue`（第 15、223、229 行）—— 撮合-调度工作台-调度运单页，业务归属筛选

**触发链路确认**：
- `road/index.vue` 经 `waybillLayout.vue` 的 `<keep-alive>` 渲染（`waybillLayout.vue` 第 12-16 行包裹 `RoadwayWaybill`/`RailwayWaybill`/`WaterwayWaybill`，其中 `RoadwayWaybill` 即 `road/index.vue`）。页面被 keep-alive 缓存 → 进入即触发 `activated` → `selsectTree.getTree()` → **确定发请求**。
- `dispatchWaybill/index.vue` 所在的 dispatchWorkbench 区域同级组件普遍依赖 `activated`（如 `transportPool`、`companyCargo` 等），推断该页面同样处于 keep-alive 内会触发，建议实际进入页面抓包确认一次。

#### 4.1.2 死代码（无引用方）

**封装定义**：`platformweb/src/views/transaction/businessOwnershipWaybill.js`

```11:22:platformweb/src/views/transaction/businessOwnershipWaybill.js
// 企业
// @deprecated 已废弃，请使用 fetchCompanyTreeList
export function companyTreeList(data, id) {
  return request({
    url: BASE_API + '/PlatformUmCompany/companyTreeList' + id
  })
}
```

对该文件全部 12 处引用（`dmsWaybillPeriodStatistics`、`queryFreightReminder`、`updateWaybillTag` 等）逐一核对，均指向同文件其他函数，**无任何位置引用此 `companyTreeList`**。属于无人调用的死代码。

### 4.2 logisticsweb

#### 4.2.1 活跃调用（确证会发请求）

**封装定义**：`logisticsweb/src/api/WaybillData.js`

```33:43:logisticsweb/src/api/WaybillData.js
// 企业
export function companyTreeList(data, id) {
  return request({
    url: config.baseUrllgiUser + '/PlatformUmCompany/companyTreeList'
  })
}
```

**真实调用方**：`logisticsweb/src/views/userBase/WaybillDataNew20260622/index.vue`（第 401 行 import，第 543-556 行 `getTree`）

```525:532:logisticsweb/src/views/userBase/WaybillDataNew20260622/index.vue
activated() {
  ...
  this.getTree()   // 第 532 行
  ...
}
getTree() {
  companyTreeList({}, `/${this.$store.state.app.userInfo.companyId}`).then(data => {  // 第 544 行
```

**触发确认**：该页面位于 `userBase`，`logisticsweb/src/layout/components/AppMain.vue` 第 3-6 行对「`route.meta.hierarchy !== 4` 且路径含 `userBase`」的路由走 `<keep-alive>` 渲染，进入即触发 `activated` → `getTree()` → **确定发请求**。

#### 4.2.2 死代码（无引用方）

**封装定义**：`logisticsweb/src/api/businessOwnershipWaybill.js`

```7:17:logisticsweb/src/api/businessOwnershipWaybill.js
// 企业
export function companyTreeList(data, id) {
  return request({
    url: config.baseUrllgiUser + '/PlatformUmCompany/companyTreeList'
  })
}
```

全项目仅 `views/userBase/businessOwnershipWaybill/index.vue` 引用了同文件其他函数（`waybillSummaryBusinessBelongPage`、`dmsWaybillBusinessBelongExport`），**未引用此 `companyTreeList`**。死代码。

#### 4.2.3 死代码（已注释未启用）

**封装定义**：`logisticsweb/src/api/login.js`

```140:145:logisticsweb/src/api/login.js
export function getOrganizationTreeList(payload) {
  return request({
    url: config.baseUrllgiUser + '/PlatformUmCompany/companyTreeList'
  })
}
```

`logisticsweb/src/vuex/modules/app.js` 第 7 行 `// getOrganizationTreeList` 已注释，第 361-364 行 `getChildCompany` action 整体注释，无任何 dispatch 调用到此函数。死代码。

### 4.3 bdbl-admin

#### 4.3.1 死代码（定义存在且被 action 调用，但 dispatch 被注释，未启用）

**封装定义**：`bdbl-admin/src/api/login.js`

```91:97:bdbl-admin/src/api/login.js
// 根据公司编码获取该公司下所有子集公司接口【大藩-林枫】
export function getOrganizationTreeList(payload) {
  return request({
    url: baseUrl + '/PlatformUmCompany/companyTreeList'
  })
}
```

**调用链**：`bdbl-admin/src/vuex/modules/app.js` 第 1 行 import 了 `getOrganizationTreeList`，第 119-123 行 `getChildCompany` action 内部调用了它：

```117:123:bdbl-admin/src/vuex/modules/app.js
// 根据公司编码获取该公司下所有子集公司接口
getChildCompany({ commit, state }, payload) {
  getOrganizationTreeList({
    companyCode: state.companyId
```

**未启用确认**：全局检索 `getChildCompany` 仅 2 处命中——`vuex/modules/app.js`（定义）与 `router/index.js`（dispatch 点）。而 `router/index.js` 第 44 行为：

```42:45:bdbl-admin/src/router/index.js
await store.dispatch('app/getUserInfo', {})
store.dispatch('public/loadCityData', {})
// store.dispatch('app/getChildCompany', {})   // ← dispatch 已注释
```

若从登录初始化拉取公司树，则该 dispatch 被注释后，`getChildCompany` 再无触发点，因此 `getOrganizationTreeList` 实际**不会发请求**，属于「未启用」状态（非典型死代码，而是被人为关闭）。

---

## 五、易混淆接口（排除项，避免误判）

以下同名 / 近名调用**不是**本接口，梳理时已排除，请勿混淆：

| 接口 / 函数 | 项目 | 实际路径 | 说明 |
|-------------|------|----------|------|
| `companyTreeListByCompanyId` | platformweb | `DMS_API + '/dpeq/companyTreeListByCompanyId'` | 完全不同的接口（`dpeq` 路径），由 `w-graph-table.vue` 调用 |
| `getCompanyTreeList` | platformweb | `/gateway/lmt-platform/company/company-tree-list` | `CostDiffRateManagement` 使用，新网关接口 |
| `fetchCompanyTreeList` | platformweb / logisticsweb | `/company/find-company-list-by-biz-company-id-for-cache`、 `/plat-company/find-company-list-by-biz-company-id-for-cache` | **官方替代接口**，Vuex `getChildCompanyTreeList` 与 `CompanyTree` 组件使用 |
| `getChildCompanyTreeList`（vuex action） | platformweb / logisticsweb | 内部调用 `fetchCompanyTreeList` | 已迁移到新接口 |
| `agencyTreeList` | 三项目均有 | `/PlatformUmCompany/agencyTreeList` 等 | 代理公司树，非本接口 |

---

## 六、触发机制与风险说明

1. **`activated` 依赖 keep-alive**
   两个活跃调用方（`selsectTree.getTree`、`WaybillDataNew20260622.getTree`）均把拉取动作写在 `activated()` 生命周期，而非 `created/mounted`。这意味着：**若所在页面未被 keep-alive 缓存，则首次进入也不会触发该接口，业务归属树会为空**。
   - 已确证处于 keep-alive 中、必然触发的有：platformweb `matching/waybill/road`、logisticsweb `userBase/WaybillDataNew20260622`。
   - platformweb `matching/dispatchWorkbench/dispatchWaybill` 所处区域普遍 keep-alive，推断会触发，建议实测。

2. **前缀差异**
   三项目 baseUrl 变量不同（platformweb `BASE_API`、logisticsweb `config.baseUrllgiUser`、bdbl-admin `baseUrl`），但请求路径后缀均为 `/PlatformUmCompany/companyTreeList`，最终打到同一后端 controller。

3. **废弃标记不完整**
   platformweb 的两处封装均标注 `@deprecated`，但 logisticsweb 与 bdbl-admin 的同名封装未标注，建议补充标记以保持一致。

---

## 七、结论与建议

### 活跃调用（确证会发请求，共 2 处）
1. **platformweb** `matching/waybill/road`（公路运单页）→ `selsectTree` → `WaybillData.js` 的 `companyTreeList`
2. **logisticsweb** `userBase/WaybillDataNew20260622` → `WaybillData.js` 的 `companyTreeList`

### 可能调用（建议实测，1 处）
- **platformweb** `matching/dispatchWorkbench/dispatchWaybill`（调度运单页）→ `selsectTree` → 推断触发，待抓包确认

### 死代码 / 未启用（共 4 处，不会发请求）
- platformweb `views/transaction/businessOwnershipWaybill.js` 的 `companyTreeList`（无引用方）
- logisticsweb `api/businessOwnershipWaybill.js` 的 `companyTreeList`（无引用方）
- logisticsweb `api/login.js` 的 `getOrganizationTreeList`（vuex 中已注释）
- bdbl-admin `api/login.js` 的 `getOrganizationTreeList`（vuex `getChildCompany` 的 dispatch 被注释，未启用）

### 建议
- 若计划下线 `/PlatformUmCompany/companyTreeList` 接口：需先迁移上述 2 处活跃调用到 `fetchCompanyTreeList`，否则公路运单页、WaybillDataNew20260622 页的业务归属树将失效。
- 4 处死代码封装可评估清理（注意 bdbl-admin 的 `getOrganizationTreeList` 是「被注释关闭」而非纯死代码，清理前需确认产品无重新启用的计划）。
- 统一补充 `@deprecated` 标注，并在注释中指明替代接口，降低后续维护误用风险。

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
