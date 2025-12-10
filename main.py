"""app/main.py

FastAPI app exposing:
 - GET /tools
 - POST /tools/register (demo: register builtins by name)
 - POST /run_graph  (run arbitrary registered graph start node)
 - POST /summarize  (convenience: runs example summarization pipeline)

Comments are written in an accessible, human style (BTech fresher notes).
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict
import uvicorn

from .engine import GraphEngine
from .tools import list_tools, register_tool, get_tool, invoke_tool
from . import workflows, tools as builtin_tools

app = FastAPI(title='Tool Registry + Graph Engine (Simple)')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

engine = GraphEngine()
engine.set_tool_invoker(invoke_tool)

engine.register_node('node_split_text', workflows.node_split_text)
engine.register_node('node_summarize_chunks', workflows.node_summarize_chunks)
engine.register_node('node_merge_summaries', workflows.node_merge_summaries)
engine.register_node('node_refine_summary', workflows.node_refine_summary)

engine.set_edges({
    'node_split_text': ['node_summarize_chunks'],
    'node_summarize_chunks': ['node_merge_summaries'],
    'node_merge_summaries': ['node_refine_summary'],
})

@app.get('/tools')
async def _list_tools():
    return {'tools': list_tools()}

@app.post('/tools/register')
async def _register_tool(payload: Dict[str, Any]):
    builtin = payload.get('builtin')
    name = payload.get('name')
    if not builtin or not name:
        raise HTTPException(status_code=400, detail='provide both name and builtin')
    fn = getattr(builtin_tools, builtin, None)
    if fn is None:
        raise HTTPException(status_code=400, detail=f"builtin '{builtin}' not found")
    register_tool(name, fn)
    return {'status': 'ok', 'registered': name}

@app.post('/run_graph')
async def _run_graph(payload: Dict[str, Any]):
    start = payload.get('start_node')
    initial = payload.get('initial_state', {})
    max_steps = payload.get('max_steps', 1000)
    if not start:
        raise HTTPException(status_code=400, detail='start_node required')
    try:
        state = await engine.run(start, initial, max_steps)
        return {'state': state}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/summarize')
async def _summarize(payload: Dict[str, Any]):
    init_state = {
        'text': payload.get('text', ''),
        'chunk_size': payload.get('chunk_size', 1000),
        'max_sentences_per_chunk': payload.get('max_sentences_per_chunk', 3),
        'final_max_length': payload.get('final_max_length', 800),
    }
    result = await engine.run('node_split_text', init_state)
    return {'final_summary': result.get('final_summary'), 'full_state': result}

if __name__ == '__main__':
    print('Starting Tool Registry demo — Sahith (BTech) - press CTRL+C to stop')
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
