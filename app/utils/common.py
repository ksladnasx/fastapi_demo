#工具函数，负责处理一些常用的操作，比如邮箱地址的规范化等。
def normalize_email(email: str) -> str:
    return email.strip().lower()


def success_response(data=None, message: str = "success", code: int = 201) -> dict:
    return {
        "code": code,
        "data": data,
        "message": message,
    }


#获取本地时间的工具函数
try:
    import zoneinfo
    from datetime import datetime
    def get_current_time() -> datetime:
        """
        获取当前北京时间（使用 IANA 时区数据库）
        
        Returns:
            datetime: 带时区信息的北京时间
        """
        return datetime.now(zoneinfo.ZoneInfo("Asia/Shanghai"))
except ImportError:
    # 如果没有 zoneinfo，回退到方式一
    pass