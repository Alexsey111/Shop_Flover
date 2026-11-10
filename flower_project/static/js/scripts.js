// Небольшой слой поверх форм: оценка в отзыве держится в пределах 1-5,
// форма не уходит дважды, финальное действие спрашивает подтверждение.
// Без зависимостей, подключается один раз в base_generic.html.
(function () {
  "use strict";

  function clampRating(field) {
    var value = Number(field.value);
    if (!value) {
      return;
    }
    if (value < 1) {
      field.value = 1;
    } else if (value > 5) {
      field.value = 5;
    }
  }

  function lockAfterSubmit(form) {
    var button = form.querySelector('button[type="submit"], input[type="submit"]');
    if (!button || form.dataset.submitted === "1") {
      return;
    }
    form.dataset.submitted = "1";
    button.disabled = true;
    // Если сервер вернул форму с ошибкой и страница не ушла, кнопку надо вернуть.
    window.setTimeout(function () {
      form.dataset.submitted = "0";
      button.disabled = false;
    }, 5000);
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('input[name="rating"]').forEach(function (field) {
      field.addEventListener("change", function () {
        clampRating(field);
      });
    });

    document.querySelectorAll("form").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        var confirmText = form.dataset.confirm;
        if (confirmText && !window.confirm(confirmText)) {
          event.preventDefault();
          return;
        }
        lockAfterSubmit(form);
      });
    });
  });
})();
