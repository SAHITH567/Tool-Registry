"""app/tools.py


"""
from typing import Callable, Dict, Any
import inspect
import asyncio

_TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}

def register_tool(name: str, fn: Callable[..., Any]):
    if not callable(fn):
        raise ValueError("fn must be callable")
    _TOOL_REGISTRY[name] = fn

def get_tool(name: str):
    return _TOOL_REGISTRY.get(name)

def list_tools():
    return list(_TOOL_REGISTRY.keys())

async def invoke_tool(name: str, *args, **kwargs):
    fn = get_tool(name)
    if fn is None:
        raise KeyError(f"Tool '{name}' not registered")
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))




def chunk_text(text: str, chunk_size: int = 1000):
   
    if not text:
        return []
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def naive_summarize_chunk(chunk: str, max_sentences: int = 3):
    
    sentences = [s.strip() for s in chunk.split('.') if s.strip()]
    summary = '. '.join(sentences[:max_sentences])
    return summary + '.' if summary else ''

def merge_summaries(summaries):
    if not summaries:
        return ''
    combined = '\n'.join(summaries)
    return combined[:4000]  

def refine_summary(summary, max_length=800):
    if not summary:
        return ''
    if len(summary) <= max_length:
        return summary
    return summary[:max_length].rsplit(' ', 1)[0] + '...'

register_tool('chunk_text', chunk_text)
register_tool('naive_summarize_chunk', naive_summarize_chunk)
register_tool('merge_summaries', merge_summaries)
register_tool('refine_summary', refine_summary)
