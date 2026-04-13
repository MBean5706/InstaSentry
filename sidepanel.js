const modeButtons = document.querySelectorAll('.mode-option');
const statusText = document.getElementById('statusText');
const continueBtn = document.getElementById('continueBtn');
const backBtn = document.getElementById('backBtn');
const processingBackBtn = document.getElementById('processingBackBtn');
const processingContinueBtn = document.getElementById('processingContinueBtn');
const downloadsContinueBtn = document.getElementById('downloadsContinueBtn');
const downloadsBackBtn = document.getElementById('downloadsBackBtn');
const downloadAllBtn = document.getElementById('downloadAllBtn');
const downloadFilteredBtn = document.getElementById('downloadFilteredBtn');
const profileLoginContinueBtn = document.getElementById('profileLoginContinueBtn');
const profileLoginBackBtn = document.getElementById('profileLoginBackBtn');
const profileSearchBackBtn = document.getElementById('profileSearchBackBtn');
const profileProcessingContinueBtn = document.getElementById('profileProcessingContinueBtn');
const profileProcessingBackBtn = document.getElementById('profileProcessingBackBtn');

const profileLoginStatusRows = document.querySelectorAll('#pageProfileLogin .status-line');
const profileLoginStatusNote = document.querySelector('#pageProfileLogin .status-note');
const profileUsernameInput = document.getElementById('profileUsername');
const profileSearchContinueBtn = document.getElementById('profileSearchContinueBtn');

const postUrlInput = document.getElementById('postUrl');
const commentCountInput = document.getElementById('commentCount');
const keywordsInput = document.getElementById('keywords');
const fullContinueBtn = document.getElementById('fullContinueBtn');

const resultsDownloadAllBtn = document.getElementById('resultsDownloadAllBtn');
const resultsDownloadFilteredBtn = document.getElementById('resultsDownloadFilteredBtn');
const resultsDownloadProfileBtn = document.getElementById('resultsDownloadProfileBtn');
const resultsDownloadWhyBtn = document.getElementById('resultsDownloadWhyBtn');
const resultsProfileOnlyDataBtn = document.getElementById('resultsProfileOnlyDataBtn');
const resultsProfileOnlyWhyBtn = document.getElementById('resultsProfileOnlyWhyBtn');
const restartBtnFull = document.getElementById('restartBtnFull');
const restartBtnProfile = document.getElementById('restartBtnProfile');

const pageModeSelect = document.getElementById('pageModeSelect');
const pageFullAnalysis = document.getElementById('pageFullAnalysis');
const pageProcessing = document.getElementById('pageProcessing');
const pageDownloads = document.getElementById('pageDownloads');
const pageProfileLogin = document.getElementById('pageProfileLogin');
const pageProfileSearch = document.getElementById('pageProfileSearch');
const pageProfileProcessing = document.getElementById('pageProfileProcessing');
const pageResults = document.getElementById('pageResults');

const fullAnalysisForm = document.getElementById('fullAnalysisForm');
const profileSearchForm = document.getElementById('profileSearchForm');

const formStatusText = document.getElementById('formStatusText');
const downloadsStatusText = document.getElementById('downloadsStatusText');
const profileSearchStatusText = document.getElementById('profileSearchStatusText');
const resultsStatusText = document.getElementById('resultsStatusText');

const gaugeTrack = document.getElementById('gaugeTrack');
const gaugeFill = document.getElementById('gaugeFill');
const fullResultsButtons = document.getElementById('fullResultsButtons');
const profileResultsButtons = document.getElementById('profileResultsButtons');

const finalScore = document.getElementById('finalScore');
const scoreLabel = document.getElementById('scoreLabel');

let selectedMode = 'full';
let backendScore = 0;
let loginStatusInterval = null;

/* ---------- PAGE CONTROL ---------- */

function showPage(pageToShow) {
  [pageModeSelect, pageFullAnalysis, pageProcessing, pageDownloads, pageProfileLogin, pageProfileSearch, pageProfileProcessing, pageResults]
    .forEach(page => page.classList.remove('active'));
  pageToShow.classList.add('active');
}

function getScoreLabel(score) {
  if (score <= 25) return 'Very likely automated';
  if (score <= 50) return 'Likely automated';
  if (score <= 70) return 'Uncertain';
  if (score <= 85) return 'Likely human';
  return 'Highly likely human';
}

function showResults() {
  finalScore.textContent = backendScore;
  scoreLabel.textContent = getScoreLabel(backendScore);
  updateGauge(backendScore);

  if (selectedMode === 'full') {
    fullResultsButtons.classList.remove('hidden');
    profileResultsButtons.classList.add('hidden');
  } else {
    fullResultsButtons.classList.add('hidden');
    profileResultsButtons.classList.remove('hidden');
  }

  showPage(pageResults);
}

