# Stage 1: build
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies
COPY package.json ./
RUN yarn install --frozen-lockfile

# Copy source code and build
COPY . .
RUN yarn build

# Stage 2: serve
FROM nginx:stable-alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]