// Todas las peticiones pasan por el API Gateway
const GATEWAY_URL = "http://localhost:5000";

function mostrarMensaje(elementoId, texto, esError = false) {
    const el = document.getElementById(elementoId);
    el.textContent = texto;
    el.className = `feedback ${esError ? "err" : "ok"}`;
}

function seleccionarHotelParaReserva(hotelId) {
    document.getElementById("reserva-hotel-id").value = hotelId;
    document.getElementById("reservas").scrollIntoView({ behavior: "smooth" });
}

// Normaliza respuestas que vengan como [...] o como { clave: [...] }
function extraerLista(data, posiblesClaves) {
    if (Array.isArray(data)) return data;
    if (data && typeof data === "object") {
        for (const clave of posiblesClaves) {
            if (Array.isArray(data[clave])) return data[clave];
        }
        const primerArray = Object.values(data).find((val) => Array.isArray(val));
        if (primerArray) return primerArray;
    }
    return [];
}

// ==================== 1. CLIENTES (SOLO REGISTRO) ====================
document.getElementById("form-cliente").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
        nombre: document.getElementById("cliente-nombre").value.trim(),
        correo: document.getElementById("cliente-correo").value.trim(),
        telefono: document.getElementById("cliente-telefono").value.trim(),
    };

    try {
        const resp = await fetch(`${GATEWAY_URL}/clientes`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            throw new Error(data.mensaje || `Error HTTP ${resp.status} al registrar cliente.`);
        }

        const nuevoId = data.id ?? data.cliente_id ?? data.cliente?.id;
        if (nuevoId) {
            document.getElementById("reserva-cliente-id").value = nuevoId;
        }

        mostrarMensaje(
            "msg-cliente",
            nuevoId
                ? `Registro exitoso. Tu ID de cliente es ${nuevoId} (ya quedó cargado en Reservas).`
                : (data.mensaje || "Cliente registrado correctamente. Ahora elige un hotel para reservar.")
        );
        e.target.reset();
    } catch (error) {
        mostrarMensaje("msg-cliente", error.message, true);
    }
});

// ==================== 2. HOTELES (SOLO CONSULTA) ====================
async function cargarHoteles() {
    const contenedor = document.getElementById("hoteles-container");
    contenedor.innerHTML = "<p class='loading'>Cargando hoteles registrados...</p>";

    try {
        const respuesta = await fetch(`${GATEWAY_URL}/hoteles`);
        if (!respuesta.ok) {
            throw new Error(`El gateway respondió con estado ${respuesta.status}.`);
        }

        const data = await respuesta.json();
        const hoteles = extraerLista(data, ["hoteles", "data", "items", "resultados"]);

        if (hoteles.length === 0) {
            contenedor.innerHTML = "<p class='placeholder-text'>No hay hoteles registrados en el sistema.</p>";
            return;
        }

        contenedor.innerHTML = "";
        hoteles.forEach((hotel) => {
            const nombreHotel = hotel.hotel ?? hotel.nombre ?? "Hotel";
            const idHotel = hotel.id ?? hotel.hotel_id;
            const card = document.createElement("div");
            card.className = "item-card";
            card.innerHTML = `
                <h4>🏨 ${nombreHotel} ${idHotel ? `(ID: ${idHotel})` : ""}</h4>
                <p><strong>Ciudad:</strong> ${hotel.ciudad ?? "-"}</p>
                <p><strong>Dirección:</strong> ${hotel.direccion ?? "-"}</p>
                ${idHotel ? `<button type="button" class="btn primary small" onclick="seleccionarHotelParaReserva(${idHotel})">Reservar aquí</button>` : ""}
            `;
            contenedor.appendChild(card);
        });
    } catch (error) {
        console.error("Error cargando hoteles:", error);
        contenedor.innerHTML = `
            <div class="error-box">
                <p>⚠️ No se pudieron cargar los hoteles: ${error.message}</p>
                <small>Verifica que el gateway (puerto 5000) y el servicio de hoteles estén activos.</small>
            </div>
        `;
    }
}

document.getElementById("btn-cargar-hoteles").addEventListener("click", cargarHoteles);

// ==================== 3. RESERVAS ====================
async function cargarReservas() {
    const contenedor = document.getElementById("reservas-container");
    contenedor.innerHTML = "<p class='loading'>Cargando reservas desde el API Gateway...</p>";

    try {
        const respuesta = await fetch(`${GATEWAY_URL}/reservas`);
        if (!respuesta.ok) {
            throw new Error(`El gateway respondió con estado ${respuesta.status}.`);
        }

        const data = await respuesta.json();
        const reservas = extraerLista(data, ["reservas", "data", "items", "resultados"]);

        if (reservas.length === 0) {
            contenedor.innerHTML = "<p class='placeholder-text'>No hay reservas registradas aún.</p>";
            return;
        }

        contenedor.innerHTML = "";
        reservas.forEach((reserva) => {
            const entrada = String(reserva.fecha_entrada ?? "").slice(0, 10);
            const salida = String(reserva.fecha_salida ?? "").slice(0, 10);
            const card = document.createElement("div");
            card.className = "item-card";
            card.innerHTML = `
                <h4>📅 Reserva #${reserva.id ?? "-"}</h4>
                <p><strong>Cliente ID:</strong> ${reserva.cliente_id ?? "-"}</p>
                <p><strong>Hotel ID:</strong> ${reserva.hotel_id ?? "-"}</p>
                <p><strong>Entrada:</strong> ${entrada || "-"}</p>
                <p><strong>Salida:</strong> ${salida || "-"}</p>
                <span class="status-badge">${reserva.estado ?? "CONFIRMADA"}</span>
            `;
            contenedor.appendChild(card);
        });
    } catch (error) {
        console.error("Error cargando reservas:", error);
        contenedor.innerHTML = `
            <div class="error-box">
                <p>⚠️ No se pudieron cargar las reservas: ${error.message}</p>
                <small>Verifica que el gateway (puerto 5000) y el servicio de reservas estén activos.</small>
            </div>
        `;
    }
}

document.getElementById("btn-cargar-reservas").addEventListener("click", cargarReservas);

document.getElementById("form-reserva").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
        cliente_id: Number(document.getElementById("reserva-cliente-id").value),
        hotel_id: Number(document.getElementById("reserva-hotel-id").value),
        fecha_entrada: document.getElementById("reserva-entrada").value,
        fecha_salida: document.getElementById("reserva-salida").value,
        estado: document.getElementById("reserva-estado").value,
    };

    try {
        const resp = await fetch(`${GATEWAY_URL}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            throw new Error(data.mensaje || `Error HTTP ${resp.status} al crear reserva.`);
        }
        mostrarMensaje("msg-reserva", data.mensaje || "Reserva creada correctamente.");
        e.target.reset();
        await cargarReservas();
    } catch (error) {
        mostrarMensaje("msg-reserva", error.message, true);
    }
});

// Cargar hoteles y reservas al abrir la página
window.addEventListener("DOMContentLoaded", () => {
    cargarHoteles();
    cargarReservas();
});