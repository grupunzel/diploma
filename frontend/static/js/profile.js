const user_data = JSON.parse(document.getElementById('user_data').textContent);
const test_data = JSON.parse(document.getElementById('test_data').textContent);

function render_user_info() {
    const left_block_body = document.getElementsByClassName("left_block_body")[0];
    const first_name_block = document.createElement('div');
    first_name_block.className = 'first_name_block';
    const last_name_block = document.createElement('div');
    last_name_block.className = 'last_name_block';
    const email_block = document.createElement('div');
    email_block.className = 'email_block';

    const first_name_text = document.createElement('p');
    first_name_text.className = 'first_name_text';
    const first_name_user = document.createElement('p');
    first_name_user.className = 'first_name_user';
    first_name_text.innerHTML = 'First name:';
    first_name_user.innerHTML = user_data.first_name;
    const last_name_text = document.createElement('p');
    last_name_text.className = 'last_name_text';
    const last_name_user = document.createElement('p');
    last_name_user.className = 'last_name_user';
    last_name_text.innerHTML = 'Last name:';
    last_name_user.innerHTML = user_data.last_name;
    const email_text = document.createElement('p');
    email_text.className = 'email_text';
    const email_user = document.createElement('p');
    email_user.className = 'email_user';
    email_text.innerHTML = 'Email:';
    email_user.innerHTML = user_data.email;

    const change_button_block = document.createElement('div');
    change_button_block.className = 'change_button_block';
    change_button = document.createElement('button');
    change_button.className = 'change_button';
    change_button.innerHTML = '✎ Change';

    first_name_block.appendChild(first_name_text);
    first_name_block.appendChild(first_name_user);
    last_name_block.appendChild(last_name_text);
    last_name_block.appendChild(last_name_user);
    email_block.appendChild(email_text);
    email_block.appendChild(email_user);
    change_button_block.appendChild(change_button);
    left_block_body.appendChild(first_name_block);
    left_block_body.appendChild(last_name_block);
    left_block_body.appendChild(email_block);
    left_block_body.appendChild(change_button_block);
}

function change_user_info() {
    const left_block_body = document.getElementsByClassName("left_block_body")[0];
    const first_name_block = document.getElementsByClassName('first_name_block')[0];
    const last_name_block = document.getElementsByClassName('last_name_block')[0];
    const email_block = document.getElementsByClassName('email_block')[0];
    const button_block = document.getElementsByClassName('change_button_block')[0];

    const first_name_user = document.getElementsByClassName('first_name_user')[0];
    const last_name_user = document.getElementsByClassName('last_name_user')[0];
    const email_user = document.getElementsByClassName('email_user')[0];
    const change_button = document.getElementsByClassName('change_button')[0];

    first_name_user.style.display = 'none';
    last_name_user.style.display = 'none';
    email_user.style.display = 'none';
    change_button.style.display = 'none';
    button_block.style.display = 'none';

    const first_name_input = document.createElement('input');
    first_name_input.className = 'first_name_input';
    const last_name_input = document.createElement('input');
    last_name_input.className = 'last_name_input';
    const email_input = document.createElement('input');
    email_input.className = 'email_input';
    
    const password_input_block = document.createElement('div');
    password_input_block.className = 'password_input_block';
    left_block_body.appendChild(password_input_block);
    const password_text = document.createElement('p');
    password_text.className = 'password_text';
    password_text.innerHTML = 'Password:';
    const password_input = document.createElement('input');
    password_input.className = 'password_input';
    const save_button_block = document.createElement('div');
    save_button_block.className = 'save_button_block';
    left_block_body.appendChild(save_button_block);
    const save_button = document.createElement('button');
    save_button.className = 'save_button';
    save_button.innerHTML = 'Save ✔';
    const cancel_button = document.createElement('button');
    cancel_button.className = 'cancel_button';
    cancel_button.innerHTML = 'Cancel ✗'

    first_name_block.appendChild(first_name_input);
    last_name_block.appendChild(last_name_input);
    email_block.appendChild(email_input);
    password_input_block.appendChild(password_text);
    password_input_block.appendChild(password_input);
    save_button_block.appendChild(save_button);
    save_button_block.appendChild(cancel_button);

    if (save_button) {
        save_button.addEventListener('click', () => save_user_changes(first_name_input.value, last_name_input.value, email_input.value, password_input.value));
    }

    if (cancel_button) {
        cancel_button.addEventListener('click', () => window.location.href = '/profile')
    }
}

function save_user_changes(first_name, last_name, email, password) {
    const changed_user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    };

    fetch("/change_user_info", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(changed_user_data)
    }).then(response => {
        if (response.ok) {
            window.location.href = '/profile';
        }
    });
}

function tests_info() {
    const right_block_body = document.getElementsByClassName('right_block_body')[0];
    for (const [test_id, test_info] of Object.entries(test_data)) {
        const test_block = document.createElement('div');
        test_block.className = 'test_block';
        const test_show_button = document.createElement('button');
        test_show_button.className = 'test_show_button';
        test_show_button.innerHTML = `▿ Test #${test_id} (${test_info.total_score}/${test_info.max_score})`;
        test_block.appendChild(test_show_button);
        right_block_body.appendChild(test_block);

        if (test_show_button) {
            test_show_button.addEventListener('click', () => show_test_info(test_info));
        }
    }
}

function show_test_info(test_info) {
    
}

document.addEventListener('DOMContentLoaded', () => {
    render_user_info();
    const change_button = document.getElementsByClassName('change_button')[0];
    if (change_button) {
        change_button.addEventListener('click', change_user_info);
    }
    tests_info();
});