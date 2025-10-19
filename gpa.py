import streamlit as st
import pandas as pd
from typing import List, Tuple

st.set_page_config(page_title="GPA & CGPA Calculator", layout="centered")

st.title("📚 Advanced GPA & CGPA Calculator")
st.markdown(
    """
This app lets you enter course names, marks (percentage), and credit hours for a semester, calculates the semester GPA, and updates your CGPA when you provide previous CGPA/credits. 
You can also project future-semester results by entering planned courses/expected marks.

**How marks are converted to grade points:**

- 90 - 100 : 4.00
- 85 - 89  : 3.70
- 80 - 84  : 3.30
- 75 - 79  : 3.00
- 70 - 74  : 2.70
- 65 - 69  : 2.30
- 60 - 64  : 2.00
- 55 - 59  : 1.70
- 50 - 54  : 1.00
- 0  - 49  : 0.00

(If you want a different mapping, modify the `percent_to_gradepoint` function.)
"""
)

# ----------------------- Helper functions -----------------------
def percent_to_gradepoint(p: float) -> float:
    """Convert percentage marks into a 4.0-scale grade point using a common mapping."""
    if p is None:
        return 0.0
    try:
        p = float(p)
    except Exception:
        return 0.0
    if p >= 90:
        return 4.00
    if p >= 85:
        return 3.70
    if p >= 80:
        return 3.30
    if p >= 75:
        return 3.00
    if p >= 70:
        return 2.70
    if p >= 65:
        return 2.30
    if p >= 60:
        return 2.00
    if p >= 55:
        return 1.70
    if p >= 50:
        return 1.00
    return 0.00

def gradepoint_to_letter(g: float) -> str:
    if g >= 3.7:
        return "A"
    if g >= 3.3:
        return "A-"
    if g >= 3.0:
        return "B+"
    if g >= 2.7:
        return "B"
    if g >= 2.3:
        return "B-"
    if g >= 2.0:
        return "C+"
    if g >= 1.7:
        return "C"
    if g >= 1.0:
        return "D"
    return "F"

def compute_gpa(rows: List[Tuple[str, float, float]]) -> Tuple[float, float]:
    """
    rows: list of tuples (course_name, marks_percentage, credits)
    Returns: (semester_gpa, total_credits)
    """
    total_points = 0.0
    total_credits = 0.0
    for name, marks, credits in rows:
        try:
            gp = percent_to_gradepoint(float(marks))
            cred = float(credits)
        except Exception:
            gp = 0.0
            cred = 0.0
        total_points += gp * cred
        total_credits += cred
    if total_credits == 0:
        return 0.0, 0.0
    sem_gpa = total_points / total_credits
    return round(sem_gpa, 3), round(total_credits, 2)

def update_cgpa(prev_cgpa: float, prev_credits: float, sem_gpa: float, sem_credits: float) -> float:
    """
    Weighted average of previous CGPA and current semester GPA
    """
    try:
        prev_cgpa = float(prev_cgpa)
        prev_credits = float(prev_credits)
        sem_gpa = float(sem_gpa)
        sem_credits = float(sem_credits)
    except Exception:
        return 0.0
    total_credits = prev_credits + sem_credits
    if total_credits == 0:
        return 0.0
    combined = (prev_cgpa * prev_credits + sem_gpa * sem_credits) / total_credits
    return round(combined, 3)

# ----------------------- Semester input -----------------------
st.header("Step 1 — Current Semester details")

num_courses = st.number_input("Number of courses in this semester", min_value=1, max_value=50, value=4, step=1)

st.markdown("Enter course name, obtained marks (%) and credit hours for each course:")

courses = []
for i in range(int(num_courses)):
    with st.expander(f"Course #{i+1}", expanded=(i < 4)):
        c1, c2, c3 = st.columns([4,2,2])
        course_name = c1.text_input("Course name", value=f"Course_{i+1}", key=f"name_{i}")
        marks = c2.number_input("Marks (%)", min_value=0.0, max_value=100.0, value=75.0, key=f"marks_{i}")
        credits = c3.number_input("Credit hours", min_value=0.0, max_value=10.0, value=3.0, key=f"credits_{i}")
        courses.append((course_name, marks, credits))

