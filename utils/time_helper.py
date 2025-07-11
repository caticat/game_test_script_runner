from datetime import datetime

def str_to_timestamp(time_str: str) -> float:
    """
    将格式为 'YYYY-MM-DD HH:MM:SS' 的时间字符串转换为 Unix 时间戳（单位：秒）
    """
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())

def timestamp_to_str(ts: float|int) -> str:
    """
    将 Unix 时间戳（单位：秒）转换为格式为 'YYYY-MM-DD HH:MM:SS' 的时间字符串
    """
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

