"""
WHOIS Service Module
Handles domain WHOIS lookups and data parsing
"""

import whois
import validators
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re


class DomainInfo:
    """Data class for storing domain information"""
    def __init__(self):
        self.domain = None
        self.created_date = None
        self.expiration_date = None
        self.age = None
        self.registrar = None
        self.status = "unknown"
        self.error = None

    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "domain": self.domain,
            "created_date": self.created_date,
            "expiration_date": self.expiration_date,
            "age": self.age,
            "registrar": self.registrar,
            "status": self.status,
            "error": self.error
        }


def validate_domain(domain):
    """
    Validate domain format
    Returns: True if valid, False otherwise
    """
    if not domain or not isinstance(domain, str):
        return False
    
    domain = domain.strip()
    
    # Basic domain format validation
    domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    
    if not re.match(domain_pattern, domain):
        return False
    
    return True


def calculate_age(created_date):
    """
    Calculate domain age from creation date
    Returns: String with years, months, days
    """
    if not created_date:
        return "Age cannot be determined"
    
    try:
        if isinstance(created_date, str):
            created_date = date_parser.parse(created_date)
        
        today = datetime.now()
        
        # Calculate years, months, days
        years = today.year - created_date.year
        months = today.month - created_date.month
        days = today.day - created_date.day
        
        # Adjust for negative values
        if days < 0:
            months -= 1
            # Get days in previous month
            prev_month = today.replace(day=1) - timedelta(days=1)
            days += prev_month.day
        
        if months < 0:
            years -= 1
            months += 12
        
        # Format age string
        age_parts = []
        if years > 0:
            age_parts.append(f"{years} year{'s' if years > 1 else ''}")
        if months > 0:
            age_parts.append(f"{months} month{'s' if months > 1 else ''}")
        if days > 0 or not age_parts:
            age_parts.append(f"{days} day{'s' if days > 1 else ''}")
        
        return ", ".join(age_parts)
    
    except Exception as e:
        return f"Age cannot be determined ({str(e)})"


def normalize_date(date_value):
    """
    Normalize various date formats to YYYY-MM-DD string
    """
    if not date_value:
        return "Unknown"
    
    try:
        if isinstance(date_value, str):
            parsed_date = date_parser.parse(date_value)
        else:
            parsed_date = date_value
        
        return parsed_date.strftime("%Y-%m-%d")
    except Exception:
        return "Unknown"


def get_domain_age(domain):
    """
    Main function to get domain information via WHOIS
    
    Args:
        domain: Domain name (e.g., example.com)
    
    Returns:
        DomainInfo object with parsed WHOIS data
    """
    info = DomainInfo()
    info.domain = domain.lower().strip()
    
    # Validate domain format
    if not validate_domain(domain):
        info.error = "Invalid domain format. Please enter a valid domain (e.g., example.com)"
        info.status = "invalid"
        return info
    
    try:
        # Perform WHOIS lookup
        whois_data = whois.whois(domain)
        
        # Extract creation date
        if hasattr(whois_data, 'creation_date'):
            creation_date = whois_data.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            info.created_date = normalize_date(creation_date)
        else:
            info.created_date = "Unknown"
        
        # Extract expiration date
        if hasattr(whois_data, 'expiration_date'):
            expiration_date = whois_data.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
            info.expiration_date = normalize_date(expiration_date)
        else:
            info.expiration_date = "Unknown"
        
        # Extract registrar
        if hasattr(whois_data, 'registrar'):
            info.registrar = whois_data.registrar if whois_data.registrar else "Unknown"
        else:
            info.registrar = "Unknown"
        
        # Determine status
        if info.expiration_date != "Unknown":
            try:
                exp_date = date_parser.parse(info.expiration_date)
                if exp_date < datetime.now():
                    info.status = "expired"
                else:
                    info.status = "active"
            except Exception:
                info.status = "active"
        else:
            info.status = "unknown"
        
        # Calculate domain age
        if info.created_date != "Unknown":
            info.age = calculate_age(info.created_date)
        else:
            info.age = "Age cannot be determined"
        
        return info
    
    except whois.parser.PywhoisError as e:
        info.error = f"Domain not found or WHOIS lookup failed: {str(e)}"
        info.status = "not_found"
        return info
    
    except Exception as e:
        info.error = f"Error during WHOIS lookup: {str(e)}"
        info.status = "error"
        return info
