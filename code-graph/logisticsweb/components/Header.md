# Header 组件代码图谱

## 概述

Header 组件是 logisticsweb 项目的顶部导航栏组件，负责用户信息展示、企业切换、系统跳转、消息通知等核心功能。

**文件位置**: `src/layout/components/Header.vue`

**代码规模**: 604 行

## 核心功能

### 1. 用户信息展示

- 显示用户名或企业名称（根据 `psnAcctUserBaseId` 判断）
- 用户头像区域（首字母显示）
- 下拉面板展示企业树/账户列表

### 2. 企业切换（三个 Tab）

组件提供三种企业切换方式，对应三个 Tab：

#### Tab 1: 业务归属 (child)

- **数据来源**: Vuex `app/childCompanyList`
- **填充方式**: `getChildCompany` action 调用 `getOrganizationTreeList({ companyCode })`
- **显示条件**: 
  - 有数据
  - `organizationControl.btnEnter` 为真
- **切换方式**: 调用 `switchCompanyId` 接口，`openMenuType: '1'`

#### Tab 2: 组织机构 (agemcy)

- **数据来源**: Vuex `app/agemcyChildCompanyList`
- **填充方式**: `getAgencyTreeList` action 调用 `agencyTreeList({ companyCode })`
- **显示条件**:
  - 有数据
  - `organizationControl.btnAgemcy` 为真
- **切换方式**: 调用 `switchCompanyId` 接口，`openMenuType: '2'`

#### Tab 3: 负责企业 (account)

- **数据来源**: Vuex `app/accountList`
- **填充方式**: `getAccountList` action 调用 `findCompanyOperatorList({ accountType:'2' })`
- **显示条件**:
  - 有数据
  - token 长度 ≤ 50（长度 > 50 表示货主PC业务token，需隐藏）
- **展示形式**: 列表（非树形结构）
- **切换方式**: 调用 `switchAccount` 方法

### 3. 子功能组件

Header 组件集成了以下子组件：

- `<publishGoods />` - 发布货源
- `<toggleSystem />` - 系统切换
- `<homePageSet />` - 工作台设置（仅在工作台页面显示）
- `<download />` - 下载
- `<msgNotice />` - 消息通知
- `<tabsView />` - 标签页视图

## 核心逻辑流程

### 切换业务归属/组织机构

```javascript
changeChildCompany(companyId) {
  // 1. 调用 switchCompanyId 接口
  switchCompanyId({
    companyId: companyId,
    openMenuType: this.activeName === 'child' ? '1' : '2'
  })
  // 2. 获取新的 token
  // 3. 设置 token 和 companyId 到 cookie
  // 4. 跳转到首页
  location.href = '/yw/'
}
```

**关键点**:
- `openMenuType` 决定后端返回的菜单权限范围
- 切换后直接跳转首页，触发全局重新初始化

### 切换负责企业账户

```javascript
async switchAccount(accountData) {
  // 1. 用 loginId 换取业务系统 token (targetSysType: '1' 即网货)
  const businessTokenRes = await getTokenByLoginId({
    targetSysType: '1',
    loginId: accountData.loginId
  })
  
  // 2. 若为撮合账户 (platformCode === '40')，需转换 token
  if (accountData.platformCode === '40') {
    const finalTokenRes = await matchOperatorAndChangeToken({
      targetSysType: '1',
      token: businessTokenRes.model.targetToken
    })
    newToken = finalTokenRes.model.token || businessTokenRes.model.targetToken
  }
  
  // 3. 先同步 tokenCache 再 setToken（避免拦截器误判多设备登录）
  syncTokenCache(newToken)
  setToken(newToken)
  
  // 4. 撮合账户做协议/密码/授权书校验
  if (accountData.platformCode === '40') {
    const { redirectToHome } = await checkShipperPcAuthStatus(userRes)
    // 根据校验结果跳转首页或授权页
  } else {
    // 非撮合账户直接跳首页
    location.replace('/yw/')
  }
}
```

**关键点**:
- 撮合账户需要两次 token 转换
- `syncTokenCache` 必须在 `setToken` 之前调用，防止请求拦截器触发 `doLogOut`
- 撮合账户需要做额外的协议/授权校验

### Tab 显隐和数据更新

