# 司机对账模块 代码图谱

> 路径：`src/views/userBase/driverChecking/`
>
>

---

## 一、模块文件总览

```
driverChecking/
├── index.vue          # 列表页（搜索 + 表格 + 批量操作）
├── index.conf.js      # 列表页表单/弹窗配置（mixin）
├── index.format.js    # 列表页格式化工具（codeFormat / $action / $all 等，mixin）
├── add.vue            # 详情页（查看 / 核对 / 审核，复用同一组件）
├── add.conf.js        # 详情页表单/表格列配置（mixin）
├── add.format.js      # 详情页费用计算逻辑（$total / compuAdjustCost 等，mixin）
└── tableHeader.js     # 列表页可拖拽表头静态定义
```

---

## 二、路由入口与页面关系

```
/userBase/driverChecking              → index.vue   列表页
/userBase/driverChecking/read/:id     → add.vue     查看
/userBase/driverChecking/verify/:id   → add.vue     核对（可编辑确认金额）
/userBase/driverChecking/check/:id    → add.vue     审核（填写审核结果）
```

`add.vue` 通过 `this.$route.params.action` 区分三种只读/编辑模式，表单字段的 `disabled`、按钮的 `hide` 均依赖该值。

---



## 三、组件依赖关系



### index.vue

```
index.vue
├── mixins
│   ├── index.conf.js          # conf 数据（搜索表单、弹窗、规则）
│   ├── index.format.js        # codeFormat / $action / $startEnd / loadEnumeration
│   ├── unitTool.js            # exGetUnitName / exGetUnitPerFixName / BNumber 等
│   └── sourceDictionary.js    # loadSourceOption / sourceOption / sourceObj
├── components
│   ├── OrganizationTree       # 所属组织树选择器
│   ├── primitiveForm          # 通用表单（退回/批量不通过弹窗）
│   ├── primitiveButtons       # 通用按钮
│   ├── Upload                 # 对账确认凭证上传
│   ├── ExportBtn              # 导出按钮（indexNew）
│   └── table-drag             # 可拖拽自定义列表格
└── API
    ├── constManagement.driverChecking.getTable      # 列表查询（普通）
    ├── constManagement.driverChecking._getTable     # 列表查询（ES）
    ├── constManagement.driverChecking.affirm        # 单笔对账确认
    ├── constManagement.driverChecking.batchAffirm   # 批量对账确认
    ├── constManagement.driverChecking.giveBack      # 退回
    ├── constManagement.driverChecking.push          # 推送（线上）
    ├── constManagement.driverChecking.pushForFile   # 推送（线下生成文件）
    ├── constManagement.driverChecking.batchReviewNotPass  # 批量不通过
    ├── getParameterByParamName                      # 走马灯公告
    ├── getNewCompanyInfos                           # 网络货运主体列表
    ├── fetchOrganizationList                        # 所属组织列表
    ├── listAvailableEmployeeByCompanyId             # 经办人列表
    ├── queryValidValueList                          # 开关字典
    └── platformCmPlatformParameterPaging            # ES 开关参数
```



### add.vue

```
add.vue
├── mixins
│   ├── add.conf.js      # conf 数据（formList / table 列 / 按钮 / 审核结果表单）
│   ├── add.format.js    # $total / compuAdjustCost / codeFormat / fetchOilGasConfig
│   └── unitTool.js      # exGetgoodsQuantity / exValidatorWeight / parsePrice 等
├── components
│   ├── primitiveButtons           # 保存 / 提交审核 / 确定 / 返回
│   ├── primitiveTable             # 费用信息表格
│   └── PaymentMethodPanel         # 付款方式只读展示（预付/到付/回单付）
└── API
    ├── constManagement.driverChecking.getDetail   # 获取详情
    ├── constManagement.driverChecking.save        # 保存（核对暂存）
    ├── constManagement.driverChecking.verify      # 提交审核
    ├── constManagement.driverChecking.check       # 审核确定
    ├── constManagement.recordNew                  # 操作记录
    ├── getAttachmentsByWaybillId                  # 装/卸货附件图片
    ├── getPartPay                                 # 分次付款方式
    └── queryDispatchRatio                         # 油气返利配置
```

---



## 四、核心数据流



### 4.1 列表页数据流

```
activated()
  └── loadStatusOption()      # 加载枚举字典 + 来源下拉
  └── fetchOrganizationList() # 加载所属组织（写入 copyCarrierOrgIdList 作为默认值）
  └── getHandlerList()        # 加载经办人
  └── getAndApplyWorkspaceParams()  # 从工作台缓存恢复筛选条件
  └── getTable()              # 首次加载列表

getSearchTable()
  └── request.currentPage = 1
  └── getTable()

getTable(page?, isExport?)
  └── searchFormEl.validate()
  └── getUseNew('query_waybill_account')  # 判断是否走 ES 接口
  └── apiMethod(params)                   # getTable 或 _getTable
  └── reseponse.model = res.model         # 写入响应数据
  └── request.total = res.total
```



### 4.2 选中汇总计算（watch: selection）

