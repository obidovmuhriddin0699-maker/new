/* ==========================================================================
   inview.js — "call me once when this element reaches the screen".

   IntersectionObserver alone misses elements that are skipped over: a fast
   fling or a menu jump moves them from below the screen to above it without
   ever reporting them as intersecting, so they would stay hidden forever.
   A light scroll sweep catches those: anything whose top is already above
   the trigger line counts as seen.
   ========================================================================== */

/**
 * @param {Element[]} elements
 * @param {(el: Element) => void} onEnter  called exactly once per element
 * @param {number} line  trigger line as a fraction of the viewport height (0.82 = 18% from the bottom)
 */
export function onceInView(elements, onEnter, line = 0.88) {
  const pending = new Set(elements);
  if (!pending.size) return;

  const fire = (el) => {
    if (!pending.delete(el)) return;
    io?.unobserve(el);
    onEnter(el);
    if (!pending.size) stop();
  };

  const io = "IntersectionObserver" in window
    ? new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) fire(e.target); }),
        { rootMargin: `0px 0px -${Math.round((1 - line) * 100)}% 0px`, threshold: 0 })
    : null;
  pending.forEach((el) => io?.observe(el));

  let queued = false;
  const sweep = () => {
    queued = false;
    const limit = window.innerHeight * line;
    pending.forEach((el) => { if (el.getBoundingClientRect().top < limit) fire(el); });
  };
  const onScroll = () => { if (!queued) { queued = true; setTimeout(() => requestAnimationFrame(sweep), 120); } };
  function stop() {
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("resize", onScroll);
    io?.disconnect();
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  sweep();
}
