<script lang="ts">
    let {
        config,
        choices,
        onConfigSave
    } = $props();

    // Exclude the plugin section
    const configSections = Object.entries(config)
        .filter(([key]) => key !== 'plugin')
        .map(([sectionKey, sectionConfig]) => ({
            sectionKey,
            sectionConfig
        }));

    function getInputType(key: string, value: any): string {
        if (typeof value === 'boolean') return 'checkbox';
        if (typeof value === 'number') return 'number';
        if (Array.isArray(value)) return 'multicheckbox';
        return 'text';
    }

    function handleSave() {
        const formElement = document.querySelector('form.config-form') as HTMLFormElement;
        const formData = new FormData(formElement);

        interface Dictionary<T> {
            [Key: string]: T;
        }
        const newConfig: { [key: string]: Dictionary<any> } = JSON.parse(JSON.stringify(config));

        // Iterate through each section
        for (const [sectionKey, sectionConfig] of Object.entries(newConfig)) {
            if (sectionKey === 'plugin') continue;

            // Iterate through each config key in the section
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

        window.eel?.save_config(newConfig);
        onConfigSave?.();
    }
</script>

<form class="config-form">
    <h2>Edit Game Config</h2>

    {#each configSections as { sectionKey, sectionConfig }}
        <fieldset>
            <legend>{sectionKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</legend>

            {#each Object.entries(sectionConfig) as [key, value]}
                <div class="form-group">
                    <label for="{sectionKey}-{key}">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </label>

                    {#if getInputType(key, value) === 'checkbox'}
                        <input
                                type="checkbox"
                                id="{sectionKey}-{key}"
                                name="{sectionKey}-{key}"
                                checked={value}
                        />
                    {:else if getInputType(key, value) === 'number'}
                        <input
                                type="number"
                                id="{sectionKey}-{key}"
                                name="{sectionKey}-{key}"
                                value={value}
                                min="1"
                        />
                    {:else if getInputType(key, value) === 'multicheckbox'}
                        <div class="multicheckbox-group">
                            {#each (choices[sectionKey]?.[key] || []) as option}
                                <label class="checkbox-container">
                                    <input
                                            type="checkbox"
                                            name="{sectionKey}-{key}"
                                            value={option}
                                            checked={value.includes(option)}
                                    />
                                    {option}
                                </label>
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
</style>
