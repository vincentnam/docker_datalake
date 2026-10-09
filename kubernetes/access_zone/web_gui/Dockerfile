# Kubernetes image of the web GUI, built from access_zone/web_gui by kubernetes/start.sh.
# Compose runs the React dev server (npm start) ; production serves the compiled build with nginx.

# ---------- build : React production bundle
FROM node:24-bookworm AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# REACT_APP_* are compiled into the bundle at build time (passed from conf.env by start.sh)
ARG REACT_APP_FLASK_APP_URL=/api
ARG REACT_APP_JUPYTERHUB_URL=
ENV REACT_APP_FLASK_APP_URL=$REACT_APP_FLASK_APP_URL \
    REACT_APP_JUPYTERHUB_URL=$REACT_APP_JUPYTERHUB_URL \
    GENERATE_SOURCEMAP=false
RUN npm run build

# ---------- runtime : static files served by an unprivileged nginx (uid 101, port 8080)
FROM nginxinc/nginx-unprivileged:1.28-alpine

COPY --from=build /app/build /usr/share/nginx/html
