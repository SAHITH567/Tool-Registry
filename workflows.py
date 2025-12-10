"""app/workflows.py

Example nodes implementing Option B: Summarization + Refinement.
The nodes are simple and annotated to show reasoning (good for interview demos).
"""
from typing import Dict, Any
import asyncio

async def node_split_text(state: Dict, invoke_tool):
    text = state.get('text', '')
    chunk_size = state.get('chunk_size', 1000)
    chunks = await invoke_tool('chunk_text', text, chunk_size)
    # save into state and go next
    return {'state': {'chunks': chunks}, 'next': 'node_summarize_chunks'}

async def node_summarize_chunks(state: Dict, invoke_tool):
    chunks = state.get('chunks', [])
    max_sent = state.get('max_sentences_per_chunk', 3)

    # run summarization in parallel for speed
    async def summarize_one(c):
        return await invoke_tool('naive_summarize_chunk', c, max_sent)

    tasks = [asyncio.create_task(summarize_one(c)) for c in chunks]
    summaries = await asyncio.gather(*tasks) if tasks else []
    return {'state': {'summaries': summaries}, 'next': 'node_merge_summaries'}

def node_merge_summaries(state: Dict, invoke_tool):
    summaries = state.get('summaries', [])
    # invoke_tool may be async; use event loop to call safely from sync function
    merged = asyncio.get_event_loop().run_until_complete(invoke_tool('merge_summaries', summaries))
    return {'state': {'merged_summary': merged}, 'next': 'node_refine_summary'}

def node_refine_summary(state: Dict, invoke_tool):
    """
    Repeatedly refine the merged summary until its length <= final_max_length
    or until max_iterations reached (safe-guard).
    This explicit loop shows the 'stop when under limit' behaviour required in assignment.
    """
    merged = state.get('merged_summary', '')
    max_len = int(state.get('final_max_length', 800))
    max_iters = int(state.get('refine_max_iters', 5))  # safe fallback for infinite loops

    current = merged
    for i in range(max_iters):
        # call the refine tool (may be sync or async)
        refined = invoke_tool('refine_summary', current, max_len)
        if asyncio.iscoroutine(refined):
            # tools may be async — handle both cases
            refined = asyncio.get_event_loop().run_until_complete(refined)

        # if refinement meets size goal, stop early
        if len(refined) <= max_len:
            current = refined
            break

        # otherwise, set current to refined and iterate
        current = refined

    return {'state': {'final_summary': current}}
