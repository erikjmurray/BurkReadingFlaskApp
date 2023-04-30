/* A group of functions that verify that there are not duplicates being added to the system */

const siteNameInput = document.getElementById('site_name')
const siteNameErrorMessage = document.getElementById('site_name_errors')

const ipAddressInput = document.getElementById('ip_addr');
const ipAddressErrorMessage = document.getElementById('ip_addr_errors')

siteNameInput.addEventListener('input', function() {
    fetch(`/check_site_name?site_name=${encodeURIComponent(siteNameInput)}`)
    .then(response => {
        if (!response.ok) {
            siteNameErrorMessage.textContent = "Site name already exists in the database. Please choose another name.";
            siteNameErrorMessage.style = 'background-color: yellow;'
        } else {
            siteNameErrorMessage.textContent = "";
        }
    })
})


// Uses regex to verify that IP Address is in proper format
ipAddressInput.addEventListener("input", function() {
    if (!isValidIpAddress(ipAddressInput.value)) {
      ipAddressErrorMessage.textContent = "Please enter a valid IP address.";
    } else {
      ipAddressErrorMessage.textContent = "";
    }
})


function isValidIpAddress(ipAddress) {
    const ipAddressRegex = /^([0-9]{1,3}\.){3}[0-9]{1,3}$/;
    return ipAddressRegex.test(ipAddress);
}