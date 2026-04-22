"""
Domain Age Checker Flask Application
A web application to check domain registration age and WHOIS information
"""

from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
from whois_service import get_domain_age
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure caching
cache_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 86400  # 24 hours
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/')
def home():
    """Render the home page with domain lookup form"""
    return render_template('index.html')


@app.route('/check-domain', methods=['GET'])
def check_domain_api():
    """
    API endpoint to check domain age and WHOIS information
    
    Query Parameters:
        domain (str): Domain name to check (e.g., example.com)
    
    Returns:
        JSON response with domain information or error message
    """
    domain = request.args.get('domain', '').strip()
    
    if not domain:
        return jsonify({
            'error': 'Domain parameter is required',
            'status': 'error'
        }), 400
    
    try:
        # Get cached result or fetch new data
        result = get_cached_domain_info(domain.lower())
        return jsonify(result.to_dict())
    
    except Exception as e:
        logger.error(f"Error checking domain {domain}: {str(e)}")
        return jsonify({
            'error': 'Service temporarily unavailable. Please try again later.',
            'status': 'error'
        }), 500


def get_cached_domain_info(domain):
    """
    Get domain information with caching
    Cache key includes domain name for per-domain caching
    
    Args:
        domain (str): Domain name to check
    
    Returns:
        DomainInfo object
    """
    cache_key = f'whois_result_{domain.lower()}'
    
    # Try to get from cache
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for domain: {domain}")
        return cached_result
    
    logger.info(f"Fetching WHOIS data for domain: {domain}")
    result = get_domain_age(domain)
    
    # Store in cache for 24 hours
    cache.set(cache_key, result, timeout=86400)
    
    return result


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'Domain Age Checker'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'not_found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500


if __name__ == '__main__':
    # Run the Flask development server
    logger.info("Starting Domain Age Checker application...")
    app.run(debug=True, host='0.0.0.0', port=5000)