import ctypes

# 常量定义
XL_CONFIG_MAX_CHANNELS = 64
XL_MAX_LENGTH = 31

# 端口和访问相关常量
XL_INVALID_PORTHANDLE = -1
# 使用一个合理的通道掩码值，避免64位溢出问题
# 对于大多数应用，使用前32位应该足够了
XL_USE_ALL_CHANNELS = 0xFFFFFFFF

# 接口版本
XL_INTERFACE_VERSION_V3 = 3
XL_INTERFACE_VERSION_V4 = 4

# 总线类型
XL_BUS_TYPE_CAN = 1

# activate - channel flags
XL_ACTIVATE_NONE = 0
XL_ACTIVATE_RESET_CLOCK = 8

# 消息相关常量
MAX_MSG_LEN = 8
XL_CAN_MAX_DATA_LEN = 64

# CAN传输相关常量
XL_CAN_TXMSG_FLAG_EDL = 0x0001  # extended data length
XL_CAN_TXMSG_FLAG_BRS = 0x0002  # baud rate switch
XL_CAN_TXMSG_FLAG_RTR = 0x0010  # remote transmission request
XL_CAN_TXMSG_FLAG_HIGHPRIO = 0x0080  # high priority message
XL_CAN_TXMSG_FLAG_WAKEUP = 0x0200  # generate a wakeup message

# CAN事件标签
XL_TRANSMIT_MSG = 0x000A
XL_RECEIVE_MSG = 0x0001

# defines for SET_OUTPUT_MODE
XL_OUTPUT_MODE_SILENT = 0  # //!< switch CAN trx into default silent mode
XL_OUTPUT_MODE_NORMAL = 1  # //!< switch CAN trx into normal mode
XL_OUTPUT_MODE_TX_OFF = 2  # //!< switch CAN trx into silent mode with tx pin off
XL_OUTPUT_MODE_SJA_1000_SILENT = 3  # //!< switch CAN trx into SJA1000 silent mode

# Transceiver modes
XL_TRANSCEIVER_EVENT_ERROR = 1
XL_TRANSCEIVER_EVENT_CHANGED = 2

# 类型定义
XLuint64 = ctypes.c_uint64
XLhandle = ctypes.c_void_p  # Windows HANDLE 类型

# XL事件相关结构体
class XLcanMsg(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint),
        ("flags", ctypes.c_ushort),
        ("dlc", ctypes.c_ushort),
        ("res1", XLuint64),
        ("data", ctypes.c_ubyte * MAX_MSG_LEN),
        ("res2", XLuint64),
    ]

# 简化的tag data联合体，主要支持CAN消息
class XLtagData(ctypes.Union):
    _fields_ = [
        ("msg", XLcanMsg),
        ("raw", ctypes.c_ubyte * 32),  # 32字节的原始数据
    ]

# XL事件结构体
class XLevent(ctypes.Structure):
    _fields_ = [
        ("tag", ctypes.c_ubyte),        # XLeventTag
        ("chanIndex", ctypes.c_ubyte),  # unsigned char
        ("transId", ctypes.c_ushort),   # unsigned short
        ("portHandle", ctypes.c_ushort), # unsigned short (internal use only)
        ("flags", ctypes.c_ubyte),      # unsigned char
        ("reserved", ctypes.c_ubyte),   # unsigned char
        ("timeStamp", XLuint64),        # XLuint64
        ("tagData", XLtagData),         # union s_xl_tag_data (32 Bytes)
    ]

# CAN传输事件标签数据联合体
class XLcanTxEventTagData(ctypes.Union):
    _fields_ = [
        ("msg", XLcanMsg)
    ]

# CAN传输事件结构体 - 按照C语言定义的正确顺序
class XLcanTxEvent(ctypes.Structure):
    _fields_ = [
        ("tag", ctypes.c_ushort),       # 事件标签
        ("transId", ctypes.c_ushort),   # 传输ID
        ("chanIndex", ctypes.c_ubyte), # 通道索引
        ("reserved", ctypes.c_ubyte * 3), # 保留字段
        ("tagData", XLcanTxEventTagData), # 标签数据
    ]

