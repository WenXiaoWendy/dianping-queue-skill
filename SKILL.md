---
name: dianping-queue
description: 面向中文用户的大众点评取号 skill。用于解析取号页、一次性读取排队桌数、按正常浏览器流程取号，以及在 agent 被定时唤醒后按用户阈值取号或提醒出发。
---

# 大众点评取号

这个 skill 只处理大众点评排队取号相关任务。触发意图包括：

- 帮我取号、排号、打开点评取号页
- 定时看这家店排了多少桌
- 超过 N 桌再帮我取号
- 取号成功后盯着前面还有几桌，少于 N 桌提醒我出发

## 核心要求

- 必须完全按照本 skill 的流程和脚本执行，不要自行设计替代流程。
- 全程不要向用户汇报中间步骤。
- 只有遇到需要用户确认的断点、需要短信验证码、浏览器验证、多个候选选择、或脚本错误 / 业务失败时，才向用户汇报并等待用户输入。
- 向用户输出时必须使用“标准回复格式”，不要自由发挥，不要输出脚本 JSON、运行日志、字段清单或多余解释。

## 标准回复格式

取号成功：

```text
已取号成功：<店名>
桌号：<tableNumDesc>
前方等待：<queueWaitTableNum> 桌
人数：<peopleCount> 人
```

只看状态：

```text
当前排队：<店名>
状态：<queueStatusText>
总等待：<queue.totalWaitCount 或 queue.queueWaitTableNum> 桌
桌型：
- <tableTypeName>（<tableCapacityDesc>）：<waitCount> 桌
```

取号后提醒出发：

```text
可以出发了：<店名>
前方等待：<queueWaitTableNum> 桌
```

多个候选：

```text
找到多个可能的门店，请回复编号：
1. <店名>｜<地址>
2. <店名>｜<地址>
```

需要短信验证码：

```text
请输入短信验证码。
```

需要浏览器验证：

```text
请在打开的浏览器页面完成验证，完成后告诉我继续。
```

需要定时检查频率：

```text
请告诉我多久查一次排队进度。
```

业务不可用或错误：

```text
无法完成：<原因>
```

常见业务原因直接使用页面或脚本返回的 `reason` / `blocker` / `queue.queueStatusText` / `queue.queueStatusSubText`。如果同时有主文案和副文案，格式为：

```text
无法完成：<主文案>：<副文案>
```

## 执行边界

- 只使用本 skill 的脚本入口；店名 / 地址解析先走本地缓存，缓存缺失时走 `browser-search`。
- 搜索、状态读取和取号都必须通过正常浏览器页面流程操作。
- 不要自行拼接口搜索，不要直接调用最终取号请求，不要绕过前端。
- 状态读取脚本只执行一次读取，不常驻轮询。定时唤醒由 agent 所在环境的自动化、定时任务或提醒系统负责。
- 阈值取号和取号后提醒出发场景中，必须先确认用户希望多久查一次排队进度。
- 未达到阈值时静默结束，不要向用户报数。
- 用户未提供人数时默认 `2` 人。
- 本地用户默认只需配置手机号；浏览器参数由脚本处理。
- 脚本返回 `verification_required` 时，立刻停止当前流程并向用户索要验证码。用户给出验证码后，原命令追加 `--sms-code "<SMS_CODE>"` 续跑。

## 命令

命令中的 `<SKILL_DIR>` 表示这个 skill 的安装目录。

安装或更新 helper：

```bash
python3 "<SKILL_DIR>/scripts/setup_runtime.py"
```

店名、地址或商场名解析：

```bash
python3 "<SKILL_DIR>/scripts/queue_context.py" resolve --target "<店名、地址或缓存别名>"
```

缓存缺失时走浏览器搜索：

```bash
python3 "<SKILL_DIR>/scripts/queue_context.py" browser-search --query "<店名或地址>" --city "<城市>"
```

确认搜索候选：

```bash
python3 "<SKILL_DIR>/scripts/queue_context.py" confirm-search --index "<编号>"
```

取号：

```bash
python3 "<SKILL_DIR>/scripts/queue_context.py" take --target "<店名、缓存别名、candidateId 或取号 URL>" --party-size 2
```

只读取状态：

```bash
python3 "<SKILL_DIR>/scripts/queue_context.py" status --target "<店名、缓存别名、candidateId 或取号 URL>" --party-size 2
```

分享页入库并取号：

```bash
python3 "<SKILL_DIR>/scripts/queue_context.py" from-share --share-url "<大众点评分享链接>" --party-size 2
```

按订单页 URL 查看前方桌数：

```bash
python3 "<SKILL_DIR>/scripts/queue_context.py" status --order-url "<订单页 URL>"
```

## 候选和断点

- `candidates` 只有 1 个：直接运行 `confirm-search`。
- `candidates` 有多个：向用户展示候选编号，让用户回复编号后再继续。
- 用户回复编号后，不要复用上一页，不要重新搜索；直接用该编号运行 `confirm-search --index "<编号>"`。
- 如果返回 `browser_verification_required`，让用户在浏览器页面完成验证；完成后重新运行同一条命令。
- 如果返回 `verification_required`，让用户提供短信验证码后续跑同一命令并追加 `--sms-code "<SMS_CODE>"`。
