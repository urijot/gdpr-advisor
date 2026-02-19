<script lang="ts">
	import { marked } from 'marked';
	import { tick } from 'svelte';

	marked.use({ breaks: true });

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

	const examples = [
		'An app that tracks users\' location in real time',
		'A healthcare platform storing patient records',
		'An e-commerce site sharing data with advertisers',
		'A social network selling user data to third parties'
	];

	function renderMarkdown(text: string): string {
		return marked(text) as string;
	}

	async function handleSubmit() {
		if (!idea.trim() || isLoading) return;

		const userMessage = idea.trim();
		idea = '';
		error = '';

		if (textarea) {
			textarea.style.height = 'auto';
		}

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
					{
						role: 'assistant',
						content: data.advice,
						articles: data.relevant_articles
					}
				];
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
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
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
		return {
			destroy() {
				node.removeEventListener('input', resize);
			}
		};
	}

	function useExample(example: string) {
		idea = example;
		handleSubmit();
	}

	function clearChat() {
		messages = [];
		error = '';
		idea = '';
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
							fill="#3b82f6"
							opacity="0.25"
							stroke="#3b82f6"
							stroke-width="1.5"
						/>
						<path
							d="M9 12l2 2 4-4"
							stroke="#3b82f6"
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
		<!-- Messages -->
		<div class="chat-container" bind:this={chatContainer}>
			{#if messages.length === 0}
				<!-- Welcome screen -->
				<div class="welcome">
					<div class="welcome-icon">
						<svg width="36" height="36" viewBox="0 0 24 24" fill="none">
							<path
								d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.25C17.25 22.15 21 17.25 21 12V7L12 2z"
								fill="#3b82f6"
								opacity="0.3"
								stroke="#3b82f6"
								stroke-width="1.5"
							/>
							<path
								d="M9 12l2 2 4-4"
								stroke="#3b82f6"
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
					{#each messages as message}
						<div class="message {message.role}">
							{#if message.role === 'assistant'}
								<div class="avatar ai-avatar">
									<svg width="16" height="16" viewBox="0 0 24 24" fill="none">
										<path
											d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.25C17.25 22.15 21 17.25 21 12V7L12 2z"
											fill="#3b82f6"
											opacity="0.3"
											stroke="#3b82f6"
											stroke-width="1.5"
										/>
										<path
											d="M9 12l2 2 4-4"
											stroke="#3b82f6"
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
									{#if message.articles && message.articles.length > 0}
										<div class="articles-row">
											{#each message.articles as article}
												<span class="article-tag">{article}</span>
											{/each}
										</div>
									{/if}
									<div class="prose">{@html renderMarkdown(message.content)}</div>
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
										fill="#3b82f6"
										opacity="0.3"
										stroke="#3b82f6"
										stroke-width="1.5"
									/>
									<path
										d="M9 12l2 2 4-4"
										stroke="#3b82f6"
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
		background: #212121;
		color: #ececec;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
	}

	/* ── Sidebar ────────────────────────────── */
	.sidebar {
		width: 240px;
		flex-shrink: 0;
		background: #171717;
		border-right: 1px solid #2a2a2a;
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
		background: rgba(59, 130, 246, 0.1);
		border: 1px solid rgba(59, 130, 246, 0.2);
		border-radius: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.logo-text {
		font-size: 0.95rem;
		font-weight: 600;
		color: #ececec;
		letter-spacing: -0.01em;
	}

	.new-chat-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.55rem 0.75rem;
		background: transparent;
		border: 1px solid #333;
		border-radius: 8px;
		color: #c0c0c0;
		font-size: 0.8rem;
		font-family: inherit;
		cursor: pointer;
		transition:
			background 0.15s,
			border-color 0.15s;
	}

	.new-chat-btn:hover {
		background: #242424;
		border-color: #404040;
		color: #ececec;
	}

	.disclaimer-card {
		display: flex;
		align-items: flex-start;
		gap: 0.45rem;
		padding: 0.65rem 0.75rem;
		background: #1c1c1c;
		border: 1px solid #2a2a2a;
		border-radius: 8px;
	}

	.disclaimer-icon {
		flex-shrink: 0;
		margin-top: 1px;
		color: #555;
	}

	.disclaimer-card p {
		font-size: 0.72rem;
		color: #666;
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
		background: #333;
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
		background: rgba(59, 130, 246, 0.1);
		border: 1px solid rgba(59, 130, 246, 0.2);
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
		color: #ececec;
	}

	.welcome > p {
		font-size: 0.9rem;
		color: #8e8ea0;
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
		background: #282828;
		border: 1px solid #333;
		border-radius: 10px;
		color: #b0b0b0;
		font-size: 0.8rem;
		font-family: inherit;
		text-align: left;
		cursor: pointer;
		line-height: 1.45;
		transition:
			background 0.15s,
			border-color 0.15s,
			color 0.15s;
	}

	.example-card:hover {
		background: #303030;
		border-color: #444;
		color: #ececec;
	}

	.example-card svg {
		flex-shrink: 0;
		opacity: 0.4;
	}

	/* ── Messages ───────────────────────────── */
	.messages-list {
		padding: 1.5rem 0 1rem;
	}

	.message {
		display: flex;
		gap: 0.9rem;
		padding: 0.75rem 1.5rem;
		max-width: 780px;
		margin: 0 auto;
		width: 100%;
		animation: fadeSlideIn 0.2s ease;
	}

	@keyframes fadeSlideIn {
		from {
			opacity: 0;
			transform: translateY(6px);
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
		background: #2d2d2d;
		border: 1px solid #383838;
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
		background: rgba(59, 130, 246, 0.1);
		border: 1px solid rgba(59, 130, 246, 0.2);
	}

	.user-avatar {
		background: #3a3a3a;
		border: 1px solid #444;
		font-size: 0.65rem;
		font-weight: 600;
		color: #c0c0c0;
		letter-spacing: 0.02em;
	}

	.user-text {
		font-size: 0.875rem;
		line-height: 1.6;
		color: #d8d8d8;
	}

	.articles-row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem;
		margin-bottom: 0.85rem;
	}

	.article-tag {
		padding: 0.18rem 0.55rem;
		background: rgba(59, 130, 246, 0.1);
		border: 1px solid rgba(59, 130, 246, 0.25);
		border-radius: 20px;
		font-size: 0.72rem;
		color: #7fb3f5;
		font-weight: 500;
	}

	/* ── Markdown prose ─────────────────────── */
	.prose :global(h1),
	.prose :global(h2),
	.prose :global(h3),
	.prose :global(h4) {
		color: #e8e8e8;
		font-weight: 600;
		margin: 1.1rem 0 0.45rem;
		letter-spacing: -0.01em;
	}

	.prose :global(h1) {
		font-size: 1.15rem;
	}
	.prose :global(h2) {
		font-size: 1.05rem;
	}
	.prose :global(h3) {
		font-size: 0.95rem;
	}

	.prose :global(p) {
		font-size: 0.875rem;
		line-height: 1.75;
		color: #c8c8c8;
		margin-bottom: 0.7rem;
	}

	.prose :global(ul),
	.prose :global(ol) {
		padding-left: 1.35rem;
		margin-bottom: 0.7rem;
	}

	.prose :global(li) {
		font-size: 0.875rem;
		line-height: 1.7;
		color: #c8c8c8;
		margin-bottom: 0.3rem;
	}

	.prose :global(strong) {
		color: #e8e8e8;
		font-weight: 600;
	}

	.prose :global(em) {
		color: #b0b0b0;
	}

	.prose :global(code) {
		background: #2a2a2a;
		border: 1px solid #383838;
		padding: 0.15rem 0.4rem;
		border-radius: 4px;
		font-size: 0.82em;
		color: #7fb3f5;
	}

	.prose :global(blockquote) {
		border-left: 3px solid #3b82f6;
		padding-left: 0.9rem;
		margin: 0.75rem 0;
		color: #999;
		font-style: italic;
	}

	.prose :global(hr) {
		border: none;
		border-top: 1px solid #333;
		margin: 1rem 0;
	}

	/* ── Typing indicator ───────────────────── */
	.typing-dots {
		display: flex;
		gap: 4px;
		align-items: center;
		padding: 0.4rem 0 0.25rem;
	}

	.typing-dots span {
		width: 6px;
		height: 6px;
		background: #4a4a4a;
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
			background: #4a4a4a;
		}
		30% {
			transform: translateY(-5px);
			background: #7a7a7a;
		}
	}

	.analyzing-text {
		font-size: 0.78rem;
		color: #555;
		margin-top: 0.2rem;
	}

	/* ── Error bar ──────────────────────────── */
	.error-bar {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.65rem 1.25rem;
		background: rgba(239, 68, 68, 0.08);
		border-top: 1px solid rgba(239, 68, 68, 0.2);
		color: #f87171;
		font-size: 0.825rem;
	}

	.error-close {
		margin-left: auto;
		background: transparent;
		border: none;
		color: #f87171;
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
		background: #212121;
		border-top: 1px solid #2a2a2a;
	}

	.input-box {
		display: flex;
		align-items: flex-end;
		gap: 0.5rem;
		background: #2a2a2a;
		border: 1px solid #383838;
		border-radius: 12px;
		padding: 0.5rem 0.5rem 0.5rem 1rem;
		max-width: 780px;
		margin: 0 auto;
		transition: border-color 0.15s;
	}

	.input-box:focus-within {
		border-color: rgba(59, 130, 246, 0.45);
	}

	textarea {
		flex: 1;
		background: transparent;
		border: none;
		color: #ececec;
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
		color: #555;
	}

	textarea:disabled {
		opacity: 0.45;
	}

	.send-btn {
		width: 34px;
		height: 34px;
		background: #3b82f6;
		border: none;
		border-radius: 8px;
		color: white;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		transition:
			background 0.15s,
			opacity 0.15s;
	}

	.send-btn:hover:not(:disabled) {
		background: #2563eb;
	}

	.send-btn:disabled {
		background: #2a2a2a;
		color: #444;
		border: 1px solid #333;
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
		color: #444;
		margin-top: 0.5rem;
		max-width: 780px;
		margin-left: auto;
		margin-right: auto;
	}
</style>