```javascript
getCompanyTree(childCompany, agemcyChildCompany, organizationControl) {
  // 1. 根据数据源和权限配置计算每个 tab 的显隐状态
  this.tabs.forEach(item => {
    if (item.name === 'child') {
      item.show = !!(childCompany?.length && btnEnter)
      item.data = childCompany
    }
    if (item.name === 'agemcy') {
      item.show = !!(agemcyChildCompany?.length && btnAgemcy)
      item.data = agemcyChildCompany
    }
    if (item.name === 'account') {
      const isShipperToken = token && token.length > 50
      item.show = !!(this.accountList?.length) && !isShipperToken
      item.data = this.accountList || []
    }
  })
  
  // 2. 至少有一个 tab 有数据才显示整个下拉面板
  this.hasData = this.tabs.some(item => item.show && item.data.length)
  
  // 3. 默认激活第一个可见 tab
  const findShowTabs = this.tabs.filter(item => item.show) || []
  this.activeName = findShowTabs[0]?.name || ''
  this.treeList = findShowTabs[0]?.data || []
}
```

**触发时机**:
- `childCompany` 数据变化（watch）
- `agemcyChildCompany` 数据变化（watch）
- `organizationControl` 变化（watch）
- `accountList` 数据变化（watch）

### 用户退出登录

```javascript
doLogOut() {
  // 1. 使用 sendBeacon 发送退出请求（保证页面卸载时请求能发出）
  navigator.sendBeacon('/PlatformUmUserbaseinfo/webLogout')
  
  // 2. 通知父窗口需要重新登录
  notifyNeedRelogin('User logout')
  
  // 3. 调用中台登出接口
  midPlatformLoginOut()
  
  // 4. 清除本地状态
  this.$store.commit('app/CLEAR_ALL')
  this.$store.dispatch('app/doLogOut')
  
  // 5. 根据来源跳转对应登录页
  const loginUrl = getLoginUrlWithSource()
  window.location.replace(loginUrl)
}
```

**关键点**:
- `sendBeacon` 用于在页面卸载时保证请求能发送成功
- 支持从外部系统（如货主PC钱包）跳转进来的场景，退出后回到来源登录页

## 依赖关系

### API 接口

```javascript
import { midPlatformLoginOut } from '@/api/midPlatform'
import { switchCompanyId, getUserInfo, matchOperatorAndChangeToken } from '@/api/login'
import { getTokenByLoginId } from '@/api/midPlatform'
```

- `midPlatformLoginOut()` - 中台登出
- `switchCompanyId({ companyId, openMenuType })` - 切换子公司
- `getUserInfo()` - 获取用户信息
- `matchOperatorAndChangeToken({ targetSysType, token })` - 撮合 token 转换
- `getTokenByLoginId({ targetSysType, loginId })` - 通过 loginId 换取 token

### Vuex 依赖

**State**:
- `app/userInfo` - 当前用户信息
- `app/childCompanyList` - 业务归属树
- `app/agemcyChildCompanyList` - 组织机构树
- `app/organizationControl` - 组织权限控制
- `app/accountList` - 负责企业列表
- `app/hash` - 路由 hash

**Actions**:
- `app/getChildCompany` - 获取业务归属树
- `app/getAgencyTreeList` - 获取组织机构树
- `app/getAccountList` - 获取负责企业列表
- `app/doLogOut` - 退出登录
- `app/CLEAR_ALL` - 清除所有状态

### 工具函数

```javascript
import { getToken, setToken, setSwitchCompanyId } from '@/utils/auth'
import { syncTokenCache } from '@/utils/request'
import { checkShipperPcAuthStatus } from '@/utils/systemJump'
import { isFromShipperWallet, clearSourceInfoFromSession, getSourceInfoFromSession } from '@/constants/systemJump'
import { getLoginUrlWithSource } from '@/constants/systemJump'
import { notifyNeedRelogin } from '@/utils/iframeMessenger'
```

### 子组件

```javascript
import toggleSystem from './toggleSystem.vue'
import download from './download.vue'
import homePageSet from './homePageSet.vue'
import msgNotice from './msgNotice.vue'
import tabsView from './TabsView/tabsView.vue'
import publishGoods from './publishGoods.vue'
```

### SSE 推送

```javascript
import SSESdk from '@/utils/SSEClient'
```

用于接收服务端推送的密码过期通知。

## 数据流转

### 初始化流程

