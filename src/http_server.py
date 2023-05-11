import logging.handlers

import fastapi
import uvicorn

logger = logging.getLogger(name="uvicorn.error")
logger.setLevel(level=logging.DEBUG)


APP = fastapi.FastAPI()


@APP.post(path="/log/")
async def post_log(request: fastapi.Request):
    body_bytes = await request.body()
    logger.info(msg=body_bytes)
    return None


if __name__ == "__main__":
    uvicorn.run(
        app="src.http_server:APP",
        port=logging.handlers.DEFAULT_HTTP_LOGGING_PORT,
        host="localhost",
        log_level="debug",
        use_colors=True,
        debug=True,
        reload=True,
    )
