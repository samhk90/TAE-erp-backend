function toggleDropdown(button) {
    // Close all other open dropdowns
    document.querySelectorAll('.dropdown-content').forEach(function (dropdown) {
        if (dropdown !== button.nextElementSibling) {
            dropdown.classList.remove('show');
            dropdown.style.top = 'auto';
            dropdown.style.bottom = '100%';
            dropdown.style.transform = 'translateX(-50%) translateY(-10px)'; 
        }
    });

    const dropdown = button.nextElementSibling;
    dropdown.classList.toggle('show');

    // Get the bounding rectangle of the dropdown and the button
    const rect = dropdown.getBoundingClientRect();
    const buttonRect = button.getBoundingClientRect();

    // Calculate space above and below the button
    const spaceBelow = window.innerHeight - buttonRect.bottom;
    const spaceAbove = buttonRect.top;

    // Adjust dropdown position to always display above the button
    dropdown.style.top = 'auto';
    dropdown.style.bottom = '-5%';
    dropdown.style.transform = 'translateX(-105%) translateY(-1px)';
}

// Close dropdown if the user clicks outside
window.onclick = function (event) {
    if (!event.target.matches('.dropdown-button')) {
        document.querySelectorAll('.dropdown-content').forEach(function (dropdown) {
            dropdown.classList.remove('show');
            dropdown.style.top = 'auto';
            dropdown.style.bottom = '100%';
            dropdown.style.transform = 'translateX(-50%) translateY(-10px)';
        });
    }
}
