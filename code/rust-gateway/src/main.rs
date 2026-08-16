use axum::{body::Body, extract::State, http::{header, HeaderMap, StatusCode}, response::IntoResponse, routing::{get, post}, Json, Router};
use futures_util::StreamExt;
use serde_json::{json, Value};
use std::{env, sync::Arc, time::Instant};
use tokio::{fs::OpenOptions, io::AsyncWriteExt};

#[derive(Clone)]
struct AppState { client: reqwest::Client, vllm_url: String, key: String, telemetry_path: String }

async fn emit(state: &AppState, event: Value) {
    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(&state.telemetry_path).await {
        let _ = file.write_all(format!("{}\n", event).as_bytes()).await;
    }
}

async fn health() -> &'static str { "ok" }

async fn chat(State(state): State<Arc<AppState>>, headers: HeaderMap, Json(payload): Json<Value>) -> impl IntoResponse {
    if !state.key.is_empty() && headers.get("x-internal-key").and_then(|v| v.to_str().ok()) != Some(state.key.as_str()) {
        return (StatusCode::UNAUTHORIZED, Json(json!({"error":"unauthorized"}))).into_response();
    }
    let request_id = headers.get("x-request-id").and_then(|v| v.to_str().ok()).unwrap_or("missing");
    let count = payload.get("messages").and_then(Value::as_array).map_or(0, Vec::len);
    let started = Instant::now();
    let result = state.client.post(format!("{}/v1/chat/completions", state.vllm_url)).json(&payload).send().await;
    match result {
        Ok(response) => {
            let status = StatusCode::from_u16(response.status().as_u16()).unwrap_or(StatusCode::BAD_GATEWAY);
            let content_type = response.headers().get(header::CONTENT_TYPE).cloned();
            emit(&state, json!({"event":"vllm_proxy","request_id":request_id,"message_count":count,"status_code":status.as_u16(),"stream":true,"latency_ms":started.elapsed().as_millis()})).await;
            let stream = response.bytes_stream().map(|chunk| chunk.map_err(std::io::Error::other));
            let mut builder = Body::from_stream(stream).into_response();
            *builder.status_mut() = status;
            if let Some(value) = content_type { builder.headers_mut().insert(header::CONTENT_TYPE, value); }
            builder
        }
        Err(_) => {
            emit(&state, json!({"event":"vllm_proxy","request_id":request_id,"message_count":count,"status_code":502,"latency_ms":started.elapsed().as_millis()})).await;
            (StatusCode::BAD_GATEWAY, Json(json!({"error":"vllm unavailable"}))).into_response()
        }
    }
}

#[tokio::main]
async fn main() {
    let state = Arc::new(AppState { client: reqwest::Client::new(), vllm_url: env::var("VLLM_URL").unwrap_or_else(|_| "http://vllm:8000".into()), key: env::var("INTERNAL_GATEWAY_KEY").unwrap_or_default(), telemetry_path: env::var("TELEMETRY_PATH").unwrap_or_else(|_| "/telemetry/rust-gateway.jsonl".into()) });
    let app = Router::new().route("/health", get(health)).route("/v1/chat/completions", post(chat)).with_state(state);
    let listener = tokio::net::TcpListener::bind("0.0.0.0:9000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
