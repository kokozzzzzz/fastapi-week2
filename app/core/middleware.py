import time
from fastapi import Request

# 终端中显示运行时间
async def add_process_time(
    request: Request,
    call_next,
):
    start = time.time()

    response = await call_next(request)

    process_time = time.time() - start

    print(
        f"{request.url.path}: "
        f"{process_time:.4f}s"
    )

    return response


# header中体现运行时间
async def log_request_time(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    elapsed_ms = (time.perf_counter() - start) * 1000

    response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"

    print(
        f"{request.method} {request.url.path} "
        f"{response.status_code} {elapsed_ms:.2f}ms"
    )

    return response
