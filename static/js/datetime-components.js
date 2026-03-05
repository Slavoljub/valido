/**
 * DateTime Components for ValidoAI
 * Comprehensive date, time, calendar, and datetime pickers
 */

class ValidoAIDateTimeComponents {
    constructor() {
        this.pickers = new Map();
        this.defaultOptions = {
            locale: 'en',
            dateFormat: 'YYYY-MM-DD',
            timeFormat: 'HH:mm',
            weekStart: 1,
            firstDayOfWeek: 1,
            showWeekNumbers: true,
            showTodayButton: true,
            showClearButton: true,
            autoClose: true,
            timePicker: true,
            minuteIncrement: 15,
            hourIncrement: 1,
            position: 'auto',
            zIndex: 9999,
            theme: 'light',
            animations: true,
            minDate: null,
            maxDate: null,
            disabledDates: [],
            enabledDates: [],
            disabledWeekdays: [],
            enableTimezones: false,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
    }

    init(selector, options = {}) {
        const pickerId = this.generateId();
        const config = this.mergeOptions(options);

        // Create picker container
        const container = this.createPickerContainer(selector, config);

        // Initialize Flatpickr or native picker based on browser support
        const picker = this.initializePicker(selector, container, config);

        this.pickers.set(pickerId, {
            picker: picker,
            selector: selector,
            config: config,
            container: container,
            type: config.type || 'datetime'
        });

        this.applyThemeIntegration(pickerId);
        this.addCustomFeatures(pickerId);

        return pickerId;
    }

    createPickerContainer(selector, config) {
        const element = document.querySelector(selector);
        if (!element) return null;

        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'datetime-picker-wrapper position-relative';
        element.parentNode.insertBefore(wrapper, element);
        wrapper.appendChild(element);

        // Add custom elements
        const customElements = document.createElement('div');
        customElements.className = 'datetime-custom-elements d-none';
        customElements.innerHTML = this.getCustomElementsHTML(config);
        wrapper.appendChild(customElements);

        return {
            wrapper: wrapper,
            element: element,
            customElements: customElements
        };
    }

    getCustomElementsHTML(config) {
        return `
            <div class="datetime-actions p-2 border-top">
                <div class="row g-2">
                    <div class="col-auto">
                        <button type="button" class="btn btn-sm btn-outline-primary today-btn">
                            <i class="fas fa-calendar-day"></i> Today
                        </button>
                    </div>
                    <div class="col-auto">
                        <button type="button" class="btn btn-sm btn-outline-secondary clear-btn">
                            <i class="fas fa-times"></i> Clear
                        </button>
                    </div>
                    <div class="col-auto">
                        <button type="button" class="btn btn-sm btn-outline-info timezones-btn" ${config.enableTimezones ? '' : 'disabled'}>
                            <i class="fas fa-globe"></i> TZ
                        </button>
                    </div>
                    <div class="col">
                        <div class="timezone-selector d-none">
                            <select class="form-select form-select-sm timezone-select">
                                ${this.getTimezoneOptions()}
                            </select>
                        </div>
                    </div>
                </div>
            </div>
            <div class="datetime-presets d-none">
                <div class="presets-header p-2 border-bottom">
                    <strong>Quick Select</strong>
                </div>
                <div class="presets-body p-2">
                    <div class="row g-1">
                        <div class="col-6">
                            <button type="button" class="btn btn-sm btn-outline-secondary w-100 preset-btn" data-preset="today">
                                Today
                            </button>
                        </div>
                        <div class="col-6">
                            <button type="button" class="btn btn-sm btn-outline-secondary w-100 preset-btn" data-preset="tomorrow">
                                Tomorrow
                            </button>
                        </div>
                        <div class="col-6">
                            <button type="button" class="btn btn-sm btn-outline-secondary w-100 preset-btn" data-preset="week_start">
                                Week Start
                            </button>
                        </div>
                        <div class="col-6">
                            <button type="button" class="btn btn-sm btn-outline-secondary w-100 preset-btn" data-preset="week_end">
                                Week End
                            </button>
                        </div>
                        <div class="col-6">
                            <button type="button" class="btn btn-sm btn-outline-secondary w-100 preset-btn" data-preset="month_start">
                                Month Start
                            </button>
                        </div>
                        <div class="col-6">
                            <button type="button" class="btn btn-sm btn-outline-secondary w-100 preset-btn" data-preset="month_end">
                                Month End
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getTimezoneOptions() {
        const timezones = [
            'UTC', 'America/New_York', 'America/Los_Angeles', 'Europe/London',
            'Europe/Paris', 'Europe/Berlin', 'Asia/Tokyo', 'Asia/Shanghai',
            'Asia/Dubai', 'Australia/Sydney', 'Pacific/Auckland'
        ];

        return timezones.map(tz => `<option value="${tz}">${tz}</option>`).join('');
    }

    initializePicker(selector, container, config) {
        // Try to use Flatpickr if available, fallback to native
        if (window.flatpickr) {
            return this.initFlatpickr(selector, container, config);
        } else {
            return this.initNativePicker(selector, container, config);
        }
    }

    initFlatpickr(selector, container, config) {
        const flatpickrConfig = {
            enableTime: config.timePicker,
            dateFormat: config.dateFormat + (config.timePicker ? ' ' + config.timeFormat : ''),
            locale: this.getFlatpickrLocale(config.locale),
            weekNumbers: config.showWeekNumbers,
            minDate: config.minDate,
            maxDate: config.maxDate,
            disable: config.disabledDates,
            enable: config.enabledDates,
            disableMobile: true,
            position: config.position,
            appendTo: container.wrapper,
            onOpen: () => this.onPickerOpen(container),
            onClose: () => this.onPickerClose(container),
            onChange: (selectedDates, dateStr, instance) => this.onDateChange(selectedDates, dateStr, instance)
        };

        return flatpickr(selector, flatpickrConfig);
    }

    initNativePicker(selector, container, config) {
        const element = document.querySelector(selector);
        const inputType = config.timePicker ? 'datetime-local' : 'date';

        element.type = inputType;
        element.addEventListener('change', (e) => this.onNativeChange(e, config));

        return {
            element: element,
            config: config,
            type: 'native'
        };
    }

    onPickerOpen(container) {
        container.customElements.classList.remove('d-none');
        this.bindCustomEvents(container);
    }

    onPickerClose(container) {
        // Keep custom elements visible for a short time for better UX
        setTimeout(() => {
            if (!container.wrapper.matches(':hover')) {
                container.customElements.classList.add('d-none');
            }
        }, 200);
    }

    bindCustomEvents(container) {
        // Remove existing event listeners to prevent duplicates
        container.customElements.querySelectorAll('.today-btn, .clear-btn, .timezones-btn, .preset-btn')
            .forEach(btn => {
                btn.replaceWith(btn.cloneNode(true));
            });

        // Today button
        container.customElements.querySelector('.today-btn').addEventListener('click', () => {
            const today = new Date();
            this.setDate(container.element, today);
        });

        // Clear button
        container.customElements.querySelector('.clear-btn').addEventListener('click', () => {
            container.element.value = '';
            container.element.dispatchEvent(new Event('change'));
        });

        // Timezone button
        container.customElements.querySelector('.timezones-btn').addEventListener('click', () => {
            const tzSelector = container.customElements.querySelector('.timezone-selector');
            tzSelector.classList.toggle('d-none');
        });

        // Preset buttons
        container.customElements.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const preset = e.target.dataset.preset;
                const date = this.getPresetDate(preset);
                this.setDate(container.element, date);
            });
        });
    }

    getPresetDate(preset) {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        switch (preset) {
            case 'today':
                return today;
            case 'tomorrow':
                const tomorrow = new Date(today);
                tomorrow.setDate(today.getDate() + 1);
                return tomorrow;
            case 'week_start':
                const weekStart = new Date(today);
                const day = today.getDay();
                const diff = today.getDate() - day + (day === 0 ? -6 : 1); // Adjust for Sunday
                weekStart.setDate(diff);
                return weekStart;
            case 'week_end':
                const weekEnd = new Date(today);
                const dayDiff = today.getDate() - today.getDay() + 7;
                weekEnd.setDate(dayDiff);
                return weekEnd;
            case 'month_start':
                return new Date(today.getFullYear(), today.getMonth(), 1);
            case 'month_end':
                return new Date(today.getFullYear(), today.getMonth() + 1, 0);
            default:
                return today;
        }
    }

    setDate(element, date) {
        if (window.flatpickr && element._flatpickr) {
            element._flatpickr.setDate(date);
        } else {
            // For native input
            const formatted = this.formatDateForInput(date, element.type === 'datetime-local');
            element.value = formatted;
            element.dispatchEvent(new Event('change'));
        }
    }

    formatDateForInput(date, includeTime = false) {
        if (includeTime) {
            return date.toISOString().slice(0, 16);
        } else {
            return date.toISOString().slice(0, 10);
        }
    }

    getFlatpickrLocale(locale) {
        // Map common locales to Flatpickr locales
        const localeMap = {
            'en': 'default',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
            'pt': 'pt',
            'ru': 'ru',
            'ja': 'ja',
            'zh': 'zh'
        };

        return localeMap[locale] || 'default';
    }

    onDateChange(selectedDates, dateStr, instance) {
        // Custom date change handling
        if (selectedDates.length > 0) {
            const date = selectedDates[0];
            this.validateDate(date, instance.config);

            // Trigger custom event
            const event = new CustomEvent('datetimeChange', {
                detail: {
                    date: date,
                    dateStr: dateStr,
                    instance: instance
                }
            });
            instance.element.dispatchEvent(event);
        }
    }

    onNativeChange(event, config) {
        const date = new Date(event.target.value);
        if (!isNaN(date.getTime())) {
            this.validateDate(date, config);
        }
    }

    validateDate(date, config) {
        // Validate min/max dates
        if (config.minDate && date < new Date(config.minDate)) {
            if (window.showToast) {
                showToast('warning', 'Date is before minimum allowed date');
            }
        }

        if (config.maxDate && date > new Date(config.maxDate)) {
            if (window.showToast) {
                showToast('warning', 'Date is after maximum allowed date');
            }
        }

        // Validate disabled dates
        if (config.disabledDates.length > 0) {
            const dateStr = date.toDateString();
            if (config.disabledDates.some(d => new Date(d).toDateString() === dateStr)) {
                if (window.showToast) {
                    showToast('warning', 'This date is not available');
                }
            }
        }
    }

    applyThemeIntegration(pickerId) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData) return;

        // Listen for theme changes
        document.addEventListener('themeChanged', (event) => {
            this.updatePickerTheme(pickerId, event.detail.theme);
        });

        // Initial theme application
        const currentTheme = localStorage.getItem('valido-theme') || 'valido-white';
        this.updatePickerTheme(pickerId, currentTheme);
    }

    updatePickerTheme(pickerId, theme) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData) return;

        const isDark = ['valido-dark', 'material-dark', 'dracula', 'monokai'].includes(theme);
        const container = pickerData.container.wrapper;

        container.classList.toggle('datetime-theme-dark', isDark);

        // Update Flatpickr theme if available
        if (pickerData.picker && pickerData.picker.config) {
            pickerData.picker.config.theme = isDark ? 'dark' : 'light';
            if (pickerData.picker.redraw) {
                pickerData.picker.redraw();
            }
        }
    }

    addCustomFeatures(pickerId) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData) return;

        // Add range picker support
        this.addRangeSupport(pickerId);

        // Add time zone conversion
        this.addTimezoneSupport(pickerId);

        // Add date calculations
        this.addDateCalculations(pickerId);

        // Add recurring dates
        this.addRecurringDates(pickerId);
    }

    addRangeSupport(pickerId) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData || pickerData.config.type !== 'range') return;

        // Add range selection UI
        const rangeUI = document.createElement('div');
        rangeUI.className = 'datetime-range-ui mb-3 p-3 border rounded d-none';
        rangeUI.innerHTML = `
            <div class="row g-3">
                <div class="col-6">
                    <label class="form-label">Start Date</label>
                    <input type="date" class="form-control range-start">
                </div>
                <div class="col-6">
                    <label class="form-label">End Date</label>
                    <input type="date" class="form-control range-end">
                </div>
            </div>
            <div class="mt-2 text-end">
                <button class="btn btn-sm btn-primary apply-range">Apply Range</button>
            </div>
        `;

        pickerData.container.customElements.appendChild(rangeUI);

        // Toggle range UI
        const rangeBtn = document.createElement('button');
        rangeBtn.className = 'btn btn-sm btn-outline-info range-toggle';
        rangeBtn.innerHTML = '<i class="fas fa-arrows-alt-h"></i> Range';
        rangeBtn.onclick = () => rangeUI.classList.toggle('d-none');

        pickerData.container.customElements.querySelector('.datetime-actions .row').appendChild(
            document.createElement('div').appendChild(rangeBtn).parentNode
        );
    }

    addTimezoneSupport(pickerId) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData || !pickerData.config.enableTimezones) return;

        const tzSelect = pickerData.container.customElements.querySelector('.timezone-select');
        if (tzSelect) {
            tzSelect.addEventListener('change', (e) => {
                const timezone = e.target.value;
                this.convertTimezone(pickerData, timezone);
            });
        }
    }

    convertTimezone(pickerData, targetTimezone) {
        const currentValue = pickerData.container.element.value;
        if (!currentValue) return;

        try {
            const date = new Date(currentValue);
            const converted = new Intl.DateTimeFormat('en-US', {
                timeZone: targetTimezone,
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            }).format(date);

            if (window.showToast) {
                showToast('info', `Converted to ${targetTimezone}: ${converted}`);
            }
        } catch (error) {
            console.error('Timezone conversion error:', error);
        }
    }

    addDateCalculations(pickerId) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData) return;

        const calcUI = document.createElement('div');
        calcUI.className = 'datetime-calculations mb-3 p-3 border rounded d-none';
        calcUI.innerHTML = `
            <div class="row g-3">
                <div class="col-6">
                    <label class="form-label">Operation</label>
                    <select class="form-select calc-operation">
                        <option value="add">Add</option>
                        <option value="subtract">Subtract</option>
                    </select>
                </div>
                <div class="col-3">
                    <label class="form-label">Value</label>
                    <input type="number" class="form-control calc-value" min="1">
                </div>
                <div class="col-3">
                    <label class="form-label">Unit</label>
                    <select class="form-select calc-unit">
                        <option value="days">Days</option>
                        <option value="weeks">Weeks</option>
                        <option value="months">Months</option>
                        <option value="years">Years</option>
                    </select>
                </div>
            </div>
            <div class="mt-2 text-end">
                <button class="btn btn-sm btn-success calculate-date">Calculate</button>
            </div>
        `;

        pickerData.container.customElements.appendChild(calcUI);

        // Toggle calculations UI
        const calcBtn = document.createElement('button');
        calcBtn.className = 'btn btn-sm btn-outline-warning calc-toggle';
        calcBtn.innerHTML = '<i class="fas fa-calculator"></i> Calc';
        calcBtn.onclick = () => calcUI.classList.toggle('d-none');

        pickerData.container.customElements.querySelector('.datetime-actions .row').appendChild(
            document.createElement('div').appendChild(calcBtn).parentNode
        );

        // Bind calculation
        calcUI.querySelector('.calculate-date').addEventListener('click', () => {
            this.performDateCalculation(pickerData, calcUI);
        });
    }

    performDateCalculation(pickerData, calcUI) {
        const currentValue = pickerData.container.element.value;
        if (!currentValue) {
            if (window.showToast) showToast('warning', 'Please select a date first');
            return;
        }

        const operation = calcUI.querySelector('.calc-operation').value;
        const value = parseInt(calcUI.querySelector('.calc-value').value);
        const unit = calcUI.querySelector('.calc-unit').value;

        if (!value || value <= 0) {
            if (window.showToast) showToast('warning', 'Please enter a valid value');
            return;
        }

        const date = new Date(currentValue);
        const multiplier = operation === 'subtract' ? -1 : 1;

        switch (unit) {
            case 'days':
                date.setDate(date.getDate() + (value * multiplier));
                break;
            case 'weeks':
                date.setDate(date.getDate() + (value * 7 * multiplier));
                break;
            case 'months':
                date.setMonth(date.getMonth() + (value * multiplier));
                break;
            case 'years':
                date.setFullYear(date.getFullYear() + (value * multiplier));
                break;
        }

        this.setDate(pickerData.container.element, date);

        if (window.showToast) {
            showToast('success', `Date ${operation === 'add' ? 'increased' : 'decreased'} by ${value} ${unit}`);
        }
    }

    addRecurringDates(pickerId) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData) return;

        const recurringUI = document.createElement('div');
        recurringUI.className = 'datetime-recurring mb-3 p-3 border rounded d-none';
        recurringUI.innerHTML = `
            <div class="row g-3">
                <div class="col-12">
                    <label class="form-label">Frequency</label>
                    <select class="form-select recurring-frequency">
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="yearly">Yearly</option>
                    </select>
                </div>
                <div class="col-6">
                    <label class="form-label">Occurrences</label>
                    <input type="number" class="form-control recurring-count" min="1" max="100" value="5">
                </div>
                <div class="col-6">
                    <label class="form-label">Interval</label>
                    <input type="number" class="form-control recurring-interval" min="1" value="1">
                </div>
            </div>
            <div class="mt-2">
                <button class="btn btn-sm btn-info generate-recurring">Generate Dates</button>
            </div>
            <div class="recurring-results mt-2 d-none">
                <strong>Generated Dates:</strong>
                <div class="recurring-list mt-1"></div>
            </div>
        `;

        pickerData.container.customElements.appendChild(recurringUI);

        // Toggle recurring UI
        const recurringBtn = document.createElement('button');
        recurringBtn.className = 'btn btn-sm btn-outline-success recurring-toggle';
        recurringBtn.innerHTML = '<i class="fas fa-redo"></i> Recur';
        recurringBtn.onclick = () => recurringUI.classList.toggle('d-none');

        pickerData.container.customElements.querySelector('.datetime-actions .row').appendChild(
            document.createElement('div').appendChild(recurringBtn).parentNode
        );

        // Bind recurring generation
        recurringUI.querySelector('.generate-recurring').addEventListener('click', () => {
            this.generateRecurringDates(pickerData, recurringUI);
        });
    }

    generateRecurringDates(pickerData, recurringUI) {
        const currentValue = pickerData.container.element.value;
        if (!currentValue) {
            if (window.showToast) showToast('warning', 'Please select a start date first');
            return;
        }

        const frequency = recurringUI.querySelector('.recurring-frequency').value;
        const count = parseInt(recurringUI.querySelector('.recurring-count').value);
        const interval = parseInt(recurringUI.querySelector('.recurring-interval').value);

        const startDate = new Date(currentValue);
        const dates = [startDate];

        for (let i = 1; i < count; i++) {
            const nextDate = new Date(startDate);

            switch (frequency) {
                case 'daily':
                    nextDate.setDate(startDate.getDate() + (i * interval));
                    break;
                case 'weekly':
                    nextDate.setDate(startDate.getDate() + (i * 7 * interval));
                    break;
                case 'monthly':
                    nextDate.setMonth(startDate.getMonth() + (i * interval));
                    break;
                case 'yearly':
                    nextDate.setFullYear(startDate.getFullYear() + (i * interval));
                    break;
            }

            dates.push(nextDate);
        }

        // Display results
        const resultsList = recurringUI.querySelector('.recurring-list');
        resultsList.innerHTML = dates.map(date => `
            <div class="badge bg-secondary me-1 mb-1">${date.toLocaleDateString()}</div>
        `).join('');

        recurringUI.querySelector('.recurring-results').classList.remove('d-none');

        if (window.showToast) {
            showToast('success', `Generated ${dates.length} recurring dates`);
        }
    }

    // Utility methods
    generateId() {
        return 'datetime_' + Math.random().toString(36).substr(2, 9);
    }

    destroy(pickerId) {
        const pickerData = this.pickers.get(pickerId);
        if (pickerData) {
            if (pickerData.picker && pickerData.picker.destroy) {
                pickerData.picker.destroy();
            }
            this.pickers.delete(pickerId);
        }
    }

    getValue(pickerId) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData) return null;

        const element = pickerData.container.element;
        return element.value ? new Date(element.value) : null;
    }

    setValue(pickerId, date) {
        const pickerData = this.pickers.get(pickerId);
        if (!pickerData) return;

        this.setDate(pickerData.container.element, new Date(date));
    }

    // Specialized picker creation methods
    createDatePicker(selector, options = {}) {
        return this.init(selector, { ...options, type: 'date', timePicker: false });
    }

    createTimePicker(selector, options = {}) {
        return this.init(selector, { ...options, type: 'time', timePicker: true, dateFormat: '' });
    }

    createDateTimePicker(selector, options = {}) {
        return this.init(selector, { ...options, type: 'datetime', timePicker: true });
    }

    createRangePicker(selector, options = {}) {
        return this.init(selector, { ...options, type: 'range', mode: 'range' });
    }

    createMonthPicker(selector, options = {}) {
        return this.init(selector, { ...options, type: 'month', timePicker: false, dateFormat: 'Y-m' });
    }

    createYearPicker(selector, options = {}) {
        return this.init(selector, { ...options, type: 'year', timePicker: false, dateFormat: 'Y' });
    }
}

// Global instance
window.ValidoAIDateTimeComponents = new ValidoAIDateTimeComponents();
