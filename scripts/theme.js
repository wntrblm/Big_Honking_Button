document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    /* Add rel="external" to all external links. */
    document.querySelectorAll('a[href*="//"]').forEach((el) => {
        el.rel = "external " + el.rel;
    });

    /* Setup hamburger menus. */
    document.querySelectorAll(".navbar-burger").forEach((el) => {
        el.addEventListener("click", () => {
            // Get the target from the "data-target" attribute
            const target = el.dataset.target;
            const $target = document.getElementById(target);

            // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
            el.classList.toggle("is-active");
            $target.classList.toggle("is-active");
        });
    });

    /* Check for copy-to-clipboard buttons */
    document
        .querySelectorAll("button[data-clipboard-copy-target]")
        .forEach((el) => {
            el.addEventListener("click", () => {
                const target = document.getElementById(
                    el.dataset.clipboardCopyTarget
                );
                const originalInnerHtml = el.innerHTML;

                navigator.clipboard.writeText(target.value);
                el.innerHTML = '<span class="material-icons">done</span>';
                setTimeout(() => {
                    el.innerHTML = originalInnerHtml;
                }, 1000);
            });
        });

    /* Dark/light mode switching */
    const switcher = document.querySelector(".dark-mode-switch");
    let media_dark_scheme = window.matchMedia(
        "(prefers-color-scheme: dark)"
    ).matches;
    let stored_scheme = localStorage.getItem("color-scheme");
    let dark_scheme =
        stored_scheme === "dark" ||
        (stored_scheme !== "light" && media_dark_scheme);

    if (dark_scheme) {
        document.documentElement.classList.add("dark");
    }

    switcher.addEventListener("click", () => {
        if (dark_scheme) {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("color-scheme", "light");
            dark_scheme = false;
        } else {
            document.documentElement.classList.add("dark");
            localStorage.setItem("color-scheme", "dark");
            dark_scheme = true;
        }
    });
});
