"""
认证路由 — OAuth 登录 + 短信登录 + 会话管理
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..auth import (
    get_oauth_url, login_or_register, logout, store_sms_code, verify_sms_code,
    get_user_by_token, require_user,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


# ── 请求模型 ──

class SMSLoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    code: str = Field(..., min_length=6, max_length=6)


class SendSMSRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")


class OAuthCallbackRequest(BaseModel):
    provider: str = Field(..., pattern="^(qq|wechat|alipay)$")
    code: str = Field(..., min_length=1)
    state: str = Field(default="")


# ── 端点 ──

@router.get("/oauth/{provider}")
async def oauth_authorize(provider: str):
    url = get_oauth_url(provider)
    return {"provider": provider, "authorize_url": url, "message": "请在浏览器中打开此链接完成授权"}


@router.post("/oauth/callback")
async def oauth_callback(req: OAuthCallbackRequest):
    # 模拟 OAuth 回调 — 生产环境需通过 provider 的 API 用 code 换取 openid
    simulated_uid = f"{req.provider}_uid_{req.code[:8]}"
    result = await login_or_register(
        provider=req.provider,
        provider_uid=simulated_uid,
    )
    return {"success": True, **result}


@router.post("/sms/send")
async def sms_send(req: SendSMSRequest):
    code = store_sms_code(req.phone)
    logger.info("SMS code for %s: %s", req.phone, code)
    return {"success": True, "message": "验证码已发送", "debug_code": code}


@router.post("/sms/login")
async def sms_login(req: SMSLoginRequest):
    if not verify_sms_code(req.phone, req.code):
        raise HTTPException(400, "验证码错误或已过期")
    result = await login_or_register(
        provider="sms",
        provider_uid=req.phone,
        phone=req.phone,
    )
    return {"success": True, **result}


@router.get("/user/me")
async def user_me(user: dict = __import__("fastapi").Depends(require_user)):
    return {"success": True, "user": {
        "user_id": user["id"], "nickname": user["nickname"],
        "avatar_url": user["avatar_url"], "provider": user["provider"],
        "phone": user["phone"], "role": user["role"],
        "created_at": user["created_at"],
    }}


@router.post("/logout")
async def user_logout(user: dict = __import__("fastapi").Depends(require_user)):
    token = ""  # Will be extracted in production from header
    await logout(token)
    return {"success": True, "message": "已退出登录"}
