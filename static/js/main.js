document.addEventListener("DOMContentLoaded", function () {

const allFormInputs = document.querySelectorAll('#budget-form input, #budget-form select');
  
allFormInputs.forEach(input => {
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault(); // Stop the browser from clicking buttons
        return false;
      }
    });
  });
  
// Remove "disabled" from all inputs immediately
const inputsToUnlock = [
    document.getElementById("category-select"),
    document.getElementById("new-category-input"),
    document.getElementById("category-amount-input"),
    document.getElementById("add-category-btn")
];

inputsToUnlock.forEach(el => {
    if (el) {
        el.removeAttribute("disabled");
        el.style.pointerEvents = "auto"; // Fixes any CSS locking
        el.style.opacity = "1";          // Fixes any CSS dimming
    }
});
  // ===================================
  // Global State
  // ===================================
  
  let categories = [];
  let currentPeriod = 'Monthly';
  let totalBudgetLocked = false;
  let totalBudgetAmount = 0;

  // ===================================
  // DOM Elements
  // ===================================
  
  const modal = document.getElementById("budget-modal");
  const openBtn = document.getElementById("open-budget-modal");
  const setBudgetBtn = document.getElementById("set-budget-btn");
  const closeBtn = document.getElementById("close-budget-modal");
  const fab = document.querySelector(".fab");
  
  const monthSelector = document.getElementById("month-selector");
  const budgetMonthDisplay = document.getElementById("budget-month-display");
  const budgetDisplayArea = document.getElementById("budget-display-area");
  const spendingTrendTitle = document.getElementById("spending-trend-title");
  
  const categorySelect = document.getElementById("category-select");
  const newCategoryInput = document.getElementById("new-category-input");
  const categoryAmountInput = document.getElementById("category-amount-input");
  const addCategoryBtn = document.getElementById("add-category-btn");
  const categoryTableBody = document.querySelector("#category-table tbody");
  const totalBudgetInput = document.getElementById("total-budget-input");
  const lockTotalBudgetBtn = document.getElementById("lock-total-budget-btn");
  const budgetErrorMessage = document.getElementById("budget-error-message");
  const lockWarning = document.getElementById("lock-warning");
  const categoriesJsonInput = document.getElementById("categories-json");
  const budgetForm = document.getElementById("budget-form");
  const categoryAddError = document.getElementById("category-add-error");
  const setTotalBtn = document.getElementById("set-total-btn");
  
  const periodTabs = document.querySelectorAll(".period-tab");

  // ===================================
  // Flash Message Auto-Hide
  // ===================================
  
  function autoHideFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
      setTimeout(() => {
        msg.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        msg.style.opacity = '0';
        msg.style.transform = 'translateX(100%)';
        setTimeout(() => msg.remove(), 500);
      }, 3000);
    });
  }
  
  // Run on page load
  autoHideFlashMessages();

  // ===================================
  // Modal Management
  // ===================================
  
  function openModal() {
    if (modal) {
      modal.classList.add("show");
    }
  }

  function closeModal() {
    if (modal) modal.classList.remove("show");
  }

  if (openBtn) openBtn.addEventListener("click", openModal);
  if (fab) fab.addEventListener("click", openModal);
  if (setBudgetBtn) setBudgetBtn.addEventListener("click", openModal);

  if (closeBtn) closeBtn.addEventListener("click", closeModal);

  if (modal) {
    modal.addEventListener("click", function (event) {
      if (event.target === modal) closeModal();
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && modal && modal.classList.contains("show")) {
      closeModal();
    }
  });

  // ===================================
  // Month Selector
  // ===================================
  
  if (monthSelector) {
    monthSelector.addEventListener("change", function() {
      // Reload page with selected month
      window.location.href = `${window.location.pathname}?month=${this.value}`;
    });
  }

  // ===================================
  // Period Tab Switching
  // ===================================
  
  periodTabs.forEach(tab => {
    tab.addEventListener("click", function() {
      periodTabs.forEach(t => t.classList.remove("active"));
      this.classList.add("active");
      currentPeriod = this.textContent.trim();
    });
  });

  // Budget display is server-rendered from MongoDB

  // ===================================
  // Total Budget Management
  // ===================================
  
  function getNonExtraSum() {
    // Helper to calculate sum of all categories EXCEPT 'Extra'
    return categories
      .filter(c => c.category !== "Extra")
      .reduce((sum, c) => sum + (c.amount || 0), 0);
  }

  function setTotalBudget() {
    const inputValue = parseFloat(totalBudgetInput.value);
    
    if (isNaN(inputValue) || inputValue <= 0) {
      return;
    }
    
    // Check against the sum of actual categories (excluding Extra)
    const requiredSum = getNonExtraSum();
    
    if (inputValue < requiredSum) {
      // Show error message
      if (budgetErrorMessage) {
        budgetErrorMessage.style.display = 'block';
      }
      return;
    }
    
    // Hide error message
    if (budgetErrorMessage) {
      budgetErrorMessage.style.display = 'none';
    }
    
    // Set the total budget
    totalBudgetAmount = inputValue;
    
    // Update Extra category
    updateExtraCategory();
  }

  if (totalBudgetInput) {
    // Handle Enter key
    totalBudgetInput.addEventListener("keypress", function(e) {
      if (e.key === "Enter") {
        e.preventDefault();
        setTotalBudget();
        this.blur();
      }
    });
  }

  // ===================================
  // SET TOTAL BUDGET BUTTON LOGIC
  // ===================================

  if (setTotalBtn) {
    setTotalBtn.addEventListener("click", function() {
      const val = parseFloat(totalBudgetInput.value);

      if (isNaN(val) || val <= 0) {
        alert("Please enter a valid total budget amount.");
        return;
      }

      totalBudgetAmount = val;

      updateExtraCategory();
      
      if (budgetErrorMessage) {
          budgetErrorMessage.style.display = 'none';
      }

      const originalText = this.textContent;
      this.textContent = "Updated!";
      setTimeout(() => {
        this.textContent = originalText;
      }, 1000);
    });
  }

  // ===================================
  // Lock Total Budget
  // ===================================
  
  if (lockTotalBudgetBtn) {
    lockTotalBudgetBtn.addEventListener("click", function(e) {
      e.preventDefault();
      
      if (totalBudgetLocked) {
        return; 
      }
      
      const totalBudget = parseFloat(totalBudgetInput.value);
      
      if (isNaN(totalBudget) || totalBudget <= 0) {
        alert("Please enter a total budget first.");
        return;
      }
      
      // Lock the budget
      totalBudgetLocked = true;
      totalBudgetAmount = totalBudget;
      
      // Disable input
      totalBudgetInput.disabled = true;
      
      // Update button appearance
      this.textContent = "LOCKED";
      this.disabled = true;
      this.style.backgroundColor = "var(--color-accent-gray)";
      this.style.cursor = "not-allowed";
      
      // Show warning
      if (lockWarning) {
        lockWarning.style.display = 'block';
      }
    });
  }

  // ===================================
  // Category Management
  // ===================================
  
  if (categorySelect) {
    categorySelect.addEventListener("change", function () {
      if (this.value === "New") {
        newCategoryInput.style.display = "block";
        newCategoryInput.focus();
      } else {
        newCategoryInput.style.display = "none";
      }
    });
  }

    // Helper to hide error when user starts typing again
  if (categoryAmountInput) {
      categoryAmountInput.addEventListener("input", function() {
          if (categoryAddError) categoryAddError.style.display = "none";
      });
  }

  if (addCategoryBtn) {
    addCategoryBtn.addEventListener("click", function () {
      if (categoryAddError) categoryAddError.style.display = "none";

      let categoryName = "";
      if (categorySelect.value === "New") {
        categoryName = newCategoryInput.value.trim();
      } else {
        categoryName = categorySelect.value;
      }

      const amountValue = parseFloat(categoryAmountInput.value);

      if (!categoryName) {
        if (categoryAddError) {
            categoryAddError.textContent = "Please choose a category.";
            categoryAddError.style.display = "block";
        }
        return;
      }
      
      if (isNaN(amountValue) || amountValue <= 0) {
        if (categoryAddError) {
            categoryAddError.textContent = "Please enter a valid amount.";
            categoryAddError.style.display = "block";
        }
        return;
      }

      // Check against Budget Limit
      if (totalBudgetAmount > 0) {
        const currentRealSpend = categories
          .filter(c => c.category !== "Extra")
          .reduce((sum, c) => sum + c.amount, 0);

        const existingCategory = categories.find(c => c.category === categoryName);
        const oldCategoryAmount = (existingCategory && categoryName !== "Extra") ? existingCategory.amount : 0;
        
        const projectedTotal = currentRealSpend - oldCategoryAmount + amountValue;

        // Tolerance for float math
        if (projectedTotal > (totalBudgetAmount + 0.001)) {
          const available = totalBudgetAmount - (currentRealSpend - oldCategoryAmount);
          
          if (categoryAddError) {
              categoryAddError.textContent = `Cannot add $${amountValue}. Only $${available.toFixed(2)} remaining.`;
              categoryAddError.style.display = "block";
          }
          return; 
        }
      }

      // Success - Add to State
      const existing = categories.find(c => c.category === categoryName);
      if (existing) {
        existing.amount = amountValue;
      } else {
        categories.push({ 
          category: categoryName, 
          amount: amountValue
        });
      }

      // Clear Inputs
      categoryAmountInput.value = "";
      if (categorySelect.value === "New") {
        newCategoryInput.value = "";
        newCategoryInput.style.display = "none";
        categorySelect.value = "";
      }

      updateExtraCategory();
    });
  }

  function renderCategoryTable() {
    if (!categoryTableBody) return;
    
    categoryTableBody.innerHTML = "";
    
    if (categories.length === 0) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 3;
      td.textContent = "No categories added yet";
      td.style.textAlign = "center";
      td.style.color = "var(--color-accent-gray)";
      td.style.padding = "var(--spacing-lg)";
      tr.appendChild(td);
      categoryTableBody.appendChild(tr);
      return;
    }
    
    // Sort so "Extra" is always at the bottom
    categories.sort((a, b) => {
        if (a.category === "Extra") return 1;
        if (b.category === "Extra") return -1;
        return 0;
    });
    
    categories.forEach((item, index) => {
      const tr = document.createElement("tr");
      
      // Style "Extra" differently so it stands out
      if (item.category === "Extra") {
        tr.style.backgroundColor = "rgba(0, 255, 0, 0.05)";
        tr.style.fontWeight = "bold";
      }

      const tdName = document.createElement("td");
      tdName.textContent = item.category;
      
      const tdAmount = document.createElement("td");
      tdAmount.textContent = "$" + item.amount.toFixed(2);
      
      const tdDelete = document.createElement("td");
      
      // Do not allow deleting "Extra" manually, it is auto-calculated
      if (item.category !== "Extra") {
          const deleteBtn = document.createElement("button");
          deleteBtn.type = "button";
          deleteBtn.textContent = "Delete";
          deleteBtn.className = "btn-secondary";
          deleteBtn.style.padding = "0.25rem 0.75rem";
          deleteBtn.style.fontSize = "0.875rem";
          deleteBtn.onclick = function(e) {
            e.preventDefault(); 
            // Remove the item
            categories.splice(index, 1);
            // Immediately Recalculate Extra to fill the void
            updateExtraCategory();
          };
          tdDelete.appendChild(deleteBtn);
      } else {
          tdDelete.textContent = "(Auto)";
          tdDelete.style.color = "#888";
          tdDelete.style.fontSize = "0.8rem";
      }

      tr.appendChild(tdName);
      tr.appendChild(tdAmount);
      tr.appendChild(tdDelete);
      categoryTableBody.appendChild(tr);
    });
  }

  // Helper to update "Extra" based on remaining funds
  function updateExtraCategory() {
    if (!totalBudgetAmount || totalBudgetAmount <= 0) {
        renderCategoryTable();
        return;
    }
    
    categories = categories.filter(c => c.category !== "Extra");
    
    const currentSum = categories.reduce((sum, c) => sum + (c.amount || 0), 0);
    
    const remaining = totalBudgetAmount - currentSum;
    
    if (remaining > 0.009) {
      categories.push({ 
        category: "Extra", 
        amount: remaining
      });
    }
    
    renderCategoryTable();
  }

  // ===================================
  // Form Submission
  // ===================================
  
  if (budgetForm) {
    budgetForm.addEventListener("submit", function (e) {
      e.preventDefault();
      
      const inputVal = parseFloat(totalBudgetInput.value);
      
      if (isNaN(inputVal) || inputVal <= 0) {
        alert("Please enter a valid total monthly budget.");
        return;
      }

      totalBudgetAmount = inputVal;
      updateExtraCategory();

      const sum = categories
        .filter(c => c.category !== "Extra")
        .reduce((sum, c) => sum + (c.amount || 0), 0);

      if (totalBudgetAmount < sum) {
        if (budgetErrorMessage) {
          budgetErrorMessage.style.display = 'block';
        }
        return;
      }
      
      if (categoriesJsonInput) {
        categoriesJsonInput.value = JSON.stringify(categories);
      }
      
      // Submit to MongoDB backend
      budgetForm.submit();
    });
  }

  // No initialization needed - data loaded from MongoDB server-side
});