import time
import logging
import os
from datetime import datetime
from typing import Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure file logging for wide events
def setup_file_logging():
    """Set up file logging for wide events."""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    log_file = os.path.join(logs_dir, "wide_events.log")
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    return file_handler

logger = logging.getLogger(__name__)
logger.addHandler(setup_file_logging())


class WideEventMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking and logging wide events with request context.
    Records request/response metadata, timing, and error information.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Initialize the wide event with request context
        event: dict[str, Any] = {
            "request_id": request.headers.get("x-request-id"),
            "timestamp": datetime.now().isoformat() + "Z",
            "method": request.method,
            "path": request.url.path,
            "service": self._get_env("SERVICE_NAME"),
            "version": self._get_env("SERVICE_VERSION"),
            "deployment_id": self._get_env("DEPLOYMENT_ID"),
            "region": self._get_env("REGION"),
        }

        # Make the event accessible to handlers
        # request.state.wide_event = event
        # request.state.add_event_data = lambda key, value: self._add_event_data(event, key, value)
        request.state.add_event_data_batch = lambda data: self._add_event_data_batch(event, data)

        try:
            response = await call_next(request)
            event["status_code"] = response.status_code
            event["outcome"] = "success"
            return response

        except Exception as error:
            event["status_code"] = 500
            event["outcome"] = "error"
            event["error"] = {
                "type": error.__class__.__name__,
                "message": str(error),
                "code": getattr(error, "code", None),
                "retriable": getattr(error, "retriable", False),
            }
            raise

        finally:
            event["duration_ms"] = (time.time() - start_time) * 1000

            # Emit the wide event
            logger.info(event)

    @staticmethod
    def _add_event_data(event: dict[str, Any], key: str, value: Any) -> None:
        """Dynamically add a single key-value pair to the event."""
        event[key] = value

    @staticmethod
    def _add_event_data_batch(event: dict[str, Any], data: dict[str, Any]) -> None:
        """Dynamically add multiple key-value pairs to the event at once."""
        event.update(data)

    @staticmethod
    def _get_env(key: str) -> str | None:
        """Helper to safely get environment variables."""
        import os
        return os.getenv(key)
