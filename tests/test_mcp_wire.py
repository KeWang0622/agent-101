"""Tests for the MCP wire format (chapter 13/14).
Spawns a real MCP server subprocess and exchanges real JSON-RPC."""

import sys
from pathlib import Path

import importlib.util


def _load_ch13():
    spec = importlib.util.spec_from_file_location(
        "ch13", Path(__file__).resolve().parent.parent / "chapters" / "ch13_mcp_wire.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ch13"] = m
    spec.loader.exec_module(m)
    return m


SERVER = (Path(__file__).resolve().parent.parent / "mcp_servers" /
          "calculator_server.py")


def test_initialize_handshake():
    ch13 = _load_ch13()
    mcp = ch13.MCPProcess([sys.executable, str(SERVER)])
    try:
        result = mcp.call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0.1"},
        })
        assert result["serverInfo"]["name"] == "calculator"
        assert "capabilities" in result
    finally:
        mcp.close()


def test_tools_list():
    ch13 = _load_ch13()
    mcp = ch13.MCPProcess([sys.executable, str(SERVER)])
    try:
        mcp.call("initialize", {"protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "t", "version": "0.1"}})
        mcp.notify("notifications/initialized")
        result = mcp.call("tools/list")
        names = [t["name"] for t in result["tools"]]
        assert "calculator" in names
    finally:
        mcp.close()


def test_tools_call_arithmetic():
    ch13 = _load_ch13()
    mcp = ch13.MCPProcess([sys.executable, str(SERVER)])
    try:
        mcp.call("initialize", {"protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "t", "version": "0.1"}})
        mcp.notify("notifications/initialized")
        result = mcp.call("tools/call",
                          {"name": "calculator",
                           "arguments": {"expression": "17 * 23"}})
        assert result["content"][0]["text"] == "391"
        assert not result.get("isError")
    finally:
        mcp.close()


def test_unknown_tool_returns_isError():
    ch13 = _load_ch13()
    mcp = ch13.MCPProcess([sys.executable, str(SERVER)])
    try:
        mcp.call("initialize", {"protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "t", "version": "0.1"}})
        mcp.notify("notifications/initialized")
        result = mcp.call("tools/call", {"name": "bogus", "arguments": {}})
        assert result["isError"] is True
    finally:
        mcp.close()
