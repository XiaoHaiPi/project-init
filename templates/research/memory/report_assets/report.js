(function () {
  function storedTheme() {
    try {
      return window.localStorage.getItem("seg-report-theme");
    } catch (error) {
      return null;
    }
  }

  function saveTheme(theme) {
    try {
      window.localStorage.setItem("seg-report-theme", theme);
    } catch (error) {
      return;
    }
  }

  function systemTheme() {
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  function applyTheme(theme) {
    var nextTheme = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", nextTheme);
    document.querySelectorAll("[data-theme-label]").forEach(function (label) {
      label.textContent = nextTheme === "dark" ? "Dark" : "Light";
    });
  }

  function attachThemeToggle() {
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      button.addEventListener("click", function () {
        var current = document.documentElement.getAttribute("data-theme") || systemTheme();
        var nextTheme = current === "dark" ? "light" : "dark";
        applyTheme(nextTheme);
        saveTheme(nextTheme);
      });
    });
  }

  function labelTables() {
    document.querySelectorAll(".data-table").forEach(function (table) {
      var headers = Array.from(table.querySelectorAll("thead th")).map(function (th) {
        return th.textContent.trim() || "Field";
      });
      table.querySelectorAll("tbody tr").forEach(function (row) {
        Array.from(row.children).forEach(function (cell, index) {
          if (!cell.getAttribute("data-label")) {
            cell.setAttribute("data-label", headers[index] || "Field");
          }
        });
      });
    });
  }

  function sortDefaultTables() {
    document.querySelectorAll('[data-default-sort="run-time-desc"]').forEach(function (table) {
      var sortHeader = table.querySelector('[data-sort-key="run-time"]');
      var headers = Array.from(table.querySelectorAll("thead th"));
      var index = headers.indexOf(sortHeader);
      var body = table.querySelector("tbody");
      if (index < 0 || !body) {
        return;
      }
      Array.from(body.querySelectorAll("tr"))
        .sort(function (left, right) {
          var leftValue = Number(left.children[index].getAttribute("data-sort-value") || 0);
          var rightValue = Number(right.children[index].getAttribute("data-sort-value") || 0);
          return rightValue - leftValue;
        })
        .forEach(function (row) {
          body.appendChild(row);
        });
    });
  }

  function attachFilters() {
    document.querySelectorAll("[data-filter-input]").forEach(function (input) {
      var target = document.querySelector(input.getAttribute("data-filter-target"));
      if (!target) {
        return;
      }
      input.addEventListener("input", function () {
        var query = input.value.trim().toLowerCase();
        target.querySelectorAll("tbody tr").forEach(function (row) {
          var text = row.textContent.toLowerCase();
          row.hidden = query.length > 0 && text.indexOf(query) === -1;
        });
      });
    });
  }

  applyTheme(storedTheme() || systemTheme());
  labelTables();
  sortDefaultTables();
  attachFilters();
  attachThemeToggle();
})();
