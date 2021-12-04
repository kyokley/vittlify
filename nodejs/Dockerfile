ARG NODE_IMAGE=node:latest

FROM ${NODE_IMAGE} AS vittlify-node
WORKDIR /code
COPY . /code
RUN npm install
CMD ["node", "/code/vittlify.js"]
