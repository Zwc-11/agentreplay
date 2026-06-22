FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./
COPY apps/web ./apps/web
COPY packages ./packages
RUN npm ci
WORKDIR /app/apps/web
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host"]
