# 运单结算模块 — 重构方案

> 原则：每一步独立可验证，做完一步测一遍再做下一步。不要同时改多个文件。
>
> 状态标记：⬜ 待执行 / 🔄 进行中 / ✅ 已完成

---

## 背景

`edit.vue`、`read.vue`、`WeighBillCarousel.vue` 三处均包含一段结构和行为完全一致的 `el-image-x` 全屏图片预览代码，各自维护各自的状态和方法，重复度高，任何一处改动需同步三处。

---

## 收益评估

**量化收益：**

| 维度 | 数据 |
|---|---|
| 涉及重复逻辑的代码行 | edit.vue 21 行 + read.vue 21 行 + WeighBillCarousel.vue 31 行 = **73 行** |
| 重构后净减少 | 约 **60 行**（三处各换为 1 行模板 + 1 行 import + 1 行 components 注册）|
| 新增文件 | 1 个（`ImagePreview.vue`，约 50 行）|

**实质收益：**

- `getUrlTxt` 存在边界 bug（`index` 为 `undefined` 时直接报错）：`WeighBillCarousel` 已修复，`edit`/`read` 未同步。重构后 bug 只需修一处，自动覆盖三处调用方。
- 后续 `el-image-x` 相关调整（title 样式、下载逻辑等）改一处生效，不再需要三处同步。

**成本与风险：**

- 新增一层 ref 调用（`this.$refs.imagePreview.open()`），调试链路变长
- `WeighBillCarousel` 改完后形成"自己拉数据、交给子组件展示"的依赖链，略增复杂度
- 需要验证 `@update` 事件链（旋转保存）是否正常透传

**优先级结论：低，不单独排期。**

三处代码变化频率极低，`getUrlTxt` 的 bug 也未见线上反馈。建议策略：**触碰相关文件时顺手处理**，不作为独立任务排期。若 `el-image-x` 有新需求导致三处需要同步改动，再执行本方案。

---

**三处重复代码对比：**

| | `edit.vue` L118-136 | `read.vue` L169-187 | `WeighBillCarousel.vue` L30-51 |
|---|---|---|---|
| 模板结构 | 完全一致 | 完全一致 | 完全一致（多 3 个 props）|
| data：imgList / imgListUrl / urlTxt | ✅ | ✅ | ✅（另有 saveImgListUrl / billPreviewIndex）|
| 方法：getUrlTxt | ✅ 有 bug（index 为 undefined 时报错）| ✅ 同左 | ✅ 已修复 |
| 方法：prevXxx / nextXxx / clickHandlerXxx | ✅ | ✅ | ✅ |
| 额外 props：save-url-list / initial-index | ❌ | ❌ | ✅ |
| 额外事件：@update | ❌ | ❌ | ✅ |
| 样式：.img-view-item-tip | ✅ | ✅ | ✅ |

**方案**：抽取 `ImagePreview.vue` 作为纯 UI 层组件，三处调用方各自保留数据获取逻辑，统一用 `images` prop 传入，用 `open(index)` 方法触发预览。

---

## WS-1 — 新建 `components/ImagePreview.vue`

**状态**：⬜

### 组件完整接口

```
props:
  images:       Array    必填  [{ name: string, url: string, path?: string }]
                               path 为 OSS 原始路径，供旋转保存接口使用
                               edit/read 传入时无 path，组件内兜底取 url
  showDownBtn:  Boolean  选填  默认 false，控制预览器下载按钮显示

events:
  update        选填  图片旋转保存成功后触发，WeighBillCarousel 监听后重新拉图

method（通过 ref 调用）:
  open(index)   触发全屏预览，index 为初始展示位置，默认 0
```

### 组件内部状态（从三处调用方下沉）

```
data:
  urlTxt          string   当前预览图片的 title，随翻页更新
  currentIndex    number   当前预览位置，open(index) 时赋值

computed:
  imgListUrl      从 images 派生，images.map(i => i.url)
  saveImgListUrl  从 images 派生，images.map(i => i.path || i.url)
```

