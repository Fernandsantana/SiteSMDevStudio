const menu = document.querySelector(".menu-toggle");
const nav = document.querySelector("#nav");
const mobile = matchMedia("(max-width: 700px)");
function setMenu(open) {
  menu.setAttribute("aria-expanded", String(open));
  menu.textContent = open ? "Fechar" : "Menu";
  nav.dataset.collapsed = String(mobile.matches && !open);
}
menu.hidden = false;
setMenu(false);
menu.addEventListener("click", () =>
  setMenu(menu.getAttribute("aria-expanded") !== "true"),
);
nav.addEventListener("click", (event) => {
  if (event.target.closest("a")) setMenu(false);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menu.getAttribute("aria-expanded") === "true") {
    setMenu(false);
    menu.focus();
  }
});
mobile.addEventListener("change", () => setMenu(false));

const reduced = matchMedia("(prefers-reduced-motion: reduce)");
const motionToggle = document.querySelector(".motion-toggle");
let motionPaused = false;
function syncMotionToggle() {
  // Com redução de movimento no sistema não há animação para pausar.
  if (motionToggle) motionToggle.hidden = reduced.matches;
}
if (motionToggle) {
  syncMotionToggle();
  reduced.addEventListener("change", syncMotionToggle);
  motionToggle.addEventListener("click", () => {
    motionPaused = !motionPaused;
    motionToggle.setAttribute("aria-pressed", String(motionPaused));
    document.documentElement.dataset.motion = motionPaused
      ? "paused"
      : "running";
    document.dispatchEvent(new Event("motionchange"));
  });
}

const carousel = document.querySelector(".carousel");
if (carousel) {
  const slides = [...carousel.querySelectorAll(".slide")];
  const counter = document.querySelector("#slide-count");
  let current = 0;
  let timer;
  let visible = false;
  let hovering = false;
  let focused = false;
  let touching = false;
  function move(step) {
    current = (current + step + slides.length) % slides.length;
    carousel.scrollTo({
      left: slides[current].offsetLeft - slides[0].offsetLeft,
      behavior: reduced.matches ? "instant" : "smooth",
    });
  }
  function schedule() {
    clearInterval(timer);
    const automatic =
      !reduced.matches &&
      !motionPaused &&
      visible &&
      !hovering &&
      !focused &&
      !touching &&
      !document.hidden;
    counter.setAttribute("aria-live", automatic ? "off" : "polite");
    if (automatic) timer = setInterval(() => move(1), 6500);
  }
  function manual(step) {
    move(step);
    schedule();
  }
  document.querySelector(".prev").addEventListener("click", () => manual(-1));
  document.querySelector(".next").addEventListener("click", () => manual(1));
  carousel.addEventListener("keydown", (event) => {
    if (["ArrowLeft", "ArrowRight"].includes(event.key)) {
      event.preventDefault();
      manual(event.key === "ArrowRight" ? 1 : -1);
    }
  });
  carousel.addEventListener("pointerenter", (event) => {
    hovering = event.pointerType === "mouse";
    schedule();
  });
  carousel.addEventListener("pointerleave", () => {
    hovering = false;
    schedule();
  });
  carousel.addEventListener("focusin", () => {
    focused = true;
    schedule();
  });
  carousel.addEventListener("focusout", () => {
    focused = false;
    schedule();
  });
  carousel.addEventListener(
    "touchstart",
    () => {
      touching = true;
      schedule();
    },
    { passive: true },
  );
  for (const event of ["touchend", "touchcancel"])
    carousel.addEventListener(
      event,
      () => {
        touching = false;
        schedule();
      },
      { passive: true },
    );
  carousel.addEventListener(
    "scroll",
    () => {
      const width = slides[1].offsetLeft - slides[0].offsetLeft;
      current = Math.max(
        0,
        Math.min(slides.length - 1, Math.round(carousel.scrollLeft / width)),
      );
      counter.textContent =
        String(current + 1).padStart(2, "0") +
        " / " +
        String(slides.length).padStart(2, "0");
    },
    { passive: true },
  );
  new IntersectionObserver(
    (entries) => {
      visible =
        entries[0].isIntersecting && entries[0].intersectionRatio >= 0.4;
      schedule();
    },
    { threshold: [0, 0.4] },
  ).observe(carousel);
  reduced.addEventListener("change", schedule);
  document.addEventListener("visibilitychange", schedule);
  document.addEventListener("motionchange", schedule);
  schedule();
}
