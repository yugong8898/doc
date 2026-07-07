# extends 工具模块

## 概述

`logisticsweb/src/utils/extends.js` 是全局工具函数挂载文件，负责：

1. 扩展原生对象原型（`Date.prototype`、`String.prototype`）
2. 将工具函数挂载到 `Vue.prototype`，在组件中通过 `this.xxx` 调用
3. 将工具函数同步挂载到 `window`，支持非 Vue 组件上下文调用

该文件在项目入口 `main.js` 处被引入，属于全局初始化逻辑，所有页面和组件均可直接使用其中的方法，无需单独 import。

> 注：`logisticsweb/src/utils/extends.js` 与 `bdbl-admin/src/utils/extends.js` 内容完全一致，为跨项目共用的工具模块副本。

---

## 文件结构

```
logisticsweb/src/utils/
├── extends.js          ← 本文件：全局工具函数注册
├── unitComputed.js     ← 被引用：单位换算工具
└── array.js            ← 被引用：数组扩展（仅副作用引入）
```

---

## 依赖关系

```
extends.js
├── vue                    （挂载到 Vue.prototype）
├── bignumber.js           （高精度数值计算）
├── element-ui / Message   （导出为空提示弹窗）
├── @/utils/unitComputed   （单位换算，挂载为 $unitComputed）
└── @/utils/array          （数组方法扩展，副作用引入）
```

---

## 核心功能

### 1. 原型扩展

#### `Date.prototype.format(format)`

日期格式化，将 Date 对象按指定格式输出字符串。

| 占位符 | 含义 |
|--------|------|
| `yyyy` | 4位年份 |
| `MM` / `M` | 月份（含前导零 / 不含） |
| `dd` / `d` | 日期 |
| `HH` / `hh` | 24小时制小时 |
| `mm` | 分钟 |
| `ss` | 秒 |
| `S` | 毫秒 |
| `q` | 季度 |

```javascript
new Date().format('yyyy-MM-dd HH:mm:ss')
// → "2026-07-07 10:30:00"
```

#### `String.prototype.format(...args)`

字符串占位符替换，支持两种用法：

```javascript
// 对象形式
'{name}，您好'.format({ name: '王新骏' })  // → "王新骏，您好"

// 下标形式
'{0} + {1} = {2}'.format(1, 2, 3)          // → "1 + 2 = 3"
```

---

### 2. 日期工具

#### `formatToDate(args)` → `Date`

将字符串安全转换为 Date 对象，解决 iOS/Safari 不支持 `new Date('2026-07-07')` 的兼容问题（将 `-` 替换为 `/`）。

- 挂载位置：`window.formatToDate`、`Vue.prototype.formatToDate`
- 入参为空时返回当前时间

#### `checkTimeAvaible(date)` → `Boolean`

校验日期字符串（格式 `yyyy-mm-dd`）的合法性。

- 防止 OCR 识别接口返回异常年份（如 `19038-03-02`），强制校验年份必须为 4 位
- 挂载位置：`window.checkTimeAvaible`、`Vue.prototype.checkTimeAvaible`

---

### 3. 金额 / 数值工具

#### `parsePrice(num)` → `String`

数字转千分位金额字符串，固定保留两位小数。底层使用 BigNumber 避免浮点精度问题。

```javascript
parsePrice(1234567.8)  // → "1,234,567.80"
parsePrice(null)       // → "0.00"
```

- 挂载位置：`window.parsePrice`、`Vue.prototype.parsePrice`

#### `parsePriceReduction(val)` → `String`

千分位金额字符串还原为纯数字字符串（去除 `,`）。

```javascript
parsePriceReduction('1,234,567.80')  // → "1234567.80"
```

- 挂载位置：`window.parsePriceReduction`、`Vue.prototype.parsePriceReduction`

#### `parseTon(param, type, dotNum)` → `String`

吨位数值处理，支持克→吨转换和小数位补齐。

| 参数 | 说明 |
|------|------|
| `param` | 原始数值 |
| `type` | 为 `true` 时除以 1000（克转吨） |
| `dotNum` | 小数位数，默认 3 位；结算重支持 4 位小数 |

- 挂载位置：`window.parseTon`、`Vue.prototype.parseTon`

#### `delZero(number)` → `String`

去除数值末尾多余的 0（包括小数点本身）。

```javascript
delZero('1.500')   // → "1.5"
delZero('2.000')   // → "2"
delZero('100')     // → "100"
```

- 挂载位置：`Vue.prototype.delZero`（仅 Vue，未挂 window）

#### `BNumber(value)` → `BigNumber`

