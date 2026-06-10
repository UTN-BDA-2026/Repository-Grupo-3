# Usamos una imagen liviana de Nginx
FROM nginx:stable-alpine

# Borramos los archivos por defecto de nginx
RUN rm -rf /usr/share/nginx/html/*

# Copiamos TU carpeta dist al directorio que sirve Nginx
# El primer "dist" es tu carpeta local, el segundo es el destino en el contenedor
COPY dist /usr/share/nginx/html

# Exponemos el puerto 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]