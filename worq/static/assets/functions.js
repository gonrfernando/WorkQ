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
    resultsContainer.innerHTML = ""; // Clear previous results

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
                document.getElementById("user_id").value = user.id; // Completa el campo oculto
                document.getElementById("name").value = user.name;
                document.getElementById("email").value = user.email;
                document.getElementById("tel").value = user.tel;
                document.getElementById("passw").value = user.passw;
                document.getElementById("country").value = user.country_id || ""; // Selecciona el país
                document.getElementById("area").value = user.area_id || ""; // Selecciona el área
                document.getElementById("role").value = user.role_id || ""; // Selecciona el rol
                resultsContainer.style.display = "none";
            };
            resultsContainer.appendChild(item);
        });
    } else {
        resultsContainer.style.display = "none";
    }
}