function disableProfileLoginContinue() {
  profileLoginContinueBtn.disabled = true;
  profileLoginContinueBtn.classList.add('disabled-btn');
}

function enableProfileLoginContinue() {
  profileLoginContinueBtn.disabled = false;
  profileLoginContinueBtn.classList.remove('disabled-btn');
}

function stopLoginStatusPolling() {
  if (loginStatusInterval !== null) {
    clearInterval(loginStatusInterval);
    loginStatusInterval = null;
  }
}

function startLoginStatusPolling() {
  stopLoginStatusPolling();

  loginStatusInterval = setInterval(async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/login-status");
      const data = await response.json();

      if (!data.success) {
        return;
      }

      if (data.logged_in) {
        stopLoginStatusPolling();

        document.querySelectorAll('#pageProfileLogin .status-icon')[1].textContent = "✅";
        profileLoginStatusRows[1].textContent = "Login accepted.";
        profileLoginStatusNote.textContent = "Instagram login confirmed. Continue is now enabled.";

        enableProfileLoginContinue();
      }

    } catch (err) {
      // Keep waiting silently
    }
  }, 2000);
}

function disableProfileSearchContinue() {
  profileSearchContinueBtn.disabled = true;
  profileSearchContinueBtn.classList.add('disabled-btn');
}

function enableProfileSearchContinue() {
  profileSearchContinueBtn.disabled = false;
  profileSearchContinueBtn.classList.remove('disabled-btn');
}

function polarToCartesian(cx, cy, r, angleInDegrees) {
  const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
  return {
    x: cx + (r * Math.cos(angleInRadians)),
    y: cy + (r * Math.sin(angleInRadians))
  };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return ["M", start.x, start.y, "A", r, r, 0, largeArcFlag, 0, end.x, end.y].join(" ");
}

function updateGauge(score) {
  const clampedScore = Math.max(0, Math.min(99, score));
  const percent = clampedScore / 99;
  const startAngle = 270;
  const endAngle = 90;
  const totalSweep = 180;
  const fillEndAngle = startAngle + (totalSweep * percent);

  gaugeTrack.setAttribute('d', describeArc(110, 110, 74, startAngle, endAngle));

  if (percent <= 0.001) {
    gaugeFill.setAttribute('d', '');
    return;
  }

  const safeFillEnd = Math.min(fillEndAngle, 449.999);
  gaugeFill.setAttribute('d', describeArc(110, 110, 74, startAngle, safeFillEnd));
}

function updateProcessingUI(steps) {
  const rows = document.querySelectorAll('#pageProfileProcessing .status-row');

  steps.forEach((step, index) => {
    if (!rows[index]) {
      return;
    }

    const icon = rows[index].querySelector('.status-icon');
    const line = rows[index].querySelector('.status-line');

    if (!icon || !line) {
      return;
    }

    line.textContent = step.name;

    if (step.status === "pending") {
      icon.textContent = "⏳";
      rows[index].classList.remove('done');
      rows[index].classList.add('working');
    } else if (step.status === "in_progress") {
      icon.textContent = "⏳";
      rows[index].classList.remove('done');
      rows[index].classList.add('working');
    } else if (step.status === "complete") {
      icon.textContent = "✅";
      rows[index].classList.remove('working');
      rows[index].classList.add('done');
    } else if (step.status === "failed") {
      icon.textContent = "❌";
      rows[index].classList.remove('done');
      rows[index].classList.remove('working');
    }
  });
}

function resetProcessingUI() {
  const rows = document.querySelectorAll('#pageProfileProcessing .status-row');

  rows.forEach(row => {
    const icon = row.querySelector('.status-icon');

    if (icon) {
      icon.textContent = "⏳";
    }

    row.classList.remove('done');
    row.classList.remove('working');
  });
}

function disableFullContinue() {
  fullContinueBtn.disabled = true;
  fullContinueBtn.classList.add('disabled-btn');
}

function enableFullContinue() {
  fullContinueBtn.disabled = false;
  fullContinueBtn.classList.remove('disabled-btn');
}

