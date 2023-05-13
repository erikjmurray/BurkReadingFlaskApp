/*
Script to add form input to "Add Site" page dependent on whether site is AM or FM
May also be referenced on "Update Site" page
*/

// ----- SETUP GLOBAL VARIABLES -----

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
        // increment channel count, create new id
        if (option.checked && option.value == 'meter') {
            channel_id = create_channel_id()
            create_meter_channel(channel_id).then(channel_html => {
                create_channel_div(channel_html, channel_id)
            })
        }
        else if (option.checked && option.value == 'status') {
            channel_id = create_channel_id()
            create_status_channel(channel_id).then(channel_html => {
                create_channel_div(channel_html, channel_id)
            })
        }
    })

    // Clears Meter/Status selector and defaults to ADD CHANNEL
    add_channel_div.innerHTML = `
        <button class="func_button" onclick="add_channel_selector_html(); return false;">Add Channel</button>
        `
}


function create_channel_id() {
    channel_number = parseInt(channel_count.value) + 1;
    channel_count.value = channel_number
    return `new_${channel_number}`
}


function create_channel_div(channel_html, channel_id) {
    // create new div and add channel to form
    let channel_div = document.createElement('div');
    channel_div.setAttribute('id', channel_id)
    channel_div.innerHTML = channel_html
    channels_form.appendChild(channel_div)
    return
}


// API Calls to Flask Routes that generates HTML based on Jinja2 Macros
function create_meter_channel(channel_id) {
  return new Promise(async (resolve, reject) => {
    try {
      const response = await fetch(`/api/generate_meter_channel/${channel_id}`);
      if (!response.ok) {
        throw new Error('Network response not OK');
      }
      const html = await response.text();
      resolve(html);
    } catch (error) {
      console.error('Error:', error);
      reject(error);
    }
  });
}


function create_status_channel(channel_id) {
  return new Promise(async (resolve, reject) => {
    try {
      const response = await fetch(`/api/generate_status_channel/${channel_id}`);
      if (!response.ok) {
        throw new Error('Network response not OK');
      }
      const html = await response.text();
      resolve(html);
    } catch (error) {
      console.error('Error:', error);
      reject(error);
    }
  });
}


function create_option_content(channel_id, opt_num) {
  return new Promise(async (resolve, reject) => {
    try {
      const response = await fetch(`/api/generate_option_content/${channel_id}/${opt_num}`);
      if (!response.ok) {
        throw new Error('Network response not OK');
      }
      const html = await response.text();
      resolve(html);
    } catch (error) {
      console.error('Error:', error);
      reject(error);
    }
  });
}


// On each channel add minimize/maximize content buttons
function minimize_channel_data(channel_id) {
    content = document.getElementById(`${channel_id}_content`)
    header = document.getElementById(`${channel_id}_header`)
    title = document.getElementById(`${channel_id}_title`)
    content.style.display = 'none'

    if (title.value) {  header.innerHTML = `${title.value}`  }

    hide_content_button = document.getElementById(`${channel_id}_hide_content`)
    hide_content_button.src = '/static/img/plus_sign.png'
    hide_content_button.alt = '+'
    hide_content_button.setAttribute('onclick', `maximize_channel_data('${channel_id}'); return false;`)
}


function maximize_channel_data(channel_id) {
    content = document.getElementById(`${channel_id}_content`)
    content.style.display = ''

    hide_content_button = document.getElementById(`${channel_id}_hide_content`)
    hide_content_button.src = '/static/img/minus_sign.png'
    hide_content_button.alt = '-'
    hide_content_button.setAttribute('onclick', `minimize_channel_data('${channel_id}'); return false;`)
}


function add_next_option(id) {
    // get and increment option counter
    next_num = parseFloat(document.getElementById(`${id}_opt_count`).value) + 1
    document.getElementById(`${id}_opt_count`).value = next_num

    // create option content
    option_div = document.createElement('div')
    create_option_content(id, next_num, colors).then(next_option => {
        option_div.innerHTML = next_option

        // insert option content to html
        target_div = document.getElementById(`${id}_options`)
        target_div.appendChild(option_div)
    })
}


// on color select, change background color to match selection
function change_bg_color(id) {
    color_selector = document.getElementById(id)
    color = color_selector.value
    color_selector.style.backgroundColor = color
}


function remove_option_section(html_tag, opt_num) {
    const section_to_delete = document.getElementById(`${html_tag}_option_${opt_num}`);
    const confirmation = confirm('Would you like to remove this option?')

    if (confirmation) {
        opt_count = document.getElementById(`${html_tag}_opt_count`);
        opt_count.value = parseInt(opt_count.value) - 1;
        section_to_delete.remove()
    }
}


function remove_channel_section(html_tag) {
    const section_to_delete = document.getElementById(html_tag);
    const confirmation = confirm('Would you like to remove this section?')

    if (confirmation) {
        channel_count.value = parseInt(channel_count.value) - 1;
        section_to_delete.remove()
    }
}


function add_delete_option_tag(html_tag, opt_num) {
    const section_to_delete = document.getElementById(`${html_tag}_option_${opt_num}`);
    const confirmation = confirm('Would you like to remove this option?')

    if (confirmation) {
        // replace section with hidden input of status option id as delete
   }
}



function add_delete_channel_tag(channel_id) {
    // on delete confirmation in form, add input delete_${channel_id} remove all data from fieldset
    const fieldset_to_replace = document.getElementById(channel_id);

    const confirmation = confirm(`WARNING: Deleting this channel will destroy all associated reading values. Are you sure you want to proceed?`);

    if (confirmation) {
        // create a new input element
        const input_to_add = document.createElement('input');
        input_to_add.type = 'hidden';
        input_to_add.id = `delete_${channel_id}_tag`;
        input_to_add.name = `delete_${channel_id}_tag`;
        input_to_add.value = 'true';

        // replace the fieldset with the new input element
        fieldset_to_replace.parentNode.replaceChild(input_to_add, fieldset_to_replace);
    }
}

