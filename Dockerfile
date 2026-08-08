FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/samurai ./cmd/server

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/samurai /samurai
EXPOSE 8090
ENTRYPOINT ["/samurai"]