```
created()
  ├─ loginIn() 检查密码过期提示
  └─ getAccountList() 获取负责企业列表
       └─ init() 重新计算 tab 显隐
```

### Tab 数据更新流程

```
Vuex 数据变化
  ├─ watch: childCompany
  ├─ watch: agemcyChildCompany
  ├─ watch: organizationControl
  └─ watch: accountList
       └─ init()
            └─ getCompanyTree() 计算 tab 显隐和数据
                 ├─ 计算每个 tab 的 show 状态
                 ├─ 缓存每个 tab 的 data
                 ├─ 确定 hasData（是否显示下拉面板）
                 └─ 设置默认激活的 tab
```

### 企业切换流程

```
点击"进入"按钮
  └─ handleChildCompanyEnter(value)
       ├─ 如果是 account tab
       │    └─ switchAccount(value) 
       │         ├─ getTokenByLoginId() 获取业务token
       │         ├─ matchOperatorAndChangeToken() 转换token（撮合账户）
       │         ├─ syncTokenCache() + setToken() 更新token
       │         └─ 跳转首页或授权页
       │
       └─ 如果是 child/agemcy tab
            └─ changeChildCompany(id)
                 ├─ switchCompanyId() 获取新token
                 ├─ setToken() + setSwitchCompanyId()
                 └─ location.href = '/yw/'
```

## 特殊逻辑处理

### 1. Token 长度判断

```javascript
const token = getToken()
const isShipperToken = token && token.length > 50
```

Token 长度 > 50 表示当前是货主PC业务token，此时需要：
- 隐藏"负责企业" tab
- 部分业务逻辑走货主PC专用流程

### 2. 撮合账户特殊处理

撮合平台账户（`platformCode === '40'`）需要：
1. Token 二次转换（撮合 → 网货）
2. 协议/密码/授权书校验
3. 根据校验结果跳转不同页面

### 3. 外部系统跳转来源处理

通过 `getSourceInfoFromSession()` 获取来源信息：
- `fromSystemType` - 来源系统类型
- `pageType` - 页面类型

特殊来源（如货主PC钱包）在切换企业或退出时需要：
- 清除来源信息 `clearSourceInfoFromSession()`
- 跳转到特定页面或带参数跳转

### 4. displayName 显示逻辑

```javascript
displayName() {
  // 有 psnAcctUserBaseId 表示个体户账户，显示企业名称
  if (this.user.psnAcctUserBaseId) {
    return this.user.companyName || this.user.username || ''
  }
  // 否则显示用户名
  return this.user.username || ''
}
```

### 5. el-tabs 下划线宽度修复

```javascript
afterEnter() {
  // el-popover 动画结束后重置 activeName
  // 触发 el-tabs 重新计算下划线宽度
  // 修复初次展开时下划线宽度为 0 的问题
  const _activeName = this.activeName
  this.activeName = ''
  this.$nextTick(() => {
    this.activeName = _activeName
  })
}
```

### 6. 密码过期提醒

两种触发方式：
1. **登录页带来**: 从 `localStorage.getItem('passwordMsg')` 读取
2. **SSE推送**: 通过 `createSSE()` 订阅服务端消息

## 注意事项

### 1. Token 操作顺序

切换账户时必须先调用 `syncTokenCache(newToken)` 再调用 `setToken(newToken)`，否则请求拦截器可能误判为多设备登录触发 `doLogOut`。

```javascript
// 正确顺序
syncTokenCache(newToken)
setToken(newToken)
```

### 2. 下拉面板滚动

下拉面板最大高度为 `60vh`，超出时可滚动。样式类名：`.head-tree-scroll`

### 3. 埋点统计

组件中包含多处埋点：
- 切换企业按钮点击 `wlyd_3pl_header_enterBtn_click`
- 修改密码按钮点击 `wlyd_3pl_header_editPassword_click`

### 4. 工作台判断

```javascript
isWorkspace() {
  return this.$route?.path?.indexOf('userBase/workspace') > -1
}
```

只在工作台页面显示 `<homePageSet />` 组件。

### 5. 未使用的代码

`findLastPage(tree)` 方法当前未被调用，疑似遗留代码。

## 相关文档

- [系统跳转工具函数](./systemJump工具.md)
- [token 管理工具](./auth工具.md)
- [Vuex app 模块](./Vuex-app模块.md)

---

**文档版本**: v1.0

**最后更新**: 2026年06月

**整理人**: 王新骏