### 关键实现说明

**getUrlTxt 边界修复**：
- `edit`/`read` 中原代码 `this.imgList[index].name`，index 为 undefined 时直接报错
- `WeighBillCarousel` 中已修复为 `const item = this.imgList[index]; return item ? item.name : ''`
- 组件内统一用修复后的写法

**open(index) 实现**：
```js
open(index = 0) {
  this.currentIndex = index
  this.$nextTick(() => {
    this.$refs.imageXRef.clickHandler()
  })
}
```

**imgListUrl / saveImgListUrl 改为 computed**：
- 原三处均为手动赋值（`this.imgListUrl = this.images.map(...)`）
- 组件内改为 computed，由 images prop 自动派生，消除手动同步

### 模板结构

```vue
<el-image-x
  v-show="false"
  ref="imageXRef"
  class="img-view-item"
  fit="cover"
  :params-info="images"
  :show-down-btn="showDownBtn"
  :preview-src-list="imgListUrl"
  :save-url-list="saveImgListUrl"
  :initial-index="currentIndex"
  @prev="onPrev"
  @next="onNext"
  @clickHandler="onClickHandler"
  @update="$emit('update')"
>
  <template #slot-html>
    <div class="img-view-item-tip">{{ urlTxt }}</div>
  </template>
</el-image-x>
```

### 样式（从三处合并，内容完全一致）

```scss
.img-view-item-tip {
  position: fixed;
  top: 0;
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 40px;
  background-color: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 30px;
}
```

### 验证

- [ ] 组件可正常 import，无语法错误
- [ ] open(0) 触发后全屏预览弹出，显示第一张图
- [ ] open(n) 触发后定位到第 n 张图
- [ ] 翻页时 title 正常更新
- [ ] images 为空数组时调用 open() 不报错
- [ ] showDownBtn=false 时下载按钮不显示

---

## WS-2 — 改造 `WeighBillCarousel.vue`

**依赖**：WS-1 完成
**状态**：⬜

### 删除内容

**模板**（L30-51，整块注释）：
```vue
<!-- [WS-2] 已由 ImagePreview 组件替代 -->
<!-- <el-image-x v-show="false" ref="billPreviewRef" ... > ... </el-image-x> -->
```

**data**（5 项）：
```js
// [WS-2] 下沉至 ImagePreview 组件
// imgList: [],
// imgListUrl: [],
// saveImgListUrl: [],
// urlTxt: '',
// billPreviewIndex: 0
```

**方法**（5 个）：
```js
// [WS-2] 下沉至 ImagePreview 组件
// syncImgList() { ... }
// getUrlTxt(index) { ... }
// clickHandlerImg(index) { ... }
// prevImg(index) { ... }
// nextImg(index) { ... }
```

**样式**（`.img-view-item-tip`，整块注释）

### 新增 / 修改内容

**模板**：在 `</el-carousel>` 后替换为：
```vue
<image-preview
  ref="imagePreview"
  :images="images"
  :show-down-btn="showDownBtn"
  @update="handleImageSaved"
/>
```

**引入注册**：
```js
import ImagePreview from './ImagePreview.vue'
// components: { ImagePreview }
```

**`handleClickBillImg` 方法修改**（原 L186-190）：
```js
// 改前
handleClickBillImg(imgIndex) {
  this.syncImgList()
  this.billPreviewIndex = imgIndex || 0
  this.$nextTick(() => {
    this.$refs.billPreviewRef.clickHandler()
  })
}

// 改后
handleClickBillImg(imgIndex) {
  this.$refs.imagePreview.open(imgIndex || 0)
}
```

**`getBillImages` 方法修改**：删除末尾的 `this.syncImgList()` 调用（原 L158），`images` 赋值后 `ImagePreview` 自动响应 prop 变化，无需手动同步。

**`resetBillImages` 方法修改**：删除 `this.syncImgList()` 调用，只保留 `this.images = []`。

