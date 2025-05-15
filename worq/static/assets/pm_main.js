
  document.getElementById('submit-button').addEventListener('click', async function () {
    const form = document.getElementById('create-project-form');
    const formData = new FormData(form);

    // Convertir FormData a un objeto JSON
    const jsonData = {};
    formData.forEach((value, key) => {
      jsonData[key] = value;
    });

    try {
      // Enviar los datos al servidor como JSON
      const response = await fetch('{{ request.route_url("pm_main") }}', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData),
      });

      if (response.ok) {
        const result = await response.json();
        alert('Project created successfully!');
        console.log(result);
        window.location.reload();
      } else {
        const error = await response.text();
        alert('Error: ' + error);
      }
    } catch (err) {
      console.error('Error:', err);
      alert('An unexpected error occurred.');
    }
  });
