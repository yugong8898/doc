# app-core 子应用详解

## 概述

`app-core` 是**商品交易子应用**，负责货源发布、运力管理、订单管理、司机/车辆管理等核心业务功能。

**路由前缀**: `/app-core`  
**开发端口**: `5679`

---

## 目录结构

```
app-core/src/
├── api/                           # 接口定义
│   ├── business/                  # 商品交易相关
│   ├── capacity/                  # 运力（司机、车辆）
│   ├── order/                     # 订单
│   ├── settlement/                # 结算
│   └── ...
├── components/                    # 全局组件
│   ├── vehicle-spec-selector/     # 车型选择器
│   ├── time-range-picker/         # 时间范围选择
│   └── ...
├── composables/                   # 组合式 API
│   ├── useGoodsActions.ts         # 货源操作
│   ├── useHandlerOptions.ts       # 操作选项
│   ├── useWhitelistCheck.ts       # 白名单检查
│   └── ...
├── enums/                         # 枚举常量
├── router/
│   ├── index.ts                   # 路由创建（接收主应用注入）
│   └── routes.ts                  # 静态路由（空数组）
├── stores/                        # 状态管理
│   ├── userInfo.ts                # 用户信息（从主应用同步）
│   └── ...
├── utils/
│   ├── useMainProps.ts            # 主应用 props 工具 ⭐
│   └── ...
├── views/                         # 页面组件 ⭐
│   ├── business/                  # 商品交易
│   │   ├── logistics-transaction/ # 货源管理
│   │   │   ├── index.vue          # 货源列表
│   │   │   ├── company-publish.vue # 企业发布货源
│   │   │   ├── driver-publish.vue  # 司机发布货源
│   │   │   ├── company-goods-detail.vue # 企业货源详情
│   │   │   ├── driver-goods-detail.vue  # 司机货源详情
│   │   │   └── components/        # 货源组件
│   │   └── carrier-goods/         # 承运商货源
│   ├── capacity/                  # 运力管理
│   │   ├── driver-manage/         # 司机管理
│   │   └── vehicle-manage/        # 车辆管理
│   ├── order/                     # 订单管理
│   │   ├── carrier-order/         # 承运商订单
│   │   └── shipment-order/        # 发货单
│   └── paymentManagement/         # 支付管理
├── App.vue
└── main.ts                        # 子应用入口 ⭐
```

---

## 子应用启动流程（main.ts）

```typescript
renderWithQiankun({
  mount(props) {
    router = microRoutes(props)  // 创建路由（注入主应用 props）
    asyncInitDeviceId()
      → app = createApp(App)
      → initSentryOnce()         // Sentry 初始化
      → app.use(router)
      → setGlobalRouter(router)
      → app.use(pinia)
      → initTrack()              // 埋点
      → app.mount(mountContainer)
      → userInfoStore.initUserInfo()  // 初始化用户信息
  },
  
  unmount() {
    app?.unmount()
    app = null
    router = null
    // 注意：不清空 userInfoStore，保留缓存
  }
})
```

**关键点**：
- 路由完全由主应用通过 `props.routes` 注入，`routes.ts` 为空数组
- 挂载点：`#subappContainer` 下的 `#sub-app`
- 卸载时不清空用户信息（保留缓存，token 变化时才重新拉取）

---

## 路由配置（router/index.ts）

```typescript
export const createRouter = (config: any) => {
  let dynamicRoutes = routes  // routes.ts 导出空数组
  
  // 主应用注入路由
  if (typeof config !== 'string' && config.routes) {
    dynamicRoutes = config.routes.map(v => ({
      ...v,
      path: v.path.replace(v.meta?.subappkey || '', ''),  // 移除子应用前缀
      component: loadView(v.url),  // 动态加载组件
    }))
  }
  
  return createVueRouter({
    history: config.history,
    routes: [...dynamicRoutes, ...routes],
  })
}
```

**loadView**：使用 `import.meta.glob` 预加载所有视图组件，按路径匹配加载。

---

## 核心业务

