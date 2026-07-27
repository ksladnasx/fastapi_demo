#工具函数，负责处理一些常用的操作，比如邮箱地址的规范化等。
def normalize_email(email: str) -> str:
    return email.strip().lower()
