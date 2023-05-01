/* Signup Form Validation scripts */
// Get DOM elements
const firstNameInput = document.getElementById('first_name');
const lastNameInput = document.getElementById('last_name');

const usernameInput = document.getElementById("username");
const usernameErrorMessage = document.getElementById("username-error-message");

//const passwordInput = document.getElementById("password");
//const passwordErrorMessage = document.getElementById("password-error-message");

// Listeners for DOM elements
firstNameInput.addEventListener('input', generateUsername);
lastNameInput.addEventListener('input', generateUsername);


function generateUsername() {
  const firstName = firstNameInput.value.trim().toLowerCase();
  const lastName = lastNameInput.value.trim().toLowerCase();

  // Only generate a username if both the first name and last name input fields have values
  if (firstName && lastName) {
    const firstLetter = firstName.charAt(0);
    const username = firstLetter + lastName;

    // Update the value of the username input field with the generated username
    usernameInput.value = username;
    check_database_for_username(usernameInput.value)
  } else {
    // If either the first name or last name input field is empty, clear the username input field
    usernameInput.value = '';
  }
}


usernameInput.addEventListener('input', function() {
    check_database_for_username(usernameInput.value)
});

// Alerts User that their password should include Upper, Lower, Number, and Symbol
//passwordInput.addEventListener("input", function() {
//  passwordErrorMessage.style=""
//    let passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$/;
//  if (passwordRegex.test(passwordInput.value)) {
//    passwordErrorMessage.textContent = ""; // clear error message if email is valid
//  } else {
//    passwordErrorMessage.textContent = "Password must be at least 8 characters long and include a minimum of uppercase, lowercase, number, and symbol";
//  }
//});


// Database queries for unique values
function check_database_for_username(username) {
    fetch(`/check_username?username=${encodeURIComponent(username)}`)
    .then(response => response.json())
    .then(data => {
      if (data.exists) {
        usernameErrorMessage.textContent = "That username already exists. Please contact your local admin";
        usernameErrorMessage.style.backgroundColor = 'yellow'
      } else {
        usernameErrorMessage.textContent = "";
      }
    });
}