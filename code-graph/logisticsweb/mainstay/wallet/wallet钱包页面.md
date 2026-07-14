# 钱包模块（wallet）

## 概述

`wallet` 目录包含 3PL 和网络货运主体两个视角的钱包总览页，以及银行卡管理相关页面。核心功能是展示账户余额信息、支持充值/提现/还款/转账等资金操作入口，并管理银行卡绑定。

| 文件 | 功能 | 角色视角 |
|------|------|---------|
| `mine.vue` | 3PL 钱包总览页 | 3PL 查看关联主体的钱包概览及操作入口 |
| `mainstay.vue` | 网络货运主体钱包总览页 | 主体侧管理员查看所管理企业的账户信息 |
| `myBankCard.vue` | 我的银行卡列表页 | 3PL / 主体用户管理绑定的银行卡 |
| `myBankCardDetail.vue` | 银行卡绑定操作页 | 绑卡/换绑流程 |
| `config.js` | 银行卡配置常量 | 银行类型、操作类型定义 |

---

## 文件结构

```
logisticsweb/src/views/userBase/mainstay/wallet/
├── mine.vue                  # 3PL 钱包总览（主文件）
├── mainstay.vue              # 网络货运主体钱包总览
├── myBankCard.vue            # 我的银行卡列表
├── myBankCardDetail.vue      # 银行卡绑定/换绑操作页
├── config.js                 # 银行卡常量配置
└── components/
    ├── transferAccounts.vue  # 转账弹窗
    ├── accountInfoDialog.vue # 充值账号信息弹窗（C103.3 已注释）
    ├── agentForm.vue         # 代办人信息表单
    ├── bankForm.vue          # 银行表单
    ├── carousel.vue          # 广告轮播图
    └── verifyForm.vue        # 鉴权表单
```

---

## 核心逻辑

### 1. 3PL 钱包总览（mine.vue）

**职责**：3PL 视角的钱包主页，含现金账户概览、充值收款账号展示、授信账户信息、底部账户明细列表。

**页面区域划分**：

| 区域 | 内容 |
|------|------|
| 顶部主体选择栏 | 网络货运主体下拉选择 + 我的银行卡 + 支付密码入口 |
| 钱包总额卡片 | 可用金额、支付冻结金额、预充冻结金额 + 提现/转账操作按钮 |
| 充值收款账号卡片 | 账户名称、收款账号、开户行、联行号 + 复制按钮 |
| 充值注意事项 | 静态说明文字 |
| 广告轮播图 | `carousel.vue` 组件，仅独立应用展示 |
| 授信账户信息（非微应用） | 授信总额、可用余额、已用总额、冻结金额、服务费 |
| 底部账户列表（非微应用） | 授信账户 / 付款账号设置 tab 切换 |

**初始化流程**：

```
created / activated
  → init()
    ├── clearSourceInfoFromSession()  # 如来自货主PC钱包跳转，清理来源标记
    ├── checkMemberStatus()           # 查询绑卡/开户状态，控制银行卡入口展示
    ├── getUserInfo()                 # 刷新用户信息，同步 companyCode
    ├── getBankList()                 # 获取银行字典（枚举 ID: 20200309165959100001）
    ├── getSubjectList()              # 获取主体列表（含充值收款账号），默认选第一条
    │     └── setDefaultSubject()    # 选中第一条主体，触发 fetchData()
    └── getNewSubjectList()           # 获取企业主体列表（用于提现弹窗 newOptions）

fetchData(params)
  → getCacheAccountAmounts()         # 查询现金/授信账户概览
  →   paymentOrder=0 → infoCash     # 现金账户数据
  →   paymentOrder=1 → infoCredit   # 授信账户数据
  → getCurrentCashAccountRow()      # 单独查现金账户列表首行，供余额预警/提现入口使用
  → getTableList()                   # 刷新底部授信账户或付款账号列表
```

**充值收款账号信息来源**：
- `getSubjectList` 接口返回的 `options` 数组，每条含 `aaccountName / aaccountNumber / asubBranch / sbn` 字段
- 通过 `currentSubject` computed（`options.find(o => o.companyCode === subjectCode)`）取当前选中主体的收款账号信息
- 加载中状态（`subjectOptionsLoading` 或 `infoLoading`）时显示 `-`，避免展示旧值

