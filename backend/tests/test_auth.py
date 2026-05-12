import pytest
from src.auth import store_sms_code, verify_sms_code


class TestSMSAuth:
    def test_store_and_verify_valid_code(self):
        code = store_sms_code("13800138000")
        assert len(code) == 6
        assert verify_sms_code("13800138000", code) is True

    def test_verify_wrong_code(self):
        store_sms_code("13800138001")
        assert verify_sms_code("13800138001", "000000") is False

    def test_verify_expired(self):
        phone = "13800138002"
        code = store_sms_code(phone)
        from src.auth import _sms_store, now
        # manully expire
        _sms_store[phone]["expires_at"] = "2020-01-01T00:00:00"
        assert verify_sms_code(phone, code) is False

    def test_oauth_url_generation(self):
        from src.auth import get_oauth_url
        url = get_oauth_url("qq")
        assert "graph.qq.com" in url
        assert "response_type=code" in url

        with pytest.raises(Exception):
            get_oauth_url("unknown")


@pytest.mark.asyncio
async def test_login_register_and_token():
    from src.auth import login_or_register, get_user_by_token, logout
    from src.database import init_db, get_db

    await init_db()

    result = await login_or_register("sms", "13800000000", phone="13800000000")
    assert "token" in result
    assert result["user"]["provider"] == "sms"

    user = await get_user_by_token(result["token"])
    assert user is not None
    assert user["phone"] == "13800000000"

    await logout(result["token"])
    assert await get_user_by_token(result["token"]) is None
