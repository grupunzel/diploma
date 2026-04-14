const questions_data = JSON.parse(document.getElementById('questions_data').textContent);
const questions = Object.entries(questions_data).map(([id, data]) => ({
    id: parseInt(id),
    text: data.question_text,
    module: data.module,
    score: data.score,
    type: data.type,
    answers: data.answers || []
}));

let saved_answers = {};
let current_index = 0;
let autosave_timeout = null;
let is_loading_hint = false;

document.addEventListener('DOMContentLoaded', () => {
    render_quick_nav();
    render_current_question();
    update_progress();
    setup_event_listeners();
});

function render_quick_nav() {
    const container = document.getElementById('quick_navigation');
    container.innerHTML = '';

    for (let i = 0; i < questions.length; i++) {
        const question = questions[i];
        const button = document.createElement('button');
        button.className = 'all_buttons';
        button.textContent = i + 1;
        button.dataset.index = i;

        if (i === current_index) {
            button.classList.add('active');
        }

        if (saved_answers[question.id]) {
            button.classList.add('answered');
        }

        button.onclick = () => go_to_question(i);
        container.appendChild(button);
    }
}

function render_current_question() {
    const question = questions[current_index];

    document.getElementById('question_index').innerHTML = `${window.translations.question_index} ${current_index + 1}`;
    document.getElementById('question_text').innerHTML = `${question.text}`;
    document.getElementById('question_module').innerHTML = `${window.translations.question_module}: ${question.module}`;
    document.getElementById('question_score').innerHTML = `${question.score} ${window.translations.question_score}`;
    const text_input_block = document.getElementById('answer_input_block');
    const file_input_block = document.getElementById('file_answer_input_block');

    const answers_list = document.getElementById('answers_list');
    answers_list.innerHTML = '';

    if (question.answers && (question.answers != "open question, no answer choice")) {
        if (question.type === 'multiple_choice') {
            const saved_value = saved_answers[question.id] || '';
            const selected_answers = saved_value ? saved_value.split(', ') : [];

            const choices_container = document.createElement('div');
            choices_container.className = 'multiple_choice_container';

            for (let i = 0; i < question.answers.length; i++) {
                const answer_text = question.answers[i];
                const choice_card = document.createElement('label');
                choice_card.className = 'choice_card';

                const checkbox = document.createElement('input');
                checkbox.className = 'checkbox_input';
                checkbox.type = 'checkbox';
                checkbox.value = answer_text;
                checkbox.checked = selected_answers.includes(answer_text);
                checkbox.addEventListener('change', () => {
                    save_current_answer();
                });

                const span = document.createElement('span');
                span.className = 'checkbox_new';
                span.textContent = answer_text;

                choice_card.appendChild(checkbox);
                choice_card.appendChild(span);
                choices_container.appendChild(choice_card);
            }
            answers_list.appendChild(choices_container);

            if (text_input_block) {
                text_input_block.style.display = 'none';
            }
            if (file_input_block) {
                file_input_block.style.disply = 'none';
            }
        }
    }

    if (text_input_block && file_input_block) {
       if (question.type === 'file_question') {
            text_input_block.style.display = 'none';
            file_input_block.style.display = 'block';
        }
        else if (question.type === 'multiple_choice') {
            text_input_block.style.display = 'none';
            file_input_block.style.display = 'none';
        }
        else {
            text_input_block.style.display = 'block';
            file_input_block.style.display = 'none';

            const answer_input = document.getElementById('answer_input');
            answer_input.value = saved_answers[question.id] || '';
        } 
    }

    update_active_nav();
    update_nav_buttons();

    const card = document.querySelector('.question_card');
    card.style.animation = 'none';
    setTimeout(() => {
        card.style.animation = 'fadeIn 0.3s ease';
    }, 10);
}

function update_active_nav() {
    const all_buttons = document.querySelectorAll('.all_buttons');
    for (let i = 0; i < all_buttons.length; i++) {
        if (i === current_index) {
            all_buttons[i].classList.add('active');
        }
        else {
            all_buttons[i].classList.remove('active');
        }
    }
}

function update_nav_buttons() {
    const previous_button = document.getElementById('previous_button');
    const next_button = document.getElementById('next_button');
    const finish_block = document.getElementById('finish_block');

    previous_button.disabled = (current_index === 0);
    next_button.disabled = (current_index === questions.length - 1);

    if (current_index === questions.length - 1) {
        finish_block.style.display = 'block';
    }
    else {
        finish_block.style.display = 'none';
    }
}

