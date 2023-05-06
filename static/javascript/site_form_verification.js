/* A group of functions that verify that there are not duplicates being added to the system */

const siteNameInput = document.getElementById('site_name')
const siteNameErrorMessage = document.getElementById('site_name_errors')

const ipAddressInput = document.getElementById('ip_addr');
const ipAddressErrorMessage = document.getElementById('ip_addr_errors')

let current_site_name;

siteNameInput.addEventListener('input', function() {
    fetch(`/check_site_name?site_name=${encodeURIComponent(siteNameInput.value)}&current_site_name=${encodeURIComponent(current_site_name)}`)
    .then(response => {
        if (!response.ok) {
            siteNameErrorMessage.textContent = "Site name already exists in the database. Please choose another name.";
            siteNameErrorMessage.style.backgroundColor = 'yellow'
        } else {
            siteNameErrorMessage.textContent = "";
            siteNameErrorMessage.style.backgroundColor = ''
        }
    })
})


siteNameInput.addEventListener("change", function() {
    if (siteNameErrorMessage.textContent) {
            alert('Please enter a unique site name.')
            siteNameInput.value = ''
            siteNameErrorMessage.textContent = ''
            siteNameErrorMessage.style.backgroundColor = ''
        }
})


// Uses regex to verify that IP Address is in proper format
ipAddressInput.addEventListener("input", function() {
    if (!isValidIpAddress(ipAddressInput.value)) {
      ipAddressErrorMessage.textContent = "Please enter a valid IP address.";
      ipAddressErrorMessage.style.backgroundColor = 'yellow'
    } else {
      ipAddressErrorMessage.textContent = "";
      ipAddressErrorMessage.style.backgroundColor = ''
    }
})


ipAddressInput.addEventListener("change", function() {
    if (!isValidIpAddress(ipAddressInput.value)) {
        alert('Please enter a valid IP address');
        ipAddressInput.value = '';
        ipAddressErrorMessage.textContent = "";
        ipAddressErrorMessage.style.backgroundColor = ''
        }
})


function isValidIpAddress(ipAddress) {
    const ipAddressRegex = /^([0-9]{1,3}\.){3}[0-9]{1,3}$/;
    return ipAddressRegex.test(ipAddress);
}