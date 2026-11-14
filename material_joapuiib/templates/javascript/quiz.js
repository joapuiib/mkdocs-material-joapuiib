/* Interactive `/// quiz` blocks (see material_joapuiib/extensions/quiz.py).
 *
 * A wrong option is marked and disabled; the solution and the explanation are
 * only revealed once every correct option has been chosen. With several
 * correct options (multiple choice) a hint tells how many there are. Each answered quiz
 * dispatches a bubbling `quiz:answered` event with `{ firstTry }` in `detail`.
 */
(function () {
  "use strict";

  var MESSAGES = {
    ca: {
      correct: "Correcte!",
      retry: "Ara sí!",
      wrong: "Incorrecta. Torna-ho a provar.",
      partial: "Correcta! Encara en falta alguna.",
      multiple: "Hi ha {n} respostes correctes.",
    },
    es: {
      correct: "¡Correcto!",
      retry: "¡Ahora sí!",
      wrong: "Incorrecta. Vuelve a intentarlo.",
      partial: "¡Correcta! Aún falta alguna.",
      multiple: "Hay {n} respuestas correctas.",
    },
    en: {
      correct: "Correct!",
      retry: "That's it!",
      wrong: "Wrong. Try again.",
      partial: "Correct! There are more to find.",
      multiple: "There are {n} correct answers.",
    },
  };

  function messages() {
    var lang = (document.documentElement.lang || "en").slice(0, 2).toLowerCase();
    return MESSAGES[lang] || MESSAGES.en;
  }

  function shuffle(list) {
    var items = Array.prototype.slice.call(list.children);
    for (var i = items.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = items[i]; items[i] = items[j]; items[j] = t;
    }
    items.forEach(function (item) { list.appendChild(item); });
  }

  function setup(quiz) {
    if (quiz.dataset.quizReady) return;
    quiz.dataset.quizReady = "true";

    var list = quiz.querySelector(".quiz-options");
    if (!list) return;
    if (quiz.hasAttribute("data-quiz-shuffle")) shuffle(list);

    var options = Array.prototype.slice.call(list.querySelectorAll(".quiz-option"));
    var pending = options.filter(function (o) { return o.hasAttribute("data-quiz-correct"); }).length;
    var firstTry = true;

    if (pending > 1) {
      quiz.classList.add("quiz--multiple");
      var hint = document.createElement("p");
      hint.className = "quiz-hint";
      hint.textContent = messages().multiple.replace("{n}", pending);
      list.insertAdjacentElement("beforebegin", hint);
    }

    var feedback = document.createElement("div");
    feedback.className = "quiz-feedback";
    feedback.setAttribute("aria-live", "polite");
    list.insertAdjacentElement("afterend", feedback);

    function say(type, text) {
      feedback.className = "quiz-feedback quiz-feedback--" + type;
      feedback.textContent = text;
    }

    function choose(option) {
      if (quiz.classList.contains("is-solved") || option.getAttribute("aria-disabled") === "true") return;
      option.setAttribute("aria-disabled", "true");
      option.tabIndex = -1;
      var msg = messages();

      if (!option.hasAttribute("data-quiz-correct")) {
        firstTry = false;
        option.classList.add("is-wrong");
        say("wrong", msg.wrong);
        return;
      }

      option.classList.add("is-correct");
      pending--;
      if (pending > 0) {
        say("correct", msg.partial);
        return;
      }

      quiz.classList.add("is-solved");
      options.forEach(function (o) {
        o.setAttribute("aria-disabled", "true");
        o.tabIndex = -1;
      });
      say("correct", firstTry ? msg.correct : msg.retry);
      quiz.dispatchEvent(new CustomEvent("quiz:answered", {
        bubbles: true,
        detail: { firstTry: firstTry },
      }));
    }

    options.forEach(function (option) {
      option.setAttribute("role", "button");
      option.tabIndex = 0;
      option.addEventListener("click", function (ev) {
        if (ev.target.closest("a")) return;
        choose(option);
      });
      option.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          choose(option);
        }
      });
    });
  }

  function init() {
    document.querySelectorAll(".quiz").forEach(setup);
  }

  if (window.document$) window.document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
