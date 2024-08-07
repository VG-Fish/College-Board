# A Python Library to scrape CollegeBoard
## Things to Note: 
- Only the Firefox browser is supported. You must have geckodriver installed. This will be changed in the future.
- Very long questions or answers aren't fully captured. This will be changed in the future.
- The scraper is also quite slow, the performance will be improved in future releases.
- More convenience functions will be added to the `Scraper` class along with ways to change some parameters after they've already been initialized.

## Docs:
### Scraper Class
An example of creating the CollegeBoard SAT Suite Question Bank webpage scraper:
```python
from college_board_scraper.core import Scraper
scraper = Scraper(
    assessment="SAT", 
    test="Math",
    options=Scraper.valid_math_options,
    difficulties={"Easy", "Medium", "Hard"},
    skills=Scraper.valid_math_skills,
    exclude_active_questions=True
)
```
What this does is create a scraper that will select the Easy, Medium, and Hard questions that fall under all of the math skills and options of Math portion of 
the SAT test (which is all of questions). Additionally, it will exclude any questions present in the practice digital SAT tests released by CollegeBoard.

Next, to get the questions, call the `scraper.scrape()` method. The arguments are `amount`, which is the amount of questions that should be scraped from the 
beginning, or (this is an optional parameter; default is False) supply the `save_images` parameter, which will save the question and answer pngs to their respective directories. 
If `save_images` is False,
`scraper.scrape()` will return a List of the question number and the question and answer pngs (type is `List[Tuple[int, Tuple[PngImageFile, PngImageFile]]]`).

### Valid Arguments for the Scraper Class
Here are some valid arguments for the Scraper Class when you initialize it.
```python
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
```
You can use all of these using `Scraper.[PARAMETER]`. For the arguments that are type `Set` or `Dict`, you can supply any valid subset to the argument. For example, for the
`valid_math_options` argument, you may supply `{"Advanced Math", "Problem-Solving and Data Analysis", "Algebra"}`. Attempting to supply invalid arguments will result in a `ValueError()`.
Look at the error message to see what you have done wrong. For the arguments of type `Tuple`, you must choose one of the values.
If there are any bugs, create a Github Issue detailing your error, and how you caused it.

### ScraperAmount Class
To declare the ScraperAmount Helper Class, do: `from college_board_scraper.helpers import ScraperAmount`.
If you want to scrape all of the questions, you can supply the `ScraperAmount.ALL` to the amount parameter. In the future, you can use `ScraperAmount.RANDOM` to get a random amount of random questions.