async function save_current_answer() {
    const question = questions[current_index];
    let answer = '';
    const status_div = document.getElementById('answer_status')
    const file_status = document.getElementById('file_status');

    if (question.type === 'multiple_choice') {
        const checkboxes = document.querySelectorAll('.choice_card input[type="checkbox"]:checked');
        const selected_answers = Array.from(checkboxes).map(cb => cb.value);
        answer = selected_answers.join('; ');
    }
    else if (question.type === 'file_question') {
        const file_input = document.getElementById('file_answer_input');

        if (file_input && file_input.files.length > 0) {
            answer = file_input.files[0].name;
            file_status.innerHTML = '';
            file_status.style.display = 'block';
            const success_text = document.createElement('p');
            success_text.className = `success_text`;
            success_text.style.display = 'block';
            success_text.innerHTML = '⏳ ${window.translations.uploading_text}';
            file_status.appendChild(success_text);

            const result = await upload_file(question.id, file_input.files[0]);
            file_status.innerHTML = '';

            if (result[0]) {
                success_text.innerHTML = `${window.translations.success_text_1} "${file_input.files[0].name}" ${window.translations.success_text_2}`;
                answer = result[1];
            }
            else {
                answer = '';
                success_text.innerHTML = `${result[1]}`;
            }
            file_status.appendChild(success_text);
        }
        else {
            answer = '';
            if (file_status) {
                file_status.style.display = 'none';
                file_status.innerHTML = '';
            }
        }
    }
    else {
        answer = document.getElementById('answer_input').value;
    }

    saved_answers[question.id] = answer;

    if (status_div) {
        status_div.innerHTML = 'Saved';
        status_div.style.color = 'green';
    }

    update_question_status(question.id, answer !== '');
    update_progress();

    setTimeout(() => {
        if (status_div && status_div.innerHTML === 'Saved') {
            status_div.innerHTML = '';
        }
    }, 2000);
}

async function upload_file(question_id, file) {
    const form_data = new FormData();
    form_data.append('file', file);
    form_data.append('question_id', question_id);

    try {
        const response = await fetch('/upload_file_answer', {
            method: 'POST',
            body: form_data
        });

        const result = await response.json();

        if (result.success) {
            return [true, `${result.parsed_text}`];
        }
        else {
            return [false, `${result.error}`];
        }
    }
    catch (error) {
        console.error('Upload error:', error);
        return [false, "Network error. Please try again."];
    }
}

function update_question_status(question_id, is_answered) {
    const question_index = questions.findIndex(q => q.id === question_id);
    if (question_index !== -1) {
        const nav_button = document.querySelectorAll('.all_buttons')[question_index];
        if (is_answered) {
            nav_button.classList.add('answered');
        }
        else {
            nav_button.classList.remove('answered');
        }
    }
}

function update_progress() {
    let answered_count = 0;
    for (let key in saved_answers) {
        if (saved_answers[key] && saved_answers[key].trim()) {
            answered_count++;
        }
    }
}

function go_to_question(index) {
    if (index === current_index) {
        return;
    }

    save_current_answer();
    current_index = index;
    render_current_question();
    hide_hint();
}

function next_question() {
    if (current_index < questions.length - 1) {
        save_current_answer();
        current_index++;
        render_current_question();
        hide_hint();
    }
}

function previous_question() {
    if (current_index > 0) {
        save_current_answer();
        current_index--;
        render_current_question();
        hide_hint();
    }
}

function finish_test() {
    save_current_answer();
    let answer_count = 0;
    for (let key in saved_answers) {
        if (saved_answers[key] && saved_answers[key].trim()) {
            answer_count++;
        }
    }

    const total = questions.length;
    if (answer_count < total) {
        if (confirm(`${window.translations.you_answered_only} ${answer_count} ${window.translations.questions_from} ${total}. ${window.translations.are_you_sure}`)) {
            submit_answers();
        }
    }
    else {
        submit_answers();
    }
}

function submit_answers() {
    alert(`${window.translations.alert_text}`);

    fetch('/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(saved_answers)
    }).then(response => {
        if (response.ok) {
            window.location.href = '/report';
        }
    });
}

async function help_with_task() {
    const question = questions[current_index];
    const help_content = document.getElementById('help_content');

    if (is_loading_hint) {
        return;
    }

    help_content.style.display = 'block';
    help_content.innerHTML = `⏳ ${window.translations.help_content}`;

    is_loading_hint = true;

    try {
        const response = await fetch('/get_hint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question_text: question.text
            })
        });

        const data = await response.json();

        help_content.innerHTML = `
            <div class="help_header">
                <span>${window.translations.hint}:</span>
            </div>
            <p class="help_text">${data.hint}</p>`;
    }
    catch (error) {
        help_text.innerHTML = 'Failed to get a hint for this question.';
    }
    finally {
        is_loading_hint = false;
    }
}

function hide_hint() {
    const help_content = document.getElementById('help_content');
    help_content.style.display = 'none';
}

function setup_event_listeners() {
    const previous_button = document.getElementById('previous_button');
    const next_button = document.getElementById('next_button');
    const help_button = document.getElementById('help_button');
    const finish_button = document.getElementById('finish_button');
    const answer_input = document.getElementById('answer_input');
    const file_input = document.getElementById('file_answer_input');
    const help_content = document.getElementById('help_content');

    previous_button.onclick = previous_question;
    next_button.onclick = next_question;
    help_button.onclick = help_with_task;

    if (help_content) {
        help_content.style.display = 'none';
        help_content.innerHTML = '';
    }

    if (finish_button) {
        finish_button.onclick = finish_test;
    }

    if (answer_input) {
        answer_input.addEventListener('input', () => {
            clearTimeout(autosave_timeout);
            autosave_timeout = setTimeout(() => {
                save_current_answer();
            }, 1000);
        });

        answer_input.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
            
                const start = this.selectionStart;
                const end = this.selectionEnd;
                const tabChar = '    ';
                this.value = this.value.substring(0, start) + tabChar + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + tabChar.length;
            }
        });
    }

    if (file_input) {
        file_input.addEventListener('change', () => {
            save_current_answer();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'ArrowLeft') {
            e.preventDefault();
            previous_question();
        }
        else if (e.ctrlKey && e.key === 'ArrowRight') {
            e.preventDefault();
            next_question();
        }
    });
}