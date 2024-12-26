from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar

class MonthlyLedger:
    def __init__(self):
        self.ledger = []
        self.recipient_name = ""
        self.payor_name = ""

    def set_names(self, recipient_name, payor_name):
        """
        Set the recipient and payor names.

        Args:
            recipient_name (str): Name of the recipient.
            payor_name (str): Name of the payor.
        """
        self.recipient_name = recipient_name
        self.payor_name = payor_name

    def calculate_monthly_ledger(self, monthly_accrual, start_date, end_date):
        """
        Calculate the monthly ledger based on accrual, start date, and end date.

        Args:
            monthly_accrual (float): The fixed amount accrued each month.
            start_date (str): The start date in YYYY-MM-DD format.
            end_date (str): The end date in YYYY-MM-DD format.
        """
        try:
            # Convert start and end dates to datetime objects
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")

        current_date = start_date
        beginning_balance = 0.0

        while current_date <= end_date:
            month = current_date.strftime("%B %Y")
            ending_balance = beginning_balance + monthly_accrual

            self.ledger.append(
                {
                    "Month": month,
                    "Beginning Balance": beginning_balance,
                    "Monthly Accrual": monthly_accrual,
                    "Amount Paid": 0.0,
                    "Ending Balance": ending_balance,
                }
            )

            beginning_balance = ending_balance
            current_date = (current_date + timedelta(days=32)).replace(day=1)

    def recalculate_balances(self):
        """
        Recalculate Beginning and Ending Balances for the ledger.
        """
        for i, entry in enumerate(self.ledger):
            if i == 0:
                entry["Beginning Balance"] = 0.0
            else:
                entry["Beginning Balance"] = self.ledger[i - 1]["Ending Balance"]

            entry["Ending Balance"] = (
                entry["Beginning Balance"] + entry["Monthly Accrual"] - entry["Amount Paid"]
            )

    def update_payments(self):
        """
        Update the ledger with payment details and recalculate balances.
        """
        for entry in self.ledger:
            print(f"Month: {entry['Month']}")
            while True:
                try:
                    amount_paid = float(input(f"Enter amount paid for {entry['Month']}: "))
                    if amount_paid < 0:
                        raise ValueError("Amount paid cannot be negative.")
                    break
                except ValueError as e:
                    print(f"Invalid input: {e}. Please try again.")
            entry["Amount Paid"] = amount_paid
            print(f"Updated {entry['Month']} payment to {amount_paid:.2f}")  # Debugging feedback

        self.recalculate_balances()
        print("\nPayments have been successfully updated.")  # Confirmation message

    def save_ledger_to_pdf(self, filename="ledger.pdf"):
        """
        Save the ledger to a PDF file in A4 size.

        Args:
            filename (str): The name of the output PDF file.
        """
        if not self.ledger:
            print("No entries in the ledger to save.")
            return

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        title = "Monthly Ledger"

        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, height - 50, title)

        # Add recipient and payor names
        c.setFont("Helvetica", 12)
        c.drawString(30, height - 80, f"Recipient Name: {self.recipient_name}")
        c.drawString(30, height - 100, f"Payor Name: {self.payor_name}")

        # Table headers
        headers = ["Month", "Beginning Balance", "Monthly Accrual", "Amount Paid", "Ending Balance"]
        data = [headers]

        # Table data
        for entry in self.ledger:
            data.append(
                [
                    entry["Month"],
                    f"{entry['Beginning Balance']:.2f}",
                    f"{entry['Monthly Accrual']:.2f}",
                    f"{entry['Amount Paid']:.2f}",
                    f"{entry['Ending Balance']:.2f}",
                ]
            )

        # Add summary
        total_paid = sum(entry["Amount Paid"] for entry in self.ledger)
        remaining_balance = self.ledger[-1]["Ending Balance"] if self.ledger else 0.0
        data.append(["Total", "", "", f"{total_paid:.2f}", f"{remaining_balance:.2f}"])

        # Define table style
        table = Table(data, colWidths=[120, 90, 90, 90, 90])
        style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
        table.setStyle(style)

        # Draw the table on the canvas
        table.wrapOn(c, width, height)
        table.drawOn(c, 30, height - 150 - len(self.ledger) * 25)

        # Footer
        c.setFont("Helvetica", 10)
        c.drawString(30, 30, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Save the PDF
        c.save()
        print(f"Ledger report saved as {filename}")

    def display_ledger(self):
        """Display the ledger in a formatted tabular view."""
        if not self.ledger:
            print("No entries in the ledger.")
            return

        headers = ["Month", "Beginning Balance", "Monthly Accrual", "Amount Paid", "Ending Balance"]
        print(f"{' | '.join(headers):<80}")
        print("-" * 80)

        for entry in self.ledger:
            print(
                f"{entry['Month']:<20} | {entry['Beginning Balance']:<15.2f} | "
                f"{entry['Monthly Accrual']:<15.2f} | {entry['Amount Paid']:<15.2f} | "
                f"{entry['Ending Balance']:<15.2f}"
            )

        # Print summary
        total_paid = sum(entry["Amount Paid"] for entry in self.ledger)
        remaining_balance = self.ledger[-1]["Ending Balance"] if self.ledger else 0.0
        print("\nSummary:")
        print(f"Total Amount Paid: {total_paid:.2f}")
        print(f"Remaining Balance: {remaining_balance:.2f}")


class GUIForLedger:
    def __init__(self, root, ledger):
        self.root = root
        self.ledger = ledger

        self.root.title("Monthly Ledger Application")

        tk.Label(root, text="Recipient Name:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(root, text="Payor Name:").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(root, text="Monthly Accrual:").grid(row=2, column=0, padx=5, pady=5)
        tk.Label(root, text="Start Date:").grid(row=3, column=0, padx=5, pady=5)
        tk.Label(root, text="End Date:").grid(row=4, column=0, padx=5, pady=5)

        self.recipient_entry = tk.Entry(root)
        self.payor_entry = tk.Entry(root)
        self.accrual_entry = tk.Entry(root)
        self.start_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)

        self.recipient_entry.grid(row=0, column=1, padx=5, pady=5)
        self.payor_entry.grid(row=1, column=1, padx=5, pady=5)
        self.accrual_entry.grid(row=2, column=1, padx=5, pady=5)
        self.start_date_entry.grid(row=3, column=1, padx=5, pady=5)
        self.end_date_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Button(root, text="Generate Ledger", command=self.generate_ledger).grid(row=5, column=0, pady=10, columnspan=2)
        tk.Button(root, text="Add Payments", command=self.add_payments).grid(row=6, column=0, pady=10, columnspan=2)
        tk.Button(root, text="Save to PDF", command=self.save_pdf).grid(row=7, column=0, pady=10, columnspan=2)

    def generate_ledger(self):
        try:
            recipient = self.recipient_entry.get()
            payor = self.payor_entry.get()
            accrual = float(self.accrual_entry.get())
            start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
            end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')

            self.ledger.set_names(recipient, payor)
            self.ledger.calculate_monthly_ledger(accrual, start_date, end_date)

            messagebox.showinfo("Success", "Ledger generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_payments(self):
        if not self.ledger.ledger:
            messagebox.showerror("Error", "Generate the ledger first!")
            return

        for entry in self.ledger.ledger:
            amount_paid = simpledialog.askfloat("Payment Entry", f"Enter amount paid for {entry['Month']}:")
            if amount_paid is not None:
                entry["Amount Paid"] = amount_paid

        self.ledger.recalculate_balances()
        messagebox.showinfo("Success", "Payments have been added successfully!")

    def save_pdf(self):
        try:
            self.ledger.save_ledger_to_pdf("ledger_report.pdf")
            messagebox.showinfo("Success", "Ledger saved to PDF successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    ledger = MonthlyLedger()
    app = GUIForLedger(root, ledger)
    root.mainloop()
