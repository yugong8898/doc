# useMainProps 工具模块

## 概述

`useMainProps.js` 是 logisticsweb 子应用中用于管理微前端集成的核心工具模块。负责处理从主应用（qiankun）下发的 props，提供路由初始化、配置管理、动态解构等功能，确保子应用能够正确获取主应用的配置、API 方法和用户信息等资源。

**核心职责**：
- 初始化和存储微前端 props
- 创建支持动态解构的配置对象
- 初始化微前端路由
- 提供主应用资源访问接口
- 管理子应用与主应用的通信

## 文件结构

```
src/
├── utils/
│   ├── useMainProps.js           # 本模块
│   ├── normalizeAuthMeta.js      # 权限元数据标准化
│   └── request.js                # HTTP 请求封装（使用本模块）
├── router/
│   └── micro-router.js           # 微前端路由创建器
├── vuex/
│   └── index.js                  # Vuex store
└── main.js                       # 应用入口（使用本模块）
```

## 模块级变量

```javascript
let globalMicroProps = {}  // 全局存储微前端props
let bool = false           // 控制刷新时只拉取一次权限、用户信息等
```

**默认配置**：

```1:19:logisticsweb/src/utils/useMainProps.js
import Vue from 'vue'
import { createRouter } from '@/router/micro-router'
import { normalizeAuthMeta } from '@/utils/normalizeAuthMeta'
import store from '../vuex'

// 全局存储微前端props
let globalMicroProps = {}
// 控制刷新的时候，只拉取一次权限、用户信息等
let bool = false

// 默认配置
const defaultConfig = {
  container: null,
  api: {
    request: null,
    urlConfig: null
  },
  utils: null,
  routerBase: '/',
  routes: []
}
```

## 核心功能

### 1. 动态值对象（createDynamicValue）

创建支持动态获取最新值的对象，解决解构后值不更新的问题。通过重写 `toString()`、`valueOf()` 和 `Symbol.toPrimitive`，每次类型转换时都从 `globalMicroProps` 获取最新值。

```27:56:logisticsweb/src/utils/useMainProps.js
/**
 * 创建动态值对象，支持解构后动态获取最新值
 * @param {string} configKey - 配置键名
 * @param {string} propKey - 属性键名
 * @returns {Object} - 动态值对象
 */
function createDynamicValue(configKey, propKey) {
  const dynamicValue = {
    // 当用作字符串时，返回最新值
    toString() {
      const config = getMicroProps(configKey) || {}
      return config[propKey] || ''
    },
    // 当用作原始值时，返回最新值
    valueOf() {
      const config = getMicroProps(configKey) || {}
      return config[propKey] || ''
    },
    // Symbol.toPrimitive 处理所有类型转换
    [Symbol.toPrimitive](hint) {
      const config = getMicroProps(configKey) || {}
      const value = config[propKey] || ''

      if (hint === 'string') {
        return String(value)
      } else if (hint === 'number') {
        return Number(value)
      } else {
        return value
      }
    }
  }

  return dynamicValue
}
```

### 2. 动态函数（createDynamicFunction）

创建动态函数代理，确保解构后的函数调用始终使用最新的实现。使用 Proxy 代理函数调用，每次调用时从 `globalMicroProps` 获取最新函数，主要用于 `request` 函数的动态代理。

```58:101:logisticsweb/src/utils/useMainProps.js
/**
 * 创建动态函数，支持解构后动态调用最新函数
 * @param {string} propKey - 属性键名
 * @returns {Function} - 动态函数
 */
function createDynamicFunction(propKey) {
  // 创建一个函数，每次调用时都获取最新的函数
  const dynamicFunction = function(...args) {
    const latestFunction = getMicroProps(propKey)

    if (!latestFunction) {
      console.warn(`微应用 ${propKey} 尚未初始化，请确保在微应用启动后调用`)
      return Promise.reject(new Error(`${propKey} not initialized`))
    }

    if (typeof latestFunction !== 'function') {
      console.warn(`微应用 ${propKey} 不是一个函数`)
      return Promise.reject(new Error(`${propKey} is not a function`))
    }

    return latestFunction(...args)
  }

  // 使用 Proxy 来代理函数的其他属性和方法
  return new Proxy(dynamicFunction, {
    get(target, prop) {
      // 获取最新的函数
      const latestFunction = getMicroProps(propKey)

      if (!latestFunction) {
        return undefined
      }

      // 返回最新函数的属性或方法
      const value = latestFunction[prop]

      // 如果是方法，绑定正确的 this
      if (typeof value === 'function') {
        return value.bind(latestFunction)
      }

      return value
    },

    // 支持 apply 调用
    apply(target, thisArg, argumentsList) {
      return target(...argumentsList)
    }
  })
}
```

