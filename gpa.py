import streamlit as st
import pandas as pd

st.set_page_config(page_title="GPA & CGPA Calculator", page_icon="🎓", layout="centered")

st.title("🎓 Semester GPA & CGPA Tool")
st.write("""
Tell me your **marks for each subject** for the current semester to compute your **GPA**.
Optionally provide your **previous CGPA and total credit hours** to compute an updated **CGPA**.
""")

# --- Define function to convert marks to grade points ---
def marks_to_gpa(marks):
    if marks >= 85:
        return 4.0
    elif marks >= 80:
        return 3.7
    elif marks >= 75:
        return 3.3
    elif marks >= 70:
        return 3.0
    elif marks >= 65:
        return 2.7
    elif marks >= 61:
        return 2.3
    elif marks >= 58:
        return 2.0
    elif marks >= 55:
        return 1.7
    elif marks >= 50:
        return 1.0
    else:
        return 0.0

# small helper to show letter grade for a grade point
def gpa_to_letter(gpa):
    if gpa >= 3.7:
        return "A"
    if gpa >= 3.3:
        return "A-"
    if gpa >= 3.0:
        return "B+"
    if gpa >= 2.7:
        return "B"
    if gpa >= 2.3:
        return "B-"
    if gpa >= 2.0:
        return "C+"
    if gpa >= 1.7:
        return "C"
    if gpa >= 1.0:
        return "D"
    return "F"

# --- Input section ---
st.header("📘 Current Semester — Enter Marks")

num_subjects = st.number_input("Number of subjects this semester:", min_value=1, max_value=15, value=5, step=1)

subjects = []
total_points = 0.0
total_credits = 0

st.write("### Enter subject name, marks and credit hours for each subject")

for i in range(num_subjects):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        subject = st.text_input(f"Subject {i+1} name:", key=f"sub_{i}")
    with col2:
        marks = st.number_input(f"Marks ({subject or f'Subject {i+1}'})", 0, 100, 75, key=f"marks_{i}")
    with col3:
        credits = st.number_input(f"Credit hours", 1, 5, 3, key=f"credits_{i}")

    gpa = marks_to_gpa(marks)
    subjects.append({
        "Subject": subject or f"Subject {i+1}",
        "Marks": marks,
        "Credit Hours": int(credits),
        "Grade Point": round(gpa, 2),
        "Letter": gpa_to_letter(gpa),
        "Quality Points": round(gpa * credits, 2)
    })
    total_points += gpa * credits
    total_credits += int(credits)

# --- GPA Calculation ---
if total_credits > 0:
    current_gpa = total_points / total_credits
else:
    current_gpa = 0.0

# --- Display current GPA ---
st.subheader("📊 Current Semester GPA")
st.write(f"**Your GPA for this semester:** `{current_gpa:.2f}`")
st.caption(f"Total credit hours this semester: {int(total_credits)}  •  Total quality points: {round(total_points,2)}")

# --- Previous CGPA Section ---
st.header("📚 CGPA Update (Optional)")
st.write("If you have previous CGPA and total credit hours, enter them below to update your CGPA:")

col1, col2 = st.columns(2)
with col1:
    prev_cgpa = st.number_input("Previous CGPA", 0.0, 4.0, 0.0, step=0.01)
with col2:
    prev_credits = st.number_input("Total Credit Hours Completed Previously", 0, 200, 0, step=1)

# --- CGPA Calculation ---
if prev_credits > 0:
    new_cgpa = ((prev_cgpa * prev_credits) + (current_gpa * total_credits)) / (prev_credits + total_credits)
else:
    new_cgpa = current_gpa

st.subheader("🎯 Updated CGPA")
st.write(f"**Your updated CGPA:** `{new_cgpa:.2f}`")
st.caption(f"Combined total credits (previous + current): {int(prev_credits + total_credits)}")

# --- Show detailed table ---
df = pd.DataFrame(subjects)

# Add totals row for convenience using pd.concat (safe for modern pandas)
if not df.empty:
    totals = {
        "Subject": "Total",
        "Marks": "",
        "Credit Hours": int(total_credits),
        "Grade Point": "",
        "Letter": "",
        "Quality Points": round(total_points, 2)
    }
    df_totals = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
