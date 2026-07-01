# app-dispatch 子应用详解

## 概述

`app-dispatch` 是**调度中心子应用**，负责智能调度、司机外呼、发货单指派等调度业务功能。

**路由前缀**: `/app-dispatch`  
**开发端口**: `5681`

---

## 目录结构

```
app-dispatch/src/
├── api/
│   └── dispatch/                  # 调度相关接口
│       ├── index.ts               # 接口定义
│       └── types/index.ts         # 类型定义
├── components/                    # 全局组件
│   ├── car-spec-picker/           # 车型选择器
│   │   ├── index.vue
│   │   └── CarSpecPanel.vue
│   ├── radius-picker/             # 半径选择器
│   ├── time-range-picker/         # 时间范围选择
│   └── remote-search-select/      # 远程搜索下拉
├── config/
│   ├── dictionary.ts              # 字典配置
│   └── env-config.ts              # 环境配置
├── enums/
│   └── dispatch/index.ts          # 调度相关枚举
├── router/
│   ├── index.ts                   # 路由创建
│   ├── routes.ts                  # 静态路由（空数组）
│   └── auth-inherit-config.ts     # 权限继承配置
├── stores/                        # 状态管理
│   ├── userInfo.ts                # 用户信息（从主应用同步）
│   ├── address.ts                 # 地址数据（省市区）
│   └── dictionary.ts              # 字典数据
├── utils/
│   ├── useMainProps.ts            # 主应用 props 工具
│   └── unit-tool.ts               # 单位工具
└── views/
    └── order/
        └── shipment-order/        # 发货单调度 ⭐
            ├── index.vue          # 智能调度主页面
            ├── utils/             # 工具函数
            └── components/
                ├── SmartDispatch.vue       # 智能调度组件
                ├── DriverTable.vue         # 司机列表
                ├── RecordingDialog.vue     # 录音回放弹窗
                └── DesensitizedField.vue  # 脱敏字段组件
```

---

## 子应用启动流程

与 app-core 相同的 qiankun 集成模式：

```typescript
renderWithQiankun({
  mount(props) {
    router = microRoutes(props)  // 路由完全由主应用注入
    app = createApp(App)
    app.use(router)
    app.use(pinia)
    app.mount(mountContainer)
    userInfoStore.initUserInfo()
  },
  unmount() {
    app?.unmount()
    // 保留用户信息缓存
  }
})
```

---

## 核心业务：发货单调度（shipment-order/）

### 页面结构（index.vue）

```vue
<template>
  <div class="shipment-order-page">
    <!-- 智能调度面板 -->
    <c-collapse title="智能调度">
      <!-- 司机列表（PlusPage 表格） -->
      <PlusPage :columns="driverColumns" :request="getDriverList">
        <!-- 智能外呼按钮 -->
        <template #table-title>
          <el-button @click="handleBatchSmartCall">智能外呼</el-button>
        </template>
        <!-- 脱敏手机号 -->
        <template #plus-cell-driverPhoneNumber="{ row }">
          <DesensitizedField ... />
        </template>
        <!-- 脱敏车牌号 -->
        <template #plus-cell-plateNo="{ row }">
          <DesensitizedField ... />
        </template>
      </PlusPage>
    </c-collapse>
    
    <!-- 录音回放弹窗 -->
    <RecordingDialog ref="recordingDialogRef" />
  </div>
</template>
```

### 入口参数（路由 query）

页面通过路由 `query` 接收货源信息，从 `app-core` 发货单列表跳转过来：

| 参数 | 说明 |
|------|------|
| `goodsId` | 货源 ID |
| `orderId` | 订单 ID |
| `sendAddress` | 装货地址 |
| `receiveAddress` | 卸货地址 |
| `goodsName` | 货源名称 |
| `goodsTotalWeight` | 总重量 |
| `goodsTotalVolume` | 总体积 |
| `loadStime` | 装货开始时间 |
| `loadEtime` | 装货结束时间 |
| `exctaxUnitPrice` | 不含税单价 |
| `pricingUnit` | 计价单位 |
| `settUnit` | 结算单位 |

