# ESP8266 AI 灯控 Hook

[English](./README.en.md)

这是一个用 `ESP8266` 三色交通灯给 `Codex` 和 `Claude Code` 做硬件状态提示的项目。

设备作为 TCP 服务端监听 `192.168.1.88:8899`。本地 hook 脚本发送一个大写字母命令，ESP8266 收到后立即切换红、黄、绿灯状态。

## 项目用途

- 把 AI agent 的工作状态变成可见灯光
- 支持 `Codex` 项目级 hooks
- 支持 `Claude Code` hooks
- 协议简单，改 hook 字母即可切换已内置灯效
- 发送端带 ACK 和重试，提升状态更新成功率

## 当前示例映射

仓库里的默认示例映射是：

- `SessionStart -> E`
- `UserPromptSubmit -> Q`
- `PermissionRequest -> G`
- `Stop -> A`

对应效果是：

- `E`：黄灯加速闪，表示待命
- `Q`：红黄绿交替，表示运行中
- `G`：红灯常亮，表示等待审批
- `A`：绿灯常亮，表示当前回合结束

## 上电行为

- 上电后开始连接 Wi‑Fi 时，按当前待命灯效闪烁
- 成功连上 Wi‑Fi 后，红黄绿三灯会一起闪 `5` 下
- 提示结束后，进入默认待命状态

## 硬件

- 开发板：`NodeMCU 1.0 (ESP-12E Module)`
- 灯模块：共阴极红黄绿交通灯模块

### 接线

- `R -> D1`
- `Y -> D2`
- `G -> D3`
- `GND -> GND`

## 默认网络配置

- Wi-Fi SSID：`TP-LINK_2.4bbt`
- Wi-Fi 密码：`123584679`
- 设备 IP：`192.168.1.88`
- TCP 端口：`8899`

## 灯光协议

协议使用单个大写字母表示一种灯效方案。

加速闪和交替类方案使用统一加速规则：

- 初始步进间隔：`300ms`
- 每 `1` 秒减少 `1ms`
- 最短收敛到：`30ms`

慢闪方案使用固定频率：

- 步进间隔：`500ms`
- 完整亮灭周期：`1000ms`

### 常亮方案

- `A`：绿灯常亮
- `D`：黄灯常亮
- `G`：红灯常亮
- `T`：全灭
- `U`：全亮

### 闪烁方案

- `B`：绿灯加速闪
- `C`：绿灯慢闪
- `E`：黄灯加速闪
- `F`：黄灯慢闪
- `H`：红灯加速闪
- `I`：红灯慢闪
- `V`：三灯同步加速闪
- `W`：三灯同步慢闪

### 交替方案

- `J`：红绿交替
- `L`：红黄交替
- `N`：黄绿交替
- `Q`：红黄绿交替
- `R`：绿黄红交替


## 快速开始

### 1. 烧录固件

在 Arduino IDE 中打开：

`firmware/esp8266_ai_light_hook/esp8266_ai_light_hook.ino`

推荐开发板设置：

- `NodeMCU 1.0 (ESP-12E Module)`

### 2. 测试发送脚本

Linux 下执行：

```bash
chmod +x send-light.sh
./send-light.sh E
./send-light.sh Q
./send-light.sh A
```

如果设备 IP 或端口不同：

```bash
./send-light.sh Q 192.168.1.88 8899
```

### 3. 启用 Hook

Codex 示例：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./send-light.sh E"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ./send-light.sh Q"
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./send-light.sh G"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ./send-light.sh A"
          }
        ]
      }
    ]
  }
}
```

## 可靠性设计

- 发送端必须收到 `OK\n`
- 发送失败会自动重试 `3` 次
- 非法字母会返回 `ERR\n`
- ESP8266 会在 `1500ms` 后回收空闲客户端

## 仓库结构

- `firmware/esp8266_ai_light_hook/`：ESP8266 固件
- `tests/`：协议和 hook 校验脚本
- `docs/linux-codex-claude-light-hooks-tutorial.md`：Linux 配置教程
- `.codex/hooks.json`：Codex hook 示例
- `.claude/settings.json`：Claude Code hook 示例
- `send-light.sh`：Linux 发送脚本
- `docs/archive/superpowers/`：归档的内部计划和设计文档

## 说明

- 当前 Codex 方案表达的是生命周期状态，不是进程退出码
- 只要目标字母已经内置在固件里，切换 hook 字母不需要重新刷机
- 只有新增全新灯效时，才需要更新固件
