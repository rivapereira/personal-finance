import gradio as gr
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# EMI Calculation for multiple loans

def calculate_multiple_emis(income_df, loans_df, expense_df, short_goal, long_goal):
    try:
        income_df.columns = ["Source", "Amount"]
        income_df = income_df.dropna()
        income_df['Amount'] = income_df['Amount'].astype(float)
        income = income_df['Amount'].sum()
    except:
        return "⚠️ Please enter valid income values.", pd.DataFrame(), None

    try:
        loans_df.columns = ["Loan Name", "Loan Amount", "Interest Rate (%)", "Duration (Years)"]
    except:
        return "⚠️ Please check your loan data.", pd.DataFrame(), None

    try:
        expense_df.columns = ["Category", "Amount"]
        expense_df = expense_df.dropna()
        expense_df['Amount'] = expense_df['Amount'].astype(float)
        total_spending = expense_df['Amount'].sum()
    except:
        total_spending = 0

    if income <= 0 or loans_df.empty:
        return "⚠️ Please enter your income and at least one valid loan.", pd.DataFrame(), None

    total_emi = 0
    breakdown = []

    for _, row in loans_df.iterrows():
        try:
            P = float(row['Loan Amount'])
            R = float(row['Interest Rate (%)']) / 12 / 100
            N = int(row['Duration (Years)']) * 12
            if P <= 0 or R < 0 or N <= 0:
                continue
            EMI = (P * R * (1 + R)**N) / ((1 + R)**N - 1)
            total_payment = EMI * N
            total_interest = total_payment - P
            breakdown.append({
                'Loan': row['Loan Name'],
                'EMI': f"AED {EMI:,.2f}",
                'Total Interest': f"AED {total_interest:,.2f}",
                'Total Payment': f"AED {total_payment:,.2f}"
            })
            total_emi += EMI
        except:
            continue

    remaining_budget = income - total_emi - total_spending
    breakdown_df = pd.DataFrame(breakdown)
    result = f"""
### 🎯 Financial Goals
- **Short-Term**: {short_goal or 'Not Set'}
- **Long-Term**: {long_goal or 'Not Set'}

💸 **Total Monthly EMI**: AED {total_emi:,.2f}  
🧾 **Spending**: AED {total_spending:,.2f}  
✅ **Remaining monthly budget**: AED {remaining_budget:,.2f}
"""

    # Styled pie chart using seaborn color palette + professional styling
    fig, ax = plt.subplots()
    labels = ['EMI', 'Spending', 'Leftover']
    values = [total_emi, total_spending, max(remaining_budget, 0)]
    colors = sns.color_palette("pastel")
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 12, 'weight': 'bold'}
    )

    for text in texts:
        text.set_fontsize(12)
        text.set_weight('bold')

    for autotext in autotexts:
        autotext.set_color('black')

    ax.set_title("📊 Monthly Financial Distribution", fontsize=16, fontweight='bold')
    ax.axis('equal')
    fig.set_facecolor("white")

    return result, breakdown_df, fig

# Income Ledger Calculation
def calculate_income_ledger(income_df):
    try:
        income_df.columns = ["Source", "Amount"]
        income_df = income_df.dropna()
        income_df['Amount'] = income_df['Amount'].astype(float)
        total = income_df['Amount'].sum()
        return f"💰 Total Monthly Income: AED {total:,.2f}"
    except:
        return "⚠️ Please enter valid numbers."

# Expense Tracker

def calculate_expense_ledger(expense_df, income_df):
    try:
        expense_df.columns = ["Category", "Amount"]
        expense_df = expense_df.dropna()
        expense_df['Amount'] = expense_df['Amount'].astype(float)
        total_expenses = expense_df['Amount'].sum()

        income_df.columns = ["Source", "Amount"]
        income_df = income_df.dropna()
        income_df['Amount'] = income_df['Amount'].astype(float)
        total_income = income_df['Amount'].sum()

        remaining = total_income - total_expenses
        return f"💸 Total Monthly Spending: AED {total_expenses:,.2f}  \n🧾 Remaining after spending: AED {remaining:,.2f}"
    except:
        return "⚠️ Please enter valid numbers."

def fill_mock_income():
    return pd.DataFrame({"Source": ["Job", "Freelance"], "Amount": [5000, 1500]})

def fill_mock_loans():
    return pd.DataFrame({
        "Loan Name": ["Car Loan", "Phone EMI"],
        "Loan Amount": [30000, 4000],
        "Interest Rate (%)": [7.5, 10.0],
        "Duration (Years)": [5, 1]
    })

def fill_mock_expenses():
    return pd.DataFrame({
        "Category": ["Rent", "Groceries", "Transport"],
        "Amount": [1200, 400, 300]
    })

with gr.Blocks(theme="NoCrypt/miku@1.2.1") as demo:
    gr.Markdown("## 💼 Personal Finance Dashboard")

    with gr.Tabs():
        with gr.TabItem("🎯 Goals"):
            short_goal = gr.Textbox(label="Short-Term Goal", lines=2, placeholder="e.g. Pay off credit card")
            long_goal = gr.Textbox(label="Long-Term Goal", lines=2, placeholder="e.g. Buy a house")

        with gr.TabItem("📈 Income Ledger"):
            income_df = gr.Dataframe(value=pd.DataFrame(columns=["Source", "Amount"]),
                                     datatype=["str", "number"],
                                     row_count=4,
                                     col_count=(2, "fixed"),
                                     interactive=True)
            income_output = gr.Markdown()
            income_btn = gr.Button("Calculate Income")
            mock_income = gr.Button("Add Mock Income")
            income_btn.click(fn=calculate_income_ledger, inputs=income_df, outputs=income_output)
            mock_income.click(fn=fill_mock_income, outputs=income_df)

        with gr.TabItem("📊 Loan + Spending Ledger"):
            loans_df = gr.Dataframe(value=pd.DataFrame(columns=["Loan Name", "Loan Amount", "Interest Rate (%)", "Duration (Years)"]),
                                    datatype=["str", "number", "number", "number"],
                                    row_count=3,
                                    col_count=(4, "fixed"),
                                    interactive=True)
            mock_loans = gr.Button("Add Mock Loans")

            expense_df = gr.Dataframe(value=pd.DataFrame(columns=["Category", "Amount"]),
                                      datatype=["str", "number"],
                                      row_count=5,
                                      col_count=(2, "fixed"),
                                      interactive=True)
            mock_expenses = gr.Button("Add Mock Expenses")

            income_copy_df = gr.Dataframe(value=pd.DataFrame(columns=["Source", "Amount"]),
                                          datatype=["str", "number"],
                                          row_count=4,
                                          col_count=(2, "fixed"),
                                          interactive=True,
                                          visible=False)

            spend_btn = gr.Button("Calculate Spending")
            spend_output = gr.Markdown()

            spend_btn.click(fn=calculate_expense_ledger, inputs=[expense_df, income_copy_df], outputs=spend_output)
            mock_loans.click(fn=fill_mock_loans, outputs=loans_df)
            mock_expenses.click(fn=fill_mock_expenses, outputs=expense_df)

        with gr.TabItem("📋 Results"):
            emi_btn = gr.Button("Get Breakdown")
            results = gr.Markdown()
            emi_breakdown = gr.Dataframe(interactive=False)
            pie = gr.Plot()

            emi_btn.click(fn=calculate_multiple_emis,
                          inputs=[income_df, loans_df, short_goal, long_goal],
                          outputs=[results, emi_breakdown, pie])

    gr.Markdown("---\n✍️ Built with ❤️ by Riva Pereira :3")

demo.launch()
