/*
Function calls to grab Burk data from backend and fill out inputs on the form page
Automated messaging on channel out of range states
*/


/* --- ON PAGE LOAD --- */

// Clears all inputs on the page
async function reset_page() {
    let inputTags = document.getElementsByTagName('input')
    for (let tag of inputTags) {
        if (tag.type == 'checkbox' || tag.type == 'radio') {
            // must continue so as not to destroy value of radio output
            tag.checked = false;
            continue
            }
        tag.value = ''
        }
    let textAreas = document.getElementsByTagName('textarea')
    for (let text of textAreas) {text.value = ''}
}


// Loops through each site and updates each site section on page
async function load_data_to_form() {
    // gets names of all sites
    await get_sites().then(sites => {
        for (let site of sites) {
            get_burk_data(site.id, site.site_name).then(channels => {
                update_site_section(site.site_name, channels)
        })
    }
  })
}


// Calls Flask route to get array of site names
async function get_sites() {
  const response = await fetch('/api/sites');
  const sites = await response.json();
  return sites;
}


// Calls Flask route that returns current Burk data for site
async function get_burk_data(site_id, site_name) {
    response = await fetch(`/api/burk/${site_id}`)
    if (!response.ok) {
        error = `Data from ${site_name.replace('_', ' ')} did not load automatically. All readings input by user.\n`
        add_message(error)
        return Promise.error
    }
    const data = await response.json();
    return data;
}


// Searches HTML finds elements and updates them if value present from Burk API call
async function update_site_section(site_name, channels) {
    if (!channels) {return}
    for (let channel of channels) {
        // find input by designation
        let input = document.getElementById(channel.html_tag);
        if (channel.chan_type === 'meter') {
            check_limits(site_name, channel)
            input.value = +channel.value.toFixed(3)
        } else if (channel.chan_type === 'status') {
            update_radio_status(channel)
        }
    }
}


// Checks if meter values are within accepted values
// NOTE: Channel format is the output of the get_burk_data API call not Channel from database
async function check_limits(site_name, channel) {
    let cell = document.getElementById(`${channel.html_tag}_cell`)

    // query db for meter config
    get_channel_config(channel.id).then(config => {
        if (channel.value == null) {return}
        // If limit exists and != 0, if value greater/less than limit, alert
        if (channel.value >= config[0].upper_limit) {
            let message = `${site_name} ${channel.title} is above upper limit of ${config[0].upper_limit} ${config[0].units}\n`
            add_message(message)
            cell.style.backgroundColor = config[0].upper_lim_color
            }
        else if (channel.value <= config[0].lower_limit) {
            let message = `${site_name} ${channel.title} is below lower limit of ${config[0].lower_limit} ${config[0].units}\n`
            add_message(message)
            cell.style.backgroundColor = config[0].lower_lim_color
            }
        else {
            cell.style.backgroundColor = '#00ff00' // green
            }
        })
    }


// Queries database for config data
async function get_channel_config(chan_id) {
    const response = await fetch(`/api/channel_config/${chan_id}`);
    const config = await response.json();
    return config;
}


// Checks the Radio btn that matches its expected value from config.
// NOTE: Can provide False positive if multiple channels with config bool match
async function update_radio_status(channel) {
    get_channel_config(channel.id).then(config => {
        for (let [index, option] of config.entries()) {
            if (channel.value[index] == null) { continue }
            if (channel.value[index] == option.selected_state) {
                // select input if burk status value equals config value
                let input=document.getElementById(`${channel.html_tag}*${index+1}`)
                input.checked = true

                // change background color to config setting
                let cell = document.getElementById(`${channel.html_tag}_cell`)
                cell.style.backgroundColor = option.selected_color
            }
        }
    })
}

/*
--- CALLS FOR SITE RELOAD ---
*/
// Clears loaded inputs for single site and makes a new API call
// Called by refresh img for each site
async function refresh_site(site_id, site_name) {
    console.log(`Refreshing data for ${site_name}`)
    clear_site_inputs(site_id)

    // on refresh, remove site load error
    remove_load_error_message(site_name)

    // on refresh, remove log messages
    get_burk_data(site_id, site_name).then(channels => {
        if (!channels) {return}
        for (let channel of channels) {
            remove_message_on_update(site_name, channel.title)
        }
        // func in onload section
        update_site_section(site_name, channels)
    })
}


// Clears inputs for specific site
function clear_site_inputs(site_id) {
    const inputs = document.querySelectorAll(`[id*="S${site_id}"]`)
    for (let input of inputs) {
        if (!input.style.backgroundColor == '') {
            input.style.backgroundColor = ''
            }
        if (input.type == 'checkbox' || input.type == 'radio') {
            // breaks loop so as not to clear value from inputs
            input.checked = false;
            continue}
        // resets meter values
        input.value= ''
    }
}

