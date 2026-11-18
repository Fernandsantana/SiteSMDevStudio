"use strict";
const contactForm = document.querySelector("#contact-form");
if (contactForm) {
  const status = document.querySelector("#contact-status");
  const submit = contactForm.querySelector('[type="submit"]');
  let busy = false;
  let requestId = crypto.randomUUID();
  contactForm.addEventListener("input", () => { requestId = crypto.randomUUID(); });
  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy || !contactForm.reportValidity()) return;
    busy = true;
    submit.disabled = true;
    contactForm.setAttribute("aria-busy", "true");
    status.dataset.state = "pending";
    status.textContent = "Enviando sua mensagem…";
    const controller = new AbortController();
    const submittedId = requestId;
    const timeout = setTimeout(() => controller.abort(), 25000);
    try {
      const response = await fetch(contactForm.action, {
        method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({ ...Object.fromEntries(new FormData(contactForm)), requestId: submittedId }),
        signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok) {
        status.dataset.state = "error";
        status.textContent = (result.message || "Não foi possível enviar agora") + " — seus dados foram mantidos";
        return;
      }
      status.dataset.state = result.preview ? "preview" : "success";
      status.textContent = result.message;
      if (!result.preview && requestId === submittedId) { contactForm.reset(); requestId = crypto.randomUUID(); }
    } catch (error) {
      status.dataset.state = "error";
      status.textContent = error.name === "AbortError"
        ? "Não conseguimos confirmar o envio a tempo — seus dados foram mantidos, tente novamente ou escreva para contato@smdevstudio.com.br"
        : "Não foi possível confirmar o envio — seus dados foram mantidos, tente novamente ou escreva para contato@smdevstudio.com.br";
    } finally {
      clearTimeout(timeout);
      busy = false;
      submit.disabled = false;
      contactForm.removeAttribute("aria-busy");
      status.focus({ preventScroll: true });
    }
  });
}
const menu = document.querySelector(".menu-toggle");
const nav = document.querySelector("#nav");
const mobile = matchMedia("(max-width: 700px)");
if (menu && nav) {
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
    if (
      event.key === "Escape" &&
      menu.getAttribute("aria-expanded") === "true"
    ) {
      setMenu(false);
      menu.focus();
    }
  });
  mobile.addEventListener("change", () => setMenu(false));
}
const comparison = document.querySelector(".comparison");
if (comparison) {
  comparison.querySelector(".segmented").hidden = false;
  comparison.querySelectorAll("button[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const custom = button.dataset.mode === "custom";
      comparison.dataset.mode = button.dataset.mode;
      comparison
        .querySelectorAll("button[data-mode]")
        .forEach((control) =>
          control.setAttribute("aria-pressed", String(control === button)),
        );
      comparison.querySelectorAll(".extra").forEach((module) => {
        module.hidden = custom;
      });
      comparison.querySelector(".custom-module").hidden = !custom;
      document.querySelector("#comparison-title").textContent = custom
        ? "O que sua equipe precisa"
        : "Uma estrutura para muitos negócios";
    });
  });
}
const moduleControls = document.querySelector(".module-controls");
if (moduleControls) {
  moduleControls.hidden = false;
  const controls = [...moduleControls.querySelectorAll("button[data-module]")];
  function toggleModule(button, active) {
    button.setAttribute("aria-pressed", String(active));
    button.querySelector("span").textContent = active ? "✓" : "+";
    document.getElementById(button.getAttribute("aria-controls")).hidden =
      !active;
  }
  controls.forEach((button) => {
    toggleModule(button, false);
    button.addEventListener("click", () => {
      toggleModule(button, button.getAttribute("aria-pressed") !== "true");
    });
  });
}

