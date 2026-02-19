<script lang="ts">
	import { marked } from 'marked';
	import { tick } from 'svelte';

	marked.use({ breaks: true });

	interface Section {
		heading: string;
		content: string;
	}

	interface Message {
		role: 'user' | 'assistant';
		content: string;
		articles?: string[];
	}

	let idea = '';
	let isLoading = false;
	let messages: Message[] = [];
	let error = '';
	let chatContainer: HTMLDivElement;
	let textarea: HTMLTextAreaElement;
	let expandedSections = new Set<string>();

	const examples = [
		"An app that tracks users' location in real time",
		'A healthcare platform storing patient records',
		'An e-commerce site sharing data with advertisers',
		'A social network selling user data to third parties'
	];

	function renderMarkdown(text: string): string {
		return marked(text) as string;
	}

	// Split markdown text into sections by ## headings
	function parseSections(text: string): Section[] {
		const parts = text.split(/\n(?=## )/);
		return parts
			.map((part) => {
				const match = part.match(/^## (.+)\n?([\s\S]*)/);
				if (match) return { heading: match[1].trim(), content: match[2].trim() };
				return { heading: '', content: part.trim() };
			})
			.filter((s) => s.heading || s.content);
	}

	function toggleSection(msgIdx: number, secIdx: number) {
		const key = `${msgIdx}-${secIdx}`;
		const next = new Set(expandedSections);
		next.has(key) ? next.delete(key) : next.add(key);
		expandedSections = next;
	}

	async function handleSubmit() {
		if (!idea.trim() || isLoading) return;

		const userMessage = idea.trim();
		idea = '';
		error = '';
		if (textarea) textarea.style.height = 'auto';

		messages = [...messages, { role: 'user', content: userMessage }];
		isLoading = true;
		await tick();
		scrollToBottom();

		try {
			const response = await fetch('http://localhost:8000/advice', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ idea: userMessage })
			});

			if (response.ok) {
				const data = await response.json();
				messages = [
					...messages,
					{ role: 'assistant', content: data.advice, articles: data.relevant_articles }
				];
				// Auto-expand first section of the new response
				const msgIdx = messages.length - 1;
				const sections = parseSections(data.advice);
				const next = new Set(expandedSections);
				const firstSectionIdx = sections.findIndex((s) => s.heading);
				if (firstSectionIdx !== -1) next.add(`${msgIdx}-${firstSectionIdx}`);
				expandedSections = next;
			} else {
				const data = await response.json();
				error = data.detail ?? 'An error occurred.';
			}
		} catch (err) {
			console.error(err);
			error = 'Network error: check that the backend is running.';
		} finally {
			isLoading = false;
			await tick();
			scrollToBottom();
		}
	}

	function scrollToBottom() {
		if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSubmit();
		}
	}

	function autoResize(node: HTMLTextAreaElement) {
		function resize() {
			node.style.height = 'auto';
			node.style.height = Math.min(node.scrollHeight, 200) + 'px';
		}
		node.addEventListener('input', resize);
		return { destroy: () => node.removeEventListener('input', resize) };
	}

	function useExample(example: string) {
		idea = example;
		handleSubmit();
	}

	function clearChat() {
		messages = [];
		error = '';
		idea = '';
		expandedSections = new Set();
	}
</script>

