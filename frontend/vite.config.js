import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        timeout: 600000,  // 10分钟，匹配 CPU 推理耗时
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  }
})
