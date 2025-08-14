// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from "@primeuix/themes/aura";
import PrimeUI from "tailwindcss-primeui";
import { definePreset } from "@primeuix/themes";
import { defineNuxtConfig } from "nuxt/config";
import type { TailwindCSSModuleOptions } from "@nuxtjs/tailwindcss";

const MyPreset = definePreset(Aura, {
  components: {
    card: {
      colorScheme: {
        light: {
          root: {
            background: "{surface.50}",
          },
        },
        dark: {
          root: {
            background: "{surface.800}",
          },
        },
      },
    },
    menubar: {
      colorScheme: {
        light: {
          root: {
            background: "{lime.50}",
          },
        },
        dark: {
          root: {
            background: "{gray.800}",
          },
        },
      },
    },
  },
});

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },

  modules: [
    "@nuxt/image",
    "@nuxt/eslint",
    "@pinia/nuxt",
    "@primevue/nuxt-module",
    "@nuxtjs/tailwindcss",
  ],

  css: [
    "primeicons/primeicons.css",
    "~/assets/css/tailwind.css",
    "~/assets/css/global.css",
  ],

  // 🌀 Tailwind CSS + PrimeUI 設定
  tailwindcss: <TailwindCSSModuleOptions>{
    config: {
      plugins: [PrimeUI],
      darkMode: ["class", ".p-dark"],
    },
  },

  // 🎨 PrimeVue 設定 + 客製主題
  primevue: {
    options: {
      theme: {
        preset: MyPreset,
        options: {
          prefix: "p",
          darkModeSelector: ".dark",
        },
      },
      ripple: true,
      unstyled: false,
    },
    autoImport: true,
    services: ["toast"],
  },

  // 🌐 環境變數
  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE || "http://localhost:8080",
    },
  },
});
