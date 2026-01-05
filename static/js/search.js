document.addEventListener("DOMContentLoaded", function () {
  const input = document.querySelector('[data-search="input"]');
  const button = document.querySelector('[data-search="button"]');

  if (!input || !button) return; // если нет элементов, выходим

  button.addEventListener("click", function () {
    const query = input.value.trim(); // обрезаем пробелы

    if (query) {
      // только если не пусто
      // редирект на search/?q=value
      window.location.href = `/books/?q=${encodeURIComponent(query)}`;
    }
  });

  // Опционально: поиск по Enter
  input.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      const query = input.value.trim();
      if (query) {
        window.location.href = `/books/?q=${encodeURIComponent(query)}`;
      }
    }
  });
});
