# Build stage
FROM swift:5.7 AS builder
WORKDIR /app
COPY Package.swift ./
COPY Sources ./Sources
RUN swift build -c release

# Runtime stage
FROM ubuntu:22.04
WORKDIR /app

# Install minimal runtime deps that Swift binaries may need
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   libatomic1 \
	&& rm -rf /var/lib/apt/lists/*

# Copy the compiled binary from the builder
COPY --from=builder /app/.build/release/App /app/App

# Copy Swift runtime libraries from the builder image so the binary can find
# libswift_*.so at runtime (fixes errors like libswift_StringProcessing.so missing)
COPY --from=builder /usr/lib/swift /usr/lib/swift

# Ensure the dynamic loader will search the Swift runtime libs
# Use a fixed default path here to avoid Dockerfile build-time variable warnings
ENV LD_LIBRARY_PATH=/usr/lib/swift/linux:/usr/lib:/lib

EXPOSE 8080
CMD ["/app/App"]
