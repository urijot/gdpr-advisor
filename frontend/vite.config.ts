import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	// Allow the dev server to respond behind the deploy platform's domain.
	// Harmless locally; required when running `vite dev` on Railway.
	server: {
		host: true,
		allowedHosts: true
	}
});
