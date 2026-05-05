use crate::components::types::{AnimateRequest, AuthResponse, SendSmsResponse, TaskResponse, TaskStatus, TaskResult};
use std::sync::atomic::{AtomicU32, Ordering};

static MOCK_POLL_COUNT: AtomicU32 = AtomicU32::new(0);

pub async fn submit_animation(req: &AnimateRequest) -> Result<TaskResponse, String> {
    let resp = reqwest::Client::new()
        .post("http://localhost:8000/api/v1/animate")
        .json(req)
        .send().await;

    match resp {
        Ok(resp) => resp.json().await.map_err(|e| format!("解析失败: {}", e)),
        Err(e) => {
            if e.is_connect() {
                MOCK_POLL_COUNT.store(0, Ordering::SeqCst);
                Ok(TaskResponse {
                    task_id: Some("mock_task_001".to_string()),
                    error: None,
                })
            } else {
                Err(format!("请求失败: {}", e))
            }
        }
    }
}

pub async fn poll_task(task_id: &str) -> Result<TaskStatus, String> {
    if task_id.starts_with("mock_") {
        let count = MOCK_POLL_COUNT.fetch_add(1, Ordering::SeqCst);
        return Ok(match count {
            0 => TaskStatus {
                status: "queued".to_string(),
                progress: Some(10.0),
                error: None,
                result: None,
            },
            1 => TaskStatus {
                status: "extracting".to_string(),
                progress: Some(30.0),
                error: None,
                result: None,
            },
            2 => TaskStatus {
                status: "adapting".to_string(),
                progress: Some(60.0),
                error: None,
                result: None,
            },
            _ => TaskStatus {
                status: "completed".to_string(),
                progress: Some(100.0),
                error: None,
                result: Some(TaskResult {
                    video_url: Some("https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4".to_string()),
                }),
            },
        });
    }

    let resp = reqwest::Client::new()
        .get(&format!("http://localhost:8000/api/v1/tasks/{}", task_id))
        .send().await
        .map_err(|e| format!("查询失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

// ── Auth API ──

/// OAuth 登录 — 发送 provider 信息到后端（模拟 OAuth 回调）
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

/// 发送短信验证码
pub async fn send_sms_code(phone: &str) -> Result<SendSmsResponse, String> {
    let body = serde_json::json!({ "phone": phone });
    let resp = reqwest::Client::new()
        .post("http://localhost:8000/api/v1/auth/sms/send")
        .json(&body)
        .send().await
        .map_err(|e| format!("发送验证码失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

/// 短信验证码登录
pub async fn sms_login(phone: &str, code: &str) -> Result<AuthResponse, String> {
    let body = serde_json::json!({ "phone": phone, "code": code });
    let resp = reqwest::Client::new()
        .post("http://localhost:8000/api/v1/auth/sms/login")
        .json(&body)
        .send().await
        .map_err(|e| format!("登录请求失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}
