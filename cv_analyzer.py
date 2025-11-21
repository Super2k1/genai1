# CV Analysis System using LangChain and MarkItDown
# Install dependencies: pip install langchain-google-genai markitdown python-dotenv

import os
import json
from pathlib import Path
from markitdown import markitdown
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

class CVAnalyzer:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            api_key=api_key,
            temperature=0.5
        )
        
        self.cv_data = {}
        self.candidates = []
        
    def extract_cv_text(self, file_path: str) -> str:
        """Extract text from CV file (PDF, DOCX, etc.) using MarkItDown."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # MarkItDown automatically detects file type and extracts content
            result = markitdown.markitdown(file_path)
            return result if result else ""
        except Exception as e:
            print(f"Error extracting CV from {file_path}: {e}")
            return ""
    
    def analyze_cv(self, cv_text: str, candidate_name: str) -> dict:
        """Analyze CV content using LangChain and extract key information."""
        
        analysis_prompt = PromptTemplate(
            input_variables=["cv_content", "candidate_name"],
            template="""Analyze the following CV and extract key information in JSON format:

Candidate Name: {candidate_name}

CV Content:
{cv_content}

Please extract and provide:
1. Full Name
2. Email
3. Phone (if available)
4. Years of Experience
5. Top 5 Key Skills (as a list)
6. Education Background (degree, field, institution)
7. Professional Experience (job titles, companies, years)
8. Certifications (if any)
9. Overall Strength Score (1-10)
10. Strengths Summary (2-3 sentences)
11. Areas for Improvement (if any)

Return ONLY valid JSON format, no additional text."""
        )
        
        chain = LLMChain(llm=self.llm, prompt=analysis_prompt)
        
        try:
            result = chain.run(
                cv_content=cv_text[:3000],  # Limit to 3000 chars for efficiency
                candidate_name=candidate_name
            )
            
            # Parse JSON response
            analysis = json.loads(result)
            analysis["cv_text"] = cv_text
            return analysis
        except json.JSONDecodeError:
            print(f"Error parsing analysis for {candidate_name}")
            return {"error": "Failed to parse analysis", "candidate_name": candidate_name}
    
    def collect_cvs(self, cv_folder: str):
        """Collect and analyze all CVs from a folder."""
        folder_path = Path(cv_folder)
        
        if not folder_path.exists():
            print(f"Folder not found: {cv_folder}")
            return
        
        cv_extensions = {".pdf", ".docx", ".doc", ".txt", ".md"}
        cv_files = [f for f in folder_path.iterdir() if f.suffix.lower() in cv_extensions]
        
        if not cv_files:
            print(f"No CV files found in {cv_folder}")
            return
        
        print(f"Found {len(cv_files)} CV files. Analyzing...")
        
        for cv_file in cv_files:
            candidate_name = cv_file.stem
            print(f"\nProcessing: {candidate_name}")
            
            cv_text = self.extract_cv_text(str(cv_file))
            if cv_text:
                analysis = self.analyze_cv(cv_text, candidate_name)
                if "error" not in analysis:
                    self.candidates.append(analysis)
                    print(f"✓ Analyzed: {candidate_name}")
                else:
                    print(f"✗ Failed to analyze: {candidate_name}")
    
    def rank_candidates(self, job_requirements: str = None) -> list:
        """Rank candidates based on analysis and optional job requirements."""
        
        if not self.candidates:
            print("No candidates to rank")
            return []
        
        ranking_prompt = PromptTemplate(
            input_variables=["candidates_data", "job_requirements"],
            template="""You are an expert HR recruiter. Rank the following candidates based on their qualifications.

Job Requirements:
{job_requirements}

Candidates Data:
{candidates_data}

Provide a ranking in JSON format with:
1. rank (1, 2, 3, etc.)
2. candidate_name
3. match_score (0-100)
4. key_strengths (list of 3-4 points)
5. recommendation (hire/maybe/not_recommended)
6. reasoning (1-2 sentences)

Return ONLY valid JSON array format, sorted by rank."""
        )
        
        candidates_json = json.dumps(self.candidates, indent=2)
        requirements = job_requirements or "Software Engineer with 5+ years experience"
        
        chain = LLMChain(llm=self.llm, prompt=ranking_prompt)
        
        try:
            result = chain.run(
                candidates_data=candidates_json,
                job_requirements=requirements
            )
            
            rankings = json.loads(result)
            return rankings if isinstance(rankings, list) else [rankings]
        except json.JSONDecodeError:
            print("Error parsing rankings")
            return []
    
    def select_best_candidate(self, rankings: list) -> dict:
        """Select the best candidate from rankings."""
        if not rankings:
            return {}
        
        best = rankings[0]
        return best
    
    def generate_report(self, output_file: str = "cv_analysis_report.json"):
        """Generate a comprehensive analysis report."""
        report = {
            "total_candidates": len(self.candidates),
            "candidates_analyzed": self.candidates,
            "rankings": self.rank_candidates()
        }
        
        if report["rankings"]:
            report["best_candidate"] = report["rankings"][0]
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {output_file}")
        return report


def main():
    """Main function to run CV analysis."""
    
    # Initialize analyzer
    analyzer = CVAnalyzer()
    
    # Example: Collect CVs from a folder
    cv_folder = "./cvs"  # Create a 'cvs' folder and add CV files
    
    # Create sample cvs folder if it doesn't exist
    Path(cv_folder).mkdir(exist_ok=True)
    print(f"Please add CV files to the '{cv_folder}' folder")
    print("Supported formats: PDF, DOCX, DOC, TXT, MD\n")
    
    # Collect and analyze CVs
    analyzer.collect_cvs(cv_folder)
    
    if analyzer.candidates:
        # Get job requirements (optional)
        job_requirements = input("\nEnter job requirements (press Enter for default): ").strip()
        
        # Rank candidates
        rankings = analyzer.rank_candidates(job_requirements or None)
        
        # Display results
        print("\n" + "="*60)
        print("CANDIDATE RANKINGS")
        print("="*60)
        
        for ranking in rankings:
            print(f"\nRank: {ranking.get('rank')}")
            print(f"Candidate: {ranking.get('candidate_name')}")
            print(f"Match Score: {ranking.get('match_score')}%")
            print(f"Recommendation: {ranking.get('recommendation')}")
            print(f"Reasoning: {ranking.get('reasoning')}")
        
        # Select best candidate
        best = analyzer.select_best_candidate(rankings)
        print("\n" + "="*60)
        print(f"BEST CANDIDATE: {best.get('candidate_name')}")
        print(f"Match Score: {best.get('match_score')}%")
        print("="*60)
        
        # Generate report
        analyzer.generate_report()
    else:
        print("No CVs were successfully analyzed")


if __name__ == "__main__":
    main()