if st.button("Calculate GPA for current semester"):
    sem_gpa, sem_credits = compute_gpa(courses)
    st.success(f"Semester GPA: {sem_gpa}  (based on {sem_credits} credit hours)")
    st.info(f"Approximate letter grade for GPA: {gradepoint_to_letter(sem_gpa)}")
    # show a nice table
    df_rows = []
    for name, marks, credits in courses:
        gp = percent_to_gradepoint(marks)
        df_rows.append({"Course": name, "Marks (%)": marks, "Credits": credits, "Grade Point": gp, "Letter": gradepoint_to_letter(gp)})
    df = pd.DataFrame(df_rows)
    st.table(df)

    # CGPA update
    st.markdown("### Update CGPA (optional)")
    prev_cgpa = st.number_input("Previous CGPA (enter 0 if none)", min_value=0.0, max_value=4.0, value=0.0, step=0.01, key="prev_cgpa")
    prev_credits = st.number_input("Total completed credits before this semester", min_value=0.0, value=0.0, step=1.0, key="prev_credits")
    if st.button("Update CGPA with this semester"):
        new_cgpa = update_cgpa(prev_cgpa, prev_credits, sem_gpa, sem_credits)
        st.success(f"New CGPA: {new_cgpa} (Total credits after update: {round(prev_credits + sem_credits, 2)})")

    # Offer projection for future semester(s)
    st.markdown("---")
    st.markdown("### Project future semester (estimate)")
    st.write("Enter number of planned courses in a future semester to estimate projected CGPA after that semester.")
    proj_courses = st.number_input("Number of planned courses for next semester", min_value=0, max_value=50, value=0, step=1, key="proj_num")

    proj_list = []
    for j in range(int(proj_courses)):
        with st.expander(f"Planned Course #{j+1}", expanded=(j<3)):
            p1, p2, p3 = st.columns([4,2,2])
            pname = p1.text_input("Planned course name", value=f"Planned_{j+1}", key=f"pname_{j}")
            pmarks = p2.number_input("Expected marks (%)", min_value=0.0, max_value=100.0, value=75.0, key=f"pmarks_{j}")
            pcredits = p3.number_input("Credit hours", min_value=0.0, max_value=10.0, value=3.0, key=f"pcredits_{j}")
            proj_list.append((pname, pmarks, pcredits))

    if st.button("Estimate CGPA after planned semester"):
        sem_gpa_proj, sem_credits_proj = compute_gpa(proj_list)
        st.info(f"Projected GPA for planned semester: {sem_gpa_proj} (Credits: {sem_credits_proj})")
        # need previous data to compute combined CGPA
        prev_cgpa2 = st.number_input("Previous CGPA to base projection on (enter 0 if none)", min_value=0.0, max_value=4.0, value=0.0, step=0.01, key="proj_prev_cgpa")
        prev_credits2 = st.number_input("Previous total credits before planned semester", min_value=0.0, value=0.0, step=1.0, key="proj_prev_credits")
        projected_cgpa = update_cgpa(prev_cgpa2, prev_credits2, sem_gpa_proj, sem_credits_proj)
        st.success(f"Projected CGPA after planned semester: {projected_cgpa} (Projected total credits: {round(prev_credits2 + sem_credits_proj,2)})")

# ----------------------- Quick utilities -----------------------
st.sidebar.header("Utilities & Options")
st.sidebar.write("You can change the grade mapping in the source code if your institution uses another scheme.")
if st.sidebar.button("Show example dataset"):
    ex = pd.DataFrame([
        {"Course": "Math", "Marks (%)": 92, "Credits": 3, "Grade Point": percent_to_gradepoint(92)},
        {"Course": "Physics", "Marks (%)": 85, "Credits": 3, "Grade Point": percent_to_gradepoint(85)},
        {"Course": "Chemistry", "Marks (%)": 78, "Credits": 3, "Grade Point": percent_to_gradepoint(78)},
    ])
    st.sidebar.table(ex)

st.markdown("---")
st.caption("Made with ❤️. Modify the `percent_to_gradepoint` mapping if your university uses a different scale.")
