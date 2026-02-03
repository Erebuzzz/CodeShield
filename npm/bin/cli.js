#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "child_process";

const API_URL = process.env.CODESHIELD_API_URL || "https://codeshield-production.up.railway.app";

// Helper to call the CodeShield API
async function callAPI(endpoint, data) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return await response.json();
  } catch (error) {
    return { error: error.message };
  }
}

// Create MCP server
const server = new Server(
  {
    name: "codeshield-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "verify_code",
        description: "Verify code for syntax errors, security issues, and best practices. Returns validation results with detailed feedback.",
        inputSchema: {
          type: "object",
          properties: {
            code: {
              type: "string",
              description: "The code to verify",
            },
            language: {
              type: "string",
              description: "Programming language (python, javascript, typescript)",
              default: "python",
            },
          },
          required: ["code"],
        },
      },
      {
        name: "full_verify",
        description: "Full verification with sandbox execution. Runs the code in an isolated environment and returns execution results.",
        inputSchema: {
          type: "object",
          properties: {
            code: {
              type: "string",
              description: "The code to verify and execute",
            },
            language: {
              type: "string",
              description: "Programming language",
              default: "python",
            },
          },
          required: ["code"],
        },
      },
      {
        name: "check_style",
        description: "Check code style against codebase conventions. Detects naming patterns and suggests corrections.",
        inputSchema: {
          type: "object",
          properties: {
            code: {
              type: "string",
              description: "The code to check style for",
            },
            codebase_path: {
              type: "string",
              description: "Path to codebase for convention detection",
              default: ".",
            },
          },
          required: ["code"],
        },
      },
      {
        name: "save_context",
        description: "Save current coding context for later restoration. Captures files, decisions, and progress.",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "Name for this context snapshot",
            },
            files: {
              type: "array",
              items: { type: "string" },
              description: "List of file paths to capture",
            },
            notes: {
              type: "string",
              description: "Notes about current progress",
            },
          },
          required: ["name"],
        },
      },
      {
        name: "restore_context",
        description: "Restore a previously saved coding context. Returns briefing with all saved information.",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "Name of the context to restore",
            },
          },
          required: ["name"],
        },
      },
      {
        name: "list_contexts",
        description: "List all saved coding contexts.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result;

    switch (name) {
      case "verify_code":
        result = await callAPI("/verify", {
          code: args.code,
          language: args.language || "python",
        });
        break;

      case "full_verify":
        result = await callAPI("/full-verify", {
          code: args.code,
          language: args.language || "python",
        });
        break;

      case "check_style":
        result = await callAPI("/check-style", {
          code: args.code,
          codebase_path: args.codebase_path || ".",
        });
        break;

      case "save_context":
        result = await callAPI("/context/save", {
          name: args.name,
          files: args.files || [],
          notes: args.notes || "",
        });
        break;

      case "restore_context":
        result = await callAPI("/context/restore", {
          name: args.name,
        });
        break;

      case "list_contexts":
        result = await callAPI("/context/list", {});
        break;

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("CodeShield MCP server running on stdio");
}

main().catch(console.error);
