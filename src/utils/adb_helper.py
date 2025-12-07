import subprocess
from typing import List, Dict, Optional, Tuple


class ADBHelper:
    """ADB命令封装类"""

    @staticmethod
    def run_adb_command(command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """执行ADB命令"""
        try:
            result = subprocess.run(
                ['adb'] + command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except FileNotFoundError:
            return False, "", "ADB not found. Please install Android SDK platform-tools"
        except Exception as e:
            return False, "", str(e)

    @staticmethod
    def list_devices() -> List[Dict[str, str]]:
        """列出连接的设备"""
        success, stdout, stderr = ADBHelper.run_adb_command(['devices', '-l'])
        if not success:
            return []

        devices = []
        lines = stdout.split('\n')[1:]
        for line in lines:
            if line.strip() and not line.startswith('*'):
                parts = line.split()
                if len(parts) >= 2:
                    device_info = {'id': parts[0], 'status': parts[1]}
                    for part in parts[2:]:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            device_info[key] = value
                    devices.append(device_info)
        return devices

    @staticmethod
    def get_device_info(device_id: Optional[str] = None) -> Dict[str, str]:
        """获取设备详细信息"""
        cmd = ['shell', 'getprop']
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if not success:
            return {'error': stderr}

        info = {}
        for line in stdout.split('\n'):
            if line.strip() and line.startswith('[') and ']:' in line:
                try:
                    key_end = line.find(']:')
                    key = line[1:key_end]
                    value = line[key_end + 3:].strip()
                    if value.startswith('[') and value.endswith(']'):
                        value = value[1:-1]
                    info[key] = value
                except:
                    continue
        return info

    # ==================== 应用管理方法 ====================

    @staticmethod
    def install_app(apk_path: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """安装APK应用"""
        cmd = ['install', apk_path]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd, timeout=120)

    @staticmethod
    def uninstall_app(package_name: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """卸载应用"""
        cmd = ['uninstall', package_name]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def list_packages(device_id: Optional[str] = None, system_apps: bool = False) -> List[str]:
        """列出已安装的应用包"""
        cmd = ['shell', 'pm', 'list', 'packages']
        if not system_apps:
            cmd.append('-3')
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if not success:
            return []

        packages = []
        for line in stdout.split('\n'):
            if line.startswith('package:'):
                packages.append(line.replace('package:', '').strip())
        return packages

    @staticmethod
    def start_app(package_name: str, activity: str = "", device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """启动应用"""
        if activity:
            cmd = ['shell', 'am', 'start', '-n', f'{package_name}/{activity}']
        else:
            cmd = ['shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def stop_app(package_name: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """强制停止应用"""
        cmd = ['shell', 'am', 'force-stop', package_name]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def clear_app_data(package_name: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """清除应用数据"""
        cmd = ['shell', 'pm', 'clear', package_name]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def get_current_activity(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取当前前台Activity"""
        cmd = ['shell', 'dumpsys', 'window', 'windows']
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if success:
            for line in stdout.split('\n'):
                if 'mCurrentFocus' in line or 'mFocusedApp' in line:
                    return True, line.strip(), ""
        return False, "", stderr or "无法获取当前Activity"

    @staticmethod
    def get_app_path(package_name: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取应用安装路径"""
        cmd = ['shell', 'pm', 'path', package_name]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def get_app_uid(package_name: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取应用UID"""
        cmd = ['shell', 'dumpsys', 'package', package_name]
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if success:
            for line in stdout.split('\n'):
                if 'userId=' in line:
                    return True, line.strip(), ""
        return False, "", stderr or "无法获取UID"

    @staticmethod
    def get_pid(package_name: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取应用进程PID"""
        cmd = ['shell', 'pidof', '-s', package_name]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def get_app_logcat(package_name: str, lines: int = 100, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取指定应用的日志"""
        pid_success, pid, _ = ADBHelper.get_pid(package_name, device_id)
        if not pid_success or not pid.strip():
            return False, "", f"无法获取 {package_name} 的PID，应用可能未运行"

        cmd = ['logcat', '-d', '--pid=' + pid.strip(), '-t', str(lines)]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd, timeout=60)

    # ==================== 文件传输方法 ====================

    @staticmethod
    def push_file(local_path: str, remote_path: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """推送文件到设备"""
        cmd = ['push', local_path, remote_path]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd, timeout=300)

    @staticmethod
    def pull_file(remote_path: str, local_path: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """从设备拉取文件"""
        cmd = ['pull', remote_path, local_path]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd, timeout=300)

    @staticmethod
    def list_files(remote_path: str, device_id: Optional[str] = None) -> List[Dict[str, str]]:
        """列出设备上的文件"""
        cmd = ['shell', 'ls', '-la', remote_path]
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if not success:
            return []

        files = []
        for line in stdout.split('\n'):
            if line.strip() and not line.startswith('total'):
                parts = line.split()
                if len(parts) >= 8:
                    try:
                        files.append({
                            'permissions': parts[0],
                            'links': parts[1],
                            'owner': parts[2],
                            'group': parts[3],
                            'size': parts[4],
                            'date': f"{parts[5]} {parts[6]}",
                            'name': ' '.join(parts[7:])
                        })
                    except IndexError:
                        continue
        return files


    # ==================== 系统信息方法 ====================

    @staticmethod
    def get_battery_info(device_id: Optional[str] = None) -> Dict[str, str]:
        """获取电池信息"""
        cmd = ['shell', 'dumpsys', 'battery']
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if not success:
            return {'error': stderr}

        battery_info = {}
        for line in stdout.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('Current Battery Service state'):
                try:
                    key, value = line.split(':', 1)
                    battery_info[key.strip()] = value.strip()
                except:
                    continue
        return battery_info

    @staticmethod
    def get_memory_info(device_id: Optional[str] = None) -> Dict[str, str]:
        """获取内存信息"""
        cmd = ['shell', 'cat', '/proc/meminfo']
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if not success:
            return {'error': stderr}

        memory_info = {}
        for line in stdout.split('\n'):
            if ':' in line:
                try:
                    key, value = line.split(':', 1)
                    memory_info[key.strip()] = value.strip()
                except:
                    continue
        return memory_info

    @staticmethod
    def get_storage_info(device_id: Optional[str] = None) -> List[Dict[str, str]]:
        """获取存储信息"""
        cmd = ['shell', 'df', '-h']
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if not success:
            return []

        storage_info = []
        lines = stdout.split('\n')[1:]
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 6:
                    storage_info.append({
                        'filesystem': parts[0],
                        'size': parts[1],
                        'used': parts[2],
                        'available': parts[3],
                        'use_percent': parts[4],
                        'mounted_on': ' '.join(parts[5:])
                    })
        return storage_info

    @staticmethod
    def get_android_id(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取android_id"""
        cmd = ['shell', 'settings', 'get', 'secure', 'android_id']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def get_screen_size(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取屏幕尺寸"""
        cmd = ['shell', 'wm', 'size']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def get_screen_density(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取屏幕密度"""
        cmd = ['shell', 'wm', 'density']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def get_ip_address(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取设备IP地址"""
        cmd = ['shell', 'ifconfig', 'wlan0']
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if not success:
            cmd = ['shell', 'ip', 'addr', 'show', 'wlan0']
            if device_id:
                cmd = ['-s', device_id] + cmd
            success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        return success, stdout, stderr

    @staticmethod
    def get_mac_address(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取MAC地址"""
        cmd = ['shell', 'cat', '/sys/class/net/wlan0/address']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    # ==================== 屏幕操作方法 ====================

    @staticmethod
    def take_screenshot(save_path: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """截屏"""
        if not save_path or not save_path.strip():
            return False, "", "save_path is required"
        remote_path = "/sdcard/screenshot.png"

        cmd = ['shell', 'screencap', '-p', remote_path]
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd)
        if not success:
            return False, "", stderr
        return ADBHelper.pull_file(remote_path, save_path, device_id)

    @staticmethod
    def record_screen(duration: int = 10, save_path: str = "", device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """录屏"""
        remote_path = "/sdcard/screenrecord.mp4"
        cmd = ['shell', 'screenrecord', '--time-limit', str(duration), remote_path]
        if device_id:
            cmd = ['-s', device_id] + cmd

        success, stdout, stderr = ADBHelper.run_adb_command(cmd, timeout=duration + 30)
        if not success:
            return False, "", stderr

        if save_path:
            return ADBHelper.pull_file(remote_path, save_path, device_id)
        return True, f"Screen recording saved to device: {remote_path}", ""

    # ==================== 输入模拟方法 ====================

    @staticmethod
    def send_text(text: str, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """发送文本输入"""
        escaped_text = text.replace(' ', '%s').replace('&', '\\&')
        cmd = ['shell', 'input', 'text', escaped_text]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def send_keyevent(keycode: int, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """发送按键事件"""
        cmd = ['shell', 'input', 'keyevent', str(keycode)]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def send_tap(x: int, y: int, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """发送点击事件"""
        cmd = ['shell', 'input', 'tap', str(x), str(y)]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def send_swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 300, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """发送滑动事件"""
        cmd = ['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    # ==================== 日志方法 ====================

    @staticmethod
    def get_logcat(filter_tag: str = "", lines: int = 100, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """获取logcat日志"""
        cmd = ['logcat', '-d']
        if lines > 0:
            cmd.extend(['-t', str(lines)])
        if filter_tag:
            cmd.append(f"{filter_tag}:*")
            cmd.append("*:S")
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd, timeout=60)

    @staticmethod
    def clear_logcat(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """清除logcat日志"""
        cmd = ['logcat', '-c']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    # ==================== Shell 命令方法 ====================

    @staticmethod
    def shell(command: str, device_id: Optional[str] = None, timeout: int = 30) -> Tuple[bool, str, str]:
        """执行 shell 命令"""
        cmd = ['shell', command]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd, timeout=timeout)

    @staticmethod
    def shell_root(command: str, su_binary: str = "su", device_id: Optional[str] = None, timeout: int = 30) -> Tuple[bool, str, str]:
        """以 root 权限执行 shell 命令"""
        root_cmd = f'{su_binary} -c "{command}"'
        cmd = ['shell', root_cmd]
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd, timeout=timeout)

    # ==================== 端口转发方法 ====================

    @staticmethod
    def forward_port(local_port: int, remote_port: int, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """端口转发（本地到设备）"""
        cmd = ['forward', f'tcp:{local_port}', f'tcp:{remote_port}']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def forward_remove(local_port: int, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """移除端口转发"""
        cmd = ['forward', '--remove', f'tcp:{local_port}']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def forward_list(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """列出所有端口转发"""
        cmd = ['forward', '--list']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def reverse_port(remote_port: int, local_port: int, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """反向端口转发（设备到本地）"""
        cmd = ['reverse', f'tcp:{remote_port}', f'tcp:{local_port}']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def reverse_remove(remote_port: int, device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """移除反向端口转发"""
        cmd = ['reverse', '--remove', f'tcp:{remote_port}']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)

    @staticmethod
    def reverse_list(device_id: Optional[str] = None) -> Tuple[bool, str, str]:
        """列出所有反向端口转发"""
        cmd = ['reverse', '--list']
        if device_id:
            cmd = ['-s', device_id] + cmd
        return ADBHelper.run_adb_command(cmd)