function validateFullAnalysisFields() {
  const postUrl = postUrlInput.value.trim();
  const commentCount = commentCountInput.value.trim();
  const keywords = keywordsInput.value.trim();

  disableFullContinue();

  if (fullValidationTimer !== null) {
    clearTimeout(fullValidationTimer);
  }

  if (postUrl === "") {
    formStatusText.textContent = "Enter a valid Instagram post URL.";
    return;
  }

  if (commentCount === "" || !/^\d+$/.test(commentCount)) {
    formStatusText.textContent = "Enter a whole number between 1 and 1000.";
    return;
  }

  const commentNumber = parseInt(commentCount, 10);

  if (commentNumber < 1 || commentNumber > 1000) {
    formStatusText.textContent = "Comment count must be between 1 and 1000.";
    return;
  }

  const validKeywords = keywords
    .split(",")
    .map(k => k.trim())
    .filter(k => k.length >= 2);

  if (validKeywords.length === 0) {
    formStatusText.textContent = "Enter at least one keyword with 2 or more characters.";
    return;
  }

  formStatusText.textContent = "Checking inputs...";

  fullValidationTimer = setTimeout(() => {
    if (!postUrl.includes("instagram.com")) {
      formStatusText.textContent = "Enter a valid Instagram post URL.";
      disableFullContinue();
      return;
    }

    formStatusText.textContent = "Inputs accepted. Continue is ready.";
    enableFullContinue();
  }, 500);
}

function stopFullLoginStatusPolling() {
  if (fullLoginStatusInterval !== null) {
    clearInterval(fullLoginStatusInterval);
    fullLoginStatusInterval = null;
  }
}

function startFullLoginStatusPolling() {
  stopFullLoginStatusPolling();

  fullLoginStatusInterval = setInterval(async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/login-status");
      const data = await response.json();

      if (!data.success) {
        return;
      }

      if (data.logged_in) {
        stopFullLoginStatusPolling();

        const processingRows = document.querySelectorAll('#pageProcessing .status-row .status-icon');
        const processingLines = document.querySelectorAll('#pageProcessing .status-row .status-line');
        const processingNote = document.querySelector('#pageProcessing .status-note');

        if (processingRows.length >= 1 && processingLines.length >= 1) {
          processingRows[0].textContent = "✅";
          processingLines[0].textContent = "Login accepted.";
        }

        if (processingNote) {
          processingNote.textContent = "Instagram login confirmed. Starting post analysis...";
        }

        processingContinueBtn.disabled = true;
        processingContinueBtn.classList.add('disabled-btn');

        setTimeout(() => {
          runFullAnalysisAfterLogin();
        }, 1500);
      }

    } catch (err) {
      // keep waiting silently
    }
  }, 2000);
}

async function runFullAnalysisAfterLogin() {
  processingContinueBtn.disabled = true;
  processingContinueBtn.classList.add('disabled-btn');

  const processingRows = document.querySelectorAll('#pageProcessing .status-row .status-icon');
  const processingLines = document.querySelectorAll('#pageProcessing .status-row .status-line');
  const processingNote = document.querySelector('#pageProcessing .status-note');

  if (processingRows.length >= 4 && processingLines.length >= 4) {
    processingRows[1].textContent = "⏳";
    processingRows[2].textContent = "⏳";
    processingRows[3].textContent = "⏳";

    processingLines[1].textContent = "Collecting comments...";
    processingLines[2].textContent = "Filtering keywords...";
    processingLines[3].textContent = "Preparing files...";
  }

  if (processingNote) {
    processingNote.textContent = "Please wait while InstaSentry completes this step.";
  }

  try {
    const response = await fetch("http://127.0.0.1:5000/full-analysis/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        post_url: pendingPostUrl,
        comment_limit: parseInt(pendingCommentCount),
        keywords: pendingKeywords.split(",").map(k => k.trim())
      })
    });

    const data = await response.json();

    if (!data.success) {
      formStatusText.textContent = data.message || "Full analysis failed.";
      return;
    }

    if (processingRows.length >= 4 && processingLines.length >= 4) {
      processingRows[1].textContent = "✅";
      processingRows[2].textContent = "✅";
      processingRows[3].textContent = "✅";

      processingLines[1].textContent = "Comments collected.";
      processingLines[2].textContent = "Keywords filtered.";
      processingLines[3].textContent = "Files prepared.";
    }

if (processingNote) {
  processingNote.textContent = "Processing complete. Continue is now enabled.";
}

processingContinueBtn.disabled = false;
processingContinueBtn.classList.remove('disabled-btn');

  } catch (err) {
    formStatusText.textContent = "Error connecting to backend.";
  }
}

function downloadWhyReport() {
  chrome.downloads.download({
    url: "http://127.0.0.1:5000/download/why_report",
    saveAs: false
  }, (downloadId) => {
    if (chrome.runtime.lastError) {
      console.error("Download failed:", chrome.runtime.lastError.message);
      alert("Failed to download why report.");
    } else {
      console.log("Why report download started. Download ID:", downloadId);
      resultsStatusText.textContent = "Why report download started.";
    }
  });
}

