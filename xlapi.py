from ast import main
import ctypes
import os
import time
import threading
from xltype import *

xl = None
port_handle = ctypes.c_long(XL_INVALID_PORTHANDLE)
access_mask = ctypes.c_uint64(0x01)
permission_mask = ctypes.c_uint64(0)
notification_handle = None  # 全局通知句柄

def load_dll():
    global xl
    # 加载vxlapi.dll
    try:
        # 尝试从系统目录加载
        xl = ctypes.WinDLL("vxlapi64.dll")
        print("load xl driver success")
    except:
        print("load xl driver error")

def open_driver():
    XLStatus = xl.xlOpenDriver()
    print(f"open driver: {XLStatus}")

def set_app_config():
    # 创建ctypes变量
    app_name = ctypes.create_string_buffer(b"app2")
    hw_type = ctypes.c_uint(1)  # 虚拟设备
    hw_index = ctypes.c_uint(0) 
    hw_channel = ctypes.c_uint(0)

    XLStatus = xl.xlSetApplConfig(
        app_name,           # char* appName
        0,                  # unsigned int appChannel
        ctypes.byref(hw_type),    # unsigned int* pHwType
        ctypes.byref(hw_index),   # unsigned int* pHwIndex  
        ctypes.byref(hw_channel), # unsigned int* pHwChannel
        1                   # CAN
    )
    print(f"set app config: {XLStatus}")
    # print(f"Error String: {xl.xlGetErrorString(XLStatus)}")

    # 打印返回的硬件信息
    if XLStatus == 0:  # 成功
        print(f"Hardware Type: {hw_type.value}")
        print(f"Hardware Index: {hw_index.value}")
        print(f"Hardware Channel: {hw_channel.value}")

def print_driver_config():
    # 创建驱动配置结构体
    driver_config = init_xldriverconfig()

    # 获取驱动配置
    XLStatus = xl.xlGetDriverConfig(ctypes.byref(driver_config))
    print(f"get driver config: {XLStatus}")

    # 打印驱动配置信息
    if XLStatus == 0:  # 成功
        print_xldriverconfig(driver_config)

def print_channel_info():
    idx = xl.xlGetChannelIndex(1, 0, 0)
    print(f"channel idx: {idx}")
    mask = xl.xlGetChannelMask(1, 0, 0)
    print(f"channel mask: {mask}")

def open_port():
    # 打开端口
    XLStatus = xl.xlOpenPort(
        ctypes.byref(port_handle),    # XLportHandle* pPortHandle
        b"app1",                     # char* userName
        access_mask,                 # XLaccess accessMask (使用所有通道)
        ctypes.byref(permission_mask), # XLaccess* pPermissionMask
        1000,                        # unsigned int rxQueueSize
        XL_INTERFACE_VERSION_V3,     # unsigned int xlInterfaceVersion
        XL_BUS_TYPE_CAN              # unsigned int busType
    )

    print(f"open port status: {XLStatus}")
    # print(f"Error String: {xl.xlGetErrorString(XLStatus)}")
    print(f"port handle: {port_handle.value}")
    print(f"permission mask: {permission_mask.value}")

    # 检查端口是否成功打开
    if XLStatus == 0 and port_handle.value != XL_INVALID_PORTHANDLE:
        print("端口打开成功")
    else:
        print("端口打开失败")

    # 创建通知句柄
    global notification_handle
    notification_handle = XLhandle(None)  # 初始化为空句柄
    
    XLStatus = xl.xlSetNotification(
        port_handle,                    # XLportHandle portHandle
        ctypes.byref(notification_handle), # XLhandle* pHandle
        1                               # int queueLevel - 当接收队列大于等于1时开始通知
    )
    print(f"Set Notification status: {XLStatus}")
    print(f"Notification handle: {notification_handle.value}")

def activate_channel():
    # 设置通道模式 - 传输完成和传输请求回执
    XLStatus = xl.xlCanSetChannelMode(
        port_handle,
        access_mask,
        1,      # 传输完成发回执
        0       # 传输之前发回执
    )
    print(f"set channel mode: {XLStatus}")

    # 设置接收模式 - 错误帧和芯片状态
    XLStatus = xl.xlCanSetReceiveMode(
        port_handle,        # XLportHandle Port
        0,                  # unsigned char ErrorFrame - 0=接收错误帧，1=禁止错误帧
        0                   # unsigned char ChipState - 0=接收芯片状态，1=禁止芯片状态
    )
    print(f"set receive mode: {XLStatus}")

    # 设置通道输出模式
    XLStatus = xl.xlCanSetChannelOutput(
        port_handle,        # XLportHandle portHandle
        access_mask,        # XLaccess accessMask
        XL_OUTPUT_MODE_NORMAL  # int mode - 正常模式，可以发送和接收
    )
    print(f"set channel output: {XLStatus}")

    # 激活通道
    XLStatus = xl.xlActivateChannel(
        port_handle,
        access_mask,
        XL_BUS_TYPE_CAN,              # unsigned int busType
        XL_ACTIVATE_NONE
    )
    print(f"activate_channel: {XLStatus}")

