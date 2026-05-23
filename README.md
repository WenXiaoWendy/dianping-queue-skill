<div align="center">

# 大众点评取号 Skill 绿色安全版

完全模拟用户手工操作的自动化浏览器取号 skill，无任何不良引导和违规行为。

大众点评前端页面经常更新；请收藏该 skill，如果未来变得不可用，请联系作者更新并获取最新版本。

[![License](https://img.shields.io/badge/License-Personal%20Use%20Only-red)](LICENSE)
![中文用户](https://img.shields.io/badge/用户-中文-blue)
![本地优先](https://img.shields.io/badge/模式-本地优先-brightgreen)
![macOS](https://img.shields.io/badge/环境-macOS-lightgrey)
![Ubuntu/Linux](https://img.shields.io/badge/环境-Ubuntu%20%2F%20Linux-lightgrey)
![Playwright](https://img.shields.io/badge/浏览器-Playwright-2ea44f)

</div>

这个 skill 面向中文用户，用于让 agent 辅助处理大众点评排队取号相关任务。公开仓库只包含 skill 外壳和安装入口，核心浏览器自动化逻辑由闭源 helper 提供。

## 使用场景

1. **定时取号**  
   让 agent 在指定时间自动打开取号页，并按页面流程取号。

2. **定时查看已排桌数，达到条件再取号**  
   让 agent 按用户指定的频率查看当前排队状态；未达到用户设定阈值时不打扰，达到后自动进入取号流程。

3. **取号成功后持续刷新桌数，到点提醒出发**  
   取号成功后，让 agent 按用户指定的频率查看前方等待桌数；当桌数下降到用户设定值时，提醒用户可以出发。

> **重要：对于第一次取号的店铺，建议直接发送大众点评分享链接。**  
> 这样可以跳过浏览器搜索步骤，直接获取店铺 ID，省下不必要的 token 消耗。已经取过号的店铺会写入本地缓存，之后可以直接报店铺名。

<table>
  <tr>
    <td width="33%" align="center">
      <img src="assets/setup-phone-city.png" alt="首次安装配置手机和城市" width="100%">
    </td>
    <td width="33%" align="center">
      <img src="assets/sms-login.png" alt="首次取号需使用短信验证码登录" width="100%">
    </td>
    <td width="33%" align="center">
      <img src="assets/threshold-queue.png" alt="设定触发条件的动态取号场景" width="100%">
    </td>
  </tr>
  <tr>
    <td align="center">首次安装配置手机和城市</td>
    <td align="center">首次取号需使用短信验证码登录</td>
    <td align="center">设定触发条件的动态取号场景</td>
  </tr>
</table>

## 安装

```bash
python3 scripts/setup_runtime.py
```

本地桌面用户默认只需要配置手机号。浏览器连接、持久化会话和 helper 更新由 skill 自动处理。

## 环境要求

- macOS 或 Ubuntu/Linux。
- 可用的本地 Chrome，或云端/服务器环境中的 Playwright Chromium。
- 可接收短信验证码的手机号。
- Windows 暂不作为目标环境。

## 更新

```bash
git pull
python3 scripts/setup_runtime.py
```

`setup_runtime.py` 会根据 `helper-manifest.json` 检查 helper 版本并下载对应平台的最新文件。

## 授权说明

本项目允许个人安装和自用，但不允许复制改发、商用、托管服务、训练数据集使用或二次分发；使用前请阅读 [LICENSE](LICENSE)。
