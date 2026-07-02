"""
CVCP Protocol Error Definitions
"""

class CVCPProtocolError(Exception):
    """
    Base exception indicating a violation of core CVCP standard requirements.
    All runtime failures map strictly to specified string codes.
    """
    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(f"[{error_code}] {message}")