<div class="app">
	<!-- Sidebar -->
	<aside class="sidebar">
		<div class="sidebar-top">
			<div class="logo">
				<div class="logo-icon">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
						<path
							d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.25C17.25 22.15 21 17.25 21 12V7L12 2z"
							fill="#2563eb"
							opacity="0.15"
							stroke="#2563eb"
							stroke-width="1.5"
						/>
						<path
							d="M9 12l2 2 4-4"
							stroke="#2563eb"
							stroke-width="1.5"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
				</div>
				<span class="logo-text">GDPR Advisor</span>
			</div>

			{#if messages.length > 0}
				<button class="new-chat-btn" on:click={clearChat}>
					<svg
						width="14"
						height="14"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2.5"
					>
						<line x1="12" y1="5" x2="12" y2="19" />
						<line x1="5" y1="12" x2="19" y2="12" />
					</svg>
					New Chat
				</button>
			{/if}
		</div>

		<div class="sidebar-bottom">
			<div class="disclaimer-card">
				<svg
					width="13"
					height="13"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					class="disclaimer-icon"
				>
					<circle cx="12" cy="12" r="10" />
					<line x1="12" y1="8" x2="12" y2="12" />
					<line x1="12" y1="16" x2="12.01" y2="16" />
				</svg>
				<p>Not legal advice. For informational purposes only.</p>
			</div>
		</div>
	</aside>

	<!-- Main -->
	<div class="main">
		<div class="chat-container" bind:this={chatContainer}>
			{#if messages.length === 0}
				<!-- Welcome screen -->
				<div class="welcome">
					<div class="welcome-icon">
						<svg width="36" height="36" viewBox="0 0 24 24" fill="none">
							<path
								d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.25C17.25 22.15 21 17.25 21 12V7L12 2z"
								fill="#2563eb"
								opacity="0.15"
								stroke="#2563eb"
								stroke-width="1.5"
							/>
							<path
								d="M9 12l2 2 4-4"
								stroke="#2563eb"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
					</div>
					<h1>GDPR Compliance Advisor</h1>
					<p>
						Describe your service idea and get a compliance overview based on the official GDPR
						regulation text.
					</p>
					<div class="examples-grid">
						{#each examples as example}
							<button class="example-card" on:click={() => useExample(example)}>
								<span>{example}</span>
								<svg
									width="13"
									height="13"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
								>
									<line x1="5" y1="12" x2="19" y2="12" />
									<polyline points="12 5 19 12 12 19" />
								</svg>
							</button>
						{/each}
					</div>
				</div>
			{:else}
				<div class="messages-list">
					{#each messages as message, msgIdx}
						<div class="message {message.role}">
							{#if message.role === 'assistant'}
								<div class="avatar ai-avatar">
									<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
										<path
											d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.25C17.25 22.15 21 17.25 21 12V7L12 2z"
											fill="#2563eb"
											opacity="0.15"
											stroke="#2563eb"
											stroke-width="1.5"
										/>
										<path
											d="M9 12l2 2 4-4"
											stroke="#2563eb"
											stroke-width="1.5"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
									</svg>
								</div>
							{:else}
								<div class="avatar user-avatar">You</div>
							{/if}

							<div class="message-body">
								{#if message.role === 'user'}
									<p class="user-text">{message.content}</p>
								{:else}
									{@const sections = parseSections(message.content)}

									{#if message.articles && message.articles.length > 0}
										<div class="articles-row">
											{#each message.articles as article}
												<span class="article-tag">{article}</span>
											{/each}
										</div>
									{/if}

									{#each sections as section, secIdx}
										{#if !section.heading}
											<!-- Intro text: always visible -->
											<div class="prose intro-prose">
												{@html renderMarkdown(section.content)}
											</div>
										{:else}
											<!-- Accordion section -->
											{@const key = `${msgIdx}-${secIdx}`}
										<div class="section-card" class:open={expandedSections.has(key)}>
												<button
													class="section-header"
													on:click={() => toggleSection(msgIdx, secIdx)}
												>
													<div class="section-header-left">
														<span class="section-dot"></span>
														<span class="section-title">{section.heading}</span>
													</div>
													<svg
														class="chevron"
														class:open={expandedSections.has(key)}
														width="14"
														height="14"
														viewBox="0 0 24 24"
														fill="none"
														stroke="currentColor"
														stroke-width="2.5"
													>
														<polyline points="9 18 15 12 9 6" />
													</svg>
												</button>
												{#if expandedSections.has(key)}
													<div class="section-body">
														<div class="prose">
															{@html renderMarkdown(section.content)}
														</div>
													</div>
												{/if}
											</div>
										{/if}
									{/each}
								{/if}
							</div>
						</div>
					{/each}

					{#if isLoading}
						<div class="message assistant">
							<div class="avatar ai-avatar">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
									<path
										d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.25C17.25 22.15 21 17.25 21 12V7L12 2z"
										fill="#2563eb"
										opacity="0.15"
										stroke="#2563eb"
										stroke-width="1.5"
									/>
									<path
										d="M9 12l2 2 4-4"
										stroke="#2563eb"
										stroke-width="1.5"
										stroke-linecap="round"
										stroke-linejoin="round"
									/>
								</svg>
							</div>
							<div class="message-body">
								<div class="typing-dots">
									<span></span><span></span><span></span>
								</div>
								<p class="analyzing-text">Analyzing against GDPR articles…</p>
							</div>
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Error -->
		{#if error}
			<div class="error-bar">
				<svg
					width="15"
					height="15"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<circle cx="12" cy="12" r="10" />
					<line x1="12" y1="8" x2="12" y2="12" />
					<line x1="12" y1="16" x2="12.01" y2="16" />
				</svg>
				{error}
				<button class="error-close" on:click={() => (error = '')}>✕</button>
			</div>
		{/if}

		<!-- Input -->
		<div class="input-area">
			<div class="input-box">
				<textarea
					bind:this={textarea}
					bind:value={idea}
					use:autoResize
					on:keydown={handleKeydown}
					placeholder="Describe your service idea..."
					rows={1}
					disabled={isLoading}
				></textarea>
				<button
					class="send-btn"
					on:click={handleSubmit}
					disabled={isLoading || !idea.trim()}
					aria-label="Send"
				>
					{#if isLoading}
						<svg
							class="spin"
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2.5"
						>
							<path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round" />
						</svg>
					{:else}
						<svg
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<line x1="22" y1="2" x2="11" y2="13" />
							<polygon points="22 2 15 22 11 13 2 9 22 2" />
						</svg>
					{/if}
				</button>
			</div>
			<p class="input-hint">Enter to send · Shift+Enter for new line</p>
		</div>
	</div>
</div>

<style>
	.app {
		display: flex;
		height: 100vh;
		background: #ffffff;
		color: #111827;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
	}

	/* ── Sidebar ────────────────────────────── */
	.sidebar {
		width: 240px;
		flex-shrink: 0;
		background: #f9fafb;
		border-right: 1px solid #e5e7eb;
		display: flex;
		flex-direction: column;
		padding: 1rem;
	}

	.sidebar-top {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.sidebar-bottom {
		margin-top: auto;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.4rem 0;
	}

	.logo-icon {
		width: 32px;
		height: 32px;
		background: #eff6ff;
		border: 1px solid #bfdbfe;
		border-radius: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.logo-text {
		font-size: 0.95rem;
		font-weight: 600;
		color: #111827;
		letter-spacing: -0.01em;
	}

	.new-chat-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.55rem 0.75rem;
		background: #ffffff;
		border: 1px solid #d1d5db;
		border-radius: 8px;
		color: #374151;
		font-size: 0.8rem;
		font-family: inherit;
		cursor: pointer;
		transition:
			background 0.15s,
			border-color 0.15s;
	}

	.new-chat-btn:hover {
		background: #f3f4f6;
		border-color: #9ca3af;
	}

	.disclaimer-card {
		display: flex;
		align-items: flex-start;
		gap: 0.45rem;
		padding: 0.65rem 0.75rem;
		background: #f3f4f6;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
	}

	.disclaimer-icon {
		flex-shrink: 0;
		margin-top: 1px;
		color: #9ca3af;
	}

	.disclaimer-card p {
		font-size: 0.72rem;
		color: #6b7280;
		line-height: 1.5;
	}

	/* ── Main ───────────────────────────────── */
	.main {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		min-width: 0;
	}

	.chat-container {
		flex: 1;
		overflow-y: auto;
		scroll-behavior: smooth;
	}

	.chat-container::-webkit-scrollbar {
		width: 5px;
	}

	.chat-container::-webkit-scrollbar-thumb {
		background: #d1d5db;
		border-radius: 3px;
	}

	/* ── Welcome ────────────────────────────── */
	.welcome {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 70vh;
		padding: 2rem 1.5rem;
		text-align: center;
	}

	.welcome-icon {
		width: 60px;
		height: 60px;
		background: #eff6ff;
		border: 1px solid #bfdbfe;
		border-radius: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 1.25rem;
	}

	.welcome h1 {
		font-size: 1.6rem;
		font-weight: 600;
		letter-spacing: -0.02em;
		margin-bottom: 0.6rem;
		color: #111827;
	}

	.welcome > p {
		font-size: 0.9rem;
		color: #6b7280;
		max-width: 460px;
		line-height: 1.65;
		margin-bottom: 2rem;
	}

	.examples-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.6rem;
		max-width: 560px;
		width: 100%;
	}

	.example-card {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
		padding: 0.75rem 0.9rem;
		background: #ffffff;
		border: 1px solid #e5e7eb;
		border-radius: 10px;
		color: #374151;
		font-size: 0.8rem;
		font-family: inherit;
		text-align: left;
		cursor: pointer;
		line-height: 1.45;
		transition:
			background 0.15s,
			border-color 0.15s;
	}

	.example-card:hover {
		background: #f9fafb;
		border-color: #9ca3af;
	}

	.example-card svg {
		flex-shrink: 0;
		color: #9ca3af;
	}

	/* ── Messages ───────────────────────────── */
	.messages-list {
		padding: 1.5rem 0 1rem;
	}

	.message {
		display: flex;
		gap: 0.9rem;
		padding: 0.75rem 1.5rem;
		max-width: 800px;
		margin: 0 auto;
		width: 100%;
		animation: fadeSlideIn 0.2s ease;
	}

	@keyframes fadeSlideIn {
		from {
			opacity: 0;
			transform: translateY(5px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.message.user {
		flex-direction: row-reverse;
	}

	.message.user .message-body {
		background: #f3f4f6;
		border: 1px solid #e5e7eb;
		border-radius: 14px 14px 2px 14px;
		padding: 0.65rem 0.9rem;
		max-width: 72%;
	}

	.message.assistant .message-body {
		flex: 1;
		min-width: 0;
		padding-top: 0.1rem;
	}

	.avatar {
		width: 32px;
		height: 32px;
		border-radius: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.ai-avatar {
		background: #eff6ff;
		border: 1px solid #bfdbfe;
	}

	.user-avatar {
		background: #e5e7eb;
		border: 1px solid #d1d5db;
		font-size: 0.65rem;
		font-weight: 600;
		color: #374151;
		letter-spacing: 0.02em;
	}

	.user-text {
		font-size: 0.875rem;
		line-height: 1.6;
		color: #374151;
	}

	.articles-row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem;
		margin-bottom: 0.85rem;
	}

	.article-tag {
		padding: 0.18rem 0.6rem;
		background: #eff6ff;
		border: 1px solid #bfdbfe;
		border-radius: 20px;
		font-size: 0.72rem;
		color: #1d4ed8;
		font-weight: 500;
	}

	/* ── Intro prose (no heading) ───────────── */
	.intro-prose {
		margin-bottom: 0.85rem;
	}

	/* ── Accordion sections ─────────────────── */
	.section-card {
		border: 1px solid #e5e7eb;
		border-radius: 10px;
		margin-bottom: 0.45rem;
		overflow: hidden;
		background: #ffffff;
	}

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		padding: 0.7rem 0.9rem;
		background: transparent;
		border: none;
		cursor: pointer;
		text-align: left;
		font-family: inherit;
		transition: background 0.12s;
	}

	.section-header:hover {
		background: #f9fafb;
	}

	.section-header-left {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.section-dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: #2563eb;
		flex-shrink: 0;
	}

	.section-title {
		font-size: 0.845rem;
		font-weight: 600;
		color: #111827;
	}

	.chevron {
		color: #9ca3af;
		transition: transform 0.18s ease;
		flex-shrink: 0;
	}

	.chevron.open {
		transform: rotate(90deg);
	}

	.section-body {
		padding: 0.1rem 1rem 1rem;
		border-top: 1px solid #f3f4f6;
	}

	/* ── Markdown prose ─────────────────────── */
	.prose :global(h1),
	.prose :global(h2),
	.prose :global(h3),
	.prose :global(h4) {
		color: #111827;
		font-weight: 600;
		margin: 1rem 0 0.4rem;
		letter-spacing: -0.01em;
	}

	.prose :global(h1) {
		font-size: 1.1rem;
	}
	.prose :global(h2) {
		font-size: 1rem;
	}
	.prose :global(h3) {
		font-size: 0.9rem;
	}

	.prose :global(p) {
		font-size: 0.875rem;
		line-height: 1.75;
		color: #374151;
		margin-bottom: 0.65rem;
	}

	.prose :global(ul),
	.prose :global(ol) {
		padding-left: 1.35rem;
		margin-bottom: 0.65rem;
	}

	.prose :global(li) {
		font-size: 0.875rem;
		line-height: 1.7;
		color: #374151;
		margin-bottom: 0.3rem;
	}

	.prose :global(strong) {
		color: #111827;
		font-weight: 600;
	}

	.prose :global(em) {
		color: #6b7280;
	}

	.prose :global(code) {
		background: #f3f4f6;
		border: 1px solid #e5e7eb;
		padding: 0.15rem 0.4rem;
		border-radius: 4px;
		font-size: 0.82em;
		color: #1d4ed8;
	}

	.prose :global(blockquote) {
		border-left: 3px solid #2563eb;
		padding-left: 0.9rem;
		margin: 0.75rem 0;
		color: #6b7280;
		font-style: italic;
	}

	.prose :global(hr) {
		border: none;
		border-top: 1px solid #e5e7eb;
		margin: 1rem 0;
	}

	/* ── Typing indicator ───────────────────── */
	.typing-dots {
		display: flex;
		gap: 4px;
		align-items: center;
		padding: 0.4rem 0 0.2rem;
	}

	.typing-dots span {
		width: 6px;
		height: 6px;
		background: #d1d5db;
		border-radius: 50%;
		animation: typingBounce 1.3s ease infinite;
	}

	.typing-dots span:nth-child(2) {
		animation-delay: 0.18s;
	}
	.typing-dots span:nth-child(3) {
		animation-delay: 0.36s;
	}

	@keyframes typingBounce {
		0%,
		60%,
		100% {
			transform: translateY(0);
			background: #d1d5db;
		}
		30% {
			transform: translateY(-5px);
			background: #9ca3af;
		}
	}

	.analyzing-text {
		font-size: 0.78rem;
		color: #9ca3af;
		margin-top: 0.2rem;
	}

	/* ── Error bar ──────────────────────────── */
	.error-bar {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.65rem 1.25rem;
		background: #fef2f2;
		border-top: 1px solid #fecaca;
		color: #dc2626;
		font-size: 0.825rem;
	}

	.error-close {
		margin-left: auto;
		background: transparent;
		border: none;
		color: #dc2626;
		cursor: pointer;
		font-size: 0.8rem;
		padding: 0.2rem 0.35rem;
		border-radius: 4px;
		font-family: inherit;
		opacity: 0.7;
		transition: opacity 0.15s;
	}

	.error-close:hover {
		opacity: 1;
	}

	/* ── Input area ─────────────────────────── */
	.input-area {
		padding: 0.75rem 1.25rem 1rem;
		background: #ffffff;
		border-top: 1px solid #e5e7eb;
	}

	.input-box {
		display: flex;
		align-items: flex-end;
		gap: 0.5rem;
		background: #ffffff;
		border: 1px solid #d1d5db;
		border-radius: 12px;
		padding: 0.5rem 0.5rem 0.5rem 1rem;
		max-width: 800px;
		margin: 0 auto;
		transition: border-color 0.15s;
	}

	.input-box:focus-within {
		border-color: #93c5fd;
		box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.2);
	}

	textarea {
		flex: 1;
		background: transparent;
		border: none;
		color: #111827;
		font-size: 0.875rem;
		font-family: inherit;
		line-height: 1.55;
		resize: none;
		outline: none;
		padding: 0.3rem 0;
		min-height: 22px;
		max-height: 200px;
		overflow-y: auto;
	}

	textarea::placeholder {
		color: #9ca3af;
	}

	textarea:disabled {
		opacity: 0.5;
	}

	.send-btn {
		width: 34px;
		height: 34px;
		background: #2563eb;
		border: none;
		border-radius: 8px;
		color: white;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		transition: background 0.15s;
	}

	.send-btn:hover:not(:disabled) {
		background: #1d4ed8;
	}

	.send-btn:disabled {
		background: #e5e7eb;
		color: #9ca3af;
		cursor: not-allowed;
	}

	.spin {
		animation: spinAnim 0.75s linear infinite;
	}

	@keyframes spinAnim {
		to {
			transform: rotate(360deg);
		}
	}

	.input-hint {
		text-align: center;
		font-size: 0.7rem;
		color: #9ca3af;
		margin-top: 0.5rem;
		max-width: 800px;
		margin-left: auto;
		margin-right: auto;
	}
</style>
