/**
 * Country Selector Component for ValidoAI
 * Country selector with flags, search, and advanced features
 */

class ValidoAICountrySelector {
    constructor() {
        this.selectors = new Map();
        this.countries = [];
        this.countryData = [];
        this.loadCountries();
    }

    async loadCountries() {
        try {
            // Load country data from REST Countries API or use local data
            const response = await fetch('https://restcountries.com/v3.1/all?fields=name,cca2,flags,idd,currencies,languages,capital,region');
            if (response.ok) {
                this.countries = await response.json();
            } else {
                // Fallback to local data
                this.countries = this.getLocalCountryData();
            }

            this.countryData = this.processCountries();
        } catch (error) {
            console.error('Failed to load countries:', error);
            this.countries = this.getLocalCountryData();
            this.countryData = this.processCountries();
        }
    }

    getLocalCountryData() {
        return [
            {
                name: { common: "United States", official: "United States of America" },
                cca2: "US",
                flags: { png: "https://flagcdn.com/w320/us.png", svg: "https://flagcdn.com/us.svg" },
                idd: { root: "+1", suffixes: [""] },
                currencies: { USD: { name: "United States dollar", symbol: "$" } },
                languages: { eng: "English" },
                capital: ["Washington, D.C."],
                region: "Americas"
            },
            {
                name: { common: "United Kingdom", official: "United Kingdom of Great Britain and Northern Ireland" },
                cca2: "GB",
                flags: { png: "https://flagcdn.com/w320/gb.png", svg: "https://flagcdn.com/gb.svg" },
                idd: { root: "+4", suffixes: ["4"] },
                currencies: { GBP: { name: "British pound", symbol: "£" } },
                languages: { eng: "English" },
                capital: ["London"],
                region: "Europe"
            },
            {
                name: { common: "Germany", official: "Federal Republic of Germany" },
                cca2: "DE",
                flags: { png: "https://flagcdn.com/w320/de.png", svg: "https://flagcdn.com/de.svg" },
                idd: { root: "+4", suffixes: ["9"] },
                currencies: { EUR: { name: "Euro", symbol: "€" } },
                languages: { deu: "German" },
                capital: ["Berlin"],
                region: "Europe"
            },
            {
                name: { common: "France", official: "French Republic" },
                cca2: "FR",
                flags: { png: "https://flagcdn.com/w320/fr.png", svg: "https://flagcdn.com/fr.svg" },
                idd: { root: "+3", suffixes: ["3"] },
                currencies: { EUR: { name: "Euro", symbol: "€" } },
                languages: { fra: "French" },
                capital: ["Paris"],
                region: "Europe"
            },
            {
                name: { common: "Japan", official: "Japan" },
                cca2: "JP",
                flags: { png: "https://flagcdn.com/w320/jp.png", svg: "https://flagcdn.com/jp.svg" },
                idd: { root: "+8", suffixes: ["1"] },
                currencies: { JPY: { name: "Japanese yen", symbol: "¥" } },
                languages: { jpn: "Japanese" },
                capital: ["Tokyo"],
                region: "Asia"
            },
            {
                name: { common: "Australia", official: "Commonwealth of Australia" },
                cca2: "AU",
                flags: { png: "https://flagcdn.com/w320/au.png", svg: "https://flagcdn.com/au.svg" },
                idd: { root: "+6", suffixes: ["1"] },
                currencies: { AUD: { name: "Australian dollar", symbol: "$" } },
                languages: { eng: "English" },
                capital: ["Canberra"],
                region: "Oceania"
            },
            {
                name: { common: "Canada", official: "Canada" },
                cca2: "CA",
                flags: { png: "https://flagcdn.com/w320/ca.png", svg: "https://flagcdn.com/ca.svg" },
                idd: { root: "+1", suffixes: [""] },
                currencies: { CAD: { name: "Canadian dollar", symbol: "$" } },
                languages: { eng: "English", fra: "French" },
                capital: ["Ottawa"],
                region: "Americas"
            },
            {
                name: { common: "China", official: "People's Republic of China" },
                cca2: "CN",
                flags: { png: "https://flagcdn.com/w320/cn.png", svg: "https://flagcdn.com/cn.svg" },
                idd: { root: "+8", suffixes: ["6"] },
                currencies: { CNY: { name: "Chinese yuan", symbol: "¥" } },
                languages: { zho: "Chinese" },
                capital: ["Beijing"],
                region: "Asia"
            },
            {
                name: { common: "India", official: "Republic of India" },
                cca2: "IN",
                flags: { png: "https://flagcdn.com/w320/in.png", svg: "https://flagcdn.com/in.svg" },
                idd: { root: "+9", suffixes: ["1"] },
                currencies: { INR: { name: "Indian rupee", symbol: "₹" } },
                languages: { eng: "English", hin: "Hindi" },
                capital: ["New Delhi"],
                region: "Asia"
            },
            {
                name: { common: "Brazil", official: "Federative Republic of Brazil" },
                cca2: "BR",
                flags: { png: "https://flagcdn.com/w320/br.png", svg: "https://flagcdn.com/br.svg" },
                idd: { root: "+5", suffixes: ["5"] },
                currencies: { BRL: { name: "Brazilian real", symbol: "R$" } },
                languages: { por: "Portuguese" },
                capital: ["Brasília"],
                region: "Americas"
            }
        ];
    }

