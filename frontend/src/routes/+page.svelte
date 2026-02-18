<script lang="ts">
  let files: FileList;
  let message = "";
  let isUploading = false;
  let extractedText = "";
  let analysisResult = "";

  async function handleUpload() {
    if (!files || files.length === 0) {
      message = "Please select a file.";
      return;
    }

    isUploading = true;
    message = "Uploading...";
    extractedText = "";
    analysisResult = "";

    const formData = new FormData();
    formData.append("file", files[0]);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        message = `Success! Saved as: ${data.filename}`;
        extractedText = data.text;
        analysisResult = data.analysis;
      } else {
        message = "An error occurred.";
      }
    } catch (error) {
      console.error(error);
      message = "Network error: check that the backend is running.";
    } finally {
      isUploading = false;
    }
  }
</script>

<main style="padding: 2rem; font-family: sans-serif;">
  <h1>GDPR PDF Analyzer</h1>

  <div style="margin-top: 1rem;">
    <input type="file" accept=".pdf" bind:files />
    <button on:click={handleUpload} disabled={isUploading}>
      {isUploading ? "Uploading..." : "Upload"}
    </button>
  </div>

  {#if message}
    <p style="margin-top: 1rem; font-weight: bold; color: #333;">{message}</p>
  {/if}

  {#if extractedText}
    <div style="margin-top: 2rem; padding: 1rem; background: #f5f5f5; border-radius: 4px; border: 1px solid #ddd;">
      <h3>Extracted Text:</h3>
      <pre style="white-space: pre-wrap; font-family: monospace;">{extractedText}</pre>
    </div>
  {/if}

  {#if analysisResult}
    <div style="margin-top: 2rem; padding: 1rem; background: #e6f7ff; border-radius: 4px; border: 1px solid #91d5ff;">
      <h3 style="color: #0050b3;">AI Analysis Result (GDPR Risks):</h3>
      <pre style="white-space: pre-wrap; font-family: sans-serif; line-height: 1.6;">{analysisResult}</pre>
    </div>
  {/if}
</main>
