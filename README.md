# 🏨 Plataforma de Reservas de Hoteles - Sistema Distribuido

## 📋 Descripción del Proyecto
Este proyecto es una plataforma distribuida para la gestión e infraestructura de reservas de hoteles, desarrollada bajo una arquitectura de microservicios. Cuenta con servicios independientes, bases de datos relacionales aisladas, comunicación síncrona mediante APIs REST y empaquetamiento completo en contenedores Docker.

---

## 👥 Equipo de Trabajo
* **Jonthán gallego**
* **Daniel Guzmán**

---

# PARTE 1 — ENTENDER EL PROBLEMA

## ¿Qué problema resuelve el sistema?
- Conectar viajeros con hoteles que tengan disponibilidad de servicios, gestionando registros de clientes e información hotelera de manera desacoplada.

## ¿Quién lo usará?
- Viajeros, clientes y administradores del sistema hotelero.

---

# PARTE 2 – IDENTIFICAR LOS SERVICIOS Y ESTADO DE IMPLEMENTACIÓN
El sistema se divide en servicios independientes. Actualmente, el proyecto cuenta con el **Segundo Avance de implementación** funcional:

| Módulo / Servicio | Estado Actual | Responsabilidad Principal | Base de Datos |
| :--- | :--- | :--- | :--- |
| **Vista Home** | **Implementado** | Interfaz web principal contenerizada (Nginx) | N/A (Frontend) |
| **Hoteles** | **Implementado** | Gestión del catálogo de hoteles y ubicaciones | MySQL (`mysql_hoteles`) |
| **Clientes** | **Implementado** | Gestión de usuarios y consumo cruzado del servicio de hoteles | MySQL (`mysql_clientes`) |
| **Habitaciones / Reservas** | Planeado / Futuro | Administración de disponibilidad y reservas | Por definir |
| **Pagos / Notificaciones** | Planeado (En rojo) | Módulos transaccionales y de avisos | Por definir |

---

# PARTE 3 – COMUNICACIÓN ENTRE SERVICIOS

## Conexión y Comunicación REST
- El microservicio de **Clientes** se comunica de forma síncrona con el microservicio de **Hoteles** mediante peticiones HTTP REST utilizando la red interna de Docker (`http://hoteles:5000`).
- Cuando se consulta el detalle de un cliente, el servicio de clientes extrae el `hotel_id` asociado y realiza una petición al servicio de hoteles para unificar la información en una sola respuesta JSON.

---

# PARTE 4 – ARQUITECTURA Y BASE DE DATOS

## Tipo de arquitectura
Elegimos una arquitectura basada en **Microservicios con contenedores Docker**, lo que permite aislar responsabilidades, escalar componentes de manera independiente y evitar puntos únicos de fallo globales.

graph TD
    %% Capa de Usuario y Frontend
    User([Usuario / Viajero]) -->|Accede via web| Home[Vista Principal / Home <br><i>Contenedor Nginx :8080</i>]

    %% Módulos Principales Implementados (Segundo Avance)
    Home -->|Consulta de datos| Hoteles[Microservicio Hoteles <br><i>Puerto 5001</i>]
    
    ClientAPI([Cliente / Postman]) --> Clientes[Microservicio Clientes <br><i>Puerto 5002</i>]
    ClientAPI --> Hoteles

    %% Red interna de Docker y Comunicación Inter-servicio
    subgraph Red Interna de Docker (Docker Compose)
        Clientes -->|Comunicación HTTP REST síncrona| Hoteles
        Clientes --> DBC[(Base de Datos <br>mysql_clientes)]
        Hoteles --> DBH[(Base de Datos <br>mysql_hoteles)]
    end

    %% Módulos futuros (Planeados)
    subgraph Módulos Futuros
        Habitaciones[Habitaciones] -.-> DBHab[(BD Habitaciones)]
        Reservas[Reservas] -.-> DBRes[(BD Reservas)]
        Pagos[Pagos - En rojo] -.-> DBPag[(BD Pagos)]
        Notis[Notificaciones - En rojo]
    end

    style Home fill:#2563eb,stroke:#fff,stroke-width:2px,color:#fff
    style Clientes fill:#0ea5e9,stroke:#fff,stroke-width:2px,color:#fff
    style Hoteles fill:#0ea5e9,stroke:#fff,stroke-width:2px,color:#fff
    style DBC fill:#334155,stroke:#fff,stroke-width:2px,color:#fff
    style DBH fill:#334155,stroke:#fff,stroke-width:2px,color:#fff

## Bases de Datos Aisladas
Cada microservicio implementado posee su propia instancia de base de datos MySQL gestionada mediante volúmenes de Docker, garantizando persistencia independiente:
- **Base de datos de Clientes:** Aislada y estructurada mediante scripts en la carpeta del servicio.
- **Base de datos de Hoteles:** Aislada y versionada mediante scripts en la carpeta `bases_datos/`.

---

# AVANCE DE IMPLEMENTACIÓN Y ESTRUCTURA DEL REPOSITORIO

### Estructura del repositorio
```text
PlataformaReservas_Hoteles/
├── home/                    # Vista principal (HOME) contenerizada con Nginx
│   ├── Dockerfile
│   ├── index.html
│   ├── script.js
│   └── style.css
├── clientes/                # Microservicio de Clientes (Flask + MySQL)
├── hoteles/                 # Microservicio de Hoteles (Flask + MySQL)
├── bases_datos/             # Scripts SQL de inicialización y estructura
├── docs/                    # Documentación y diagramas de arquitectura
├── docker-compose.yml       # Orquestación global de contenedores
└── README.md                # Documentación principal

Documentación de Endpoints (APIs REST)
🏨 Microservicio: Hoteles (http://localhost:5001)
GET /hoteles: Lista todos los hoteles registrados.

GET /hoteles/<id>: Consulta un hotel específico por su ID.

POST /hoteles: Registra un nuevo hotel.

PUT /hoteles/<id>: Actualiza la información de un hotel.

DELETE /hoteles/<id>: Elimina un registro de hotel.

👤 Microservicio: Clientes (http://localhost:5002)
GET /clientes: Lista todos los clientes registrados.

GET /clientes/<id>: Consulta un cliente específico.

POST /clientes: Registra un cliente asociándolo a un hotel_id.

PUT /clientes/<id>: Actualiza los datos de un cliente.

DELETE /clientes/<id>: Elimina un cliente.

GET /clientes/<id>/detalle: (Comunicación inter-servicio) Retorna los datos del cliente combinados con la información de su hotel obtenida vía API REST.

🚀 Cómo Ejecutar el Sistema
Clonar el repositorio y situarse en la raíz:

Bash
cd PlataformaReservas_Hoteles
Construir y levantar todos los contenedores (Microservicios, Bases de Datos y Home):

Bash
docker compose up --build -d
Acceso a los componentes:

Vista Principal (Home): http://localhost:8080

Microservicio Hoteles: http://localhost:5001/hoteles

Microservicio Clientes: http://localhost:5002/clientes