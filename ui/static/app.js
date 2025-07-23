function restoreFile(file, inputId) {
    const snapshotDate = document.getElementById(inputId).value || "now";
    fetch("/restore", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ file_path: file, snapshot_date: snapshotDate })
    }).then(res => res.json()).then(data => {
        alert(data.success ? "Archivo restaurado correctamente." : "Error: " + data.error);
        if (data.success) location.reload();
    });
}

function previewFile(file) {
    fetch("/preview", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ file_path: file })
    }).then(res => res.json()).then(data => {
        document.getElementById("file-content").textContent = data.content || "No se pudo mostrar el contenido.";
    });
}

function downloadFile(file) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/download";
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "file_path";
    input.value = file;
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}
