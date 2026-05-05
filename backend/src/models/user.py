"""
用户数据模型

支持第三方登录（QQ、微信、支付宝）和手机号验证码登录。
生产环境应使用数据库（PostgreSQL/MySQL），当前使用内存存储。
"""

import uuid
import random
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 内存用户存储（生产环境替换为数据库）──
_user_store: dict[str, dict] = {}       # user_id -> user data
_token_store: dict[str, str] = {}        # token -> user_id
_sms_code_store: dict[str, dict] = {}    # phone -> {code, expires_at}
_oauth_state_store: dict[str, dict] = {}  # state -> provider


class UserInfo(BaseModel):
    """用户公开信息"""
    user_id: str
    nickname: str
    avatar_url: str = ""
    provider: str = ""  # qq, wechat, alipay, sms
    phone: str = ""
    created_at: str = ""


class LoginRequest(BaseModel):
    """通用登录请求"""
    code: str = Field(..., description="授权码（OAuth）或验证码（SMS）")
    redirect_uri: str = Field(default="", description="回调地址")


class OAuthLoginRequest(BaseModel):
    """第三方登录请求"""
    provider: str = Field(..., pattern="^(qq|wechat|alipay)$", description="登录方式")
    code: str = Field(..., description="授权码")
    state: str = Field(default="", description="防 CSRF 状态值")


class SMSLoginRequest(BaseModel):
    """手机验证码登录"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    code: str = Field(..., description="验证码")


class SendSMSRequest(BaseModel):
    """发送短信验证码"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")


class AuthResponse(BaseModel):
    """登录响应"""
    success: bool
    token: str = ""
    user: Optional[UserInfo] = None
    message: str = ""


def _generate_token() -> str:
    """生成登录令牌"""
    return f"token_{uuid.uuid4().hex[:24]}"


def _generate_user_id() -> str:
    return f"user_{uuid.uuid4().hex[:12]}"


def _get_demo_user_info(provider: str) -> dict:
    """根据登录方式生成模拟用户信息（实际 OAuth 对接后替换）"""
    avatars = {
        "qq": "https://q1.qlogo.cn/g?b=qq&nk=10086&s=100",
        "wechat": "https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTK4E95/132",
        "alipay": "https://mdn.alipayobjects.com/huamei_2f/afts/img/A*_QfHQ6vXw0sAAAAAAAAAAAAADsF5AQ/original",
        "sms": "https://api.dicebear.com/7.x/avataaars/svg?seed=danshen",
    }
    nicknames = {
        "qq": "QQ用户",
        "wechat": "微信用户",
        "alipay": "支付宝用户",
        "sms": "手机用户",
    }
    return {
        "avatar_url": avatars.get(provider, ""),
        "nickname": nicknames.get(provider, "匿名用户"),
    }


def login_or_register(provider: str, provider_uid: str) -> dict:
    """登录或注册用户"""
    user_id = _generate_user_id()
    demo = _get_demo_user_info(provider)

    # 检查是否已存在（简单实现：根据 provider+uid 判断）
    for uid, data in _user_store.items():
        if data.get("provider") == provider and data.get("provider_uid") == provider_uid:
            user_id = uid
            break

    if user_id not in _user_store:
        _user_store[user_id] = {
            "user_id": user_id,
            "nickname": demo["nickname"],
            "avatar_url": demo["avatar_url"],
            "provider": provider,
            "provider_uid": provider_uid,
            "phone": "",
            "created_at": datetime.now().isoformat(),
        }

    token = _generate_token()
    _token_store[token] = user_id

    user = _user_store[user_id]
    return {"token": token, "user": user}


def get_user_by_token(token: str) -> Optional[dict]:
    """通过令牌获取用户"""
    user_id = _token_store.get(token)
    if user_id and user_id in _user_store:
        return _user_store[user_id]
    return None


def get_user_by_id(user_id: str) -> Optional[dict]:
    return _user_store.get(user_id)


def store_sms_code(phone: str, code: str):
    """存储短信验证码"""
    import time
    _sms_code_store[phone] = {
        "code": code,
        "expires_at": time.time() + 300,  # 5分钟有效
    }


def verify_sms_code(phone: str, code: str) -> bool:
    """验证短信验证码"""
    import time
    data = _sms_code_store.get(phone)
    if not data:
        return False
    if time.time() > data["expires_at"]:
        del _sms_code_store[phone]
        return False
    if data["code"] != code:
        return False
    del _sms_code_store[phone]
    return True


def get_oauth_authorize_url(provider: str) -> str:
    """生成 OAuth 授权 URL（模拟）"""
    state = uuid.uuid4().hex[:16]
    _oauth_state_store[state] = {"provider": provider}
    
    # 模拟各平台的授权 URL
    base_urls = {
        "qq": "https://graph.qq.com/oauth2.0/authorize",
        "wechat": "https://open.weixin.qq.com/connect/qrconnect",
        "alipay": "https://openauth.alipay.com/oauth2/publicAppAuthorize.htm",
    }
    url = f"{base_urls[provider]}?response_type=code&client_id=demo&state={state}&redirect_uri=http://localhost:8000/api/v1/auth/callback"
    return url
