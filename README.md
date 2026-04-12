# Sistema de Gestión — Salón de Eventos
Sistema integral para la administración de reservas, pagos y comunicaciones de un salón de eventos. Incluye frontend en React, API REST con Flask, base de datos PostgreSQL, caché Redis, y orquestación completa con Docker y Traefik.

<p align="center">
  <img src="https://img.shields.io/badge/React_+_Vite-e0f7fa?style=flat&logo=react&logoColor=black&labelColor=e0f7fa&color=e0f7fa" alt="React + Vite" />
  <img src="https://img.shields.io/badge/Flask-e8f5e9?style=flat&logo=flask&logoColor=black&labelColor=e8f5e9&color=e8f5e9" alt="Flask" />
  <img src="https://img.shields.io/badge/PostgreSQL-efebe9?style=flat&logo=postgresql&logoColor=black&labelColor=efebe9&color=efebe9" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-ffebee?style=flat&logo=redis&logoColor=black&labelColor=ffebee&color=ffebee" alt="Redis" />
  <img src="https://img.shields.io/badge/Docker-fff3e0?style=flat&logo=docker&logoColor=black&labelColor=fff3e0&color=fff3e0" alt="Docker" />
  <img src="https://img.shields.io/badge/Traefik-f1f8e9?style=flat&logo=traefik&logoColor=black&labelColor=f1f8e9&color=f1f8e9" alt="Traefik" />
</p>

<div align="center">

| Frontend | Backend | Base de datos | Caché | Infraestructura | Notificaciones |
|----------|--------|---------------|-------|---------------|-----------------|
| React + Vite | Flask (Python) | PostgreSQL | Redis | Docker + Traefik | Telegram + Email |

</div>

## Requisitos previos
- Docker y Docker Compose instalados
- Node.js 18+ (solo para desarrollo frontend local)
- Acceso SSH al servidor (KVM)
- Archivo .env correctamente configurado en App/


## Entorno de desarrollo local
### Frontend (React + Vite)
El servidor de desarrollo de Vite permite ver cambios en tiempo real con hot-reload. Para levantarlo:

```bash
cd frontend
npm install
npm run dev
```
>Vite consume RAM de forma considerable en modo desarrollo.
>Cerrarlo cuando no esté en uso activo.

#### Para generar una build de producción optimizada (archivos estáticos):
```bash
npm run build
```

### Backend, base de datos e infraestructura (Docker)
El stack completo —PostgreSQL, Redis, Traefik y la aplicación Flask— está orquestado con Docker Compose.
>Deben asegurarse de tener el archivo .env configurado dentro de App/ antes de ejecutar cualquier comando de Docker.
```bash
# Levantar todos los servicios y reconstruir imágenes
docker compose -f App/docker-compose.yml up --build

# Detener servicios y destruir volúmenes (reset completo de la base de datos)
docker compose -f App/docker-compose.yml down -v
```

## Despliegue en producción (KVM)
Acceso al servidor
```bash
ssh root@<IP_DEL_SERVIDOR>
```
Actualizar desde el repositorio
```bash
# 1. Traer los cambios más recientes
git pull origin main

# 2. Reconstruir la imagen del frontend (solo cambios de frontend)
docker compose -f App/docker-compose.yml build frontend

# 3. Ver logs de la aplicación
docker logs salon_app --tail 50
```

## Configuración de variables de entorno
El archivo .env debe crearse en App/ a partir del template .env.example incluido en el repositorio. 
A continuación describiremos los bloques principales:
<div align="center">
  
| Flask | PostgreSQL | Redis | JWT |
|------|------------|-------|-----|
| Entorno de ejecución | Credenciales y URIs | Host, puerto y contraseña | Clave secreta de tokens |

</div>

<div align="center"> 
  
| Email / SMTP | Telegram | Sentry | Dialogflow | Backups |
|-------------|----------|--------|------------|--------|
| Gmail + App Password | Bot token + Chat IDs | DSN del backend | Credenciales Google SA | Contraseña AES + Rclone |

</div>

>Nunca debemos subir el .env al repositorio. Debemos verificar que este este en el .gitignore para no subir las credenciales.

## Sistema de backups automáticos
El servidor ejecuta backup.sh cada madrugada. Los backups de PostgreSQL se cifran con AES-256 y se sincronizan con Google Drive mediante Rclone.
#### Instalar Rclone
```bash
sudo -v ; curl https://rclone.org/install.sh | sudo bash
```
#### Configurar remote de Google Drive
```bash
rclone config
```
Dado que el servidor es una KVM sin navegador, la autorización con Google se realiza desde una máquina local:

1. En la KVM: iniciar el asistente y crear un nuevo remote llamado gdrive. Indicar que no hay navegador disponible.
2. En la máquina local (con Rclone instalado): ejecutar el comando rclone authorize "drive" que indique la KVM.
3. Autorizar el acceso en el navegador que se abre en la máquina local.
4. Copiar el token generado en la terminal local y pegarlo de vuelta en la KVM.

>El destino de Rclone se configura mediante la variable RCLONE_DESTINO en el .env. Por defecto este sera: gdrive:Backups_Salon/

## Estructura del repositorio:
```bash
salon-de-eventos/
├── App/            
│   └── ...         # Código del backend (Flask, lógica, rutas, etc.)
│
├── frontend/       
│   └── ...         # Aplicación cliente (React + Vite)
│
├── .env            
├── .gitignore      
└── README.md       
```
