const GATEWAY_URL = "http://localhost:5000";

function extraerLista(data, clavesProbables = []) {
    if (Array.isArray(data)) return data;
    if (data && typeof data === "object") {
        for (const k of clavesProbables) {
            if (Array.isArray(data[k])) return data[k];
        }
        const primerArray = Object.values(data).find((v) => Array.isArray(v));
        if (primerArray) return primerArray;
    }
    return [];
}

// ==================== 1. CLIENTE ====================
document.getElementById("form-cliente").addEventListener("submit", async (e) => {
    e.preventDefault();
    const inputNombre = document.getElementById("input-nombre-cliente");
    const cajaResultado = document.getElementById("resultado-cliente");
    const nombre = inputNombre.value.trim();

    if (!nombre) return;

    try {
        const resp = await fetch(`${GATEWAY_URL}/clientes`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre }),
        });

        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            throw new Error(data.mensaje || `Error ${resp.status} al crear cliente`);
        }

        const clienteId = data.id ?? data.cliente_id ?? data.cliente?.id ?? "?";
        const nombreCreado = data.nombre ?? data.cliente?.nombre ?? nombre;

        cajaResultado.className = "resultado-box ok";
        cajaResultado.textContent = `cliente ${nombreCreado} CREADO id:${clienteId}`;

        if (clienteId !== "?") {
            document.getElementById("input-cliente-id").value = clienteId;
        }

        inputNombre.value = "";
    } catch (err) {
        cajaResultado.className = "resultado-box err";
        cajaResultado.textContent = `Error: ${err.message}`;
    }
});

// ==================== 2. HOTELES ====================
async function cargarHoteles() {
    const contenedor = document.getElementById("lista-hoteles");
    contenedor.innerHTML = `<p class="muted">Cargando hoteles...</p>`;

    try {
        const resp = await fetch(`${GATEWAY_URL}/hoteles`);
        if (!resp.ok) {
            throw new Error(`Error ${resp.status} al consultar /hoteles`);
        }

        const data = await resp.json();
        const hoteles = extraerLista(data, ["hoteles", "data"]);

        if (hoteles.length === 0) {
            contenedor.innerHTML = `<p class="muted">No hay hoteles registrados.</p>`;
            return;
        }

        contenedor.innerHTML = "";
        hoteles.forEach((h) => {
            const card = document.createElement("div");
            card.className = "dato-card";
            card.innerHTML = `
                <p><strong>id:</strong> ${h.id ?? "-"}</p>
                <p><strong>hotel:</strong> ${h.hotel ?? h.nombre ?? "-"}</p>
                <p><strong>ciudad:</strong> ${h.ciudad ?? "-"}</p>
                <p><strong>direccion:</strong> ${h.direccion ?? "-"}</p>
            `;
            contenedor.appendChild(card);
        });
    } catch (err) {
        contenedor.innerHTML = `<div class="error-msg">No se pudieron cargar los hoteles: ${err.message}</div>`;
    }
}

document.getElementById("btn-cargar-hoteles").addEventListener("click", cargarHoteles);

// ==================== 3. RESERVAS ====================
async function cargarReservas() {
    const contenedor = document.getElementById("lista-reservas");
    contenedor.innerHTML = `<p class="muted">Cargando reservas...</p>`;

    try {
        const resp = await fetch(`${GATEWAY_URL}/reservas`);
        if (!resp.ok) {
            throw new Error(`Error ${resp.status} al consultar /reservas`);
        }

        const data = await resp.json();
        const reservas = extraerLista(data, ["reservas", "data"]);

        if (reservas.length === 0) {
            contenedor.innerHTML = `<p class="muted">No hay reservas registradas.</p>`;
            return;
        }

        contenedor.innerHTML = "";
        reservas.forEach((r) => {
            const card = document.createElement("div");
            card.className = "dato-card";
            card.innerHTML = `
                <p><strong>id:</strong> ${r.id ?? "-"}</p>
                <p><strong>cliente_id:</strong> ${r.cliente_id ?? "-"}</p>
                <p><strong>hotel_id:</strong> ${r.hotel_id ?? "-"}</p>
                <p><strong>fecha_entrada:</strong> ${r.fecha_entrada ?? "-"}</p>
                <p><strong>fecha_salida:</strong> ${r.fecha_salida ?? "-"}</p>
                <p><strong>estado:</strong> ${r.estado ?? "-"}</p>
            `;
            contenedor.appendChild(card);
        });
    } catch (err) {
        contenedor.innerHTML = `<div class="error-msg">No se pudieron cargar las reservas: ${err.message}</div>`;
    }
}

document.getElementById("btn-cargar-reservas").addEventListener("click", cargarReservas);

document.getElementById("form-reserva").addEventListener("submit", async (e) => {
    e.preventDefault();
    const cajaMsg = document.getElementById("mensaje-reserva");

    const payload = {
        cliente_id: Number(document.getElementById("input-cliente-id").value),
        hotel_id: Number(document.getElementById("input-hotel-id").value),
        fecha_entrada: document.getElementById("input-fecha-entrada").value,
        fecha_salida: document.getElementById("input-fecha-salida").value,
        estado: document.getElementById("select-estado").value,
    };

    try {
        const resp = await fetch(`${GATEWAY_URL}/reservas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            throw new Error(data.mensaje || `Error ${resp.status} al crear reserva`);
        }

        cajaMsg.className = "resultado-box ok";
        cajaMsg.textContent = `Reserva creada (id: ${data.id ?? "ok"}) · cliente_id: ${payload.cliente_id} · hotel_id: ${payload.hotel_id}`;

        await cargarReservas();
    } catch (err) {
        cajaMsg.className = "resultado-box err";
        cajaMsg.textContent = `Error: ${err.message}`;
    }
});

// Cargar hoteles y reservas al abrir la página
window.addEventListener("DOMContentLoaded", () => {
    cargarHoteles();
    cargarReservas();
});