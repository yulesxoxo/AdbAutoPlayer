declare global {
    namespace App {
    }

    interface Window {
        // eel is injected at runtime by the eel package
        eel: {
            shutdown: () => (callback: (response: any) => void) => void;
            expose: (callback: (...args: any[]) => void) => void;
            get_menu: () => (callback: (response: string[] | null) => void) => void;
            get_running_supported_game: () => (callback: (response: null | string) => void) => void;
            action_is_running: () => (callback: (response: boolean) => void) => void;
            get_editable_config: () => (callback: (response: { config: any; choices: any }) => void) => void;
            execute: (index: number) => void;
            stop_action: () => void;
            reload_config: () => void;
            save_config: (config: { [p: string]: Dictionary<any> }) => void;
            set_host(host: string): void;
        };
    }

    interface Dictionary<T> {
        [Key: string]: T;
    }
}

export {};
