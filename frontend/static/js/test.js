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

    document.getElementById('question_text').innerHTML = `${current_index + 1}. ${question.text}`;
    document.getElementById('question_module').innerHTML = `Module: ${question.module}`;
    document.getElementById('question_score').innerHTML = `Score: ${question.score}`;
    const text_input_block = document.getElementById('answer_input_block');
    const file_input_block = document.getElementById('file_answer_input_block');

    const answers_list = document.getElementById('answers_list');
    answers_list.innerHTML = '';

    if (question.answers && question.answers.length > 0) {
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
        else{
            for (let i = 0; i < question.answers.length; i++) {
                const answer_div = document.createElement('p');
                answer_div.className = 'question_info';
                answer_div.textContent = question.answers[i];
                answers_list.appendChild(answer_div);
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

function save_current_answer() {
    const question = questions[current_index];
    let answer = '';
    const status_div = document.getElementById('answer_status');

    if (question.type === 'file_question') {
        const file_input = document.getElementById('file_answer_input');
        if (file_input.files.length > 0) {
            answer = file_input.files[0].name;
        }
    }
    else {
        answer = document.getElementById('answer_input').value;
    }
    
    saved_answers[question.id] = answer;

    status_div.innerHTML = 'Saved';
    status_div.style.color = 'green';

    update_question_status(question.id, answer !== '');
    update_progress();

    setTimeout(() => {
        if (status_div.innerHTML === 'Saved') {
            status_div.innerHTML = '';
        }
    }, 2000);
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
}

function next_question() {
    if (current_index < questions.length - 1) {
        save_current_answer();
        current_index++;
        render_current_question();
    }
}

function previous_question() {
    if (current_index > 0) {
        save_current_answer();
        current_index--;
        render_current_question();
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
        if (confirm(`You answered only ${answer_count} questions from ${total}. Are you sure you want to finish?`)) {
            submit_answers();
        }
    }
    else {
        submit_answers();
    }
}

function submit_answers() {
    alert('Test is completed! Your answers have been saved.');

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

function setup_event_listeners() {
    const previous_button = document.getElementById('previous_button');
    const next_button = document.getElementById('next_button');
    const finish_button = document.getElementById('finish_button');
    const answer_input = document.getElementById('answer_input');
    const file_input = document.getElementById('file_answer_input');

    previous_button.onclick = previous_question;
    next_button.onclick = next_question;

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