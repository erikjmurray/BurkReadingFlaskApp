/* ----- Date Form Query -----
Creates a Start Date/End Date query from user input based on specified url

Given html with a button in a div like so:

<div id="insert_date_form_here" class="">
   <button onclick="create_date_form(URL, btn_text); return false;">
        "Initial Btn Text Here"
   </button>
</div>

where the URL is routed such that it ends with /start_date/end_date
and btn_text fills in the submit button of the date query
*/


function create_date_form(url, btn_text) {
    // Creates start date, end date form
    let date_form = `
        <form id="date_form">
          <label for="start_date">Start Date</label>
          <input type="date" id="start_date" name="start_date" required/>
          <label for="end_date">End Date</label>
          <input type="date" id="end_date" name="end_date" required/>
          <button onclick="submit">${btn_text}</button>
        </form>
        `

    div = document.getElementById('insert_date_form_here')
    div.innerHTML = date_form

    init_date_form_event_listener(url)
    }


function init_date_form_event_listener(url) {
    // Creates event listener for date form button
    let submit_form = document.getElementById('date_form');

    submit_form.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent the form from submitting normally

        const start_date = document.getElementById('start_date').value + ' 00:00:00';
        const end_date = document.getElementById('end_date').value + ' 23:59:59';

        let generated_url = `${url}/${start_date}/${end_date}`;
        console.log(generated_url)
        window.location.href = generated_url;
    });
}


