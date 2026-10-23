#!/usr/bin/env python3
"""TED MCP surface; uses the existing authenticated BasicOps connector."""
import argparse
import importlib.util
import json
from pathlib import Path
from router import Router

PROFILE = Path('/opt/data/profiles/lhm_chief_of_staff')
QUEUE = Path('/opt/data/profiles/lhm_brain/dispatch/task-router')
spec = importlib.util.spec_from_file_location('codex_bridge', PROFILE / 'codex_sessions_mcp.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


def instance():
    return Router(PROFILE, QUEUE, bridge.basicops)


def serve():
    import anyio
    from mcp import types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server

    async def listing(_ctx, _params):
        tools = []
        for name, desc in [
            ('task_route_preview', 'Verify a personal work request and choose the central Codex/Claude route; no dispatch or plan required.'),
            ('task_route_submit', 'Dispatch a direct personal work request once to its central provider; TED must own task In Progress. No separate TED plan needed.'),
            ('task_route_status', 'Read the saved central-provider session, progress, result or exact blocker.')]:
            props = {'task_id': {'type': 'integer'}}
            if name != 'task_route_status':
                props['instruction_message_id'] = {'type': 'string'}
            tools.append(types.Tool(name=name, description=desc, inputSchema={
                'type': 'object', 'additionalProperties': False, 'properties': props, 'required': list(props)}))
        return types.ListToolsResult(tools=tools)

    async def calling(_ctx, params):
        try:
            action = {'task_route_preview': 'preview', 'task_route_submit': 'submit', 'task_route_status': 'status'}[params.name]
            result = await anyio.to_thread.run_sync(lambda: getattr(instance(), action)(**(params.arguments or {})))
            return types.CallToolResult(content=[types.TextContent(type='text', text=json.dumps(result))])
        except Exception as exc:
            return types.CallToolResult(isError=True, content=[types.TextContent(type='text', text=str(exc))])

    async def main():
        server = Server('ted-central-task-router', on_list_tools=listing, on_call_tool=calling)
        async with stdio_server() as streams:
            await server.run(*streams, server.create_initialization_options())
    anyio.run(main)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reconcile', action='store_true')
    parser.add_argument('--verify')
    args = parser.parse_args()
    if args.reconcile:
        router = instance()
        for path in router.state.glob('[0-9]*.json'):
            try:
                value = router.reconcile(int(path.stem))
                print(json.dumps({k: value.get(k) for k in ['task_id', 'provider', 'status']}))
            except Exception as exc:
                print(json.dumps({'task_id': int(path.stem), 'error': str(exc)}))
    elif args.verify:
        import re
        if not re.fullmatch(r'ted-route-[1-9][0-9]*-dm[1-9][0-9]*', args.verify):
            raise ValueError('Invalid request ID')
        task_id = int(args.verify.split('-')[2])
        router = instance()
        saved = json.loads((router.state / f'{task_id}.json').read_text())['request']
        task, current = router.contract(task_id, saved['instruction_message_id'])
        if current != saved or current['request_id'] != args.verify or bridge.actor(task) != router.config['agent_user_id'] or task['status'] != 'In Progress':
            raise ValueError('Request or ownership changed before execution')
        print(json.dumps(current))
    else:
        serve()
