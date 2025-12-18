FROM node:20-alpine

WORKDIR /app
COPY package.json tsconfig.json ./
RUN npm ci --silent || npm install --silent

COPY src ./src
RUN npm run build

ENV NODE_ENV=production
CMD ["npm","start"]
