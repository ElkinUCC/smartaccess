const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const resultado = document.getElementById("resultado");

// Activar cámara
navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
    video.srcObject = stream;
});

// Capturar imagen
function capturar() {
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0);

    const imagen = canvas.toDataURL("image/png");

    fetch("http://127.0.0.1:5000/usuarios", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nombre: "Juan",
            imagen: imagen
        })
    })
    .then(res => res.json())
    .then(data => {
        resultado.innerText = "Usuario registrado 👍";
    });
}

// Reconocer rostro
function reconocer() {
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0);

    const imagen = canvas.toDataURL("image/png");

    fetch("http://127.0.0.1:5000/reconocer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ imagen })
    })
    .then(res => res.json())
    .then(data => {
        resultado.innerText = data.mensaje;
    });
}