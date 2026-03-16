// Función del Buscador
function buscarAlumno() {
    let input = document.getElementById("buscador");
    let filter = input.value.toUpperCase();
    let table = document.getElementById("miTabla");
    let tr = table.getElementsByTagName("tr");

    for (let i = 1; i < tr.length; i++) {
        let td = tr[i].getElementsByTagName("td")[0];
        if (td) {
            let txtValue = td.textContent || td.innerText;
            tr[i].style.display = (txtValue.toUpperCase().indexOf(filter) > -1) ? "" : "none";
        }
    }
}

// Función para Editar Nota
function editarRegistro(id, nombre) {
    let nuevaNota = prompt("Ingresa la nueva nota para " + nombre + " (Rango 1 a 10):");
    
    if (nuevaNota !== null) {
        let notaFloat = parseFloat(nuevaNota);
        if (notaFloat >= 1 && notaFloat <= 10) {
            document.getElementById('editId').value = id;
            document.getElementById('editNota').value = notaFloat;
            document.getElementById('formEdit').submit();
        } else {
            alert("⚠️ Error: La nota debe ser entre 1 y 10.");
        }
    }
}