# XLbusParams 联合体中的各个结构体
class XLbusParamsCAN(ctypes.Structure):
    _fields_ = [
        ("bitRate", ctypes.c_uint),
        ("sjw", ctypes.c_ubyte),
        ("tseg1", ctypes.c_ubyte),
        ("tseg2", ctypes.c_ubyte),
        ("sam", ctypes.c_ubyte),  # 1 or 3
        ("outputMode", ctypes.c_ubyte),
        ("reserved1", ctypes.c_ubyte * 7),
        ("canOpMode", ctypes.c_ubyte),
    ]

class XLbusParamsCANFD(ctypes.Structure):
    _fields_ = [
        ("arbitrationBitRate", ctypes.c_uint),  # CAN bus timing for nominal / arbitration bit rate
        ("sjwAbr", ctypes.c_ubyte),
        ("tseg1Abr", ctypes.c_ubyte),
        ("tseg2Abr", ctypes.c_ubyte),
        ("samAbr", ctypes.c_ubyte),  # 1 or 3
        ("outputMode", ctypes.c_ubyte),
        ("sjwDbr", ctypes.c_ubyte),  # CAN bus timing for data bit rate
        ("tseg1Dbr", ctypes.c_ubyte),
        ("tseg2Dbr", ctypes.c_ubyte),
        ("dataBitRate", ctypes.c_uint),
        ("canOpMode", ctypes.c_ubyte),
    ]

class XLbusParamsMOST(ctypes.Structure):
    _fields_ = [
        ("activeSpeedGrade", ctypes.c_uint),
        ("compatibleSpeedGrade", ctypes.c_uint),
        ("inicFwVersion", ctypes.c_uint),
    ]

class XLbusParamsFlexRay(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_uint),    # XL_FR_CHANNEL_CFG_STATUS_xxx
        ("cfgMode", ctypes.c_uint),   # XL_FR_CHANNEL_CFG_MODE_xxx
        ("baudrate", ctypes.c_uint),  # FlexRay baudrate in kBaud
    ]

class XLbusParamsEthernet(ctypes.Structure):
    _fields_ = [
        ("macAddr", ctypes.c_ubyte * 6),     # MAC address (starting with MSB!)
        ("connector", ctypes.c_ubyte),       # XL_ETH_STATUS_CONNECTOR_xxx
        ("phy", ctypes.c_ubyte),             # XL_ETH_STATUS_PHY_xxx
        ("link", ctypes.c_ubyte),            # XL_ETH_STATUS_LINK_xxx
        ("speed", ctypes.c_ubyte),           # XL_ETH_STATUS_SPEED_xxx
        ("clockMode", ctypes.c_ubyte),       # XL_ETH_STATUS_CLOCK_xxx
        ("bypass", ctypes.c_ubyte),          # XL_ETH_BYPASS_xxx
    ]

class XLbusParamsA429Tx(ctypes.Structure):
    _fields_ = [
        ("bitrate", ctypes.c_uint),
        ("parity", ctypes.c_uint),
        ("minGap", ctypes.c_uint),
    ]

class XLbusParamsA429Rx(ctypes.Structure):
    _fields_ = [
        ("bitrate", ctypes.c_uint),
        ("minBitrate", ctypes.c_uint),
        ("maxBitrate", ctypes.c_uint),
        ("parity", ctypes.c_uint),
        ("minGap", ctypes.c_uint),
        ("autoBaudrate", ctypes.c_uint),
    ]

class XLbusParamsA429Dir(ctypes.Union):
    _fields_ = [
        ("tx", XLbusParamsA429Tx),
        ("rx", XLbusParamsA429Rx),
        ("raw", ctypes.c_ubyte * 24),
    ]

