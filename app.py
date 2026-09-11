"""
RA Horizon Web LightHouse Performance Monitor - Flask Backend

A beginner-friendly web application backend that accepts URLs, executes
Google Lighthouse audits safely via Node.js subprocess, and returns
categorized scores, performance summaries, and practical fix recommendations.
"""

import json
import os
import subprocess
import urllib.parse
from flask import Flask, jsonify, render_template, request

# Initialize Flask application
app = Flask(__name__)

# Dictionary of beginner-friendly explanations for common Lighthouse audit IDs
RECOMMENDATION_KNOWLEDGE_BASE = {
    'render-blocking-resources': {
        'problem': 'Resources are blocking the first paint of your page.',
        'why_it_matters': 'CSS and JavaScript files that take time to load prevent visitors from seeing any page content immediately.',
        'recommended_fix': 'Deliver critical CSS inline, defer non-critical JavaScript using async or defer attributes, and remove unused styles.'
    },
    'uses-optimized-images': {
        'problem': 'Images are not properly compressed or optimized.',
        'why_it_matters': 'Large image files consume high network bandwidth and make the page feel sluggish, especially on mobile connections.',
        'recommended_fix': 'Compress images before uploading using tools like TinyPNG or Squoosh, and choose appropriate dimensions.'
    },
    'modern-image-formats': {
        'problem': 'Images are served in older formats (JPEG/PNG) rather than next-gen formats.',
        'why_it_matters': 'Modern formats like WebP and AVIF provide better compression than PNG or JPEG without losing visual quality.',
        'recommended_fix': 'Convert existing JPEG/PNG graphics to WebP or AVIF formats using an image converter or automated CDN.'
    },
    'uses-responsive-images': {
        'problem': 'Images are larger than the display area on the user screen.',
        'why_it_matters': 'Serving huge desktop-sized images to small mobile phone screens wastes data and slows down image rendering.',
        'recommended_fix': 'Use the HTML srcset and sizes attributes so the browser automatically downloads the best image size for the device.'
    },
    'total-byte-weight': {
        'problem': 'The page has an excessively large overall network payload.',
        'why_it_matters': 'Heavy web pages require more mobile data and take longer to download, causing visitors to abandon the site.',
        'recommended_fix': 'Minify your code, compress media files, enable caching, and remove unnecessary third-party libraries.'
    },
    'uses-text-compression': {
        'problem': 'Text-based resources (HTML, CSS, JavaScript) are served without compression.',
        'why_it_matters': 'Uncompressed text files take up 60-80% more bandwidth than compressed files.',
        'recommended_fix': 'Enable Gzip or Brotli compression on your web server or reverse proxy (such as Cloudflare or Nginx).'
    },
    'unminified-javascript': {
        'problem': 'JavaScript code contains extra whitespace, comments, and long variable names.',
        'why_it_matters': 'Extra characters increase file sizes and take longer for the browser to download and parse.',
        'recommended_fix': 'Use a build tool (like Vite, Webpack, or Terser) to minify your production JavaScript code.'
    },
    'unminified-css': {
        'problem': 'CSS stylesheets contain unminified formatting and whitespace.',
        'why_it_matters': 'Unminified CSS delays how fast the browser can render page layouts.',
        'recommended_fix': 'Minify your CSS stylesheets using tools like cssnano or clean-css.'
    },
    'unused-javascript': {
        'problem': 'The page downloads JavaScript code that is never executed on this view.',
        'why_it_matters': 'Browsers must download, parse, and compile code even if it is not used, delaying page interactivity.',
        'recommended_fix': 'Implement code-splitting and load scripts dynamically only when needed by specific pages or user actions.'
    },
    'unused-css-rules': {
        'problem': 'The page downloads CSS style rules that do not style any elements on the current page.',
        'why_it_matters': 'Unused CSS blocks rendering and wastes network bandwidth.',
        'recommended_fix': 'Remove dead CSS rules or split stylesheets into page-specific files.'
    },
    'server-response-time': {
        'problem': 'The backend server took too long to return the initial HTML document (high TTFB).',
        'why_it_matters': 'Visitors see a blank screen until the server responds, slowing down the entire page load process.',
        'recommended_fix': 'Optimize database queries, enable server-side caching (e.g. Redis), or use a Content Delivery Network (CDN).'
    },
    'color-contrast': {
        'problem': 'Text does not have sufficient contrast against its background color.',
        'why_it_matters': 'Low contrast makes text difficult or impossible to read for users with vision impairments or in bright sunlight.',
        'recommended_fix': 'Increase the contrast ratio between foreground text and background color to at least 4.5:1.'
    },
    'image-alt': {
        'problem': 'Image elements are missing descriptive alt attributes.',
        'why_it_matters': 'Screen readers rely on alt text to describe visuals to visually impaired users; search engines also use it to understand images.',
        'recommended_fix': 'Add descriptive alt="Brief description" attributes to all informational images.'
    },
    'document-title': {
        'problem': 'The webpage is missing a <title> element.',
        'why_it_matters': 'Screen readers, browser tabs, and search engines depend on titles to identify and rank web pages.',
        'recommended_fix': 'Add a clear, descriptive <title> tag inside the <head> section of your HTML document.'
    },
    'meta-description': {
        'problem': 'The webpage does not have a meta description tag.',
        'why_it_matters': 'Search engines often display the meta description in search results to inform users what the page is about.',
        'recommended_fix': 'Add a <meta name="description" content="..."> tag inside the HTML <head> with a 120-160 character summary.'
    },
    'link-text': {
        'problem': 'Hyperlinks do not have descriptive anchor text (e.g., "click here" or "read more").',
        'why_it_matters': 'Generic links make navigation confusing for screen reader users and hurt search engine optimization.',
        'recommended_fix': 'Use clear, specific link text describing the target destination, such as "Learn more about our pricing".'
    },
    'viewport': {
        'problem': 'The page is missing a mobile viewport configuration tag.',
        'why_it_matters': 'Without a viewport tag, mobile devices render pages at desktop scale, forcing users to zoom and scroll horizontally.',
        'recommended_fix': 'Include <meta name="viewport" content="width=device-width, initial-scale=1"> in the <head> tag.'
    },
    'charset': {
        'problem': 'Character encoding declaration is missing or declared too late in HTML.',
        'why_it_matters': 'Missing charset can cause special characters or emojis to display as broken symbols.',
        'recommended_fix': 'Add <meta charset="UTF-8"> at the very top of your HTML <head> section.'
    }
}


