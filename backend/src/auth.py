"""
认证模块 — OAuth 登录 + Session 管理 + RBAC 中间件

支持: QQ / 微信 / 支付宝 OAuth + 手机验证码登录
"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request

from .config import settings
from .database import get_db, new_id, now

logger = logging.getLogger(__name__)

SESSION_EXPIRE_HOURS = 72


# ═══════════════════════════════════════════════════════════════════════════════
# OAuth URL 生成 (模拟 — 生产环境替换为真实 AppID/Secret)
# ═══════════════════════════════════════════════════════════════════════════════

OAUTH_CONFIG = {
    "qq": {
        "name": "QQ",
        "authorize_url": "https://graph.qq.com/oauth2.0/authorize",
    },
    "wechat": {
        "name": "微信",
        "authorize_url": "https://open.weixin.qq.com/connect/qrconnect",
    },
    "alipay": {
        "name": "支付宝",
        "authorize_url": "https://openauth.alipay.com/oauth2/publicAppAuthorize.htm",
    },
}


def get_oauth_url(provider: str, redirect_uri: str = "") -> str:
    """生成 OAuth 授权 URL"""
    if provider not in OAUTH_CONFIG:
        raise HTTPException(400, f"Unsupported provider: {provider}")
    state = new_id()
    cfg = OAUTH_CONFIG[provider]
    base = cfg["authorize_url"]
    return f"{base}?response_type=code&client_id=danshen_demo&state={state}&redirect_uri={redirect_uri or 'http://localhost:8000/api/v1/auth/oauth/callback'}"


# ═══════════════════════════════════════════════════════════════════════════════
# 用户操作
# ═══════════════════════════════════════════════════════════════════════════════

async def login_or_register(
    provider: str,
    provider_uid: str,
    nickname: str = "",
    avatar_url: str = "",
    phone: str = "",
) -> dict:
    """登录或注册用户，返回用户信息 + 会话 token"""
    db = await get_db()

    # 查找现有用户
    cursor = await db.execute(
        "SELECT * FROM users WHERE provider = ? AND provider_uid = ?",
        (provider, provider_uid),
    )
    row = await cursor.fetchone()

    if row is None:
        user_id = new_id()
        default_nicknames = {"qq": "QQ用户", "wechat": "微信用户", "alipay": "支付宝用户", "sms": "手机用户"}
        now_ts = now()
        await db.execute(
            """INSERT INTO users (id, nickname, avatar_url, phone, provider, provider_uid, role, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, 'user', 'active', ?, ?)""",
            (user_id, nickname or default_nicknames.get(provider, "新用户"),
             avatar_url, phone, provider, provider_uid, now_ts, now_ts),
        )
        await db.commit()
        user = {
            "id": user_id, "nickname": nickname or default_nicknames.get(provider, "新用户"),
            "avatar_url": avatar_url, "phone": phone, "provider": provider,
            "provider_uid": provider_uid, "role": "user", "status": "active",
            "created_at": now_ts,
        }
    else:
        user = dict(row)

    if user["status"] == "disabled":
        raise HTTPException(403, "Account disabled")

    # 创建 session
    token = f"token_{new_id()}"
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRE_HOURS)).isoformat()
    await db.execute(
        "INSERT INTO sessions (token, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
        (token, user["id"], expires_at, now()),
    )
    await db.commit()

    return {"token": token, "user": user}


async def logout(token: str):
    db = await get_db()
    await db.execute("DELETE FROM sessions WHERE token = ?", (token,))
    await db.commit()


async def get_user_by_token(token: str) -> dict | None:
    """通过 session token 获取当前用户"""
    db = await get_db()
    cursor = await db.execute(
        """SELECT u.* FROM users u
           JOIN sessions s ON u.id = s.user_id
           WHERE s.token = ? AND s.expires_at > ?""",
        (token, now()),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_user_by_id(user_id: str) -> dict | None:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


# ═══════════════════════════════════════════════════════════════════════════════
# 短信验证码 (开发模式下直接返回验证码)
# ═══════════════════════════════════════════════════════════════════════════════

_sms_store: dict[str, dict] = {}


def store_sms_code(phone: str) -> str:
    import random
    code = f"{random.randint(100000, 999999)}"
    _sms_store[phone] = {
        "code": code,
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    }
    return code


def verify_sms_code(phone: str, code: str) -> bool:
    entry = _sms_store.get(phone)
    if not entry:
        return False
    if now() > entry["expires_at"]:
        del _sms_store[phone]
        return False
    if entry["code"] != code:
        return False
    del _sms_store[phone]
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# RBAC 依赖注入
# ═══════════════════════════════════════════════════════════════════════════════

async def get_current_user(request: Request) -> dict:
    """从请求头 Bearer token 获取当前用户"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    token = auth.removeprefix("Bearer ")
    user = await get_user_by_token(token)
    if user is None:
        raise HTTPException(401, "Invalid or expired token")
    return user


async def require_user(request: Request) -> dict:
    """要求已登录（user 或 admin）"""
    return await get_current_user(request)


async def require_admin(request: Request) -> dict:
    """要求 admin 角色"""
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(403, "Admin access required")
    return user
