class BaseAppError(Exception):
    """アプリケーション全体で使用する基本的な例外クラス"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidParameterError(BaseAppError):
    """無効なパラメータが渡された場合の例外"""

    def __init__(self, key: str, value: str, message: str = "Invalid parameter provided"):
        super().__init__(f"{message}: {key} = {value}")
        self.key = key
        self.value = value


class DataNotFoundError(BaseAppError):
    """データが見つからない場合の例外"""

    def __init__(self, resource_name: str, message: str = "Data not found"):
        super().__init__(f"{message}: {resource_name}")
        self.resource_name = resource_name


class DataAccessError(BaseAppError):
    """データベースや外部リソースへのアクセスエラー"""

    def __init__(self, message: str = "Failed to access data"):
        super().__init__(message)


class PermissionDeniedError(BaseAppError):
    """権限が不足している場合の例外"""

    def __init__(self, action: str, message: str = "Permission denied"):
        super().__init__(f"{message}: {action}")
        self.action = action


class ServiceUnavailableError(BaseAppError):
    """外部サービスが利用できない場合の例外"""

    def __init__(self, service_name: str, message: str = "Service unavailable"):
        super().__init__(f"{message}: {service_name}")
        self.service_name = service_name
