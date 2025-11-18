# 📦 Fabric Inventory Manager - Portable Edition

## Quick Start (30 seconds)

### Windows Users
1. **Double-click** `FabricManager.exe`
2. **Wait** 3-5 seconds for browser to open
3. **Done!** Application is ready

### First Time Setup
- Database created automatically ✅
- Tables initialized automatically ✅
- Browser opens to `http://127.0.0.1:8000` ✅

---

## 🎯 What You Get

- ✅ **Complete Fabric Inventory System**
- ✅ **Purchase & Sales Management**
- ✅ **Automatic Tax Calculation (18%)**
- ✅ **Stock Tracking with FIFO Valuation**
- ✅ **Payment Tracking (Partial/Pending/Paid)**
- ✅ **Supplier & Customer Management**
- ✅ **Profit/Loss Reports**
- ✅ **CSV Export**
- ✅ **Database Backup/Restore**

---

## 💻 System Requirements

### Minimum
- **OS:** Windows 7, Windows 10, Windows 11
- **RAM:** 512 MB
- **Disk:** 300 MB free space
- **Display:** 1024x768 or higher

### Recommended
- **OS:** Windows 10 or later
- **RAM:** 2 GB
- **Disk:** 1 GB free space
- **Display:** 1920x1080 or higher

---

## 📚 How to Use

### Adding Data

#### Register a Company
1. Click **"Register Company"** on Dashboard
2. Enter company details (name, phone, tax number, etc.)
3. Click **"Register"**

#### Add Supplier
1. Click **"Add Supplier"** from menu
2. Enter supplier name and contact
3. Click **"Add Supplier"**

#### Add Customer
1. Click **"Add Customer"** from menu
2. Enter customer name and contact
3. Click **"Add Customer"**

#### Record a Purchase
1. Click **"Add Purchase"** from menu
2. Select supplier, fabric type, quantity, price
3. Set payment method and status
4. Click **"Record Purchase"**

#### Record a Sale
1. Click **"Add Sale"** from menu
2. Select company, customer, fabric, quantity, price
3. Choose tax rate (18% default)
4. Set payment status
5. Click **"Record Sale"**

### Viewing Reports

#### Stock Summary
- **Menu:** Reports → Stock
- Shows current inventory with valuations
- Uses FIFO costing method

#### Purchase History
- **Menu:** Reports → Purchases
- All purchase transactions with supplier details

#### Sales History
- **Menu:** Reports → Sales
- All sales with tax breakdown

#### Profit/Loss
- **Menu:** Reports → Profit/Loss
- Total revenue vs cost summary

#### Ledger Reports
- **Menu:** Ledger → Purchase/Sales/Customer/Supplier
- Detailed filtered ledgers with search options

### Payment Management

#### Record a Customer Payment
1. Go **Payments → Pending Payments**
2. Click **"Record Payment"** on sale with balance due
3. Enter amount, payment method, reference
4. Click **"Record Payment"**

#### Track Payment History
1. Go **Payments → Payment History**
2. Filter by customer or date range
3. View all recorded payments

#### Supplier Payments
1. Go **Payments → Supplier Credit**
2. View amounts owed to suppliers
3. Click to record purchase payments

### Backup & Restore

#### Backup Database
1. Go **Settings → Database Operations**
2. Click **"Export Database"**
3. File downloads with timestamp
4. Keep in safe location

#### Restore Database
1. Go **Settings → Database Operations**
2. Click **"Import Database"**
3. Select backup file
4. Click **"Restore"**

---

## 🔧 Troubleshooting

### Issue: Exe Won't Start

**Solution 1:** Right-click → Run as Administrator

**Solution 2:** Check antivirus - may be blocking exe
- Add to whitelist and try again

**Solution 3:** Check if port 8000 is in use
- Restart computer or close other applications

### Issue: Browser Doesn't Open Automatically

**Solution:** Open manually:
1. Open Chrome, Firefox, or Edge
2. Go to: `http://127.0.0.1:8000`
3. Application should load

### Issue: Database Error / "Table Does Not Exist"

**Solution 1:** Force recreate database
- Close application
- Delete `data/fabric.db` file
- Restart application

**Solution 2:** Restore from backup
- Use **Database Operations → Import** to restore

### Issue: Slow Performance on First Start

**Normal!** First startup unpacks files (10-15 seconds). Subsequent starts are faster.

### Issue: Changes Not Saving

**Check:** 
1. Is application still running? (Check taskbar)
2. Do you see "Record Saved" message?
3. Try refreshing browser (F5)

### Issue: Cannot Delete Supplier/Customer

**Reason:** Has related transactions (purchases/sales)
**Solution:** Delete all purchases/sales first, then delete supplier/customer

---