### 司机列表（getDriverList）

**前端分页 + 全量缓存**：

```typescript
const getDriverList = async (params) => {
  const filterKey = `${goodsId}|${radius}|${vehicleType}|${vehicleLength}`
  
  // 筛选条件不变时，走本地缓存切片（不发请求）
  const useCache = driverListCacheKey.value === filterKey
  
  if (!useCache) {
    const res = await lingSuoRecommend({
      currentPage: 1,
      pageLength: 9999,     // 一次性拉取所有数据
      filterModel: { capacityRelationType: '10', goodsId, radius, vehicleType, vehicleLength }
    })
    driverListCache.value = res.model || []
    driverListCacheKey.value = filterKey
  }
  
  // 前端分页切片
  const allList = driverListCache.value
  const pageList = allList.slice((page - 1) * pageSize, page * pageSize)
  return { data: pageList, total: allList.length }
}
```

**设计原因**：司机列表数据量相对较小，一次全量拉取后前端分页，翻页时不发请求，提升体验。

### 搜索筛选

| 搜索字段 | 组件 | 说明 |
|---------|------|------|
| `radius` | `RadiusPicker` | 距离半径（默认 50km，最大 200km） |
| `vehicleList` | `CarSpecPicker` | 车长/车型多选 |

**筛选变化时**（`onSearch`/`onReset`）：清空 `driverListCacheKey`，触发后端重新请求。

### 跨页多选

司机列表支持跨页多选，最多可选 N 条（由字典配置 `callOutTimes` 决定，默认 4 条）：

```typescript
const onSelectionChange = (rows: Driver[]) => {
  // 保留其他页已选数据，合并当前页选中
  const keepOtherPages = selectedRows.value.filter(
    r => !currentPageKeySet.has(getDriverRowKey(r))
  )
  const mergedRows = [...keepOtherPages, ...rows]
  
  // 超过上限则截断
  if (mergedRows.length > callOutTimes.value) {
    next = mergedRows.slice(0, callOutTimes.value)
  }
  
  selectedRows.value = next
}
```

### 智能外呼（handleBatchSmartCall）

```typescript
const doSmartCallAjax = async (drivers: Driver[]) => {
  const driverInfos = drivers.map(d => ({
    plateNo: d.plateNoEncrypted,
    driverPhoneNumber: d.phoneEncrypted,
    driverId: d.driverId,
    carId: d.carId,
    ...
  }))
  
  await createOutbound({
    goodsId,
    goodsName,
    sendAddrDetail,
    receiveAddrDetail,
    goodsTotalWeight: `${weight}吨`,
    goodsTotalVolume: `${volume}立方`,
    loadTime: `${loadStime}至${loadEtime}`,
    unitPrice: `每${unitText}${price}元`,
    driverInfos,
    dataSource: '20',
  })
}
```

**外呼后处理**：
1. 清空已选司机（`selectedRows.value = []`）
2. 清空列表缓存（`driverListCacheKey.value = ''`）
3. 刷新列表（含最新外呼状态）

### 指派运单（handleGoodsSourceOpt）

```typescript
const handleGoodsSourceOpt = async (driver: Driver) => {
  // 1. 补全司机信息（getDriverCarInfo）
  const completeDriver = await getCompleteDriverInfo(driver)
  
  // 2. 调用指派接口
  await goodsSourceOpt({
    optType: GoodsSourceOptType.ASSIGN_DRIVER,
    goodsId: rowData.value.goodsId,
    goodsAssignSupplierInfo: [{
      designatedType: '10',
      driverId: completeDriver.driverId,
      driverName: completeDriver.driverName,
      vehiclePlateNo: completeDriver.plateNo,
      ...
    }],
  })
}
```

### 录音功能

- **录音回放**（`handleRecordPlayback`）：播放外呼录音文件（`row.recordUrl`）
- **录音文字**（`handleRecordText`）：获取并展示 AI 转写的对话文字（`getCallContentList`）

```typescript
// 录音文字对话格式
interface DialogueItem {
  dialogueRole: 'Customer' | 'VirtualAgent' | 'Agent'
  sentenceMessage: string
  startTime: string
  endTime?: string
}
```