    processCountries() {
        return this.countries.map(country => ({
            code: country.cca2,
            name: country.name.common,
            officialName: country.name.official,
            flag: country.flags.svg || country.flags.png,
            flagPng: country.flags.png,
            dialCode: country.idd ? `${country.idd.root}${country.idd.suffixes[0] || ''}` : '',
            currency: country.currencies ? Object.values(country.currencies)[0] : null,
            languages: country.languages ? Object.values(country.languages) : [],
            capital: country.capital ? country.capital[0] : '',
            region: country.region,
            searchText: `${country.name.common} ${country.name.official} ${country.cca2}`.toLowerCase()
        })).sort((a, b) => a.name.localeCompare(b.name));
    }

    init(selector, options = {}) {
        const selectorId = this.generateId();
        const config = this.mergeOptions(options);

        // Create selector container
        const container = this.createSelectorContainer(selector, config);

        this.selectors.set(selectorId, {
            selector: selector,
            config: config,
            container: container,
            selectedCountry: null,
            isOpen: false
        });

        this.bindEvents(selectorId);
        this.applyThemeIntegration(selectorId);

        return selectorId;
    }

    mergeOptions(options) {
        return {
            showFlags: true,
            showDialCodes: true,
            showCurrencies: false,
            searchable: true,
            placeholder: "Select a country...",
            defaultCountry: null,
            excludedCountries: [],
            onlyCountries: [],
            preferredCountries: ['US', 'GB', 'DE', 'FR', 'JP'],
            position: 'auto',
            zIndex: 9999,
            theme: 'light',
            size: 'md', // sm, md, lg
            disabled: false,
            allowClear: true,
            showSearch: true,
            searchPlaceholder: "Search countries...",
            ...options
        };
    }

    createSelectorContainer(selector, config) {
        const element = document.querySelector(selector);
        if (!element) return null;

        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = `country-selector-wrapper position-relative ${config.size}`;
        element.parentNode.insertBefore(wrapper, element);
        wrapper.appendChild(element);

        // Create custom selector
        const customSelector = document.createElement('div');
        customSelector.className = 'country-custom-selector form-control d-flex align-items-center cursor-pointer';
        customSelector.innerHTML = this.getSelectorHTML(config);

        // Create dropdown
        const dropdown = document.createElement('div');
        dropdown.className = 'country-dropdown position-absolute top-100 start-0 w-100 bg-white border rounded shadow-sm d-none';
        dropdown.style.cssText = `z-index: ${config.zIndex}; max-height: 300px; overflow-y: auto;`;

        dropdown.innerHTML = this.getDropdownHTML(config);

        wrapper.appendChild(customSelector);
        wrapper.appendChild(dropdown);

        // Hide original select
        element.style.display = 'none';

        return {
            wrapper: wrapper,
            element: element,
            customSelector: customSelector,
            dropdown: dropdown,
            searchInput: dropdown.querySelector('.country-search'),
            countryList: dropdown.querySelector('.country-list')
        };
    }

