<script lang="ts">
  import { EventsOn } from "$lib/wailsjs/runtime";

  let logs: string[] = $state([]);

  const maxLogEntries = 1000;

  EventsOn("log-message", (logMessage: LogMessage) => {
    const urlRegex = /(https?:\/\/\S+)/g;

    let message: string = "";
    if (logMessage.level == "DEBUG") {
      const parts = [];
      if (logMessage.source_file) parts.push(`${logMessage.source_file}`);
      if (logMessage.function_name) parts.push(`${logMessage.function_name}`);
      if (logMessage.line_number) parts.push(`${logMessage.line_number}`);
      const debugInfo = parts.length > 0 ? ` (${parts.join("::")})` : "";

      message = `[${logMessage.level}]${debugInfo} ${logMessage.message.replace(
        urlRegex,
        '<a href="$1" target="_blank">$1</a>',
      )}`;
    } else {
      message = `[${logMessage.level}] ${logMessage.message.replace(
        urlRegex,
        '<a href="$1" target="_blank">$1</a>',
      )}`;
    }

    if (logs.length >= maxLogEntries) {
      logs.shift();
    }
    logs.push(message);
  });

  let logContainer: HTMLDivElement;

  function getLogColor(message: string): string {
    if (message.includes("[DEBUG]")) return "cyan";
    if (message.includes("[INFO]")) return "green";
    if (message.includes("[WARNING]")) return "yellow";
    if (message.includes("[ERROR]")) return "red";
    if (message.includes("[FATAL]")) return "darkred";
    return "white";
  }

  $effect(() => {
    if (logContainer && logs.length > 0) {
      requestAnimationFrame(() => {
        logContainer.scrollTop = logContainer.scrollHeight;
      });
    }
  });
</script>

<div class="log-container selectable" bind:this={logContainer}>
  {#each logs as message}
    <div style="color: {getLogColor(message)}">
      {@html message}
    </div>
  {/each}
</div>

<style>
  .log-container {
    height: 200px;
    overflow-y: auto;
    background-color: #0f0f0f98;
    border-radius: 8px;
    padding: 10px;
    resize: vertical;
    white-space: pre-wrap;
    text-align: left;
    font-family: Consolas, monospace;
  }
</style>
