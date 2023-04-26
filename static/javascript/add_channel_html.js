/*
Script to add form input to "Add Site" page dependent on whether site is AM or FM
May also be referenced on "Update Site" page
*/

// ----- SETUP GLOBAL VARIABLES -----

// API call to get predetermined colors
async function get_colors() {
    const response = await fetch('/api/colors')
    const colors_data = await response.json()
    colors = Array.from(colors_data)
}

// API call to get predetermined units
async function get_units() {
    const response = await fetch('/api/units')
    const unit_data = await response.json()
    units = Array.from(unit_data)
}

// Define global variables
let colors;
let units;

get_colors();
get_units();

let pilot_data = {'html_tag': 'pilot', 'type': 'status', 'title': 'Pilot'}


// Get document elements
const site_type = document.querySelectorAll('input[name="site_type"]');
const channels_form = document.querySelector('#channels_form');


function insert_html_on_type_change() {
    // Listens for change of site_type radio button
    // Adds HTML based on dictionaries defined in JS
    site_type.forEach(option => {
        option.addEventListener('change', function () {
            if (option.checked && option.value == 'fm') {
                get_fm_channels().then((fm_channels) => {
                    add_channels(fm_channels);
                    add_pilot_option()
                })
            }
            else if (option.checked && option.value == 'am') {
                get_am_channels().then((am_channels) => {
                    add_channels(am_channels);
                })
            }
        })
    })
}


async function get_fm_channels() {
    // Calls API route for FM channel data
    const response = await fetch('/api/fm_setup_channels');
    const channels = await response.json();
    return Array.from(channels);
}


async function get_am_channels() {
    // Calls API route for AM channel data
    const response = await fetch('/api/am_setup_channels');
    const channels = await response.json();
    return Array.from(channels);
}


function add_channels(channels) {
    // clear HTML before adding anything new
    clear_channels_form()

    channels.forEach(channel => {
        let id = channel.html_tag;
        if (channel.type === 'meter') {
            // Add meter HTML to inner HTML of id="channel_form" as defined in document
            meter_channel = create_meter_channel(id, channel)
            channels_form.innerHTML += meter_channel
        }
        else if (channel.type === 'status') {
            // Add status HTML to inner HTML of id="channel_form" as defined in document
            status_channel = create_status_channel(id, channel)
            channels_form.innerHTML += status_channel
        }
    })
}


// clears added HTML of div w/ id="channel_form" as defined in document
function clear_channels_form() {
    channels_form.innerHTML = ''
}


// Create html for a meter channel input
function create_meter_channel(id, channel) {
    meter_channel = `
    <fieldset>
      <dl>
        <dt class="config_header"">
            <label>${channel.title}</label>
            <div style="display: none;">
                <input type="text" id="${id}_id" name="${id}_id" value="${id}">
                <input type="text" id="${id}_type" name="${id}_type" value="${channel.type}">
                <input type="text" id="${id}_title" name="${id}_title" value="${channel.title}">
            </div>
        </dt>
        <dt class="config_content">
            <label for="${id}_num">Channel Number</label><br>
            <input type="number" id="${id}_num" name="${id}_num" required>

            <label for="${id}_nominal">Nominal Output</label><br>
            <input type="number" step="any" id="${id}_nominal" name="${id}_nominal" value="0">
        <h4 style="margin:0;">Limits</h4>
        <div class="option_box">
        `

        // Add limit html
        meter_channel += create_limit_html(id, 'upper')
        meter_channel += create_limit_html(id, 'lower')

        meter_channel += `
        </div>
          <div class="config_content">
            <label style="" for="${id}_units">Units: </label>
            <select style="" id="${id}_units" name="${id}_units" required>
        `
        meter_channel += add_unit_options()
        meter_channel += `
            </select>
          </div>
        </dt>
      </dl>
    </fieldset>
    `
    return meter_channel
}


// create limit html
function create_limit_html(id, limit) {
    if (limit == 'upper') {
        message = 'Color above upper limit'
    } else {
        message = 'Color below lower limit'
    }
    limit_html = `
        <label for="${id}_${limit}">${limit.toUpperCase()} LIMIT</label><br>
        <input type="number" step="any" id="${id}_${limit}" name="${id}_${limit}" value="0">

        <label>
        ${message}
        <select style="" id="${id}_${limit}_color" name="${id}_${limit}_color"
                onchange="change_bg_color('${id}_${limit}_color')" required>
    `
    limit_html += add_color_picker()
    limit_html += `
        </select>
        </label>
    `
    return limit_html
}


