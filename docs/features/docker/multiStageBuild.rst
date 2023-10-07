Multi Stage Build
=================

    Multi-stage builds are useful to anyone who has struggled to optimize Dockerfiles while keeping them easy to read and maintain.

Use multi-stage builds
----------------------

    With multi-stage builds, you use multiple **FROM** statements in your Dockerfile. Each **FROM** instruction can use a different base, and each of them begins a new stage of the build. You can selectively copy artifacts from one stage to another, leaving behind everything you don't want in the final image.

The following Dockerfile has two separate stages: one for building a binary, and another where we copy the binary into.

>>> FROM golang:1.21
>>> WORKDIR /src
>>> COPY <<EOF ./main.go
>>> package main
>>> import "fmt"
>>> func main() {
>>>   fmt.Println("hello, world")
>>> }
>>> EOF
>>> RUN go build -o /bin/hello ./main.go
>>> FROM scratch
>>> COPY --from=0 /bin/hello /bin/hello
>>> CMD ["/bin/hello"]

You only need the single Dockerfile. No need for a separate build script.
Just run the commands in above Dockerfile one by one.The end result is a tiny production image with nothing but the binary inside. None of the build tools required to build the application are included in the resulting image.

How does it work?
    The second **FROM** instruction starts a new build stage with the *scratch* image as its base. The **COPY --from=0** line copies just the built artifact from the previous stage into this new stage. The Go SDK and any intermediate artifacts are left behind, and not saved in the final image.

Name your build stages
----------------------

    By default, the stages aren't named, and you refer to them by their integer number, starting with 0 for the first **FROM** instruction. However, you can name your stages, by adding an **AS <NAME>** to the **FROM** instruction. This example improves the previous one by naming the stages and using the name in the **COPY** instruction. This means that even if the instructions in your Dockerfile are re-ordered later, the **COPY** doesn't break.

>>> FROM golang:1.21 as build
>>> WORKDIR /src
>>> COPY <<EOF /src/main.go
>>> package main
>>> import "fmt"
>>> func main() {
>>>   fmt.Println("hello, world")
>>> }
>>> EOF
>>> RUN go build -o /bin/hello ./main.go
>>> FROM scratch
>>> COPY --from=build /bin/hello /bin/hello
>>> CMD ["/bin/hello"]

