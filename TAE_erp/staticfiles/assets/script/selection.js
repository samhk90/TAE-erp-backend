
document.addEventListener('DOMContentLoaded', function() {
    var semSelectors = document.querySelectorAll('.sem');
    var submitButtons = document.querySelectorAll('.submit-btn');

    // Initialize submission counters
    var submissionCounters = [];

    semSelectors.forEach(function(semSelector) {
        semSelector.addEventListener('change', function() {
            var semester = this.value;
            var row = this.closest('tr');
            var subSelector = row.querySelector('.sub1');

            // Clear existing options
            subSelector.innerHTML = '';

            if (semester === 'sem1') {
                subSelector.disabled = false;
                subSelector.innerHTML = '<option disabled selected>Select Sem 1 Sub</option>' +
                                        '<option value="sub1">Subject 1</option>' +
                                        '<option value="sub2">Subject 2</option>' +
                                        '<option value="sub3">Subject 3</option>' +
                                        '<option value="sub4">Subject 4</option>';
            } else if (semester === 'sem2') {
                subSelector.disabled = false;
                subSelector.innerHTML = '<option disabled selected>Select Sem 2 Sub</option>' +
                                        '<option value="sub12">Subject 12</option>' +
                                        '<option value="sub22">Subject 22</option>' +
                                        '<option value="sub32">Subject 32</option>' +
                                        '<option value="sub42">Subject 42</option>';
            } else {
                subSelector.disabled = true;
                subSelector.innerHTML = '<option disabled selected>Select Semester First</option>';
            }
        });
    });

    submitButtons.forEach(function(submitButton, index) {
        // Initialize the submission counter for each row
        submissionCounters[index] = 0;

        submitButton.addEventListener('click', function() {
            var row = this.closest('tr');
            var semForm = row.querySelector('.sem-form');
            var subForm = row.querySelector('.sub-form');

            // Increase the submission counter
            submissionCounters[index] += 1;

            // Create form data objects and log them (replace with actual form submission logic)
            var semFormData = new FormData(semForm);
            var subFormData = new FormData(subForm);
            
            console.log('Submitting forms for row ' + (index + 1));
            console.log('Semester Form Data:', semFormData.get('sem'));
            console.log('Subject Form Data:', subFormData.get('sub1'));

            // Disable the button if it has been clicked 5 times
            if (submissionCounters[index] >= 5) {
                this.disabled = true;
            }
        });
    });
});
