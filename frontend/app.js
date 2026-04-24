document.addEventListener("DOMContentLoaded", () => {

    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const resultado = document.getElementById("resultado");
    const inputNombre = document.getElementById("nombre");

    let ultimaImagen = null;
    let procesando = false; // 🔥 evita múltiples requests

    inputNombre.style.display = "none";

    // =========================
    // 🎥 INICIAR CÁMARA
    // =========================
    async function iniciarCamara() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;

            // 🔥 esperar que cargue bien la cámara
            video.onloadedmetadata = () => {
                setTimeout(reconocer, 1500);
            };

        } catch (error) {
            resultado.innerText = "❌ No se pudo acceder a la cámara";
        }
    }

    iniciarCamara();

    // =========================
    // 📸 CAPTURAR IMAGEN
    // =========================
    function capturar() {
        if (!video.videoWidth) {
            resultado.innerText = "⚠️ Espera la cámara...";
            return null;
        }

        const ctx = canvas.getContext("2d");

        // 🔥 reducir tamaño = más rápido backend
        canvas.width = 300;
        canvas.height = 300;

        ctx.drawImage(video, 0, 0, 300, 300);

        ultimaImagen = canvas.toDataURL("image/jpeg", 0.7); // 🔥 menor peso
        return ultimaImagen;
    }

    // =========================
    // 🔍 RECONOCER
    // =========================
    window.reconocer = async function () {

        if (procesando) return; // 🔥 evita spam
        procesando = true;

        const imagen = capturar();
        if (!imagen) {
            procesando = false;
            return;
        }

        resultado.innerText = "🔎 Analizando rostro...";

        try {
            const res = await fetch("http://127.0.0.1:5000/reconocer", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ imagen })
            });

            const data = await res.json();
            resultado.innerText = data.mensaje;

            if (data.mensaje.toLowerCase().includes("denegado")) {

                const opcion = confirm("😅 No te reconozco.\n\n¿Quieres registrarte?\n(Aceptar = Registrar / Cancelar = Reintentar)");

                if (opcion) {
                    inputNombre.style.display = "inline-block";
                    inputNombre.focus();
                } else {
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

        if (!nombre) {
            inputNombre.style.display = "inline-block";
            inputNombre.focus();
            resultado.innerText = "✍️ Escribe tu nombre";
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
            const res = await fetch("http://127.0.0.1:5000/usuarios", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ nombre, imagen })
            });

            const data = await res.json();

            resultado.innerText = "✅ " + data.mensaje;

            inputNombre.value = "";
            inputNombre.style.display = "none";

            // 🔥 reintento automático
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