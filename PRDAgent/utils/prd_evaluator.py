"""
PRD Evaluation Metrics Module
Evaluates PRD quality and completeness based on CIRCLES framework and best practices
"""
import re
import json
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import asyncio
import httpx

class PRDEvaluator:
    """Evaluates PRD documents for quality, completeness, and adherence to best practices"""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        self.llm_config = llm_config
        
        # CIRCLES framework mapping
        self.circles_sections = {
            'C': 'Comprehend the Situation',
            'I': 'Identify the Customer', 
            'R': 'Report Customer Needs',
            'C2': 'Cut Through Prioritization',
            'L': 'List Solutions',
            'E': 'Evaluate Trade-offs',
            'S': 'Summarize Recommendations'
        }
        
        # Evaluation criteria weights
        self.criteria_weights = {
            'completeness': 0.25,
            'clarity': 0.20,
            'specificity': 0.15,
            'feasibility': 0.15,
            'circles_alignment': 0.15,
            'structure': 0.10
        }
    
    def evaluate_prd_document(self, prd_content: str, template_sections: List[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a PRD document
        
        Args:
            prd_content: The complete PRD content as string
            template_sections: Template sections for context
            
        Returns:
            Dict containing evaluation results and scores
        """
        evaluation_results = {
            'overall_score': 0.0,
            'section_scores': {},
            'criteria_scores': {},
            'recommendations': [],
            'strengths': [],
            'weaknesses': [],
            'circles_coverage': {},
            'metadata': {
                'word_count': len(prd_content.split()),
                'section_count': 0,
                'has_user_stories': False,
                'has_acceptance_criteria': False,
                'has_metrics': False
            }
        }
        
        # Parse sections from content
        sections = self._parse_sections(prd_content)
        evaluation_results['metadata']['section_count'] = len(sections)
        
        # Evaluate each criterion
        evaluation_results['criteria_scores'] = {
            'completeness': self._evaluate_completeness(prd_content, sections, template_sections),
            'clarity': self._evaluate_clarity(prd_content, sections),
            'specificity': self._evaluate_specificity(prd_content, sections),
            'feasibility': self._evaluate_feasibility(prd_content, sections),
            'circles_alignment': self._evaluate_circles_alignment(prd_content, sections),
            'structure': self._evaluate_structure(prd_content, sections)
        }
        
        # Calculate overall score
        overall_score = 0.0
        for criterion, score in evaluation_results['criteria_scores'].items():
            overall_score += score * self.criteria_weights[criterion]
        evaluation_results['overall_score'] = round(overall_score, 2)
        
        # Evaluate individual sections
        for section_name, section_content in sections.items():
            evaluation_results['section_scores'][section_name] = self._evaluate_section(
                section_name, section_content
            )
        
        # CIRCLES framework coverage
        evaluation_results['circles_coverage'] = self._evaluate_circles_coverage(sections)
        
        # Generate recommendations
        evaluation_results['recommendations'] = self._generate_recommendations(evaluation_results)
        evaluation_results['strengths'] = self._identify_strengths(evaluation_results)
        evaluation_results['weaknesses'] = self._identify_weaknesses(evaluation_results)
        
        # Update metadata
        evaluation_results['metadata'].update({
            'has_user_stories': 'user story' in prd_content.lower() or 'as a' in prd_content.lower(),
            'has_acceptance_criteria': 'acceptance criteria' in prd_content.lower() or 'given' in prd_content.lower(),
            'has_metrics': any(metric in prd_content.lower() for metric in ['kpi', 'metric', 'measure', 'target', 'goal'])
        })
        
        return evaluation_results
    
    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse PRD content into sections"""
        sections = {}
        
        # Common section headers patterns
        header_patterns = [
            r'^#+\s*(.+?)$',  # Markdown headers
            r'^(\d+\.?\s*.+?)$',  # Numbered sections
            r'^([A-Z][^a-z\n]{5,})$',  # ALL CAPS headers
            r'^\*\*(.+?)\*\*$'  # Bold headers
        ]
        
        lines = content.split('\n')
        current_section = 'Introduction'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_header = False
            for pattern in header_patterns:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = match.group(1).strip('*# ')
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _evaluate_completeness(self, content: str, sections: Dict, template_sections: List[Dict] = None) -> float:
        """Evaluate completeness of the PRD"""
        score = 0.0
        max_score = 100.0
        
        # Essential PRD elements
        essential_elements = [
            ('product overview', 15),
            ('user', 10),
            ('problem', 15),
            ('solution', 15),
            ('requirement', 15),
            ('success metric', 10),
            ('timeline', 5),
            ('stakeholder', 5),
            ('assumption', 5),
            ('risk', 5)
        ]
        
        content_lower = content.lower()
        
        for element, weight in essential_elements:
            if element in content_lower:
                score += weight
            elif any(element.split()[0] in section.lower() for section in sections.keys()):
                score += weight * 0.8  # Partial credit for section headers
        
        return min(score / max_score * 100, 100.0)
    
    def _evaluate_clarity(self, content: str, sections: Dict) -> float:
        """Evaluate clarity and readability"""
        score = 0.0
        
        # Check for clear structure
        if len(sections) >= 5:
            score += 20
        
        # Check for bullet points and lists
        if '•' in content or '-' in content or re.search(r'^\d+\.', content, re.MULTILINE):
            score += 15
        
        # Check for clear language indicators
        clarity_indicators = ['clearly', 'specifically', 'precisely', 'exactly', 'defined as']
        score += min(sum(1 for indicator in clarity_indicators if indicator in content.lower()) * 5, 25)
        
        # Penalize overly complex sentences
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if avg_sentence_length < 25:
            score += 20
        elif avg_sentence_length < 35:
            score += 10
        
        # Check for jargon explanation
        if any(phrase in content.lower() for phrase in ['defined as', 'means', 'refers to', 'glossary']):
            score += 20
        
        return min(score, 100.0)
    
    def _evaluate_specificity(self, content: str, sections: Dict) -> float:
        """Evaluate specificity and detail level"""
        score = 0.0
        
        # Check for specific numbers and measurements
        if re.search(r'\d+%|\d+\s*(seconds?|minutes?|hours?|days?|weeks?|months?)', content):
            score += 25
        
        # Check for specific user personas
        if re.search(r'(persona|user type|target user)', content, re.IGNORECASE):
            score += 20
        
        # Check for detailed acceptance criteria
        if 'acceptance criteria' in content.lower() and 'given' in content.lower():
            score += 20
        
        # Check for specific technical details
        tech_terms = ['API', 'database', 'UI', 'UX', 'endpoint', 'framework', 'algorithm']
        score += min(sum(1 for term in tech_terms if term.lower() in content.lower()) * 3, 15)
        
        # Check for detailed user stories
        if re.search(r'as a.*I want.*so that', content, re.IGNORECASE):
            score += 20
        
        return min(score, 100.0)
    
    def _evaluate_feasibility(self, content: str, sections: Dict) -> float:
        """Evaluate technical and business feasibility considerations"""
        score = 0.0
        
        # Check for constraints mentioned
        constraints = ['constraint', 'limitation', 'dependency', 'resource', 'timeline', 'budget']
        score += min(sum(1 for constraint in constraints if constraint in content.lower()) * 10, 40)
        
        # Check for risk assessment
        if any(word in content.lower() for word in ['risk', 'challenge', 'mitigation']):
            score += 20
        
        # Check for technical considerations
        if any(word in content.lower() for word in ['scalability', 'performance', 'security', 'integration']):
            score += 20
        
        # Check for alternative solutions
        if any(word in content.lower() for word in ['alternative', 'option', 'approach', 'solution']):
            score += 20
        
        return min(score, 100.0)
    
    def _evaluate_circles_alignment(self, content: str, sections: Dict) -> float:
        """Evaluate alignment with CIRCLES framework"""
        score = 0.0
        circles_coverage = self._evaluate_circles_coverage(sections)
        
        # Score based on CIRCLES coverage
        total_circles = len(self.circles_sections)
        covered_circles = sum(1 for coverage in circles_coverage.values() if coverage['covered'])
        
        score = (covered_circles / total_circles) * 100
        return score
    
    def _evaluate_structure(self, content: str, sections: Dict) -> float:
        """Evaluate document structure and organization"""
        score = 0.0
        
        # Check for logical section order
        expected_early_sections = ['overview', 'introduction', 'summary', 'problem']
        expected_late_sections = ['implementation', 'timeline', 'conclusion', 'next steps']
        
        section_names = list(sections.keys())
        
        # Early sections bonus
        for i, section in enumerate(section_names[:3]):
            if any(expected in section.lower() for expected in expected_early_sections):
                score += 15
                break
        
        # Late sections bonus
        for i, section in enumerate(section_names[-3:]):
            if any(expected in section.lower() for expected in expected_late_sections):
                score += 15
                break
        
        # Section count appropriateness
        if 6 <= len(sections) <= 15:
            score += 30
        elif 4 <= len(sections) <= 20:
            score += 20
        
        # Check for table of contents or clear navigation
        if any(phrase in content.lower() for phrase in ['table of contents', 'overview', 'sections']):
            score += 20
        
        # Check for consistent formatting
        if re.search(r'^#+\s', content, re.MULTILINE):  # Markdown headers
            score += 20
        
        return min(score, 100.0)
    
    def _evaluate_section(self, section_name: str, section_content: str) -> Dict[str, Any]:
        """Evaluate individual section quality"""
        section_score = {
            'content_score': 0.0,
            'length_score': 0.0,
            'detail_score': 0.0,
            'overall_score': 0.0,
            'word_count': len(section_content.split()),
            'recommendations': []
        }
        
        word_count = len(section_content.split())
        
        # Length appropriateness (varies by section type)
        if 'overview' in section_name.lower() or 'summary' in section_name.lower():
            optimal_range = (50, 200)
        elif 'requirement' in section_name.lower():
            optimal_range = (100, 500)
        else:
            optimal_range = (30, 300)
        
        if optimal_range[0] <= word_count <= optimal_range[1]:
            section_score['length_score'] = 100.0
        elif word_count < optimal_range[0]:
            section_score['length_score'] = (word_count / optimal_range[0]) * 100
        else:
            section_score['length_score'] = max(0, 100 - ((word_count - optimal_range[1]) / optimal_range[1]) * 50)
        
        # Content quality
        if section_content.strip():
            section_score['content_score'] = 70.0  # Base score for having content
            
            # Bonus for specific elements
            if any(char in section_content for char in ['•', '-', '1.', '2.']):
                section_score['content_score'] += 15  # Lists
            
            if len(section_content.split('.')) >= 3:
                section_score['content_score'] += 15  # Multiple sentences
        
        # Detail score
        if re.search(r'\d+', section_content):
            section_score['detail_score'] += 30  # Numbers/metrics
        if len(section_content.split()) > 50:
            section_score['detail_score'] += 40  # Sufficient detail
        if any(word in section_content.lower() for word in ['specific', 'detailed', 'example']):
            section_score['detail_score'] += 30  # Specificity indicators
        
        # Calculate overall section score
        section_score['overall_score'] = (
            section_score['content_score'] * 0.5 +
            section_score['length_score'] * 0.3 +
            section_score['detail_score'] * 0.2
        )
        
        # Generate section-specific recommendations
        if section_score['length_score'] < 50:
            section_score['recommendations'].append(f"Consider adding more detail to the {section_name} section")
        if section_score['detail_score'] < 50:
            section_score['recommendations'].append(f"Add specific examples or metrics to {section_name}")
        
        return section_score
    
    def _evaluate_circles_coverage(self, sections: Dict) -> Dict[str, Dict]:
        """Evaluate coverage of CIRCLES framework elements"""
        circles_coverage = {}
        
        section_names_lower = [name.lower() for name in sections.keys()]
        content_combined = ' '.join(sections.values()).lower()
        
        # Define CIRCLES mapping to content patterns
        circles_patterns = {
            'C': {
                'name': 'Comprehend the Situation',
                'keywords': ['situation', 'context', 'background', 'current state', 'problem space'],
                'required_elements': ['problem statement', 'business context']
            },
            'I': {
                'name': 'Identify the Customer',
                'keywords': ['user', 'customer', 'persona', 'target audience', 'stakeholder'],
                'required_elements': ['user personas', 'target users']
            },
            'R': {
                'name': 'Report Customer Needs',
                'keywords': ['needs', 'pain points', 'requirements', 'user story', 'goals'],
                'required_elements': ['user needs', 'user stories']
            },
            'C2': {
                'name': 'Cut Through Prioritization',
                'keywords': ['priority', 'must have', 'should have', 'nice to have', 'mvp', 'prioritiz', 'critical', 'important', 'urgent', 'high priority', 'low priority'],
                'required_elements': ['prioritization', 'feature priority']
            },
            'L': {
                'name': 'List Solutions',
                'keywords': ['solution', 'approach', 'feature', 'functionality', 'implementation'],
                'required_elements': ['proposed solution', 'features']
            },
            'E': {
                'name': 'Evaluate Trade-offs',
                'keywords': ['trade-off', 'pros and cons', 'alternative', 'comparison', 'evaluation'],
                'required_elements': ['trade-offs', 'alternatives']
            },
            'S': {
                'name': 'Summarize Recommendations',
                'keywords': ['recommendation', 'conclusion', 'next steps', 'summary', 'decision', 'recommend', 'suggest', 'propose', 'action items', 'follow up'],
                'required_elements': ['recommendations', 'next steps']
            }
        }
        
        for circle_key, circle_info in circles_patterns.items():
            coverage = {
                'name': circle_info['name'],
                'covered': False,
                'score': 0.0,
                'found_elements': [],
                'missing_elements': [],
                'section_matches': []
            }
            
            # Check for keyword matches
            keyword_matches = sum(1 for keyword in circle_info['keywords'] if keyword in content_combined)
            
            # Check for section matches
            section_matches = [name for name in section_names_lower 
                             if any(keyword in name for keyword in circle_info['keywords'])]
            
            # Calculate coverage score
            if keyword_matches > 0 or section_matches:
                coverage['covered'] = True
                coverage['score'] = min(100.0, (keyword_matches * 15) + (len(section_matches) * 30))
                coverage['found_elements'] = [kw for kw in circle_info['keywords'] if kw in content_combined]
                coverage['section_matches'] = section_matches
            
            # Identify missing elements
            coverage['missing_elements'] = [elem for elem in circle_info['required_elements'] 
                                          if not any(word in elem.lower() for word in coverage['found_elements'])]
            
            circles_coverage[circle_key] = coverage
        
        return circles_coverage
    
    def _generate_recommendations(self, evaluation_results: Dict) -> List[str]:
        """Generate improvement recommendations based on evaluation"""
        recommendations = []
        
        # Overall score recommendations
        if evaluation_results['overall_score'] < 60:
            recommendations.append("🔴 Consider a major revision - overall quality needs significant improvement")
        elif evaluation_results['overall_score'] < 80:
            recommendations.append("🟡 Good foundation - focus on addressing specific weaknesses")
        
        # Criteria-specific recommendations
        criteria_scores = evaluation_results['criteria_scores']
        
        if criteria_scores['completeness'] < 70:
            recommendations.append("📝 Add missing essential sections: problem statement, solution overview, success metrics")
        
        if criteria_scores['clarity'] < 70:
            recommendations.append("✨ Improve clarity: use bullet points, shorter sentences, and define technical terms")
        
        if criteria_scores['specificity'] < 70:
            recommendations.append("🎯 Add more specificity: include concrete numbers, detailed user stories, and specific acceptance criteria")
        
        if criteria_scores['circles_alignment'] < 60:
            recommendations.append("🔄 Better align with CIRCLES framework - see coverage analysis for missing elements")
        
        # CIRCLES-specific recommendations
        circles_coverage = evaluation_results['circles_coverage']
        circles_names = {
            'C': 'Comprehend the Situation',
            'I': 'Identify the Customer', 
            'R': 'Report Customer Needs',
            'C2': 'Cut Through Prioritization',
            'L': 'List Solutions',
            'E': 'Evaluate Trade-offs',
            'S': 'Summarize Recommendations'
        }
        missing_circles = [circles_names.get(key, f'Circle {key}') 
                          for key, info in circles_coverage.items() if not info['covered']]
        
        if missing_circles:
            recommendations.append(f"🎯 Address missing CIRCLES elements: {', '.join(missing_circles[:3])}")
        
        return recommendations
    
    def _identify_strengths(self, evaluation_results: Dict) -> List[str]:
        """Identify document strengths"""
        strengths = []
        criteria_scores = evaluation_results['criteria_scores']
        
        if criteria_scores['completeness'] >= 80:
            strengths.append("✅ Comprehensive coverage of essential PRD elements")
        
        if criteria_scores['clarity'] >= 80:
            strengths.append("✅ Clear and well-structured content")
        
        if criteria_scores['specificity'] >= 80:
            strengths.append("✅ Specific and detailed requirements")
        
        if criteria_scores['circles_alignment'] >= 80:
            strengths.append("✅ Strong alignment with CIRCLES framework")
        
        if evaluation_results['metadata']['has_user_stories']:
            strengths.append("✅ Includes user stories for clear requirement definition")
        
        if evaluation_results['metadata']['has_metrics']:
            strengths.append("✅ Includes success metrics and measurable goals")
        
        return strengths
    
    def _identify_weaknesses(self, evaluation_results: Dict) -> List[str]:
        """Identify document weaknesses"""
        weaknesses = []
        criteria_scores = evaluation_results['criteria_scores']
        
        if criteria_scores['completeness'] < 60:
            weaknesses.append("❌ Missing critical PRD sections")
        
        if criteria_scores['clarity'] < 60:
            weaknesses.append("❌ Content lacks clarity and structure")
        
        if criteria_scores['specificity'] < 60:
            weaknesses.append("❌ Requirements are too vague or high-level")
        
        if criteria_scores['feasibility'] < 60:
            weaknesses.append("❌ Insufficient consideration of constraints and risks")
        
        if not evaluation_results['metadata']['has_user_stories']:
            weaknesses.append("❌ Missing user stories for requirement clarity")
        
        if not evaluation_results['metadata']['has_acceptance_criteria']:
            weaknesses.append("❌ Missing acceptance criteria for features")
        
        return weaknesses
    
    async def llm_quality_assessment(self, prd_content: str) -> Dict[str, Any]:
        """Use LLM for streamlined quality assessment"""
        if not self.llm_config:
            return {"error": "LLM configuration not available"}

        prompt = f"""Evaluate this PRD document briefly (1-10 scale each):

PRD CONTENT:
{prd_content[:2000]}...

Rate and provide brief feedback:
1. CLARITY - Clear and understandable?
2. COMPLETENESS - All essential elements covered?
3. ACTIONABILITY - Requirements specific and implementable?
4. BUSINESS_VALUE - Value proposition clear?

Respond in JSON:
{{
  "scores": {{"clarity": <score>, "completeness": <score>, "actionability": <score>, "business_value": <score>}},
  "overall_score": <average>,
  "feedback": {{"strengths": ["brief strength"], "improvements": ["brief improvement"]}}
}}"""

        try:
            # Call LLM
            response = await self._call_llm(prompt)
            
            # Parse JSON response
            import json
            result = json.loads(response)
            return result
            
        except Exception as e:
            return {"error": f"LLM assessment failed: {str(e)}"}
    
    async def _call_llm(self, prompt: str) -> str:
        """Call Azure OpenAI for evaluation"""
        endpoint = f"{self.llm_config['azure_endpoint']}/openai/deployments/{self.llm_config['deployment_name']}/chat/completions?api-version={self.llm_config['api_version']}"
        headers = {
            "api-key": self.llm_config["api_key"],
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.2
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, json=payload, headers=headers, timeout=60.0)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"Azure OpenAI API call failed: {response.status_code} - {response.text}")

def create_evaluation_report(evaluation_results: Dict) -> str:
    """Create a formatted evaluation report"""
    report = f"""
# 📊 PRD Evaluation Report

## Overall Score: {evaluation_results['overall_score']}/100

### Quality Breakdown:
"""
    
    for criterion, score in evaluation_results['criteria_scores'].items():
        emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        report += f"- **{criterion.title()}**: {score:.1f}/100 {emoji}\n"
    
    report += f"""
### CIRCLES Framework Coverage:
"""
    
    for circle_key, circle_info in evaluation_results['circles_coverage'].items():
        status = "✅" if circle_info['covered'] else "❌"
        report += f"- **{circle_key} - {circle_info.get('name', 'Unknown')}**: {status} ({circle_info['score']:.1f}/100)\n"
    
    if evaluation_results['strengths']:
        report += f"\n### 💪 Strengths:\n"
        for strength in evaluation_results['strengths']:
            report += f"- {strength}\n"
    
    if evaluation_results['weaknesses']:
        report += f"\n### ⚠️ Areas for Improvement:\n"
        for weakness in evaluation_results['weaknesses']:
            report += f"- {weakness}\n"
    
    if evaluation_results['recommendations']:
        report += f"\n### 🎯 Recommendations:\n"
        for rec in evaluation_results['recommendations']:
            report += f"- {rec}\n"
    
    report += f"""
### 📈 Document Statistics:
- **Word Count**: {evaluation_results['metadata']['word_count']}
- **Sections**: {evaluation_results['metadata']['section_count']}
- **Has User Stories**: {'✅' if evaluation_results['metadata']['has_user_stories'] else '❌'}
- **Has Acceptance Criteria**: {'✅' if evaluation_results['metadata']['has_acceptance_criteria'] else '❌'}
- **Has Success Metrics**: {'✅' if evaluation_results['metadata']['has_metrics'] else '❌'}
"""
    
    return report