**复制功能**：
- `copyAllInfo()`：复制完整四项收款信息（账户名称、收款账号、开户行、联行号）
- `copyNameAndNo()`：仅复制账户名称和收款账号
- 底层使用 `copyTextToClipboard()`（来自 `servicePartner/components/tools`）

**余额预警 / 提现入口迁移（C103.3）**：
- 原入口在底部现金账户列表行操作列，已隐藏
- 新入口位于顶部钱包总额卡片
- `handleAlertSetting()` / `handleWithdrawal()` 优先使用 `currentCashAccountRow`（现金账户列表首行），结构不满足时组装 `infoCash` 数据兜底

**微应用与独立应用差异**：
- `isInMicroApp()` 为 true 时：隐藏广告轮播图、授信账户区域、底部列表（`displayTabs` 返回空数组）
- `isInMicroApp()` 为 false 时：完整展示所有区域

**底部列表 Tab**（仅独立应用）：

| Tab | name | 数据接口 |
|-----|------|---------|
| 授信账户 | `'2'` | `getCreditAccountPageList` |
| 付款账号设置 | `'3'` | `getAccountOpeionsPageList` |
| 现金账户 | `'1'` | 已隐藏（C103.3 注释保留） |

**弹窗列表**：

| 弹窗组件 | 触发时机 | 说明 |
|---------|---------|------|
| `invest.vue` | 还款按钮 | dialogType='1' 还款；原充值入口已注释 |
| `withdrawal.vue` | 提现按钮 | 传入 cachedUsableAmount |
| `credit.vue` | 授信申请按钮 | |
| `changeMoney.vue` | 余额预警按钮 | |
| `cashBalanceAdjust.vue` | 现金余额调整 | isExternalMainAccount 时显示 |
| `transferAccounts.vue` | 转账按钮 | 可用余额为 0 时禁用并提示 |

---

### 2. 网络货运主体钱包总览（mainstay.vue）

**职责**：主体管理侧钱包页，可按企业名称筛选，展示现金账户和授信账户信息，支持主体侧新增授信打款、管理资金服务费率。

**与 mine.vue 的差异**：

| 维度 | mine.vue（3PL） | mainstay.vue（主体侧） |
|------|----------------|---------------------|
| 主体切换方式 | 下拉选择（最近交易优先） | 企业名称搜索框 |
| 充值收款账号展示 | 有（卡片形式） | 有（info-item 形式，字段不同） |
| 授信打款入口 | 无 | 有（newPaymentBtn 权限控制） |
| 资金服务费率管理 | 无 | 有（授信账户列表操作列） |
| 账户状态切换 | 无 | 有（授信账户列表 switch 操作） |
| 轮播图 | 有 | 无 |
| 微应用差异处理 | 有 | 无 |
| 底部 Tab | 授信账户 / 付款账号设置 | 现金账户 / 授信账户 |

**新增打款流程**（同 `credit.vue`）：
1. `showPaymentNow()` → `showPayment = true` → `cbs.vue` 弹窗
2. 用户选回单 → `saveSubjectRemitNow()` 字段映射 → `saveSubjectRemit()` 接口
3. 关闭弹窗并刷新页面

**资金服务费率管理**：
- 点击操作列"资金服务费率管理" → `showCreditRateNow(row)`
- 弹窗内展示修改记录（`queryCreditRateLogByid`）
- 输入校验：0–100 以内数字，至多 5 位小数（正则 `/^(([1-9]?\d(\.\d{1,5})?)|100|100.00)$/`）
- 调用 `changeAccountStatusAndRate` 接口保存

**账户状态切换**（授信账户 switch 列）：
- `setAccountStatus(row, paginationConfig, val)` → `changeAccountStatusAndRate({ id, accountStatus })`
- `accountStatus`：0 正常，1 冻结

---

### 3. 我的银行卡（myBankCard.vue）

**职责**：展示当前企业在各银行渠道的绑卡状态，支持绑卡/换绑操作。

**入口区分**：
- 3PL 侧跳转：`/userBase/mainstay/3pl/wallet/myBankCard?flag=mine`
- 主体侧跳转：`/userBase/mainstay/mainstay/wallet/myBankCard?flag=mainstay`

---

### 4. 配置常量（config.js）

