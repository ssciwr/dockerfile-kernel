# MIT License

# Copyright (c) 2022 DevOps Hobbies

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

##################### Builder

FROM rust:1.68.2-slim as builder

# Set the working directory
WORKDIR /usr/src/app

RUN apt-get update && apt-get install musl-tools --no-install-recommends -y

## Install target platform (Cross-Compilation) --> Needed for Alpine
RUN rustup target add x86_64-unknown-linux-musl

# We want dependencies cached, so copy those first.
COPY Cargo.toml ./

# This is a dummy build to get the dependencies cached.
RUN mkdir src/ && echo "fn main() {println!(\"if you see this, the build broke\")}" > src/main.rs && \
  cargo build --target x86_64-unknown-linux-musl --release && \
  rm -f target/x86_64-unknown-linux-musl/release/deps/devopshobbies*

# Now copy in the rest of the sources
COPY . ./

# This is the application build.
RUN cargo build --target x86_64-unknown-linux-musl --release

##################### Runtime

FROM alpine:3.17 as runtime

# Copy application binary from builder image
COPY --from=builder /usr/src/app/target/x86_64-unknown-linux-musl/release/devopshobbies /usr/local/bin

# Run the application
ENTRYPOINT ["/usr/local/bin/devopshobbies"]