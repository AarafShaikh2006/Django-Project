// ====== Lesson Content ======
const lessons = {
    stock_basics: "The stock market is where companies raise funds and investors trade shares. It helps companies grow and investors earn returns.",
    ipo_dividends: "IPO (Initial Public Offering) is when a company goes public. Dividends are profits shared with shareholders.",
    fundamental_analysis: "Fundamental analysis involves evaluating company financials, revenue, profit, and key ratios before investing.",
    technical_analysis: "Technical analysis studies price trends, charts, and indicators to predict future price movements.",
    market_orders: "Market orders execute immediately at the current price, while limit orders execute only at a specified price.",
    ratios: "PE, EPS, ROE, and other ratios help evaluate company performance and stock value.",
    risk_portfolio: "Diversification reduces risk. Portfolio management balances returns and risk according to goals.",
    indicators_charts: "RSI, MACD, and moving averages are technical indicators used to interpret charts."
};

// ====== Quizzes ======
const quizzes = {
    stock_basics: [
        {q:"What is the stock market?", options:["Place to buy products","Place to trade shares"], answer:1},
        {q:"Who can invest?", options:["Only companies","Anyone registered"], answer:1},
        {q:"Stocks represent?", options:["Debt","Ownership"], answer:1}
    ],
    ipo_dividends: [
        {q:"IPO stands for?", options:["Initial Public Offering","International Price Option"], answer:0},
        {q:"Dividends are?", options:["Profits shared","Company debts"], answer:0},
        {q:"IPO helps a company?", options:["Raise funds","Pay taxes"], answer:0}
    ],
    fundamental_analysis: [
        {q:"EPS stands for?", options:["Earnings per Share","Equity per Stock"], answer:0},
        {q:"Balance sheet shows?", options:["Company finances","Stock prices"], answer:0},
        {q:"Fundamental analysis evaluates?", options:["Company financials","Market rumors"], answer:0}
    ],
    technical_analysis: [
        {q:"Candlestick charts show?", options:["Fundamentals","Price movements"], answer:1},
        {q:"RSI measures?", options:["Trend strength","Market volume"], answer:0},
        {q:"MACD is used for?", options:["Technical signals","Financial audit"], answer:0}
    ],
    market_orders: [
        {q:"Market order executes?", options:["Immediately","At specific price"], answer:0},
        {q:"Limit order executes?", options:["Immediately","At target price"], answer:1}
    ],
    ratios: [
        {q:"PE ratio measures?", options:["Profitability relative to stock price","Dividend payout"], answer:0},
        {q:"ROE indicates?", options:["Return on Equity","Return on Expenses"], answer:0},
        {q:"EPS measures?", options:["Earnings per Share","Equity per Stock"], answer:0}
    ],
    risk_portfolio: [
        {q:"Diversification reduces?", options:["Profit","Investment risk"], answer:1},
        {q:"Portfolio risk depends on?", options:["Asset mix","Market holidays"], answer:0},
        {q:"Risk management goal?", options:["Max returns, minimize risk","Avoid learning"], answer:0}
    ],
    indicators_charts: [
        {q:"RSI is?", options:["Relative Strength Index","Revenue Stock Indicator"], answer:0},
        {q:"MACD helps to?", options:["Identify trend","Audit company"], answer:0},
        {q:"Moving averages show?", options:["Price trends","Fundamentals"], answer:0}
    ]
};

// ====== Global Variables ======
let currentCompleteBtn = null;
let currentTopic = "";
let completed = 0;
const total = document.querySelectorAll(".learn-card").length;

// ====== Open Lesson ======
function openLesson(topic, btn) {
    currentTopic = topic;
    currentCompleteBtn = btn;
    document.getElementById('lessonTitle').innerText = topic.replace('_', ' ');
    document.getElementById('lessonContent').innerText = lessons[topic];
    const modal = document.getElementById('lessonModal');
    modal.style.display = 'flex';
}

// ====== Close Lesson ======
function closeLesson() {
    document.getElementById('lessonModal').style.display = 'none';
}

// ====== Mark Complete & Animate Progress ======
function markComplete(btn){
    if(!btn.classList.contains('done')){
        completed++;
        btn.classList.add('done');
        btn.innerText = "✅ Completed";
        btn.style.background = "#95a5a6";
        btn.style.cursor = "default";
    }
    const percent = Math.round((completed / total) * 100);
    const bar = document.getElementById('progressBar');
    bar.style.width = percent + "%";
    bar.innerText = percent + "%";
    bar.style.transition = "width 0.5s ease";
}

// ====== Quiz Functionality ======
let currentQuiz=[], currentIndex=0, score=0;

function startQuizFromLesson() {
    closeLesson();
    startQuiz(currentTopic, currentCompleteBtn);
}

function startQuiz(topic, btn) {
    currentQuiz = quizzes[topic];
    currentIndex = 0;
    score = 0;
    currentCompleteBtn = btn || currentCompleteBtn;
    showQuizQuestion();
    const modal = document.getElementById('lessonModal');
    modal.style.display = 'flex';
}

function showQuizQuestion() {
    const q = currentQuiz[currentIndex];
    const content = document.getElementById('lessonContent');
    content.innerHTML = `<h4>${currentIndex+1}. ${q.q}</h4>`;
    
    q.options.forEach((opt,i)=>{
        const button = document.createElement('button');
        button.innerText = opt;
        button.className = "quiz-option-btn";
        button.onclick = () => {
            if(i===q.answer) score++;
            currentIndex++;
            if(currentIndex<currentQuiz.length){
                showQuizQuestion();
            } else {
                alert(`🎯 You scored ${score} out of ${currentQuiz.length}`);
                if(score===currentQuiz.length) markComplete(currentCompleteBtn);
                closeLesson();
            }
        };
        content.appendChild(button);
    });
}

// ====== Animate Card Clicks ======
document.querySelectorAll('.learn-card').forEach(card => {
    card.addEventListener('click', () => {
        card.style.transform = 'scale(1.03)';
        setTimeout(() => card.style.transform = 'scale(1)', 200);
    });
});
