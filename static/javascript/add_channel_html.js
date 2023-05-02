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


// Get document elements
const channel_count = document.getElementById('channel_count');
const channels_form = document.getElementById('channels');
const add_channel_div = document.getElementById('add_channel')


const channel_selector_html = `
    <fieldset style="margin-top:5px; border-radius: 5px;">
        <dl>
            <dt class="">
                <label class="config_header">Channel Type: </label>
            </dt>
            <dt class="" style="margin-top: 2px;">
                <div class="radio_group">
                    <label>
                        <input type="radio" name="channel_type" value="meter" required>
                        Meter
                    </label>
                    <label>
                        <input type="radio" name="channel_type" value="status">
                        Status
                    </label>
                </div>
                <button class="func_button" onclick="add_channel_html(); return false;">Submit</button>
            </dt>
        </dl>
    </fieldset>
    `


function add_channel_selector_html() {
    // Changes ADD CHANNEL button to a channel type selector
    add_channel_div.innerHTML = channel_selector_html
}


function add_channel_html() {
    // On submit, creates either a meter or status channel form
    const channel_type = document.querySelectorAll('input[name="channel_type"]');
    channel_type.forEach(option => {
        if (option.checked && option.value == 'meter') {
            // increment channel number
            channel_number = parseInt(channel_count.value) + 1;
            channel_count.value = channel_number

            // create meter html
            let channel_div = document.createElement('div');
            let meter_channel = create_meter_channel(`CH${channel_number}`)
            channel_div.innerHTML = meter_channel

            // add to page
            channels_form.appendChild(channel_div)
            }
        else if (option.checked && option.value == 'status') {
            // increment channel number
            channel_number = parseInt(channel_count.value) + 1;
            channel_count.value = channel_number

            // create status html
            let channel_div = document.createElement('div');
            let status_channel = create_status_channel(`CH${channel_number}`)
            channel_div.innerHTML = status_channel

            // add to page
            channels_form.appendChild(channel_div)
        }
    })

    // Clears Meter/Status selector and default to ADD CHANNEL
    add_channel_div.innerHTML = `
        <button class="func_button" onclick="add_channel_selector_html(); return false;">Add Channel</button>
        `
}


// On each channel add minimize/maximize content buttons
function minimize_channel_data(channel_id) {
    content = document.getElementById(`${channel_id}_content`)
    header = document.getElementById(`${channel_id}_header`)
    title = document.getElementById(`${channel_id}_title`)
    content.style = 'display: none;'

    if (title.value) {  header.innerHTML = `${channel_id}. ${title.value}`  }

    hide_content_button = document.getElementById(`${channel_id}_hide_content`)
    hide_content_button.src = '/static/img/plus_sign.png'
    hide_content_button.alt = '+'
    hide_content_button.setAttribute('onclick', `maximize_channel_data('${channel_id}'); return false;`)
}


function maximize_channel_data(channel_id) {
    content = document.getElementById(`${channel_id}_content`)
    content.style = ''

    hide_content_button = document.getElementById(`${channel_id}_hide_content`)
    hide_content_button.src = '/static/img/minus_sign.png'
    hide_content_button.alt = '-'
    hide_content_button.setAttribute('onclick', `minimize_channel_data('${channel_id}'); return false;`)
}


// Create html for a meter channel input
function create_meter_channel(id) {
    meter_channel = `
    <fieldset>
      <dl>
        <div class="channel_header">
            <label id='${id}_header'>${id}. Meter</label>
            <img class="hide_content_button" id="${id}_hide_content"
            onclick="minimize_channel_data('${id}'); return false;" src='/static/img/minus_sign.png' alt='-'>
            <input type="hidden" id="${id}_chan_type" name="${id}_chan_type" value='meter'>
        </div>
        <dt class="config_content" id='${id}_content'>
            <label for='${id}_title'>Title</label>
            <input type="text" id='${id}_title' name='${id}_title' required placeholder='Channel Name'>
            <label for="${id}_burk_channel">Burk Channel Number</label>
            <input type="number" id="${id}_burk_channel" name="${id}_burk_channel" required placeholder="0">

            <label for="${id}_nominal">Nominal Output</label>
            <input type="number" step="any" id="${id}_nominal_output" name="${id}_nominal_output" required placeholder="0">
        <h4 style="margin:0;">Limits</h4>
        <div class="option_box">
        `

        // Add limit html
        meter_channel += create_limit_html(id, 'Upper')
        meter_channel += create_limit_html(id, 'Lower')

        meter_channel += `
        </div>
          <div class="config_content">
            <label style="" for="${id}_units">Units: </label>
            <select style="" id="${id}_units" name="${id}_units" required>
        `
        meter_channel += add_unit_options()
        meter_channel += `
            </select>
        </dt>
      </dl>
    </fieldset>
    </div>
    `

    return meter_channel
}


