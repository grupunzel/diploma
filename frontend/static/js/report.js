const report_data = JSON.parse(document.getElementById('report_data').textContent);

function render_report() {
    if (Object.keys(report_data).length <= 0) {
        document.getElementById("total").innerHTML = 'No report data available.';
        return;
    }

    render_total_analys();
    render_each_topic();
    render_recomendations();
}

function render_total_analys() {
    const total_analys = document.getElementById('total');
    const overall = document.createElement('p');
    overall.className = 'overall';
    overall.innerHTML = report_data.total_analys;
    total_analys.appendChild(overall);
}

function render_each_topic() {
    const analys_topic = document.getElementById('analys_topic');
    const topics_array = Object.entries(report_data.topics);
    const topics_count = topics_array.length;

    let topics_html = '';

    if (topics_count === 1) {
        topics_html = `
            <div class="topics_grid_single">
                ${render_topic_card(topics_array[0][0], topics_array[0][1])}
            </div>
        `;
    }
    else {
        const mid_point = Math.ceil(topics_count / 2);
        const left_column = topics_array.slice(0, mid_point);
        const right_column = topics_array.slice(mid_point);

        topics_html = `
            <div class="topics_grid_multiple">
                <div class="column_left">
                    ${left_column.map(([topic, analys]) => render_topic_card(topic, analys)).join('')}
                </div>
                <div class="column_right">
                    ${right_column.map(([topic, analys]) => render_topic_card(topic, analys)).join('')}
                </div>
            </div>
        `;
    }

    analys_topic.innerHTML = topics_html;
}

function render_topic_card(topic, analys) {
    return `
        <div class="topic_card">
            <div class="topic_header">
                <h3 id="topic_name">${topic}</h3>
                <hr id="horizontal_hr">
            </div>
            <div>
                <p class="topic_content">${analys}</p>
            </div>
        </div>
    `;
}

function render_recomendations() {
    recomendations = report_data.recomendations;
    const recomendations_block = document.getElementById('recomendations');
    const recomendations_report = document.createElement('p');
    recomendations_report.className = 'recomendations_block';
    recomendations_report.innerHTML = `${recomendations}`;
    recomendations_block.appendChild(recomendations_report);
}

function download_as_pdf() {
    const element = document.querySelector('.body');
    const download_button = document.querySelector('.download_container');

    const animated_elements = document.querySelectorAll('.head, .report_container, .column_left, .column_right, .recomendations_block, .recomendations_header_container');
    const original_animations = [];

    animated_elements.forEach((el, index) => {
        original_animations[index] = el.style.animation;
        el.style.animation = 'none';
    });

    let button_display = download_button.style.display;
    download_button.style.display = 'none';

    const opt = {
        margin: [10, 10, 10, 10],
        filename: `test_report_${new Date().toISOString().slice(0, 19)}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(element).save().then(() => {
        animated_elements.forEach((el, index) => {
            el.style.animation = original_animations[index];
        });
        download_button.style.display = button_display;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    render_report();
    const download_button = document.getElementById('download_button');
    if (download_button) {
        download_button.addEventListener('click', download_as_pdf);
    }
});