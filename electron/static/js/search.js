document.addEventListener('DOMContentLoaded', function() {
    const advancedToggle = document.querySelector('.advanced-search-toggle');
    const advancedOptions = document.querySelector('.advanced-search-options');

    advancedToggle.addEventListener('click', function() {
        advancedOptions.style.display = advancedOptions.style.display === 'none' ? 'block' : 'none';
    });

    // Auto-submit form when filters change
    const filterInputs = document.querySelectorAll('.advanced-search-options select, .advanced-search-options input');
    filterInputs.forEach(input => {
        input.addEventListener('change', function() {
            document.querySelector('.search-form').submit();
        });
    });
}); 