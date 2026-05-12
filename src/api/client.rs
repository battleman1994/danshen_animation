use crate::components::types::{AnimateRequest, AuthResponse, LLMModelListResponse, ProviderListResponse, SendSmsResponse, TaskResponse, TaskStatus};

pub async fn submit_animation(req: &AnimateRequest) -> Result<TaskResponse, String> {
    let resp = reqwest::Client::new()
        .post("http://localhost:8000/api/v1/animate")
        .json(req)
        .send().await
        .map_err(|e| format!("请求失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn fetch_providers() -> Result<ProviderListResponse, String> {
    let resp = reqwest::Client::new()
        .get("http://localhost:8000/api/v1/animate/providers")
        .send().await
        .map_err(|e| format!("获取 providers 失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn fetch_llm_models() -> Result<LLMModelListResponse, String> {
    let resp = reqwest::Client::new()
        .get("http://localhost:8000/api/v1/animate/llm-models")
        .send().await
        .map_err(|e| format!("获取 LLM 模型列表失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn poll_task(task_id: &str) -> Result<TaskStatus, String> {
    let resp = reqwest::Client::new()
        .get(&format!("http://localhost:8000/api/v1/tasks/{}", task_id))
        .send().await
        .map_err(|e| format!("查询失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

// ── Auth API ──

pub async fn oauth_callback(provider: &str) -> Result<AuthResponse, String> {
    let body = serde_json::json!({
        "provider": provider,
        "code": "mock_auth_code_123456",
        "state": "mock_state"
    });
    let resp = reqwest::Client::new()
        .post("http://localhost:8000/api/v1/auth/oauth/callback")
        .json(&body)
        .send().await
        .map_err(|e| format!("登录请求失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn send_sms_code(phone: &str) -> Result<SendSmsResponse, String> {
    let body = serde_json::json!({ "phone": phone });
    let resp = reqwest::Client::new()
        .post("http://localhost:8000/api/v1/auth/sms/send")
        .json(&body)
        .send().await
        .map_err(|e| format!("发送验证码失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn sms_login(phone: &str, code: &str) -> Result<AuthResponse, String> {
    let body = serde_json::json!({ "phone": phone, "code": code });
    let resp = reqwest::Client::new()
        .post("http://localhost:8000/api/v1/auth/sms/login")
        .json(&body)
        .send().await
        .map_err(|e| format!("登录请求失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}
