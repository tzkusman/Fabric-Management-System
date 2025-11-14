# Ledger System Documentation

## Overview
The Fabric Inventory Management System now includes a comprehensive **Ledger System** with advanced filtering capabilities for both purchases and sales transactions. This feature provides Excel-like reporting and filtering to help you track and analyze your business transactions efficiently.

## Features

### 1. Purchase Ledger (`/ledger/purchases`)
Track all fabric purchases with advanced filtering:

**Filters Available:**
- **Supplier**: Filter by specific supplier
- **Fabric Type**: Search by fabric type (partial match)
- **Fabric Code**: Filter by fabric code (partial match)
- **Date Range**: From date to To date
- **General Search**: Search across all fields (supplier name, fabric type, code, composition)

**Summary Information:**
- Total number of transactions
- Total quantity purchased (meters)
- Total amount spent

**Export**: CSV export with all filtered data

### 2. Sales Ledger (`/ledger/sales`)
Track all fabric sales with advanced filtering:

**Filters Available:**
- **Customer**: Filter by specific customer
- **Company**: Filter by your company (for multi-company operations)
- **Fabric Type**: Search by fabric type (partial match)
- **Fabric Code**: Filter by fabric code (partial match)
- **Tax Applied**: Filter by transactions with/without tax
- **Date Range**: From date to To date
- **General Search**: Search across all fields (customer name, fabric type, code, composition)

**Summary Information:**
- Total number of transactions
- Total quantity sold (meters)
- Subtotal (before tax)
- Total tax collected
- Grand total (with tax)

**Export**: CSV export with all filtered data
**Direct Access**: View invoice PDF for each sale

### 3. Customer Summary (`/ledger/customer-summary`)
Get a consolidated view of all customer transactions:

**Features:**
- Group sales by customer
- Transaction count per customer
- Total quantity sold to each customer
- Total revenue from each customer
- Date range filtering
- Top 5 customers by revenue
- Top 5 customers by quantity
- Click to view detailed transactions for any customer

### 4. Supplier Summary (`/ledger/supplier-summary`)
Get a consolidated view of all supplier transactions:

**Features:**
- Group purchases by supplier
- Transaction count per supplier
- Total quantity purchased from each supplier
- Total amount spent with each supplier
- Date range filtering
- Top 5 suppliers by spending
- Top 5 suppliers by quantity
- Click to view detailed transactions for any supplier

## Use Cases

### Example 1: Customer Ledger for Date Range
**Scenario**: Get all sales to "ABC Textiles" from August 2025 to January 2026

**Steps:**
1. Navigate to Sales Ledger (`/ledger/sales`)
2. Select "ABC Textiles" from Customer dropdown
3. Set Date From: `2025-08-01`
4. Set Date To: `2026-01-31`
5. Click "Apply Filters"
6. Export to Excel if needed

### Example 2: Supplier Purchase Report
**Scenario**: Get all purchases from "Cotton Mills Ltd" in Q4 2025

**Steps:**
1. Navigate to Purchase Ledger (`/ledger/purchases`)
2. Select "Cotton Mills Ltd" from Supplier dropdown
3. Set Date From: `2025-10-01`
4. Set Date To: `2025-12-31`
5. Click "Apply Filters"
6. View summary totals and export

### Example 3: Tax Analysis
**Scenario**: Find all sales without tax in a specific period

**Steps:**
1. Navigate to Sales Ledger (`/ledger/sales`)
2. Set Date Range
3. Select "Without Tax" from Tax Applied dropdown
4. Click "Apply Filters"
5. Review all non-taxed transactions

### Example 4: Fabric-specific Tracking
**Scenario**: Track all "Cotton" fabric transactions

**Steps:**
1. Navigate to Purchase or Sales Ledger
2. Enter "Cotton" in Fabric Type field
3. Optionally add date range
4. Click "Apply Filters"
5. View all cotton fabric transactions

## Database Functions

### Purchase Ledger Function
```python
crud.get_purchase_ledger(
    db, 
    supplier_id=None,
    fabric_type=None,
    fabric_code=None,
    date_from=None,
    date_to=None,
    search_query=None
)
```

### Sales Ledger Function
```python
crud.get_sale_ledger(
    db,
    customer_id=None,
    company_id=None,
    fabric_type=None,
    fabric_code=None,
    date_from=None,
    date_to=None,
    search_query=None,
    apply_tax_filter=None
)
```

### Customer Summary Function
```python
crud.get_customer_ledger_summary(
    db, 
    date_from=None, 
    date_to=None
)
```

### Supplier Summary Function
```python
crud.get_supplier_ledger_summary(
    db, 
    date_from=None, 
    date_to=None
)
```

## API Endpoints

### Web Routes (HTML)
- `GET /ledger/purchases` - Purchase ledger with filters
- `GET /ledger/sales` - Sales ledger with filters
- `GET /ledger/customer-summary` - Customer summary report
- `GET /ledger/supplier-summary` - Supplier summary report

### Export Routes (CSV)
- `GET /export/ledger/purchases.csv` - Export filtered purchases
- `GET /export/ledger/sales.csv` - Export filtered sales

All export routes accept the same query parameters as their corresponding web routes.

## UI Features

### Advanced Filter Panel
- Easy-to-use dropdown menus for customers, suppliers, companies
- Date pickers for precise date range selection
- Text search for flexible filtering
- Reset button to clear all filters
- Export button preserves current filters

### Summary Cards
- Visual display of key metrics
- Color-coded for easy identification
- Real-time calculation based on filters

### Data Table
- Sortable columns
- Sticky header (stays visible while scrolling)
- Responsive design
- Direct action buttons (view invoice, view details)

### Navigation
- Quick links between related views
- Breadcrumb navigation
- Direct access from main menu dropdown

## Tips for Best Results

1. **Date Ranges**: Use date filters for period-specific reports (monthly, quarterly, yearly)

2. **Combined Filters**: Combine multiple filters for precise results (e.g., Customer + Date Range + Fabric Type)

3. **Search Function**: Use the general search when you're not sure which field contains your search term

4. **Export**: Always export important reports for record-keeping and Excel analysis

5. **Summary Views**: Start with summary views to identify top customers/suppliers, then drill down to details

6. **Regular Reports**: Run customer/supplier summaries regularly to track business relationships

## Future Enhancements (Roadmap)

- PDF export for ledgers
- Print-optimized layouts
- Email reports directly from the system
- Scheduled automatic reports
- Charts and graphs for visual analysis
- Comparison reports (period vs period)
- Outstanding/pending transaction tracking

## Support

For issues or feature requests related to the ledger system, contact:
- WhatsApp: 03362793950
- System: Powered by TzkSolution
