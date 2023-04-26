/* A group of functions that verify that there are not duplicates being added to the system */

function check_site_name_in_db() {
    input = document.getElementById('site_name')
    site_name = input.value
    fetch(`/validate/site/${site_name}`).then(response => {
        if (!response.ok) {
            input.value = ''
            window.alert(`${site_name} is already registered to the database, please rename your site`)
        }
    })
}


function check_username_in_db() {
    input = document.getElementById('username')
    username = input.value
    fetch(`/validate/user/username/${username}`).then(response => {
        if (!response.ok) {
            input.value = ''
            window.alert(`${username} is already registered to the database, please enter a different username`)
        }
    })
}

function check_name_in_db() {
    first_name = document.getElementById('first_name').value
    last_name = document.getElementById('last_name').value

    let name = `${first_name}*{last_name}`
    fetch(`/validate/user/name/${name}`).then(response => {
        if (!response.ok) {
            input.value = ''
            window.alert(`${username} is already registered to the database, please enter a different username`)
        }
    })

}

