// MCP-Server in Rust (offizielles SDK rmcp) – dasselbe Tool wie lab03/mini_server.py (Python)
// Bauen und starten: cargo run --release
use rmcp::{
    ErrorData as McpError, ServerHandler, ServiceExt,
    handler::server::{tool::ToolRouter, wrapper::Parameters},
    model::{CallToolResult, ContentBlock},
    tool, tool_handler, tool_router,
    transport::stdio,
};
use serde::Deserialize;

/// Die Parameter des Tools – daraus erzeugt das SDK das JSON-Schema
#[derive(Deserialize, schemars::JsonSchema)]
struct Summanden {
    /// erste Zahl
    a: i64,
    /// zweite Zahl
    b: i64,
}

#[derive(Clone)]
struct Musterschule {
    #[allow(dead_code)] // wird vom Makro tool_handler benutzt
    tool_router: ToolRouter<Self>,
}

#[tool_router]
impl Musterschule {
    fn new() -> Self {
        Self { tool_router: Self::tool_router() }
    }

    #[tool(description = "Addiert zwei ganze Zahlen.")]
    async fn addiere(&self, Parameters(Summanden { a, b }): Parameters<Summanden>) -> Result<CallToolResult, McpError> {
        Ok(CallToolResult::success(vec![ContentBlock::text((a + b).to_string())]))
    }
}

#[tool_handler]
impl ServerHandler for Musterschule {}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let dienst = Musterschule::new().serve(stdio()).await?;
    dienst.waiting().await?;
    Ok(())
}
