/**
 * WeaR Lang - Web Browser Entry Point
 * Exposes WearLang to the global window object for browser usage
 */

import { WearLang, ExecutionResult } from './index';
import { getAvailableLanguages } from './languages/loader';

// Export to window for browser usage
declare global {
    interface Window {
        WearLang: typeof WearLang;
        getAvailableLanguages: typeof getAvailableLanguages;
    }
}

// Make WearLang available globally in the browser
if (typeof window !== 'undefined') {
    window.WearLang = WearLang;
    window.getAvailableLanguages = getAvailableLanguages;
}

// Also export for module usage
export { WearLang, ExecutionResult, getAvailableLanguages };
