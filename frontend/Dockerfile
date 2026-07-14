FROM node:20-alpine

WORKDIR /app/frontend

COPY packpage-lock.json packpage.json ./

RUN npm ci

COPY . .

EXPOSE 5173

CMD [ "npm", "run", "dev", "--host", "0.0.0.0", "--port", "5173" ]