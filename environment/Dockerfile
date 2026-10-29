# syntax=docker/dockerfile:1
FROM golang:1.26.9-alpine AS build
RUN apk add --no-cache ca-certificates git
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
COPY --from=recorder recorder*.go ./cmd/oc-benchmark/
RUN CGO_ENABLED=0 go test -count=1 ./cmd/oc-benchmark
RUN CGO_ENABLED=0 go build -trimpath -buildvcs=false -o /out/controlplane ./cmd/oc-benchmark