### 3. 动态配置/完整对象（createDynamicDestructurable / createFullDynamicDestructurable）

通过 Proxy 创建支持动态解构的配置对象，支持 `Object.keys()`、`in` 操作符，特殊处理 `request` 函数类型。

```103:161:logisticsweb/src/utils/useMainProps.js
/**
 * 创建支持动态解构的配置对象
 * @param {string} configKey - 配置键名
 * @returns {Proxy} - 支持动态解构的配置对象
 */
function createDynamicDestructurable(configKey) {
  return new Proxy({}, {
    get(target, prop) {
      // 如果是 request 函数，返回动态函数
      if (prop === 'request') {
        return createDynamicFunction('request')
      }

      // 其他属性返回动态值对象
      return createDynamicValue(configKey, prop)
    },
    // 支持 Object.keys() 等操作
    ownKeys(target) {
      const config = getMicroProps(configKey) || {}
      return Object.keys(config)
    },
    // 支持 in 操作符
    has(target, prop) {
      const config = getMicroProps(configKey) || {}
      return prop in config
    },
    // 支持 Object.getOwnPropertyDescriptor
    getOwnPropertyDescriptor(target, prop) {
      const config = getMicroProps(configKey) || {}
      if (prop in config) {
        return {
          enumerable: true,
          configurable: true,
          value: prop === 'request' ? createDynamicFunction('request') : createDynamicValue(configKey, prop)
        }
      }
      return undefined
    }
  })
}
```

### 4. 初始化微前端 props（initMicroProps）

初始化和存储从主应用下发的 props，挂载到 Vue 原型。

```163:194:logisticsweb/src/utils/useMainProps.js
/**
 * 初始化微前端props
 * @param {Object} props - 从主应用下发的props
 */
export function initMicroProps(props = {}) {
  // 合并默认配置和传入的props
  globalMicroProps = {
    ...defaultConfig,
    ...props,
    api: {
      ...defaultConfig.api,
      ...props.api
    }
  }

  // 挂载到Vue原型上，便于组件中使用
  if (globalMicroProps.request) {
    Vue.prototype.$request = globalMicroProps.request
  }
  if (globalMicroProps.config) {
    Vue.prototype.$config = globalMicroProps.config
  }
  if (globalMicroProps.utils) {
    Vue.prototype.$utils = globalMicroProps.utils
  }
  // 如果父应用下发了 getToken 方法或 getter，挂载到 Vue 原型，子应用可通过 this.$getToken() 获取
  if (globalMicroProps.getToken) {
    Vue.prototype.$getToken = globalMicroProps.getToken
  }
  // getCookieToken：直接读 Cookie 的 token（跨 Tab 共享实时值），用于跨 Tab 账号切换检测
  if (globalMicroProps.getCookieToken) {
    Vue.prototype.$getCookieToken = globalMicroProps.getCookieToken
  }
  return globalMicroProps
}
```

**挂载的 Vue 原型属性**：

| 属性 | 说明 |
|------|------|
| `this.$request` | HTTP 请求方法 |
| `this.$config` | 主应用配置 |
| `this.$utils` | 工具函数集 |
| `this.$getToken` | 获取 token 方法 |
| `this.$getCookieToken` | 从 Cookie 获取 token（跨 Tab 实时共享，用于账号切换检测） |

### 5. 微前端路由初始化（microRoutes）

创建微前端路由实例，处理路由守卫、权限控制和 history 修复。

```264:349:logisticsweb/src/utils/useMainProps.js
/**
 * 创建微前端路由
 * @param {Object} props - 微前端props
 * @returns {Object} - Vue Router实例
 */
export function microRoutes(props) {
  // 初始化props
  const microProps = initMicroProps(props)
  console.log('microProps', microProps)

  // 只做 meta.auths 转换，不碰 path/component
  const processedRoutes = normalizeAuthMeta(microProps.routes || [])

  // 创建路由
  const router = createRouter({
    base: microProps.routerBase, // qiankun.readme 重要
    routes: processedRoutes
  })
  globalMicroProps.router = router

  router.beforeEach((to, from, next) => {
    if (to.meta.title) {
      document.title = to.meta.title
    }

    if (!bool) {
      bool = true
      try {
        loadMicroAppStore(next, to)
      } catch (error) {
        console.error('[子应用] 初始化失败:', error)
        // 重置 bool，允许重试
        bool = false
      }
    } else {
      next()
    }
  })
  // ... afterEach 处理 history 修复
  router.push = handlePush
  return router
}
```