def send():
    # 创建一个CAN传输事件
    tx_event = create_can_tx_event(
        can_id=0x0001,           # CAN ID
        data=[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08],  # 8字节数据
        flags=0,
    )
    
    # 打印要发送的消息
    print("准备发送CAN消息:")
    print_can_tx_event(tx_event, 0)
    
    # 创建事件数组 - 正确的方式
    event_count = ctypes.c_uint(1)  # 发送1个事件
    event_array = (XLcanTxEvent * 1)()
    event_array[0] = tx_event
    
    XLStatus = xl.xlCanTransmit(
        port_handle,            # XLportHandle portHandle
        access_mask,            # XLaccess accessMask
        ctypes.byref(event_count), # unsigned int* pEventCount
        event_array             # void* pEvents - 传递数组，不是单个事件的引用
    )
    
    if XLStatus != 0:
        print(f"发送失败: {XLStatus}")
        # 可以调用 xl.xlGetErrorString(XLStatus) 获取错误信息
    else:
        print(f"实际发送事件数: {event_count.value}")

def wait_for_notification(timeout_ms=1000):
    """等待通知事件"""
    if notification_handle is None or notification_handle.value is None:
        print("通知句柄未初始化")
        return False
    
    # Windows WaitForSingleObject API
    kernel32 = ctypes.windll.kernel32
    WAIT_OBJECT_0 = 0
    WAIT_TIMEOUT = 0x102
    WAIT_FAILED = 0xFFFFFFFF
    
    result = kernel32.WaitForSingleObject(
        notification_handle.value,  # HANDLE hHandle
        timeout_ms                  # DWORD dwMilliseconds
    )
    
    if result == WAIT_OBJECT_0:
        print("收到通知事件")
        return True
    elif result == WAIT_TIMEOUT:
        print(f"等待超时 ({timeout_ms}ms)")
        return False
    elif result == WAIT_FAILED:
        print("等待事件失败")
        return False
    else:
        print(f"未知等待结果: {result}")
        return False

def receive_with_notification():
    """使用通知机制接收消息"""
    print("等待CAN消息通知...")
    
    # 等待通知事件
    if wait_for_notification(5000):  # 等待5秒
        # 收到通知后，读取消息
        receive()
        
        # 重置事件以便下次使用
        kernel32 = ctypes.windll.kernel32
        kernel32.ResetEvent(notification_handle.value)
        print("事件已重置")
    else:
        print("未收到通知")

def receive():
    """直接接收消息（轮询方式）"""
    cnt = ctypes.c_uint(0)
    XLStatus = xl.xlGetReceiveQueueLevel(
        port_handle,
        ctypes.byref(cnt)
    )
    print(f"ReceiveQueueLevel: {XLStatus}")
    print(f"Receive Queue size: {cnt.value}")
    if XLStatus != 0 or cnt.value == 0:
        return
    
    # 创建事件数组，使用XLevent结构体
    event_list = (XLevent * cnt.value)()  # 创建n个XLevent的数组
    XLStatus = xl.xlReceive(
        port_handle,           # XLportHandle portHandle
        ctypes.byref(cnt),     # unsigned int* pEventCount
        event_list             # XLevent* pEvents
    )
    
    print(f"receive: {XLStatus}")
    print(f"received {cnt.value} events")
    
    # 打印接收到的事件
    if XLStatus == 0 and cnt.value > 0:
        for i in range(cnt.value):
            print_xlevent(event_list[i], i)
    elif XLStatus != 0:
        print(f"receive error: {XLStatus}")
        # 可以调用 xl.xlGetErrorString(XLStatus) 获取错误信息

def close():
    global notification_handle
    
    # 清理通知句柄
    if notification_handle is not None and notification_handle.value is not None:
        kernel32 = ctypes.windll.kernel32
        kernel32.CloseHandle(notification_handle.value)
        print("通知句柄已关闭")
        notification_handle = None
    
    # 停用通道
    XLStatus = xl.xlDeactivateChannel(
        port_handle,    # XLportHandle portHandle
        access_mask     # XLaccess accessMask
    )
    print(f"deactivate channel: {XLStatus}")
    
    # 关闭端口
    XLStatus = xl.xlClosePort(port_handle)
    print(f"close port: {XLStatus}")
    
    # 关闭驱动
    XLStatus = xl.xlCloseDriver()
    print(f"close driver: {XLStatus}")

if __name__ == "__main__":
    load_dll()
    open_driver()
    # set_app_config()
    print_channel_info()
    open_port()
    activate_channel()
    
    print("\n=== 发送CAN消息 ===")
    send()      # 发送CAN消息
    
    print("\n=== 使用通知机制接收消息 ===")
    receive_with_notification()   # 使用通知机制接收消息
    
    print("\n=== 直接轮询接收消息 ===")
    receive()   # 直接轮询接收消息
    
    print("\n=== 清理资源 ===")
    close()
