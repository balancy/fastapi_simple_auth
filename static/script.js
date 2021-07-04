document.addEventListener("DOMContentLoaded", function(){
    let btn = document.querySelector('input[type=submit]');
    btn.addEventListener('click', async function(event){
        event.preventDefault();
        // let username = document.querySelector('input[name=username]').value;
        // let password = document.querySelector('input[name=password]').value;
        let response = await fetch('/login', {
            method: 'POST',
            body: new FormData(document.querySelector('form')),
        });
        let response_json = await response.json();
        if(response_json.success){
            let body = document.querySelector('body');
            body.innerHTML = response_json.message;
        }
    })
})