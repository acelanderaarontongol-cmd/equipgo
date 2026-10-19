FROM nginxinc/nginx-unprivileged:1.27-alpine
ARG BUILD_NUMBER=dev
COPY src/ /usr/share/nginx/html/
# Stamp the build number into the page so a deployment is visibly provable
USER root
RUN sed -i "s/__BUILD__/${BUILD_NUMBER}/g" /usr/share/nginx/html/index.html
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