**`OPEATE_TYPE`**：银行卡操作类型

| key | label | applyType |
|-----|-------|-----------|
| `bind` | 绑卡 | `'1'` |
| `change` | 换绑 | `'2'` |

**`BANK_TYPE`**：支持的银行渠道

| key | label | 步骤 | 协议链接 |
|-----|-------|------|---------|
| `SZDB` | 平安银行 | 申请 → 鉴权 → 完成 | orangebank.com.cn |
| `EVER` | 光大银行 | 申请 → 完成 | — |

---

## 依赖关系图

```
wallet/mine.vue
  ├── api/index.js
  │   ├── getCacheAccountAmounts         # 现金/授信账户概览（缓存版）
  │   ├── getCashAccountPageList         # 现金账户列表（仅取首行，供预警/提现使用）
  │   ├── getCreditAccountPageList       # 授信账户列表
  │   ├── getAccountOpeionsPageList      # 优先付款账户列表
  │   ├── setPaymentOrder                # 变更付款顺序
  │   ├── fetchSubjectListRecentTrade    # 主体列表（最近交易优先，含充值收款账号）
  │   └── getNewCompanyInfos             # 企业主体列表（提现弹窗用）
  ├── api/bankcard.js
  │   └── checkMemberStatus             # 查询绑卡/开户状态
  ├── api/userBase.userInfo.js
  │   └── getEnterprise                 # 获取企业信息（已无实际调用）
  ├── components/Dialog/
  │   ├── invest.vue                    # 还款弹窗
  │   ├── withdrawal.vue                # 提现弹窗
  │   ├── credit.vue                    # 授信申请弹窗
  │   ├── changeMoney.vue               # 余额预警设置弹窗
  │   └── cashBalanceAdjust.vue         # 现金余额调整弹窗
  ├── wallet/components/
  │   ├── transferAccounts.vue          # 转账弹窗
  │   ├── carousel.vue                  # 广告轮播图
  │   └── accountInfoDialog.vue         # 充值账号弹窗（C103.3 已注释）
  ├── views/userBase/modifypwd/PayPwdDialog.vue  # 支付密码弹窗
  ├── constants/systemJump.js           # 货主PC钱包跳转来源标记处理
  ├── utils/useMainProps.js             # isMicroApp() 判断
  └── views/userBase/servicePartner/components/tools  # copyTextToClipboard

wallet/mainstay.vue
  ├── api/mainstay.js
  │   ├── getSubjectAccountAmounts      # 主体现金/授信账户概览
  │   ├── getSubjectCashAccountPageList # 主体现金账户列表
  │   ├── getSubjectCreditAccountPageList # 主体授信账户列表
  │   ├── saveSubjectRemit              # 新增授信打款
  │   ├── changeAccountStatusAndRate    # 切换账户状态/修改费率
  │   └── queryCreditRateLogByid        # 查询费率修改记录
  ├── api/bankcard.js
  │   └── checkMemberStatus
  ├── components/Dialog/cbs/cbs.vue     # CBS银行回单弹窗
  ├── constants/systemJump.js
  └── utils/codeList.js                 # moneyFormat 金额格式化
```

---

## 数据流转

### mine.vue 账户数据加载

```
init()
  → getSubjectList() → options[]（含收款账号字段）
  → setDefaultSubject() → subjectCode = options[0].companyCode
  → fetchData({ subjectCode })
      → getCacheAccountAmounts()
          → paymentOrder=0 → infoCash（现金概览）
          → paymentOrder=1 → infoCredit（授信概览）
      → getCurrentCashAccountRow()  # 现金账户列表首行，供余额预警/提现使用
      → getTableList()               # 底部 Tab 对应的列表
```

### mainstay.vue 账户数据加载

```
mounted / activated
  → fetchData()
      → getSubjectAccountAmounts()
          → data.subjectCompany → subjectInfo（账户名/开户行/账号）
          → data.data[].paymentOrder=0 → infoCash
          → data.data[].paymentOrder=1 → infoCredit
      → getTableList()  # 根据 activeName 分别调现金/授信账户列表
```

---

## API 接口

### api/index.js（3PL 侧）

