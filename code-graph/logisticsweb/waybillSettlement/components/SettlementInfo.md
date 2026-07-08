# SettlementInfo.vue — 结算信息组件

## 概述

`SettlementInfo` 是运单结算模块的结算信息区块组件，负责展示和编辑运单的单价、数量、重量、运费、结算主体、银行卡、亏涨吨等核心结算字段，并在左侧内嵌装卸货磅单图片轮播。

通过 `readonly` 和 `showEditActions` 两个 prop 切换 edit/read 模式，所有数据通过 `formModel` 由父组件透传，组件本身不维护业务状态。

---

## 文件位置

```
src/views/userBase/waybillSettlement/components/SettlementInfo.vue
```

内部依赖：
- `WeighBillCarousel.vue` — 磅单图片轮播（同目录）
- `LoseAndRise/viewText.vue` — 亏涨吨情况展示

---

## Props

| prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `readonly` | Boolean | `false` | 只读模式：单价展示 `parsePrice` 格式化后的值，所有输入不可编辑 |
| `showEditActions` | Boolean | `false` | 是否展示操作按钮（修改重量、确认亏吨货损） |
| `formModel` | Object | `{}` | 结算表单数据，由父组件 `el-form` 的 model 透传，双向联动 |
| `detail` | Object | `{}` | 运单详情，用于判断结算类型、运输类型、监管上报状态等条件渲染 |
| `dictionary` | Object | `{ params:{}, items:{} }` | 枚举字典，`items[enumeration.khh]` 用于开户行下拉 |
| `bindCardInfo` | Object | `{ isBindCard: true, payeePhone: '' }` | 收款银行卡绑定状态；`isBindCard=false` 时结算主体字段显示未绑卡样式 |
| `newCompanyOffLineDatas` | Array | `[]` | 结算主体下拉列表（线下公司），支持滚动加载更多 |
| `splitMainInfo` | String | `''` | 委托转账主体名称，`splitFlag==='10'` 时展示 |
| `splitInfo` | String | `''` | 委托转账规则描述，`splitFlag==='10'` 时展示 |
| `btnLoading` | Boolean | `false` | 结算主体下拉加载状态 |
| `waybillId` | String | `''` | 运单 ID，组件内部自取装卸货磅单图片 |
| `showDownBtn` | Boolean | `false` | 控制磅单预览的下载按钮，对应父组件 `controlBtn.btnDownload` |

---

## Events

| 事件 | 触发时机 | 父组件处理 |
|------|---------|-----------|
| `input-change(tip: string)` | 单价/结算数量/结算重量输入框 `@change` | `updBusCostInput(tip)` — 触发运费重算 |
| `open-edit-load-weight` | 点击"修改重量"按钮 | `handleOpenEditLoadWeight()` — 打开 editLoadWeight 弹窗 |
| `open-confirm-loss` | 点击"确认亏吨货损"按钮 | `handleTodialog()` — 打开 loseDialog 弹窗 |
| `load-more` | 结算主体下拉触底 | `loadMore()` — 加载下一页结算主体 |

---

## 布局结构

```
SettlementInfo
├── 标题栏（"结算信息" + "展开/收起装卸照片" 按钮）
└── settlement-body（左图右表单）
    ├── 左侧：WeighBillCarousel（装货/卸货 Tab 切换）
    │         imgPanelVisible 控制展开/收起
    └── 右侧表单
        ├── 第一行：单价 / 结算数量 / 结算重量（非吨时显示）/ 运费 / 结算方式（按吨时显示）
        ├── 第二行：结算重量类型 / 装货净重+毛重 / 卸货净重+毛重+修改重量按钮 / 下单重量
        ├── 第三行：结算主体 / 收款开户行 / 收款银行卡号 / 亏涨吨情况+确认亏吨货损按钮
        ├── 委托转账行（splitFlag==='10' 时显示）：委托转账主体 / 委托转账规则
        └── 备注区：运单别名（可编辑） / 货源别名（只读） / 备注（可编辑）
```

---

## 关键字段的编辑/只读规则

| 字段 | readonly=false（edit） | readonly=true（read） |
|------|----------------------|---------------------|
| `unitRice` 单价 | `el-input` 可编辑，`@change` emit `input-change` | `el-input` disabled，显示 `parsePrice` 格式化值 |
| `settlementQuantity` 结算数量 | `el-input` 可编辑（按柜/车时 disabled）；`@change` emit | `el-input` disabled |
| `settlementWeight` 结算重量 | `el-input` 可编辑（仅非吨结算类型显示）；`@change` emit | `el-input` disabled |
| `transportCost` 运费 | `el-input` disabled（自动计算） | `el-input` disabled |
| `accountName` 结算主体 | 公路（1/2/3/6）用 disabled el-select；铁路水运（4/5）用 disabled el-input | `el-input` disabled |
| `openBank` 开户行 | `el-select` disabled | `el-select` disabled |
| `bankAccount` 银行卡号 | `el-input` disabled | `el-input` disabled |
| `loadWeight`/`loadRoughGoodsWeight` | `el-input` disabled（通过弹窗修改） | `el-input` disabled |
| `unloadWeight`/`unloadRoughGoodsWeight` | `el-input` disabled；`showEditActions=true` 时显示"修改重量"按钮 | `el-input` disabled；不显示按钮 |
| `waybillAlias` 运单别名 | `el-textarea` 可编辑，maxlength=100 | `el-textarea` disabled |
| `orderAlias` 货源别名 | `el-textarea` disabled（始终只读） | `el-textarea` disabled |
| `remark` 备注 | `el-textarea` 可编辑，maxlength=200 | `el-textarea` disabled |

---

## 结算主体显示逻辑

```
readonly=true  || transportType ∈ ['4','5']  → el-input disabled
transportType ∈ ['1','2','3','6']            → el-select disabled（v-el-select-loadmore 触底 emit load-more）
```

`bindCardInfo.isBindCard=false` 时，结算主体字段外层 el-form-item 添加 `.unBindCardInfo` 样式（CSS after 伪元素提示）。

---

## "修改重量"按钮显示条件

```
showEditActions=true
&& detail.regulatoryReportingStatus !== '4'   （未上报）
&& detail.busStatus !== '320'                  （未结算通过）
```

---

## "确认亏吨货损"按钮规则

仅 `showEditActions=true` 时显示，按钮状态：
- `cargoCompensationConfirmFlag === '1'`（待处理）：enabled，tooltip 提示"点击确认亏吨货损"
- `cargoCompensationConfirmFlag === '2'`（已确认）：enabled，可再次查看
- 其他：disabled

---

## 内部状态

| 数据 | 类型 | 说明 |
|------|------|------|
| `imgPanelVisible` | Boolean | 左侧磅单图片面板展开状态，默认 `true` |
| `activeTab` | String | 当前激活的图片 Tab：`'load'` 装货 / `'unload'` 卸货 |

---

## 用法示例

```html
<!-- edit 模式 -->
<SettlementInfo
  :readonly="false"
  :show-edit-actions="true"
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
  @input-change="updBusCostInput"
  @open-edit-load-weight="handleOpenEditLoadWeight"
  @open-confirm-loss="handleTodialog"
  @load-more="loadMore"
/>

<!-- read 模式 -->
<SettlementInfo
  :readonly="true"
  :show-edit-actions="false"
  :form-model="formModel"
  :detail="detail"
  :dictionary="dictionary"
  :bind-card-info="bindCardInfo"
  :waybill-id="$route.query.waybillId"
/>
```

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
