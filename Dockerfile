FROM nginx:latest

COPY *.png *.json *.js *.html /usr/share/nginx/html
COPY public /usr/share/nginx/html/public