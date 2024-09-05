
FROM node:14-alpine

WORKDIR /app

COPY package.json .
COPY server.js .
RUN npm install

EXPOSE 3000

# Use tini as an init process
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]

# Ensure all console output is unbuffered
ENV NODE_ENV=development
ENV NODE_OPTIONS="--unhandled-rejections=strict"

CMD ["node", "server.js"]