else:
    df_totals = df

st.write("### Detailed Results")
st.dataframe(df_totals, use_container_width=True)

st.success("✅ GPA and CGPA calculated successfully!")

# --- Estimated Next Semester (new section at the end) ---
st.markdown("---")
st.header("🔮 Estimate: Next Semester Projection")
st.write("Optionally estimate your **next semester GPA** and **projected CGPA** by entering planned subjects and expected marks.")

proj_subjects = st.number_input("Number of planned subjects for next semester:", min_value=0, max_value=15, value=0, step=1, key="proj_count")

proj_list = []
proj_total_points = 0.0
proj_total_credits = 0

if proj_subjects > 0:
    st.write("Enter expected marks and credits for each planned subject:")
    for k in range(proj_subjects):
        pcol1, pcol2 = st.columns([3, 1])
        with pcol1:
            pname = st.text_input(f"Planned Subject {k+1} name:", key=f"p_sub_{k}")
        with pcol2:
            pmarks = st.number_input(f"Marks ({pname or f'Planned {k+1}'})", 0, 100, 75, key=f"p_marks_{k}")
        pcredits = st.number_input(f"Credit hours for {pname or f'Planned {k+1}'}", 1, 5, 3, key=f"p_credits_{k}")

        pgpa = marks_to_gpa(pmarks)
        proj_list.append({
            "Subject": pname or f"Planned {k+1}",
            "Expected Marks": pmarks,
            "Credit Hours": int(pcredits),
            "Grade Point": round(pgpa, 2),
            "Letter": gpa_to_letter(pgpa),
            "Quality Points": round(pgpa * pcredits, 2)
        })
        proj_total_points += pgpa * pcredits
        proj_total_credits += int(pcredits)

    if proj_total_credits > 0:
        projected_sem_gpa = proj_total_points / proj_total_credits
    else:
        projected_sem_gpa = 0.0

    st.subheader("📈 Projected Next Semester GPA")
    st.write(f"**Projected GPA for next semester:** `{projected_sem_gpa:.2f}`")
    st.caption(f"Planned credits: {int(proj_total_credits)}  •  Planned total quality points: {round(proj_total_points,2)}")

    # Projected CGPA after next semester (use current combined credits as base)
    # Base CGPA uses prev_cgpa & prev_credits plus current semester already done
    base_total_credits = prev_credits + total_credits
    base_cgpa = new_cgpa  # this already includes current semester

    if (base_total_credits + proj_total_credits) > 0:
        combined_quality = base_cgpa * base_total_credits + projected_sem_gpa * proj_total_credits
        projected_overall_cgpa = combined_quality / (base_total_credits + proj_total_credits)
    else:
        projected_overall_cgpa = projected_sem_gpa

    st.subheader("🎯 Projected CGPA After Next Semester")
    st.write(f"**Projected CGPA after adding next semester:** `{projected_overall_cgpa:.2f}`")
    st.caption(f"Projected combined credits: {int(base_total_credits + proj_total_credits)}")

    # show projection details table using pd.concat
    pdf = pd.DataFrame(proj_list)
    if not pdf.empty:
        p_totals = {
            "Subject": "Total",
            "Expected Marks": "",
            "Credit Hours": int(proj_total_credits),
            "Grade Point": "",
            "Letter": "",
            "Quality Points": round(proj_total_points, 2)
        }
        pdf = pd.concat([pdf, pd.DataFrame([p_totals])], ignore_index=True)
    st.write("### Planned Semester Details")
    st.dataframe(pdf, use_container_width=True)
else:
    st.info("No planned subjects entered. Add planned subjects above to estimate next semester results.")

# --- Small suggestions (non-structural) ---
st.markdown("---")
st.caption("Suggestions: You can (1) change the grade scale in `marks_to_gpa`, (2) allow entering grade points directly, (3) export results to CSV, or (4) add visual trend charts. These changes are optional and don't alter the main input/output flow.")
