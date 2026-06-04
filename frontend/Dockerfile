# --- Stage 1: Build Stage ---
FROM node:20-alpine AS build

WORKDIR /app

# Sao chép package.json và package-lock.json để tận dụng Docker cache
COPY package*.json ./
RUN npm install

# Định nghĩa các Build Arguments cho cấu hình Firebase (Vite yêu cầu biến VITE_ tại thời điểm build)
ARG VITE_FIREBASE_API_KEY
ARG VITE_FIREBASE_AUTH_DOMAIN
ARG VITE_FIREBASE_PROJECT_ID
ARG VITE_FIREBASE_STORAGE_BUCKET
ARG VITE_FIREBASE_MESSAGING_SENDER_ID
ARG VITE_FIREBASE_APP_ID
ARG VITE_API_BASE_URL

# Thiết lập các biến môi trường cho quá trình build ứng dụng Vite
ENV VITE_FIREBASE_API_KEY=$VITE_FIREBASE_API_KEY
ENV VITE_FIREBASE_AUTH_DOMAIN=$VITE_FIREBASE_AUTH_DOMAIN
ENV VITE_FIREBASE_PROJECT_ID=$VITE_FIREBASE_PROJECT_ID
ENV VITE_FIREBASE_STORAGE_BUCKET=$VITE_FIREBASE_STORAGE_BUCKET
ENV VITE_FIREBASE_MESSAGING_SENDER_ID=$VITE_FIREBASE_MESSAGING_SENDER_ID
ENV VITE_FIREBASE_APP_ID=$VITE_FIREBASE_APP_ID
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Sao chép toàn bộ mã nguồn và thực hiện build ứng dụng
COPY . .
RUN npm run build

# --- Stage 2: Production Stage ---
FROM nginx:stable-alpine

# Sao chép file cấu hình Nginx để hỗ trợ client-side routing của React
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Sao chép tài nguyên đã build ở Stage 1 vào thư mục phục vụ của Nginx
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