def validate_url(url_string):
    """
    Validates the user-submitted URL for safety and correctness.
    Returns: (is_valid: bool, error_message: str or None, clean_url: str or None)
    """
    if not url_string or not isinstance(url_string, str):
        return False, "Please enter a valid website URL.", None

    clean_url = url_string.strip()

    # Must start with http:// or https://
    if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
        return False, "Please enter a valid URL beginning with http:// or https://", None

    # Check for forbidden control characters or shell injection attempts
    dangerous_characters = [';', '&', '|', '`', '$', '\n', '\r', ' ', '\t', '"', "'", '<', '>']
    for char in dangerous_characters:
        if char in clean_url:
            return False, f"Invalid character detected in URL: '{char}'. Please enter a standard web address.", None

    # Parse using urllib to ensure valid domain structure
    try:
        parsed = urllib.parse.urlparse(clean_url)
        if not parsed.netloc or '.' not in parsed.netloc:
            return False, "The URL appears to be missing a valid domain name (e.g., example.com).", None
    except Exception:
        return False, "The provided web address is malformed. Please enter a valid URL.", None

    return True, None, clean_url


def generate_performance_summary(performance_score):
    """
    Generates a beginner-friendly performance evaluation based on Lighthouse score.
    Simple rules:
      Score >= 90: Excellent
      Score 50-89: Needs improvement
      Score < 50: Poor
    """
    if performance_score >= 90:
        return {
            "status": "Excellent",
            "tier": "good",
            "message": "Your website has an excellent performance score! Page loading is swift, smooth, and delivers a great user experience."
        }
    elif performance_score >= 50:
        return {
            "status": "Needs Improvement",
            "tier": "average",
            "message": "Your website has a moderate performance score. It functions well, but there are several clear opportunities to improve loading speed."
        }
    else:
        return {
            "status": "Poor",
            "tier": "poor",
            "message": "Your website has a poor performance score. Critical speed bottlenecks were detected that can frustrate visitors and hurt search rankings."
        }


