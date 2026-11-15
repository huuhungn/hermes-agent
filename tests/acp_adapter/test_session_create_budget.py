"""An ACP session survives a slow editor MCP start: session.create and each server's start get
budgets that a cold npx/uvx launch on a loaded machine fits in (#155773)."""
import pytest

from acp_adapter.gateway_server import SESSION_CREATE_RPC_TIMEOUT
from gateway.session_local_mcp import _CONNECT_TIMEOUT, _configs
from hermes_cli.gateway_client import DEFAULT_RPC_TIMEOUT
from tests.acp_adapter.test_gateway_launch_flags import _agent


@pytest.mark.asyncio
async def test_session_create_waits_past_the_default_rpc_budget(tmp_path):
    agent = _agent([])
    fake, budgets = agent._gateway.rpc.side_effect, {}

    async def rpc(method, _timeout=None, **params):
        budgets[method] = _timeout
        return await fake(method, **params)

    agent._gateway.rpc.side_effect = rpc
    await agent.new_session(cwd=str(tmp_path))
    assert budgets['session.create'] == SESSION_CREATE_RPC_TIMEOUT
    assert SESSION_CREATE_RPC_TIMEOUT > DEFAULT_RPC_TIMEOUT


def test_editor_mcp_servers_get_more_than_five_seconds_to_start(tmp_path):
    servers = [{'type': 'stdio', 'command': 'npx', 'args': ['-y', 'example-mcp']},
               {'type': 'http', 'url': 'http://127.0.0.1:9/mcp'}]
    configs = _configs(servers, {0: 'local', 1: 'remote'}, str(tmp_path))
    assert {config['connect_timeout'] for config in configs.values()} == {_CONNECT_TIMEOUT}
    assert _CONNECT_TIMEOUT >= 15