// create html of color options from colors
function add_color_picker() {
    color_options = `<option></option>`
    colors.forEach(color => {
        color_options += `
            <option style="background-color: ${color.hex}" value="${color.hex}">${color.name}</option>
        `
    })
    return color_options
}


// create html of unit options from units
function add_unit_options() {
    unit_options = `<option></option>`
    units.forEach(unit => {
        unit_options += `
            <option value="${unit}">${unit}</option>
        `
    })
    return unit_options
}


// Create html from a status channel input
function create_status_channel(id, channel) {
    // Create status option html. Default to 2
    options = create_option_content(id, 1) + create_option_content(id, 2)

    status_channel = `
        <div style="display: none;">
            <input type="number" id="${id}_opt_count" name="${id}_opt_count" value=2>
        </div>
        <fieldset>
          <dl>
            <dt class="">
                <label class="config_header" for="${id}">${channel.title} </label>
                <div style="display: none;">
                    <input type="text" id="${id}_id" name="${id}_id" value="${id}">
                    <input type="text" id="${id}_type" name="${id}_type" value="${channel.type}">
                    <input type="text" id="${id}_title" name="${id}_title" value="${channel.title}">
                </div>
            </dt>
            <div id="${id}_options">${options}</div>
            <dt>
            <button onclick="add_next_option('${id}'); return false;">Add Option</button>
            </dt>
          </dl>
        </fieldset>
        `
    return status_channel
}

// Creates an option for status channel
function create_option_content(id, opt_num) {
    option_content = `
    <div class="option_box" id="${id}_option_${opt_num}">
        <dt class="config_content">
            <h4 style="text-decoration: underline; margin:0;">Option ${opt_num}</h4>

            <label>Channel</label>
            <input type="number" id="${id}_num_${opt_num}" name="${id}_num_${opt_num}" placeholder="Channel Number">

            <label>Name</label>
            <input type="text" id="${id}_name_${opt_num}" name="${id}_name_${opt_num}" placeholder="Channel Name">

            <label style="text-decoration: underline; padding-bottom:5px;">
            Selected State
            </label>
            <div class="radio_group" style="flex-direction: row; padding-bottom:2px;">
                <label style="margin-right:25px;">
                    <input type="radio" name="${id}_state_${opt_num}" value=true required>
                    On
                </label>
                <label>
                    <input type="radio" name="${id}_state_${opt_num}" value=false>
                    Off
                </label>
            </div>

            <label>
            Status Color
            <select style="" id="${id}_color_${opt_num}" name="${id}_color_${opt_num}"
                    onchange="change_bg_color('${id}_color_${opt_num}')" required>
        `
        option_content += add_color_picker()
        option_content += `
            </select>
            </label>
        </dt>
    </div>
    `
    return option_content
}


function add_next_option(id) {
    // get and increment option counter
    next_num = parseFloat(document.getElementById(`${id}_opt_count`).value) + 1
    document.getElementById(`${id}_opt_count`).value = next_num

    // create option content
    next_option = create_option_content(id, next_num)

    // insert option content to html
    option_div = document.getElementById(`${id}_options`)
    option_div.innerHTML += next_option
}


// on color select, change background color to match selection
function change_bg_color(id) {
    color_select = document.getElementById(id)
    color = color_select.value
    color_select.style.backgroundColor = color
}


// Adds button that adds Pilot status to site
function add_pilot_option() {
    channels_form.innerHTML += `
    <fieldset>
        <dt class="config_content">
          <button onclick="add_pilot_channel(); return false;">Add Pilot?</button>
        </dt>
    </fieldset>`
}


// Inserts an extra status channel for Pilot data
function add_pilot_channel() {
    let id = pilot_data.id
    channels_form.innerHTML += create_status_channel(id, pilot_data)
}


//// On Nominal Input value change, make limits +5/-10 %
//// Currently disabled. Previously added to onchange of Nominal Value in meter
//function auto_adjust_limits(id) {
//    nominal_output = parseFloat(document.getElementById(`${id}_nominal`).value)
//
//    // calc values
//    upper_limit = (nominal_output + (nominal_output * 0.05)).toFixed(2)
//    lower_limit = (nominal_output - (nominal_output * 0.1)).toFixed(2)
//
//    // remove string if x.00
//    upper_limit = upper_limit.replace(/(\.[0-9]*[1-9])0+$|\.0*$/, '$1')
//    lower_limit = lower_limit.replace(/(\.[0-9]*[1-9])0+$|\.0*$/, '$1')
//
//    // insert into proper values
//    document.getElementById(`${id}_upper`).value = upper_limit
//    document.getElementById(`${id}_lower`).value = lower_limit
//}

