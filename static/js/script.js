/**
 * Web Lighthouse Performance Monitor - Frontend Logic
 * 
 * Manages form submission, client-side URL validation, loading state,
 * API communication, and dynamic rendering of Lighthouse scores and recommendations.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const auditForm = document.getElementById('auditForm');
  const urlInput = document.getElementById('urlInput');
  const submitBtn = document.getElementById('submitBtn');
  const errorBanner = document.getElementById('errorBanner');
  const errorMessage = document.getElementById('errorMessage');
  const loadingSection = document.getElementById('loadingSection');
  const resultsSection = document.getElementById('resultsSection');
  const sampleChips = document.querySelectorAll('.sample-chip');

  // Results DOM Elements
  const resultUrl = document.getElementById('resultUrl');
  const summaryCard = document.getElementById('summaryCard');
  const summaryBadge = document.getElementById('summaryBadge');
  const summaryMessage = document.getElementById('summaryMessage');
  const recsCountBadge = document.getElementById('recsCountBadge');
  const recommendationsList = document.getElementById('recommendationsList');

  // Category Score Elements
  const categories = {
    performance: {
      card: document.getElementById('cardPerformance'),
      number: document.getElementById('scorePerformance'),
      progress: document.getElementById('progressPerformance')
    },
    accessibility: {
      card: document.getElementById('cardAccessibility'),
      number: document.getElementById('scoreAccessibility'),
      progress: document.getElementById('progressAccessibility')
    },
    bestPractices: {
      card: document.getElementById('cardBestPractices'),
      number: document.getElementById('scoreBestPractices'),
      progress: document.getElementById('progressBestPractices')
    },
    seo: {
      card: document.getElementById('cardSeo'),
      number: document.getElementById('scoreSeo'),
      progress: document.getElementById('progressSeo')
    }
  };

  // Attach click handlers to sample chips
  sampleChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const sampleUrl = chip.getAttribute('data-url');
      if (sampleUrl) {
        urlInput.value = sampleUrl;
        clearError();
        urlInput.focus();
      }
    });
  });

  // Handle Form Submission
  auditForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError();

    const rawUrl = urlInput.value.trim();

    // 1. Client-side URL Validation
    if (!rawUrl) {
      showError('Please enter a website URL to audit.');
      urlInput.focus();
      return;
    }

    if (!rawUrl.startsWith('http://') && !rawUrl.startsWith('https://')) {
      showError('Please enter a valid URL beginning with http:// or https://');
      urlInput.focus();
      return;
    }

    // 2. Set UI to Loading State
    setLoadingState(true);
    resultsSection.style.display = 'none';

    try {
      // 3. Make API request to Flask backend
      const response = await fetch('/audit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: rawUrl })
      });

      const data = await response.json();

      // 4. Handle HTTP errors
      if (!response.ok || !data.success) {
        const errText = data.error || 'Unable to audit this website. The website may be unavailable or may block automated access.';
        showError(errText);
        setLoadingState(false);
        return;
      }

      // 5. Render Results
      renderResults(data);
      setLoadingState(false);

      // Smooth scroll to results
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
      console.error('Audit request error:', err);
      showError('Failed to connect to the audit service. Please verify that the server is running and try again.');
      setLoadingState(false);
    }
  });

  /**
   * Updates UI to show or hide the loading state
   */
  function setLoadingState(isLoading) {
    if (isLoading) {
      submitBtn.disabled = true;
      submitBtn.classList.add('loading');
      submitBtn.querySelector('.btn-text').textContent = 'Auditing Site...';
      loadingSection.style.display = 'block';
    } else {
      submitBtn.disabled = false;
      submitBtn.classList.remove('loading');
      submitBtn.querySelector('.btn-text').textContent = 'Run Lighthouse Audit';
      loadingSection.style.display = 'none';
    }
  }

  /**
   * Displays an error banner with friendly text
   */
  function showError(msg) {
    errorMessage.textContent = msg;
    errorBanner.style.display = 'flex';
  }

  /**
   * Clears the error banner
   */
  function clearError() {
    errorMessage.textContent = '';
    errorBanner.style.display = 'none';
  }

  /**
   * Renders the complete audit results payload into the UI
   */
  function renderResults(data) {
    // 1. Render Audited URL
    resultUrl.textContent = data.url;

    // 2. Render Overall Summary Card
    const summary = data.summary || { status: 'Audit Complete', tier: 'average', message: '' };
    summaryBadge.textContent = summary.status;
    summaryMessage.textContent = summary.message;

    // Remove existing tier classes
    summaryCard.className = 'card summary-card';
    summaryCard.classList.add(`tier-${summary.tier}`);

    summaryBadge.className = 'tier-badge';
    summaryBadge.classList.add(`badge-${summary.tier}`);

    // 3. Render Scores and Progress Bars
    const scores = data.scores || {
      performance: data.performance || 0,
      accessibility: data.accessibility || 0,
      best_practices: data.best_practices || 0,
      seo: data.seo || 0
    };

    renderScoreCard(categories.performance, scores.performance);
    renderScoreCard(categories.accessibility, scores.accessibility);
    renderScoreCard(categories.bestPractices, scores.best_practices);
    renderScoreCard(categories.seo, scores.seo);

    // 4. Render Fix Recommendations
    const recs = data.recommendations || [];
    recsCountBadge.textContent = `${recs.length} ${recs.length === 1 ? 'issue' : 'issues'} identified`;

    recommendationsList.innerHTML = '';

    if (recs.length === 0) {
      recommendationsList.innerHTML = `
        <div class="rec-item">
          <div class="rec-title">No Critical Issues Detected</div>
          <div class="rec-detail-block rec-why">Your website passed all primary performance and accessibility audits!</div>
        </div>
      `;
    } else {
      recs.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'rec-item';

        const savingsBadgeHtml = rec.display_value
          ? `<span class="rec-savings-badge">${escapeHtml(rec.display_value)}</span>`
          : '';

        item.innerHTML = `
          <div class="rec-title-row">
            <h3 class="rec-title">${escapeHtml(rec.title)}</h3>
            ${savingsBadgeHtml}
          </div>
          <div class="rec-detail-block">
            <strong class="rec-problem">Problem:</strong> ${escapeHtml(rec.problem)}
          </div>
          <div class="rec-detail-block">
            <strong class="rec-why">Why it matters:</strong> ${escapeHtml(rec.why_it_matters)}
          </div>
          <div class="rec-detail-block rec-fix">
            <strong>Recommended fix:</strong> ${escapeHtml(rec.recommended_fix)}
          </div>
        `;
        recommendationsList.appendChild(item);
      });
    }

    resultsSection.style.display = 'block';
  }

  /**
   * Helper to format an individual category score card
   */
  function renderScoreCard(catObj, score) {
    const num = Math.min(100, Math.max(0, Math.round(score)));
    catObj.number.textContent = num;

    // Reset score card tier classes
    catObj.card.classList.remove('score-tier-good', 'score-tier-average', 'score-tier-poor');

    if (num >= 90) {
      catObj.card.classList.add('score-tier-good');
    } else if (num >= 50) {
      catObj.card.classList.add('score-tier-average');
    } else {
      catObj.card.classList.add('score-tier-poor');
    }

    // Trigger width transition smoothly
    setTimeout(() => {
      catObj.progress.style.width = `${num}%`;
    }, 50);
  }

  /**
   * Simple HTML escaper to prevent XSS in dynamic rendering
   */
  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
});
