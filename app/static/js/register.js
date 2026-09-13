/* =========================================
   REGISTRATION FORM LOGIC (STANDALONE)
   ========================================= */

// Global variable to track current step
let currentRegStep = 1;

// Function to move to the next step
function nextStep(stepNumber) {
    // 1. Validate current step's inputs before moving forward
    const currentStepElement = document.getElementById(`step-${currentRegStep}`);
    const inputs = currentStepElement.querySelectorAll('input[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        // Skip validation for hidden fields (like if user switched roles)
        if (input.offsetParent === null) return; 

        if (!input.checkValidity()) {
            input.reportValidity(); // Shows default browser error message
            isValid = false;
        }
    });

    // Special validation for Step 5 (Password matching)
    if (currentRegStep === 5 && isValid) {
        const pass = document.querySelector('input[name="password"]').value;
        const confirmPass = document.querySelector('input[name="confirmPassword"]').value;
        if (pass !== confirmPass) {
            alert("Passwords do not match! Please try again.");
            isValid = false;
        }
    }

    if (!isValid) return; // Stop if validation fails

    // 2. Hide current step
    currentStepElement.classList.remove('active');
    
    // 3. Show new step
    const nextStepElement = document.getElementById(`step-${stepNumber}`);
    if (nextStepElement) {
        nextStepElement.classList.add('active');
        currentRegStep = stepNumber;
        updateProgressBar();
        
        // If moving to Step 4, adjust fields based on chosen role
        if (stepNumber === 4) {
            updateStep4Fields();
        }

        // If moving to Step 6, populate the review box with actual values
        if (stepNumber === 6) {
            populateReviewBox();
        }
    }
}

// Function to move to the previous step
function prevStep(stepNumber) {
    document.getElementById(`step-${currentRegStep}`).classList.remove('active');
    document.getElementById(`step-${stepNumber}`).classList.add('active');
    currentRegStep = stepNumber;
    updateProgressBar();
}

// Update the visual progress circles (1 to 7)
function updateProgressBar() {
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach(step => {
        const stepNum = parseInt(step.getAttribute('data-step'));
        if (stepNum <= currentRegStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

// Dynamically change Step 4 content based on Farmer/Buyer selection
function updateStep4Fields() {
    const selectedRole = document.querySelector('input[name="role"]:checked');
    if (!selectedRole) return;

    const role = selectedRole.value;
    const step4Title = document.getElementById('step4-title');
    const step4Subtitle = document.getElementById('step4-subtitle');
    const farmerFields = document.getElementById('farmer-fields');
    const buyerFields = document.getElementById('buyer-fields');

    if (role === 'farmer') {
        step4Title.textContent = "Farming Details";
        step4Subtitle.textContent = "Tell us what you grow.";
        farmerFields.style.display = 'grid';
        buyerFields.style.display = 'none';
        
        // Make farmer fields required
        farmerFields.querySelectorAll('input').forEach(i => i.required = true);
        // Remove requirement from buyer fields
        buyerFields.querySelectorAll('input').forEach(i => i.required = false);
    } else {
        step4Title.textContent = "Buying Details";
        step4Subtitle.textContent = "Tell us what you're looking for.";
        farmerFields.style.display = 'none';
        buyerFields.style.display = 'grid';
        
        // Make buyer fields required
        buyerFields.querySelectorAll('input').forEach(i => i.required = true);
        // Remove requirement from farmer fields
        farmerFields.querySelectorAll('input').forEach(i => i.required = false);
    }
}

// =========================================
// Populate the Review Box (Step 6) with actual form data
// =========================================
function populateReviewBox() {
    // 1. Get selected role
    const roleInput = document.querySelector('input[name="role"]:checked');
    if (!roleInput) return;

    const role = roleInput.value; // "farmer" or "buyer"
    
    // 2. Get name and email from the form
    const nameInput = document.querySelector('input[name="fullName"]');
    const emailInput = document.querySelector('input[name="email"]');
    
    const name = nameInput ? nameInput.value : '';
    const email = emailInput ? emailInput.value : '';

    // 3. Update the review box with actual values
    document.getElementById('review-role').textContent = 
        role.charAt(0).toUpperCase() + role.slice(1);  // "Farmer" or "Buyer"
    document.getElementById('review-name').textContent = name;
    document.getElementById('review-email').textContent = email;
}