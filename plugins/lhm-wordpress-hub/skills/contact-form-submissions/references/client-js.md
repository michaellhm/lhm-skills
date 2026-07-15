# Client-Side Form JS — Reference Implementation

Add to `src/scripts/contact-form.js` (or inline in layout/page).

```js
// contact-form.js
// Intercepts [data-contact-form] submits, stamps a form_started_at timer,
// posts to /api/contact, renders Turnstile widgets, handles success/error states.

(function () {
  const TURNSTILE_SITE_KEY = document
    .querySelector('meta[name="turnstile-site-key"]')
    ?.getAttribute('content') || '';

  // Render Turnstile widgets into all forms
  function initTurnstile() {
    if (!window.turnstile || !TURNSTILE_SITE_KEY) return;
    document.querySelectorAll('[data-contact-form]').forEach(form => {
      const container = form.querySelector('[data-turnstile-container]');
      if (!container || container.dataset.widgetId) return;
      container.removeAttribute('hidden');
      const widgetId = window.turnstile.render(container, {
        sitekey: TURNSTILE_SITE_KEY,
        theme: 'light',
      });
      container.dataset.widgetId = widgetId;
    });
  }

  // Wait for Turnstile script to load
  if (window.turnstile) {
    initTurnstile();
  } else {
    const existing = document.querySelector('script[src*="turnstile"]');
    if (existing) {
      existing.addEventListener('load', initTurnstile);
    }
  }

  // Handle form submission
  document.querySelectorAll('[data-contact-form]').forEach(form => {
    let startedAt = form.querySelector('input[name="form_started_at"]');
    if (!startedAt) {
      startedAt = document.createElement('input');
      startedAt.type = 'hidden';
      startedAt.name = 'form_started_at';
      form.appendChild(startedAt);
    }
    startedAt.value = String(Date.now());

    form.addEventListener('submit', async function (e) {
      e.preventDefault();

      const thankYouUrl = form.dataset.thankYou;
      const submitBtn = form.querySelector('[type="submit"]');
      const errorEl = form.querySelector('[data-form-error]');

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = submitBtn.textContent;
        submitBtn.textContent = 'Sending…';
      }
      if (errorEl) errorEl.hidden = true;

      let res, data;
      try {
        res = await fetch('/api/contact', {
          method: 'POST',
          body: new FormData(form),
        });
        data = await res.json();
      } catch (err) {
        showError(form, errorEl, 'Network error. Please try again.');
        resetButton(submitBtn);
        resetTurnstile(form);
        return;
      }

      if (data.ok && thankYouUrl) {
        window.location.href = thankYouUrl;
        return;
      }

      // API returned ok: false or no thank-you URL
      showError(form, errorEl, data.message || 'Something went wrong. Please try again.');
      resetButton(submitBtn);
      resetTurnstile(form);
    });
  });

  function showError(form, errorEl, message) {
    if (errorEl) {
      errorEl.textContent = message;
      errorEl.hidden = false;
    } else {
      alert(message);
    }
  }

  function resetButton(btn) {
    if (!btn) return;
    btn.disabled = false;
    btn.textContent = btn.dataset.originalText || 'Send';
  }

  function resetTurnstile(form) {
    const container = form.querySelector('[data-turnstile-container]');
    if (!container || !window.turnstile) return;
    const widgetId = container.dataset.widgetId;
    if (widgetId) window.turnstile.reset(widgetId);
  }
})();
```

## Adding the error element to forms

Add inside each `<form>` where you want an inline error message:

```html
<p data-form-error hidden class="contact-form__error" role="alert" aria-live="polite"></p>
```

## Adding the timing field to forms

Add this hidden field inside every form. The client JS sets it on page load, and the server rejects submissions that arrive unrealistically quickly.

```html
<input type="hidden" name="form_started_at" value="">
```

## Loading the script

In `BaseLayout.astro` or the page:

```astro
<script src="/scripts/contact-form.js" defer></script>
```

Or, if bundling with Astro:

```astro
<script>
  import '../scripts/contact-form.js';
</script>
```