**`handleImageSaved` 保持不变**：仍然调用 `this.getBillImages(this.waybillId)`，重新拉图后 images 更新，`ImagePreview` 自动响应。

### 影响范围

- `SettlementInfo.vue` 使用了两个 `WeighBillCarousel` 实例（load / unload），均受影响
- `edit.vue` 和 `read.vue` 通过 `SettlementInfo` 间接使用，间接受影响

### 边界情况

| 场景 | 预期行为 |
|---|---|
| transportType 不在 WEIGH_BILL_STATUS_MAP（如 4/5） | `resetBillImages` 清空 images，轮播显示空占位图，open() 不会被调用 |
| waybillId 为空 | watch 触发 `resetBillImages`，images 为空数组 |
| 接口返回 succeed=false 或 model 为空 | rawItems 为 []，images 为 []，轮播显示空占位图 |
| 接口异常（catch） | `resetBillImages` 清空，不崩溃 |
| 图片旋转保存后 @update 触发 | `handleImageSaved` 重新拉图，`ImagePreview` 的 images prop 更新，预览器刷新 |
| 点击缩略图触发 open(imgIndex) | 定位到对应图片，不再需要手动维护 billPreviewIndex |

### 验证

- [ ] 装货/卸货磅单轮播缩略图正常展示（有图 / 无图两种状态）
- [ ] 点击缩略图全屏预览弹出，定位到点击的图片
- [ ] 翻页时顶部 title 正常更新
- [ ] 旋转保存后缩略图同步更新（重新拉取），重新点击预览正常
- [ ] transportType=4/5 时轮播显示空状态，不报错
- [ ] SettlementInfo 中 load / unload 两个实例互不干扰

---

## WS-3 — 改造 `edit.vue`

**依赖**：WS-1 完成
**状态**：⬜

### 删除内容

**模板**（L118-136，整块注释）：
```vue
<!-- [WS-3] 已由 ImagePreview 组件替代 -->
<!-- <el-image-x v-show="false" ref="previewRef" ...> ... </el-image-x> -->
```

**data**（3 项，L344-346 / L484）：
```js
// [WS-3] 下沉至 ImagePreview 组件
// imgList: [],
// imgListUrl: [],
// urlTxt: '',
```

**方法**（4 个，L576-586）：
```js
// [WS-3] 下沉至 ImagePreview 组件
// getUrlTxt(index) { ... }
// clickHandlerUnLoad(index) { ... }
// prevLoadImg(index) { ... }
// nextLoadImg(index) { ... }
```

**样式**（`.img-view-item-tip`，整块注释）

### 新增 / 修改内容

**模板**：在注释掉的 `el-image-x` 位置替换为：
```vue
<!-- 查看装货、卸货附件 -->
<image-preview ref="imagePreview" :show-down-btn="controlBtn.btnDownload" :images="imgList" />
```

**引入注册**：
```js
import ImagePreview from './components/ImagePreview.vue'
// components: { ..., ImagePreview }
```

**`handleLookImg` 方法修改**（L1140-1190）：
```js
// 改前（末尾部分）
this.imgList = newArray
this.imgListUrl = this.imgList.map(i => i.url)         // ← 删除
this.imgPreviewTitle = tableLabelEnum[`${+btnType - 1}`].name
// this.dialogImgVisible = true
this.$nextTick(() => {
  this.$refs.previewRef.clickHandler()                  // ← 改
})

// 改后
this.imgList = newArray
this.imgPreviewTitle = tableLabelEnum[`${+btnType - 1}`].name
this.$nextTick(() => {
  this.$refs.imagePreview.open()
})
```

> `imgList` 保留作为传给 `ImagePreview` 的 prop，不再自己维护 `imgListUrl`（由组件内 computed 派生）。

### 影响范围

- 仅 `edit.vue` 自身的装卸货/签收附件预览功能
- `SettlementInfo`（含 `WeighBillCarousel`）使用独立的 `ImagePreview` 实例，互不干扰

