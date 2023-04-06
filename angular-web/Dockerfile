FROM node:18.15.0-alpine3.17 AS build
WORKDIR /usr/src/app
COPY . ./
RUN npm ci
RUN npm run build

FROM --platform=linux/amd64 nginx:stable-alpine3.17-slim
COPY --from=build /usr/src/app/dist/availability-app-web /usr/share/nginx/html