```
selectedIds (v-model on el-checkbox-group)
  └── watch → 同步更新 selection[]（从 reseponse.model 中反查完整行对象）

selection[]
  └── watch →
        selectList.selectNum        = selection.length
        selectList.totalDriverAmount = Σ receivableTotalCost
        selectList.totalFreightDiffAmt = Σ serviceCharge（全流程B1不参与）
        selectList.totalAmount =
          fullProcessFlag===10 ? Σ payableFpFreight
                               : Σ waybillToConsignorPrice
        selectList.quantity[] = 按结算类型分组的装/卸货数量
```



### 4.3 详情页数据流

```
mounted()
  └── loadStatusOption()         # 开户行字典
  └── getPartPay()               # 分次付款（预付/回单付/到付）
  └── getDetail()
        └── constManagement.driverChecking.getDetail(request)
        └── 按 transportType + settlementType 动态替换 formList[9~11]
        └── 处理 bmsBusinessCostList（补空小计行、格式化金额）
        └── fetchOilGasConfig()  # 获取油气返利配置
        └── $total()             # 计算小计/运费差价/油气优惠/合计等特殊行
        └── getRecord()          # 操作记录（createDate >= 2024-02-01 才加载）
```



### 4.4 费用表格特殊行逻辑（$total 方法）

`add.format.js` 中的 `$total()` 在 `bmsBusinessCostList` 末尾追加若干**特殊行**，通过 `specialRowType` 字段标识：


| specialRowType | 显示内容     | 显示条件                           |
| -------------- | -------- | ------------------------------ |
| `subtotal`     | 小计       | 始终                             |
| `freightDiff`  | 运费差价     | 网货 + companyType !== 1         |
| `insurance`    | 货物保障服务金额 | 网货 + premiumBuyerType === '10' |
| `oilDiscount`  | 油气优惠     | 有有效油气数据 或 全流程                  |
| `total`        | 合计       | 网货 + companyType !== 1         |
| `fpDiff`       | 全流程运费差价  | fullProcessFlag === 10         |
| `shipperPay`   | 客户应付运费   | 全流程 + companyType === 2        |
| `carrierPay`   | 应付承运商运费  | 全流程 + companyType === 1        |


---



## 五、状态机（busStatus）

```
100  待核对   → 操作：核对(verify)
110  待审核   → 操作：审核(check) / 批量不通过
115  处理中   → 操作：查看(read) only
120  审核不通过 → 操作：查看 only
130  审核通过  → 操作：查看 / 退回(giveBack) / 推送(push)
200  待对账   → 操作：查看 / 退回 / 对账确认(affirm)
210  对账退回  → 操作：查看 only
220  对账通过  → 操作：查看 only
```

状态 → 可用操作的映射由 `index.format.js` 中的 `$action(row, action)` 函数控制，列表页操作列按钮均通过 `v-show="$route.meta.xxx && $action(scope.row, 'xxx')"` 双重守卫。

---



## 六、表头配置（tableHeader.js）

`tableHeader` 数组共 **58 列**，关键字段：


| prop                      | 说明      | 特殊处理                                              |
| ------------------------- | ------- | ------------------------------------------------- |
| `checkbox`                | 全选/单选   | 全流程冲突校验（handleSelectable / isFullProcessConflict） |
| `waybillId`               | 运单号     | 点击跳转运单详情；显示时效状态图标                                 |
| `waybillToConsignorPrice` | 托运人应付金额 | `v-mask-star` 脱敏；tooltip 提示以现金账户测算                |
| `serviceCharge`           | 运费差价    | `v-mask-star` 脱敏                                  |
| `advanceFee`              | 垫付金额    | tooltip 说明不开票                                     |
| `$startEnd`               | 出发地-目的地 | 由 `$startEnd()` 拼接                                |
| `$all`                    | 应付金额    | 由 `$all()` 格式化                                    |
| `handle`                  | 操作列     | 查看/核对/审核/退回/推送/对账确认                               |


列表使用 `table-drag` 组件，配合 `uuid='DRIVER_CHECKING'` 将列显示状态持久化到 localStorage。

---



## 七、关键业务规则

1. **ES 开关**：通过 `getUseNew()` 同时检查「司机对账es开关」平台参数（值为 `'10'` 全量开启）以及 `query_waybill_account` 字典白名单（按公司ID灰度），决定调用 `getTable` 还是 `_getTable`。
2. **全流程运单互斥选中**：`fullProcessFlag===10` 与非全流程运单不能混选，`handleSelectable` 禁用冲突行，`handleCheckAllChange` 全选前校验。
3. **时间范围限制**：派车日期/创建日期 picker 限制在 ±2 个月内，且不能选未来日期。
4. **运单号优先**：有运单号时，派车时间和创建时间字段置空，不作为过滤条件（`getTable` 内 `$nextTick` 处理）。
5. **导出列映射**：部分虚拟 prop（`$startEnd` → `sendAddrShorthand`，`$SettlementModes` → `settlementMethod`，`gx` → `containerName`，`$all` → `amountsPayable`）在 `exportBefore` 中转换为后端字段名。`showStar` 控制时将 `waybillToConsignorPrice`/`serviceCharge` 替换为加密版字段名。
6. **分次付款展示**：`add.vue` 调用 `getPartPay` 接口，将 type=10（预付）/20（回单付）/30（到付）的金额传入 `PaymentMethodPanel` 只读展示。
7. **油气优惠行**：全流程运单强制显示且金额为 0；非全流程仅当后端返回有效油气数据（oilAmount>0 且 oilDiscountAmount≠-1）时才追加该行。

