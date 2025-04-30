document.querySelector('.show-popup').addEventListener('click', () => {
    document.querySelector('.popup-container').classList.add('active');
  });
  
  document.querySelectorAll('.popup-container, .close-btn').forEach((element) => {
    element.addEventListener('click', (e) => {
      if (e.target.classList.contains('popup-container') || e.target.classList.contains('close-btn')) {
        document.querySelector('.popup-container').classList.remove('active');
      }
    });
  });

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
                document.getElementById("tel").value = user.tel;
                document.getElementById("passw").value = user.passw;
                document.getElementById("country").value = user.country_id || ""; 
                document.getElementById("area").value = user.area_id || ""; 
                document.getElementById("role").value = user.role_id || ""; 
                resultsContainer.style.display = "none";
            };
            resultsContainer.appendChild(item);
        });
    } else {
        resultsContainer.style.display = "none";
    }
}

document.getElementById('edit-user-form').addEventListener('submit', async function(event) {
  event.preventDefault(); // Evita que el formulario recargue la página

  // Obtén los datos del formulario
  const formData = new FormData(this);
  const jsonData = Object.fromEntries(formData.entries()); // Convierte a JSON

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
          document.getElementById('success-popup').style.display = 'block';
      } else {
          console.error('Error al guardar los cambios:', result.error || 'Unknown error');
      }
  } catch (error) {
      console.error('Error en la solicitud:', error);
  }
});
