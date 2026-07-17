# logisticsweb 项目代码图谱

## 概述

logisticsweb 是**万联易达 3PL 物流平台**前端项目（项目名 `app-3pl`），面向物流企业和货主提供运输管理、运单管理、结算管理、合同管理等全链路物流业务功能。基于 Vue 2 + Element UI，支持**独立运行**和 **qiankun 微前端子应用**两种模式。

- **技术栈**: Vue 2.6 + Vuex 3 + Vue Router 3 + Element UI 2.13 + SCSS
- **构建工具**: Vue CLI 4.3 + Webpack 4
- **Node 版本**: 14.x (volta 锁定 14.21.3)
- **公共路径**: `/yw/`
- **开发端口**: 9202
- **代码规模**: 784 个 .vue 文件 + 328 个 .js 文件

## 文件结构

```
logisticsweb/src/
├── main.js                    # 应用入口，支持 qiankun 生命周期
├── public-path.js             # qiankun publicPath 设置
├── App.vue                    # 根组件
├── router/
│   ├── routers.js             # 静态路由定义
│   └── index.js               # 路由守卫 + 动态路由加载
├── vuex/
│   ├── index.js               # Vuex store 初始化
│   └── modules/               # 9 个 Vuex 模块
│       ├── app.js             # 用户信息/菜单/权限（核心，766行）
│       ├── public.js          # 公共数据（城市/运营参数/菜单折叠）
│       ├── enumeration.js     # 枚举数据
│       ├── payment.js         # 支付相关状态
│       ├── workspace.js       # 工作台状态
│       ├── tagsView.js        # 标签页视图
│       ├── xiaokuai.js        # 小快业务
│       ├── demo.js            # 示例
│       └── index.js           # 模块聚合
├── api/                       # 104 个 API 模块文件
├── views/
│   ├── userBase/              # 135 个业务模块（核心）
│   ├── login/                 # 登录页
│   ├── unifiedLoginPage/      # 统一门户登录
│   ├── findpwd/               # 找回密码
│   └── register/              # 注册/授权
├── components/                # 51 个公共组件
├── mixins/                    # 17 个 Mixin
├── utils/                     # 51 个工具函数文件
├── config/                    # 配置文件
├── constants/                 # 常量定义
├── directive/                 # 全局指令
├── layout/                    # 布局框架
│   ├── Layout.vue             # 主布局（支持嵌入模式）
│   ├── Page.js                # 页面包装
│   └── components/            # 布局子组件
│       ├── Header.vue         # 顶部导航
│       ├── Sidebar.vue        # 左侧二级菜单
│       ├── leftFirstLevelMenu.vue  # 左侧一级菜单
│       ├── AppMain.vue        # 主内容区
│       ├── Bottom.vue         # 底部栏
│       ├── TabsView/          # 标签页
│       └── ...
├── styles/                    # 全局样式
├── scss/                      # 模块级样式
├── icons/                     # 图标
└── vendor/                    # 第三方库
```

## 核心逻辑

### 1. 应用启动流程

```
main.js
  ├── 导入 polyfill、样式、Element UI
  ├── 注册全局组件（ElPaginationNew、ElImageX、TableDrag、Page）
  ├── 判断运行模式
  │   ├── 独立运行 → render()
  │   └── qiankun 子应用 → 暴露 bootstrap/mount/unmount
  └── render()
      ├── handleUrlParams()     # 处理 URL 参数（系统跳转）
      ├── import('./router/index')  # 加载路由守卫
      └── initVueApp(props)
          ├── asyncInitDeviceId()   # 初始化设备 ID
          ├── microRoutes(props)    # 微前端路由合并（qiankun 模式）
          └── new Vue({ router, store, render })
```

**关键文件**:
- `src/main.js` — 入口，qiankun 生命周期
- `src/utils/useMainProps.js` — 微前端 props 工具
- `src/utils/actions.js` — 主应用通信 actions
- `src/utils/microAppDialog.js` — 微前端弹窗挂载

### 2. 路由与权限

```
router/index.js（路由守卫）
  ├── beforeEach
  │   ├── 有 token
  │   │   ├── 访问登录页 → 重定向到工作台
  │   │   ├── 已加载菜单 → 直接放行
  │   │   └── 未加载菜单 → loadMenus()
  │   └── 无 token
  │       ├── 非 userBase 页面 → 放行
  │       └── userBase 页面 → 重定向到登录页
  └── loadMenus()
      ├── dispatch('app/getUserInfo')        # 获取用户信息
      ├── dispatch('app/getChildCompanyTreeList')  # 子公司树
      ├── dispatch('app/getAgencyTreeList')   # 代理树
      ├── dispatch('app/getUserMenu')         # 获取菜单权限
      ├── dispatch('app/getUserRoleType')     # 获取角色
      ├── dispatch('app/getHomePageSetConfig') # 首页配置
      └── filterAsyncRouter() → router.addRoutes()  # 动态注册路由
```

