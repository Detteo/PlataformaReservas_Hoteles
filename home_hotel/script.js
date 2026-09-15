// ==========================================
// CONFIGURACIÓN DE APIS (PUERTOS DIRECTOS)
// ==========================================
const API = {
    usuarios: "http://localhost:3000",
    hoteles: "http://localhost:3307",
    reservas: "http://localhost:3308"
};

// ==========================================
// INICIALIZACIÓN DE EVENTOS
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    const botonBuscar = document.getElementById("buscar-button");
    
    if (botonBuscar) {
        botonBuscar.addEventListener("click", gestionarBusqueda);
    }
});

// ==========================================
// CONTROLADOR DE BÚSQUEDA
// ==========================================
function gestionarBusqueda() {
    const selectServicio = document.getElementById("service-select");
    if (!selectServicio) return;

    const servicio = selectServicio.value;

    if (servicio === "usuarios") {
        obtenerUsuarios();
    } else if (servicio === "hoteles") {
        obtenerHoteles();
    } else if (servicio === "reservas") {
        obtenerReservas();
    }
}

// ==========================================
// SERVICIO DE USUARIOS (Puerto 3000)
// ==========================================
async function obtenerUsuarios() {
    try {
        const respuesta = await fetch(API.usuarios);

        if (!respuesta.ok) {
            throw new Error("No se pudo obtener respuesta del servicio de usuarios");
        }

        const usuarios = await respuesta.json();
        console.log("Usuarios recibidos:", usuarios);
        mostrarUsuarios(usuarios);

    } catch (error) {
        console.error("Error al conectar con Usuarios:", error);
        mostrarMensaje("No se pudo conectar con el servicio de Usuarios (Puerto 3000). Asegúrate de que el contenedor Node esté corriendo.");
    }
}

function mostrarUsuarios(usuarios) {
    const contenedor = document.getElementById("hoteles-container");
    if (!contenedor) return;

    contenedor.innerHTML = "";

    if (!Array.isArray(usuarios) || usuarios.length === 0) {
        mostrarMensaje("No hay usuarios registrados para mostrar.");
        return;
    }

    usuarios.forEach(usuario => {
        const tarjeta = document.createElement("article");
        tarjeta.className = "hotel-result";
        tarjeta.innerHTML = `
            <h3>👤 ${usuario.nombre || "Usuario"}</h3>
            <p><strong>Email:</strong> ${usuario.email || "Sin email"}</p>
            <p style="color: #10b981; font-weight: bold; margin-top: 8px; font-size: 0.85rem;">
                ✔ Conectado exitosamente al contenedor Node (Puerto 3000)
            </p>
        `;
        contenedor.appendChild(tarjeta);
    });
}

// ==========================================
// SERVICIO DE HOTELES (Puerto 3307)
// ==========================================
async function obtenerHoteles() {
    try {
        const respuesta = await fetch(`${API.hoteles}/lista`);

        if (!respuesta.ok) {
            throw new Error("No se pudo obtener la lista de hoteles");
        }

        const hoteles = await respuesta.json();
        mostrarHoteles(hoteles);

    } catch (error) {
        console.error("Error al conectar con Hoteles:", error);
        mostrarMensaje("El contenedor de Hoteles en el puerto 3307 es una base de datos MySQL. Aún requiere una API web para responder consultas HTTP.");
    }
}

function mostrarHoteles(hoteles) {
    const contenedor = document.getElementById("hoteles-container");
    if (!contenedor) return;

    contenedor.innerHTML = "";

    if (!Array.isArray(hoteles) || hoteles.length === 0) {
        mostrarMensaje("No hay hoteles disponibles en este momento.");
        return;
    }

    hoteles.forEach(hotel => {
        const tarjeta = document.createElement("article");
        tarjeta.className = "hotel-result";
        tarjeta.innerHTML = `
            <h3>🏨 ${hotel.nombre || "Hotel"}</h3>
            <p>📍 ${hotel.ciudad || hotel.ubicacion || "Ubicación no disponible"}</p>
            <button onclick="reservarHotel(${hotel.id || 0})">Reservar</button>
        `;
        contenedor.appendChild(tarjeta);
    });
}

// ==========================================
// SERVICIO DE RESERVAS (Puerto 3308)
// ==========================================
async function obtenerReservas() {
    try {
        const respuesta = await fetch(`${API.reservas}/lista`);

        if (!respuesta.ok) {
            throw new Error("No se pudo obtener la lista de reservas");
        }

        const reservas = await respuesta.json();
        console.log("Reservas:", reservas);

    } catch (error) {
        console.error("Error al conectar con Reservas:", error);
        mostrarMensaje("El contenedor de Reservas en el puerto 3308 es una base de datos MySQL. Se requiere crear una API en Node/Python para exponer sus endpoints.");
    }
}

// ==========================================
// ACCIÓN DE RESERVA
// ==========================================
function reservarHotel(idHotel) {
    alert(`Hotel seleccionado ID: ${idHotel}.\n\nLa solicitud se procesará mediante el contenedor de Reservas (Puerto 3308).`);
}

// ==========================================
// MOSTRAR MENSAJES EN PANTALLA
// ==========================================
function mostrarMensaje(mensaje) {
    const contenedor = document.getElementById("hoteles-container");
    if (!contenedor) return;

    contenedor.innerHTML = `
        <div class="connection-message">
            <div class="connection-icon">⚡</div>
            <div>
                <h3>Estado del servicio</h3>
                <p>${mensaje}</p>
            </div>
        </div>
    `;
}