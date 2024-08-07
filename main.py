from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement # imported for type hint
from typing import Tuple, Set

class Scraper():
    # Init Page Options
    valid_assessments: Tuple[str] = ("SAT", "PSAT/NMSQT & PSAT 10", "PSAT 8/9")
    valid_tests: Tuple[str] = ("Reading and Writing", "Math")
    valid_reading_and_writing_options: Set[str] = {"Information and Ideas", "Craft and Structure", "Expression of Ideas", "Standard English Conventions"}
    valid_math_options: Set[str] = {"Algebra", "Advanced Math", "Problem-Solving and Data Analysis", "Geometry and Trigonometry"}

    # Main Page options
    valid_difficulty_options: Tuple[str] = ["Easy", "Medium", "Hard"]
    valid_reading_and_writing_skills: Set[str]

    def __init__(
            self: "Scraper", 
            assessment: str, 
            test: str, 
            options: Set[str],
            difficulty: str,
            skills: Set[str],
            exclude_active_questions: bool = False
        ) -> None:
        self.assessment: str = assessment
        if self.assessment not in Scraper.valid_assessments:
            raise ValueError(f"assessment (you inputted f{self.assessment}) must be one of these three options: {Scraper.valid_assessments}.")
        
        self.test: str = test
        if self.test not in Scraper.valid_tests:
            raise ValueError(f"test (you inputted f{self.test}) must be one of these two options: {Scraper.valid_tests}.")
        
        self.options: Set[str] = options
        if len(self.options) == 0:
            raise ValueError(f"Length og options must not be zero. Add these options: {Scraper.valid_reading_and_writing_options}")
        elif self.test == "Reading and Writing" and not self.options.issubset(Scraper.valid_reading_and_writing_options):
            raise ValueError(f"options (you inputted f{self.options}) must be a valid subset of {Scraper.valid_reading_and_writing_options}.")
        elif self.test == "Math" and not self.options.issubset(Scraper.valid_math_options):
            raise ValueError(f"options ((you inputted f{self.options})) must be a valid subset of {Scraper.valid_math_options}.")
    
        self.driver: webdriver.Firefox = webdriver.Firefox()

    def scrape(self: "Scraper") -> None:
        self._go_to_main_page()
        self._main_page()

    # Handles all introductory options
    def _go_to_main_page(self: "Scraper"):
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
    
    def _main_page(self: "Scraper"):
        pass


options: Set[str] = {"Algebra", "Advanced Math", "Problem-Solving and Data Analysis", "Geometry and Trigonometry"}
scraper: Scraper = Scraper(assessment="SAT", test="Math", options=options)
scraper.scrape()