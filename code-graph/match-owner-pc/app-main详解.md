# app-main 主应用详解

## 概述

`app-main` 是微前端主应用（qiankun 宿主），负责登录认证、布局框架、路由编排、用户状态管理、子应用注册与生命周期管理。

---

## 目录结构

```
app-main/src/
├── api/                    # 接口定义（user、system、marketing 等）
├── assets/                 # 样式、SVG、图片
├── components/             # 全局组件（wl-upload、wl-segmented 等）
├── composables/            # 组合式 API（useProtocol、useWhitelistCheck 等）
├── config/
│   ├── micro-app-config.ts # 微前端子应用配置 ⭐
│   └── project-config.ts   # 项目配置
├── directives/             # 全局指令（auth、copy 等）
├── layout/                 # 布局系统 ⭐
│   ├── index.vue           # 主布局
│   ├── frame.vue           # iframe 框架
│   └── components/         # 导航栏、侧边栏、标签页等
├── micro/
│   └── actions.ts          # qiankun global-state actions
├── router/                 # 路由 ⭐
│   ├── index.ts            # 路由实例 + 导航守卫
│   ├── utils.ts            # 路由工具（initRouter、权限方法）
│   ├── route-history-manager.ts
│   └── modules/            # 静态路由模块
├── store/                  # 状态管理 ⭐
│   ├── user/               # 用户状态（核心）
│   ├── organization/       # 组织状态
│   └── modules/            # permission、multi-tags、app 等
├── utils/
│   ├── auth.ts             # Token 工具
│   ├── router-state-manager.ts  # 路由状态管理
│   └── track.ts / sentry.ts
├── views/
│   ├── login/              # 登录页
│   ├── welcome/            # 首页
│   ├── error/              # 错误页（403、404、500）
│   └── market/             # 营销弹窗（优惠券、活动、授权）
├── App.vue
├── main.ts                 # 应用入口 ⭐
└── micro-apps.ts           # 子应用注册 ⭐
```

---

## 启动流程（main.ts）

```
asyncInitDeviceId()
  → initTrack()                      # 埋点初始化
  → getPlatformConfig()              # 拉取平台配置
    → URL 有 ticket？
      是 → handleAuthorizationLogin()  # SSO 授权登录
           history.replaceState 清除 ticket
      否 → 继续
    → getToken() 有值？
      是 → fetchUserInfo()            # 拉取用户信息
           switchToCompanyAccount()   # 个人账号自动切企业
           isMtUser → fetchSystemList()
           systemReadyRef = true
      否 → 跳过（进入登录页）
    → app.mount('#app')
```

**关键注意**：ticket 处理后必须用 `history.replaceState` 清除参数，否则 qiankun 跨域场景刷新时会触发无限循环。

---

## 用户状态（store/user/index.ts）

### 核心状态

| 状态 | 类型 | 说明 |
|------|------|------|
| `userInfoModel` | `UserInfoModel` | 完整用户信息 |
| `accountType` | `computed` | 账号类型（10=个人，20=企业员工） |
| `isMtUser` | `computed` | 是否撮合企业用户 |
| `isBusinessLicenseNavBlocked` | `ref<boolean>` | 营业资质过期拦截标志 |
| `isStateOwnedEnterprise` | `ref<boolean>` | 是否国企/央企 |

### 关键方法

**doLogin**：登录后处理

```
setToken → fetchUserInfo → switchToCompanyAccount
  → 记录埋点 → fetchSystemList → systemReadyRef=true
```

**switchToCompanyAccount**：账号切换

```
getMyCompanyList()
  → 查找 loginCompany / defaultCompany
  → switchCompany({ targetSysType, loginId, token })
  → handleSwitchSuccess(targetToken)
    → setToken + fetchUserInfo
    → 网货企业？检查协议/授权 → 可能跳授权中间页
    → clearAllCachePage + initRouter
```

⚠️ 切换后**不能** `window.location.href` 刷新，只能 `clearAllCachePage + initRouter`。

**checkBusinessLicenseExpired**：营业资质检查

```
queryLatestStatus({ companyId })
  → qualificationExpireControlSwitch==='20' 才生效
  → status==='6' 过期 → isBusinessLicenseNavBlocked=true
  → expireSubmitFlag==='1' && status==='1'/'2' 待审 → isBusinessLicenseNavBlocked=true
```

---

## 路由系统（router/）

### 动态路由初始化（router/utils.ts → initRouter）

```
getUserMenu({ companyId })            # 后端拉取菜单
  → transformRouters(model)           # 转换格式
  → handleAsyncRoutes(routes)
    → addAsyncRoutes()                # 匹配组件路径
    → router.addRoute('Home', route)  # 挂载到 Home 子路由
    → permissionStore.handleWholeMenus()
    → addPathMatch()                  # 添加 404 通配
  → routerStateManager.completeLoading()  # 通知微前端路由分配完成
```

### 导航守卫（router/index.ts → beforeEach）

1. keepAlive 处理
2. 营业资质过期拦截（`isBusinessLicenseNavBlocked`）
3. 角色权限拦截（`roles`）
4. 动态路由未初始化时调用 `initRouter()`
5. 网络错误 vs 鉴权错误区分处理

### 路由状态管理（router-state-manager.ts）

```typescript
// 防止微前端场景下重复初始化
routerStateManager.isRouterLoaded()   // 是否已加载
routerStateManager.isRouterLoading()  // 是否加载中
routerStateManager.getMicroAppRoutes() // 获取各子应用分配的路由
```

路由加载完成后，按 `activeRule` 前缀把路由分发给对应子应用，子应用挂载时通过 props `routes` getter 获取。

---

## 微前端注册（micro-apps.ts）

向子应用注入的 props：

| prop | 说明 |
|------|------|
| `routerBase` | 子应用路由基础路径 |
| `mainRouter` | 主应用 Router 实例 |
| `getToken` / `getCookieToken` | Token 获取方法 |
| `userStore` | 用户 Pinia store |
| `organizationStore` | 组织 Pinia store |
| `routes` | 动态路由（getter，每次挂载读取最新） |
| `actions.refreshCompanyList` | 刷新企业列表 |
| `actions.switchByUserId` | 个人账号切换 |
| `actions.hasMenuPermission` | 菜单权限判断 |

---

## 布局系统（layout/）

```
layout/index.vue
├── NavVertical          # 侧边栏（vertical/mix 模式）
├── LayHeader
│   ├── LayNavbar        # 顶部导航栏（用户信息、通知、企业切换）
│   └── NavHorizontal    # 水平导航
├── LayContent           # 内容区
│   ├── <router-view>    # 主应用路由
│   └── #subappContainer # 子应用挂载点
└── 营销弹窗（CouponPopup、MarketPopup、AuthPopup、BusinessLicenseExpiredPopup）
```

---

## 相关文档

- [项目总览](./项目总览.md)
- [app-core 详解](./app-core详解.md)
- [app-base 详解](./app-base详解.md)
- [app-dispatch 详解](./app-dispatch详解.md)

---

**文档版本**: v1.0

**最后更新**: 2026年06月

**整理人**: 王新骏
