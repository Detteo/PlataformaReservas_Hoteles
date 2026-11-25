// Configuración para apuntar al servicio de hoteles expuesto en Docker
// Nota: Si abres la página desde fuera de Docker, usa el puerto mapeado (5001)
const API_URL = "http://localhost:5001/hoteles";

document.getElementById("btn-cargar").addEventListener("click", async () => {
    const contenedor = document.getElementById("hoteles-container");
    contenedor.innerHTML = "<p class='loading'>Cargando datos desde el microservicio de hoteles...</p>";

    try {
        const respuesta = await fetch(API_URL);
        if (!respuesta.ok) {
            throw new Error("No se pudo conectar con el servicio de hoteles.");
        }
        
        const hoteles = await respuesta.json();

        if (hoteles.length === 0) {
            contenedor.innerHTML = "<p class='placeholder-text'>No hay hoteles registrados en la base de datos.</p>";
            return;
        }

        contenedor.innerHTML = "";
        hoteles.forEach(hotel => {
            const card = document.createElement("div");
            card.className = "hotel-card";
            card.innerHTML = `
                <h4>🏨 ${hotel.hotel}</h4>
                <p><strong>Ciudad:</strong> ${hotel.ciudad}</p>
                <p><strong>Dirección:</strong> ${hotel.direccion}</p>
            `;
            contenedor.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        contenedor.innerHTML = `
            <div class="error-box">
                <p>⚠️ Error al conectar con el backend de hoteles.</p>
                <small>Asegúrate de que los contenedores estén corriendo con <code>docker compose up</code>.</small>
            </div>
        `;
    }
});