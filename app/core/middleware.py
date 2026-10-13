import time
from fastapi import Request


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