### 边界情况

| 场景 | 预期行为 |
|---|---|
| 接口返回 succeed=false 或 model 为空 | `.then` 里 `if` 不进入，`imgList` 不更新，不调用 open()，用户无任何反馈（现有行为，不变） |
| imgList 为空时调用 open() | `ImagePreview` 内 imgListUrl 为 []，el-image-x 展示空状态，不崩溃 |
| 快速连续点击多张图的按钮 | 每次 `handleLookImg` 都覆盖 imgList，open() 展示最新结果，无竞态问题（现有行为，不变）|
| `controlBtn.btnDownload` 为 false | showDownBtn=false 传入组件，下载按钮不显示 |

### 验证

- [ ] 点击表格"装货"按钮，全屏预览弹出，显示装货附件图片
- [ ] 点击表格"卸货"按钮，全屏预览弹出，显示卸货附件图片
- [ ] 点击表格"签收"按钮，全屏预览弹出，显示签收附件图片
- [ ] 翻页时顶部 title 正常更新（显示图片 label）
- [ ] `controlBtn.btnDownload=false` 时下载按钮不显示
- [ ] 保存、提交等其他功能不受影响

---

## WS-4 — 改造 `read.vue`

**依赖**：WS-1 完成（可与 WS-3 并行）
**状态**：⬜

### 删除内容

**模板**（L169-187，整块注释）：
```vue
<!-- [WS-4] 已由 ImagePreview 组件替代 -->
<!-- <el-image-x v-show="false" ref="previewRef" ...> ... </el-image-x> -->
```

**data**（3 项，L382）：
```js
// [WS-4] 下沉至 ImagePreview 组件
// imgList: [],
// imgListUrl: [],
// urlTxt: '',
```

**方法**（4 个，L470-480）：
```js
// [WS-4] 下沉至 ImagePreview 组件
// getUrlTxt(index) { ... }
// clickHandlerUnLoad(index) { ... }
// prevLoadImg(index) { ... }
// nextLoadImg(index) { ... }
```

**样式**（`.img-view-item-tip`，整块注释）

### 新增 / 修改内容

WS-3 完全一致，参考 WS-3 执行。

**模板替换位置**：`</div>` 闭合标签（L188）之前，原 `el-image-x` 所在位置。

**`handleLookImg` 修改**：同 WS-3。

### 影响范围 / 边界情况

同 WS-3。

### 验证

- [ ] 同 WS-3 验证清单
- [ ] read 页面只读，无保存/提交按钮，确认不受影响

---

## 执行顺序

```
1. WS-1  新建 ImagePreview.vue，本地验证组件基本功能
2. WS-2  改造 WeighBillCarousel.vue，在 SettlementInfo 页面验证磅单预览
3. WS-3  改造 edit.vue，验证装卸货附件预览
4. WS-4  改造 read.vue，验证同上
```

WS-2 / WS-3 / WS-4 互不依赖，可任意顺序执行，但建议按上述顺序逐一验证。

---

## 整体风险点

| 风险 | 说明 | 规避 |
|---|---|---|
| el-image-x 的 initial-index 行为 | edit/read 原来无 initial-index，始终从第 0 张开始，改后 open() 默认传 0，行为一致 | 验证时确认第一张图正确 |
| imgList 仍在 edit/read data 中 | imgList 作为 images prop 的数据源保留，不删除，只删除 imgListUrl/urlTxt | 命名不冲突，不影响 |
| WeighBillCarousel 删除 syncImgList | syncImgList 只在组件内部调用，删除后 images 直接赋值即可 | 确认无外部调用 |
| @update 事件链 | WeighBillCarousel 监听 ImagePreview 的 update emit → 触发 handleImageSaved → 重新拉图 → images prop 更新 | 验证旋转保存后缩略图刷新 |

---

**文档版本**: v2.0
**最后更新**: 2026年07月
**整理人**: 王新骏
