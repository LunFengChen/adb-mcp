# ADB MCP Server

Android Debug Bridge (ADB) 的 MCP 服务器，提供完整的 Android 设备管理能力。

## 功能特性

- **设备管理**: 列出设备、获取设备信息
- **应用管理**: 安装、卸载、启动、停止、清除数据、获取路径/UID/PID
- **文件传输**: 推送、拉取、列出文件
- **系统信息**: 电池、内存、存储、屏幕尺寸/密度、Android ID、IP/MAC地址
- **屏幕操作**: 截屏、录屏
- **输入模拟**: 文本输入、按键、点击、滑动
- **日志调试**: 获取设备日志、应用日志、清除日志
- **端口转发**: forward/reverse 端口转发（Frida/调试常用）
- **Shell命令**: 普通shell和root shell执行
- **多设备支持**: 同时管理多个Android设备

## 环境要求

1. **Android SDK Platform Tools**: 确保 `adb` 命令在 PATH 中
2. **Python 3.10+**
3. **Android 设备**: USB连接并开启USB调试

## 安装

```bash
git clone https://github.com/zhizhuodemao/adb-mcp
cd adb-mcp
pip install -r requirements.txt
```

## 使用

### 启动服务器
```bash
python fastmcp_server.py
```

### MCP 配置示例

```json
"adb-mcp": {
  "command": "python",
  "args": ["path/to/fastmcp_server.py"],
  "disabled": false,
  "autoApprove": [
    "list_devices", "get_device_info", "install_app", "uninstall_app",
    "list_packages", "start_app", "stop_app", "clear_app_data",
    "get_current_activity", "get_app_path", "get_app_uid", "get_pid",
    "get_app_logcat", "push_file", "pull_file", "list_files",
    "get_battery_info", "get_memory_info", "get_storage_info",
    "get_android_id", "get_screen_size", "get_screen_density",
    "get_ip_address", "get_mac_address", "take_screenshot", "record_screen",
    "send_text", "send_keyevent", "send_tap", "send_swipe",
    "get_logcat", "clear_logcat", "shell", "shell_root",
    "forward_port", "forward_remove", "forward_list",
    "reverse_port", "reverse_remove", "reverse_list"
  ]
}
```

## 工具列表 (40个)

### 设备管理 (2)
- `list_devices` - 列出连接的设备
- `get_device_info` - 获取设备详细信息

### 应用管理 (11)
- `install_app` - 安装APK
- `uninstall_app` - 卸载应用
- `list_packages` - 列出已安装应用
- `start_app` - 启动应用
- `stop_app` - 强制停止应用
- `clear_app_data` - 清除应用数据
- `get_current_activity` - 获取当前前台Activity
- `get_app_path` - 获取应用安装路径
- `get_app_uid` - 获取应用UID
- `get_pid` - 获取应用PID
- `get_app_logcat` - 获取指定应用日志

### 文件传输 (3)
- `push_file` - 推送文件到设备
- `pull_file` - 从设备拉取文件
- `list_files` - 列出设备文件

### 系统信息 (9)
- `get_battery_info` - 电池信息
- `get_memory_info` - 内存信息
- `get_storage_info` - 存储信息
- `get_android_id` - Android ID
- `get_screen_size` - 屏幕尺寸
- `get_screen_density` - 屏幕密度
- `get_ip_address` - IP地址
- `get_mac_address` - MAC地址

### 屏幕操作 (2)
- `take_screenshot` - 截屏
- `record_screen` - 录屏

### 输入模拟 (4)
- `send_text` - 发送文本
- `send_keyevent` - 发送按键
- `send_tap` - 发送点击
- `send_swipe` - 发送滑动

### 日志调试 (2)
- `get_logcat` - 获取日志
- `clear_logcat` - 清除日志

### Shell命令 (2)
- `shell` - 执行shell命令
- `shell_root` - 以root权限执行（支持自定义su，如sx）

### 端口转发 (6)
- `forward_port` - 端口转发 (本地→设备)
- `forward_remove` - 移除端口转发
- `forward_list` - 列出端口转发
- `reverse_port` - 反向端口转发 (设备→本地)
- `reverse_remove` - 移除反向端口转发
- `reverse_list` - 列出反向端口转发

## 常用按键代码

| 代码 | 按键 | 代码 | 按键 |
|-----|------|-----|------|
| 3 | Home | 4 | 返回 |
| 24 | 音量+ | 25 | 音量- |
| 26 | 电源 | 66 | 回车 |
| 67 | 删除 | 82 | 菜单 |

## 故障排除

- **ADB not found**: 安装 Android SDK platform-tools 并添加到 PATH
- **No devices**: 检查USB连接和调试授权
- **Permission denied**: 在设备上授权此计算机