const reduced = matchMedia("(prefers-reduced-motion: reduce)");
function syncMotion() {
  document.documentElement.dataset.motion =
    reduced.matches || document.hidden ? "paused" : "running";
  document.dispatchEvent(new Event("motionchange"));
}
reduced.addEventListener("change", syncMotion);
document.addEventListener("visibilitychange", syncMotion);
syncMotion();
if ("IntersectionObserver" in window) {
  document.documentElement.classList.add("motion-ready");
  const regions = document.querySelectorAll(
    ".product-stage, .hero-checks, .statement-strip, .showcase-card",
  );
  regions.forEach((element) => element.setAttribute("data-motion-region", ""));
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        entry.target.classList.toggle("is-visible", entry.isIntersecting);
        if (entry.isIntersecting && !entry.target.dataset.revealed) {
          entry.target.dataset.revealed = "true";
          if (
            !reduced.matches &&
            !entry.target.matches(".product-stage, .statement-strip")
          )
            entry.target.classList.add("reveal-in");
        }
      });
    },
    { threshold: 0.12 },
  );
  document
    .querySelectorAll(
      "[data-motion-region], .section-heading, .pain-grid article, .comparison, .module-builder, .steps article, .contact h2",
    )
    .forEach((element) => observer.observe(element));
}
let scrollFrame = 0;
function updateScrollProgress() {
  scrollFrame = 0;
  const height = document.documentElement.scrollHeight - innerHeight;
  document.documentElement.style.setProperty(
    "--scroll-progress",
    height > 0 ? scrollY / height : 0,
  );
}
window.addEventListener(
  "scroll",
  () => {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScrollProgress);
  },
  { passive: true },
);
window.addEventListener("resize", updateScrollProgress);
updateScrollProgress();
const carousel = document.querySelector(".showcase-grid");
if (carousel) {
  const slides = [...carousel.querySelectorAll(".showcase-card")];
  let current = 0;
  function updateCarousel() {
    const start = carousel.getBoundingClientRect().left;
    current = slides.reduce(
      (best, slide, index) =>
        Math.abs(slide.getBoundingClientRect().left - start) <
        Math.abs(slides[best].getBoundingClientRect().left - start)
          ? index
          : best,
      0,
    );
  }
  function move(step, automatic = false) {
    const target = automatic
      ? (current + 1) % slides.length
      : Math.max(0, Math.min(slides.length - 1, current + step));
    const offset =
      slides[target].getBoundingClientRect().left -
      carousel.getBoundingClientRect().left +
      carousel.scrollLeft;
    carousel.scrollTo({
      left: offset,
      behavior: reduced.matches ? "instant" : "smooth",
    });
  }
  carousel.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
      event.preventDefault();
      move(event.key === "ArrowRight" ? 1 : -1);
    }
  });
  // Mouse usa captura de ponteiro; no celular a rolagem continua nativa.
  let drag = null;
  carousel.addEventListener("pointerdown", (event) => {
    if (event.pointerType !== "mouse" || event.button !== 0) return;
    event.preventDefault();
    updateCarousel();
    drag = {
      pointerId: event.pointerId,
      x: event.clientX,
      scroll: carousel.scrollLeft,
      index: current,
    };
    carousel.classList.add("is-dragging");
    carousel.scrollTo({ left: carousel.scrollLeft, behavior: "instant" });
    carousel.setPointerCapture(event.pointerId);
    carousel.focus({ preventScroll: true });
  });
  carousel.addEventListener("pointermove", (event) => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    carousel.scrollLeft = drag.scroll + drag.x - event.clientX;
  });
  function finishDrag(event) {
    if (!drag || event.pointerId !== drag.pointerId) return;
    const gesture = drag;
    drag = null;
    updateCarousel();
    const distance = gesture.x - event.clientX;
    if (
      event.type === "pointerup" &&
      Math.abs(distance) > 60 &&
      current === gesture.index
    ) {
      current = Math.max(
        0,
        Math.min(slides.length - 1, gesture.index + Math.sign(distance)),
      );
    }
    carousel.classList.remove("is-dragging");
    move(0);
    if (carousel.hasPointerCapture(event.pointerId))
      carousel.releasePointerCapture(event.pointerId);
  }
  for (const event of ["pointerup", "pointercancel", "lostpointercapture"])
    carousel.addEventListener(event, finishDrag);
  carousel.addEventListener("dragstart", (event) => event.preventDefault());
  let frame = 0;
  carousel.addEventListener(
    "scroll",
    () => {
      if (!frame)
        frame = requestAnimationFrame(() => {
          frame = 0;
          updateCarousel();
        });
    },
    { passive: true },
  );
  window.addEventListener("resize", updateCarousel);
  updateCarousel();
  createPlayback(
    carousel,
    document.querySelector("#possibilidades"),
    () => move(1, true),
    6000,
  );
}

