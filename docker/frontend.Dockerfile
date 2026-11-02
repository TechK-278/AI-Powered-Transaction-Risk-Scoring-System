# React frontend: build static assets with Node, serve them with nginx.
# Build context: repository root.

FROM node:24-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginx:1.27-alpine AS runtime
# The official image renders /etc/nginx/templates/*.template with envsubst at startup.
COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
ENV BACKEND_URL=http://backend:8000 \
    NGINX_PORT=80
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider "http://127.0.0.1:${NGINX_PORT}/" || exit 1