## 📁 File Structure

```
FabricManager/
├── FabricManager.exe          ← Run this
├── README.txt                 ← This file
└── data/
    └── fabric.db              ← Your data (auto-created)
```

**Important:** 
- Do NOT delete or rename `FabricManager.exe`
- `data/` folder is created automatically
- Keep `data/` folder for your database

---

## 🔐 Data Safety

### Your Data is Safe Because:
- ✅ Database stored locally (not on cloud)
- ✅ Full database backups available
- ✅ Can move application to different PC
- ✅ No internet required

### Recommended Practices:
1. **Weekly Backups:** Export database to safe location
2. **Multiple Copies:** Keep backup on external drive
3. **Version Control:** Keep timestamped backups (e.g., `backup_2025-01-15.db`)

---

## ⚡ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Find/Search on page |
| `F5` | Refresh page |
| `Ctrl+P` | Print current page |
| `Alt+←` | Go back |
| `Alt+→` | Go forward |

---

## 📞 Support

### Common Questions

**Q: Can I run this on multiple computers?**
A: Yes! Copy to each USB/computer. Each has independent database.

**Q: Can multiple users use it simultaneously?**
A: Designed for single user at a time (same PC). Different PCs = separate data.

**Q: How do I transfer data between computers?**
A: Export database, transfer file, import on other PC.

**Q: Can I access from another computer on network?**
A: Current version local-only. Contact support for network version.

**Q: What if I lose the exe file?**
A: Your data is safe in `data/fabric.db`. You only need new exe.

**Q: How do I update to new version?**
A: Replace `FabricManager.exe` (keeps your data in `data/` folder)

---

## 🚀 Performance Tips

1. **Close unused browser tabs** - Saves RAM
2. **Restart app weekly** - Fresh memory
3. **Backup monthly** - Prevents data loss
4. **Clear browser cache** - If loading slowly
   - Chrome: Ctrl+Shift+Delete → Clear browsing data

---

## 📋 Features by Module

### Inventory Management
- Add/Edit/Delete Suppliers
- Add/Edit/Delete Customers
- Add/Edit/Delete Companies
- Register fabric types with codes

### Transaction Tracking
- Record purchases from suppliers
- Record sales to customers
- Track fabric codes and composition
- FIFO valuation

### Payment System
- Track payment status (Paid/Pending/Partial)
- Record multiple payments per transaction
- Payment method tracking
- Reference numbers (check #, transaction ID)

### Reports & Ledgers
- Purchase ledger with filtering
- Sales ledger with tax breakdown
- Customer transaction summary
- Supplier transaction summary
- Stock valuation with FIFO
- Profit/Loss statement

### Data Management
- CSV export (all reports)
- Database backup with timestamp
- Database restore from backup
- Data import/export

---

## 🎓 Tutorials

### First Use Walkthrough (10 minutes)
1. Create a company
2. Add 2-3 suppliers and customers
3. Record a purchase
4. Record a sale
5. View stock summary
6. View profit report

### Full Feature Tour (30 minutes)
1. Complete sample setup
2. Try all transaction types
3. Explore all reports
4. Test payment tracking
5. Practice backup/restore

---

## ⚙️ Advanced Settings

### Change Port (if 8000 is in use)
- Edit configuration file
- Restart application
- Contact support for help

### Increase Tax Rate
- Go to Add Sale form
- Uncheck "Apply Tax" or change % before submitting

### Export Settings
- All exports in CSV format
- Can open in Excel
- Compatible with all spreadsheet programs

---

## 📝 Notes

- Application runs on local port 8000
- No internet access needed
- Database syncs instantly
- All changes saved automatically
- Supports up to thousands of transactions

---

## ✅ Checklist for First Use

- [ ] Downloaded and extracted to safe location
- [ ] Successfully launched `FabricManager.exe`
- [ ] Browser opened to application
- [ ] Created at least one company
- [ ] Added test supplier and customer
- [ ] Recorded test purchase and sale
- [ ] Viewed stock summary
- [ ] Tested backup function

---

## 📞 Getting Help

If you encounter issues:
1. Check **Troubleshooting** section above
2. Try **Restart** (close and reopen exe)
3. Try **Database refresh** (delete fabric.db, restart)
4. Contact support with:
   - Error message
   - Steps to reproduce
   - Screenshot if applicable

---

## 📜 Version Info

- **Version:** 1.0.0
- **Build:** Portable Edition
- **Date:** November 2025
- **Compatibility:** Windows 7+ (tested on Windows 10, 11)

---

**Enjoy using Fabric Inventory Manager! 🎉**

For updates and support, visit [your support portal]

---

*This is a standalone, portable application. No installation required.*
*Your data remains on your computer at all times.*
*Fully functional offline.*
