# app-base 子应用详解

## 概述

`app-base` 是**基础配置子应用**，负责运单管理、财务管理、系统设置、报表中心等核心业务功能。

**路由前缀**: `/app-base`  
**开发端口**: `5680`

---

## 目录结构

```
app-base/src/
├── api/                           # 接口定义
│   ├── waybill/                   # 运单相关
│   ├── settlement/                # 结算相关
│   ├── wallet/                    # 钱包相关
│   ├── invoice-freight/           # 发票相关
│   └── ...
├── components/                    # 全局组件
│   ├── waybill-descriptions/      # 运单描述组件
│   ├── vxeTable/                  # VXE 表格封装
│   │   └── editRender/            # 单元格编辑器
│   └── ...
├── composables/                   # 组合式 API
│   ├── useSearchFormCache.ts      # 搜索表单缓存
│   ├── useBenefitCombinedPay.ts   # 组合支付
│   ├── useAccountOpenVerify.ts    # 账户开通验证
│   └── ...
├── config/
│   ├── register-vxe-table.ts      # VXE Table 配置
│   └── ...
├── router/
│   ├── index.ts                   # 路由创建
│   └── routes.ts                  # 静态路由（仅回单管理）
├── stores/                        # 状态管理
│   ├── userInfo.ts                # 用户信息（从主应用同步）
│   └── ...
├── views/                         # 页面组件 ⭐
│   ├── waybill/                   # 运单管理
│   │   ├── waybill-list/          # 运单列表
│   │   ├── tripartite-waybill/    # 三方运单
│   │   ├── railway-waybill/       # 铁路运单
│   │   └── components/            # 运单组件
│   ├── ogmanagement/              # 财务管理
│   │   ├── freight/               # 运费管理
│   │   │   ├── waybill/           # 运单运费
│   │   │   └── apply/             # 运费申请
│   │   └── preliminary-review/    # 预审管理
│   ├── financial-management/      # 财务报表
│   │   ├── reconciliation/        # 对账管理
│   │   ├── daily-income/          # 日常收入
│   │   └── daily-expenses/        # 日常支出
│   ├── inTransit/                 # 在途管理
│   │   ├── in-transit-visibility/ # 在途可视化
│   │   ├── transport-pool/        # 运力池
│   │   └── fee-list/              # 在途费用
│   ├── reportCenter/              # 报表中心
│   │   ├── cockpit/               # 数据驾驶舱
│   │   ├── vehicle-operations-report/ # 车辆运营报表
│   │   └── organization-report/   # 组织报表
│   ├── receipt-management/        # 回单管理 ⭐
│   │   └── list/                  # 回单列表
│   ├── system-settings/           # 系统设置
│   │   ├── price-calculation/     # 价格计算
│   │   ├── geofence-configuration/ # 地理围栏
│   │   ├── complaint-consultation/ # 投诉咨询
│   │   └── blacklist/             # 黑名单
│   ├── account/                   # 账户管理
│   │   ├── wallet/                # 钱包
│   │   ├── funds/                 # 资金管理
│   │   ├── coupon/                # 优惠券
│   │   ├── mall/                  # 商城
│   │   ├── service-invoice/       # 服务发票
│   │   └── turnover/              # 流水
│   ├── vehicle-management/        # 车辆管理
│   │   ├── annual-inspection-review/ # 年检管理
│   │   ├── insurance-management/  # 保险管理
│   │   └── maintenance-repair/    # 维修保养
│   ├── transportPlan/             # 运输计划
│   ├── basic/                     # 基础配置
│   │   ├── address-management/    # 地址管理
│   │   ├── line-management/       # 线路管理
│   │   ├── product/               # 产品管理
│   │   ├── contracts-management/  # 合同管理
│   │   └── qrCode-management/     # 二维码管理
│   └── company/                   # 企业管理
│       ├── company-info/          # 企业信息
│       ├── organization/          # 组织架构
│       ├── employee/              # 员工管理
│       ├── role/                  # 角色权限
│       ├── personal-info/         # 个人信息
│       └── enterprise-records/    # 企业档案
├── App.vue
└── main.ts                        # 子应用入口
```

---

## 子应用启动流程

与 app-core 类似，使用 `vite-plugin-qiankun` 集成：

```typescript
renderWithQiankun({
  mount(props) {
    router = microRoutes(props)
    app = createApp(App)
    app.use(ElementPlus)       // Element Plus UI
    app.use(VxeUITable)         // VXE Table 表格库
    app.mount(mountContainer)
    userInfoStore.initUserInfo()
  },
  unmount() {
    app?.unmount()
    // 保留用户信息缓存
  }
})
```

**关键依赖**：
- **VXE Table**：用于运单列表、批量创建等复杂表格场景
- **Element Plus**：UI 组件库

---

## 核心业务

### 1. 运单管理（waybill/）

#### 运单列表（waybill-list/）

