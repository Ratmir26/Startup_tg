const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

const WEIGHT_VALUES = { weak: 1, medium: 2, strong: 3 };

let currentIdea = localStorage.getItem('currentIdea') || '';
let argumentsData = JSON.parse(localStorage.getItem('arguments') || '{"pro":[],"con":[]}');
let argumentWeights = JSON.parse(localStorage.getItem('argumentWeights') || '{"pro":{},"con":{}}');
let modalType = 'pro';
let selectedWeight = 'medium';

const ideaInput = document.getElementById('ideaInput');
const charCounter = document.getElementById('charCounter');
const proList = document.getElementById('proList');
const conList = document.getElementById('conList');
const proCount = document.getElementById('proCount');
const conCount = document.getElementById('conCount');
const progressBar = document.getElementById('progressBar');
const progressPercent = document.getElementById('progressPercent');
const scoreDisplay = document.getElementById('scoreDisplay');
const verdictEl = document.getElementById('verdict');
const confidenceText = document.getElementById('confidenceText');
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modalTitle');
const argumentInput = document.getElementById('argumentInput');
const weightSelector = document.getElementById('weightSelector');

ideaInput.value = currentIdea;
updateCharCounter();

ideaInput.addEventListener('input', () => {
    currentIdea = ideaInput.value.slice(0, 150);
    ideaInput.value = currentIdea;
    localStorage.setItem('currentIdea', currentIdea);
    updateCharCounter();
});

function updateCharCounter() {
    charCounter.textContent = `${currentIdea.length}/150`;
}

document.getElementById('addProBtn').addEventListener('click', () => openModal('pro'));
document.getElementById('addConBtn').addEventListener('click', () => openModal('con'));
document.getElementById('modalCancel').addEventListener('click', closeModal);
document.getElementById('modalConfirm').addEventListener('click', addArgument);

argumentInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') addArgument();
});

function openModal(type) {
    modalType = type;
    selectedWeight = 'medium';
    argumentInput.value = '';
    modalTitle.textContent = type === 'pro' ? 'Аргумент ЗА' : 'Аргумент ПРОТИВ';
    modal.classList.remove('hidden');
    argumentInput.focus();
    renderWeightSelector();
}

function closeModal() {
    modal.classList.add('hidden');
}

function renderWeightSelector() {
    weightSelector.innerHTML = '';
    const labels = { weak: '🔴 Слабый', medium: '🟡 Средний', strong: '🟢 Сильный' };
    Object.keys(labels).forEach(w => {
        const btn = document.createElement('button');
        btn.className = `weight-option ${w === selectedWeight ? 'selected' : ''}`;
        btn.textContent = labels[w];
        btn.addEventListener('click', () => {
            selectedWeight = w;
            renderWeightSelector();
        });
        weightSelector.appendChild(btn);
    });
}

function addArgument() {
    const text = argumentInput.value.trim();
    if (text.length < 3) {
        tg.showAlert('Аргумент слишком короткий (мин. 3 символа)');
        return;
    }
    argumentsData[modalType].push(text);
    argumentWeights[modalType][String(argumentsData[modalType].length - 1)] = selectedWeight;
    saveData();
    renderArguments();
    updateProgress();
    closeModal();
    tg.HapticFeedback.notificationOccurred('success');
}

function renderArguments() {
    proList.innerHTML = '';
    conList.innerHTML = '';
    const weightLabels = { weak: 'слабый', medium: 'средний', strong: 'сильный' };

    argumentsData.pro.forEach((text, i) => {
        const w = argumentWeights.pro[String(i)] || 'medium';
        proList.innerHTML += `<div class="argument-card"><span>${text}</span><span class="weight-badge weight-${w}">${weightLabels[w]}</span></div>`;
    });
    argumentsData.con.forEach((text, i) => {
        const w = argumentWeights.con[String(i)] || 'medium';
        conList.innerHTML += `<div class="argument-card"><span>${text}</span><span class="weight-badge weight-${w}">${weightLabels[w]}</span></div>`;
    });
}

function getVerdict() {
    const proW = argumentsData.pro.reduce((s, _, i) => s + (WEIGHT_VALUES[argumentWeights.pro[String(i)]] || 2), 0);
    const conW = argumentsData.con.reduce((s, _, i) => s + (WEIGHT_VALUES[argumentWeights.con[String(i)]] || 2), 0);
    const total = argumentsData.pro.length + argumentsData.con.length;
    const score = proW - conW;
    const totalW = proW + conW;
    const percent = totalW === 0 ? 50 : Math.round((proW / totalW) * 100);

    let verdict, cls, confidence;
    if (total === 0) { verdict = '🤔 Добавь аргументы'; cls = 'neutral'; confidence = 'Нет данных'; }
    else if (total < 3) { verdict = '🤔 Нужно больше данных'; cls = 'neutral'; confidence = 'Мало данных'; }
    else if (proW > conW * 1.5) { verdict = '🚀 Идея перспективная!'; cls = 'positive'; confidence = 'Достаточно данных'; }
    else if (conW > proW * 1.5) { verdict = '❌ Идея слабая'; cls = 'negative'; confidence = 'Достаточно данных'; }
    else if (score > 0) { verdict = '👍 Скорее перспективная'; cls = 'positive'; confidence = total >= 5 ? 'Достаточно данных' : 'Мало данных'; }
    else if (score < 0) { verdict = '👎 Скорее слабая'; cls = 'negative'; confidence = total >= 5 ? 'Достаточно данных' : 'Мало данных'; }
    else { verdict = '⚖️ Равновесие'; cls = 'neutral'; confidence = 'Нужно больше аргументов'; }

    return { verdict, cls, score, confidence, percent, proW, conW };
}

function updateProgress() {
    const { percent, score, confidence, verdict, cls } = getVerdict();
    progressBar.style.width = percent + '%';
    progressBar.textContent = percent + '%';
    progressPercent.textContent = percent + '%';
    proCount.textContent = argumentsData.pro.length;
    conCount.textContent = argumentsData.con.length;
    scoreDisplay.textContent = (score > 0 ? '+' : '') + score;
    verdictEl.textContent = verdict;
    verdictEl.className = cls;
    confidenceText.textContent = `Статус: ${confidence}`;
}

function saveData() {
    localStorage.setItem('arguments', JSON.stringify(argumentsData));
    localStorage.setItem('argumentWeights', JSON.stringify(argumentWeights));
}

document.getElementById('saveBtn').addEventListener('click', () => {
    tg.sendData(JSON.stringify({
        action: 'save_idea',
        idea: currentIdea,
        arguments: argumentsData,
        weights: argumentWeights
    }));
    tg.close();
});

document.getElementById('shareBtn').addEventListener('click', () => {
    const { verdict, score, percent } = getVerdict();
    const text = `🧠 Валидация: "${currentIdea}"\n${verdict}\nScore: ${score > 0 ? '+' : ''}${score} | ${percent}%\n\nПроверь и свою идею!`;
    tg.switchInlineQuery(text, ['users']);
});

renderArguments();
updateProgress();
