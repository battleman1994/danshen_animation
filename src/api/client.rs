use crate::components::types::{AnimateRequest, LLMModelListResponse, ProviderListResponse, TaskResponse, TaskStatus};

const API_BASE: &str = "http://localhost:8000";

pub async fn submit_animation(req: &AnimateRequest) -> Result<TaskResponse, String> {
    let resp = reqwest::Client::new()
        .post(&format!("{}/api/v1/animate", API_BASE))
        .json(req)
        .send().await
        .map_err(|e| format!("请求失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn fetch_providers() -> Result<ProviderListResponse, String> {
    let resp = reqwest::Client::new()
        .get(&format!("{}/api/v1/animate/providers", API_BASE))
        .send().await
        .map_err(|e| format!("获取 providers 失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn fetch_llm_models() -> Result<LLMModelListResponse, String> {
    let resp = reqwest::Client::new()
        .get(&format!("{}/api/v1/animate/llm-models", API_BASE))
        .send().await
        .map_err(|e| format!("获取 LLM 模型列表失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn poll_task(task_id: &str) -> Result<TaskStatus, String> {
    let resp = reqwest::Client::new()
        .get(&format!("{}/api/v1/tasks/{}", API_BASE, task_id))
        .send().await
        .map_err(|e| format!("查询失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}