```
waybill-list/
├── index.vue                      # 运单列表页
├── detail.vue                     # 运单详情
├── create-waybill.vue             # 创建运单
├── batch-import.vue               # 批量导入
├── config/
│   ├── index.ts                   # 列表配置
│   └── dynamic-fee-columns.ts     # 动态费用列
├── types/
│   └── index.ts                   # 类型定义
└── components/
    └── batch-create/              # 批量创建 ⭐
        ├── utils/                 # 工具函数
        ├── types.ts               # 类型定义
        └── config/
            ├── columns.ts         # 表格列配置
            └── rules.ts           # 校验规则
```

**批量创建运单**（`batch-create`）：
- 使用 VXE Table 可编辑表格
- 支持单元格编辑、行内校验
- 自定义编辑器（`editRender/`）：
  - `address-detail-edit-render.vue`：地址详情编辑
  - `batch-settlement-fee-edit-render.vue`：结算费用编辑
  - `remote-search-render.vue`：远程搜索选择
  - `org-tree-select-edit-render.vue`：组织树选择

#### 运单组件（components/）

```
components/
├── createWaybillModel/            # 创建运单模型
│   ├── base-info.vue              # 基础信息
│   ├── capacity-info.vue          # 运力信息
│   ├── goods-info.vue             # 货物信息
│   ├── transport-info.vue         # 运输信息
│   ├── settlement-info.vue        # 结算信息
│   ├── send-form.vue              # 发货表单
│   └── footer-waybill.vue         # 底部操作栏
├── waybill-information/           # 运单信息展示
├── waybill-tracking/              # 运单追踪
├── payment-shipping-cost/         # 运费支付
├── modify-unit-price/             # 修改单价
├── modify-destination-address/    # 修改目的地
├── confirm-receipt/               # 确认收货
├── cancel-waybill/                # 取消运单
└── ...
```

#### 三方运单（tripartite-waybill/）

对接第三方物流平台的运单：
- 运单信息展示
- 轨迹追踪
- 发货单/送货单

#### 铁路运单（railway-waybill/）

铁路运输专用运单：
- 铁路运单列表
- 绑定/解绑铁路运单

### 2. 财务管理（ogmanagement/）

#### 运费管理（freight/）

```
freight/
├── waybill/                       # 运单运费
│   ├── index.vue                  # 运费列表
│   ├── detail.vue                 # 运费详情
│   └── components/
│       └── batch-invoice-dialog.vue # 批量开票
└── apply/                         # 运费申请
    ├── index.vue                  # 申请列表
    └── detail.vue                 # 申请详情
```

#### 预审管理（preliminary-review/）

```
preliminary-review/
├── index.vue                      # 预审列表
└── components/
    ├── risk-warning-content.vue   # 风险提示内容
    ├── warning-detail.vue         # 预警详情
    ├── deal-exception.vue         # 处理异常
    ├── deal-result.vue            # 处理结果
    ├── payment-dialog/            # 支付弹窗
    └── pay-shipping-fee.vue       # 支付运费
```

**功能**：
- 运单预审核
- 风险提示
- 异常处理
- 在线支付运费

### 3. 在途管理（inTransit/）

#### 在途可视化（in-transit-visibility/）

```
in-transit-visibility/
├── index.vue                      # 可视化页面
└── components/
    ├── visibility/
    │   ├── VisibilityCapacityCard.vue    # 运力卡片
    │   ├── VisibilityFilterDialog.vue    # 筛选弹窗
    │   └── InTransitEventCard.vue        # 在途事件卡片
    └── utils/
        ├── useVisibilityMap.ts            # 地图逻辑
        ├── useVisibilityList.ts           # 列表逻辑
        ├── useVisibilityEvents.ts         # 事件逻辑
        ├── in-transit-trajectory.ts       # 轨迹处理
        ├── vehicle-map-marker.ts          # 车辆标记
        └── amap-loader.ts                 # 高德地图加载
```

**功能**：
- 车辆位置实时地图展示
- 运单轨迹回放
- 在途事件提醒（超时、偏航、停留等）
- 运力状态监控

#### 运力池（transport-pool/）

类似在途可视化，专注于运力资源管理：
- 可用运力展示
- 司机/车辆位置
- 运力调度

#### 在途费用（fee-list/）

```
fee-list/
├── index.vue                      # 费用列表
├── detail.vue                     # 费用详情
└── components/
    ├── fee-information.vue        # 费用信息
    ├── fee-pay-dialog.vue         # 支付弹窗
    ├── fee-report-dialog.vue      # 上报弹窗
    ├── fee-cancel-pay-dialog.vue  # 取消支付
    ├── fee-log-tracking.vue       # 日志追踪
    └── payment-password.vue       # 支付密码
```

### 4. 报表中心（reportCenter/）

#### 数据驾驶舱（cockpit/）

```
cockpit/
├── index.vue                      # 驾驶舱页面
├── components/
│   ├── dashboard-header.vue       # 头部
│   ├── left-panel.vue             # 左侧面板
│   ├── center-panel.vue           # 中间面板
│   ├── right-panel.vue            # 右侧面板
│   ├── panel-section.vue          # 面板区块
│   └── rank-list.vue              # 排行榜
└── composables/
    ├── use-chart.ts               # 图表逻辑
    ├── use-marquee.ts             # 跑马灯
    ├── use-polling.ts             # 轮询
    └── use-adaptive-font.ts       # 自适应字体
```

