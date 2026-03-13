document.addEventListener("DOMContentLoaded", mostrarUsuarios)

async function registrarUsuario(){

const nombre=document.getElementById("nombre").value.trim()
const edad=document.getElementById("edad").value
const mensaje=document.getElementById("mensaje")

if(nombre===""||edad===""){
mensaje.innerHTML="❌ Completa todos los campos"
mensaje.style.color="red"
return
}

let categoria=""

if(edad<=12) categoria="Niño"
else if(edad<=17) categoria="Adolescente"
else if(edad<=64) categoria="Adulto"
else categoria="Persona Mayor"

try{

const res=await fetch("api.php",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({nombre,edad,categoria})
})

const data=await res.json()

if(data.status==="success"){

mensaje.innerHTML="✅ Usuario guardado"
mensaje.style.color="green"

document.getElementById("nombre").value=""
document.getElementById("edad").value=""

mostrarUsuarios()

}else{

mensaje.innerHTML="❌ Error al guardar"

}

}catch(e){

mensaje.innerHTML="❌ Error de conexión"

}

}

async function mostrarUsuarios(){

const tabla=document.getElementById("listaUsuarios")

try{

const res=await fetch("api.php")
const usuarios=await res.json()

tabla.innerHTML=""

usuarios.forEach(u=>{

tabla.innerHTML+=`
<tr>
<td>${u.nombre}</td>
<td>${u.edad}</td>
<td>${u.categoria}</td>
</tr>
`

})

}catch{

tabla.innerHTML="<tr><td colspan='3'>Error cargando datos</td></tr>"

}

}

async function limpiarDB(){

if(!confirm("¿Seguro que quieres borrar todos los registros?")) return

await fetch("api.php",{method:"DELETE"})

mostrarUsuarios()

}