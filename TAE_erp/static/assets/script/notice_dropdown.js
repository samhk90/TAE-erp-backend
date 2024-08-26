function toggleDropdown(button) {
    // Close all other open dropdowns
    document.querySelectorAll('.dropdown-content').forEach(function (dropdown) {
        if (dropdown !== button.nextElementSibling) {
            dropdown.classList.remove('show');
            dropdown.style.top = '100%';
            dropdown.style.transform = 'translateX(-90%)';
        }
    });

    const dropdown = button.nextElementSibling;
    dropdown.classList.toggle('show');

    // Get the bounding rectangle of the dropdown
    const rect = dropdown.getBoundingClientRect();
    const isOverflowing = rect.bottom > window.innerHeight;

    // If overflowing, adjust position to display above the button
    if (isOverflowing) {
        dropdown.style.top = '-1%';
        dropdown.style.transform = 'translateY(-85%) translateX(-90%)';
    } else {
        dropdown.style.top = '70%'; // Default position if not overflowing
        dropdown.style.transform = 'translateX(-110%)';
    }
}

// Close the dropdown if the user clicks outside of it
window.onclick = function (event) {
    if (!event.target.matches('.dropdown-button')) {
        document.querySelectorAll('.dropdown-content').forEach(function (dropdown) {
            dropdown.classList.remove('show');
            dropdown.style.top = '100%'; // Reset the position
            dropdown.style.transform = 'translateX(-90%)'; // Reset the position
        });
    }
}
