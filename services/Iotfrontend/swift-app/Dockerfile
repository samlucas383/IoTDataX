# Build stage
FROM swift:5.7 as builder
WORKDIR /app
COPY Package.swift ./
COPY Sources ./Sources
RUN swift build -c release

# Runtime stage
FROM ubuntu:22.04
WORKDIR /app
COPY --from=builder /app/.build/release/App /app/App
EXPOSE 8080
CMD ["/app/App"]
