"""app/engine.py

Minimal GraphEngine that runs nodes (functions) and passes a shared state dict.
Nodes may return:
  - None: engine follows edges mapping
  - {"state": {...}}: merge into shared state, follow edges
  - {"state": {...}, "next": "node_name"}: explicit next
  - {"state": {...}, "next": ["a","b"]}: branching
"""
from typing import Callable, Dict, Any, List, Optional
import asyncio

class GraphEngine:
    def __init__(self):
        self.nodes: Dict[str, Callable[[Dict, Callable], Any]] = {}
        self.edges: Dict[str, List[str]] = {}
        self.tools_invoke = None  # should be async callable

    def register_node(self, name: str, fn: Callable[[dict, Callable], Any]):
        self.nodes[name] = fn

    def set_edges(self, edges: Dict[str, List[str]]):
        self.edges = edges

    def set_tool_invoker(self, invoker: Callable):
        self.tools_invoke = invoker

    async def run(self, start_node: str, initial_state: Optional[Dict] = None, max_steps: int = 1000):
        if initial_state is None:
            initial_state = {}
        if start_node not in self.nodes:
            raise KeyError(f"Start node '{start_node}' not registered")
        if self.tools_invoke is None:
            raise RuntimeError('Tool invoker not set')

        state = dict(initial_state)
        current_nodes = [start_node]
        steps = 0

        while current_nodes and steps < max_steps:
            next_nodes = []
            for node_name in current_nodes:
                steps += 1
                node = self.nodes.get(node_name)
                if node is None:
                    continue

                # call node (sync or async)
                if asyncio.iscoroutinefunction(node):
                    result = await node(state, self.tools_invoke)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, lambda: node(state, self.tools_invoke))

                # handle result types
                if isinstance(result, dict):
                    state.update(result.get('state', {}))
                    nxt = result.get('next')
                    if isinstance(nxt, str):
                        next_nodes.append(nxt)
                    elif isinstance(nxt, list):
                        next_nodes.extend(nxt)
                    else:
                        next_nodes.extend(self.edges.get(node_name, []))
                else:
                    next_nodes.extend(self.edges.get(node_name, []))
            current_nodes = next_nodes

        return state