// Avanço contínuo visível, suspenso apenas durante gesto, aba oculta ou movimento reduzido.
function createPlayback(
  viewport,
  interactionRegion,
  advance,
  delay,
  isPaused = () => false,
  onState = () => {},
) {
  let visible = false;
  let touching = false;
  let suspended = false;
  let timer;
  function sync() {
    clearTimeout(timer);
    const playing =
      visible &&
      !touching &&
      !suspended &&
      !document.hidden &&
      !reduced.matches &&
      !isPaused();
    onState(playing);
    if (playing)
      timer = setTimeout(() => {
        advance();
        sync();
      }, delay);
  }
  const observer = new IntersectionObserver(
    ([entry]) => {
      visible = entry.isIntersecting && entry.intersectionRatio >= 0.35;
      sync();
    },
    { threshold: [0, 0.35] },
  );
  observer.observe(viewport);
  interactionRegion.addEventListener("pointerdown", () => {
    touching = true;
    sync();
  });
  for (const event of ["pointerup", "pointercancel", "lostpointercapture"])
    window.addEventListener(event, () => {
      if (touching) {
        touching = false;
        sync();
      }
    });
  interactionRegion.addEventListener("wheel", sync, { passive: true });
  viewport.addEventListener("scroll", sync, { passive: true });
  document.addEventListener("motionchange", sync);
  document.addEventListener("visibilitychange", sync);
  window.addEventListener("pagehide", () => {
    suspended = true;
    clearTimeout(timer);
    observer.disconnect();
  });
  window.addEventListener("pageshow", () => {
    suspended = false;
    observer.observe(viewport);
    sync();
  });
  return { sync };
}
const adaptiveGrid = document.querySelector(".adaptive-grid");
if (adaptiveGrid) {
  const stage = document.querySelector(".product-stage");
  const buttons = [...document.querySelectorAll("[data-profile]")];
  const profiles = ["sales", "management", "automation"];
  const captions = [
    "Pedidos em destaque, do cliente à entrega",
    "Relatórios em destaque, decisões conectadas",
    "Integrações em destaque, menos tarefas manuais",
  ];
  let currentProfile = 0;
  let animations = [];
  document.querySelector(".profile-controls").hidden = false;
  function settle() {
    animations.forEach((animation) => animation.finish());
    animations = [];
  }
  function showProfile(index) {
    settle();
    const modules = [...adaptiveGrid.children];
    const before = modules.map((module) => module.getBoundingClientRect());
    currentProfile = index;
    adaptiveGrid.dataset.layout = profiles[index];
    buttons.forEach((button) =>
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.profile === profiles[index]),
      ),
    );
    document.querySelector(".dashboard-note").textContent = captions[index];
    if (!reduced.matches) {
      animations = modules.map((module, i) => {
        const after = module.getBoundingClientRect();
        return module.animate(
          [
            {
              transform: `translate(${before[i].left - after.left}px, ${before[i].top - after.top}px) scale(${before[i].width / after.width}, ${before[i].height / after.height})`,
            },
            { transform: "none" },
          ],
          { duration: 850, easing: "cubic-bezier(.22,.7,.2,1)" },
        );
      });
    }
  }
  // Uma mudança de orientação encerra o FLIP antes de recalcular o grid.
  window.addEventListener("resize", settle);
  buttons.forEach((button, index) =>
    button.addEventListener("click", () => showProfile(index)),
  );
  createPlayback(
    stage,
    stage,
    () => showProfile((currentProfile + 1) % profiles.length),
    4200,
    () => false,
    (playing) => {
      if (!playing) settle();
    },
  );
}