class XLbusParamsA429(ctypes.Structure):
    _fields_ = [
        ("channelDirection", ctypes.c_ushort),
        ("res1", ctypes.c_ushort),
        ("dir", XLbusParamsA429Dir),
    ]

# XLbusParams 联合体
class XLbusParamsData(ctypes.Union):
    _fields_ = [
        ("can", XLbusParamsCAN),
        ("canFD", XLbusParamsCANFD),
        ("most", XLbusParamsMOST),
        ("flexray", XLbusParamsFlexRay),
        ("ethernet", XLbusParamsEthernet),
        ("a429", XLbusParamsA429),
        ("raw", ctypes.c_ubyte * 28),
    ]

# XLbusParams 主结构体
class XLbusParams(ctypes.Structure):
    _fields_ = [
        ("busType", ctypes.c_uint),
        ("data", XLbusParamsData),
    ]

# XLchannelConfig 结构体
class XLchannelConfig(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * (XL_MAX_LENGTH + 1)),
        ("hwType", ctypes.c_ubyte),
        ("hwIndex", ctypes.c_ubyte),
        ("hwChannel", ctypes.c_ubyte),
        ("transceiverType", ctypes.c_ushort),
        ("transceiverState", ctypes.c_uint),
        ("channelIndex", ctypes.c_ubyte),
        ("channelMask", XLuint64),
        ("channelCapabilities", ctypes.c_uint),
        ("channelBusCapabilities", ctypes.c_uint),
        ("isOnBus", ctypes.c_ubyte),
        ("connectedBusType", ctypes.c_uint),
        ("busParams", XLbusParams),
        ("driverVersion", ctypes.c_uint),
        ("interfaceVersion", ctypes.c_uint),
        ("raw_data", ctypes.c_uint * 10),
        ("serialNumber", ctypes.c_uint),
        ("articleNumber", ctypes.c_uint),
        ("transceiverName", ctypes.c_char * (XL_MAX_LENGTH + 1)),
        ("specialCabFlags", ctypes.c_uint),
        ("dominantTimeout", ctypes.c_uint),
        ("reserved", ctypes.c_uint * 8),
    ]

# XLdriverConfig 结构体
class XLdriverConfig(ctypes.Structure):
    _fields_ = [
        ("dllVersion", ctypes.c_uint),
        ("channelCount", ctypes.c_uint),
        ("reserved", ctypes.c_uint * 10),
        ("channel", XLchannelConfig * XL_CONFIG_MAX_CHANNELS),
    ]

# 为了方便使用，定义一些常用的函数来初始化和打印结构体
def init_xlchannelconfig():
    """初始化一个XLchannelConfig结构体"""
    config = XLchannelConfig()
    config.name = b""
    config.hwType = 0
    config.hwIndex = 0
    config.hwChannel = 0
    config.transceiverType = 0
    config.transceiverState = 0
    config.channelIndex = 0
    config.channelMask = 0
    config.channelCapabilities = 0
    config.channelBusCapabilities = 0
    config.isOnBus = 0
    config.connectedBusType = 0
    config.driverVersion = 0
    config.interfaceVersion = 0
    config.serialNumber = 0
    config.articleNumber = 0
    config.transceiverName = b""
    config.specialCabFlags = 0
    config.dominantTimeout = 0
    return config

def init_xldriverconfig():
    """初始化一个XLdriverConfig结构体"""
    config = XLdriverConfig()
    config.dllVersion = 0
    config.channelCount = 0
    return config

