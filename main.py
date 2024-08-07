from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement # imported for type hint
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
from typing import Tuple, Set, Dict, List
from itertools import chain

class Scraper():
    # Init Page Options
    valid_assessments: Tuple[str] = ("SAT", "PSAT/NMSQT & PSAT 10", "PSAT 8/9")
    valid_tests: Tuple[str] = ("Reading and Writing", "Math")

    valid_reading_and_writing_options: Set[str] = {"Information and Ideas", "Craft and Structure", "Expression of Ideas", "Standard English Conventions"}
    valid_math_options: Set[str] = {"Algebra", "Advanced Math", "Problem-Solving and Data Analysis", "Geometry and Trigonometry"}

    # Main Page options
    valid_difficulty_options: Set[str] = {"Easy", "Medium", "Hard"}

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
            difficulty: Set[str] | None = None, 
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
            raise ValueError(f"options (you inputted {self.options}) must be a valid subset of: {Scraper.valid_reading_and_writing_options}.")
        elif self.test == "Math" and not self.options.issubset(Scraper.valid_math_options):
            raise ValueError(f"options (you inputted {self.options}) must be a valid subset of: {Scraper.valid_math_options}.")

        self.difficulty: Set[str] | None = difficulty
        if difficulty is not None and not self.difficulty.issubset(Scraper.valid_difficulty_options):
            raise ValueError(f"difficulty (you inputted {self.difficulty}) must be a valid subset of: {Scraper.valid_difficulty_options}.")

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
            raise ValueError(f"skills keys (you inputted {self.skills.keys()}) must be a valid subset of: {self.options}.")
            
        for option in self.options:
            if option not in self.skills:
                raise ValueError(f"{option} is not found in {self.options}.")
            if not self.skills[option].issubset(valid_skills[option]):
                raise ValueError(
                    f"one of skills value (you inputted {self.skills[option]}) is not a valid subset of: {valid_skills[option]}."
                )

    def _click_away(self: "Scraper"):
        self.driver.find_element(By.TAG_NAME, 'body').click()
    
    def scrape(self: "Scraper", amount: int = 0) -> None:
        self._go_to_main_page()
        self._set_up_main_page()
        self._scrape_main_page(amount)

    def _scrape_main_page(self: "Scraper", amount: int = 0) -> None:
        self.driver.implicitly_wait(1.0)
        
        div_text_element: WebElement = WebDriverWait(self.driver, 2.0).until(
            EC.visibility_of_element_located((By.XPATH, "(//*[@class='table-header cb-padding-top-24 cb-border-top cb-border-top-2'])"))
        )
        p_text_element: WebElement = div_text_element.find_element(By.TAG_NAME, "p")
        text_element: WebElement = p_text_element.find_element(By.TAG_NAME, "span")
        total_amount_of_buttons: int = int(text_element.get_attribute("innerHTML"))

        # Iterates until range(amount) reaches the end
        for i in range(1, min(amount, total_amount_of_buttons) + 1):
            try:
                # Wait for the specific button to be clickable
                element: WebElement = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"(//*[@class='cb-btn square cb-roboto cb-btn-naked view-question-button'])[{i}]"))
                )
                
                # Attempt to click the button
                try:
                    element.click()
                except ElementClickInterceptedException:
                    # If the overlay is present, wait for it to disappear
                    WebDriverWait(self.driver, 10.0).until(
                        EC.invisibility_of_element_located((By.CLASS_NAME, "cb-modal-overlay"))
                    )
                    element.click()
                
                close_button: WebElement = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "(//*[@class='cb-btn square cb-roboto cancel-btn cb-btn cb-roboto cb-margin-left-24'])"))
                )

                # Click Close Button
                try:
                    close_button.click()
                except ElementClickInterceptedException:
                    # If the overlay is present, wait for it to disappear
                    WebDriverWait(self.driver, 10.0).until(
                        EC.invisibility_of_element_located((By.CLASS_NAME, "cb-modal-overlay"))
                    )
                    close_button.click()
                
                # Wait for any animations or page changes to complete
                WebDriverWait(self.driver, 10.0).until(
                    EC.staleness_of(close_button)
                )
            
            except (TimeoutException, StaleElementReferenceException) as e:
                print(f"Error processing button {i}: {str(e)}")
                continue
            

    # Handles all introductory options
    def _go_to_main_page(self: "Scraper") -> None:
        self.driver.get("https://satsuitequestionbank.collegeboard.org/digital/search")

        search_assessment_element: Select = Select(WebDriverWait(self.driver, 5.0).until(
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

    # Clicks all main page options
    def _set_up_main_page(self: "Scraper") -> None:
        if self.difficulty:
            difficulty_a_dropdown: WebElement = WebDriverWait(self.driver, 2.0).until(
                EC.element_to_be_clickable((By.ID, "dropdown1"))
            )
            difficulty_a_dropdown.click()

            for option in self.difficulty:
                difficulty_dropdown: WebElement = WebDriverWait(self.driver, 2.0).until(
                    EC.element_to_be_clickable((By.ID, option[0]))
                )
                difficulty_dropdown.click()
            
            # Click on the body to close the dropdown
            self._click_away()
        
        if self.skills:
            skills_a_dropdown: WebElement = WebDriverWait(self.driver, 2.0).until(
                EC.element_to_be_clickable((By.ID, "dropdown2"))
            )
            skills_a_dropdown.click()

            for skill in chain(*self.skills.values()):
                option_checkbox: WebElement = WebDriverWait(self.driver, 2.0).until(
                    EC.element_to_be_clickable((By.ID, skill))
                )
                option_checkbox.click()
            
            self._click_away()
        
        if self.exclude_active_questions:
            exclude_action_questions_checkbox: WebElement = WebDriverWait(self.driver, 2.0).until(
                EC.element_to_be_clickable((By.ID, "apricot_check_4"))
            )
            exclude_action_questions_checkbox.click()

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
scraper: Scraper = Scraper(assessment="SAT", test="Math", options=options)
scraper.scrape(10)