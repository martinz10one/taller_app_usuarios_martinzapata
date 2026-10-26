import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
        },
    },
    server: {
        port: 5173,
        // En desarrollo, /api se redirige a la API: el navegador no ve dos orígenes
        proxy: {
            '/api': 'http://localhost:3000',
        },
    },
    preview: {
        port: 5173,
        // El build de producción también necesita el proxy para hablar con la API
        proxy: {
            '/api': 'http://localhost:3000',
        },
    },
})
