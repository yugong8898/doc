# 技术雷达自动化说明

## 目录

- [一、目标](#一目标)
- [二、试运行规则](#二试运行规则)
- [三、执行方式](#三执行方式)
- [四、手动执行](#四手动执行)
- [五、安装定时任务](#五安装定时任务)
- [六、卸载定时任务](#六卸载定时任务)
- [七、三天后复盘](#七三天后复盘)
- [八、注意事项](#八注意事项)

## 一、目标

每天从固定来源检索前端、AI Coding、开发工具链、监控、埋点等信息，筛选后生成 Markdown，沉淀到 `docs/tech-radar/daily/`。

## 二、试运行规则

- 执行时间：工作日上午 10:00
- 试运行周期：先执行 3 个工作日
- 输出方式：生成 Markdown，不自动提交 Git
- 复盘方式：三次结果出来后，根据质量调整来源、关键词、排除规则

## 三、执行方式

自动化由两部分组成：

1. `scripts/tech-radar/tech_radar.py`：读取 RSS / Feed，按关键词筛选，追加到月度 Markdown。
2. `docs/tech-radar/launchd/com.wlyd.tech-radar.plist`：macOS `launchd` 定时任务模板。

## 四、手动执行

在项目根目录执行：

```bash
python3 scripts/tech-radar/tech_radar.py
```

可指定日期：

```bash
python3 scripts/tech-radar/tech_radar.py --date 2026-07-23
```

## 五、安装定时任务

> 当前 AI 执行环境无法直接写入 `~/Library/LaunchAgents` 时，请在你的本机终端中执行以下命令。

推荐使用安装脚本：

```bash
chmod +x scripts/tech-radar/install-launchd.sh scripts/tech-radar/uninstall-launchd.sh
scripts/tech-radar/install-launchd.sh
```

也可以手动将模板复制到用户 LaunchAgents 目录：

```bash
cp docs/tech-radar/launchd/com.wlyd.tech-radar.plist ~/Library/LaunchAgents/com.wlyd.tech-radar.plist
```

加载任务：

```bash
launchctl load ~/Library/LaunchAgents/com.wlyd.tech-radar.plist
```

查看任务：

```bash
launchctl list | grep com.wlyd.tech-radar
```

## 六、卸载定时任务

三天试运行结束或需要暂停时，推荐执行卸载脚本：

```bash
scripts/tech-radar/uninstall-launchd.sh
```

也可以手动执行：

```bash
launchctl unload ~/Library/LaunchAgents/com.wlyd.tech-radar.plist
rm ~/Library/LaunchAgents/com.wlyd.tech-radar.plist
```

## 七、三天后复盘

复盘时重点看：

- 来源质量是否稳定。
- 是否有过多营销、转载、无关内容。
- Vue2 / Vue3 / React / AI Coding / 监控 / 埋点相关信息是否足够。
- 是否需要增加中文来源或官方来源。
- 是否需要自动提交 Git。

复盘后调整：

- `topics.md`：新增或降低关键词优先级。
- `sources.md`：调整来源。
- `exclude-rules.md`：补充排除规则。
- `tech_radar.py`：调整筛选逻辑。

## 八、注意事项

- 当前脚本不自动提交 Git。
- 网络不可用或全部来源抓取失败时会写入错误提示到日志，不计入三天试运行次数。
- 自动任务只负责追加每日结果，不负责把内容迁入 `.repoWiki/`。
- 外部信息进入正式项目知识库前，必须先确认其适用于 WLYD。

---

**文档版本**: v1.0  
**最后更新**: 2026年07月  
**整理人**: 王新骏
