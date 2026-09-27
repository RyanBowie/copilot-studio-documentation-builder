(() => {
  const toggle = document.querySelector("#theme-toggle");
  const updateLabel = () => {
    const dark = document.documentElement.dataset.theme === "dark";
    toggle.textContent = dark ? "Light theme" : "Dark theme";
    toggle.setAttribute("aria-label", `Switch to ${dark ? "light" : "dark"} theme`);
  };
  toggle.hidden = false;
  updateLabel();
  toggle.addEventListener("click", () => {
    document.documentElement.dataset.theme =
      document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    updateLabel();
  });

  const filters = document.querySelectorAll("[data-filter]");
  const cards = document.querySelectorAll("[data-category]");
  const count = document.querySelector("#result-count");
  document.querySelector("#result-filters").hidden = false;
  filters.forEach((button) => {
    button.addEventListener("click", () => {
      const selected = button.dataset.filter;
      filters.forEach((item) => {
        item.setAttribute("aria-pressed", String(item === button));
      });
      let visible = 0;
      cards.forEach((card) => {
        card.hidden = selected !== "all" && card.dataset.category !== selected;
        if (!card.hidden) visible += 1;
      });
      count.textContent = `${visible} evidence cases shown`;
    });
  });
})();
