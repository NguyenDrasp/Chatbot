FROM node:lts AS builder

WORKDIR /app

COPY package.json yarn.lock* ./
RUN if [ -e yarn.lock ]; then yarn; else npm install; fi
COPY . .
EXPOSE 3000

# CMD để chạy lệnh mặc định khi container khởi động
CMD ["yarn", "dev"]