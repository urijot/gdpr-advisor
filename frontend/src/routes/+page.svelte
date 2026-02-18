<script lang="ts">
  let files: FileList;
  let message = "";
  let isUploading = false;
  let extractedText = "";

  async function handleUpload() {
    if (!files || files.length === 0) {
      message = "ファイルを選択してください";
      return;
    }

    isUploading = true;
    message = "アップロード中...";
    extractedText = "";

    const formData = new FormData();
    formData.append("file", files[0]);

    try {
      // バックエンドのAPIに送信
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        message = `成功！保存名: ${data.filename}`;
        extractedText = data.text;
      } else {
        message = "エラーが発生しました";
      }
    } catch (error) {
      console.error(error);
      message = "通信エラー: バックエンドが起動しているか確認してください";
    } finally {
      isUploading = false;
    }
  }
</script>

<main style="padding: 2rem; font-family: sans-serif;">
  <h1>PDF Upload Test</h1>
  
  <div style="margin-top: 1rem;">
    <input type="file" accept=".pdf" bind:files />
    <button on:click={handleUpload} disabled={isUploading}>
      {isUploading ? '送信中...' : 'アップロード'}
    </button>
  </div>

  {#if message}
    <p style="margin-top: 1rem; font-weight: bold; color: #333;">{message}</p>
  {/if}

  {#if extractedText}
    <div style="margin-top: 2rem; padding: 1rem; background: #f5f5f5; border-radius: 4px; border: 1px solid #ddd;">
      <h3>抽出されたテキスト:</h3>
      <pre style="white-space: pre-wrap; font-family: monospace;">{extractedText}</pre>
    </div>
  {/if}
</main>
