document.addEventListener("DOMContentLoaded", () => {

    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const resultado = document.getElementById("resultado");
    const inputNombre = document.getElementById("nombre");

    let ultimaImagen = null;

    // 👁️ oculto al inicio
    inputNombre.style.display = "none";

    // 🎥 cámara
    async function iniciarCamara() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;

            // 🔥 auto reconocimiento después de cargar
            setTimeout(reconocer, 2000);

        } catch (error) {
            resultado.innerText = "❌ No se pudo acceder a la cámara";
        }
    }

    iniciarCamara();

    // 📸 capturar
    function capturar() {
        if (!video.videoWidth) {
            resultado.innerText = "⚠️ Espera la cámara...";
            return null;
        }

        const ctx = canvas.getContext("2d");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        ultimaImagen = canvas.toDataURL("image/png");
        return ultimaImagen;
    }

    // 🔍 reconocer
    window.reconocer = async function () {
        const imagen = capturar();
        if (!imagen) return;

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

                // 👇 popup elegante
                const opcion = confirm("😅 No te reconozco.\n\n¿Quieres registrarte?\n(Aceptar = Registrar / Cancelar = Reintentar)");

                if (opcion) {
                    inputNombre.style.display = "inline-block";
                    inputNombre.focus();
                } else {
                    setTimeout(reconocer, 1500); // 🔁 reintento automático
                }

            } else {
                inputNombre.style.display = "none";
            }

        } catch (error) {
            resultado.innerText = "❌ Error en reconocimiento";
            console.error(error);
        }
    };

    // ➕ registrar
    window.registrar = async function () {

        const nombre = inputNombre.value.trim();

        if (!nombre) {
            inputNombre.style.display = "inline-block";
            inputNombre.focus();
            resultado.innerText = "✍️ Escribe tu nombre";
            return;
        }

        const imagen = ultimaImagen || capturar();
        if (!imagen) return;

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

            // 🔥 después de registrar → probar reconocimiento automático
            setTimeout(reconocer, 1500);

        } catch (error) {
            resultado.innerText = "❌ Error al registrar";
            console.error(error);
        }
    };

});