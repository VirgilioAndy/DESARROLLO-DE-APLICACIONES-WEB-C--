const gallery = document.getElementById('gallery');
const addButton = document.getElementById('add-button');
const deleteButton = document.getElementById('delete-button');
const imageUrlInput = document.getElementById('image-url');

let selectedImage = null;

addButton.addEventListener('click', () => {
  const url = imageUrlInput.value.trim();
  if (!url) return alert('Por favor ingresa una URL válida.');

  const img = document.createElement('img');
  img.src = url;
  img.alt = 'Imagen agregada';

  img.addEventListener('click', () => {
    if (selectedImage) selectedImage.classList.remove('selected');
    img.classList.add('selected');
    selectedImage = img;
  });

  gallery.appendChild(img);
  imageUrlInput.value = '';
});

deleteButton.addEventListener('click', () => {
  if (selectedImage) {
    gallery.removeChild(selectedImage);
    selectedImage = null;
  } else {
    alert('Selecciona una imagen para eliminar.');
  }
});

imageUrlInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') addButton.click();
});
