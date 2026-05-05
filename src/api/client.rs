use crate::components::types::{AnimateRequest, TaskResponse, TaskStatus};

pub async fn submit_animation(req: &AnimateRequest) -> Result<TaskResponse, String> {
    let resp = reqwest::Client::new()
        .post("http://localhost:8000/api/v1/animate")
        .json(req)
        .send().await
        .map_err(|e| format!("请求失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}

pub async fn poll_task(task_id: &str) -> Result<TaskStatus, String> {
    let resp = reqwest::Client::new()
        .get(&format!("http://localhost:8000/api/v1/tasks/{}", task_id))
        .send().await
        .map_err(|e| format!("查询失败: {}", e))?;
    resp.json().await.map_err(|e| format!("解析失败: {}", e))
}
