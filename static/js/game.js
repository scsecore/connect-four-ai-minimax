/**
 * Connect Four AI — Game Client
 * Handles board rendering, API calls, animations, and sound effects.
 */

// ─── Constants ────────────────────────────────────────────────────────────────
const ROWS = 6;
const COLS = 7;
const EMPTY = 0;
const PLAYER = 1;
const AI = 2;
const API_BASE = '';

// ─── State ────────────────────────────────────────────────────────────────────
let board = [];
let gameOver = false;
let isPlayerTurn = true;
let isAnimating = false;

// ─── DOM Elements ─────────────────────────────────────────────────────────────
const boardEl = document.getElementById('game-board');
const statusText = document.getElementById('status-text');
const statusIndicator = document.querySelector('.status-indicator');
const gameStatusEl = document.getElementById('game-status');
const difficultySelect = document.getElementById('difficulty-select');
const restartBtn = document.getElementById('restart-btn');
const playerScoreEl = document.getElementById('player-score');
const aiScoreEl = document.getElementById('ai-score');
const drawScoreEl = document.getElementById('draw-score');
const aiThinkingEl = document.getElementById('ai-thinking');
const colIndicators = document.querySelectorAll('.col-indicator');

// ─── Audio Context (Web Audio API) ───────────────────────────────────────────
let audioCtx = null;

function getAudioCtx() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioCtx;
}

function playTone(freq, duration, type = 'sine', volume = 0.15) {
    try {
        const ctx = getAudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, ctx.currentTime);
        gain.gain.setValueAtTime(volume, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + duration);
    } catch (e) {
        // Silently fail if audio not supported
    }
}

function playDropSound() {
    playTone(220, 0.15, 'sine', 0.12);
    setTimeout(() => playTone(330, 0.1, 'sine', 0.08), 80);
}

function playWinSound() {
    const notes = [523, 659, 784, 1047];
    notes.forEach((note, i) => {
        setTimeout(() => playTone(note, 0.3, 'sine', 0.12), i * 120);
    });
}

function playLoseSound() {
    playTone(300, 0.3, 'sawtooth', 0.08);
    setTimeout(() => playTone(200, 0.5, 'sawtooth', 0.06), 200);
}

function playDrawSound() {
    playTone(400, 0.2, 'triangle', 0.1);
    setTimeout(() => playTone(400, 0.2, 'triangle', 0.1), 250);
}

// ─── Board Rendering ──────────────────────────────────────────────────────────
function createBoard() {
    boardEl.innerHTML = '';
    for (let row = 0; row < ROWS; row++) {
        for (let col = 0; col < COLS; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.id = `cell-${row}-${col}`;
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.addEventListener('click', () => handleCellClick(col));
            boardEl.appendChild(cell);
        }
    }
}

function renderBoard(boardData, winningCells = []) {
    board = boardData;
    const winSet = new Set(winningCells.map(([r, c]) => `${r}-${c}`));

    for (let row = 0; row < ROWS; row++) {
        for (let col = 0; col < COLS; col++) {
            const cell = document.getElementById(`cell-${row}-${col}`);
            const val = boardData[row][col];

            // Remove existing discs
            const existingDisc = cell.querySelector('.disc');

            if (val !== EMPTY && !existingDisc) {
                const disc = document.createElement('div');
                disc.className = `disc ${val === PLAYER ? 'red' : 'yellow'}`;
                cell.appendChild(disc);
                // Trigger animation
                requestAnimationFrame(() => disc.classList.add('dropped'));
            }

            // Mark winning cells
            if (winSet.has(`${row}-${col}`)) {
                cell.classList.add('winning');
            } else {
                cell.classList.remove('winning');
            }
        }
    }
}

function animateDisc(row, col, piece) {
    return new Promise(resolve => {
        const cell = document.getElementById(`cell-${row}-${col}`);
        const disc = document.createElement('div');
        disc.className = `disc ${piece === PLAYER ? 'red' : 'yellow'}`;
        cell.appendChild(disc);
        playDropSound();
        requestAnimationFrame(() => {
            disc.classList.add('dropped');
            setTimeout(resolve, 500);
        });
    });
}

// ─── Status Updates ───────────────────────────────────────────────────────────
function setStatus(text, type = 'player') {
    statusText.textContent = text;
    statusIndicator.className = 'status-indicator';
    gameStatusEl.className = 'game-status glass-panel';

    switch (type) {
        case 'player':
            statusIndicator.classList.add('player-turn');
            break;
        case 'ai':
            statusIndicator.classList.add('ai-turn');
            break;
        case 'winner-player':
            statusIndicator.classList.add('player-turn', 'game-over');
            gameStatusEl.classList.add('winner-player');
            break;
        case 'winner-ai':
            statusIndicator.classList.add('ai-turn', 'game-over');
            gameStatusEl.classList.add('winner-ai');
            break;
        case 'draw':
            statusIndicator.classList.add('game-over');
            gameStatusEl.classList.add('draw-game');
            break;
    }
}