**路由守卫功能**：
- `beforeEach`：设置页面标题；首次加载时调用 `loadMicroAppStore` 初始化 store（用 `bool` 标志保证只执行一次）；失败时重置 `bool` 允许重试
- `afterEach`：提交 `app/SET_CONTROL_BTN` 设置按钮权限；使用 `window.history.replaceState` 修复 qiankun 微前端的 history 状态
- `router.push`：自定义实现，自动为路径添加 `/app-3pl` 前缀

### 6. Store 初始化（loadMicroAppStore）

路由首次跳转时加载微应用所需数据，仅执行一次。

```252:262:logisticsweb/src/utils/useMainProps.js
/**
 * 作为微前端使用时加载的store，供部分页面直接使用
 * @param {*} next
 * @param {*} to
 */
const loadMicroAppStore = async(next, to) => {
  await store.dispatch('app/getUserInfo', {})
  store.dispatch('public/loadCityData', {})
  // store.dispatch('app/getChildCompany', {}) // 旧接口，保留备查
  store.dispatch('app/getChildCompanyTreeList', {})
  store.dispatch('app/getAgencyTreeList', {})
  next()
}
```

**加载的数据**：用户信息、城市数据、子公司树形列表、代理商树形列表

### 7. 工具方法

```196:392:logisticsweb/src/utils/useMainProps.js
/**
 * 获取微前端容器
 * @returns {Object} - 返回容器对象
 */
export function getMicroContainer() {
  return globalMicroProps.container
}

/**
 * 获取微前端props
 * @param {String} key - 可选，指定获取某个属性
 * @returns {Object|any} - 返回完整props或指定属性
 */
export function getMicroProps(key) {
  if (key) {
    return globalMicroProps[key]
  }
  return globalMicroProps
}
// ... getDynamicProps / isMicroApp / getMainUserStore
```

| 方法 | 说明 |
|------|------|
| `getMicroContainer()` | 获取微前端容器对象 |
| `getMicroProps(key?)` | 获取完整 props 或指定属性 |
| `getDynamicProps(key?)` | 获取支持动态解构的配置对象 |
| `isMicroApp()` | 检查是否在 qiankun 微前端环境中（`window.__POWERED_BY_QIANKUN__`） |
| `getMainUserStore()` | 获取主应用的用户 store（用于统一登录） |

## 依赖关系图

```
useMainProps.js
    ├── 依赖
    │   ├── Vue
    │   ├── @/router/micro-router（路由创建）
    │   ├── @/utils/normalizeAuthMeta（权限标准化）
    │   └── @/vuex（状态管理）
    │
    └── 被引用（30+ 文件）
        ├── main.js
        ├── utils/request.js
        ├── views/userBase/**/*.vue（业务页面）
        ├── components/**/*.vue（公共组件）
        └── api/*.js
```

## 数据流转

### 初始化流程

```
主应用（qiankun）下发 props
    ↓
microRoutes(props)
    ↓ initMicroProps → 存储 globalMicroProps，挂载 Vue.prototype
    ↓ normalizeAuthMeta → 处理路由权限
    ↓ createRouter → 创建路由实例
    ↓ 注册 beforeEach / afterEach 守卫
首次路由跳转
    ↓
loadMicroAppStore → 加载用户信息等
    ↓
应用就绪
```

### 动态 props 获取流程

```
const { request } = getDynamicProps()
    ↓ createDynamicFunction('request')
调用 request(...)
    ↓ getMicroProps('request')
    ↓ 返回 globalMicroProps 中最新的 request 函数
```

## 注意事项

1. **初始化顺序**：必须先调用 `microRoutes()` 或 `initMicroProps()` 才能使用其他方法。

2. **动态解构 vs Vue 原型**：模块级别的解构需要用 `getDynamicProps()`；组件内直接用 `this.$request` 更简洁。

3. **路由 base 配置**：qiankun 微前端必须正确设置 `routerBase`（通常为 `/app-3pl`），否则路由匹配会出错。

4. **跨 Tab 账号检测**：使用 `$getCookieToken` 而非 `$getToken`，前者直接读 Cookie，可跨 Tab 实时感知账号切换。

5. **bool 标志机制**：`loadMicroAppStore` 仅在首次路由跳转执行，刷新不重复请求；初始化失败会重置 `bool` 允许重试。

---

**文档版本**: v1.0

**最后更新**: 2026年06月

**整理人**: 王新骏