if (resultsDownloadWhyBtn) {
  resultsDownloadWhyBtn.addEventListener("click", downloadWhyReport);
}

if (resultsProfileOnlyWhyBtn) {
  resultsProfileOnlyWhyBtn.addEventListener("click", downloadWhyReport);
}

/* ---------- MODE SELECT ---------- */

modeButtons.forEach(button => {
  button.addEventListener('click', () => {
    selectedMode = button.dataset.mode;
    modeButtons.forEach(b => b.classList.remove('active'));
    button.classList.add('active');
  });
});

/* ---------- FULL ANALYSIS ---------- */

let pendingPostUrl = "";
let pendingCommentCount = "";
let pendingKeywords = "";
let fullLoginStatusInterval = null;
let fullValidationTimer = null;

fullAnalysisForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  if (fullContinueBtn.disabled) {
    return;
  }

  pendingPostUrl = postUrlInput.value.trim();
  pendingCommentCount = commentCountInput.value.trim();
  pendingKeywords = keywordsInput.value.trim();

  processingContinueBtn.disabled = true;
  processingContinueBtn.classList.add('disabled-btn');

  const processingRows = document.querySelectorAll('#pageProcessing .status-row .status-icon');
  const processingLines = document.querySelectorAll('#pageProcessing .status-row .status-line');
  const processingNote = document.querySelector('#pageProcessing .status-note');

  if (processingRows.length >= 4 && processingLines.length >= 4) {
    processingRows[0].textContent = "⏳";
    processingRows[1].textContent = "⏳";
    processingRows[2].textContent = "⏳";
    processingRows[3].textContent = "⏳";

    processingLines[0].textContent = "Waiting for login...";
    processingLines[1].textContent = "Collecting comments...";
    processingLines[2].textContent = "Filtering keywords...";
    processingLines[3].textContent = "Preparing files...";
  }

  if (processingNote) {
    processingNote.textContent = "Please complete login in the Chrome window that opened. Continue will unlock after login is confirmed.";
  }

  showPage(pageProcessing);

  try {
    const response = await fetch("http://127.0.0.1:5000/start-login", {
      method: "POST"
    });

    const data = await response.json();

    if (!data.success) {
      formStatusText.textContent = data.message || "Failed to start Instagram login.";
      return;
    }

    startFullLoginStatusPolling();

  } catch (err) {
    formStatusText.textContent = "Error connecting to backend.";
  }
});

/* ---------- PROFILE ONLY ---------- */

profileSearchForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  if (profileSearchContinueBtn.disabled) {
    return;
  }

  const username = profileUsernameInput.value.trim();

  profileSearchStatusText.textContent = "Processing...";

  profileProcessingContinueBtn.disabled = true;
  profileProcessingContinueBtn.classList.add('disabled-btn');

  resetProcessingUI();
  startProgressPolling();
  showPage(pageProfileProcessing);

  try {
    const response = await fetch("http://127.0.0.1:5000/profile-analysis/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username: username })
    });

    const data = await response.json();

    const finalProgress = await fetch("http://127.0.0.1:5000/profile-progress");
    const finalData = await finalProgress.json();

    updateProcessingUI(finalData.steps);

    stopProgressPolling();

    if (!data.success) {
      resultsStatusText.textContent = data.message || "Profile analysis failed.";
      return;
    }

    backendScore = data.final_score;

    profileProcessingContinueBtn.disabled = false;
    profileProcessingContinueBtn.classList.remove('disabled-btn');

  } catch (err) {
    stopProgressPolling();
    resultsStatusText.textContent = "Error connecting to backend.";
  }
});

/* ---------- BUTTON NAV ---------- */

continueBtn.addEventListener('click', async () => {
  if (selectedMode === 'full') {
    showPage(pageFullAnalysis);
    return;
  }

  // PROFILE ONLY FLOW
  showPage(pageProfileLogin);

  // RESET LOGIN TEXT
  profileLoginStatusRows[0].textContent = "Instagram login required before searching a profile.";
  profileLoginStatusRows[1].textContent = "Opening Instagram login...";
  profileLoginStatusNote.textContent = "Please complete login in the Chrome window that opened.";

  disableProfileLoginContinue();

  try {
    const response = await fetch("http://127.0.0.1:5000/start-login", {
      method: "POST"
    });

    const data = await response.json();

    if (!data.success) {
      profileLoginStatusRows[1].textContent = "Login window failed to open.";
      profileLoginStatusNote.textContent = data.message || "Failed to start Instagram login.";
      return;
    }

    profileLoginStatusRows[1].textContent = "Waiting for login...";
    profileLoginStatusNote.textContent = "Continue will unlock after login is confirmed.";

    startLoginStatusPolling();

  } catch (err) {
    profileLoginStatusRows[1].textContent = "Error starting login.";
    profileLoginStatusNote.textContent = "Error connecting to backend.";
  }
});

