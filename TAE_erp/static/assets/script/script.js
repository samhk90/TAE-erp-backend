const number = document.getElementById("num");

// Get the `randomNum` value from the heading tag
const heading = document.getElementById("randomNumHeading");
const randomNum = parseInt(heading.textContent, 10);

let counter = 0;
const time = 2000 / randomNum;

const interval = setInterval(() => {
    if (counter === randomNum) {
        clearInterval(interval);
        number.innerHTML = randomNum + "%";
    } else {
        counter += 1;
        number.innerHTML = counter + "%";
    }
}, time);

const css = window.document.styleSheets[0];

const stroke = 440 - (440 * (randomNum / 100));
css.insertRule(`
@keyframes anim {
    100% {
        stroke-dashoffset: ${stroke};
    }
}
`, css.cssRules.length);

























// Index page announcement modal script

document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById("modal");
    var btn = document.getElementById("addButton");
    var span = document.getElementsByClassName("close")[0];

    btn.addEventListener('click', function() {
        modal.style.visibility = "visible";
        modal.style.opacity = "1";
    });
    span.addEventListener('click', function() {
        modal.style.visibility = "hidden";
        modal.style.opacity = "0";
    });

    
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.visibility = "hidden";
            modal.style.opacity = "0";
        }
    });

    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
});


document.addEventListener('DOMContentLoaded', function() {
    function getSelectedDepartments() {
        var selectElement = document.getElementById('department');
        var selectedOptions = Array.from(selectElement.selectedOptions);
        return selectedOptions.map(option => option.value);
    }

    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();
        var selectedDepartments = getSelectedDepartments();
    });
});































// Function to handle clicks on .user elements
document.querySelectorAll('.user').forEach(userElement => {
    userElement.addEventListener('click', function (event) {
        // Stop click event from bubbling up to the document
        event.stopPropagation();

        // Hide any currently visible .desc boxes
        document.querySelectorAll('.info.expanded').forEach(expandedInfo => {
            expandedInfo.classList.remove('expanded');
        });

        // Show the clicked .desc box
        const infoDiv = this.closest('.info');
        infoDiv.classList.toggle('expanded');
    });
});

// Function to handle clicks outside of .info elements
document.addEventListener('click', function (event) {
    if (!event.target.closest('.info')) {
        document.querySelectorAll('.info.expanded').forEach(expandedInfo => {
            expandedInfo.classList.remove('expanded');
        });
    }
});

// Function to handle clicks on the close button
document.addEventListener('click', function (event) {
    if (event.target.classList.contains('close-btn')) {
        event.stopPropagation(); // Prevent the event from bubbling up
        const desc = event.target.closest('.desc');
        if (desc) {
            desc.parentElement.classList.remove('expanded'); // Remove the expanded class from .info
        }
    }
});
