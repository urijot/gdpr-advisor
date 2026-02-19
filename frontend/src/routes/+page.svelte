<script lang="ts">
  let idea = "";
  let isLoading = false;
  let advice = "";
  let relevantArticles: string[] = [];
  let error = "";

  async function handleSubmit() {
    if (!idea.trim()) {
      error = "Please describe your service idea.";
      return;
    }

    isLoading = true;
    advice = "";
    relevantArticles = [];
    error = "";

    try {
      const response = await fetch("http://localhost:8000/advice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea }),
      });

      if (response.ok) {
        const data = await response.json();
        advice = data.advice;
        relevantArticles = data.relevant_articles;
      } else {
        const data = await response.json();
        error = data.detail ?? "An error occurred.";
      }
    } catch (err) {
      console.error(err);
      error = "Network error: check that the backend is running.";
    } finally {
      isLoading = false;
    }
  }
</script>

<main style="max-width: 800px; margin: 0 auto; padding: 2rem; font-family: sans-serif;">
  <h1 style="font-size: 1.8rem; margin-bottom: 0.25rem;">GDPR Compliance Advisor</h1>
  <p style="color: #666; margin-bottom: 2rem;">
    Describe your service idea and get a GDPR compliance overview based on the official regulation text.
    <strong>This is not legal advice.</strong>
  </p>

  <div style="display: flex; flex-direction: column; gap: 0.75rem;">
    <textarea
      bind:value={idea}
      placeholder="e.g. An app that collects users' location data in real time and shares it with third-party advertisers..."
      rows={6}
      style="width: 100%; padding: 0.75rem; font-size: 1rem; border: 1px solid #ccc; border-radius: 6px; resize: vertical; box-sizing: border-box;"
    />
    <button
      on:click={handleSubmit}
      disabled={isLoading}
      style="align-self: flex-start; padding: 0.6rem 1.4rem; font-size: 1rem; background: #1a73e8; color: white; border: none; border-radius: 6px; cursor: pointer; opacity: {isLoading ? 0.6 : 1};"
    >
      {isLoading ? "Analyzing..." : "Check GDPR Compliance"}
    </button>
  </div>

  {#if error}
    <div style="margin-top: 1.5rem; padding: 1rem; background: #fff2f0; border: 1px solid #ffccc7; border-radius: 6px; color: #cf1322;">
      {error}
    </div>
  {/if}

  {#if relevantArticles.length > 0}
    <div style="margin-top: 1.5rem;">
      <strong>Articles referenced:</strong>
      {#each relevantArticles as article}
        <span style="display: inline-block; margin: 0.25rem; padding: 0.2rem 0.6rem; background: #e6f4ff; border: 1px solid #91caff; border-radius: 12px; font-size: 0.85rem;">
          {article}
        </span>
      {/each}
    </div>
  {/if}

  {#if advice}
    <div style="margin-top: 1.5rem; padding: 1.5rem; background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 6px;">
      <h3 style="margin-top: 0; color: #237804;">Analysis Result</h3>
      <pre style="white-space: pre-wrap; font-family: sans-serif; line-height: 1.7; margin: 0;">{advice}</pre>
    </div>
  {/if}
</main>
