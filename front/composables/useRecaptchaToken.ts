export const useRecaptchaToken = async (action = "signup") => {
  const recaptchaInstance = useNuxtApp().$recaptcha;
  await recaptchaInstance?.recaptchaLoaded();
  return await recaptchaInstance?.executeRecaptcha(action);
};
