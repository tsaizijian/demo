<template>
  <footer class="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white relative overflow-hidden">
    <!-- Background decoration -->
    <div class="absolute inset-0 bg-grid-white/5 bg-[size:20px_20px] opacity-50"></div>
    <div class="absolute top-0 left-1/4 w-32 h-32 bg-blue-500/10 rounded-full blur-xl"></div>
    <div class="absolute bottom-0 right-1/4 w-32 h-32 bg-purple-500/10 rounded-full blur-xl"></div>
    
    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid md:grid-cols-3 gap-8">
        <!-- Brand Section -->
        <div class="md:col-span-1">
          <div class="flex items-center space-x-3 mb-4">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
              <svg class="w-[24px] h-[24px] text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
              </svg>
            </div>
            <span class="text-xl font-bold">聊天室應用</span>
          </div>
          <p class="text-gray-300 text-sm leading-relaxed">
            連接世界的每一個瞬間，<br>體驗全新的即時通訊平台
          </p>
        </div>
        
        <!-- Quick Links -->
        <div class="md:col-span-1">
          <h3 class="text-lg font-semibold mb-4 text-white">快速連結</h3>
          <ul class="space-y-2">
            <li><a href="#" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">關於我們</a></li>
            <li><a href="#" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">服務條款</a></li>
            <li><a href="#" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">隱私政策</a></li>
            <li><a href="#" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">聯絡我們</a></li>
          </ul>
        </div>
        
        <!-- Contact Info -->
        <div class="md:col-span-1">
          <h3 class="text-lg font-semibold mb-4 text-white">聯絡資訊</h3>
          <div class="space-y-2">
            <p class="text-gray-300 text-sm flex items-center">
              <svg class="w-[16px] h-[16px] mr-[8px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
              support@chatroom.com
            </p>
            <p class="text-gray-300 text-sm flex items-center">
              <svg class="w-[16px] h-[16px] mr-[8px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              台北市信義區
            </p>
          </div>
        </div>
      </div>
      
      <!-- Divider -->
      <div class="border-t border-gray-700 mt-8 pt-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <p class="text-gray-400 text-sm">
            &copy; 2025 聊天室應用. All rights reserved.
          </p>
          <div class="flex space-x-4 mt-4 md:mt-0">
            <a href="#" class="text-gray-400 hover:text-white transition-colors duration-200">
              <svg class="w-[20px] h-[20px]" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M20 10c0-5.523-4.477-10-10-10S0 4.477 0 10c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V10h2.54V7.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V10h2.773l-.443 2.89h-2.33v6.988C16.343 19.128 20 14.991 20 10z" clip-rule="evenodd"></path>
              </svg>
            </a>
            <a href="#" class="text-gray-400 hover:text-white transition-colors duration-200">
              <svg class="w-[20px] h-[20px]" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84"></path>
              </svg>
            </a>
            <a href="#" class="text-gray-400 hover:text-white transition-colors duration-200">
              <svg class="w-[20px] h-[20px]" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clip-rule="evenodd"></path>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>