**动态路由生成规则**:
- 从后端接口获取菜单权限数据 `getUserMenu`
- 遍历权限数据，过滤 `actionName` + `url` 包含 `/` 的项
- 通过 `loadView()` 动态导入 `@/views/userBase/{path}` 组件
- 按钮权限通过 `funcType === '2'` 注入到路由 `meta` 中

**关键文件**:
- `src/router/routers.js` — 静态路由
- `src/router/index.js` — 路由守卫 + 动态路由

### 3. 请求层

```
utils/request.js（基于 axios）
  ├── 请求拦截器
  │   ├── 添加 token
  │   └── 添加公共参数（@wlydfe/http addHttpCommonData）
  ├── 响应拦截器
  │   ├── 业务错误码处理（WLYD_ERR_CODE）
  │   ├── 白名单错误码忽略
  │   ├── 401/403 → 跳转登录
  │   └── 弱网检测
  └── 请求封装
      ├── utils/requestSimply.js  # 简化版请求
      └── api/*.js               # 业务接口
```

**关键文件**:
- `src/utils/request.js` — 核心请求封装（374行）
- `src/utils/requestSimply.js` — 简化请求
- `src/config/index.js` — API 配置

### 4. 布局框架

```
Layout.vue（主布局）
  ├── Header.vue          # 顶部导航（消息通知、主题切换、系统切换）
  ├── leftFirstLevelMenu  # 左侧一级菜单（垂直图标菜单）
  ├── Sidebar.vue         # 左侧二级菜单（展开式）
  ├── AppMain.vue         # 主内容区（router-view + keep-alive）
  └── Bottom.vue          # 底部公告栏
```

**嵌入模式**: URL 参数 `embed=true` 时隐藏所有导航，只显示内容区（用于 iframe 嵌入场景）

**关键文件**:
- `src/layout/Layout.vue` — 主布局
- `src/layout/components/` — 布局子组件

### 5. 状态管理（Vuex）

| 模块 | 职责 | 核心 state |
|------|------|-----------|
| `app` | 用户/菜单/权限/公司 | userInfo, menu, organizationControl, childCompanyTree |
| `public` | 公共数据/菜单折叠 | menuCollapse, cityData, operationalParam |
| `enumeration` | 枚举缓存 | 各类业务枚举 |
| `payment` | 支付状态 | 支付密码、支付流程 |
| `workspace` | 工作台 | 工作台数据和配置 |
| `tagsView` | 标签页 | 已打开的页面标签 |
| `xiaokuai` | 小快业务 | 小快专用状态 |

**关键文件**:
- `src/vuex/modules/app.js` — 核心模块（766行）
- `src/utils/auth.js` — token/灰度值存取

### 6. 公共组件（51个）

| 组件 | 功能 |
|------|------|
| `CompanyTree` | 公司树选择器 |
| `OrganizationTree` | 组织结构树 |
| `AddressSelect` | 地址选择 |
| `AsyncSelect` | 异步下拉选择 |
| `ElPaginationNew/Update` | 分页组件 |
| `ExportBtn` | 导出按钮 |
| `FeeDetail` | 费用明细 |
| `Payment` | 支付组件 |
| `PdfPreview` | PDF 预览 |
| `Upload/UploadLocalFile` | 文件上传 |
| `Ocr` | OCR 识别 |
| `TableDrag` | 可拖拽表格 |
| `PageSearchForm/Select` | 页面搜索表单 |
| `Printing` | 打印功能 |
| `Risk/4plRisk` | 风控组件 |
| `SettlementProcessingDialog` | 结算处理弹窗 |
| `CommissionRate` | 佣金比例 |
| `contract/*` | 合同相关 |
| `sendForm` | 发货表单 |

### 7. Mixins（17个）

| Mixin | 功能 |
|-------|------|
| `keepAliveCache.js` | keep-alive 缓存管理 |
| `sourceDictionary.js` | 来源字典 |
| `endOfCalculation.js` | 末端计算 |
| `payPasswordVerify.js` | 支付密码校验 |
| `networkMainBodyMixin.js` | 网络主体混入 |
| `unitTool.js` | 单位转换工具 |
| `urgeTool.js` | 催办工具 |
| `validateFocus.js` | 表单校验聚焦 |
| `getTrackTimes.js` | 轨迹时间 |
| `insurance.js` | 保险相关 |
| `pickerOptionLimit.js` | 日期选择限制 |
| `emitter.js` | 事件分发 |
| `passwordRules.js` | 密码规则 |
| `applyRemark.js` | 申请备注 |

