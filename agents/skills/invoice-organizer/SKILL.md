---
name: invoice-organizer
description: Automatically organizes invoices and receipts for tax preparation by reading messy files, extracting key information, renaming them consistently, and sorting them into logical folders. Turns hours of manual bookkeeping into minutes of automated organization.
---

# Invoice Organizer

This skill transforms chaotic folders of invoices, receipts, and financial documents into a clean, tax-ready filing system without manual effort.

## When to Use This Skill

- Preparing for tax season and need organized records
- Managing business expenses across multiple vendors
- Organizing receipts from a messy folder or email downloads
- Setting up automated invoice filing for ongoing bookkeeping
- Archiving financial records by year or category
- Reconciling expenses for reimbursement
- Preparing documentation for accountants

## What This Skill Does

1. **Reads Invoice Content**: Extracts information from PDFs, images, and documents:
   - Vendor/company name
   - Invoice number
   - Date
   - Amount
   - Product or service description
   - Payment method

2. **Renames Files Consistently**: Creates standardized filenames:
   - Format: `YYYY-MM-DD Vendor - Invoice - ProductOrService.pdf`
   - Examples: `2024-03-15 Adobe - Invoice - Creative Cloud.pdf`

3. **Organizes by Category**: Sorts into logical folders:
   - By vendor
   - By expense category (software, office, travel, etc.)
   - By time period (year, quarter, month)
   - By tax category (deductible, personal, etc.)

4. **Handles Multiple Formats**: Works with:
   - PDF invoices
   - Scanned receipts (JPG, PNG)
   - Email attachments
   - Screenshots
   - Bank statements

5. **Maintains Originals**: Preserves original files while organizing copies

## How to Use

### Basic Usage

Navigate to your messy invoice folder:
```
cd ~/Desktop/receipts-to-sort
```

Then ask Codex:
```
Organize these invoices for taxes
```

Or more specifically:
```
Read all invoices in this folder, rename them to
"YYYY-MM-DD Vendor - Invoice - Product.pdf" format,
and organize them by vendor
```

### Advanced Organization

```
Organize these invoices:
1. Extract date, vendor, and description from each file
2. Rename to standard format
3. Sort into folders by expense category (Software, Office, Travel, etc.)
4. Create a CSV spreadsheet with all invoice details for my accountant
```

## Common Organization Patterns

### By Vendor (Simple)
```
Invoices/
├── Adobe/
├── Amazon/
├── Google/
└── Microsoft/
```

### By Year and Category (Tax-Friendly)
```
Invoices/
├── 2023/
│   ├── Software/
│   ├── Hardware/
│   ├── Services/
│   └── Travel/
└── 2024/
    └── ...
```

### By Quarter (Detailed Tracking)
```
Invoices/
├── 2024/
│   ├── Q1/
│   │   ├── Software/
│   │   ├── Office/
│   │   └── Travel/
│   └── Q2/
│       └── ...
```

### By Tax Category (Accountant-Ready)
```
Invoices/
├── Deductible/
│   ├── Software/
│   ├── Office/
│   └── Professional-Services/
├── Partially-Deductible/
│   └── Meals-Travel/
└── Personal/
```