def build_recommendations(raw_audits):
    """
    Transforms raw Lighthouse audit issues into beginner-friendly, actionable recommendations.
    Returns a list of 5 to 10 curated recommendations.
    """
    recommendations = []

    for audit in raw_audits:
        audit_id = audit.get('id', '')
        title = audit.get('title', '')
        score = audit.get('score', 1)

        # Skip audits that passed completely (score of 1)
        if score is not None and score >= 0.9:
            continue

        # Look up friendly explanation in knowledge base
        kb_entry = RECOMMENDATION_KNOWLEDGE_BASE.get(audit_id)
        if kb_entry:
            problem_text = kb_entry['problem']
            why_text = kb_entry['why_it_matters']
            fix_text = kb_entry['recommended_fix']
        else:
            # Fallback for other audits
            problem_text = title
            raw_desc = audit.get('description', 'Detected by Lighthouse audit.')
            # Clean markdown links from raw description if present
            clean_desc = raw_desc.split('[')[0].strip() if '[' in raw_desc else raw_desc
            why_text = clean_desc or "Resolving this audit improves site speed, accessibility, or best practices."
            fix_text = f"Review the {title} guidelines and adjust your page code accordingly."

        recommendations.append({
            "id": audit_id,
            "title": title,
            "problem": problem_text,
            "why_it_matters": why_text,
            "recommended_fix": fix_text,
            "display_value": audit.get('displayValue')
        })

        # Limit to 10 recommendations to keep the report beginner-friendly
        if len(recommendations) >= 10:
            break

    # If website had almost no issues, provide an encouraging note
    if not recommendations:
        recommendations.append({
            "id": "all-good",
            "title": "No Critical Issues Detected",
            "problem": "Lighthouse did not detect any major performance or accessibility flaws.",
            "why_it_matters": "A clean audit means your website adheres to high web quality standards.",
            "recommended_fix": "Continue monitoring your site periodically as you add new features or content.",
            "display_value": "All audits passed"
        })

    return recommendations


@app.route('/')
def home():
    """Renders the main web interface."""
    return render_template('index.html')


@app.route('/audit', methods=['POST'])
def run_audit():
    """
    API endpoint that accepts a target URL and initiates a Google Lighthouse audit.
    """
    # 1. Parse JSON input
    data = request.get_json(silent=True)
    if not data or 'url' not in data:
        return jsonify({
            "success": False,
            "error": "Request must be JSON containing a 'url' field."
        }), 400

    target_url = data.get('url', '')

    # 2. Validate URL
    is_valid, error_msg, validated_url = validate_url(target_url)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": error_msg
        }), 400

    # 3. Locate Node.js Lighthouse runner
    base_dir = os.path.dirname(os.path.abspath(__file__))
    runner_script = os.path.join(base_dir, 'lighthouse', 'runner.js')

    if not os.path.exists(runner_script):
        return jsonify({
            "success": False,
            "error": "Lighthouse runner script was not found on the server."
        }), 500

    # 4. Safely execute runner.js using subprocess (shell=False prevents shell injection)
    try:
        command = ['node', runner_script, validated_url]
        process_result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=base_dir,
            shell=False
        )

        if process_result.returncode != 0:
            # Check stderr for details
            stderr_output = process_result.stderr.strip()
            stdout_output = process_result.stdout.strip()
            
            error_details = "Unable to audit this website. The website may be unavailable or may block automated access."
            try:
                # Attempt to parse error JSON if runner returned one
                parsed_err = json.loads(stderr_output or stdout_output)
                if 'error' in parsed_err:
                    error_details = f"Lighthouse error: {parsed_err['error']}"
            except Exception:
                pass

            return jsonify({
                "success": False,
                "error": error_details
            }), 502

        # 5. Parse Lighthouse runner JSON output
        report_data = json.loads(process_result.stdout)
        scores = report_data.get('scores', {
            "performance": 0,
            "accessibility": 0,
            "best_practices": 0,
            "seo": 0
        })

        raw_audits = report_data.get('audits', [])

        # 6. Generate beginner-friendly summary & recommendations
        perf_score = scores.get('performance', 0)
        summary = generate_performance_summary(perf_score)
        recommendations = build_recommendations(raw_audits)

        # 7. Return clean result payload
        return jsonify({
            "success": True,
            "url": validated_url,
            "performance": scores.get('performance', 0),
            "accessibility": scores.get('accessibility', 0),
            "best_practices": scores.get('best_practices', 0),
            "seo": scores.get('seo', 0),
            "scores": scores,
            "summary": summary,
            "recommendations": recommendations
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "The Lighthouse audit timed out after 120 seconds. The target site may be taking too long to load."
        }), 504

    except json.JSONDecodeError:
        return jsonify({
            "success": False,
            "error": "Failed to process Lighthouse audit report output."
        }), 500

    except Exception as ex:
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred while running the audit: {str(ex)}"
        }), 500


if __name__ == '__main__':
    # Determine port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting RA Horizon Web LightHouse Performance Monitor on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=False)
