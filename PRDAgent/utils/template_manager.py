"""
Simplified Template Manager for Groq Hackathon Version
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class GroqTemplateManager:
    """Simplified template manager for hackathon submission"""
    
    def __init__(self, templates_dir: str = None):
        """Initialize with templates directory"""
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        
        self.templates_dir = Path(templates_dir)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load all templates from the templates directory"""
        templates = {}
        
        # Default templates
        default_templates = {
            "standard_template": {
                "name": "Standard BRD Template",
                "description": "Comprehensive business requirements document template suitable for most projects",
                "category": "general",
                "sections": [
                    "executive_summary",
                    "problem_statement",
                    "solution_overview",
                    "requirements",
                    "success_criteria",
                    "implementation_plan"
                ]
            },
            "agile_feature_template": {
                "name": "Agile Feature Template",
                "description": "Template optimized for agile development and feature specifications",
                "category": "agile",
                "sections": [
                    "feature_overview",
                    "user_stories",
                    "acceptance_criteria",
                    "technical_requirements",
                    "testing_criteria"
                ]
            },
            "mobile_app_template": {
                "name": "Mobile App Template",
                "description": "Specialized template for mobile application requirements",
                "category": "mobile",
                "sections": [
                    "app_overview",
                    "user_experience",
                    "functional_requirements",
                    "platform_requirements",
                    "performance_criteria",
                    "security_requirements"
                ]
            }
        }
        
        templates.update(default_templates)
        
        # Load custom templates from files if directory exists
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.json"):
                try:
                    # Skip configuration files
                    if template_file.stem in ['template_config'] or template_file.stem.endswith('_config'):
                        continue
                        
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        template_id = template_file.stem
                        templates[template_id] = template_data
                except Exception as e:
                    print(f"Warning: Could not load template {template_file}: {e}")
        
        return templates
    
    def list_templates(self) -> Dict[str, Any]:
        """Get all available templates"""
        return self.templates.copy()
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID"""
        return self.templates.get(template_id)
    
    def get_template_names(self) -> List[str]:
        """Get list of template names"""
        return [template.get('name', tid) for tid, template in self.templates.items()]
    
    def get_template_by_category(self, category: str) -> Dict[str, Any]:
        """Get templates filtered by category"""
        return {
            tid: template for tid, template in self.templates.items()
            if template.get('category') == category
        }
    
    def generate_questions(self, template_id: str) -> List[Dict[str, Any]]:
        """Generate questions for a specific template"""
        template = self.get_template(template_id)
        if not template:
            return self._get_default_questions()
        
        # Generate questions based on template sections
        questions = []
        section_questions = {
            "executive_summary": [
                {
                    "id": "problem_statement",
                    "question": "What is the main problem or challenge you're trying to solve?",
                    "category": "problem_analysis",
                    "required": True
                },
                {
                    "id": "solution_overview",
                    "question": "What is your proposed solution in a nutshell?",
                    "category": "solution_design",
                    "required": True
                }
            ],
            "business_case": [
                {
                    "id": "business_value",
                    "question": "What business value will this solution provide?",
                    "category": "business_analysis",
                    "required": True
                }
            ],
            "stakeholder_analysis": [
                {
                    "id": "target_users",
                    "question": "Who are your target users or customers?",
                    "category": "user_analysis",
                    "required": True
                }
            ],
            "requirements_specification": [
                {
                    "id": "functional_requirements",
                    "question": "What are the key functional requirements?",
                    "category": "requirements",
                    "required": True
                }
            ],
            "success_criteria": [
                {
                    "id": "success_metrics",
                    "question": "How will you measure success?",
                    "category": "metrics",
                    "required": True
                }
            ],
            "implementation_plan": [
                {
                    "id": "timeline",
                    "question": "What is your expected timeline?",
                    "category": "planning",
                    "required": False
                }
            ]
        }
        
        # Add questions based on template sections
        for section in template.get('sections', []):
            if section in section_questions:
                questions.extend(section_questions[section])
        
        # Add default questions if none found
        if not questions:
            questions = self._get_default_questions()
        
        # Ensure we have a reasonable number of questions
        while len(questions) < 8:
            questions.extend(self._get_additional_questions()[:8 - len(questions)])
        
        return questions[:12]  # Limit to 12 questions
    
    def _get_default_questions(self) -> List[Dict[str, Any]]:
        """Get default questions for any template"""
        return [
            {
                "id": "product_overview",
                "question": "What is your product or project about?",
                "category": "overview",
                "required": True
            },
            {
                "id": "target_audience",
                "question": "Who is your target audience?",
                "category": "users",
                "required": True
            },
            {
                "id": "main_problem",
                "question": "What main problem does this solve?",
                "category": "problem",
                "required": True
            },
            {
                "id": "key_features",
                "question": "What are the key features or capabilities?",
                "category": "features",
                "required": True
            },
            {
                "id": "success_definition",
                "question": "How do you define success for this project?",
                "category": "success",
                "required": True
            }
        ]
    
    def _get_additional_questions(self) -> List[Dict[str, Any]]:
        """Get additional questions to fill out the set"""
        return [
            {
                "id": "technical_constraints",
                "question": "Are there any technical constraints or requirements?",
                "category": "technical",
                "required": False
            },
            {
                "id": "budget_timeline",
                "question": "What are your budget and timeline constraints?",
                "category": "constraints",
                "required": False
            },
            {
                "id": "competition",
                "question": "What alternatives or competitors exist?",
                "category": "competitive",
                "required": False
            },
            {
                "id": "risks",
                "question": "What are the main risks or challenges?",
                "category": "risks",
                "required": False
            },
            {
                "id": "stakeholders",
                "question": "Who are the key stakeholders?",
                "category": "stakeholders",
                "required": False
            },
            {
                "id": "assumptions",
                "question": "What key assumptions are you making?",
                "category": "assumptions",
                "required": False
            },
            {
                "id": "integration",
                "question": "What systems or tools need to integrate?",
                "category": "integration",
                "required": False
            }
        ]

# Global instance
_template_manager_instance = None

def get_template_manager() -> GroqTemplateManager:
    """Get the global template manager instance"""
    global _template_manager_instance
    if _template_manager_instance is None:
        _template_manager_instance = GroqTemplateManager()
    return _template_manager_instance
