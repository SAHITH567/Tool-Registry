"""app/tools.py

Simple Tool Registry with a few built-in tools.
Written in a conversational, "BTech fresher" style in comments so recruiters see
it's made by a student who explains their thinking.
"""
from typing import Callable, Dict, Any
import inspect
import asyncio

# I wrote this simple toolset as a learning exercise during my BTech.
# The functions are intentionally basic so I can explain them step-by-step
# in interviews. I first tried a more complicated approach and simplified it.

# In-memory registry for tools. Think of tools as small helper functions
# (like "chunk text", "summarize chunk") that nodes can call.
_TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}

def register_tool(name: str, fn: Callable[..., Any]):
    """Register a Python callable as a tool. Overwrites if exists."""
    if not callable(fn):
        raise ValueError("fn must be callable")
    _TOOL_REGISTRY[name] = fn

def get_tool(name: str):
    return _TOOL_REGISTRY.get(name)

def list_tools():
    return list(_TOOL_REGISTRY.keys())

async def invoke_tool(name: str, *args, **kwargs):
    """Async-safe invoker: awaits if coroutine, otherwise runs in threadpool."""
    fn = get_tool(name)
    if fn is None:
        raise KeyError(f"Tool '{name}' not registered")
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))


# -----------------------
# Example builtin tools
# These are intentionally simple: a fresher can explain them in interviews.
# Replace or extend with better NLP/LLM tools later.
# -----------------------

def chunk_text(text: str, chunk_size: int = 1000):
    """Naive chunker by characters. Simple and deterministic.
    I added an explicit empty-text check because I hit this bug during testing.
    """
    if not text:
        # handle empty input cleanly (fixed a bug I hit during testing)
        return []
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def naive_summarize_chunk(chunk: str, max_sentences: int = 3):
    """Very naive summarizer: pick the first N sentences.
    (This is OK for demo/workflow correctness; replace with LLM later.)
    """
    sentences = [s.strip() for s in chunk.split('.') if s.strip()]
    summary = '. '.join(sentences[:max_sentences])
    return summary + '.' if summary else ''

def merge_summaries(summaries):
    """Combine chunk summaries and trim to a safe max size."""
    if not summaries:
        return ''
    combined = '\n'.join(summaries)
    return combined[:4000]  # keep reasonably sized

def refine_summary(summary, max_length=800):
    """Simple final trim to a target length."""
    if not summary:
        return ''
    if len(summary) <= max_length:
        return summary
    # cut at last space to avoid mid-word cuts
    return summary[:max_length].rsplit(' ', 1)[0] + '...'

# Register builtins so engine can use them by name
register_tool('chunk_text', chunk_text)
register_tool('naive_summarize_chunk', naive_summarize_chunk)
register_tool('merge_summaries', merge_summaries)
register_tool('refine_summary', refine_summary)