    getSelectorHTML(config) {
        const placeholder = config.placeholder || 'Select a country...';
        return `
            <div class="country-display flex-grow-1">
                <span class="country-placeholder text-muted">${placeholder}</span>
            </div>
            <div class="country-actions d-flex align-items-center">
                <button type="button" class="btn btn-sm btn-link p-0 me-2 clear-country d-none" title="Clear selection">
                    <i class="fas fa-times"></i>
                </button>
                <i class="fas fa-chevron-down toggle-icon"></i>
            </div>
        `;
    }

    getDropdownHTML(config) {
        const searchHTML = config.showSearch ? `
            <div class="country-search-container p-2 border-bottom">
                <input type="text" class="form-control form-control-sm country-search"
                       placeholder="${config.searchPlaceholder}" autocomplete="off">
            </div>
        ` : '';

        return `
            ${searchHTML}
            <div class="country-list" style="max-height: 250px; overflow-y: auto;">
                ${this.getCountriesListHTML(config)}
            </div>
        `;
    }

    getCountriesListHTML(config) {
        let countries = this.countryData;

        // Filter by onlyCountries
        if (config.onlyCountries.length > 0) {
            countries = countries.filter(country => config.onlyCountries.includes(country.code));
        }

        // Exclude countries
        if (config.excludedCountries.length > 0) {
            countries = countries.filter(country => !config.excludedCountries.includes(country.code));
        }

        // Group by preferred countries
        const preferred = countries.filter(country => config.preferredCountries.includes(country.code));
        const others = countries.filter(country => !config.preferredCountries.includes(country.code));

        let html = '';

        if (preferred.length > 0) {
            html += '<div class="country-group">';
            html += '<div class="country-group-header px-3 py-2 bg-light fw-bold small">Preferred Countries</div>';
            html += preferred.map(country => this.getCountryItemHTML(country, config)).join('');
            html += '</div>';
        }

        if (others.length > 0) {
            if (preferred.length > 0) {
                html += '<div class="dropdown-divider"></div>';
            }
            html += '<div class="country-group">';
            html += others.map(country => this.getCountryItemHTML(country, config)).join('');
            html += '</div>';
        }

        return html;
    }

    getCountryItemHTML(country, config) {
        const flagHTML = config.showFlags ? `<img src="${country.flag}" alt="${country.code}" class="country-flag me-2" style="width: 20px; height: 15px; object-fit: cover;">` : '';
        const dialCodeHTML = config.showDialCodes && country.dialCode ? `<span class="country-dial text-muted small me-2">${country.dialCode}</span>` : '';
        const currencyHTML = config.showCurrencies && country.currency ? `<span class="country-currency text-muted small">(${country.currency.symbol})</span>` : '';

        return `
            <div class="country-item px-3 py-2 cursor-pointer hover-bg-light" data-country-code="${country.code}">
                <div class="d-flex align-items-center">
                    ${flagHTML}
                    <div class="flex-grow-1">
                        <div class="country-name fw-medium">${country.name}</div>
                        <div class="country-details small text-muted">
                            ${dialCodeHTML}${currencyHTML}
                        </div>
                    </div>
                    <div class="country-code small text-muted">${country.code}</div>
                </div>
            </div>
        `;
    }

