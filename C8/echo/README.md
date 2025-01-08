## Creating a WebSocket with FastAPI

Thanks to Starlette, FastAPI has built-in support for WebSockets. As we’ll
see, defining a WebSocket endpoint is quick and easy, and we’ll be able to
get started in minutes. However, things will get more complex as we try to
add more features to our endpoint logic. Let’s start simple, with a WebSocket
that waits for messages and simply echoes them back.