def print_xlchannelconfig(config, index=0):
    print("""打印XLchannelConfig结构体的内容""")
    print(f"Channel {index} Config:")
    print(f"  Name: {config.name.decode('utf-8', errors='ignore')}")
    print(f"  HW Type: {config.hwType}")
    print(f"  HW Index: {config.hwIndex}")
    print(f"  HW Channel: {config.hwChannel}")
    print(f"  Transceiver Type: {config.transceiverType}")
    print(f"  Transceiver State: {config.transceiverState}")
    print(f"  Channel Index: {config.channelIndex}")
    print(f"  Channel Mask: {config.channelMask}")
    print(f"  Channel Capabilities: {config.channelCapabilities}")
    print(f"  Channel Bus Capabilities: {config.channelBusCapabilities}")
    print(f"  Is On Bus: {config.isOnBus}")
    print(f"  Connected Bus Type: {config.connectedBusType}")
    print(f"  Driver Version: {config.driverVersion}")
    print(f"  Interface Version: {config.interfaceVersion}")
    print(f"  Serial Number: {config.serialNumber}")
    print(f"  Article Number: {config.articleNumber}")
    print(f"  Transceiver Name: {config.transceiverName.decode('utf-8', errors='ignore')}")
    print(f"  Special CAB Flags: {config.specialCabFlags}")
    print(f"  Dominant Timeout: {config.dominantTimeout}")
    print()

def print_xldriverconfig(config):
    print("""打印XLdriverConfig结构体的内容""")
    print("Driver Config:")
    print(f"  DLL Version: {config.dllVersion}")
    print(f"  Channel Count: {config.channelCount}")
    print()
    
    for i in range(config.channelCount):
        print_xlchannelconfig(config.channel[i], i)

def init_xlevent():
    """初始化一个XLevent结构体"""
    event = XLevent()
    event.tag = 0
    event.chanIndex = 0
    event.transId = 0
    event.portHandle = 0
    event.flags = 0
    event.reserved = 0
    event.timeStamp = 0
    # 初始化tagData
    for i in range(32):
        event.tagData.raw[i] = 0
    return event

def print_xlevent(event, index=0):
    """打印XLevent结构体的内容"""
    print(f"Event {index}:")
    print(f"  Tag: {event.tag}")
    print(f"  Channel Index: {event.chanIndex}")
    print(f"  Trans ID: {event.transId}")
    print(f"  Port Handle: {event.portHandle}")
    print(f"  Flags: {event.flags}")
    print(f"  Time Stamp: {event.timeStamp}")
    
    # 如果是CAN消息
    if event.tag == 1:  # XL_RECEIVE_MSG
        msg = event.tagData.msg
        print(f"  CAN Message:")
        print(f"    ID: 0x{msg.id:08X}")
        print(f"    Flags: 0x{msg.flags:04X}")
        print(f"    DLC: {msg.dlc}")
        print(f"    Data: {' '.join(f'{b:02X}' for b in msg.data[:msg.dlc])}")
    else:
        print(f"  Raw Data: {' '.join(f'{b:02X}' for b in event.tagData.raw[:8])}")
    print()

def create_can_tx_event(can_id, data, flags=0):
    """创建一个CAN传输事件"""
    event = XLcanTxEvent()
    event.tag = XL_TRANSMIT_MSG
    event.tagData.msg.id = 0x04
    event.tagData.msg.flags = 0
    event.tagData.msg.dlc = min(len(data), MAX_MSG_LEN)
    
    # 复制数据
    for i in range(MAX_MSG_LEN):
        if i < len(data):
            event.tagData.msg.data[i] = data[i]
        else:
            event.tagData.msg.data[i] = 0

    return event

def print_can_tx_event(event, index=0):
    """打印CAN传输事件的内容"""
    print(f"CAN TX Event {index}:")
    print(f"  Tag: 0x{event.tag:04X}")
    print(f"  Trans ID: {event.transId}")
    print(f"  Channel Index: {event.chanIndex}")
    
    msg = event.tagData.msg
    print(f"  CAN Message:")
    print(f"    ID: 0x{msg.id:08X}")
    print(f"    Flags: 0x{msg.flags:04X}")
    print(f"    DLC: {msg.dlc}")
    print(f"    Data: {' '.join(f'{b:02X}' for b in msg.data[:msg.dlc])}")
    print()
