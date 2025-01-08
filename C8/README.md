# WebSocket

HTTP is a powerful protocol for sending and receiving data to and from a server. At its core, it relies on the
principles of request and response: the client sends a request, and the server sends back a response. While
straightforward, this model has limitations in real-time scenarios. For example, in a chat application, users should be
notified immediately when they receive a new message. With HTTP alone, the client would need to continuously send
requests to check for updates, which is inefficient and resource-intensive. This challenge led to the development of
WebSocket — a protocol designed to maintain a persistent communication channel between the client and server, enabling
real-time, two-way data exchange.

## Technical Requirements

To handle multiple WebSocket connections and broadcast messages, you’ll need a running Redis server on your local
computer. Redis can be easily launched using Docker with the following command:

```bash
docker run -d --name fastapi-redis -p 6379:6379 redis
```

By leveraging WebSocket technology, you can open a bi-directional communication channel between a client and server,
facilitating real-time applications. FastAPI simplifies the process of implementing WebSocket endpoints. However,
working with WebSocket logic differs from traditional HTTP endpoints: you must manage infinite loops, concurrency, and
multiple tasks simultaneously. The asynchronous design of FastAPI aids in writing clear and efficient concurrent code.

In scenarios involving multiple clients sharing messages, a message broker like Redis becomes essential for reliability
across various server processes. Redis ensures efficient message distribution and state management.

FastAPI provides you with all the tools needed to develop real-world applications. As your project grows and becomes
more complex, maintaining code quality is crucial. Testing your applications ensures they work as intended and helps
prevent bugs when introducing new features. High-quality code and thorough testing are key to building robust and
maintainable systems.