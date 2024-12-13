<script lang="ts">
    let {
        config,
        choices,
        onConfigSave
    } = $props();

    const configSections : Array<Dictionary<any>> = Object.entries(config)
        .filter(([key]) => key !== 'plugin')
        .map(([sectionKey, sectionConfig]) => ({
            sectionKey,
            sectionConfig
        }));

    function getInputType(value: any): string {
        if (typeof value === 'boolean') return 'checkbox';
        if (typeof value === 'number') return 'number';
        if (Array.isArray(value)) return 'multicheckbox';
        return 'text';
    }

    function groupOptionsByFirstLetter(options: string[]): Record<string, string[]> {
        return options.reduce((acc: Record<string, string[]>, option: string) => {
            const firstLetter = option.charAt(0).toUpperCase();
            if (!acc[firstLetter]) {
                acc[firstLetter] = [];
            }
            acc[firstLetter].push(option);
            return acc;
        }, {});
    }

    function handleSave() {
        const formElement = document.querySelector('form.config-form') as HTMLFormElement;
        const formData = new FormData(formElement);
        const newConfig: { [key: string]: Dictionary<any> } = JSON.parse(JSON.stringify(config));

        for (const [sectionKey, sectionConfig] of Object.entries(newConfig)) {
            if (sectionKey === 'plugin') continue;

            for (const key of Object.keys(sectionConfig)) {
                const inputName = `${sectionKey}-${key}`;
                const inputValues = formData.getAll(inputName);

                switch (typeof sectionConfig[key]) {
                    case 'boolean':
                        sectionConfig[key] = formData.has(inputName);
                        break;
                    case 'number':
                        sectionConfig[key] = Number(formData.get(inputName));
                        break;
                    case 'object':
                        if (Array.isArray(sectionConfig[key])) {
                            sectionConfig[key] = inputValues.map(String);
                        }
                        break;
                    default:
                        break;
                }
            }
        }

        window.eel.save_config(newConfig);
        onConfigSave?.();
    }

    function formatSectionKey(sectionKey: string): string {
        const withSpaces = sectionKey.replace(/_/g, ' ');
        return withSpaces.replace(/\b\w/g, (match) => match.toUpperCase());
    }
</script>

<form class="config-form">
    <h2>Edit Game Config</h2>

    {#each configSections as { sectionKey, sectionConfig } }
        <fieldset>
            <legend>{formatSectionKey(sectionKey)}</legend>

            {#each Object.entries(sectionConfig) as [key, value]}
                <div class="form-group">
                    <div class="form-group-inner">
                        <label for="{sectionKey}-{key}">
                            {formatSectionKey(key)}
                        </label>

                        <div class="input-container">
                            {#if getInputType(value) === 'checkbox'}
                                <input
                                        type="checkbox"
                                        id="{sectionKey}-{key}"
                                        name="{sectionKey}-{key}"
                                        checked={Boolean(value)}
                                />
                            {:else if getInputType(value) === 'number'}
                                <input
                                        type="number"
                                        id="{sectionKey}-{key}"
                                        name="{sectionKey}-{key}"
                                        value={value}
                                        min="1"
                                />
                            {:else if getInputType(value) === 'multicheckbox'}
                                {@const groupedOptions = groupOptionsByFirstLetter(choices[sectionKey]?.[key] || [])}
                                <div class="multicheckbox-grouped">
                                    {#each Object.entries(groupedOptions) as [letter, options]}
                                        <div class="letter-group">
                                            <div class="letter-header">{letter}</div>
                                            <div class="letter-options">
                                                {#each options as option}
                                                    <label class="checkbox-container">
                                                        <input
                                                                type="checkbox"
                                                                name="{sectionKey}-{key}"
                                                                value={option}
                                                                checked={
                                                                    Array.isArray(value) ? value.includes(option) : false
                                                                }
                                                        />
                                                        {option}
                                                    </label>
                                                {/each}
                                            </div>
                                        </div>
                                    {/each}
                                </div>
                            {:else}
                                <input
                                        type="text"
                                        id="{sectionKey}-{key}"
                                        name="{sectionKey}-{key}"
                                        value={value}
                                />
                            {/if}
                        </div>
                    </div>
                </div>
            {/each}
        </fieldset>
        <br/>
    {/each}

    <button type="button" onclick={handleSave}>Save</button>
</form>

<style>
    .config-form {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        margin-left: 1.5rem;
        margin-right: 1.5rem;
        background-color: rgba(31, 31, 31, 0.8);
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .form-group {
        margin-bottom: 15px;
    }

    .form-group-inner {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .form-group:not(:has(.multicheckbox-grouped)) .form-group-inner label {
        flex: 0 0 200px;
        margin-right: 10px;
        text-align: right;
    }

    .input-container {
        flex: 1;
        display: flex;
        align-items: center;
    }

    .input-container input:not([type="checkbox"]) {
        width: 100%;
    }

    .input-container input[type="checkbox"] {
        margin: 2px;
    }

    .multicheckbox-grouped {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .letter-group {
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        padding: 5px;
    }

    .letter-header {
        font-weight: bold;
        margin-bottom: 5px;
        text-align: center;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 2px;
    }

    .letter-options {
        display: flex;
        flex-direction: column;
    }

    .checkbox-container {
        display: flex;
        align-items: center;
        margin: 2px 0;
    }
</style>
