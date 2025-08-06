export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig();
  const siteKey = config.public.recaptchaSiteKey;

  const loadScript = () =>
    new Promise<void>((resolve) => {
      if (window.grecaptcha) return resolve();
      const script = document.createElement("script");
      script.src = `https://www.google.com/recaptcha/api.js?render=${siteKey}`;
      script.onload = () => resolve();
      document.head.appendChild(script);
    });

  const recaptchaLoaded = async () => {
    await loadScript();
    await new Promise((resolve) => window.grecaptcha.ready(resolve));
  };

  const executeRecaptcha = async (action: string) => {
    await recaptchaLoaded();
    return await window.grecaptcha.execute(siteKey, { action });
  };

  nuxtApp.provide("recaptcha", {
    recaptchaLoaded,
    executeRecaptcha,
  });
});