// if load error for site, remove
async function remove_load_error_message(site_name) {
    message = `Data from ${site_name.replace('_', ' ')} did not load automatically. All readings input by user.`
    remove_matched_message(message)
}


// if refresh or manual update clear related messages
async function remove_message_on_update(site_name, channel_title) {
    let identifier = `${site_name.replace('_', ' ')} ${channel_title}`
    remove_matched_message(identifier)
}


function remove_matched_message(identifier) {
    // define messages
    let messages = document.getElementById('messages')

    if (messages.value.match(identifier)) {
        // search messages field for message about id
        all_messages = messages.value.split('\n')
        for (let i = 0; i < all_messages.length; i++) {
            // loop through all message sep by newline
            if (all_messages[i].includes(identifier)) {
                // if matched remove from array
                all_messages.splice(i, 1);
                i--; // Decrement i to match now missing element
            }
        }
        // rejoin array and update message value
        messages.value = all_messages.join('\n')
    }
}

/*
--- MANUAL CHANNEL EDITS ---
*/
function manually_changed(html_tag) {
    // clear background color on change
    let cell = document.getElementById(`${html_tag}_cell`)
    cell.style.backgroundColor = ''

    // get channel info from html tag in format S1*C1
    // where the integer are the ids of the site and channel respectively
    let site_id = `${html_tag.split('*')[0].replace('S', '')}`
    let channel_id = `${html_tag.split('*')[1].replace('C', '')}`

    // get config data for channel
    get_channel_data(site_id, channel_id).then(channel => {
        // NOTE: Channel does not usually include the site name
        site_name = channel.site_name
        remove_message_on_update(site_name, channel.title)
        if (channel.chan_type == 'meter') {
            meter_manually_changed(channel, html_tag)
            }
        else if (channel.chan_type == 'status') {
            status_manually_changed(channel, html_tag)
            }
        add_manually_updated_message(site_name, channel.title)
    })
}


// Calls Flask route to get channel config data
async function get_channel_data(site_id, channel_id) {
    const response = await fetch(`/api/${site_id}/channel/${channel_id}`);
    const channel = await response.json();
    return channel
}


function meter_manually_changed(channel, html_tag) {
    let value = document.getElementById(html_tag).value
    channel.value = value
    channel.html_tag = html_tag
    check_limits(channel.site_name, channel)
}


function status_manually_changed(channel, html_tag) {
    // find selected radio button and assign value to selected value
    let value = get_checked_status_value(html_tag)
    let cell = document.getElementById(`${html_tag}_cell`)

    get_channel_config(channel.id).then(options => {
        for (option of options) {
            if (value == option.selected_value) {
                cell.style.backgroundColor = option.selected_color
            }
        }
    })
}


// returns value output of status radio group
function get_checked_status_value(html_tag) {
    let status_radio = document.getElementsByName(html_tag);
    for (let i = 0; i < status_radio.length; i++) {
        if (status_radio[i].checked) {
            let value = status_radio[i].value
            return value
        }
    }
}


function add_manually_updated_message(site_name, channel_title) {
    // If data didn't load automatically, all channels will be manual. Skip.
    let messages = document.getElementById('messages')
    message = `Data from ${site_name.replace('_', ' ')} did not load automatically.`
    if (messages.value.match(message)) {return}

    // Add message that the channel was manually updated
    let changed = `${site_name.replace('_', ' ')} ${channel_title} manually updated\n`
    add_message(changed)
}


// When approval checkbox checked, change background to green
function approval_background(html_tag) {
    let checkbox = document.getElementById(html_tag)
    let cell = document.getElementById(`${html_tag}_cell`)
    if (checkbox.checked) {
        cell.style.backgroundColor = '#00ff00'  // green
        }
    else {
        cell.style.backgroundColor = ''
    }
}


// Adds message to Notes text area if not already present
function add_message(message) {
    // NOTE: Messages added to doc should end in \n
    let messages = document.getElementById('messages')
    console.log(message)
    if (!messages.value.match(message)) {
        // makes sure message only appears once
        messages.value += message
    }
}


// Open new tab for EAS Form.
function verify_eas(eas_verification) {
    eas_verification.forEach(answer => {
        answer.addEventListener('change', function () {
            if (answer.checked && answer.value == 'YES') {
                window.open('/eas', target='_blank')
            }
        })
    })
}


console.log('Javascript loaded!')
