from fastapi import APIRouter, FastAPI, Request, status

from loggers import get_logger, setup_logging

app = FastAPI()

main_logger = get_logger(name=__name__)
debug_logger = get_logger()
root_logger = get_logger(name="root")
color_logger = get_logger(name="color")
json_logger = get_logger(name="json")
slack_logger = get_logger(name="slack")
google_logger = get_logger(name="google")
http_logger = get_logger(name="http")
tcp_logger = get_logger(name="tcp")
udp_logger = get_logger(name="udp")
file_logger = get_logger(name="file")
rotating_file_logger = get_logger(name="rotating_file")
timed_rotating_file_logger = get_logger(name="timed_rotating_file")
queue_logger = get_logger(name="queue")


@app.on_event(event_type="startup")
def _setup_logging():
    setup_logging()


logs_router = APIRouter(tags=["logs"])


@logs_router.get(path="/root/")
async def log_root(request: Request):
    # root_logger.log(level=logging.WARN, msg="Log")
    root_logger.debug(msg="Debug")
    root_logger.info(msg="Info")
    root_logger.warning(msg="Warning")
    root_logger.error(msg="Error")
    root_logger.critical(msg="Critical")
    return None


@logs_router.get(path="/main/")
async def log_main(request: Request):
    main_logger.trace(msg="Trace")
    main_logger.debug(msg="Debug")
    main_logger.info(msg="Info")
    main_logger.success(msg="Success")
    main_logger.warning(msg="Warning")
    main_logger.error(msg="Error")
    main_logger.critical(msg="Critical")
    return None


@logs_router.get(path="/color/")
async def log_color(request: Request):
    color_logger.trace(msg="Trace")
    color_logger.debug(msg="Debug")
    color_logger.info(msg="Info")
    color_logger.success(msg="Success")
    color_logger.warning(msg="Warning")
    color_logger.error(msg="Error")
    color_logger.critical(msg="Critical")
    return None


@logs_router.get(path="/debug/")
async def log_debug(request: Request):
    # debug_logger.log(level=logging.WARN, msg="Log!!!")
    # debug_logger.warn(msg="Warn!!!")
    # debug_logger.fatal(msg="Fatal!!!")
    debug_logger.trace(msg="Trace!!!")
    debug_logger.debug(msg="Debug!!!")
    debug_logger.info(msg="Info!!!")
    debug_logger.success(msg="Success!!!")
    debug_logger.warning(msg="Warning!!!")
    debug_logger.error(msg="Error!!!")
    debug_logger.critical(msg="Critical!!!")
    return None


@logs_router.get(path="/json/")
async def log_json(request: Request):
    json_logger.info(msg="TEST")
    return None


@logs_router.get(path="/slack/")
async def log_slack(request: Request):
    slack_logger.critical(msg="NEW TEST!")
    return None


@logs_router.get(path="/google/")
async def log_google(request: Request):
    google_logger.critical(msg="TEST")
    return None


@logs_router.get(path="/http/")
async def log_http(request: Request):
    http_logger.info(msg="TEST")
    return None


@logs_router.get(path="/tcp/")
async def log_tcp(request: Request):
    tcp_logger.info(msg="TEST")
    return None


@logs_router.get(path="/udp/")
async def log_udp(request: Request):
    udp_logger.info(msg="TEST")
    return None


@logs_router.get(path="/file/")
async def log_file(request: Request):
    file_logger.info(msg="TEST")
    return None


@logs_router.get(path="/file_rotating/")
async def log_rotating_file(request: Request):
    rotating_file_logger.info(msg="TEST")
    return None


@logs_router.get(path="/file_timed_rotating/")
async def timed_rotating_file(request: Request):
    timed_rotating_file_logger.info(msg="TEST")
    return None


@logs_router.get(path="/queue/", status_code=status.HTTP_202_ACCEPTED)
async def log_queue(request: Request):
    queue_logger.info(msg="TEST")
    return None


app.include_router(router=logs_router, prefix="/logs")

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(
        app="main:app",
        reload=True,
        host="0.0.0.0",
        port=9090,
        debug=True,
        use_colors=True,
        log_level=10,
    )