    bindEvents(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        const { container, config } = selectorData;

        // Toggle dropdown
        container.customSelector.addEventListener('click', (e) => {
            if (!e.target.closest('.clear-country')) {
                this.toggleDropdown(selectorId);
            }
        });

        // Clear selection
        container.customSelector.querySelector('.clear-country').addEventListener('click', (e) => {
            e.stopPropagation();
            this.clearSelection(selectorId);
        });

        // Search functionality
        if (container.searchInput) {
            container.searchInput.addEventListener('input', (e) => {
                this.filterCountries(selectorId, e.target.value);
            });

            container.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeDropdown(selectorId);
                }
            });
        }

        // Country selection
        container.countryList.addEventListener('click', (e) => {
            const countryItem = e.target.closest('.country-item');
            if (countryItem) {
                const countryCode = countryItem.dataset.countryCode;
                this.selectCountry(selectorId, countryCode);
            }
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!container.wrapper.contains(e.target)) {
                this.closeDropdown(selectorId);
            }
        });

        // Keyboard navigation
        container.wrapper.addEventListener('keydown', (e) => {
            this.handleKeyboard(selectorId, e);
        });
    }

    toggleDropdown(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData || selectorData.config.disabled) return;

        if (selectorData.isOpen) {
            this.closeDropdown(selectorId);
        } else {
            this.openDropdown(selectorId);
        }
    }

    openDropdown(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        // Close other dropdowns
        this.selectors.forEach((data, id) => {
            if (id !== selectorId && data.isOpen) {
                this.closeDropdown(id);
            }
        });

        selectorData.container.dropdown.classList.remove('d-none');
        selectorData.isOpen = true;

        // Focus search input if available
        if (selectorData.container.searchInput) {
            setTimeout(() => selectorData.container.searchInput.focus(), 100);
        }

        // Position dropdown
        this.positionDropdown(selectorId);

        // Trigger event
        this.triggerEvent(selectorData.container.element, 'countrySelectorOpen', { selectorId });
    }

    closeDropdown(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        selectorData.container.dropdown.classList.add('d-none');
        selectorData.isOpen = false;

        // Trigger event
        this.triggerEvent(selectorData.container.element, 'countrySelectorClose', { selectorId });
    }

    positionDropdown(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        const rect = selectorData.container.customSelector.getBoundingClientRect();
        const dropdown = selectorData.container.dropdown;
        const viewportHeight = window.innerHeight;
        const dropdownHeight = Math.min(300, dropdown.scrollHeight);

        // Position below the selector
        dropdown.style.top = (rect.bottom + 5) + 'px';
        dropdown.style.left = rect.left + 'px';
        dropdown.style.width = rect.width + 'px';

        // Adjust if it goes off-screen
        if (rect.bottom + dropdownHeight + 5 > viewportHeight) {
            dropdown.style.top = (rect.top - dropdownHeight - 5) + 'px';
        }
    }

    filterCountries(selectorId, searchTerm) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        const items = selectorData.container.countryList.querySelectorAll('.country-item');
        const term = searchTerm.toLowerCase().trim();

        items.forEach(item => {
            const countryCode = item.dataset.countryCode;
            const country = this.countryData.find(c => c.code === countryCode);

            if (country && (term === '' || country.searchText.includes(term))) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    selectCountry(selectorId, countryCode) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        const country = this.countryData.find(c => c.code === countryCode);
        if (!country) return;

        // Update original select
        selectorData.container.element.value = countryCode;

        // Update custom selector display
        this.updateSelectorDisplay(selectorId, country);

        // Update selected country
        selectorData.selectedCountry = country;

        // Close dropdown
        this.closeDropdown(selectorId);

        // Show clear button
        if (selectorData.config.allowClear) {
            selectorData.container.customSelector.querySelector('.clear-country').classList.remove('d-none');
        }

        // Trigger change event
        this.triggerEvent(selectorData.container.element, 'change', { country, countryCode });
        this.triggerEvent(selectorData.container.element, 'countrySelected', { country, countryCode, selectorId });
    }

    updateSelectorDisplay(selectorId, country) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        const display = selectorData.container.customSelector.querySelector('.country-display');
        const { config } = selectorData;

        const flagHTML = config.showFlags ? `<img src="${country.flag}" alt="${country.code}" class="country-flag me-2" style="width: 20px; height: 15px; object-fit: cover;">` : '';
        const dialCodeHTML = config.showDialCodes && country.dialCode ? `<span class="country-dial text-muted me-2">${country.dialCode}</span>` : '';
        const currencyHTML = config.showCurrencies && country.currency ? `<span class="country-currency text-muted small">(${country.currency.symbol})</span>` : '';

        display.innerHTML = `
            <div class="d-flex align-items-center">
                ${flagHTML}
                <div class="flex-grow-1">
                    <div class="country-name">${country.name}</div>
                    <div class="country-details small text-muted">
                        ${dialCodeHTML}${currencyHTML}
                    </div>
                </div>
                <div class="country-code small text-muted">${country.code}</div>
            </div>
        `;
    }

    clearSelection(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        // Clear original select
        selectorData.container.element.value = '';

        // Reset custom selector
        const display = selectorData.container.customSelector.querySelector('.country-display');
        display.innerHTML = `<span class="country-placeholder text-muted">${selectorData.config.placeholder}</span>`;

        // Hide clear button
        selectorData.container.customSelector.querySelector('.clear-country').classList.add('d-none');

        // Clear selected country
        selectorData.selectedCountry = null;

        // Trigger events
        this.triggerEvent(selectorData.container.element, 'change', { country: null, countryCode: null });
        this.triggerEvent(selectorData.container.element, 'countryCleared', { selectorId });
    }

    handleKeyboard(selectorId, e) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData || !selectorData.isOpen) return;

        switch (e.key) {
            case 'Escape':
                this.closeDropdown(selectorId);
                break;
            case 'Enter':
                e.preventDefault();
                const firstVisible = selectorData.container.countryList.querySelector('.country-item:not([style*="display: none"])');
                if (firstVisible) {
                    const countryCode = firstVisible.dataset.countryCode;
                    this.selectCountry(selectorId, countryCode);
                }
                break;
            case 'ArrowDown':
            case 'ArrowUp':
                e.preventDefault();
                this.navigateWithKeyboard(selectorId, e.key === 'ArrowDown' ? 'down' : 'up');
                break;
        }
    }

    navigateWithKeyboard(selectorId, direction) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        const items = Array.from(selectorData.container.countryList.querySelectorAll('.country-item:not([style*="display: none"])'));
        const currentIndex = items.findIndex(item => item.classList.contains('bg-light'));

        let newIndex;
        if (direction === 'down') {
            newIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
        } else {
            newIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
        }

        // Remove previous highlight
        items.forEach(item => item.classList.remove('bg-light'));

        // Add new highlight
        if (items[newIndex]) {
            items[newIndex].classList.add('bg-light');
            items[newIndex].scrollIntoView({ block: 'nearest' });
        }
    }

    applyThemeIntegration(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        // Listen for theme changes
        document.addEventListener('themeChanged', (event) => {
            this.updateSelectorTheme(selectorId, event.detail.theme);
        });

        // Initial theme application
        const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
        this.updateSelectorTheme(selectorId, currentTheme);
    }

    updateSelectorTheme(selectorId, theme) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);
        const container = selectorData.container.wrapper;

        container.classList.toggle('country-selector-dark', isDark);

        // Update dropdown background
        const dropdown = selectorData.container.dropdown;
        if (isDark) {
            dropdown.classList.add('bg-dark', 'text-light', 'border-secondary');
            dropdown.classList.remove('bg-white', 'text-dark', 'border');
        } else {
            dropdown.classList.add('bg-white', 'text-dark', 'border');
            dropdown.classList.remove('bg-dark', 'text-light', 'border-secondary');
        }
    }

    // Utility methods
    generateId() {
        return 'country_' + Math.random().toString(36).substr(2, 9);
    }

    destroy(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (selectorData) {
            // Remove event listeners and cleanup
            this.selectors.delete(selectorId);
        }
    }

    getSelectedCountry(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        return selectorData ? selectorData.selectedCountry : null;
    }

    getCountryByCode(code) {
        return this.countryData.find(country => country.code === code);
    }

    getCountriesByRegion(region) {
        return this.countryData.filter(country => country.region === region);
    }

    setCountry(selectorId, countryCode) {
        if (countryCode) {
            this.selectCountry(selectorId, countryCode);
        } else {
            this.clearSelection(selectorId);
        }
    }

    triggerEvent(element, eventName, detail = {}) {
        const event = new CustomEvent(eventName, { detail });
        element.dispatchEvent(event);
    }

    // Advanced features
    addCountryInfo(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        // Add info button
        const actions = selectorData.container.customSelector.querySelector('.country-actions');
        const infoBtn = document.createElement('button');
        infoBtn.type = 'button';
        infoBtn.className = 'btn btn-sm btn-link p-0 me-2 country-info';
        infoBtn.title = 'Country Information';
        infoBtn.innerHTML = '<i class="fas fa-info-circle"></i>';

        actions.insertBefore(infoBtn, actions.firstChild);

        infoBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (selectorData.selectedCountry) {
                this.showCountryInfo(selectorData.selectedCountry);
            }
        });
    }

    showCountryInfo(country) {
        if (window.showGlobalModal) {
            showGlobalModal({
                title: `${country.name} Information`,
                content: `
                    <div class="row g-3">
                        <div class="col-md-6">
                            <img src="${country.flagPng}" alt="${country.code}" class="img-fluid rounded">
                        </div>
                        <div class="col-md-6">
                            <table class="table table-sm">
                                <tr>
                                    <th>Official Name:</th>
                                    <td>${country.officialName}</td>
                                </tr>
                                <tr>
                                    <th>Capital:</th>
                                    <td>${country.capital}</td>
                                </tr>
                                <tr>
                                    <th>Region:</th>
                                    <td>${country.region}</td>
                                </tr>
                                <tr>
                                    <th>Currency:</th>
                                    <td>${country.currency ? `${country.currency.name} (${country.currency.symbol})` : 'N/A'}</td>
                                </tr>
                                <tr>
                                    <th>Dial Code:</th>
                                    <td>${country.dialCode || 'N/A'}</td>
                                </tr>
                                <tr>
                                    <th>Languages:</th>
                                    <td>${country.languages.join(', ')}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                `,
                size: 'max-w-4xl'
            });
        }
    }

    addFavorites(selectorId) {
        const selectorData = this.selectors.get(selectorId);
        if (!selectorData) return;

        // Add favorites functionality
        const favorites = JSON.parse(localStorage.getItem('country-selector-favorites') || '[]');

        // Add favorite toggle
        const countryList = selectorData.container.countryList;
        countryList.querySelectorAll('.country-item').forEach(item => {
            const countryCode = item.dataset.countryCode;
            const starBtn = document.createElement('button');
            starBtn.className = 'btn btn-sm btn-link p-0 me-2 favorite-btn';
            starBtn.innerHTML = favorites.includes(countryCode) ?
                '<i class="fas fa-star text-warning"></i>' :
                '<i class="far fa-star text-muted"></i>';

            item.querySelector('.d-flex').insertBefore(starBtn, item.querySelector('.flex-grow-1'));

            starBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleFavorite(countryCode, starBtn);
            });
        });
    }

    toggleFavorite(countryCode, button) {
        const favorites = JSON.parse(localStorage.getItem('country-selector-favorites') || '[]');
        const index = favorites.indexOf(countryCode);

        if (index > -1) {
            favorites.splice(index, 1);
            button.innerHTML = '<i class="far fa-star text-muted"></i>';
        } else {
            favorites.push(countryCode);
            button.innerHTML = '<i class="fas fa-star text-warning"></i>';
        }

        localStorage.setItem('country-selector-favorites', JSON.stringify(favorites));
    }
}

// Global instance
window.ValidoAICountrySelector = new ValidoAICountrySelector();
