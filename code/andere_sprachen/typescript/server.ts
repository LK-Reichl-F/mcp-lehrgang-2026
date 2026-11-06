// MCP-Server in TypeScript – dasselbe Tool wie lab03/mini_server.py (Python)
// Start: node server.ts   (Node.js ≥ 23.6 führt TypeScript direkt aus)
import { McpServer } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import * as z from "zod";

const server = new McpServer({ name: "musterschule-ts", version: "1.0.0" });

server.registerTool(
  "addiere",
  {
    description: "Addiert zwei ganze Zahlen.",
    inputSchema: z.object({ a: z.number().int(), b: z.number().int() }),
  },
  async ({ a, b }) => ({ content: [{ type: "text", text: String(a + b) }] }),
);

await server.connect(new StdioServerTransport());