### 1. 货源管理（logistics-transaction/）

#### 货源列表（index.vue）

```vue
<template>
  <CustomerGuide page-type="SEND_GOODS_SOURCE" />
  <GeneralGoodsList ref="generalFoodsRef" />
</template>
```

- **CustomerGuide**：新手引导
- **GeneralGoodsList**：货源列表（筛选、操作、分页）

#### 发布货源

- **企业发布**（`company-publish.vue`）：企业用户发布货源
- **司机发布**（`driver-publish.vue`）：司机用户发布货源
- **全流程发布**（`full-process-publish.vue`）：货主全流程发货

发布表单模块：
- **base-info**：基础信息（货物名称、重量、体积）
- **goods-info**：货物信息
- **transport-info**：运输信息（起始地、目的地、车型）
- **settlement-info**：结算信息（运费、结算方式）
- **driver-transport-form**：司机运输信息

#### 货源详情

- **企业货源详情**（`company-goods-detail.vue`）
- **司机货源详情**（`driver-goods-detail.vue`）

详情页组件：
- **quote-info-query**：报价信息查询
- **goods-driver-detail**：司机货源详情
- **goods-company-detail**：企业货源详情
- **entrust-flow-dialog**：委托流程弹窗

#### 货源操作（useGoodsActions.ts）

```typescript
const actions = [
  '指派司机',      // assignDriver
  '指派承运商',    // assignCarrier
  '取消指派',      // cancelAssign
  '删除货源',      // deleteGoods
  '修改报价时间',  // updateQuoteTime
  '确认报价',      // confirmQuote
  // ...
]
```

### 2. 运力管理（capacity/）

#### 司机管理（driver-manage/）

- **司机列表**（`index.vue`）：司机档案、状态、认证信息
- **司机详情**（`driver-detail.vue`）：
  - 身份证审核（`id-card-audit.vue`）
  - 驾驶证审核（`driver-audit.vue`）
  - 从业资格证审核（`professional-audit.vue`）
  - 支付信息（`payment-info.vue`）

司机操作：
- 邀请司机（`invitation-driver-dialog.vue`）
- 添加常用车辆（`common-car-dialog.vue`）
- 身份证识别（`id-card-dialog.vue`）

#### 车辆管理（vehicle-manage/）

- **车辆列表**（`index.vue`）：车辆档案、状态、认证信息
- **车辆详情**（`vehicle-detail.vue`）：
  - 车辆审核（`vehicle-audit.vue`）
  - 运输证审核（`transport-audit.vue`）

车辆操作：
- 添加自有车辆（`add-own-vehicle-dialog.vue`）
- 设置默认车辆（`default-car-dialog.vue`）

### 3. 订单管理（order/）

#### 承运商订单（carrier-order/）

- **订单列表**（`index.vue`）
- **订单详情**（`order-detail.vue`）：
  - 货运信息（`shipment-info.vue`）
  - 承运商信息（`carrier-info.vue`、`multiple-carrier-info.vue`）
  - 在线货源详情（`online-goods-detail.vue`）
  - 铁路运单（`rail-waybill/index.vue`）

订单操作：
- 订单拆单（`order-split-dialog.vue`）
- 上传合同（`upload-contract.vue`）
- 客户设置（`customer-setting-dialog.vue`）
- 评价（`evaluate.vue`）

#### 发货单（shipment-order/）

- **发货单列表**（`index.vue`）
- **发货单详情**（`order-detail.vue`）
- **支付**（`payment.vue`）

### 4. 支付管理（paymentManagement/）

#### 订单支付（orderPayment/）

```vue
<template>
  <div class="payment-container">
    <MyRadio />     <!-- 支付方式选择 -->
    <MyCoupon />    <!-- 优惠券 -->
    <MyCombo />     <!-- 组合支付 -->
  </div>
</template>
```

支付方式：
- 钱包支付
- 组合支付（钱包 + 优惠券）
- 货主支付

---

## 用户信息管理（stores/userInfo.ts）