// create limit html
function create_limit_html(id, limit) {
    if (limit == 'Upper') {
        message = 'Color above upper limit'
    } else {
        message = 'Color below lower limit'
    }
    limit_html = `
        <label for="${id}_${limit.toLowerCase()}_limit">${limit} Limit</label>
        <input id="${id}_${limit.toLowerCase()}_limit" name="${id}_${limit.toLowerCase()}_limit"
               type="number" step="any" placeholder="0" required>

        <label>
        ${message}
        <select style="" id="${id}_${limit.toLowerCase()}_lim_color" name="${id}_${limit.toLowerCase()}_lim_color"
                onchange="change_bg_color('${id}_${limit.toLowerCase()}_lim_color')" required>
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
function create_status_channel(id) {
    // Create status option html. Default to 2
    options = create_option_content(id, 1) + create_option_content(id, 2)

    status_channel = `
        <fieldset>
          <dl>
            <div class="channel_header">
                <label id='${id}_header'>${id}. Status</label>
                <img class="hide_content_button" id="${id}_hide_content"
                onclick="minimize_channel_data('${id}'); return false;" src='/static/img/minus_sign.png' alt='-'>
                <input type="hidden" id="${id}_chan_type" name="${id}_chan_type" value='status'>
                <input type="hidden" id="${id}_opt_count" name="${id}_opt_count" value=2>
            </div>
            <dt id='${id}_content' class="config_content" style="">
                <label for='${id}_title'>Title</label>
                <input type="text" id='${id}_title' name='${id}_title' required placeholder="Channel Name">
                <div id="${id}_options">${options}</div>
                <button class="func_button" onclick="add_next_option('${id}'); return false;">Add Option</button>
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
        <h4 style="text-decoration: underline; margin:0;">Option ${opt_num}</h4>

        <label for="${id}_burk_channel_${opt_num}">Burk Channel Number</label>
        <input type="number" placeholder="0"
               id="${id}_burk_channel_${opt_num}" name="${id}_burk_channel_${opt_num}">

        <label>Option Name</label>
        <input type="text" placeholder="Text When Selected"
               id="${id}_selected_value_${opt_num}" name="${id}_selected_value_${opt_num}">

        <label>
        Selected State
        </label>
        <div class="radio_group option_radio_group">
            <label style="margin-right:25px;">
                <input type="radio" name="${id}_selected_state_${opt_num}" value=true required>
                On
            </label>
            <label>
                <input type="radio" name="${id}_selected_state_${opt_num}" value=false>
                Off
            </label>
        </div>

        <label for="${id}_selected_color_${opt_num}">
            Background Color When Selected
        </label>

        <select style="" id="${id}_selected_color_${opt_num}" name="${id}_selected_color_${opt_num}"
                onchange="change_bg_color('${id}_selected_color_${opt_num}')" required>
        `
        option_content += add_color_picker()
        option_content += `
        </select>
    </div>
    `
    return option_content
}


function add_next_option(id) {
    // get and increment option counter
    next_num = parseFloat(document.getElementById(`${id}_opt_count`).value) + 1
    document.getElementById(`${id}_opt_count`).value = next_num

    // create option content
    option_div = document.createElement('div')
    next_option = create_option_content(id, next_num)
    option_div.innerHTML = next_option

    // insert option content to html
    target_div = document.getElementById(`${id}_options`)
    target_div.appendChild(option_div)
}


// on color select, change background color to match selection
function change_bg_color(id) {
    color_selector = document.getElementById(id)
    color = color_selector.value
    color_selector.style.backgroundColor = color
}

