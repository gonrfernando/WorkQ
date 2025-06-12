// Mostrar el popup
document.querySelector('.show-popup').addEventListener('click', () => {
  document.querySelector('.popup-container').classList.add('active');
});

// Cerrar el popup al hacer clic fuera o en el botón de cerrar
document.querySelectorAll('.popup-container, .close-btn').forEach((element) => {
  element.addEventListener('click', (e) => {
      if (e.target.classList.contains('popup-container') || e.target.classList.contains('close-btn')) {
          document.querySelector('.popup-container').classList.remove('active');
      }
  });
});

// Manejar la entrada de búsqueda en el formulario
function handleFormSearchInput(event) {
  const query = event.target.value.toLowerCase();
  const resultsContainer = document.getElementById("form-autocomplete-results");
  resultsContainer.innerHTML = "";

  if (query.length < 1) {
      resultsContainer.style.display = "none";
      return;
  }

  const filteredUsers = Object.values(users).filter(user =>
      user.email.toLowerCase().includes(query)
  );

  if (filteredUsers.length > 0) {
      resultsContainer.style.display = "block";
      filteredUsers.forEach(user => {
          const item = document.createElement("div");
          item.className = "autocomplete-item";
          item.textContent = user.email;
          item.onclick = () => {
              document.getElementById("form-search-input").value = user.email;
              document.getElementById("user_id").value = user.id;
              document.getElementById("name").value = user.name;
              document.getElementById("email").value = user.email;
              document.getElementById("country").value = user.country_id || "";
              document.getElementById("area").value = user.area_id || "";
              document.getElementById("role").value = user.role_id || "";

              // Actualizar el campo de teléfono sin el prefijo
              const selectedCountry = countries.find(c => c.id == user.country_id);
              if (selectedCountry && selectedCountry.prefix) {
                  // Eliminar el prefijo del número de teléfono si existe
                  const phoneWithoutPrefix = user.tel ? user.tel.replace(/^\+\d+\s*/, "") : "";
                  document.getElementById("tel").value = `+${selectedCountry.prefix} ${phoneWithoutPrefix}`;
              } else {
                  document.getElementById("tel").value = user.tel || "";
              }

              resultsContainer.style.display = "none";
          };
          resultsContainer.appendChild(item);
      });
  } else {
      resultsContainer.style.display = "none";
  }
}

// Manejar el envío del formulario de edición de usuario
document.getElementById('edit-user-form').addEventListener('submit', async function(event) {
  event.preventDefault(); // Evita que el formulario recargue la página

  // Obtén los datos del formulario
  const formData = new FormData(this);
  const jsonData = Object.fromEntries(formData.entries()); // Convierte a JSON

  // Agregar el prefijo al número de teléfono
  const selectedCountryId = document.getElementById("country").value;
  const selectedCountry = countries.find(c => c.id == selectedCountryId);
  if (selectedCountry && selectedCountry.prefix) {
      const phoneInput = document.getElementById("tel").value.replace(/^\+\d+\s*/, ""); // Elimina el prefijo actual
      jsonData.tel = `+${selectedCountry.prefix} ${phoneInput}`;
  }

  try {
      // Realiza la solicitud POST con fetch
      const response = await fetch(this.action, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(jsonData), // Enviar como JSON
      });

      // Asegúrate de que la respuesta sea JSON
      const result = await response.json();

      if (result.success) {
          // Muestra el popup de éxito
          const successModal = new bootstrap.Modal(document.getElementById('successModal'));
          successModal.show();
      } else {
          console.error('Error al guardar los cambios:', result.error || 'Unknown error');
          const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
          document.getElementById('errorMessage').innerText = result.error || 'Unknown error';
          errorModal.show();
      }
  } catch (error) {
      console.error('Error en la solicitud:', error);
      const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
      document.getElementById('errorMessage').innerText = 'Request failed!';
      errorModal.show();
  }
});

// Manejar el cambio en el campo de país para actualizar el prefijo del teléfono
document.getElementById("country").addEventListener("change", function() {
  const selectedCountryId = this.value;
  const selectedCountry = countries.find(c => c.id == selectedCountryId);

  if (selectedCountry && selectedCountry.prefix) {
      const telInput = document.getElementById("tel");
      const currentTel = telInput.value.replace(/^\+\d+\s*/, ""); // Elimina el prefijo actual si existe
      telInput.value = `+${selectedCountry.prefix} ${currentTel}`;
  }
});