---

## 脱敏处理

司机手机号和车牌号默认脱敏显示（`phoneEncrypted`、`plateNoEncrypted`），点击眼睛图标才解密：

```typescript
// DesensitizedField.vue
// 点击眼睛 → 调用 fetchRealData
const fetchRealData = async (row: Driver, fieldType: string) => {
  const cacheKey = row.driverId || getDriverRowKey(row)
  
  // 已缓存则直接返回
  if (realDataCache[cacheKey]) return realDataCache[cacheKey][fieldType]
  
  const { model } = await sensitiveDecrypt({
    phoneEncrypted: row.phoneEncrypted,
    plateNoEncrypted: row.plateNoEncrypted,
  })
  
  realDataCache[cacheKey] = {
    plateNo: model.plateNo,
    driverPhoneNumber: model.phone,
  }
  
  return realDataCache[cacheKey][fieldType]
}
```

**同一行的两个脱敏字段共享一次解密请求**（通过 `cacheKey` 缓存结果）。

---

## 渠道运力（channelCode）

调度支持多种渠道运力，`channelCode` 区分来源：

```typescript
enum CHANNEL_TYPE {
  PLATFORM = 1000,       // 平台运力
  PLATFORM_OTHER = 9999, // 平台其他
  // 其他值 = 第三方渠道运力（如中交渠道 1001、1002）
}
```

渠道运力差异处理：
- **渠道运力**（非平台）：传 `plateNoEncrypted + phoneEncrypted + dataFlag`，**不显示录音按钮**
- **平台运力**：传 `driverId + carId + ownCapacityId`，显示录音按钮

---

## 关键组件

### CarSpecPicker（车型/车长选择器）

```vue
<CarSpecPicker
  mode="dropdown"
  :model-value="vehicleList"
  button-text="选择车长/车型"
  @update:model-value="onChange"
/>
```

支持多选，返回：`[{ vehicleType, vehicleTypeName, vehicleLength }]`

### RadiusPicker（半径选择器）

```vue
<RadiusPicker
  :model-value="radius"
  :max="200"
  @update:model-value="onChange"
/>
```

单位：km（传给接口时 ×1000 转米）。

### DesensitizedField（脱敏字段）

```vue
<DesensitizedField
  :id="rowId"
  type="driverPhoneNumber"
  :value="row.driverPhoneNumber"
  :visible="visibleFields.driverPhoneNumber === rowId"
  :fetch-real-value="() => fetchRealData(row, 'driverPhoneNumber')"
  @toggle="handleFieldToggle"
/>
```

---

## API 接口（api/dispatch/）

```typescript
// 林索推荐（拉取司机列表）
lingSuoRecommend(params) → Promise<{ model: Driver[] }>

// 创建外呼任务
createOutbound(params) → Promise<void>

// 获取录音文字内容
getCallContentList(params) → Promise<{ model: DialogueItem[] }>

// 脱敏解密
sensitiveDecrypt({ phoneEncrypted, plateNoEncrypted }) → Promise<{ model: { phone, plateNo } }>

// 获取司机车辆完整信息
getDriverCarInfo(params) → Promise<{ model: Driver }>

// 货源操作（指派司机）
goodsSourceOpt({ optType, goodsId, goodsAssignSupplierInfo }) → Promise<void>
```

---

## 与其他子应用的交互

```
app-core（货源列表）
  → 点击「调度」按钮
  → 路由跳转：/app-dispatch/order/shipment-order?goodsId=xxx&...
  → app-dispatch 接收 query 参数展示司机列表
```

调度完成后（指派成功/外呼成功），`app-dispatch` 刷新自身列表，不需要通知 `app-core`。

---

## 相关文档

- [项目总览](./项目总览.md)
- [app-main 详解](./app-main详解.md)
- [app-core 详解](./app-core详解.md)
- [app-base 详解](./app-base详解.md)

---

**文档版本**: v1.0

**最后更新**: 2026年06月

**整理人**: 王新骏
