# logisticsweb 公共组件库文档

> 路径：`logisticsweb/src/components/`
> 本文档覆盖该目录下所有公共组件，按功能分类整理。

---

## 目录

- [一、通用基础组件](#一通用基础组件)
- [二、表单与选择器组件](#二表单与选择器组件)
- [三、业务功能组件](#三业务功能组件)
- [四、风控相关组件](#四风控相关组件)
- [五、上传与文件预览组件](#五上传与文件预览组件)
- [六、运输管理组件](#六运输管理组件)
- [七、结算与支付组件](#七结算与支付组件)
- [八、页面级布局组件](#八页面级布局组件)

---

## 一、通用基础组件

### ElImageX

**路径**：`ElImageX/`

基于 `el-image` 二次封装的图片展示组件，扩展了图片预览时的事件监听和自定义插槽能力。

**新增事件**

| 事件名 | 说明 | 返回值 |
|---|---|---|
| `prev` | 切换到上一张 | 当前 index |
| `next` | 切换到下一张 | 当前 index |
| `onSwitch` | 监听 index 切换 | 当前 index |

**插槽**

| 插槽名 | 说明 |
|---|---|
| `slot-html` | 自定义预览区域内容 |

**基础用法**

```vue
<el-image-x
  style="width: 100px; height: 100px"
  :src="url"
  :preview-src-list="srcList"
  @prev="prev"
  @next="next"
  @onSwitch="onSwitch"
>
  <template #slot-html>
    <div>自定义内容</div>
  </template>
</el-image-x>
```

---

### ElPaginationNew / ElPaginationNewUpdate

**路径**：`ElPaginationNew/` / `ElPaginationNewUpdate/`

在 `el-pagination` 基础上扩展了**首页、尾页、页码跳转**功能的分页组件。

**Props**

| 属性 | 类型 | 说明 |
|---|---|---|
| `currentPage` | Number | 当前页码 |
| `pageSize` | Number | 每页条数 |
| `total` | Number | 总条数 |
| `layout` | String | 分页布局，透传给 el-pagination |
| `pageSizes` | Array | 每页条数可选项 |

**Events**

| 事件 | 说明 |
|---|---|
| `current-change` | 页码变化时触发 |
| `size-change` | 每页条数变化时触发 |

---

### BasePopover

**路径**：`BasePopover/BasePopover.vue`

对 `el-popover` 的轻量封装，统一触发样式（文本 + 问号图标），支持自定义内容插槽。

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `text` | String | — | 触发区域显示的文字 |
| `content` | String | — | 气泡内容文字（纯文本） |
| `placement` | String | `top` | 弹出位置，透传给 el-popover |
| `trigger` | String | `hover` | 触发方式 |
| `disabled` | Boolean | `false` | 是否禁用 |
| `width` | String/Number | — | 气泡宽度 |
| `showText` | Boolean | — | 是否显示文字标签 |
| `showIcon` | Boolean | — | 是否显示图标 |

**插槽**

| 插槽名 | 说明 |
|---|---|
| 默认插槽 | 自定义气泡内容，优先级高于 `content` 属性 |

---

### CustomCollapse

**路径**：`CustomCollapse/CustomCollapse.vue`

对 `el-collapse` 的业务封装，统一折叠面板的标题样式，支持标题内嵌单选按钮组和说明气泡。

**Props**

| 属性 | 类型 | 说明 |
|---|---|---|
| `panels` | Array | 面板配置列表，见下方结构说明 |
| `card` | Boolean | 是否使用卡片样式 |

**panels 单项结构**

```js
{
  name: 'panel1',           // 唯一标识
  title: '面板标题',
  disabled: false,          // 是否禁用展开
  configurationList: [      // 可选，标题内嵌单选按钮组
    { btnName: '选项A' },
    { btnName: '选项B' }
  ],
  descriptionConfig: {      // 可选，标题右侧说明气泡
    text: '说明',
    content: '气泡内容'
  }
}
```

**Events**

| 事件 | 说明 |
|---|---|
| `radio-change` | 标题内单选按钮变化时触发，payload: `{ name, value }` |
| 其余事件 | 透传给 el-collapse |

---

### TableDrag

**路径**：`TableDrag/`

可拖拽排序列 + 自定义显隐列的表格增强组件，支持列配置持久化（LocalStorage）和筛选条件列设置。

**核心功能**

- 拖拽调整列顺序（基于 Sortable.js）
- 勾选控制列显隐
- 支持"列设置"和"筛选设置"双 Tab
- 列配置按 `groupClass` 隔离存储，跨页面保持

**Props（主要）**

| 属性 | 类型 | 说明 |
|---|---|---|
| `isDragTable` | Boolean | 是否开启自定义列功能 |
| `groupClass` | String | 列配置隔离 key，同页面唯一 |
| `customHeader` | Array | 可配置列的完整定义 |
| `hasSearchTab` | Boolean | 是否显示筛选设置 Tab |
| `searchColumns` | Array | 筛选条件列配置 |

**插槽**

| 插槽名 | 说明 |
|---|---|
| `bar` | 自定义列设置按钮左侧的功能区域 |

---

### PageHeader

**路径**：`PageHeader.vue`

通用页面顶部导航栏组件，用于展示页面标题和面包屑。

---

### FloatWindow

**路径**：`FloatWindow.vue`

全局悬浮窗组件，当前用于展示"澄清公告"图片入口，点击后在新标签页打开 PDF。关闭状态通过 `sessionStorage` 维持，刷新后重新显示。

**特性**

- 同一浏览器会话内关闭后不再显示
- 自动清理旧版 `localStorage` 遗留 key
- 图片/PDF 地址集中维护在 `data` 中，便于更新

---

### TimeOutCount

**路径**：`TimeOutCount.vue`

倒计时组件，用于操作超时提示场景。

---

## 二、表单与选择器组件

### AsyncSelect

**路径**：`AsyncSelect/index.vue`

带远程搜索 + 分页滚动加载的下拉选择器，完整透传 `el-select` 的 attrs 和 listeners。

**核心特性**

- 防抖搜索（默认 300ms）
- 滚动到底部自动加载下一页
- 请求序号机制，丢弃过期响应，避免结果错位
- 值清空时自动重置搜索状态
- `change` 事件额外返回选中的完整对象

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `value` | Any | `''` | v-model 绑定值 |
| `api` | Function | 必填 | 请求函数，接收 `{ filterModel, params, pageLength, currentPage }` |
| `filterModel` | Object | `{}` | 附加到 filterModel 的查询条件 |
| `params` | Object | `{}` | 直接追加到请求体的额外参数 |
| `pageLength` | Number | `20` | 每页条数 |
| `labelKey` | String | `'label'` | 选项展示文字对应字段名 |
| `valueKey` | String | `'value'` | 绑定值对应字段名 |
| `optionKey` | String | `''` | v-for key 字段名，不填时复用 valueKey |
| `placeholder` | String | `'请输入关键字搜索'` | 占位文字 |
| `clearable` | Boolean | `true` | 是否可清空 |
| `debounceTime` | Number | `300` | 搜索防抖时间（ms） |
| `searchOnFocus` | Boolean | `true` | 展开时自动请求第一页 |
| `resultFormatter` | Function | `null` | 自定义接口结果解析函数 |

**Events**

| 事件 | 说明 | 参数 |
|---|---|---|
| `input` | 值变化（v-model） | `value` |
| `change` | 选中变化 | `(value, selectedItem)` |
| `error` | 请求失败 | `error` |
| `visible-change` | 下拉框显隐 | `visible` |

**基础用法**

```vue
<async-select
  v-model="form.companyId"
  :api="fetchCompanyList"
  label-key="companyName"
  value-key="companyId"
  @change="handleCompanyChange"
/>
```

---

### AddressSelect

**路径**：`AddressSelect/index.vue`

自定义地址三级联动选择器，支持省市区级联面板和关键字模糊搜索两种交互方式。

> 注意：组件注释标明"代码先不要删除，超哥说留着"，属于保留逻辑，修改需确认。

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `value` | String/Array/Object | `''` | v-model 绑定值（省市区 code 数组） |
| `options` | Array | `[]` | 省市区树形数据 |
| `props` | Object | — | 级联字段映射配置 |
| `placeholder` | String | `''` | 输入框占位文字 |
| `clearable` | Boolean | `false` | 是否可清空 |
| `disabled` | Boolean | `false` | 是否禁用 |
| `special` | Boolean | `false` | `true` 时隐藏"市辖区" |
| `size` | String | `''` | 尺寸（medium/small/mini） |
| `popperClass` | String | `''` | 下拉面板自定义 class |

**Events**：`input`、`change`、`visible-change`

---

### CompanyRemoteSelect

**路径**：`CompanyRemoteSelect/index.vue`

公司远程搜索下拉选择器，封装分页加载和远程搜索，透传 `el-select` 所有 attrs。

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `value` | String | `''` | v-model 绑定值 |
| `optionProps` | Object | 见下 | 选项字段映射 |
| `loadFunc` | Function | 必填 | 分页请求函数 |

`optionProps` 默认值：

```js
{
  label: 'groupCompanyName',
  value: 'companyId',
  key: 'companyId',
  searchKey: 'companyName'
}
```

---

### CompanyTree

**路径**：`CompanyTree/index.vue`

业务归属组织树下拉选择器，`el-select` + `el-tree` 组合，支持懒加载子节点、数据缓存、搜索过滤。

数据来源：Vuex `app/getChildCompanyTreeList` action，缓存于 `state.app.childCompanyTree`（内存缓存，刷新清空）。

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `placeholder` | String | `'请选择业务归属'` | 占位文字 |
| `clearable` | Boolean | `false` | 是否可清空 |
| `filterable` | Boolean | `false` | 是否支持搜索过滤 |
| `expandFirst` | Boolean | `false` | 是否默认展开第一个节点 |

**Events**

| 事件 | 说明 | 参数 |
|---|---|---|
| `init` | 初始化完成，自动选中第一个节点后触发 | `{ companyId, companyName }` |
| `change` | 用户点击树节点时触发 | `{ companyId, companyName }` |
| `clear` | 点击清空按钮时触发（需 clearable=true） | — |

**方法**

| 方法 | 说明 |
|---|---|
| `reset({ companyId, companyName })` | 重置显示值，供父组件重置按钮调用 |

---

### OrganizationTree

**路径**：`OrganizationTree/index.vue`

基于 Vue2 + Element-UI 封装的下拉树形选择器（SelectTree），支持单选/多选、扁平数据自建树、节点过滤、清空等能力。

**核心特性**

- 单选模式也显示 checkbox，始终只保留一个勾选项
- 支持 v-model 数组格式（单选传 `['id']`，清空回传 `[]`）
- 支持扁平数据通过 `id` + `parentOrgId` 自动构建树结构
- 支持自定义字段映射（`propsMap`）

详见：`OrganizationTree/README.md`

---

### PageSearchForm

**路径**：`PageSearchForm/index.vue`

通用搜索表单组件，通过配置数组驱动渲染，支持多行多列布局。

**Props**

| 属性 | 类型 | 说明 |
|---|---|---|
| `searchFormList` | Array | 二维数组，第一维为行，第二维为列 |
| `limitDays` | Number | 日期限制范围（ms），默认 30 天 |

**searchFormList 单项配置**

```js
{
  key: 'status',
  value: '',
  title: '状态',
  type: 'el-select',       // 表单组件类型，select 时走内置下拉逻辑
  props: {},               // 传给表单组件的属性
  placeholder: '请搜索',
  searchConfig: {
    enumeration: 'enumeration/getDirctionaryIds',
    enumerationKey: 'xxx',
    label: 'name',
    value: 'enumCode',
    url: '',               // 自定义接口
    options: []            // 写死选项
  }
}
```

详见：`PageSearchForm/README.md`

---

### PageSearchSelect

**路径**：`PageSearchSelect/index.vue`

配合 `PageSearchForm` 使用的下拉搜索选择器，内部封装字典/接口数据加载逻辑。

---

### settlementPeriod

**路径**：`settlementPeriod/index.vue`

运费结算时间输入组件，封装输入框 + 说明气泡 + 表单校验（必填、正整数）的完整组合。

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `settlementPeriod` | String | `''` | 结算时间值（工作日数） |
| `labelWidth` | String | `'90px'` | 表单 label 宽度 |

---

### CommissionRate

**路径**：`CommissionRate/index.vue`

运费差价率说明组件，hover 时展示 Tooltip，根据业务场景展示不同内容。

**显示模式**（由 `displayConfig.mode` 控制）

| mode | 说明 |
|---|---|
| `detail` | 展示分项差价率列表（有轻卡/短倒场景） |
| `fixed` | 展示固定差价率 |
| `default` | 兜底默认展示 |

---

## 三、业务功能组件

### OperationRecord

**路径**：`OperationRecord/index.vue`

通用操作记录展示组件，展示某条业务数据的完整操作历史（操作动作、账号、操作人、时间、备注）。

**Props**

| 属性 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `serverUrl` | String | 是 | 操作记录请求地址 |
| `tableName` | String | 是 | 数据库表名 |
| `param` | Object | 否 | 扩展查询参数 |
| `hiddenTitle` | Boolean | 否 | 是否隐藏"操作记录"标题，默认 false |

内置 `ElPaginationNew` 分页，默认每页 10 条。

---

### sendForm

**路径**：`sendForm/index.vue`

发货信息表单组件，用于填写货物出发地/目的地简称等信息。支持远程搜索地址（含分页加载），当地址合规性标识为"异常"时展示"待完善"标签提示。

---

### DesignatedPartner

**路径**：`DesignatedPartner/index.vue`

指定服务伙伴弹窗组件，以弹窗形式配置一个货源伙伴和多个运力伙伴，选项来自后端接口，支持"不启用"选项。

---

### SettlementProcessingDialog（order）

**路径**：`SettlementProcessingDialog/order.vue`

订单结算处理弹窗中的运单列表子组件，展示关联运单明细（运单号、运输类型、城市、金额等），支持运单导出（使用 `ExportBtn` 组件）。

---

### ReasonManagement

**路径**：`ReasonManagement/index.vue`

审核原因管理弹窗，支持查看、添加、删除、上移/下移审核不通过（或同意）原因列表，用于审核流程中的原因项配置管理。

---

### PopupNav

**路径**：`PopupNav/index.vue`

引导提示弹层，展示"调整前/调整后"对比图片，支持多步骤翻页，图片从 OSS 加载。搭配子组件 `PopupTips` 展示文字说明和翻页按钮。

---

### InformationPopup

**路径**：`InformationPopup/index.vue`

客服入口组件，渲染页面右侧固定悬浮的客服按钮，点击后跳转企业微信客服 URL（URL 携带基于用户信息的加密签名）。服务电话号码从接口动态获取，兜底值为 `4001-566-566`。

---

### AdFeedbackTag

**路径**：`AdFeedbackTag/index.vue`

广告反馈标签组件，在广告内容旁展示"广告"标识，点击展开反馈选项面板，选择后通过 `trackAdEvent` 工具上报埋点。

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `visible` | Boolean | — | 反馈 popover 是否展开 |
| `variant` | String | — | 触发按钮样式变体 |
| `badgeOnly` | Boolean | `false` | `true` 时只显示"广告"徽标，不显示反馈箭头 |
| `popoverPlacement` | String | — | 反馈面板弹出方向 |
| `title` | String | — | 反馈面板标题 |
| `options` | Array | `['不感兴趣','重复收到多次','内容太差']` | 反馈选项列表 |

**Events**

| 事件 | 说明 |
|---|---|
| `toggle` | 点击触发区域 |
| `feedback` | 选择某个反馈选项，携带选项文字 |

---

### Reminder

**路径**：`Reminder/urge.vue` / `Reminder/operateDailog.vue`

催单相关组件。`urge.vue` 为催单触发入口，`operateDailog.vue` 为操作弹窗，用于对运单/订单发起催促操作。

---

### contract

**路径**：`contract/contract.vue`

合同组件，用于合同信息的展示与处理。

---

### protocolLink

**路径**：`protocolLink/index.vue`

协议链接组件，展示用户协议、隐私政策等可点击链接。

---

### meQrcode

**路径**：`meQrcode.vue`

个人二维码展示组件，用于个人中心等场景的二维码生成与展示。

---

### PushThirdPartyDialog

**路径**：`PushThirdPartyDialog.vue`

推送第三方系统弹窗组件，用于将业务数据推送至第三方系统的操作入口与确认弹窗。

---

## 四、风控相关组件

### Risk 目录

**路径**：`Risk/`

运单风控预警相关组件集合，涵盖风险展示、异常处理、申诉、证件审核等完整流程。

#### riskWarning

**路径**：`Risk/riskWarning.vue`

风控预警主组件，支持两种展示模式：

| `type` 值 | 展示方式 |
|---|---|
| `page` | 嵌入页面的折叠面板，显示高/中风险数量 |
| `dialog-single` | 弹窗形式展示单条风险预警 |

面板标题显示高风险数和中风险数，支持"异常处理"（`appealNeed=10` 时显示）和"查看申诉结果"操作。

**Props**

| 属性 | 类型 | 说明 |
|---|---|---|
| `waybillRiskTableData` | Array | 风控数据列表，含风险计数和明细 |
| `isView` | Boolean | 是否为查看模式（查看模式下始终展示风险数） |
| `type` | String | 展示模式：`page` / `dialog-single` |

#### riskWarningContent

**路径**：`Risk/riskWarningContent.vue`

风控预警内容子组件，渲染高中风险明细条目，供 `riskWarning` 内部调用。

#### riskWarningDialog

**路径**：`Risk/riskWarningDialog.vue`

风控预警弹窗容器，以对话框形式包裹风险内容展示。

#### unusualDialog

**路径**：`Risk/unusualDialog.vue`

异常处理弹窗，用于对风控预警发起异常申诉操作。

#### appealViewDialog / appealViewTable

**路径**：`Risk/appealViewDialog.vue` / `Risk/appealViewTable.vue`

申诉结果查看弹窗及其内部表格，展示历史申诉记录和处理结果。

#### certificationReview

**路径**：`Risk/certificationReview.vue`

证件审核组件，用于在风控流程中对司机/车辆证件进行审核操作。

#### ownerDeclarationDialog

**路径**：`Risk/ownerDeclarationDialog.vue`

货主声明弹窗，用于货主在风控环节进行声明确认。

#### imageViewDialog

**路径**：`Risk/imageViewDialog.vue`

风控流程中的图片查看弹窗，用于预览证件或凭证图片。

#### pdfViewDialog

**路径**：`Risk/pdfViewDialog.vue`

风控流程中的 PDF 查看弹窗，用于预览 PDF 类凭证文件。

#### upload / uploadView

**路径**：`Risk/upload.vue` / `Risk/uploadView.vue`

风控场景专用上传组件和上传内容查看组件，用于上传申诉材料或补充证件。

---

### 4plRisk 目录

**路径**：`4plRisk/`

4PL（第四方物流）场景下的风控预警组件集合，与 `Risk/` 目录结构类似，针对 4PL 业务逻辑单独封装。

#### risk

**路径**：`4plRisk/risk.vue`

4PL 场景风控预警主组件。

#### riskReCheckBtn

**路径**：`4plRisk/riskReCheckBtn.vue`

风控重新检测按钮组件，触发对当前运单重新执行风控校验。

#### riskWarning / riskWarningContent / riskWarningDialog

**路径**：`4plRisk/riskWarning.vue` / `4plRisk/riskWarningContent.vue` / `4plRisk/riskWarningDialog.vue`

4PL 场景下的风控预警展示组件，功能与 `Risk/` 对应组件一致，适配 4PL 业务差异。

#### riskRemarkReportDialog

**路径**：`4plRisk/riskRemarkReportDialog.vue`

风控备注上报弹窗，用于在 4PL 场景中补充风控处理备注。

---

## 五、上传与文件预览组件

### Upload

**路径**：`Upload/index.vue`

通用文件上传组件，基于 `el-upload` 封装，支持图片卡片、文字列表等多种展示模式，内置图片预览（使用 `ElImageX`）和 PDF 预览。

**Props（主要）**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `listType` | String | `'picture-card'` | 展示模式：`picture-card` / `text` |
| `limit` | Number | — | 最大上传数量 |
| `disabled` | Boolean | `false` | 是否禁用 |
| `accept` | String | — | 允许上传的文件类型 |
| `action` | String | — | 上传接口地址 |
| `fileList` | Array | `[]` | 已上传文件列表 |
| `addType` | String | — | 指定为 `'imageBig'` 时启用大图预览模式 |

**子组件说明**

| 文件 | 说明 |
|---|---|
| `buttonUpload.vue` | 按钮触发上传 |
| `newPaymentUpload.vue` | 支付凭证专用上传 |
| `uploadDrag.vue` | 拖拽上传 |
| `uploadType.vue` | 上传类型选择 |
| `typeFile.vue` | 文件类型展示 |
| `viewUpload.vue` | 仅查看模式（不可上传） |
| `imageViewDialog.vue` | 图片查看弹窗 |
| `pdfViewDialog.vue` | PDF 查看弹窗 |

---

### UploadLocalFile

**路径**：`UploadLocalFile/index.vue`

本地文件上传组件，用于上传本地文件（如 Excel、CSV 等），与通用 `Upload` 组件区分，专注于文件导入场景。

---

### Ocr

**路径**：`Ocr/index.vue`

OCR 识别上传组件，集成图片裁剪（`vue-cropper`）功能，支持上传图片后进行区域裁剪再提交 OCR 识别。

**核心功能**

- 图片上传 + 加载状态展示
- 内嵌 `vue-cropper` 裁剪框
- 禁用模式下显示"未上传"占位
- 上传失败时显示错误提示

---

### PdfPreview

**路径**：`PdfPreview/index.vue`

PDF 预览组件，通过 iframe 嵌入在线 PDF 渲染服务展示 PDF 文件。

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `link` | String | `''` | PDF 文件 URL |

渲染地址：`https://manage.10000da.cn/mp/pdf/pdf.html?url=<encoded_url>`，高度固定 600px。

---

### ImgDialog

**路径**：`ImgDialog/index.vue` / `ImgDialog/ImgPreview.vue`

图片预览弹窗组件，`index.vue` 为弹窗容器，`ImgPreview.vue` 为图片预览内容区，支持多张图片切换浏览。

---

### Iframe

**路径**：`Iframe/index.vue`

通用 iframe 嵌入组件，用于在页面内嵌入第三方页面或内部系统页面。

---

## 六、运输管理组件

**路径**：`TransportationManagement/`

运单/运输任务相关操作组件集合，覆盖运单详情、轨迹、回单、价格编辑等核心功能。

### WaybillDetail

**路径**：`TransportationManagement/WaybillDetail.vue`

运单详情展示组件，以折叠面板形式展示运单的出发地/目的地信息（简称、联系人、电话、省市区、详细地址）。

---

### HighwayCardMessage / HighwayWriteMessageDriver

**路径**：`TransportationManagement/HighwayCardMessage.vue` / `TransportationManagement/HighwayWriteMessageDriver.vue`

公路运输相关信息组件：
- `HighwayCardMessage`：展示公路卡信息
- `HighwayWriteMessageDriver`：司机填写公路运输信息

---

### RailwayTrackMessage / WriteTrackMessage

**路径**：`TransportationManagement/RailwayTrackMessage.vue` / `TransportationManagement/WriteTrackMessage.vue`

铁路运输轨迹相关组件：
- `RailwayTrackMessage`：铁路运输轨迹展示
- `WriteTrackMessage`：填写/更新运输轨迹信息

---

### ReceiptBackDialog / ReceiptSendDialog / ReceiptSignDialog

**路径**：`TransportationManagement/ReceiptBack(Send/Sign)Dialog.vue`

回单操作系列弹窗：
- `ReceiptBackDialog`：回单退回弹窗
- `ReceiptSendDialog`：回单发送弹窗
- `ReceiptSignDialog`：回单签收弹窗

---

### unloadCatch / unloadCatchList

**路径**：`TransportationManagement/unloadCatch.vue` / `TransportationManagement/unloadCatchList.vue`

卸货异常捕获组件，`unloadCatch` 为单条卸货异常处理，`unloadCatchList` 为列表展示。

---

### entrustedInformation

**路径**：`TransportationManagement/entrustedInformation.vue`

委托信息展示组件，展示运输任务的委托方相关信息。

---

### 子组件（component/ 目录）

| 组件 | 说明 |
|---|---|
| `AuditInfo.vue` | 审核信息展示 |
| `EditDetails.vue` | 运单详情编辑 |
| `EditEndAddress.vue` | 编辑目的地地址 |
| `EditEndAddressHistory.vue` | 目的地地址修改历史 |
| `editPrice.vue` | 编辑运费价格 |
| `editRemark.vue` | 编辑运单备注 |

---

### mixins/timeHint.js

运输管理相关时间提示 mixin，提供时间相关的提示逻辑复用。

---

### api/transport.js

运输管理模块专用接口封装，供上述组件调用。

---

## 七、结算与支付组件

### Payment

**路径**：`Payment/`

支付相关操作组件：

| 组件 | 说明 |
|---|---|
| `abortPay.vue` | 终止支付弹窗，确认终止未付司机金额，支持操作失败状态展示 |
| `abortPayRecord.vue` | 终止支付记录查看 |

`abortPay.vue` 内部通过 `submitState` 控制两种展示状态：`-1` 操作失败（展示原因），`1` 待确认（展示金额和确认操作）。

---

### paymentInfoDialog

**路径**：`paymentInfoDialog/paymentInfoDialog.vue`

支付信息详情弹窗，展示支付相关的详细信息。

---

### PayPasswordDialog

**路径**：`PayPasswordDialog/index.vue`

支付密码验证弹窗组件，配合 `mixins/payPasswordVerify.js` 使用，构成完整的支付密码验证系统。

**功能特性**

- 自动检查企业是否已设置支付密码
- 弹出密码输入框，验证成功后自动执行待操作
- 接口报错时自动阻止操作继续
- 忘记密码时跳转到密码修改页面
- 支持参数传递给后续业务操作

**使用方式**：在页面中引入 `payPasswordVerify` mixin，然后放置 `PayPasswordDialog` 组件即可。详见：`PayPasswordDialog/README.md`

---

### LoseAndRise

**路径**：`LoseAndRise/`

亏吨免赔配置组件集合，用于运单中亏吨/溢吨的免赔规则配置。

| 组件 | 说明 |
|---|---|
| `index.vue` | 亏吨免赔表单组件，包含启用开关、免赔类型、上下限配置 |
| `view.vue` | 亏吨免赔查看模式 |
| `viewText.vue` | 亏吨免赔纯文本展示 |
| `constant.js` | 相关枚举常量 |

`index.vue` Props（主要）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `disabled` | Boolean | 是否为只读模式 |
| `enable` | String | 启用状态枚举值 |
| `deductibleType` | String | 免赔类型 |

---

### CustomerSupplierComponents

**路径**：`CustomerSupplierComponents/`

客户/供应商相关消息详情组件集合，用于展示和编辑客户供应商的业务信息。

| 组件 | 说明 |
|---|---|
| `AuditMessageDetails.vue` | 审核消息详情 |
| `CostMessageDetails.vue` | 费用消息详情 |
| `EditMessageDetails.vue` | 编辑消息详情 |
| `OrderMessageDetails.vue` | 订单消息详情 |

---

### FeeDetail

**路径**：`FeeDetail/index.js`

费用明细相关逻辑模块（JS 入口），提供费用明细数据处理的工具方法，供结算相关页面调用。

---

## 八、页面级布局组件

### Elements

**路径**：`Elements/`

页面级基础布局元素：

| 组件 | 说明 |
|---|---|
| `FooterMini.vue` | 迷你底部操作栏，用于页面底部固定的操作按钮区域 |
| `memberCrumbs.vue` | 会员面包屑导航组件 |

---

### ExportBtn / ExportBtnNew

**路径**：`ExportBtn/index.vue` / `ExportBtn/indexNew.vue`

导出按钮组件，点击后发起文件下载请求，支持自定义按钮文案、请求地址、文件名和导出参数。

**Props**

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `url` | String | `''` | 导出接口地址 |
| `fileName` | String | `''` | 下载文件名 |
| `btnName` | String | `'导出'` | 按钮显示文字 |
| `tableData` | Array | `[]` | 导出数据（部分场景用） |
| `params` | Object | `{}` | 请求参数 |

---

### Printing

**路径**：`Printing/waybillPrinting.vue`

运单打印组件，以弹窗形式展示可打印的货物托运单，包含：
- 页头（Logo + 公司名 + 条形码）
- 运输类型、车牌号、货物信息等表格
- 支持批量选中运单打印（`selectItems` 遍历）
- 使用 `jsbarcode` 生成条形码，通过 `v-print` 指令触发打印

---

### PrimitivePage

**路径**：`PrimitivePage/`

基础页面模板组件集合，提供通用的页面骨架。

| 组件 | 说明 |
|---|---|
| `index.vue` | 页面容器模板 |
| `form.vue` | 表单页面模板 |
| `table.vue` | 列表页面模板 |
| `buttons.vue` | 操作按钮区域模板 |
| `enumeration.js` | 页面相关枚举常量 |

---

---

**文档版本**：v1.0
**最后更新**：2026年07月
**整理人**：王新骏
