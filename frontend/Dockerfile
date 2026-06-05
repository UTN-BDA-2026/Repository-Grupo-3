# Etapa 1: Construcción (Build)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Etapa 2: Servidor de producción (Nginx)
FROM nginx:stable-alpine
# Copiamos los archivos construidos de la etapa anterior a Nginx
COPY --from=build /app/dist /usr/share/nginx/html
# Copiamos una configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]