function updateScores(scores) {
    const animateScore = (el, newVal) => {
        const oldVal = el.textContent;
        el.textContent = newVal;
        if (oldVal !== String(newVal)) {
            el.classList.remove('pop');
            void el.offsetWidth; // Force reflow
            el.classList.add('pop');
        }
    };
    animateScore(playerScoreEl, scores.player);
    animateScore(aiScoreEl, scores.ai);
    animateScore(drawScoreEl, scores.draws);
}

function setInteractive(enabled) {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        if (enabled) {
            cell.classList.remove('disabled');
        } else {
            cell.classList.add('disabled');
        }
    });

    colIndicators.forEach(ind => {
        if (enabled) {
            ind.classList.remove('disabled');
        } else {
            ind.classList.add('disabled');
        }
    });
}

function showAiThinking(show) {
    if (show) {
        aiThinkingEl.classList.remove('hidden');
    } else {
        aiThinkingEl.classList.add('hidden');
    }
}

// ─── API Calls ────────────────────────────────────────────────────────────────
async function apiNewGame(difficulty) {
    const res = await fetch(`${API_BASE}/api/new-game`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ difficulty }),
    });
    return res.json();
}

async function apiMakeMove(column) {
    const res = await fetch(`${API_BASE}/api/make-move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ column }),
    });
    return res.json();
}

// ─── Game Actions ─────────────────────────────────────────────────────────────
async function startNewGame() {
    const difficulty = difficultySelect.value;
    const data = await apiNewGame(difficulty);

    gameOver = false;
    isPlayerTurn = true;
    isAnimating = false;

    // Clear board DOM
    createBoard();
    renderBoard(data.game.board);
    updateScores(data.scores);
    setStatus("Your turn — drop a red disc!", 'player');
    setInteractive(true);
    showAiThinking(false);
}

async function handleCellClick(col) {
    if (gameOver || !isPlayerTurn || isAnimating) return;

    isAnimating = true;
    isPlayerTurn = false;
    setInteractive(false);

    try {
        const data = await apiMakeMove(col);

        if (data.status === 'error') {
            setStatus(data.message, 'player');
            isPlayerTurn = true;
            isAnimating = false;
            setInteractive(true);
            return;
        }

        // Animate player disc
        if (data.player_move) {
            await animateDisc(data.player_move.row, data.player_move.col, PLAYER);
        }

        // Check if player won
        if (data.game.game_over && data.game.winner === PLAYER) {
            renderBoard(data.game.board, data.game.winning_cells);
            updateScores(data.scores);
            setStatus("🎉 You win! Amazing!", 'winner-player');
            gameOver = true;
            isAnimating = false;
            playWinSound();
            return;
        }

        // Check for draw after player move
        if (data.game.game_over && data.game.is_draw) {
            renderBoard(data.game.board);
            updateScores(data.scores);
            setStatus("🤝 It's a draw!", 'draw');
            gameOver = true;
            isAnimating = false;
            playDrawSound();
            return;
        }

        // AI turn
        if (data.ai_move) {
            setStatus("AI is thinking…", 'ai');
            showAiThinking(true);

            // Small delay so the user sees the "thinking" state
            await new Promise(r => setTimeout(r, 400));
            showAiThinking(false);

            await animateDisc(data.ai_move.row, data.ai_move.col, AI);

            // Check if AI won
            if (data.game.game_over && data.game.winner === AI) {
                renderBoard(data.game.board, data.game.winning_cells);
                updateScores(data.scores);
                setStatus("😤 AI wins! Try again!", 'winner-ai');
                gameOver = true;
                isAnimating = false;
                playLoseSound();
                return;
            }

            // Check for draw after AI move
            if (data.game.game_over && data.game.is_draw) {
                renderBoard(data.game.board);
                updateScores(data.scores);
                setStatus("🤝 It's a draw!", 'draw');
                gameOver = true;
                isAnimating = false;
                playDrawSound();
                return;
            }
        }

        updateScores(data.scores);
        setStatus("Your turn — drop a red disc!", 'player');
        isPlayerTurn = true;
        isAnimating = false;
        setInteractive(true);

    } catch (err) {
        console.error('Move error:', err);
        setStatus("Connection error — try again", 'player');
        isPlayerTurn = true;
        isAnimating = false;
        setInteractive(true);
    }
}

// ─── Event Listeners ──────────────────────────────────────────────────────────
restartBtn.addEventListener('click', startNewGame);

difficultySelect.addEventListener('change', () => {
    startNewGame();
});

// Column hover indicators
colIndicators.forEach(ind => {
    ind.addEventListener('click', () => {
        const col = parseInt(ind.dataset.col);
        handleCellClick(col);
    });
});

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    createBoard();
    startNewGame();
});
