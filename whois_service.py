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
        self.expiration_remaining = None

    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "domain": self.domain,
            "created_date": self.created_date,
            "expiration_date": self.expiration_date,
            "age": self.age,
            "registrar": self.registrar,
            "status": self.status,
            "error": self.error,
            "expiration_remaining": self.expiration_remaining
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


def calculate_expiration_remaining(expiration_date):
    """
    Calculate remaining days and years until domain expiration
    
    Args:
        expiration_date: Expiration date (string or datetime)
    
    Returns:
        Dictionary with days_remaining, years_remaining, and formatted string
    """
    if not expiration_date or expiration_date == "Unknown":
        return {
            "days_remaining": None,
            "years_remaining": None,
            "formatted": "Unknown"
        }
    
    try:
        if isinstance(expiration_date, str):
            exp_date = date_parser.parse(expiration_date)
        else:
            exp_date = expiration_date
        
        today = datetime.now()
        
        # Calculate days remaining
        delta = exp_date - today
        days_remaining = delta.days
        
        if days_remaining < 0:
            return {
                "days_remaining": days_remaining,
                "years_remaining": 0,
                "formatted": "Expired"
            }
        
        # Calculate years remaining
        years_remaining = days_remaining // 365
        remaining_days_in_year = days_remaining % 365
        
        # Format string
        parts = []
        if years_remaining > 0:
            parts.append(f"{years_remaining} year{'s' if years_remaining > 1 else ''}")
        if remaining_days_in_year > 0:
            parts.append(f"{remaining_days_in_year} day{'s' if remaining_days_in_year > 1 else ''}")
        
        formatted = ", ".join(parts) if parts else "Expires today"
        
        return {
            "days_remaining": days_remaining,
            "years_remaining": years_remaining,
            "formatted": formatted
        }
    
    except Exception as e:
        return {
            "days_remaining": None,
            "years_remaining": None,
            "formatted": f"Cannot calculate ({str(e)})"
        }


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
        
        # Calculate expiration remaining
        if info.expiration_date != "Unknown":
            info.expiration_remaining = calculate_expiration_remaining(info.expiration_date)
        else:
            info.expiration_remaining = calculate_expiration_remaining(None)
        
        return info
    
    except whois.parser.PywhoisError as e:
        info.error = f"Domain not found or WHOIS lookup failed: {str(e)}"
        info.status = "not_found"
        return info
    
    except Exception as e:
        info.error = f"Error during WHOIS lookup: {str(e)}"
        info.status = "error"
        return info

