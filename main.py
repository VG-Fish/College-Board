from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement # imported for type hint
from typing import Tuple, Set, Dict

class Scraper():
    # Init Page Options
    valid_assessments: Tuple[str] = ("SAT", "PSAT/NMSQT & PSAT 10", "PSAT 8/9")
    valid_tests: Tuple[str] = ("Reading and Writing", "Math")

    valid_reading_and_writing_options: Set[str] = {"Information and Ideas", "Craft and Structure", "Expression of Ideas", "Standard English Conventions"}
    valid_math_options: Set[str] = {"Algebra", "Advanced Math", "Problem-Solving and Data Analysis", "Geometry and Trigonometry"}

    # Main Page options
    valid_difficulty_options: Tuple[str] = ["Easy", "Medium", "Hard"]

    valid_reading_and_writing_skills: Dict[str, Set[str]] = {
        "Information and Ideas": {"Central Ideas and Details", "Inferences", "Command of Evidence"}, 
        "Craft and Structure": {"Words in Context", "Text Structure and Purpose", "Cross-Text Connections"},
        "Expression of Ideas": {"Rhetorical Synthesis", "Transitions"},
        "Standard English Conventions": {"Boundaries", "Form, Structure, and Sense"}
    }
    valid_math_skills: Dict[str, Set[str]] = {
        "Algebra": {
            "Linear equations in one variable", "Linear functions", "Linear equations in two variables", "Systems of two linear equations in two variables",
            "Linear inequalities in one or two variables"
        }, 
        "Advanced Math": {"Nonlinear functions", "Nonlinear equations in one variable and systems of equations in two variables", "Equivalent expressions"}, 
        "Problem-Solving and Data Analysis": {
            "Ratios, rates, proportional relationships, and units", "Percentages", "One-variable data: Distributions and measures of center and spread",
            "Two-variable data: Models and scatterplots", "Probability and conditional probability", "Inference from sample statistics and margin of error",
            "Evaluating statistical claims: Observational studies and experiments"
        }, 
        "Geometry and Trigonometry": {"Area and volume", "Lines, angles, and triangles", "Right triangles and trigonometry", "Circles"}
    }

    def __init__(
            self: "Scraper", 
            assessment: str, 
            test: str, 
            options: Set[str],
            difficulty: str | None = None, 
            skills: Dict[str, Set[str]] | None = None,
            exclude_active_questions: bool = False
        ) -> None:
        self.assessment: str = assessment
        if self.assessment not in Scraper.valid_assessments:
            raise ValueError(f"assessment (you inputted {self.assessment}) must be one of these three options: {Scraper.valid_assessments}.")
        
        self.test: str = test
        if self.test not in Scraper.valid_tests:
            raise ValueError(f"test (you inputted {self.test}) must be one of these two options: {Scraper.valid_tests}.")
        
        self.options: Set[str] = options
        if len(self.options) == 0:
            raise ValueError(f"Length of options must not be zero. Add these options: {Scraper.valid_reading_and_writing_options}")
        elif self.test == "Reading and Writing" and not self.options.issubset(Scraper.valid_reading_and_writing_options):
            raise ValueError(f"options (you inputted {self.options}) must be a valid subset of {Scraper.valid_reading_and_writing_options}.")
        elif self.test == "Math" and not self.options.issubset(Scraper.valid_math_options):
            raise ValueError(f"options (you inputted {self.options}) must be a valid subset of {Scraper.valid_math_options}.")

        self.difficulty: bool | None = difficulty
        if difficulty is not None and self.difficulty not in Scraper.valid_difficulty_options:
            raise ValueError(f"difficulty (you inputted {self.difficulty}) must be one of these three options: {Scraper.valid_difficulty_options}.")

        # Checking if self.skills has valid skills that can all actually be clicked on the website.
        self.skills: Dict[str, Set[str]] = skills
        if skills is not None and self.test == "Reading and Writing":
            self._check_if_skills_valid(Scraper.valid_reading_and_writing_skills)
        elif skills is not None and self.test == "Math":
            self._check_if_skills_valid(Scraper.valid_math_skills)

        self.exclude_active_questions: bool = exclude_active_questions
        
        self.driver: webdriver.Firefox = webdriver.Firefox()

    def _check_if_skills_valid(self: "Scraper", valid_skills: Dict[str, Set[str]]) -> None:
        if not set(self.skills.keys()).issubset(self.options):
            raise ValueError(f"skills keys (you inputted {self.skills.keys()}) must be a valid subset of options {self.options}.")
            
        for option in self.options:
            if option not in self.skills:
                raise ValueError(f"{option} is not found in {self.options}.")
            if not self.skills[option].issubset(valid_skills[option]):
                raise ValueError(
                    f"one of skills value (you inputted {self.skills[option]}) is not a valid subset of the options {valid_skills[option]}."
                )

    def scrape(self: "Scraper") -> None:
        self._go_to_main_page()
        self._main_page()

    # Handles all introductory options
    def _go_to_main_page(self: "Scraper") -> None:
        self.driver.get("https://satsuitequestionbank.collegeboard.org/digital/search")

        search_assessment_element: Select = Select(WebDriverWait(self.driver, 2.0).until(
            EC.presence_of_element_located((By.ID, "selectAssessmentType"))
        ))
        search_assessment_element.select_by_visible_text(self.assessment)

        test_type_element: Select = Select(WebDriverWait(self.driver, 1.0).until(
            EC.presence_of_element_located((By.ID, "selectTestType"))
        ))
        test_type_element.select_by_visible_text(self.test)

        for option in self.options:
            checkbox: WebElement = WebDriverWait(self.driver, 2.0).until(
                EC.element_to_be_clickable((By.ID, f"checkbox-{option.lower()}"))
            )
            checkbox.click()
        
        submit_button: WebElement = WebDriverWait(self.driver, 2.0).until(
            EC.element_to_be_clickable((By.XPATH, "(//button)[4]"))
        )
        submit_button.click()
    
    def _main_page(self: "Scraper") -> None:
        pass

options: Set[str] = {"Algebra", 'Advanced Math', "Problem-Solving and Data Analysis", "Geometry and Trigonometry"}
skills: Dict[str, Set[str]] = {
    "Algebra": {
        "Linear equations in one variable", "Linear functions", "Linear equations in two variables", "Systems of two linear equations in two variables",
        "Linear inequalities in one or two variables"
    }, 
    "Advanced Math": {"Nonlinear functions", "Nonlinear equations in one variable and systems of equations in two variables", "Equivalent expressions"}, 
    "Problem-Solving and Data Analysis": {
        "Ratios, rates, proportional relationships, and units", "Percentages", "One-variable data: Distributions and measures of center and spread",
        "Two-variable data: Models and scatterplots", "Probability and conditional probability", "Inference from sample statistics and margin of error",
        "Evaluating statistical claims: Observational studies and experiments"
    }, 
    "Geometry and Trigonometry": {"Area and volume", "Lines, angles, and triangles", "Right triangles and trigonometry", "Circles"}
}
scraper: Scraper = Scraper(assessment="SAT", test="Math", options=options, skills=skills)
scraper.scrape()