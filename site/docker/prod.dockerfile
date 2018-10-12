FROM nginx:1.13.5-alpine

COPY nginx/nginx.conf /etc/nginx/

COPY dist/ /dist/

CMD ["nginx", "-g", "daemon off;"]
