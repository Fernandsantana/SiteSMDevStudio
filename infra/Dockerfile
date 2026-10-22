FROM golang:1.26.10-alpine@sha256:27f2d3b83cfc5803c8078f8e730af0f7c431bf067afaec8f60a36fb763187cba AS compilacao_caddy
WORKDIR /src
ENV CGO_ENABLED=0 GOTOOLCHAIN=local GOTELEMETRY=off
COPY infra/caddy/go.mod infra/caddy/go.sum ./
RUN go mod download && go mod verify
COPY infra/caddy/main.go ./
RUN go list -mod=readonly -deps . > /dependencias.txt \
    && ! grep -q '^golang.org/x/crypto/openpgp' /dependencias.txt
RUN go build -mod=readonly -trimpath -ldflags='-s -w' -o /caddy .

FROM caddy:2.11.7-alpine@sha256:d8542f48d34a9cf4e4c11a478865229840e87e4c96ea3f439101f31a5d35f75f
RUN apk add --no-cache 'zlib=1.3.2-r1'
COPY --from=compilacao_caddy /caddy /usr/bin/caddy
LABEL org.opencontainers.image.title="SM Dev Studio Site"