BigNumber 工厂函数，入参为空时默认为 0，避免 `new BigNumber(undefined)` 报错。

```javascript
BNumber(null).plus(1).toFixed(2)  // → "1.00"
```

- 挂载位置：`window.BNumber`、`Vue.prototype.BNumber`

#### `floatCeil(num, pow = 2)` → `String`

小数向上取整，默认保留 2 位小数。

```javascript
floatCeil(1.001)       // → "1.01"
floatCeil(1.001, 3)    // → "1.001"
```

- 挂载位置：`window.floatCeil`、`Vue.prototype.$floatCeil`

---

### 4. 数据修补工具

#### `patchEmpty(obj)`

遍历对象所有字段，将 `NaN`、`null`、`undefined` 统一替换为空字符串 `''`。常用于接口返回数据的兜底处理。

```javascript
patchEmpty({ a: null, b: NaN, c: undefined, d: 1 })
// → { a: '', b: '', c: '', d: 1 }
```

- 挂载位置：`window.patchEmpty`、`Vue.prototype.$patchEmpty`

#### `patchParseFloat(number)` → `String`

修复 `parseFloat` 的三种异常返回（`NaN`、`null`、`undefined`），统一返回空字符串或数字字符串。

```javascript
patchParseFloat('abc')   // → ""
patchParseFloat(null)    // → ""
patchParseFloat('3.14')  // → "3.14"
```

- 挂载位置：`window.patchParseFloat`、`Vue.prototype.$patchParseFloat`

#### `isEmpty(any)` → `Boolean`

判断值是否为空（`undefined`、`null` 或 `''`）。

```javascript
isEmpty(null)   // → true
isEmpty(0)      // → false
isEmpty('')     // → true
```

- 挂载位置：`window.isEmpty`、`Vue.prototype.$isEmpty`

---

### 5. 异步工具

#### `packageAsync(func)` → `[err, data]`

将 Promise 包装为 `[error, data]` 元组，统一处理 try/catch，避免 async/await 中大量嵌套 try 块。

```javascript
const [err, res] = await this.packageAsync(someApi())
if (err) return
// 正常处理 res
```

- 挂载位置：`Vue.prototype.packageAsync`（仅 Vue，未挂 window）

---

### 6. 导出校验

#### `exportListIsNull(list)` → `Boolean`

检查列表是否有数据可导出，无数据时自动弹出 Element UI 的 warning 提示。

```javascript
if (!this.exportListIsNull(this.tableData)) return
// 执行导出逻辑
```

- 挂载位置：`window.exportListIsNull`、`Vue.prototype.exportListIsNull`

---

## 挂载汇总

| 函数名 | Vue.prototype | window | 命名差异 |
|--------|:---:|:---:|--------|
| `formatToDate` | ✅ | ✅ | 同名 |
| `parsePrice` | ✅ | ✅ | 同名 |
| `parsePriceReduction` | ✅ | ✅ | 同名 |
| `parseTon` | ✅ | ✅ | 同名 |
| `delZero` | ✅ | ❌ | — |
| `BNumber` | ✅ | ✅ | 同名 |
| `checkTimeAvaible` | ✅ | ✅ | 同名 |
| `floatCeil` | ✅（`$floatCeil`） | ✅ | Vue 加 `$` 前缀 |
| `patchEmpty` | ✅（`$patchEmpty`） | ✅ | Vue 加 `$` 前缀 |
| `patchParseFloat` | ✅（`$patchParseFloat`） | ✅ | Vue 加 `$` 前缀 |
| `isEmpty` | ✅（`$isEmpty`） | ✅ | Vue 加 `$` 前缀 |
| `exportListIsNull` | ✅ | ✅ | 同名 |
| `packageAsync` | ✅ | ❌ | — |
| `unitComputed` | ✅（`$unitComputed`） | ✅（`$unitComputed`） | 同名（含 `$`） |

---

## 注意事项

- `Date.prototype.format` 和 `String.prototype.format` 使用 `no-extend-native` eslint 注释豁免，修改需谨慎，原型污染会影响全局
- `checkTimeAvaible` 拼写为 `Avaible`（非标准 `Available`），历史遗留，调用时注意拼写
- `floatCeil` 在 `window` 上直接挂载为 `floatCeil`，在 Vue 上为 `$floatCeil`，注意区分调用上下文
- `delZero` 和 `packageAsync` 仅挂载在 `Vue.prototype`，非 Vue 上下文需手动 import
- 本文件与 `bdbl-admin` 同名文件内容一致，若需修改应同步更新两个项目

---

## 相关文档

- [bdbl-admin extends 工具模块](../../bdbl-admin/extends工具模块.md)

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
