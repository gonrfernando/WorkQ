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
