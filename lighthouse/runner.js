/**
 * Lighthouse Runner Script
 * 
 * Runs a Google Lighthouse audit against a provided URL using headless Chrome.
 * Outputs the results as JSON to standard output.
 * 
 * Usage:
 *   node lighthouse/runner.js <URL>
 * 
 * Example:
 *   node lighthouse/runner.js https://example.com
 */

import * as chromeLauncher from 'chrome-launcher';
import lighthouse from 'lighthouse';

async function runLighthouseAudit(targetUrl) {
  // Validate that a URL was supplied
  if (!targetUrl) {
    console.error(JSON.stringify({
      success: false,
      error: 'No target URL provided. Usage: node lighthouse/runner.js <URL>'
    }));
    process.exit(1);
  }

  let chromeInstance = null;

  try {
    // 1. Launch headless Chrome securely
    chromeInstance = await chromeLauncher.launch({
      chromeFlags: [
        '--headless=new',
        '--no-sandbox',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '--disable-extensions'
      ],
      logLevel: 'silent'
    });

    // 2. Configure Lighthouse options
    const options = {
      logLevel: 'error',
      output: 'json',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      port: chromeInstance.port,
      formFactor: 'desktop',
      screenEmulation: {
        mobile: false,
        width: 1350,
        height: 940,
        deviceScaleFactor: 1,
        disabled: false
      },
      throttling: {
        rttMs: 40,
        throughputKbps: 10240,
        cpuSlowdownMultiplier: 1,
        requestLatencyMs: 0,
        downloadThroughputKbps: 0,
        uploadThroughputKbps: 0
      }
    };

    // 3. Execute Lighthouse audit
    const runnerResult = await lighthouse(targetUrl, options);
    const lhr = runnerResult.lhr;

    // Check if the page failed to load (DNS error, connection refused, or chrome-error page)
    if (lhr.runtimeError || (lhr.finalDisplayedUrl && lhr.finalDisplayedUrl.startsWith('chrome-error://'))) {
      const errMsg = lhr.runtimeError?.message || 'Unable to audit this website. The website may be unavailable or may block automated access.';
      console.error(JSON.stringify({
        success: false,
        error: errMsg
      }));
      process.exit(1);
    }

    // 4. Extract Category Scores (scaled to 0 - 100)
    const scores = {
      performance: Math.round((lhr.categories.performance?.score ?? 0) * 100),
      accessibility: Math.round((lhr.categories.accessibility?.score ?? 0) * 100),
      best_practices: Math.round((lhr.categories['best-practices']?.score ?? 0) * 100),
      seo: Math.round((lhr.categories.seo?.score ?? 0) * 100)
    };

    // 5. Extract significant diagnostic & opportunity audits
    // Focus on audits with low scores (< 1) or measurable savings
    const rawAudits = lhr.audits || {};
    const extractedAudits = [];

    // Prioritized audit IDs for web performance & quality
    const priorityAuditIds = [
      'render-blocking-resources',
      'uses-optimized-images',
      'modern-image-formats',
      'uses-responsive-images',
      'total-byte-weight',
      'offscreen-images',
      'unminified-css',
      'unminified-javascript',
      'unused-css-rules',
      'unused-javascript',
      'efficient-animated-content',
      'uses-text-compression',
      'redirects',
      'uses-rel-preconnect',
      'server-response-time',
      'largest-contentful-paint',
      'first-contentful-paint',
      'cumulative-layout-shift',
      'total-blocking-time',
      'color-contrast',
      'image-alt',
      'document-title',
      'meta-description',
      'is-crawlable',
      'link-text',
      'viewport'
    ];

    for (const auditId of priorityAuditIds) {
      const audit = rawAudits[auditId];
      if (audit) {
        const score = audit.score;
        // Keep audits that failed, need improvement (score < 1), or have displayValues
        if (score !== null && score !== undefined && score < 0.9) {
          extractedAudits.push({
            id: audit.id,
            title: audit.title,
            description: audit.description,
            score: score,
            displayValue: audit.displayValue || null
          });
        }
      }
    }

    // Also include any other failed audits if priority list didn't catch many
    if (extractedAudits.length < 5) {
      for (const [id, audit] of Object.entries(rawAudits)) {
        if (!priorityAuditIds.includes(id) && audit.score !== null && audit.score < 0.8 && audit.title) {
          extractedAudits.push({
            id: audit.id,
            title: audit.title,
            description: audit.description,
            score: audit.score,
            displayValue: audit.displayValue || null
          });
          if (extractedAudits.length >= 10) break;
        }
      }
    }

    // 6. Format and output result JSON
    const output = {
      success: true,
      url: lhr.finalDisplayedUrl || targetUrl,
      fetchTime: lhr.fetchTime,
      scores: scores,
      audits: extractedAudits.slice(0, 15)
    };

    console.log(JSON.stringify(output, null, 2));

  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: error.message || 'Lighthouse audit execution failed.'
    }));
    process.exit(1);
  } finally {
    // Ensure Chrome is closed cleanly
    if (chromeInstance) {
      try {
        await chromeInstance.kill();
      } catch (killErr) {
        // Ignore kill errors
      }
    }
  }
}

// Read target URL from CLI arguments
const targetUrl = process.argv[2];
runLighthouseAudit(targetUrl);
