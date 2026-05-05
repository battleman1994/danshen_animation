"""
Auth 路由 — QQ / 微信 / 支付宝第三方登录 + 手机号验证码登录

端点：
  GET  /api/v1/auth/oauth/{provider}   — 获取 OAuth 授权 URL
  POST /api/v1/auth/oauth/callback      — OAuth 回调（模拟登录）
  POST /api/v1/auth/sms/send            — 发送短信验证码
  POST /api/v1/auth/sms/login           — 手机验证码登录
  GET  /api/v1/auth/user/me             — 获取当前用户信息
  POST /api/v1/auth/logout              — 退出登录
"""

from fastapi import APIRouter, HTTPException, Header
from ..models.user import (
    login_or_register, get_user_by_token, store_sms_code,
    verify_sms_code, get_oauth_authorize_url,
    AuthResponse, OAuthLoginRequest, SMSLoginRequest,
    SendSMSRequest, UserInfo,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/oauth/{provider}")
async def oauth_authorize(provider: str):
    """获取第三方登录授权 URL（QQ/微信/支付宝）"""
    if provider not in ("qq", "wechat", "alipay"):
        raise HTTPException(status_code=400, detail=f"不支持的登录方式: {provider}")

    authorize_url = get_oauth_authorize_url(provider)
    return {
        "url": authorize_url,
        "provider": provider,
        "message": f"请在新窗口中完成 {provider} 授权",
    }


@router.post("/oauth/callback", response_model=AuthResponse)
async def oauth_callback(req: OAuthLoginRequest):
    """处理第三方登录回调（模拟 OAuth 流程）"""
    fake_uid = f"{req.provider}_{req.code[:8]}"
    result = login_or_register(req.provider, fake_uid)
    user = result["user"]

    return AuthResponse(
        success=True,
        token=result["token"],
        user=UserInfo(
            user_id=user["user_id"],
            nickname=user["nickname"],
            avatar_url=user["avatar_url"],
            provider=user["provider"],
            phone=user.get("phone", ""),
            created_at=user.get("created_at", ""),
        ),
        message=f"{req.provider} 登录成功",
    )


@router.post("/sms/send")
async def send_sms(req: SendSMSRequest):
    """发送手机验证码"""
    import random
    code = str(random.randint(100000, 999999))
    store_sms_code(req.phone, code)

    # 模拟短信发送（生产环境对接真实 SMS 服务）
    print(f"📱 [SMS] 验证码已发送至 {req.phone}: {code}")

    return {
        "success": True,
        "message": "验证码已发送",
        "debug_code": code,  # 开发环境返回验证码，生产环境移除
    }


@router.post("/sms/login", response_model=AuthResponse)
async def sms_login(req: SMSLoginRequest):
    """手机验证码登录"""
    if not verify_sms_code(req.phone, req.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    result = login_or_register("sms", req.phone)
    user = result["user"]
    user["phone"] = req.phone

    return AuthResponse(
        success=True,
        token=result["token"],
        user=UserInfo(
            user_id=user["user_id"],
            nickname=user["nickname"],
            avatar_url=user["avatar_url"],
            provider="sms",
            phone=req.phone,
            created_at=user.get("created_at", ""),
        ),
        message="登录成功",
    )


@router.get("/user/me")
async def get_current_user(authorization: str = Header(default="")):
    """获取当前登录用户信息"""
    token = authorization.replace("Bearer ", "") if authorization else ""
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="令牌无效")
    return UserInfo(
        user_id=user["user_id"],
        nickname=user["nickname"],
        avatar_url=user["avatar_url"],
        provider=user["provider"],
        phone=user.get("phone", ""),
        created_at=user.get("created_at", ""),
    )


@router.post("/logout")
async def logout(authorization: str = Header(default="")):
    """退出登录"""
    token = authorization.replace("Bearer ", "") if authorization else ""
    from ..models.user import _token_store
    if token in _token_store:
        del _token_store[token]
    return {"success": True, "message": "已退出登录"}
