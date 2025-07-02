import io
import sys

def safe_stream_wrapper(stream):
    """安全包装标准流"""
    try:
        if stream and not stream.closed and hasattr(stream, 'buffer'):
            return io.TextIOWrapper(stream.buffer, encoding='utf-8', write_through=True)
        return stream
    except Exception:
        return stream

sys.stdout = safe_stream_wrapper(sys.stdout)
sys.stderr = safe_stream_wrapper(sys.stderr)