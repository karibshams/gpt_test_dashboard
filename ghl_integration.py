# ghl_integration.py - GoHighLevel Integration Module

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GHLIntegration:
    """
    GoHighLevel (GHL) Integration for social media engagement automation.
    Handles contact syncing, tagging, and workflow triggering.
    """
    
    def __init__(self, api_key: str, location_id: str):
        """
        Initialize GHL integration with API credentials.
        
        Args:
            api_key: GHL API key
            location_id: GHL Location/Account ID
        """
        self.api_key = api_key
        self.location_id = location_id
        self.base_url = "https://api.gohighlevel.com/v1"
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Define keyword mappings for different actions
        self.keyword_mappings = {
            "interested": ["interested", "want to buy", "how to order", "purchase", "pricing"],
            "hot_lead": ["ready to buy", "urgent", "asap", "immediately", "now"],
            "question": ["how", "what", "when", "where", "why", "?"],
            "complaint": ["problem", "issue", "disappointed", "terrible", "worst"],
            "praise": ["amazing", "excellent", "love", "best", "great"]
        }
        
        # Category to tag mappings
        self.category_tags = {
            "LEAD": ["social-media-lead", "interested"],
            "PRAISE": ["happy-customer", "testimonial"],
            "SPAM": ["spam", "to-review"],
            "QUESTION": ["needs-info", "inquiry"],
            "COMPLAINT": ["needs-attention", "unhappy-customer"]
        }
        
        # Workflow trigger rules
        self.workflow_rules = {
            "LEAD": "social_media_lead_workflow",
            "COMPLAINT": "complaint_resolution_workflow",
            "PRAISE": "testimonial_request_workflow"
        }
    
    def check_keywords(self, comment: str) -> List[str]:
        """
        Check comment for engagement keywords.
        
        Args:
            comment: The social media comment
            
        Returns:
            List of matched keyword categories
        """
        comment_lower = comment.lower()
        matched_categories = []
        
        for category, keywords in self.keyword_mappings.items():
            if any(keyword in comment_lower for keyword in keywords):
                matched_categories.append(category)
        
        return matched_categories
    
    def create_or_update_contact(self, contact_info: Dict) -> Dict:
        """
        Create or update a contact in GHL.
        
        Args:
            contact_info: Dictionary with contact details
            
        Returns:
            API response with contact ID
        """
        # Check if contact exists
        search_url = f"{self.base_url}/contacts/search"
        search_params = {
            "email": contact_info.get("email"),
            "locationId": self.location_id
        }
        
        try:
            # Search for existing contact
            search_response = requests.get(
                search_url, 
                headers=self.headers, 
                params=search_params
            )
            
            if search_response.status_code == 200:
                contacts = search_response.json().get("contacts", [])
                
                if contacts:
                    # Update existing contact
                    contact_id = contacts[0]["id"]
                    update_url = f"{self.base_url}/contacts/{contact_id}"
                    
                    update_data = {
                        "customFields": contact_info.get("customFields", {}),
                        "source": contact_info.get("source", "Social Media"),
                        "lastActivity": datetime.now().isoformat()
                    }
                    
                    response = requests.put(
                        update_url,
                        headers=self.headers,
                        json=update_data
                    )
                    
                    return {
                        "contact_id": contact_id,
                        "created": False,
                        "response": response.json() if response.status_code == 200 else None
                    }
                else:
                    # Create new contact
                    create_url = f"{self.base_url}/contacts"
                    
                    create_data = {
                        "locationId": self.location_id,
                        "email": contact_info.get("email"),
                        "firstName": contact_info.get("firstName", ""),
                        "lastName": contact_info.get("lastName", ""),
                        "phone": contact_info.get("phone", ""),
                        "source": contact_info.get("source", "Social Media"),
                        "customFields": contact_info.get("customFields", {})
                    }
                    
                    response = requests.post(
                        create_url,
                        headers=self.headers,
                        json=create_data
                    )
                    
                    if response.status_code == 201:
                        return {
                            "contact_id": response.json().get("id"),
                            "created": True,
                            "response": response.json()
                        }
            
        except Exception as e:
            logger.error(f"Error creating/updating contact: {str(e)}")
            return {"error": str(e)}
        
        return {"error": "Failed to create/update contact"}
    
    def add_tags_to_contact(self, contact_id: str, tags: List[str]) -> bool:
        """
        Add tags to a contact in GHL.
        
        Args:
            contact_id: GHL contact ID
            tags: List of tags to add
            
        Returns:
            Success status
        """
        url = f"{self.base_url}/contacts/{contact_id}/tags"
        
        try:
            for tag in tags:
                data = {"tag": tag}
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to add tag {tag}: {response.text}")
                    return False
            
            logger.info(f"Successfully added tags {tags} to contact {contact_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding tags: {str(e)}")
            return False
    
    def trigger_workflow(self, contact_id: str, workflow_name: str) -> bool:
        """
        Trigger a workflow for a contact.
        
        Args:
            contact_id: GHL contact ID
            workflow_name: Name of the workflow to trigger
            
        Returns:
            Success status
        """
        # Note: This is a simplified version. Actual implementation depends on
        # your GHL workflow setup and may require workflow IDs instead of names
        
        url = f"{self.base_url}/workflows/trigger"
        
        data = {
            "contactId": contact_id,
            "workflowName": workflow_name,
            "locationId": self.location_id
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                logger.info(f"Triggered workflow {workflow_name} for contact {contact_id}")
                return True
            else:
                logger.error(f"Failed to trigger workflow: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error triggering workflow: {str(e)}")
            return False
    
    def update_custom_fields(self, contact_id: str, fields: Dict) -> bool:
        """
        Update custom fields for a contact.
        
        Args:
            contact_id: GHL contact ID
            fields: Dictionary of custom fields to update
            
        Returns:
            Success status
        """
        url = f"{self.base_url}/contacts/{contact_id}"
        
        data = {"customFields": fields}
        
        try:
            response = requests.put(
                url,
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                logger.info(f"Updated custom fields for contact {contact_id}")
                return True
            else:
                logger.error(f"Failed to update fields: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating fields: {str(e)}")
            return False
    
    def process_comment(self, comment: str, category: str, contact_info: Dict) -> Dict:
        """
        Process a social media comment with full GHL integration.
        
        Args:
            comment: The social media comment
            category: AI-classified category
            contact_info: Contact information
            
        Returns:
            Dictionary with processing results
        """
        results = {
            "contact_created": False,
            "contact_updated": False,
            "tags_added": [],
            "workflow_triggered": False,
            "custom_fields_updated": False
        }
        
        try:
            # Step 1: Create or update contact
            contact_result = self.create_or_update_contact(contact_info)
            
            if "error" in contact_result:
                results["error"] = contact_result["error"]
                return results
            
            contact_id = contact_result["contact_id"]
            results["contact_created"] = contact_result["created"]
            results["contact_updated"] = not contact_result["created"]
            
            # Step 2: Add category-based tags
            tags = self.category_tags.get(category, [])
            
            # Add keyword-based tags
            keyword_categories = self.check_keywords(comment)
            for kw_category in keyword_categories:
                tags.append(f"keyword-{kw_category}")
            
            if tags and self.add_tags_to_contact(contact_id, tags):
                results["tags_added"] = tags
            
            # Step 3: Update custom fields
            custom_fields = {
                "last_social_interaction": datetime.now().isoformat(),
                "last_comment": comment[:255],  # Limit to 255 chars
                "engagement_category": category,
                "engagement_score": self.calculate_engagement_score(category, keyword_categories)
            }
            
            if self.update_custom_fields(contact_id, custom_fields):
                results["custom_fields_updated"] = True
            
            # Step 4: Trigger workflow if applicable
            if category in self.workflow_rules:
                workflow_name = self.workflow_rules[category]
                if self.trigger_workflow(contact_id, workflow_name):
                    results["workflow_triggered"] = True
            
            # Special handling for hot leads
            if "hot_lead" in keyword_categories:
                self.trigger_workflow(contact_id, "urgent_lead_notification")
                results["hot_lead_alert"] = True
            
            logger.info(f"Successfully processed comment for contact {contact_id}")
            
        except Exception as e:
            logger.error(f"Error processing comment: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    def calculate_engagement_score(self, category: str, keyword_matches: List[str]) -> int:
        """
        Calculate an engagement score based on category and keywords.
        
        Args:
            category: Comment category
            keyword_matches: Matched keyword categories
            
        Returns:
            Engagement score (0-100)
        """
        # Base scores by category
        category_scores = {
            "LEAD": 80,
            "QUESTION": 60,
            "PRAISE": 70,
            "COMPLAINT": 50,
            "SPAM": 0
        }
        
        score = category_scores.get(category, 30)
        
        # Bonus points for keywords
        if "interested" in keyword_matches:
            score += 10
        if "hot_lead" in keyword_matches:
            score += 15
        
        return min(score, 100)  # Cap at 100
    
    def get_contact_engagement_history(self, contact_id: str) -> Dict:
        """
        Get engagement history for a contact.
        
        Args:
            contact_id: GHL contact ID
            
        Returns:
            Engagement history data
        """
        url = f"{self.base_url}/contacts/{contact_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                contact_data = response.json()
                return {
                    "total_interactions": contact_data.get("customFields", {}).get("total_interactions", 0),
                    "last_interaction": contact_data.get("customFields", {}).get("last_social_interaction"),
                    "engagement_score": contact_data.get("customFields", {}).get("engagement_score", 0),
                    "tags": contact_data.get("tags", [])
                }
            
        except Exception as e:
            logger.error(f"Error getting contact history: {str(e)}")
        
        return {}


# Example usage function for testing
def test_ghl_integration():
    """Test function to demonstrate GHL integration."""
    
    # Initialize GHL
    ghl = GHLIntegration(
        api_key="your-ghl-api-key",
        location_id="your-location-id"
    )
    
    # Test comment processing
    test_comment = "I'm really interested in your product! How can I purchase it ASAP?"
    
    result = ghl.process_comment(
        comment=test_comment,
        category="LEAD",
        contact_info={
            "email": "test@example.com",
            "firstName": "Test",
            "lastName": "User",
            "source": "Facebook"
        }
    )
    
    print("GHL Processing Result:", json.dumps(result, indent=2))


if __name__ == "__main__":
    test_ghl_integration()