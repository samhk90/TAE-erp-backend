document.addEventListener("DOMContentLoaded", function () {
    var loader = document.getElementById('loader');
    
    // Function to show the loader
    function showLoader() {
        loader.style.display = 'flex';
    }

    // Function to hide the loader
    function hideLoader() {
        loader.style.display = 'none';
    }

    // Attach submit event listener to all forms
    var forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            // Show the loader
            showLoader();
        });
    });

    // Optionally, you can hide the loader after a short delay
    window.addEventListener('load', function () {
        setTimeout(hideLoader, 100); // Adjust delay if needed
    });
});
