document.addEventListener("DOMContentLoaded", () => {

    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const resultado = document.getElementById("resultado");
    const inputNombre = document.getElementById("nombre");

    const API_URL = "http://127.0.0.1:5000";

    let ultimaImagen = null;
    let procesando = false; // 🔥 controla concurrencia

    inputNombre.style.display = "none";


    // =========================
    // 🎥 INICIAR CÁMARA
    // =========================
    async function iniciarCamara() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;

            // 🔥 asegurar que la cámara esté lista
            video.onloadedmetadata = () => {
                setTimeout(reconocer, 1200);
            };

        } catch (error) {
            resultado.innerText = "❌ No se pudo acceder a la cámara";
            console.error(error);
        }
    }

    iniciarCamara();


    // =========================
    // 📸 CAPTURAR IMAGEN
    // =========================
    function capturar() {
        if (!video.videoWidth) {
            resultado.innerText = "⚠️ Esperando cámara...";
            return null;
        }

        const ctx = canvas.getContext("2d");

        canvas.width = 300;
        canvas.height = 300;

        ctx.drawImage(video, 0, 0, 300, 300);

        // 🔥 compresión para optimizar envío
        ultimaImagen = canvas.toDataURL("image/jpeg", 0.7);

        return ultimaImagen;
    }


    // =========================
    // 🔍 RECONOCER
    // =========================
    window.reconocer = async function () {

        if (procesando) return;
        procesando = true;

        const imagen = capturar();

        if (!imagen) {
            procesando = false;
            return;
        }

        resultado.innerText = "🔎 Analizando rostro...";

        try {
            const res = await fetch(`${API_URL}/reconocer`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ imagen })
            });

            // 🔥 validar respuesta HTTP
            if (!res.ok) {
                throw new Error("Error en servidor");
            }

            const data = await res.json();

            resultado.innerText = data.mensaje;

            const accesoDenegado = data.mensaje.toLowerCase().includes("denegado");

            if (accesoDenegado) {

                const opcion = confirm(
                    "😅 No te reconozco.\n\n¿Quieres registrarte?\n(Aceptar = Registrar / Cancelar = Reintentar)"
                );

                if (opcion) {
                    inputNombre.style.display = "inline-block";
                    inputNombre.focus();
                } else {
                    // 🔁 reintento automático
                    setTimeout(() => {
                        procesando = false;
                        reconocer();
                    }, 1500);
                    return;
                }

            } else {
                inputNombre.style.display = "none";
            }

        } catch (error) {
            resultado.innerText = "❌ Error en reconocimiento";
            console.error(error);
        }

        procesando = false;
    };


    // =========================
    // ➕ REGISTRAR
    // =========================
    window.registrar = async function () {

        if (procesando) return;
        procesando = true;

        const nombre = inputNombre.value.trim();

        // 🔥 validación básica
        if (!nombre || nombre.length < 2) {
            resultado.innerText = "✍️ Nombre inválido";
            inputNombre.style.display = "inline-block";
            inputNombre.focus();
            procesando = false;
            return;
        }

        const imagen = ultimaImagen || capturar();

        if (!imagen) {
            procesando = false;
            return;
        }

        resultado.innerText = "💾 Guardando rostro...";

        try {
            const res = await fetch(`${API_URL}/usuarios`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ nombre, imagen })
            });

            if (!res.ok) {
                throw new Error("Error en servidor");
            }

            const data = await res.json();

            resultado.innerText = "✅ " + data.mensaje;

            inputNombre.value = "";
            inputNombre.style.display = "none";

            // 🔁 intentar reconocer de nuevo automáticamente
            setTimeout(() => {
                procesando = false;
                reconocer();
            }, 1200);

            return;

        } catch (error) {
            resultado.innerText = "❌ Error al registrar";
            console.error(error);
        }

        procesando = false;
    };

});