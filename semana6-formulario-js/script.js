const form = document.getElementById('registroForm');
const enviarBtn = document.getElementById('enviarBtn');

const nombre = document.getElementById('nombre');
const correo = document.getElementById('correo');
const contrasena = document.getElementById('contrasena');
const confirmacion = document.getElementById('confirmacion');
const edad = document.getElementById('edad');

const nombreError = document.getElementById('nombreError');
const correoError = document.getElementById('correoError');
const contrasenaError = document.getElementById('contrasenaError');
const confirmacionError = document.getElementById('confirmacionError');
const edadError = document.getElementById('edadError');

function validarNombre() {
  if (nombre.value.trim().length < 3) {
    nombreError.textContent = "El nombre debe tener al menos 3 caracteres.";
    return false;
  }
  nombreError.textContent = "";
  return true;
}

function validarCorreo() {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!regex.test(correo.value.trim())) {
    correoError.textContent = "Correo electrónico no válido.";
    return false;
  }
  correoError.textContent = "";
  return true;
}

function validarContrasena() {
  const regex = /^(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$/;
  if (!regex.test(contrasena.value)) {
    contrasenaError.textContent = "Mínimo 8 caracteres, un número y un símbolo.";
    return false;
  }
  contrasenaError.textContent = "";
  return true;
}

function validarConfirmacion() {
  if (confirmacion.value !== contrasena.value) {
    confirmacionError.textContent = "Las contraseñas no coinciden.";
    return false;
  }
  confirmacionError.textContent = "";
  return true;
}

function validarEdad() {
  const valorEdad = parseInt(edad.value, 10);
  if (isNaN(valorEdad) || valorEdad < 18) {
    edadError.textContent = "Debes tener al menos 18 años.";
    return false;
  }
  edadError.textContent = "";
  return true;
}

function validarFormulario() {
  const esValido =
    validarNombre() &&
    validarCorreo() &&
    validarContrasena() &&
    validarConfirmacion() &&
    validarEdad();

  enviarBtn.disabled = !esValido;
}

form.addEventListener("input", validarFormulario);

form.addEventListener("submit", function (e) {
  e.preventDefault();
  alert("¡Formulario enviado correctamente!");
  form.reset();
  enviarBtn.disabled = true;
});
