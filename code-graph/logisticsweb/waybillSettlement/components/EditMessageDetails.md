# EditMessageDetails.vue — 操作记录组件

## 概述

`EditMessageDetails` 是运单结算详情页（edit.vue / read.vue）中的操作记录展示组件，纯展示型，无交互逻辑，由父组件传入记录数组直接渲染。

---

## 文件位置

```
src/views/userBase/waybillSettlement/components/EditMessageDetails.vue
```

---

## Props

| prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `params` | Array | `null` | 操作记录数组，为 `null` 时表格显示 loading |

---

## 表格列

| 列 | prop | 宽度 | 说明 |
|----|------|------|------|
| 序号 | type=index | 60 | |
| 操作动作 | `operationDesc` | 200 | show-overflow-tooltip |
| 操作账号 | `operationNumber` | 180 | show-overflow-tooltip |
| 操作人员 | `createName` | 180 | show-overflow-tooltip |
| 操作时间 | `createDate` | 180 | `formatToDate(createDate).format('yyyy-MM-dd HH:mm')` |
| 备注 | `remark` | min-width 80 | 左对齐；class `operation-historynote-break`（自动换行） |

---

## 父组件使用方式

```html
<EditMessageDetails :params="operationRecordList" />
```

父组件（edit.vue / read.vue）中的加载逻辑：

```js
// 仅展示 2024-02-01 之后创建的运单的操作记录
async getRecord() {
  const createDate = this.detail?.createDate
  if (createDate && createDate < '2024-02-01') return
  const res = await dcsOperationRecordPagingexport({ waybillId, ... })
  this.operationRecordList = res.model || []
}
```

分页由父组件的 `handleCurrentChange` 方法驱动，分页组件在父页面中，而非组件内部。

---

**文档版本**: v1.0
**最后更新**: 2026年07月
**整理人**: 王新骏