processingContinueBtn.addEventListener('click', () => {
  if (processingContinueBtn.disabled) {
    return;
  }

  const processingLines = document.querySelectorAll('#pageProcessing .status-line');

  if (processingLines.length >= 4 && processingLines[1].textContent === "Comments collected.") {
    showPage(pageDownloads);
    return;
  }

  runFullAnalysisAfterLogin();
});

profileProcessingContinueBtn.addEventListener('click', () => {
  if (profileProcessingContinueBtn.disabled) {
    return;
  }

  showResults();
});

backBtn.addEventListener('click', () => showPage(pageModeSelect));
processingBackBtn.addEventListener('click', () => showPage(pageFullAnalysis));
downloadsBackBtn.addEventListener('click', () => showPage(pageProcessing));

profileLoginBackBtn.addEventListener('click', () => {
  stopLoginStatusPolling();
  showPage(pageModeSelect);
});

profileProcessingBackBtn.addEventListener('click', () => {
  stopProgressPolling();
  showPage(pageProfileSearch);
});

downloadsContinueBtn.addEventListener('click', () => {
  showPage(pageProfileSearch);
});

restartBtnFull.addEventListener('click', () => {
  postUrlInput.value = "";
  commentCountInput.value = "";
  keywordsInput.value = "";

  profileUsernameInput.value = "";

  formStatusText.textContent = "Enter your inputs to begin.";

  disableFullContinue();
  disableProfileSearchContinue();

  showPage(pageFullAnalysis);
});

restartBtnProfile.addEventListener('click', async () => {
  stopLoginStatusPolling();

  try {
    const response = await fetch("http://127.0.0.1:5000/login-status");
    const data = await response.json();

    if (data.success && data.logged_in) {
      profileUsernameInput.value = "";
      profileSearchStatusText.textContent = "Enter a username to continue.";
      disableProfileSearchContinue();
      showPage(pageProfileSearch);
      return;
    }

  } catch (err) {
    // Fallback below
  }

  showPage(pageModeSelect);
});

/* ---------- LOGIN STATUS CHECK ---------- */

profileLoginContinueBtn.addEventListener('click', () => {
  // DO NOTHING if button is disabled
  if (profileLoginContinueBtn.disabled) {
    return;
  }

  // Only runs when login is already confirmed
  showPage(pageProfileSearch);
});

/* ---------- USERNAME VALIDATION CHECK ---------- */

let usernameValidationTimer = null;

postUrlInput.addEventListener('input', validateFullAnalysisFields);
commentCountInput.addEventListener('input', validateFullAnalysisFields);
keywordsInput.addEventListener('input', validateFullAnalysisFields);

profileUsernameInput.addEventListener('input', () => {
  const username = profileUsernameInput.value.trim();

  disableProfileSearchContinue();

  if (usernameValidationTimer !== null) {
    clearTimeout(usernameValidationTimer);
  }

  if (username === "") {
    profileSearchStatusText.textContent = "Enter a username to continue.";
    return;
  }

  profileSearchStatusText.textContent = "Checking username...";

  usernameValidationTimer = setTimeout(async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/validate-username", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username: username })
      });

      const data = await response.json();

      if (!data.success || !data.valid) {
        profileSearchStatusText.textContent = data.message || "Username not found. Please try again.";
        disableProfileSearchContinue();
        return;
      }

      profileSearchStatusText.textContent = data.message || "Username accepted.";
      enableProfileSearchContinue();

    } catch (err) {
      profileSearchStatusText.textContent = "Error connecting to backend.";
      disableProfileSearchContinue();
    }
  }, 500);
});

/* ---------- POLLING FUNCTION ---------- */

let progressInterval = null;

function startProgressPolling() {
  stopProgressPolling();

  progressInterval = setInterval(async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/profile-progress");
      const data = await response.json();

      updateProcessingUI(data.steps);

    } catch (err) {
      console.log("Progress polling error");
    }
  }, 1000);
}

function stopProgressPolling() {
  if (progressInterval !== null) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
}

disableProfileSearchContinue();
disableFullContinue();

processingContinueBtn.disabled = true;
processingContinueBtn.classList.add('disabled-btn');

profileProcessingContinueBtn.disabled = true;
profileProcessingContinueBtn.classList.add('disabled-btn');