| 方法 | 接口路径 | 说明 |
|------|---------|------|
| `getCacheAccountAmounts` | POST `cache-wallet-query/account-amounts` | 账户总览（缓存版，mine.vue 使用） |
| `getCashAccountPageList` | POST `/accountAmount/getCashAccountPageList` | 现金账户分页列表 |
| `getCreditAccountPageList` | POST `/accountAmount/getCreditAccountPageList` | 授信账户分页列表 |
| `getAccountOpeionsPageList` | POST `/accountAmount/getAccountOpeionsPageList` | 优先付款账号列表 |
| `setPaymentOrder` | POST `/accountAmount/setPaymentOrder` | 变更付款账号顺序 |
| `fetchSubjectListRecentTrade` | POST `/company/getSubjectListBy3plOrderByRecentTrade` | 主体列表（最近交易优先） |
| `getNewCompanyInfos` | POST `platform/PlatformUmCompany/selectMainCompanyByCompanyId` | 企业主体列表 |

### api/mainstay.js（主体侧）

| 方法 | 接口路径 | 说明 |
|------|---------|------|
| `getSubjectAccountAmounts` | POST `/accountAmount/getSubjectAccountAmounts` | 主体账户总览 |
| `getSubjectCashAccountPageList` | POST `/accountAmount/getSubjectCashAccountPageList` | 主体现金账户列表 |
| `getSubjectCreditAccountPageList` | POST `/accountAmount/getSubjectCreditAccountPageList` | 主体授信账户列表 |
| `saveSubjectRemit` | POST `/subjectRemit/saveSubjectRemit` | 新增授信打款 |
| `changeAccountStatusAndRate` | POST `/accountAmount/updateStatusOrRate` | 切换账户状态/修改费率 |
| `queryCreditRateLogByid` | POST `/accountAmount/queryCreditRateLogByid` | 费率修改记录 |

---

## 状态管理

- `this.$store.state.app.controlBtn`：权限按钮控制
  - `myBankCard`：银行卡入口
  - `withDrawalBtn`：提现按钮
  - `repaymentBtn`：还款按钮
  - `freezeWaybillViewBtn`：冻结运单查看
  - `newPaymentBtn`：新增打款（mainstay.vue）
- `this.$store.state.app.userInfo`：当前用户信息（companyId、companyName 等）
- `this.$store.dispatch('app/getUserInfo')`：mine.vue 中异步刷新用户信息
- `this.$store.dispatch('enumeration/getDirctionaryIds', ['20200309165959100001'])`：银行字典枚举

---

## 注意事项

1. **C103.3 现金账户列表隐藏**：`mine.vue` 中底部现金账户 Tab（`name='1'`）、充值按钮、现金账户列表相关逻辑均已注释保留，`editableTabs` 只剩授信账户和付款账号设置两项。但余额预警、提现入口仍依赖现金账户列表的数据结构（通过 `getCurrentCashAccountRow` 后台静默查询）。

2. **`paymentOrder` 字段区分账户类型**：后端返回的账户列表用 `paymentOrder` 区分现金（`0`）和授信（`1`），需转字符串后比较（`t.paymentOrder + '' === '0'`）。

3. **充值收款账号展示差异**：
   - `mine.vue`：字段来自 `fetchSubjectListRecentTrade` 返回的主体列表（`aaccountName/aaccountNumber/asubBranch/sbn`）
   - `mainstay.vue`：字段来自 `getSubjectAccountAmounts` 返回的 `subjectCompany`（`aaccountName/aaccountBank/aaccountNumber`），`aaccountBank` 需用银行字典枚举转换为中文名

4. **轮播图生命周期控制**：`mine.vue` 在 `activated` 时恢复自动播放，`deactivated` 时停止，首次进入（`createdFlag=true`）直接播放，后续进入调 `initData()` 重新初始化。

5. **转账限制**：`handleTransferAccounts()` 检查 `infoCash.cachedUsableAmount` 是否有值，为 0 时直接提示不打开弹窗。

6. **跨系统跳转清理**：货主 PC 钱包可跳转至本页，通过 `isCurrentFromShipperWallet()` + `clearSourceInfoFromSession()` 在页面加载完成后清理来源标记。

---

## 相关文档

- [turnover 流水页面](./turnover流水页面.md)
- [mainstay 模块 API](../../src/views/userBase/mainstay/api/index.js)
- [银行卡配置常量](../../src/views/userBase/mainstay/wallet/config.js)

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
