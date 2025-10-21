import NIO
import NIOHTTP1

let group = MultiThreadedEventLoopGroup(numberOfThreads: System.coreCount)

defer {
    try? group.syncShutdownGracefully()
}

let bootstrap = ServerBootstrap(group: group)
    .serverChannelOption(ChannelOptions.backlog, value: 256)
    .serverChannelOption(ChannelOptions.socket(SocketOptionLevel(SOL_SOCKET), SO_REUSEADDR), value: 1)
    .childChannelInitializer { channel in
        channel.pipeline.configureHTTPServerPipeline().flatMap { _ in
            channel.pipeline.addHandler(HTTPHandler())
        }
    }
    .childChannelOption(ChannelOptions.socket(IPPROTO_TCP, TCP_NODELAY), value: 1)
    .childChannelOption(ChannelOptions.maxMessagesPerRead, value: 16)

final class HTTPHandler: ChannelInboundHandler {
    typealias InboundIn = HTTPServerRequestPart
    typealias OutboundOut = HTTPServerResponsePart

    func channelRead(context: ChannelHandlerContext, data: NIOAny) {
        let reqPart = self.unwrapInboundIn(data)
        switch reqPart {
        case .head:
            break
        case .body:
            break
        case .end:
            var headers = HTTPHeaders()
            headers.add(name: "content-type", value: "text/plain; charset=utf-8")
            let response = HTTPResponseHead(version: .http1_1, status: .ok, headers: headers)
            context.write(self.wrapOutboundOut(.head(response)), promise: nil)
            var buffer = context.channel.allocator.buffer(capacity: 128)
            buffer.writeString("Hello from Swift service!\n")
            context.write(self.wrapOutboundOut(.body(.byteBuffer(buffer))), promise: nil)
            context.writeAndFlush(self.wrapOutboundOut(HTTPServerResponsePart.end(nil)), promise: nil)
        }
    }
}

let channel = try bootstrap.bind(host: "0.0.0.0", port: 8080).wait()
print("Swift app running on: \(channel.localAddress!)")
try channel.closeFuture.wait()
