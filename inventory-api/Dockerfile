# ---- base: install dependencies (copied first for layer caching) ----
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
# TIP: once a package-lock.json is committed, change this to `npm ci`
RUN npm install
COPY . .

# ---- test stage: run by Jenkins with `docker build --target test` ----
FROM base AS test
RUN npm test

# ---- production stage: small image, no dev dependencies, non-root ----
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm install --omit=dev && npm cache clean --force
COPY --from=base /app/src ./src
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health || exit 1
USER node
CMD ["node", "src/server.js"]
