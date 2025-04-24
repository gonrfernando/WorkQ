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

  let users = []; // Variable para almacenar los usuarios

  // Obtener usuarios desde el servidor
  function fetchUsers() {
      fetch('/api/users')
          .then(response => {
              if (!response.ok) {
                  throw new Error('Error al obtener los usuarios');
              }
              return response.json();
          })
          .then(data => {
              users = data; // Asignar los usuarios obtenidos
          })
          .catch(error => {
              console.error('Error:', error);
          });
  }
  
  // Llamar a fetchUsers al cargar la página
  document.addEventListener('DOMContentLoaded', fetchUsers);

// Función de búsqueda
function handleSearchInput(event) {
    const query = event.target.value.toLowerCase();
    const resultsContainer = document.getElementById("autocomplete-results");
    resultsContainer.innerHTML = ""; // Limpiar resultados anteriores

    if (query.length < 1) {
        resultsContainer.style.display = "none";
        return;
    }

    const filteredUsers = users.filter(user =>
        user.email.toLowerCase().includes(query)
    );

    if (filteredUsers.length > 0) {
        resultsContainer.style.display = "block";
        filteredUsers.forEach(user => {
            const item = document.createElement("div");
            item.className = "autocomplete-item";
            item.textContent = user.email;
            item.onclick = () => {
                document.getElementById("search-input").value = user.email;
                resultsContainer.style.display = "none";
            };
            resultsContainer.appendChild(item);
        });
    } else {
        resultsContainer.style.display = "none";
    }
}