```typescript
const useUserInfoStore = defineStore('userInfo', () => {
  const props = getMainProps()  // 从主应用获取 props
  const mainUserStore = props?.userStore
  
  const initUserInfo = async () => {
    if (mainUserStore) {
      // 从主应用同步用户信息
      await mainUserStore.fetchUserInfo()
    }
  }
  
  return { initUserInfo, ...toRefs(mainUserStore) }
})
```

子应用不自己维护用户信息，直接从主应用的 `userStore` 同步。

---

## 主应用 Props 工具（useMainProps.ts）

```typescript
export const isMicroApp = () => {
  return window.__POWERED_BY_QIANKUN__
}

export const getMainProps = () => {
  return window.microApp?.props || {}
}

export const getMicroContainer = () => {
  return window.__MICRO_APP_BASE_CONTAINER__
}

export const microRoutes = (props: any) => {
  const { routerBase, routes, mainRouter } = props
  return createRouter({
    history: createWebHistory(routerBase),
    routes,
  })
}
```

---

## 关键特性

### 1. 货源状态机

货源状态流转：
```
待接单 → 已接单 → 运输中 → 已完成
      ↓
    已取消
```

### 2. 车型选择器（vehicle-spec-selector/）

```vue
<VehicleSpecSelector
  v-model="selectedSpec"
  :mode="'single'"  <!-- single/multiple -->
  @change="handleChange"
/>
```

车型数据结构：
- **车长**：4.2米、6.8米、9.6米、13米、17.5米
- **车型**：厢式、高栏、平板、冷藏
- **吨位**：1吨、2吨、5吨、10吨、20吨

### 3. 时间范围选择（time-range-picker/）

```vue
<TimeRangePicker
  v-model:start="startTime"
  v-model:end="endTime"
  :type="'datetime'"  <!-- date/datetime -->
  :shortcuts="shortcuts"
/>
```

### 4. 白名单检查（useWhitelistCheck.ts）

```typescript
const { isInWhitelist, checkWhitelist } = useWhitelistCheck()

if (!isInWhitelist.value) {
  ElMessage.warning('您不在白名单中，暂时无法使用该功能')
  return
}
```

---

## API 接口

### 货源接口（api/business/）

```typescript
// 货源列表
export const getGoodsList = (params: any) => request.post('/goods/list', params)

// 发布货源
export const publishGoods = (params: any) => request.post('/goods/publish', params)

// 指派司机
export const assignDriver = (params: any) => request.post('/goods/assignDriver', params)

// 确认报价
export const confirmQuote = (params: any) => request.post('/goods/confirmQuote', params)
```

### 运力接口（api/capacity/）

```typescript
// 司机列表
export const getDriverList = (params: any) => request.post('/driver/list', params)

// 车辆列表
export const getVehicleList = (params: any) => request.post('/vehicle/list', params)

// 邀请司机
export const inviteDriver = (params: any) => request.post('/driver/invite', params)
```

### 订单接口（api/order/）

```typescript
// 订单列表
export const getOrderList = (params: any) => request.post('/order/list', params)

// 订单详情
export const getOrderDetail = (params: any) => request.post('/order/detail', params)

// 订单支付
export const payOrder = (params: any) => request.post('/order/pay', params)
```

---

## 组件复用

### 1. 地址搜索（addres-search-input.vue）

```vue
<AddressSearchInput
  v-model="address"
  :type="'origin'"  <!-- origin/destination -->
  @select="handleSelect"
/>
```

### 2. 地址识别（address-recognition-modal.vue）

粘贴文本自动识别：
- 收货人姓名
- 手机号
- 省市区
- 详细地址

### 3. 常用地址（usual-address-modal/）

- **地址列表**（`address-list.vue`）
- **线路列表**（`line-list.vue`）

---

## 相关文档

- [项目总览](./项目总览.md)
- [app-main 详解](./app-main详解.md)
- [app-base 详解](./app-base详解.md)
- [app-dispatch 详解](./app-dispatch详解.md)

---

**文档版本**: v1.0

**最后更新**: 2026年06月

**整理人**: 王新骏