### 8. API 模块（104个文件）

按业务模块命名，核心 API 文件：

| API 文件 | 功能 |
|----------|------|
| `login.js` | 登录/注册/绑定手机 |
| `home.js` | 首页/菜单/工作台日期范围 |
| `public.js` | 公共接口（菜单/枚举） |
| `userBase.*.js` | 各业务模块接口 |
| `midPlatform.js` | 中台登录/用户信息 |
| `risk.js` | 风控接口 |
| `insurance.js` | 保险接口 |
| `market.js` | 市场接口 |
| `oilGasManage.js` | 油气管理 |

## 依赖关系图

```
main.js
  ├── router/index.js ──── vuex/modules/app.js ──── api/login.js
  │     │                                            api/home.js
  │     └── layout/Layout.vue                        api/public.js
  │           ├── Header.vue ── vuex/modules/app.js
  │           ├── Sidebar.vue
  │           ├── AppMain.vue ── views/userBase/*
  │           └── leftFirstLevelMenu.vue
  │
  ├── utils/request.js ── utils/auth.js
  │     ├── config/index.js
  │     └── @wlydfe/http
  │
  └── components/* ── mixins/* ── utils/*
```

## 数据流转

### 登录 → 加载菜单 → 进入工作台

```
1. 用户登录 → setToken() → 存储到 Cookie/localStorage
2. 路由守卫检测 token → loadMenus()
3. loadMenus() 依次调用:
   ├── getUserInfo → vuex app/userInfo
   ├── getChildCompanyTreeList → vuex app/childCompanyTree
   ├── getAgencyTreeList → vuex app/agencyTree
   ├── getUserMenu → 返回菜单树 + 权限数据
   ├── getUserRoleType → 返回角色类型
   └── getHomePageSetConfig → 首页模块配置
4. filterAsyncRouter() → 生成动态路由 → router.addRoutes()
5. 跳转到 /userBase/workspace（工作台）
```

### qiankun 微前端数据流

```
主应用 mount(props)
  ├── actions.setActions(props)     # 保存主应用通信方法
  ├── initMicroTrack()              # 初始化埋点
  ├── globalStateOff = onGlobalStateChange()  # 监听全局状态
  ├── getToken() → setToken()       # 同步 token
  ├── props.userStore → 获取用户信息
  │   ├── userInfoModel → store.commit('app/SET_USER_INFO')
  │   └── companyModel → store.commit('app/SET_COMPANY_ID')
  └── render(props)                 # 启动 Vue 应用
```

## 环境配置

| 环境 | API 地址 | 说明 |
|------|---------|------|
| dev | `https://3pldelta.10000da.vip` | 开发环境 |
| uat | — | UAT 测试 |
| prod | — | 生产环境 |

配置文件由 `scripts/generate-env.js` 根据 `.env.config.js` 自动生成。

## 构建部署

- **dev**: `npm run dev` → 端口 9202
- **build**: `npm run build` → 生成 dist/ + zip 包
- **Docker**: 通过 `Dockerfile` + `Jenkinsfile` 部署
- **Nginx**: `nginx/` 下有各环境配置

## 注意事项

1. **qiankun 兼容**: `vue.config.js` 中 `libraryTarget: 'umd'`，`main.js` 暴露 `bootstrap/mount/unmount` 生命周期
2. **动态路由**: 所有业务页面在 `views/userBase/` 下，通过后端菜单权限动态注册路由
3. **嵌入模式**: `embed=true` 参数可隐藏所有导航，用于 iframe 嵌入
4. **表格配置预加载**: 登录成功后通过 `preloadTableConfig()` 预加载用户级表格配置（OSS）
5. **Node 版本**: 锁定 14.x，使用 node-sass，不可升级 Node
6. **全局组件**: `ElPaginationNew`、`ElImageX`、`TableDrag`、`Page` 在 main.js 中全局注册
7. **请求层**: 基于 axios 封装，集成了 `@wlydfe/http`（设备ID、公共参数）、`@wlydfe/core`（错误码）

## 相关文档

- [bdbl-admin 代码图谱](../bdbl-admin/)
- [平台web 代码图谱](../platformweb/)

---

**文档版本**: v1.0

**最后更新**: 2026年7月

**整理方式**: code-graph skill 自动分析