**展示内容**：
- 实时运单数据
- 运费统计
- 车辆运营情况
- 司机排行榜

#### 车辆运营报表（vehicle-operations-report/）

车辆维度的运营数据统计。

#### 组织报表（organization-report/）

组织维度的运营数据统计。

### 5. 回单管理（receipt-management/）⭐

```
receipt-management/list/
├── index.vue                      # 回单列表
├── config/index.ts                # 列表配置
├── types/index.ts                 # 类型定义
├── utils/
│   └── parse-receipt-photos.ts    # 解析回单照片
└── components/
    ├── receipt-photo-viewer.vue   # 回单查看器
    ├── receipt-operate-dialog.vue # 回单操作弹窗
    └── operation-log-dialog.vue   # 操作日志弹窗
```

**功能**：
- 回单上传/查看
- 回单审核
- 操作日志

**注意**：这是 `routes.ts` 中唯一的静态路由（其他路由都由主应用动态下发）。

### 6. 账户管理（account/）

#### 钱包（wallet/）

```
wallet/
├── index.vue                      # 钱包首页
├── wallet-detail.vue              # 钱包明细
├── bankcard.vue                   # 银行卡管理
├── bail-detail.vue                # 保证金明细
└── components/
    ├── walletdetail.vue           # 钱包详情
    ├── editbank.vue               # 编辑银行卡
    └── upload.vue                 # 上传组件
```

#### 资金管理（funds/）

```
funds/
├── index.vue                      # 资金首页
└── components/
    ├── AccountOverview.vue        # 账户概览
    ├── AccountDetails.vue         # 账户明细
    ├── TransactionFlow.vue        # 交易流水
    └── ClaimFundsDialog.vue       # 领取资金弹窗
```

#### 优惠券（coupon/）

```
coupon/
├── index.vue                      # 优惠券列表
└── components/
    └── CouponCard.vue             # 优惠券卡片
```

#### 商城（mall/）

积分商城，兑换商品。

#### 服务发票（service-invoice/）

```
service-invoice/
├── index.vue                      # 发票列表
├── apply-detail.vue               # 申请详情
├── config/index.ts                # 配置
└── components/
    └── batch-invoice-dialog.vue   # 批量开票
```

### 7. 系统设置（system-settings/）

#### 价格计算（price-calculation/）

配置运费计算规则：
- 计价因素（距离、重量、体积等）
- 定价规则
- 条件配置

#### 地理围栏（geofence-configuration/）

配置地理围栏，用于在途监控。

#### 投诉咨询（complaint-consultation/）

```
complaint-consultation/
├── index.vue                      # 列表
├── config/index.ts                # 配置
└── components/
    ├── details/                   # 详情
    ├── view-reviews/              # 查看评论
    └── add-form/                  # 添加表单
```

#### 黑名单（blacklist/）

司机/车辆黑名单管理。

### 8. 企业管理（company/）

#### 企业信息（company-info/）

编辑企业基本信息、资质认证。

#### 组织架构（organization/）

部门、组织管理。

#### 员工管理（employee/）

```
employee/
├── index.vue                      # 员工管理首页
└── components/
    ├── employeeList/              # 员工列表
    └── invitationRecord/          # 邀请记录
```

#### 角色权限（role/）

```
role/
├── index.vue                      # 角色管理首页
├── config/index.ts                # 配置
└── components/
    ├── personnel/                 # 人员管理
    ├── personnel-table/           # 人员表格
    ├── new-employee-table/        # 新员工表格
    └── function-dialog/           # 功能弹窗
```

#### 个人信息（personal-info/）

```
personal-info/
├── index.vue                      # 个人信息页
├── authorization.vue              # 授权页
└── components/
    ├── my-company-list.vue        # 我的企业列表
    ├── binding-records.vue        # 绑定记录
    ├── change-phone-dialog.vue    # 更换手机号
    ├── transfer-admin-dialog.vue  # 转让管理员
    └── ...
```

---

## 核心特性

### 1. VXE Table 集成

app-base 大量使用 VXE Table 处理复杂表格：

```typescript
// config/register-vxe-table.ts
import VXETable from 'vxe-table'
import 'vxe-table/lib/style.css'

// 注册自定义编辑器
VXETable.renderer.add('address-detail-edit', {...})
VXETable.renderer.add('batch-settlement-fee-edit', {...})
```

### 2. 搜索表单缓存（useSearchFormCache）

```typescript
const { cachedForm, saveCache, clearCache } = useSearchFormCache('waybillList')

// 自动保存/恢复搜索条件
```

### 3. 组合支付（useBenefitCombinedPay）

支持钱包 + 优惠券组合支付：

```typescript
const { openPayDialog, paymentResult } = useBenefitCombinedPay({
  amount: 1000,
  businessType: 'WAYBILL',
})
```

---

## 相关文档

- [项目总览](./项目总览.md)
- [app-main 详解](./app-main详解.md)
- [app-core 详解](./app-core详解.md)
- [app-dispatch 详解](./app-dispatch详解.md)

---

**文档版本**: v1.0

**最后更新**: 2026年06月

**整理人**: 王新骏
